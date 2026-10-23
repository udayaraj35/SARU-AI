"""Theme-following noninteractive corner indicators for active screen viewing."""
import ctypes,os,tkinter as tk
from theme_manager import palette

class ScreenCorners:
 def __init__(self,root,cfg):
  self.root=root;self.cfg=cfg;self.windows=[];self.job=None;self.closed=False;self.visible=False;self.last=None
  for _ in range(4):
   window=tk.Toplevel(root);window.withdraw();window.overrideredirect(True);window.configure(bg='#010203');window.attributes('-topmost',True)
   if os.name=='nt':window.wm_attributes('-transparentcolor','#010203')
   canvas=tk.Canvas(window,width=72,height=72,bg='#010203',highlightthickness=0);canvas.pack();self.windows.append((window,canvas))
  self.refresh()
 def refresh(self):
  if self.closed:return
  colors=palette(self.cfg.get('theme'));width=self.root.winfo_screenwidth();height=self.root.winfo_screenheight();token=(colors['primary'],colors['accent'],width,height)
  if token!=self.last:
   self.last=token
   for index,(window,canvas) in enumerate(self.windows):
    right=index%2;bottom=index//2;x=width-72 if right else 0;y=height-72 if bottom else 0
    window.geometry(f'72x72+{x}+{y}');canvas.delete('all')
    points=[(58 if right else 14),(14 if bottom else 58),(58 if right else 14),(58 if bottom else 14),(14 if right else 58),(58 if bottom else 14)]
    canvas.create_line(*points,fill=colors['primary'],width=7,capstyle='round',joinstyle='round')
    canvas.create_line(*points,fill=colors['accent'],width=2,capstyle='round',joinstyle='round')
    window.update_idletasks()
    if os.name=='nt':
     user=ctypes.WinDLL('user32',use_last_error=True)
     user.GetParent.argtypes=[ctypes.c_void_p];user.GetParent.restype=ctypes.c_void_p
     hwnd=user.GetParent(window.winfo_id()) or window.winfo_id()
     get=getattr(user,'GetWindowLongPtrW',user.GetWindowLongW);set_=getattr(user,'SetWindowLongPtrW',user.SetWindowLongW)
     get.argtypes=[ctypes.c_void_p,ctypes.c_int];get.restype=ctypes.c_ssize_t
     set_.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_ssize_t];set_.restype=ctypes.c_ssize_t
     set_(hwnd,-20,get(hwnd,-20)|0x20|0x80|0x08000000)
     user.SetWindowDisplayAffinity.argtypes=[ctypes.c_void_p,ctypes.c_uint];user.SetWindowDisplayAffinity(hwnd,0x11)
  self.job=self.root.after(500,self.refresh)
 def show(self):
  if self.closed:return
  self.visible=True
  for window,canvas in self.windows:window.deiconify();window.lift()
 def hide(self):
  self.visible=False
  for window,canvas in self.windows:window.withdraw()
 def close(self):
  if self.closed:return
  self.closed=True
  if self.job:self.root.after_cancel(self.job)
  for window,canvas in self.windows:window.destroy()
