"""Find registered Start Menu applications; never execute user-provided shell text."""
import os
from pathlib import Path
from dataclasses import dataclass
import json
import re
import subprocess

def find_apps(name,roots=None):
 if not name or len(name)>100 or any(c in name for c in ('/','\\',':',';','|','&','\n','\r')):raise ValueError('Use the app name only, without a path or command.')
 if roots is None:
  roots=[Path(os.getenv('APPDATA',''))/'Microsoft/Windows/Start Menu/Programs',Path(os.getenv('PROGRAMDATA',r'C:\ProgramData'))/'Microsoft/Windows/Start Menu/Programs']
 exact=[];partial=[];seen=set();query=name.casefold().strip()
 for root in roots:
  root=Path(root)
  if not root.is_dir():continue
  for directory,folders,files in os.walk(root,followlinks=False):
   folders[:]=[f for f in folders if not (Path(directory)/f).is_symlink()]
   for file in files:
    path=Path(directory)/file
    if path.suffix.casefold()!='.lnk' or path.is_symlink():continue
    title=path.stem.casefold()
    if title in seen:continue
    seen.add(title)
    if title==query:exact.append(path)
    elif query in title:partial.append(path)
 return exact or partial[:20]

@dataclass(frozen=True)
class AppEntry:
 title:str
 kind:str
 target:str

def builtin_apps():
 root=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32'
 names={'Notepad':'notepad.exe','Calculator':'calc.exe','Task Manager':'taskmgr.exe','Paint':'mspaint.exe','File Explorer':'explorer.exe'}
 entries=[AppEntry(title,'exe',str(root/name)) for title,name in names.items() if (root/name).is_file()]
 if (root.parent/'explorer.exe').is_file():entries.append(AppEntry('File Explorer','exe',str(root.parent/'explorer.exe')))
 return entries

def installed_apps(extra=None,include_registered=True):
 """Catalog shortcuts, registered executables, Store apps and selected portable apps."""
 result=builtin_apps()
 roots=[Path(os.getenv('APPDATA',''))/'Microsoft/Windows/Start Menu/Programs',Path(os.getenv('PROGRAMDATA',r'C:\ProgramData'))/'Microsoft/Windows/Start Menu/Programs']
 for root in roots:
  if root.is_dir():
   for directory,folders,files in os.walk(root,followlinks=False):
    folders[:]=[name for name in folders if not (Path(directory)/name).is_symlink()]
    for name in files:
     path=Path(directory)/name
     if path.suffix.lower()=='.lnk' and not path.is_symlink():result.append(AppEntry(path.stem,'shortcut',str(path)))
 if os.name=='nt':
  import winreg
  for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
   for access in (winreg.KEY_READ,winreg.KEY_READ|winreg.KEY_WOW64_32KEY):
    try:
     with winreg.OpenKey(hive,r'Software\Microsoft\Windows\CurrentVersion\App Paths',0,access) as registry:
      index=0
      while True:
       try:name=winreg.EnumKey(registry,index);index+=1
       except OSError:break
       try:
        with winreg.OpenKey(registry,name) as child:target=str(winreg.QueryValue(child,None)).strip('"')
        if Path(target).suffix.lower()=='.exe' and Path(target).is_file():result.append(AppEntry(Path(name).stem,'exe',target))
       except OSError:pass
    except OSError:pass
  try:
   if not include_registered:return _unique_entries(result,extra)
   shell=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
   command="[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); @(Get-StartApps | Select-Object Name,AppID) | ConvertTo-Json -Compress"
   response=subprocess.run([str(shell),'-NoProfile','-NonInteractive','-Command',command],capture_output=True,encoding='utf-8-sig',timeout=8,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   if response.returncode==0:
    data=json.loads(response.stdout)
    if isinstance(data,dict):data=[data]
    for item in data:
     appid=item.get('AppID','')
     if isinstance(appid,str) and re.fullmatch(r'[A-Za-z0-9_.!{}+-]{1,250}',appid):result.append(AppEntry(item['Name'],'registered',appid))
  except (OSError,ValueError,subprocess.TimeoutExpired):pass
 return _unique_entries(result,extra)

def _unique_entries(result,extra=None):
 result=list(result)
 for title,target in (extra or {}).items():
  if Path(target).suffix.lower()=='.exe' and Path(target).is_file():result.append(AppEntry(title,'exe',target))
 seen=set();unique=[]
 for entry in result:
  key=(entry.title.casefold(),entry.target.casefold())
  if key not in seen:seen.add(key);unique.append(entry)
 return sorted(unique,key=lambda item:item.title.casefold())

def match_entries(name,entries):
 if not name or len(name)>100 or any(c in name for c in ('/','\\',':',';','|','&','\n','\r')):raise ValueError('Use an application name without commands or arguments.')
 query=name.casefold().strip()
 query={'vs code':'visual studio code','vscode':'visual studio code','ms word':'word','ms excel':'excel','explorer':'file explorer','calc':'calculator'}.get(query,query)
 exact=[entry for entry in entries if entry.title.casefold()==query]
 matches=exact or [entry for entry in entries if query in entry.title.casefold()]
 # Prefer a standard shortcut when StartApps lists the same title again.
 titles={}
 for entry in matches:
  key=entry.title.casefold()
  priority={'registered':0,'exe':1,'shortcut':2}
  if key not in titles or priority.get(entry.kind,0)>priority.get(titles[key].kind,0):titles[key]=entry
 return list(titles.values())[:30]

def launch_entry(entry):
 if entry.kind in ('exe','shortcut'):
  path=Path(entry.target)
  if not path.is_file() or path.suffix.lower()!=('.exe' if entry.kind=='exe' else '.lnk'):raise ValueError('Application path is no longer available.')
  if entry.kind=='exe':return subprocess.Popen([str(path)],cwd=path.parent).pid
  else:os.startfile(str(path))
 elif entry.kind=='registered' and re.fullmatch(r'[A-Za-z0-9_.!{}+-]{1,250}',entry.target):
  if '!' in entry.target:
   from windows_activation import activate_registered
   return activate_registered(entry.target)
  os.startfile('shell:AppsFolder\\'+entry.target)
 else:raise ValueError('Unsupported application entry.')
