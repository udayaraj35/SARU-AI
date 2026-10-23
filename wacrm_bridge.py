"""Pinned WACRM local server + official scoped REST adapter. No personal-Web scraping."""
from pathlib import Path
import json,os,re,secrets,shutil,subprocess,threading,zipfile
from urllib.parse import urlsplit
import requests

PIN='34bce1a8abf56281505d90bac165123b6ab7d51a'
ENV_KEYS={'NEXT_PUBLIC_SUPABASE_ANON_KEY':'WACRM_ANON','SUPABASE_SERVICE_ROLE_KEY':'WACRM_SERVICE_ROLE','ENCRYPTION_KEY':'WACRM_ENCRYPTION','META_APP_SECRET':'WACRM_META_SECRET'}

def install_directory(cfg):
 return Path(cfg.get('wacrm_install_dir') or ('D:/SARU_AI/Integrations/wacrm' if Path('D:/').is_dir() else str(Path.home()/'AppData'/'Local'/'SARU_AI'/'wacrm'))).resolve()

def checked_origin(value):
 p=urlsplit(value)
 if p.username or p.password or p.query or p.fragment or p.path not in ('','/') or (p.scheme!='https' and not (p.scheme=='http' and p.hostname in ('127.0.0.1','localhost','::1'))):raise ValueError('Use an HTTPS CRM origin, or HTTP on localhost only, without credentials/path/query.')
 if not p.hostname:raise ValueError('CRM host is required.')
 return value.rstrip('/')

def runtime_environment(cfg):
 env=dict(os.environ);env['NEXT_PUBLIC_SUPABASE_URL']=cfg.get('wacrm_supabase_url','').strip()
 for name,key in ENV_KEYS.items():env[name]=cfg.get('keys',{}).get(key,'').strip()
 missing=[name for name in ('NEXT_PUBLIC_SUPABASE_URL',*ENV_KEYS) if not env.get(name)]
 if missing:raise ValueError('WACRM setup required: '+', '.join(missing)+'. Enter these in the local WhatsApp CRM setup form.')
 checked_origin(env['NEXT_PUBLIC_SUPABASE_URL'])
 if not re.fullmatch('[0-9a-fA-F]{64}',env['ENCRYPTION_KEY']):raise ValueError('WACRM encryption key must be 64 hex characters.')
 env.update(NEXT_PUBLIC_SITE_URL='http://127.0.0.1:3876',NEXT_PUBLIC_APP_LOCALE='en',NEXT_TELEMETRY_DISABLED='1')
 return env

def install_local(cfg,report=lambda text:None):
 target=install_directory(cfg);archive=Path(__file__).with_name('wacrm_source.zip')
 if not (target/'package.json').is_file():
  if target.exists() and any(target.iterdir()):raise ValueError('WACRM target is not empty; choose its existing installation.')
  if not archive.is_file():raise ValueError('Pinned WACRM source bundle is missing. Use the current SARU installer.')
  target.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(archive) as z:
   for item in z.infolist():
    path=(target/item.filename).resolve()
    if target not in path.parents:raise ValueError('Invalid WACRM bundle path.')
   z.extractall(target)
 npm=shutil.which('npm.cmd')
 if not npm:raise ValueError('Install Node.js 22.12 or newer, then retry WACRM dependencies.')
 report('Installing pinned WACRM dependencies; package lifecycle scripts are disabled…')
 result=subprocess.run([npm,'ci','--ignore-scripts','--no-audit','--no-fund'],cwd=target,capture_output=True,text=True,timeout=600,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if result.returncode:raise RuntimeError('WACRM dependency installation failed; check network/Node version and retry. No account connected.')
 mcp=target/'mcp-server'
 if (mcp/'package-lock.json').is_file():
  for args in ([npm,'ci','--ignore-scripts','--no-audit','--no-fund'],[npm,'run','build']):
   result=subprocess.run(args,cwd=mcp,capture_output=True,text=True,timeout=600,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   if result.returncode:raise RuntimeError('WACRM web dependencies installed, but MCP component setup failed. Retry repair.')
 return 'WACRM source and Node dependencies installed. Configure Supabase and Meta before starting.'

class LocalCRM:
 def __init__(self):self.process=None
 def start(self,cfg,report=lambda text:None):
  if self.process and self.process.poll() is None:return 'WACRM is already running locally.'
  env=runtime_environment(cfg);folder=install_directory(cfg);cli=folder/'node_modules'/'next'/'dist'/'bin'/'next';node=shutil.which('node.exe') or shutil.which('node')
  if not node or not cli.is_file():raise ValueError('Install/repair WACRM dependencies first.')
  self.process=subprocess.Popen([node,str(cli),'dev','--hostname','127.0.0.1','--port','3876'],cwd=folder,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  process=self.process;private=[v for k,v in env.items() if k in ENV_KEYS]
  def read():
   for line in process.stdout:
    for value in private:
     if value:line=line.replace(value,'[redacted]')
    report(line.strip()[:400])
  threading.Thread(target=read,daemon=True).start()
  return 'WACRM start requested on http://127.0.0.1:3876. Wait for Ready; database/Meta connection is not verified by starting the server.'
 def stop(self):
  if self.process and self.process.poll() is None:
   import psutil
   try:
    parent=psutil.Process(self.process.pid);children=parent.children(recursive=True)
    for child in reversed(children):child.terminate()
    self.process.terminate()
   except psutil.Error:pass
  self.process=None

local_crm=LocalCRM()

class CRMClient:
 def __init__(self,cfg,session=requests):
  self.base=checked_origin(cfg.get('wacrm_api_url','http://127.0.0.1:3876'));self.key=cfg.get('keys',{}).get('WACRM_API','');self.session=session
  if not self.key:raise ValueError('Save a scoped WACRM API key in local WhatsApp CRM setup first.')
 def request(self,method,path,body=None):
  if method not in ('GET','POST') or path not in ('me','contacts','conversations','messages'):raise ValueError('Unsupported CRM operation.')
  r=self.session.request(method,self.base+'/api/v1/'+path,headers={'Authorization':'Bearer '+self.key},json=body,timeout=20,allow_redirects=False)
  if r.status_code not in (200,201):raise RuntimeError('WACRM request failed: HTTP '+str(r.status_code)+'. Check server/account/scopes. No automatic retry.')
  return r.json()
 def send(self,to,text):
  if not re.fullmatch(r'\+[1-9]\d{7,14}',to) or not text.strip() or len(text)>4096:raise ValueError('Use an exact +country-code phone number and 1–4096 character message.')
  return self.request('POST','messages',{'to':to,'type':'text','text':text})
