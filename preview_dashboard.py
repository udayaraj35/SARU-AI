"""Disposable no-audio visual preview for desktop UI review."""
import os,sys
from pathlib import Path
import tempfile
import tkinter as tk
import runpy
base=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='.gui-test-',dir=base) as temp:
 os.environ['SARU_DATA_DIR']=temp;os.environ['SARU_DISABLE_AUTOLISTEN']='1'
 original=tk.Misc.mainloop
 def preview(root,*args,**kwargs):
  import inspect
  app=inspect.currentframe().f_back.f_globals
  root.title('SARU Reference Preview');root.geometry('1280x790');app['orb'].withdraw()
  if '--fullscreen' in sys.argv:root.attributes('-fullscreen',True)
  def finish():app['voice_hub'].close();app['con'].close();root.destroy()
  root.after(120000,finish);original(root)
 tk.Misc.mainloop=preview
 try:runpy.run_path(str(base/'app.py'),run_name='__main__')
 finally:tk.Misc.mainloop=original
