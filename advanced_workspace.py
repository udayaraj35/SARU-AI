"""SARU launcher for reviewed Mark LVI source in a separate process/environment."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path

def bundle_manifest(root):
 bundle=Path(root)/'mark_suite';data=json.loads((bundle/'SOURCE_INVENTORY.json').read_text(encoding='utf8'))
 for entry in data['files']:
  relative=Path(entry['path'])
  if relative.is_absolute() or '..' in relative.parts or ':' in str(relative):raise ValueError('Unsafe bundled path')
  path=bundle/relative
  if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Advanced source changed without review: '+entry['path'])
 return data

def prepare_runtime(root,data):
 root=Path(root);manifest=bundle_manifest(root);runtime=Path(data)/'advanced/runtime';runtime.mkdir(parents=True,exist_ok=True)
 for entry in manifest['files']:
  source=root/'mark_suite'/entry['path'];target=runtime/entry['path'];target.parent.mkdir(parents=True,exist_ok=True)
  if target.is_symlink():raise ValueError('Symlink in workspace runtime')
  if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest()!=entry['sha256']:
   if target.exists():
    backup=Path(data)/'advanced/source-backups'/entry['sha256']/entry['path'];backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
   shutil.copy2(source,target)
 # Source-only metadata. Config, memories, sessions and approved plugins stay private.
 shutil.copy2(root/'mark_suite/SOURCE_INVENTORY.json',runtime/'SOURCE_INVENTORY.json')
 return runtime

def advanced_python(root,windowed=False):
 name='pythonw.exe' if windowed else 'python.exe'
 for env in [Path(root)/'.advanced-env',Path(os.environ.get('LOCALAPPDATA',''))/'Programs/SARU AI/.advanced-env']:
  path=env/'Scripts'/name
  if path.is_file():return path
 return None

class AdvancedWorkspace:
 def __init__(self,root,data,config,tkroot,voice_hub,report):
  self.root=Path(root);self.data=Path(data);self.config=config;self.tkroot=tkroot;self.voice=voice_hub;self.report=report;self.process=None;self.resume=False;self.closed=False;self.starting=False
 @property
 def active(self):return bool(self.process and self.process.poll() is None)
 def start(self):
  if self.starting:return 'Advanced workspace is already starting.'
  if self.active:
   (self.data/'advanced/activate.request').write_text('show',encoding='ascii');return 'Advanced workspace is already running; requested its window.'
  python=advanced_python(self.root,True)
  if not python:raise ValueError('Advanced dependencies are not installed. Open Advanced workspace → Install dependencies.')
  runtime=prepare_runtime(self.root,self.data)
  for name in ('stop.request','activate.request'):(self.data/'advanced'/name).unlink(missing_ok=True)
  self.resume=bool(self.voice.engine and self.voice.engine.active)
  self.starting=True
  if self.resume:self.voice.stop()
  # Wait for microphone cleanup before the child takes ownership of the device.
  def launch():
   if self.closed or not self.starting:return
   if self.voice.engine and self.voice.engine.active:self.tkroot.after(100,launch);return
   env=os.environ.copy();env['PYTHONUTF8']='1';env['PLAYWRIGHT_BROWSERS_PATH']=str(self.data/'advanced/browsers')
   self.starting=False
   try:self.process=subprocess.Popen([str(python),str(self.root/'advanced_bootstrap.py'),'--runtime',str(runtime),'--parent',str(os.getpid())],cwd=self.root,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   except OSError as exc:
    self.report('Advanced workspace could not start: '+str(exc))
    if self.resume:self.voice.start()
    self.resume=False;return
   self.tkroot.after(600,self.poll)
  launch();return 'Advanced workspace starting. SARU main voice pauses while it owns the microphone. Hold Ctrl+Space to talk there.'
 def poll(self):
  if self.closed:return
  if self.active:self.tkroot.after(600,self.poll);return
  code=self.process.returncode if self.process else 0
  self.report('Advanced workspace closed.' if code==0 else 'Advanced workspace failed to start; check its dependency status and private advanced/startup-error.txt.')
  if self.resume and self.config.get('auto_listen',True) and self.voice.auto_enabled:self.voice.start()
  self.resume=False
 def stop(self):
  pending=self.starting
  self.starting=False
  if self.active:(self.data/'advanced/stop.request').write_text('stop',encoding='ascii');return 'Advanced workspace stop requested.'
  if pending and self.resume and not self.closed and self.voice.auto_enabled:self.voice.start()
  self.resume=False
  return 'Advanced workspace is not running.'
 def close(self):self.closed=True;self.stop()
