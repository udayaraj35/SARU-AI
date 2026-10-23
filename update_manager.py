"""SARU update utilities. Never execute a downloaded update without explicit user confirmation."""
import os,sys,json,hashlib,zipfile,subprocess,shutil,tempfile,platform,re
from pathlib import Path
from urllib.parse import urlparse
import requests
ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('APPDATA',str(Path.home())))/'SARU_AI'
from version import VERSION
def latest_release(repo):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Expected owner/repository')
 r=requests.get('https://api.github.com/repos/'+repo+'/releases/latest',timeout=15);r.raise_for_status()
 obj=r.json();assets=obj.get('assets',[])
 packages=[a for a in assets if a['name'].lower().startswith('saru_ai_') and a['name'].lower().endswith('.zip')]
 checks=[a for a in assets if packages and a['name']==packages[0]['name']+'.sha256']
 return {'tag':obj.get('tag_name',''), 'page':obj.get('html_url',''), 'package':packages[0] if packages else None,'checksum':checks[0] if checks else None}
def _download(asset,dest):
 url=asset['browser_download_url']
 if urlparse(url).scheme!='https' or urlparse(url).hostname not in ('github.com','objects.githubusercontent.com','release-assets.githubusercontent.com'):raise ValueError('Untrusted download host')
 with requests.get(url,timeout=60,stream=True,allow_redirects=True) as r:
  r.raise_for_status()
  with open(dest,'wb') as f:
   size=0
   for part in r.iter_content(131072):
    size+=len(part)
    if size>250_000_000:raise ValueError('Package exceeds 250 MB limit')
    f.write(part)
def stage_verified_release(release):
 if not release['package'] or not release['checksum']:raise ValueError('Release must include SARU_AI_*.zip and .sha256 assets')
 staging=DATA/'update_staging';staging.mkdir(parents=True,exist_ok=True)
 for asset in (release['package'],release['checksum']):
  name=asset['name']
  if not name or '/' in name or '\\' in name or ':' in name or name in ('.','..'):raise ValueError('Unsafe release asset name')
 pkg=staging/release['package']['name'];checksum=staging/release['checksum']['name']
 _download(release['package'],pkg);_download(release['checksum'],checksum)
 digest=hashlib.sha256(pkg.read_bytes()).hexdigest();expected=checksum.read_text(encoding='utf8').split()[0].lower()
 if digest!=expected:pkg.unlink(missing_ok=True);raise ValueError('SHA256 checksum mismatch: update rejected')
 with zipfile.ZipFile(pkg) as z:
  for i in z.infolist():
   path=Path(i.filename)
   if path.is_absolute() or '..' in path.parts or i.is_dir() and i.filename.startswith('/') or i.file_size>100_000_000:raise ValueError('Unsafe archive entry')
  names=[n.replace('\\','/') for n in z.namelist()]
  if not any(n.endswith('/app.py') or n=='app.py' for n in names):raise ValueError('Missing app.py in update')
 return pkg

def external_updates_preview():
 if sys.platform!='win32':return 'Windows only'
 if not shutil.which('winget'):return 'winget is not installed (Windows 8 may not support it). Use vendor installers manually.'
 p=subprocess.run(['winget','upgrade','--include-unknown'],capture_output=True,text=True,timeout=60)
 return (p.stdout or p.stderr)[-9000:]

def launch_external_updates():
 if sys.platform!='win32':raise RuntimeError('Windows only')
 if not shutil.which('winget'):raise RuntimeError('winget not installed')
 # Opens visible terminal; user approves each update, no silent license acceptance.
 subprocess.Popen(['cmd','/k','winget upgrade --all --interactive'],creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_windows_update():
 if sys.platform=='win32':os.startfile('ms-settings:windowsupdate')
 else:raise RuntimeError('Windows only')

def is_newer(tag, current=VERSION):
 def parts(value):
  match=re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)',value)
  if not match:raise ValueError('Release version must be vMAJOR.MINOR.PATCH')
  return tuple(map(int,match.groups()))
 return parts(tag)>parts(current)

def configure_repository(value):
 value=value.strip().removeprefix('https://github.com/').rstrip('/')
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',value):raise ValueError('Use a GitHub owner/repository or repository URL.')
 return value
