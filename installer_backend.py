"""Installer backend. No UI calls from worker threads; API secrets travel via stdin."""
import json
import os
from pathlib import Path
import subprocess
import sys
from install_support import copy_application,write_manifest,register_install

def runtime_environment():
 environment=dict(os.environ)
 for name in ('TCL_LIBRARY','TK_LIBRARY','PYTHONHOME','PYTHONPATH','SARU_BUNDLED_PYTHON_ZIP'):environment.pop(name,None)
 return environment

API_SCRIPT='''import json,os,sys
from pathlib import Path
from settings_store import SettingsStore
payload=json.load(sys.stdin)
path=Path(os.environ.get('APPDATA',str(Path.home())))/'SARU_AI'/'settings.json'
store=SettingsStore(path,{'keys':{}})
cfg=store.load()
cfg.setdefault('keys',{})[payload['provider']]=payload['key']
cfg['provider']=payload['provider']
cfg['model']=payload.get('model') or cfg.get('provider_models',{}).get(payload['provider'],'')
if payload.get('model'):
 cfg.setdefault('provider_models',{})[payload['provider']]=payload['model']
if payload.get('custom_url'):cfg['custom_url']=payload['custom_url']
store.save(cfg)
'''

PREFERENCES_SCRIPT="import json,os,sys\nfrom pathlib import Path\nfrom settings_store import SettingsStore\npayload=json.load(sys.stdin)\npath=Path(os.environ.get('APPDATA',str(Path.home())))/'SARU_AI'/'settings.json'\nstore=SettingsStore(path,{'keys':{}});cfg=store.load()\ncfg['auto_listen']=bool(payload['auto_listen']);store.save(cfg)\n"

def configure_api(python,target,api,runner=subprocess.run):
 if not api or not api.get('key','').strip():return False
 # No API key in arguments, logs or a temporary plaintext file.
 result=runner([str(python),'-c',API_SCRIPT],input=json.dumps(api),cwd=str(target),capture_output=True,text=True,env=runtime_environment(),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if result.returncode:raise RuntimeError('API settings could not be encrypted. Existing settings were preserved. Configure the key later in Settings.')
 return True

def prepare_python(target,emit):
 python=target/'.venv'/'Scripts'/'python.exe'
 if python.exists():return python
 runtime_archive=os.getenv('SARU_BUNDLED_PYTHON_ZIP')
 base=sys.executable
 if runtime_archive:
  import zipfile
  runtime=target/'.python-runtime'
  if runtime.exists() and (runtime.is_symlink() or runtime.resolve().parent!=target.resolve()):raise ValueError('Linked Python runtime folders are not supported.')
  runtime.mkdir(exist_ok=True)
  if not (runtime/'.complete').exists() or not (runtime/'python.exe').exists():
   emit('Installing bundled Python runtime…')
   with zipfile.ZipFile(runtime_archive) as archive:
    for item in archive.infolist():
     path=(runtime/item.filename).resolve()
     if runtime.resolve() not in path.parents or Path(item.filename).is_absolute() or ':' in item.filename:raise ValueError('Invalid bundled runtime path')
    archive.extractall(runtime)
   (runtime/'.complete').write_text('SARU bundled Python runtime',encoding='ascii')
  base=str(runtime/'python.exe')
 elif getattr(sys,'frozen',False):raise RuntimeError('Bundled Python runtime missing. Use the complete SARU Setup executable.')
 emit('Creating isolated Python environment…')
 result=subprocess.run([base,'-m','venv',str(target/'.venv')],capture_output=True,text=True,env=runtime_environment(),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if result.returncode:raise RuntimeError('Bundled Python environment failed: '+str(result.returncode)+' '+(result.stderr or result.stdout)[-1500:])
 return python

def install_application(source,target,options,api,emit):
 source=Path(source);target=Path(target)
 warnings=[]
 emit('Backing up previous files and copying SARU…');files=copy_application(source,target)
 python=prepare_python(target,emit)
 emit('Installing dependencies. This may take several minutes…')
 result=subprocess.run([str(python),'-m','pip','install','-r',str(target/'requirements.txt')],capture_output=True,text=True,env=runtime_environment(),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if result.returncode:raise RuntimeError('Dependency installation failed. Check your Internet connection and retry.\n'+result.stderr[-1200:])
 emit('Preparing local semantic memory and private social browser…')
 try:
  result=subprocess.run([str(python),str(target/'backend_setup.py'),'--memory','--browser','--receipt'],capture_output=True,text=True,env=runtime_environment(),timeout=600,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  if result.returncode:warnings.append('Backend model/browser setup incomplete. Run backend_setup.py --memory --browser --receipt to retry. Existing memory/keys are preserved.')
 except subprocess.TimeoutExpired:warnings.append('Backend setup timed out; retry backend_setup.py --memory --browser --receipt when connected.')
 if options.get('voice_profiles',True):
  emit('Installing local voice-profile model (CPU)…')
  result=subprocess.run([str(python),str(target/'setup_voice_profiles.py')],capture_output=True,text=True,env=runtime_environment(),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  if result.returncode:raise RuntimeError('Voice-profile model setup failed. Retry, or uncheck this optional component and configure it later.\n'+result.stderr[-1200:])
 launcher=target/'Start SARU AI.cmd';launcher.write_text('@echo off\ncd /d "%~dp0"\nstart "" "%~dp0.venv\\Scripts\\pythonw.exe" "%~dp0launch_saru.py"\n',encoding='utf8')
 write_manifest(target,files)
 emit('Registering Control Panel / Installed apps…');size=register_install(target)
 if any(options.values()):
  import pythoncom
  pythoncom.CoInitialize()
  try:
   import win32com.client
   shell=win32com.client.Dispatch('WScript.Shell')
   for name,special in [('desktop','Desktop'),('startup','Startup'),('startmenu','Programs')]:
    if options.get(name):
     if name=='desktop':
      from shortcut_support import consolidate_desktop_shortcut
      consolidate_desktop_shortcut(shell,target,Path(shell.SpecialFolders(special)));continue
     link=shell.CreateShortcut(str(Path(shell.SpecialFolders(special))/'SARU AI.lnk'))
     link.TargetPath=str(launcher);link.WorkingDirectory=str(target);link.IconLocation=str(target/'saru.ico')+',0';link.Save()
   del shell
  finally:pythoncom.CoUninitialize()
 if api and api.get('key'):
  emit('Saving your API key with Windows encryption…')
  try:configure_api(python,target,api)
  except RuntimeError as exc:warnings.append(str(exc))
 if 'auto_listen' in options:
  result=subprocess.run([str(python),'-c',PREFERENCES_SCRIPT],input=json.dumps({'auto_listen':options['auto_listen']}),cwd=str(target),capture_output=True,text=True,env=runtime_environment(),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  if result.returncode:warnings.append('Automatic voice preference could not be saved; configure it in Settings → Voice.')
 emit(f'Installed size: {size/1024:.1f} MiB')
 return warnings
