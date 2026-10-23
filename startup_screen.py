"""SARU startup artwork with progress tied to completed initialization stages."""
from pathlib import Path
import tkinter as tk
from PIL import Image,ImageTk,ImageOps

STAGES=(('runtime','Windows interface ready'),('modules','Core modules loaded'),('settings','Saved settings unlocked'),('memory','Local memory opened'),('assets','Dashboard artwork prepared'),('services','Assistant services configured'),('interface','Main interface prepared'))

class StartupProgress:
 def __init__(self):self.completed=[];self.error=None
 @property
 def percent(self):return round(100*len(self.completed)/len(STAGES))
 def complete(self,key):
  expected=STAGES[len(self.completed)][0] if len(self.completed)<len(STAGES) else None
  if key!=expected:raise ValueError('Startup stages must complete in order: '+str(expected))
  self.completed.append(key)
 def ready(self):return self.percent==100 and self.error is None

class StartupScreen:
 def __init__(self,folder,root=None):
  self.root=root or tk.Tk();self.root.withdraw();self.folder=Path(folder);self.progress=StartupProgress();self.cancelled=False;self.closed=False
  self.window=tk.Toplevel(self.root);self.window.title('Starting SARU AI');self.window.overrideredirect(True);self.window.configure(bg='#061226');self.window.attributes('-topmost',True)
  width=min(1120,self.root.winfo_screenwidth()-80);height=round(width*9/16)
  self.width=width;self.height=height;self.window.geometry(f'{width}x{height}+{(self.root.winfo_screenwidth()-width)//2}+{(self.root.winfo_screenheight()-height)//2}')
  self.canvas=tk.Canvas(self.window,width=width,height=height,bg='#061226',highlightthickness=1,highlightbackground='#a52775');self.canvas.pack(fill='both',expand=True)
  self.background=None
  try:
   with Image.open(self.folder/'startup_scene.png') as image:self.background=ImageTk.PhotoImage(ImageOps.fit(image.convert('RGB'),(width,height)))
  except OSError:pass
  self.detail='Preparing your personal workspace';self.draw();self.window.bind('<Escape>',lambda event:self.cancel());self.window.protocol('WM_DELETE_WINDOW',self.cancel)
  self.root.update()
 def cancel(self):self.cancelled=True;self.window.withdraw()
 def complete(self,key):
  if self.cancelled:raise SystemExit(0)
  self.progress.complete(key);self.detail=dict(STAGES)[key];self.draw();self.root.update()
 def draw(self):
  if self.closed:return
  c=self.canvas;w=self.width;h=self.height;s=w/1120;c.delete('all')
  if self.background:c.create_image(0,0,image=self.background,anchor='nw')
  x=w*.59;right=w*.96
  c.create_rectangle(x-18,h*.12,right+10,h*.91,fill='#071226',outline='#32436c',width=2)
  def text(px,py,value,size,color='#f1f4ff',anchor='nw'):
   return c.create_text(px,py,text=value,fill=color,anchor=anchor,font=('Segoe UI',max(9,round(size*s)),'bold'))
  text(x,h*.19,'SARU',45);text(x+round(168*s),h*.19,'AI',45,'#ff367e')
  text(x,h*.30,'YOUR PERSONAL AI ASSISTANT',11,'#85ddf8')
  text(x,h*.39,'Think. Create. Explore.',17)
  text(x,h*.44,'Your intelligent workspace.',12,'#b1bad6')
  detail=self.progress.error or self.detail
  c.create_text(x,h*.56,text=detail,anchor='nw',fill='#ffb4c8' if self.progress.error else '#edf4ff',font=('Segoe UI',max(9,round(11*s)),'bold'),width=right-x)
  y=h*.64;barw=right-x-45*s
  c.create_rectangle(x,y,x+barw,y+9*s,fill='#17213d',outline='#567294')
  if self.progress.percent:c.create_rectangle(x,y,x+barw*self.progress.percent/100,y+9*s,fill='#ff2775',outline='')
  text(right,y-4*s,str(self.progress.percent)+'%',11,anchor='ne')
  for i,(symbol,name) in enumerate((('◈','MIND'),('◎','MEMORY'),('▦','TEAM'),('◖','VOICE'))):
   tx=x+i*(right-x)/4;tw=(right-x)/4-8*s
   c.create_rectangle(tx,h*.72,tx+tw,h*.81,fill='#101b35',outline='#663756')
   text(tx+tw/2,h*.735,symbol,15,'#ff4b91',anchor='n');text(tx+tw/2,h*.782,name,8,anchor='n')
  text(x,h*.86,f'{len(self.progress.completed)} / {len(STAGES)} startup checks complete',9,'#a6b5d5')
  c.create_text(w-18,18,text='×',fill='white',font=('Segoe UI',17,'bold'),tags='close');c.tag_bind('close','<Button-1>',lambda event:self.cancel())
 def fail(self,message):
  self.progress.error='Startup needs attention: '+str(message)[:180];self.draw();self.window.attributes('-topmost',False);self.root.update()
 def close(self):
  if self.closed:return
  self.closed=True
  try:self.window.destroy()
  except tk.TclError:pass
 def finish(self):
  if self.cancelled:raise SystemExit(0)
  if not self.progress.ready():raise ValueError('Startup checks are not complete.')
  self.close();self.root.deiconify()

_boot=None
def begin_startup(folder):
 global _boot
 if _boot is None or _boot.closed:
  import sys
  if sys.platform=='win32':
   import ctypes
   ctypes.windll.user32.SetProcessDPIAware()
  _boot=StartupScreen(folder)
 return _boot

def current_startup():return _boot
