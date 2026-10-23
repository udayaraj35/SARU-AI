"""Real Tk wizard navigation test, with all installation effects mocked."""
from pathlib import Path
import tempfile
import time
import tkinter as tk
from unittest.mock import patch
from installer import SetupWizard

with tempfile.TemporaryDirectory(prefix='.setup-test-',dir=Path(__file__).resolve().parent.parent) as temp:
 calls=[]
 def backend(source,target,options,api,emit):
  calls.append((str(target),dict(api)));emit('Synthetic install test');return []
 root=tk.Tk()
 with patch.dict('os.environ',{'LOCALAPPDATA':temp}),patch('installer.installed_location',return_value=None):wizard=SetupWizard(root,backend=backend)
 try:
  assert wizard.page==0 and wizard.mode=='Install';wizard.next();assert wizard.page==1
  wizard.destination.set(str(Path(temp)/'Installed SARU'));wizard.next();assert wizard.page==2
  wizard.api_key.set('discard-this-synthetic-key');wizard.skip();assert wizard.page==3 and wizard.api_key.get()==''
  assert wizard.next_button.cget('text')=='Install'
  wizard.back();assert wizard.page==2
  wizard.provider.set('OpenAI');wizard.api_key.set('synthetic-test-only');wizard.model.set('test-model');wizard.next();assert wizard.page==3
  wizard.start_install()
  until=time.monotonic()+4
  while not wizard.success and time.monotonic()<until:root.update();time.sleep(.01)
  assert wizard.success and wizard.page==5
  assert calls[0][1]['key']=='synthetic-test-only';assert wizard.api_key.get()==''
  wizard.launch.set(False)
  root.update_idletasks()
  print('PASS: Next, Back, API Skip, optional API payload, progress and Finish. No installation/registry effects.')
 finally:root.destroy()

root=tk.Tk()
with patch('installer.installed_location',return_value=Path('C:/SARU Existing')):
 wizard=SetupWizard(root,backend=backend)
try:
 assert wizard.mode=='Update';wizard.page=3;wizard.show()
 assert wizard.next_button.cget('text')=='Update'
 print('PASS: existing installation shows Update; new installation shows Install.')
finally:root.destroy()
