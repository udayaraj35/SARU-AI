"""Optional pinned MoneyPrinterTurbo runtime with a private environment and loopback API."""
import json
import os
from pathlib import Path,PurePosixPath
import re
import secrets
import subprocess
import sys
import zipfile
import requests

PIN='33dde166da7f75287ea727c10e37243f03d167c8'
REPO='harry0703/MoneyPrinterTurbo'

def marker(data):return Path(data)/'integrations'/'moneyprinter.json'

def install(data,report=lambda text:None):
 root=Path(data)/'integrations'/'MoneyPrinterTurbo'/PIN;root.mkdir(parents=True,exist_ok=True)
 archive=root.parent/(PIN+'.zip')
 if not (root/'.source-ready').is_file():
  report('Downloading the pinned MoneyPrinterTurbo source…')
  with requests.get('https://codeload.github.com/'+REPO+'/zip/'+PIN,stream=True,timeout=90) as response:
   response.raise_for_status();size=0
   with archive.open('wb') as output:
    for part in response.iter_content(1048576):
     size+=len(part)
     if size>350*1048576:raise ValueError('Backend archive exceeds 350 MiB.')
     output.write(part)
  with zipfile.ZipFile(archive) as package:
   total=0
   for item in package.infolist():
    parts=PurePosixPath(item.filename).parts[1:]
    if not parts or item.is_dir():continue
    if '..' in parts or any(':' in p or '\\' in p for p in parts) or (item.external_attr>>16)&0o170000==0o120000:raise ValueError('Invalid archive member.')
    total+=item.file_size
    if total>600*1048576:raise ValueError('Expanded backend exceeds 600 MiB.')
    target=root.joinpath(*parts)
    if root.resolve() not in target.resolve().parents:raise ValueError('Archive escaped backend folder.')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(package.read(item))
  archive.unlink(missing_ok=True);(root/'.source-ready').write_text(PIN)
 # Keep site-packages paths short: litellm includes deeply nested web assets.
 runtime=Path(data)/'mpt-env';python=runtime/'Scripts'/'python.exe'
 if not python.is_file():
  report('Creating a separate Python environment…');subprocess.run([sys.executable,'-m','venv',str(runtime)],check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 report('Installing backend dependencies; this may take several minutes…')
 log=root.parent/'dependency-install.log'
 with log.open('w',encoding='utf8') as output:
  result=subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check','-r',str(root/'requirements.txt')],stdout=output,stderr=subprocess.STDOUT,timeout=1200,cwd=root,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if result.returncode:raise RuntimeError('Backend dependency installation failed. Review '+str(log))
 config=root/'config.toml'
 if not config.exists():
  content=(root/'config.example.toml').read_text(encoding='utf8').replace('listen_host = "0.0.0.0"','listen_host = "127.0.0.1"').replace('listen_port = 8080','listen_port = 8088')
  content=content.replace('api_key = ""','api_key = "'+secrets.token_urlsafe(32)+'"',1)
  config.write_text(content,encoding='utf8')
 payload={'root':str(root),'sha':PIN,'repo':REPO,'url':'http://127.0.0.1:8088'}
 marker(data).write_text(json.dumps(payload,indent=2),encoding='utf8');report('MoneyPrinterTurbo installed. Configure its providers before generating.');return payload

class MoneyPrinter:
 def __init__(self,data):
  self.data=data;self.process=None
 def info(self):
  path=marker(self.data)
  if not path.is_file():raise ValueError('Install the MoneyPrinterTurbo engine first.')
  info=json.loads(path.read_text(encoding='utf8'));root=Path(info['root'])
  expected=(Path(self.data)/'integrations'/'MoneyPrinterTurbo'/PIN).resolve()
  if root.resolve()!=expected or info.get('sha')!=PIN:raise ValueError('Unrecognized backend installation.')
  return info
 def start(self):
  info=self.info();root=Path(info['root'])
  if self.process and self.process.poll() is None:return
  import tomllib
  config=tomllib.loads((root/'config.toml').read_text(encoding='utf8'))
  if config.get('listen_host')!='127.0.0.1' or config.get('listen_port')!=8088:raise ValueError('Use listen_host 127.0.0.1 and listen_port 8088 in the backend config.')
  log_path=root.parent/'backend.log';self.start_offset=log_path.stat().st_size if log_path.exists() else 0
  log=log_path.open('a',encoding='utf8')
  try:self.process=subprocess.Popen([str(Path(self.data)/'mpt-env/Scripts/python.exe'),str(root/'main.py')],cwd=root,stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  finally:log.close()
 def request(self,method,path,body=None):
  info=self.info();import tomllib
  config=tomllib.loads((Path(info['root'])/'config.toml').read_text(encoding='utf8'));key=config.get('app',{}).get('api_key','')
  response=requests.request(method,info['url']+path,headers={'x-api-key':key},json=body,timeout=30,allow_redirects=False);response.raise_for_status()
  return response.json()
 def create(self,subject,script='',voice='en-US-AriaNeural-Female'):
  if not subject.strip():raise ValueError('Enter a video topic.')
  return self.request('POST','/api/v1/videos',{'video_subject':subject,'video_script':script,'video_aspect':'9:16','voice_name':voice,'subtitle_enabled':True,'video_count':1,'n_threads':2})
 def task(self,identifier):
  if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',identifier):raise ValueError('Invalid task id.')
  return self.request('GET','/api/v1/tasks/'+identifier)
 def wait_ready(self,seconds=90):
  import time
  deadline=time.monotonic()+seconds
  while time.monotonic()<deadline:
   if self.process and self.process.poll() is not None:
    log=Path(self.info()['root']).parent/'backend.log'
    text=log.read_bytes()[getattr(self,'start_offset',0):][-12000:].decode('utf8',errors='replace') if log.exists() else ''
    if 'ctranslate2.dll' in text:raise RuntimeError('Backend needs the Microsoft Visual C++ x64 runtime. See Microsoft runtime help, then restart the engine.')
    raise RuntimeError('Backend exited. Review the local backend.log for its startup error.')
   try:
    result=self.request('GET','/api/v1/tasks')
    return result
   except requests.RequestException:time.sleep(.5)
  raise RuntimeError('Backend is not ready yet. Check backend.log and retry.')
 def stop(self):
  if self.process and self.process.poll() is None:self.process.terminate()
