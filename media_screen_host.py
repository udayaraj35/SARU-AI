"""SARU's native Qt video/chat screen. No browser tab or website Python bridge."""
import argparse,json,sys,threading
from queue import Queue,Empty
from urllib.parse import urlsplit

def emit(event,value):print(json.dumps({'event':event,'value':value},ensure_ascii=False),flush=True)

def run(url,theme='Neon Rose',self_test=False):
 from PySide6.QtCore import QUrl,QTimer,Qt
 from PySide6.QtGui import QIcon,QAction,QKeySequence,QTextCursor
 from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QSplitter,QLineEdit,QPushButton,QTextEdit,QLabel
 from PySide6.QtWebEngineCore import QWebEnginePage,QWebEngineSettings
 from PySide6.QtWebEngineWidgets import QWebEngineView
 from pathlib import Path
 from theme_manager import palette
 parts=urlsplit(url)
 if parts.scheme!='http' or parts.hostname!='127.0.0.1' or not parts.port:raise ValueError('Expected the private local SARU player.')
 app=QApplication(sys.argv[:1]);app.setApplicationName('SARU Video Screen');events=Queue(maxsize=200)
 colors=palette(theme)
 class Page(QWebEnginePage):
  def createWindow(self,kind):
   window.statusBar().showMessage('This screen keeps playback here. New browser windows are disabled.');return None
  def acceptNavigationRequest(self,target,kind,main):
   return not main or (target.scheme()=='http' and target.host()=='127.0.0.1' and target.port()==parts.port)
 class Window(QMainWindow):
  def __init__(self):
   super().__init__();self.setWindowTitle('SARU AI — Video & Chat');self.resize(1260,820);self.setMinimumSize(720,520);self.setWindowIcon(QIcon(str(Path(__file__).with_name('saru.ico'))))
   self.setStyleSheet(f"QMainWindow,QWidget{{background:{colors['bg']};color:{colors['text']}}} QLineEdit,QTextEdit{{background:{colors['panel']};border:1px solid {colors['accent'] if 'accent' in colors else colors['primary']};border-radius:10px;padding:10px}} QPushButton{{background:{colors['panel']};padding:9px;border-radius:10px;border:1px solid {colors['primary']}}} QSplitter::handle{{background:{colors['primary']};width:7px}}")
   body=QWidget();layout=QVBoxLayout(body);self.setCentralWidget(body)
   toolbar=QHBoxLayout();layout.addLayout(toolbar);toolbar.addWidget(QLabel('SARU · VIDEO + CHAT'))
   for name,fn in [('Large',lambda:self.command({'action':'large'})),('Small',lambda:self.command({'action':'small'})),('Fullscreen',self.toggle_full),('Minimize',self.showMinimized)]:
    b=QPushButton(name);b.clicked.connect(fn);toolbar.addWidget(b)
   self.splitter=QSplitter(Qt.Orientation.Horizontal);layout.addWidget(self.splitter,1)
   search=QHBoxLayout();self.video_query=QLineEdit();self.video_query.setPlaceholderText('YouTube link or video title');search.addWidget(self.video_query);play=QPushButton('Play YouTube');search.addWidget(play);layout.insertLayout(1,search)
   def video_request():
    text=self.video_query.text().strip()
    if text:emit('video',text)
   self.video_query.returnPressed.connect(video_request);play.clicked.connect(video_request)
   self.view=QWebEngineView();self.view.setPage(Page(self.view));self.splitter.addWidget(self.view)
   self.view.settings().setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled,True)
   self.view.settings().setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture,False)
   self.view.page().fullScreenRequested.connect(self.full_request)
   chat=QWidget();chat_layout=QVBoxLayout(chat);chat_layout.addWidget(QLabel('Talk to SARU · existing voice remains in the main app'))
   self.chat=QTextEdit();self.chat.setReadOnly(True);chat_layout.addWidget(self.chat,1)
   self.entry=QLineEdit();self.entry.setPlaceholderText('Ask SARU or say: pause video / next video');chat_layout.addWidget(self.entry)
   send=QPushButton('Send');send.clicked.connect(self.submit);chat_layout.addWidget(send);self.entry.returnPressed.connect(self.submit)
   self.splitter.addWidget(chat);self.splitter.setSizes([900,360]);self.splitter.setChildrenCollapsible(False)
   self.statusBar().showMessage('Resize this window or drag the divider. F11: fullscreen · Esc: restore. No browser tab is opened.')
   for key,fn in [('F11',self.toggle_full),('Escape',self.restore)]:
    a=QAction(self);a.setShortcut(QKeySequence(key));a.triggered.connect(fn);self.addAction(a)
   self.view.setUrl(QUrl(url))
  def submit(self):
   text=self.entry.text().strip()
   if text and len(text)<=4000:self.entry.clear();emit('chat',text)
  def full_request(self,request):request.accept();self.showFullScreen() if request.toggleOn() else self.showNormal()
  def toggle_full(self):self.showNormal() if self.isFullScreen() else self.showFullScreen()
  def restore(self):self.showNormal()
  def command(self,item):
   action=item.get('action');value=item.get('value')
   if action=='chat':self.chat.moveCursor(QTextCursor.MoveOperation.End);self.chat.insertPlainText(str(value));self.chat.ensureCursorVisible()
   elif action=='show':self.showNormal();self.raise_();self.activateWindow()
   elif action=='fullscreen':self.showFullScreen()
   elif action=='restore':self.showNormal()
   elif action=='large':self.showNormal();self.resize(1400,900)
   elif action=='small':self.showNormal();self.resize(840,580)
   elif action=='minimize':self.showMinimized()
   elif action=='close':self.close()
 window=Window()
 def read():
  for line in sys.stdin:
   try:events.put(json.loads(line))
   except ValueError:pass
  events.put({'action':'close'})
 if not self_test:threading.Thread(target=read,daemon=True).start()
 def pump():
  try:
   for _ in range(50):window.command(events.get_nowait())
  except Empty:pass
 timer=QTimer();timer.timeout.connect(pump);timer.start(50);window.show();emit('ready','SARU video/chat screen ready.')
 if self_test:
  def check():
   window.command({'action':'chat','value':'SARU: synthetic screen test\n'});assert 'synthetic' in window.chat.toPlainText()
   window.command({'action':'small'});assert window.width()==840
   window.command({'action':'fullscreen'});assert window.isFullScreen()
   window.command({'action':'restore'});assert not window.isFullScreen()
   window.splitter.setSizes([600,240]);assert len(window.splitter.sizes())==2
   def inspect(result):
    if not result:emit('error','Media HTML did not render');app.exit(1);return
    emit('tested','PASS: native video/chat, split resize, fullscreen and local controls rendered.');window.close()
   window.view.page().runJavaScript("!!document.getElementById('volume') && !!document.getElementById('stage')",inspect)
  QTimer.singleShot(2400,check);QTimer.singleShot(12000,lambda:app.exit(2))
 return app.exec()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--url',required=True);parser.add_argument('--theme',default='Neon Rose');parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 try:raise SystemExit(run(args.url,args.theme,args.self_test))
 except Exception as exc:emit('error',str(exc));raise SystemExit(1)
if __name__=='__main__':main()
