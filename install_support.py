"""Per-user Windows installation metadata, manifests and size accounting."""
import datetime
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import stat

APP_ID='SARU_AI_Studio'
from version import VERSION
UNINSTALL_KEY=r'Software\Microsoft\Windows\CurrentVersion\Uninstall\SARU_AI_Studio'
MANIFEST='saru-install.json'

def tree_bytes(root):
 root=Path(root);total=0
 if not root.exists():return 0
 for directory,folders,files in os.walk(root,followlinks=False):
  folders[:]=[name for name in folders if not (Path(directory)/name).is_symlink() and not (getattr((Path(directory)/name).lstat(),'st_file_attributes',0) & getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024))]
  for name in files:
   path=Path(directory)/name
   try:
    if not path.is_symlink():total+=path.stat().st_size
   except OSError:pass
 return total

def installed_location(registry=None):
 if registry is None:
  if os.name!='nt':return None
  import winreg as registry
 try:
  with registry.OpenKey(registry.HKEY_CURRENT_USER,UNINSTALL_KEY) as key:
   path=Path(registry.QueryValueEx(key,'InstallLocation')[0]).resolve()
  return path if (path/'app.py').is_file() else None
 except OSError:return None

def register_install(target,registry=None):
 if registry is None:
  import winreg as registry
 target=Path(target).resolve()
 command=subprocess.list2cmdline([str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32'/'WindowsPowerShell'/'v1.0'/'powershell.exe'),'-NoProfile','-ExecutionPolicy','Bypass','-File',str(target/'uninstall.ps1')])
 values={'DisplayName':'SARU AI','DisplayVersion':VERSION,'Publisher':'SARU AI','InstallLocation':str(target),'DisplayIcon':str(target/'saru.ico')+',0','UninstallString':command,'InstallDate':datetime.date.today().strftime('%Y%m%d'),'EstimatedSize':min(0xffffffff,math.ceil(tree_bytes(target)/1024)),'NoModify':1,'NoRepair':1}
 with registry.CreateKey(registry.HKEY_CURRENT_USER,UNINSTALL_KEY) as key:
  for name,value in values.items():registry.SetValueEx(key,name,0,registry.REG_DWORD if isinstance(value,int) else registry.REG_SZ,value)
 return values['EstimatedSize']

def source_files(source):
 source=Path(source)
 for item in source.iterdir():
  if item.is_file() and (item.suffix.lower() in ('.py','.md','.txt','.bat','.cmd','.ps1','.png','.jpg','.gif','.ico') or item.name=='wacrm_source.zip') and item.name not in ('settings.json','memory.db'):
   yield item.relative_to(source)
 guide=source/'MYRA_OFFICIAL_GUIDES'
 if guide.exists():
  for item in guide.rglob('*'):
   if item.is_file() and not item.is_symlink():yield item.relative_to(source)

def validate_target(target,source):
 target=Path(target).resolve();source=Path(source).resolve()
 if target==source or source in target.parents or target in source.parents:raise ValueError('Choose an install folder outside the source tree and its parents.')
 if target==Path(target.anchor) or target==Path.home().resolve():raise ValueError('Choose a dedicated SARU application folder.')
 if target.exists() and any(target.iterdir()) and not (target/'app.py').exists() and not (target/MANIFEST).exists():raise ValueError('The selected folder is not empty and is not an existing SARU installation.')
 return target

def copy_application(source,target):
 source=Path(source);target=validate_target(target,source);target.mkdir(parents=True,exist_ok=True)
 files=list(source_files(source));backup=target/'.saru-backups'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
 copied=[]
 try:
  for relative in files:
   dest=target/relative
   if dest.exists():
    saved=backup/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,saved)
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/relative,dest);copied.append(relative)
 except Exception:
  for relative in reversed(copied):
   saved=backup/relative
   if saved.exists():shutil.copy2(saved,target/relative)
   else:(target/relative).unlink(missing_ok=True)
  raise
 return files

def write_manifest(target,files):
 target=Path(target).resolve()
 old=[]
 if (target/MANIFEST).exists():
  data=json.loads((target/MANIFEST).read_text(encoding='utf8'))
  if data.get('app_id')!=APP_ID:raise ValueError('Unexpected installation manifest')
  old=data.get('files',[])
 names=sorted(set(old+[str(p).replace('\\','/') for p in files]+['Start SARU AI.cmd','uninstall.ps1',MANIFEST]))
 for name in names:
  if Path(name).is_absolute() or '..' in Path(name).parts or ':' in name:raise ValueError('Unsafe manifest path')
 data={'app_id':APP_ID,'version':VERSION,'install_location':str(target),'files':names,'managed_directories':['.venv','.python-runtime','.saru-backups','__pycache__']}
 temporary=target/(MANIFEST+'.tmp');temporary.write_text(json.dumps(data,indent=2),encoding='utf8');temporary.replace(target/MANIFEST)
