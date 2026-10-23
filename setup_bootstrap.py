"""Standalone SARU setup entry point with embedded public source and Python runtime."""
import json,hashlib,os,sys,tempfile,zipfile
from pathlib import Path


def verified_payload(root,name,metadata):
 path=root/name
 if hashlib.sha256(path.read_bytes()).hexdigest()!=metadata[name]:raise RuntimeError('Setup payload checksum failed: '+name)
 return path


def main():
 import tkinter as tk
 from tkinter import messagebox
 root=tk.Tk();root.withdraw()
 try:
  payload=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'setup_payload'
  metadata=json.loads((payload/'checksums.json').read_text(encoding='utf-8'))
  source_zip=verified_payload(payload,'application.zip',metadata);runtime_zip=verified_payload(payload,'python-runtime.zip',metadata)
  os.environ['SARU_BUNDLED_PYTHON_ZIP']=str(runtime_zip)
  with tempfile.TemporaryDirectory(prefix='SARU-Setup-') as directory:
   folder=Path(directory)
   with zipfile.ZipFile(source_zip) as archive:
    for item in archive.infolist():
     path=(folder/item.filename).resolve()
     if folder.resolve() not in path.parents or Path(item.filename).is_absolute() or ':' in item.filename:raise RuntimeError('Invalid application payload path')
    archive.extractall(folder)
   from installer import SetupWizard
   if '--self-test' in sys.argv:
    import subprocess
    from installer_backend import prepare_python
    from unittest.mock import patch
    target=folder/'qa-install';target.mkdir()
    python=prepare_python(target,lambda text:None)
    result=subprocess.run([str(python),'-c','import tkinter,ssl,venv; print("Runtime OK")'],capture_output=True,text=True,env=__import__('installer_backend').runtime_environment())
    if result.returncode:raise RuntimeError('Bundled runtime check failed: '+result.stderr)
    with patch.dict(os.environ,{'LOCALAPPDATA':str(folder/'qa-local'),'APPDATA':str(folder/'qa-roaming')}),patch('installer.installed_location',return_value=None):wizard=SetupWizard(root,source=folder,backend=lambda *args:[])
    assert wizard.mode=='Install';wizard.page=3;wizard.show();assert wizard.next_button.cget('text')=='Install'
    wizard.mode='Update';wizard.show();assert wizard.next_button.cget('text')=='Update'
    report=Path(sys.argv[sys.argv.index('--report')+1])
    report.write_text('PASS: embedded payload checksums, clean bundled Python/venv/Tk/SSL, Install and Update wizard buttons. No application install, registry changes, device recording or account actions.',encoding='utf-8')
    root.destroy();return
   root.deiconify();SetupWizard(root,source=folder);root.mainloop()
 except Exception as exc:
  if '--self-test' in sys.argv and '--report' in sys.argv:
   Path(sys.argv[sys.argv.index('--report')+1]).write_text('FAIL: '+str(exc),encoding='utf-8');root.destroy();raise SystemExit(1)
  messagebox.showerror('SARU Setup',str(exc),parent=root)
  try:root.destroy()
  except Exception:pass

if __name__=='__main__':main()
