"""Separate Qt event loop for SARU Browser; no Python API exposed to websites."""
import argparse,json,sys,threading
from pathlib import Path
from queue import Queue,Empty
from saru_browser import checked_url


def emit(event,message):print(json.dumps({'event':event,'message':message}),flush=True)


def run(data,self_test=False):
 from PySide6.QtCore import QUrl,QTimer
 from PySide6.QtGui import QAction,QKeySequence,QIcon
 from PySide6.QtWidgets import QApplication,QMainWindow,QTabWidget,QToolBar,QLineEdit,QFileDialog,QMessageBox,QInputDialog
 from PySide6.QtWebEngineCore import QWebEngineProfile,QWebEnginePage,qWebEngineChromiumVersion
 from PySide6.QtWebEngineWidgets import QWebEngineView
 app=QApplication(sys.argv[:1]);app.setApplicationName('SARU Browser')
 data=Path(data);data.mkdir(parents=True,exist_ok=True)
 # A profile must not be opened by multiple processes concurrently.
 from PySide6.QtCore import QLockFile
 profile_lock=QLockFile(str(data/'profile.lock'));profile_lock.setStaleLockTime(30000)
 if not profile_lock.tryLock(0):raise RuntimeError('SARU Browser profile is already open. Use the existing SARU window.')
 class View(QWebEngineView):
  def createWindow(self,kind):return window.add_tab(None)
 class Window(QMainWindow):
  def __init__(self):
   super().__init__();self.setWindowTitle('SARU Browser');self.resize(1200,800);self.setWindowIcon(QIcon(str(Path(__file__).with_name('saru.ico'))))
   self.profile=QWebEngineProfile('SARU',self);self.profile.setPersistentStoragePath(str(data/'profile'));self.profile.setCachePath(str(data/'cache'));self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
   from browser_identity import compatible_user_agent
   self.profile.setHttpUserAgent(compatible_user_agent(self.profile.httpUserAgent(),qWebEngineChromiumVersion()))
   self.profile.downloadRequested.connect(self.download)
   self.tabs=QTabWidget();self.tabs.setTabsClosable(True);self.tabs.setMovable(True);self.setCentralWidget(self.tabs);self.tabs.tabCloseRequested.connect(self.close_tab);self.tabs.currentChanged.connect(self.sync)
   bar=QToolBar('Navigation');self.addToolBar(bar)
   for name,action in [('Back','back'),('Forward','forward'),('Reload','reload'),('New tab','new_tab')]:
    item=QAction(name,self);item.triggered.connect(lambda checked=False,a=action:self.command(a));bar.addAction(item)
   self.address=QLineEdit();self.address.setPlaceholderText('Website address — login directly on the website');self.address.returnPressed.connect(self.navigate);bar.addWidget(self.address)
   self.statusBar().showMessage('SARU Browser · Separate local login profile · Voice/text navigation from SARU')
   self.setStyleSheet('QMainWindow,QToolBar,QTabWidget::pane{background:#071226;color:#edf4ff} QLineEdit{background:#12213a;color:white;padding:8px;border:1px solid #ff3978} QTabBar::tab{background:#14243b;color:white;padding:10px} QTabBar::tab:selected{background:#a91b50}')
   for shortcut,callback in [('Ctrl+L',self.address.setFocus),('Ctrl+T',lambda:self.command('new_tab')),('Ctrl+W',lambda:self.command('close_tab')),('Ctrl+R',lambda:self.command('reload'))]:
    a=QAction(self);a.setShortcut(QKeySequence(shortcut));a.triggered.connect(callback);self.addAction(a)
   self.add_tab(None)
  def current(self):return self.tabs.currentWidget()
  def add_tab(self,url):
   view=View();page=QWebEnginePage(self.profile,view);view.setPage(page)
   i=self.tabs.addTab(view,'New tab');self.tabs.setCurrentIndex(i)
   view.titleChanged.connect(lambda title,v=view:self.tabs.setTabText(self.tabs.indexOf(v),title[:36] or 'New tab'))
   view.urlChanged.connect(lambda url:self.sync())
   view.loadFinished.connect(lambda ok:emit('loaded','SARU Browser page loaded.' if ok else 'SARU Browser could not fully load the page.'))
   if url:view.setUrl(QUrl(checked_url(url)))
   return view
  def sync(self,*args):
   if self.current():self.address.setText(self.current().url().toString())
  def navigate(self):
   try:self.command('open',self.address.text())
   except ValueError as exc:self.statusBar().showMessage(str(exc))
  def close_tab(self,index):
   if self.tabs.count()==1:self.current().setUrl(QUrl('about:blank'));return
   view=self.tabs.widget(index);self.tabs.removeTab(index);view.deleteLater()
  def fill_password(self):
   view=self.current();page=view.page();url=view.url()
   if url.scheme()!='https':raise ValueError('Password filling requires an HTTPS page.')
   origin=url.scheme()+'://'+url.host()+(':'+str(url.port()) if url.port()!=-1 else '')
   def inspect(result):
    if isinstance(result,str):
     try:result=json.loads(result)
     except ValueError:result=None
    if not isinstance(result,dict) or not result.get('password') or result.get('origin')!=origin:
     self.statusBar().showMessage('Focus the real website password field first. No password requested.');return
    secret,ok=QInputDialog.getText(self,'One-time password · '+url.host(),'Enter only for this site. SARU will not save it or submit the form.',QLineEdit.EchoMode.Password)
    if not ok or not secret:return
    try:
     if self.current() is not view or view.url().host()!=url.host():self.statusBar().showMessage('Website changed. Password not inserted.');return
     script='''(function(value,expected){try{let e=window.__saruPasswordField;delete window.__saruPasswordField;if(location.origin!==expected||!e||!e.isConnected||e.tagName!=="INPUT"||e.type!=="password")return false;Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set.call(e,value);e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}));return true;}finally{value="";}})('''+json.dumps(secret)+','+json.dumps(origin)+')'
     page.runJavaScript(script,lambda success:self.statusBar().showMessage('Password inserted once; not saved by SARU; form not submitted.' if success else 'Password field changed; no insertion.'))
    finally:secret=''
   page.runJavaScript('(function(){let e=document.activeElement;window.__saruPasswordField=e;return JSON.stringify({password:!!e&&e.tagName==="INPUT"&&e.type==="password",origin:location.origin});})()',inspect)
  def command(self,action,value=None):
   view=self.current()
   if action=='open':view.setUrl(QUrl(checked_url(value)));self.showNormal();self.raise_();self.activateWindow()
   elif action=='new_tab':self.add_tab(value or 'https://www.google.com/')
   elif action in ('back','forward','reload'):getattr(view,action)()
   elif action=='close_tab':self.close_tab(self.tabs.currentIndex())
   elif action=='select_tab':
    if not 1<=int(value)<=self.tabs.count():raise ValueError('That browser tab does not exist.')
    self.tabs.setCurrentIndex(int(value)-1)
   elif action in ('zoom_in','zoom_out'):view.setZoomFactor(max(.5,min(2,view.zoomFactor()+(.1 if action=='zoom_in' else -.1))))
   elif action=='fill_password':self.fill_password()
   elif action=='close':self.close()
   else:raise ValueError('Unsupported browser control')
  def download(self,item):
   path,_=QFileDialog.getSaveFileName(self,'Save download',str(Path.home()/'Downloads'/Path(item.suggestedFileName()).name))
   if path:item.setDownloadDirectory(str(Path(path).parent));item.setDownloadFileName(Path(path).name);item.accept()
   else:item.cancel()
  def closeEvent(self,event):
   for i in range(self.tabs.count()):self.tabs.widget(i).page().deleteLater()
   super().closeEvent(event)
 window=Window();events=Queue(maxsize=100)
 def read():
  for line in sys.stdin:
   try:events.put(json.loads(line))
   except ValueError:pass
  events.put({'action':'close'})
 if not self_test:threading.Thread(target=read,daemon=True).start()
 def pump():
  try:
   for _ in range(20):
    item=events.get_nowait()
    try:window.command(item['action'],item.get('value'))
    except Exception as exc:emit('error',str(exc))
  except Empty:pass
 timer=QTimer();timer.timeout.connect(pump);timer.start(100);window.show();emit('ready','SARU Browser ready. Log in directly on the website.'); 
 if self_test:
  def check():
   assert not window.profile.isOffTheRecord()
   assert window.profile.persistentStoragePath()==str(data/'profile').replace('\\','/') or Path(window.profile.persistentStoragePath())==data/'profile'
   window.add_tab(None);assert window.tabs.count()==2
   window.command('select_tab',1);assert window.tabs.currentIndex()==0
   window.command('zoom_in');assert window.current().zoomFactor()>1
   window.command('close_tab');assert window.tabs.count()==1
   window.current().setHtml('<html><title>SARU Browser Test</title><body>Local browser rendering works<input id="test-pass" type="password"></body></html>',QUrl('https://saru-browser-test.invalid/'))
   def rendered(ok):
    if ok:
     original=QInputDialog.getText
     QInputDialog.getText=staticmethod(lambda *args,**kwargs:('synthetic-local-only',True))
     def focused(value):
      window.fill_password()
      def verify():
       def checked(success):
        QInputDialog.getText=original
        if success:emit('tested','PASS: Qt tabs, navigation, profile, local rendering and one-time masked password-field fill');window.close()
        else:emit('error','Password helper self-test failed: '+window.statusBar().currentMessage());app.exit(1)
       window.current().page().runJavaScript('document.getElementById("test-pass").value === "synthetic-local-only"',checked)
      QTimer.singleShot(800,verify)
     window.current().page().runJavaScript('document.getElementById("test-pass").focus(); true',focused)
   window.current().loadFinished.connect(rendered)
  QTimer.singleShot(300,check)
  QTimer.singleShot(15000,app.quit)
 code=app.exec();profile_lock.unlock();return code

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--data',required=True);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 try:raise SystemExit(run(args.data,args.self_test))
 except Exception as exc:emit('error','SARU Browser failed: '+str(exc));raise SystemExit(1)

if __name__=="__main__":main()
