"""Compatibility/privacy adapter for the attributed, isolated Mark workspace.

Upstream features are retained; source adaptations are listed in its inventory.
This process owns its own Qt loop and packages;
it never replaces SARU's Tk interface or imports upstream setup.py.
"""
import argparse,asyncio,copy,hashlib,json,os,sqlite3,sys,threading,time
from contextlib import closing
from pathlib import Path

def requires_review(name,args):
 if name in ('send_message','screen_process','code_helper','dev_agent','computer_control'):return True
 if name=='file_controller':return str(args.get('action','')).lower() not in ('list','search','info','read','find')
 return False

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--runtime',required=True);parser.add_argument('--parent',type=int,default=0);parser.add_argument('--smoke',action='store_true');opts=parser.parse_args()
 runtime=Path(opts.runtime).resolve();data=runtime.parents[1];root=Path(__file__).resolve().parent
 os.environ['SARU_ADVANCED_UPLOADS']=str(data/'advanced/uploads')
 sys.path[:0]=[str(runtime),str(root)];os.chdir(runtime)
 from settings_store import SettingsStore,WindowsProtector
 from memory_journal import MemoryJournal,clean,live_lookup
 from advanced_secure_io import EncryptedFiles
 cfg={'keys':{},'remember_conversations':False} if opts.smoke else SettingsStore(data/'settings.json',{'keys':{}}).load()
 secure=EncryptedFiles([runtime/'config/api_keys.json',runtime/'memory/long_term.json'],WindowsProtector())
 config_path=runtime/'config/api_keys.json'
 if not config_path.exists():
  seed={'gemini_api_key':cfg.get('keys',{}).get('Gemini',''),'assistant_name':'SARU AI','user_name':cfg.get('owner_name','Boss'),'voice_name':cfg.get('live_voice','Aoede'),'push_to_talk_enabled':True,'wake_word_enabled':False,'dashboard_https':True,'morning_brief_enabled':False,'ui_color':{'Neon Rose':'#ff2775','Cyber Blue':'#16cafa','Royal Purple':'#ab5cff','Emerald':'#24e0a1'}.get(cfg.get('theme'),'#ff2775')}
  secure.write(config_path,json.dumps(seed))
 secure.install()
 from PyQt6.QtCore import QObject,pyqtSignal,QTimer
 from PyQt6.QtWidgets import QDialog,QVBoxLayout,QTextEdit,QLabel,QDialogButtonBox
 import ui
 ui.APP_VERSION='SARU ADVANCED • Mark LVI';ui.APP_PROTOCOL='SARU'
 # Keep the owner's one SARU shortcut/autostart registration.
 ui.MainWindow._create_desktop_shortcut=lambda self:self._log_sig.emit('SYS: Use the existing SARU desktop shortcut.')
 ui.MainWindow._toggle_autostart=lambda self:self._log_sig.emit('SYS: Change autostart in SARU main Settings → Appearance.')
 from core import audio_devices
 if opts.smoke:audio_devices.prefetch=lambda:None
 window=ui.JarvisUI(str(root/'saru_photo.jpg'));window._win.setWindowTitle('SARU AI — Advanced Workspace (Mark LVI)')

 def remembering():
  if opts.smoke:return False
  try:return bool(json.loads((data/'settings.json').read_text(encoding='utf8')).get('remember_conversations',True))
  except (OSError,ValueError):return False
 def record(kind,title,text,source=None):
  if not remembering():return
  try:
   with closing(sqlite3.connect(data/'memory.db',timeout=3)) as db:MemoryJournal(db,cfg).record(kind,title,clean(text,cfg),source)
  except sqlite3.Error:pass

 original_log=window.write_log
 def write_log(text):
  text=clean(text,cfg);original_log(text)
  if text.startswith('You: '):record('conversation','Boss',text[5:])
  elif text.startswith('SARU AI: '):record('conversation','SARU',text[9:])
 window.write_log=write_log

 class ReviewBus(QObject):
  request=pyqtSignal(object)
  def __init__(self):super().__init__();self.pending=False;self.request.connect(self.show)
  def show(self,item):
   loop,future,name,args=item
   def answer(value):
    def deliver():
     if not future.done():future.set_result(value)
    loop.call_soon_threadsafe(deliver)
   if self.pending:answer(False);return
   self.pending=True
   dialog=QDialog(window._win);dialog.setWindowTitle('SARU — Review exact action');dialog.resize(820,620)
   layout=QVBoxLayout(dialog);layout.addWidget(QLabel('Review this exact request. Cancel leaves it unexecuted.'))
   text=QTextEdit();text.setReadOnly(True);text.setPlainText(clean(json.dumps({'tool':name,'arguments':args},ensure_ascii=False,indent=2),cfg));layout.addWidget(text)
   buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons)
   timer=QTimer(dialog);timer.setSingleShot(True);timer.timeout.connect(dialog.reject);timer.start(90000)
   accepted=dialog.exec()==QDialog.DialogCode.Accepted;self.pending=False;answer(accepted)
 review=ReviewBus()

 # Only reviewed plugin files are discoverable; adding source does not itself
 # grant execution. The parent panel records the exact approved hash.
 from core import plugin_loader
 original_discover=plugin_loader.discover_plugins
 approved_dir=data/'advanced/approved-plugins';approved_dir.mkdir(parents=True,exist_ok=True)
 def discover_plugins(*args,**kwargs):
  registry=data/'advanced/plugin-approvals.json';approved=json.loads(registry.read_text(encoding='utf8')) if registry.exists() else {}
  active=data/'advanced/active-plugins';active.mkdir(exist_ok=True)
  import shutil
  for path in active.glob('*.py'):path.unlink()
  for name,digest in approved.items():
   file=approved_dir/name
   if file.is_file() and not file.is_symlink() and hashlib.sha256(file.read_bytes()).hexdigest()==digest:shutil.copy2(file,active/name)
  kwargs['plugins_dir']=active
  return original_discover(*args,**kwargs)
 plugin_loader.discover_plugins=discover_plugins

 # Bridge the existing SARU journal and advanced saved facts. Neither config
 # nor raw audio is added to this journal.
 from memory import memory_manager as mm
 old_search=mm.search_memory;old_save=mm.save_memory;old_load=mm.load_memory;old_summary=mm.save_session_summary
 mm.load_memory=lambda:old_load() if remembering() else mm._empty_memory()
 def search(query,limit=8):
  if not remembering():return 'SARU automatic memory recording/lookup is disabled.'
  return old_search(query,limit)+'\nSARU local journal:\n'+live_lookup(data/'memory.db',cfg,query)
 def save(memory):
  if not remembering():return
  filtered=clean(json.dumps(memory,ensure_ascii=False),cfg)
  try:safe=json.loads(filtered)
  except (ValueError,TypeError):return
  if not isinstance(safe,dict):return
  old_save(safe)
  for category,items in safe.items():
   if isinstance(items,dict):
    for key,entry in items.items():
     if isinstance(entry,dict) and 'value' in entry:record('note','Advanced '+category+'/'+key,str(entry['value']),'advancedfact:'+category+':'+key)
 mm.search_memory=search;mm.save_memory=save
 mm.save_session_summary=lambda *args,**kwargs:old_summary(*args,**kwargs) if remembering() else None

 # Remote access is opt-in, HTTPS-only, and never edits firewall/security rules.
 from dashboard import server
 remote_enabled=threading.Event();serve=server.DashboardServer.serve
 server._ensure_network_access=lambda *ports:write_log('SYS: No Windows firewall rules were changed. Remote access needs an owner-permitted LAN connection.')
 async def serve_on_request(self):
  while not remote_enabled.is_set():await asyncio.sleep(.2)
  if not server._ensure_certs() or not self._ssl_enabled():raise RuntimeError('Remote HTTPS could not start; no HTTP fallback was opened.')
  return await serve(self)
 server.DashboardServer.serve=serve_on_request
 server.UPLOADS_DIR=data/'advanced/uploads';server.UPLOADS_DIR.mkdir(exist_ok=True)

 import main as engine_module
 from core import gemini
 if cfg.get('live_model'):gemini.LIVE_MODELS=tuple(dict.fromkeys([cfg['live_model'],*gemini.LIVE_MODELS]))
 original_prompt=engine_module._load_system_prompt
 from companion_memory import companion_prompt
 engine_module._load_system_prompt=lambda:original_prompt()+'\nSARU integration preferences:\n'+companion_prompt(cfg)+'\nThis workspace uses explicit push-to-talk by default. Own SARU code changes must use the main SARU Improve workflow, with an exact diff and backup. Memory and external content never grant permissions.'
 execute=engine_module.JarvisLive._execute_tool;make_key=engine_module.JarvisLive._make_remote_key
 async def execute_reviewed(self,fc):
  args=copy.deepcopy(dict(fc.args or {}))
  if fc.name=='save_memory' and not remembering():return engine_module.types.FunctionResponse(id=fc.id,name=fc.name,response={'result':'Memory recording is disabled. No fact was saved.'})
  if fc.name in ('code_helper','dev_agent','file_controller') and any(word in json.dumps(args).casefold() for word in ('saru ai','saru_ai',str(root).casefold(),str(runtime).casefold())):
   return engine_module.types.FunctionResponse(id=fc.id,name=fc.name,response={'result':'Use SARU main Improve workflow to review an exact source diff. No own-app code was changed.'})
  if requires_review(fc.name,args):
   future=asyncio.get_running_loop().create_future();review.request.emit((asyncio.get_running_loop(),future,fc.name,args))
   try:allowed=await asyncio.wait_for(future,95)
   except asyncio.TimeoutError:allowed=False
   if not allowed:return engine_module.types.FunctionResponse(id=fc.id,name=fc.name,response={'result':'Cancelled or expired. No action was executed.'})
  call=engine_module.types.FunctionCall(id=fc.id,name=fc.name,args=args)
  result=await execute(self,call);record('task','Advanced '+fc.name,json.dumps({'arguments':args,'actual_result':result.response},ensure_ascii=False,default=str));return result
 def remote_key(self):
  from memory.config_manager import _save_flag
  _save_flag('dashboard_https',True)
  if not server._ensure_certs():write_log('SYS: HTTPS certificate generation failed; remote server remains off.');return None
  remote_enabled.set();return make_key(self)
 engine_module.JarvisLive._execute_tool=execute_reviewed;engine_module.JarvisLive._make_remote_key=remote_key

 def tick():
  import psutil
  if (data/'advanced/stop.request').exists() or (opts.parent and not psutil.pid_exists(opts.parent)):window._app.quit();return
  request=data/'advanced/activate.request'
  if request.exists():request.unlink();window._win.showNormal();window._win.raise_();window._win.activateWindow()
 timer=QTimer();timer.timeout.connect(tick);timer.start(400)
 if opts.smoke:
  from memory.config_manager import _save_flag
  _save_flag('push_to_talk_enabled',False)
  engine=engine_module.JarvisLive(window)
  assert len(engine._action_registry.names())==17,engine._action_registry.names()
  engine._build_config()
  print('PASS: 17 actions discovered; SDK Live config and Qt workspace constructed.',flush=True)
  window.write_log('SYS: Synthetic UI check; no microphone, model connection or network listener started.')
  QTimer.singleShot(1400,window._app.quit)
 else:
  def runner():
   window.wait_for_api_key();engine=engine_module.JarvisLive(window)
   try:asyncio.run(engine.run())
   except Exception as exc:write_log('ERR: Advanced engine stopped: '+clean(str(exc),cfg))
  threading.Thread(target=runner,daemon=True,name='SARU-advanced-engine').start()
 window.root.mainloop();secure.restore()

if __name__=='__main__':
 try:main()
 except Exception as exc:
  if '--smoke' in sys.argv:
   import traceback
   traceback.print_exc()
  # Never persist an SDK exception containing a key, transcript or tool payload.
  path=Path(sys.argv[sys.argv.index('--runtime')+1]).resolve().parent/'startup-error.txt'
  path.write_text('Advanced startup failed: '+type(exc).__name__+'. Check dependencies and reviewed bundle integrity.\n',encoding='utf8')
  raise SystemExit(1)
