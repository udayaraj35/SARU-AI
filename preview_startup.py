"""Visual QA only: hold the real startup after its services check, without audio."""
import os,inspect,runpy,tempfile,tkinter as tk
from pathlib import Path
from startup_screen import StartupScreen

base=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='.gui-test-',dir=base) as temp:
 os.environ['SARU_DATA_DIR']=temp;os.environ['SARU_DISABLE_AUTOLISTEN']='1'
 complete=StartupScreen.complete;mainloop=tk.Misc.mainloop
 def paused(self,key):
  complete(self,key)
  if key=='services':
   self.window.overrideredirect(False)
   self.window.title('SARU Loading Preview · Visual QA')
   gate=tk.BooleanVar(self.root,value=False)
   self.root.after(45000,lambda:gate.set(True));self.root.wait_variable(gate)
 def preview(root,*args,**kwargs):
  app=inspect.currentframe().f_back.f_globals;root.title('SARU Assistant Preview · Visual QA');app['orb'].withdraw()
  def finish():app['voice_hub'].close();app['con'].close();root.destroy()
  root.after(90000,finish);mainloop(root)
 StartupScreen.complete=paused;tk.Misc.mainloop=preview
 try:runpy.run_path(str(base/'app.py'),run_name='__main__')
 finally:StartupScreen.complete=complete;tk.Misc.mainloop=mainloop
