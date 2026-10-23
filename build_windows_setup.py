"""Build a self-contained Windows setup UI with public app and clean stdlib runtime."""
import hashlib,json,os,subprocess,sys,zipfile
from pathlib import Path
from install_support import source_files
from version import VERSION

ROOT=Path(__file__).resolve().parent

def build():
 payload=ROOT/'build'/'setup_payload';payload.mkdir(parents=True,exist_ok=True)
 application=payload/'application.zip';runtime=payload/'python-runtime.zip'
 with zipfile.ZipFile(application,'w',zipfile.ZIP_DEFLATED) as archive:
  for relative in source_files(ROOT):archive.write(ROOT/relative,relative.as_posix())
 base=Path(sys.base_prefix)
 with zipfile.ZipFile(runtime,'w',zipfile.ZIP_DEFLATED) as archive:
  for item in base.iterdir():
   if item.is_file() and (item.suffix.lower() in ('.exe','.dll') or item.name=='LICENSE.txt'):archive.write(item,item.name)
  for name in ('Lib','DLLs','tcl'):
   for directory,folders,files in os.walk(base/name):
    folders[:]=[f for f in folders if f not in ('site-packages','__pycache__','test','tests')]
    for filename in files:
     item=Path(directory)/filename
     if item.suffix.lower() not in ('.pyc','.pyo') and not item.is_symlink():archive.write(item,item.relative_to(base).as_posix())
 checksums={item.name:hashlib.sha256(item.read_bytes()).hexdigest() for item in (application,runtime)}
 (payload/'checksums.json').write_text(json.dumps(checksums,indent=2),encoding='utf-8')
 for item in (application,runtime):
  with zipfile.ZipFile(item) as archive:assert archive.testzip() is None
 build_python=ROOT/'.setup-build-env'/'Scripts'/'python.exe'
 if not build_python.exists():subprocess.run([sys.executable,'-m','venv',str(ROOT/'.setup-build-env')],check=True)
 subprocess.run([str(build_python),'-m','pip','install','pyinstaller>=6,<7','pywin32'],check=True)
 subprocess.run([str(build_python),'-m','PyInstaller','--noconfirm','--clean','--onefile','--windowed','--name',f'SARU_AI_Setup_{VERSION}','--icon',str(ROOT/'saru.ico'),'--add-data',str(payload)+';setup_payload','--hidden-import','win32crypt','--hidden-import','win32com.client','--hidden-import','pythoncom',str(ROOT/'setup_bootstrap.py')],cwd=ROOT,check=True)
 exe=ROOT/'dist'/f'SARU_AI_Setup_{VERSION}.exe';digest=hashlib.sha256(exe.read_bytes()).hexdigest();exe.with_suffix('.exe.sha256').write_text(digest+'  '+exe.name+'\n',encoding='ascii')
 print('SETUP READY:',exe,'MiB:',round(exe.stat().st_size/1024/1024,1))

if __name__=='__main__':build()
