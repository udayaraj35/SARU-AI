"""Visible local-only screen preview. No storage, cloud upload or input."""
import ctypes
import os
import tkinter as tk
from queue import Queue,Empty
import threading
from PIL import ImageTk


def desktop_available():
 if os.name!='nt':return False
 user=ctypes.WinDLL('user32',use_last_error=True)
 user.OpenInputDesktop.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];user.OpenInputDesktop.restype=ctypes.c_void_p
 user.CloseDesktop.argtypes=[ctypes.c_void_p]
 user.GetUserObjectInformationW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(ctypes.c_ulong)]
 desktop=user.OpenInputDesktop(0,False,1)
 if not desktop:return False
 try:
  name=ctypes.create_unicode_buffer(256);needed=ctypes.c_ulong()
  return bool(user.GetUserObjectInformationW(desktop,2,name,ctypes.sizeof(name),ctypes.byref(needed))) and name.value.casefold()=='default'
 finally:user.CloseDesktop(desktop)

class ScreenWatch(tk.Toplevel):
 def __init__(self,root,on_stop=None,cfg=None):
  super().__init__(root);self.on_stop=on_stop;self.title('SARU · Local screen view');self.geometry('640x430');self.configure(bg='#071226');self.closed=False;self.busy=False;self.job=None;self.events=Queue(maxsize=1)
  self.status=tk.Label(self,text='SCREEN VIEW ON · Local preview only · No cloud sharing',bg='#071226',fg='#ff3978',font=('Segoe UI',11,'bold'));self.status.pack(fill='x',padx=10,pady=10)
  tk.Button(self,text='Stop screen view',command=self.stop).pack(pady=4)
  self.preview=tk.Label(self,bg='#071226');self.preview.pack(fill='both',expand=True,padx=10,pady=8)
  from screen_corners import ScreenCorners
  self.corners=ScreenCorners(root,cfg or {})
  self.protocol('WM_DELETE_WINDOW',self.stop)
  self.bind('<Destroy>',self.cleanup,add='+');self.poll()
 def poll(self):
  if self.closed:return
  try:
   image,error=self.events.get_nowait();self.busy=False
   if image is not None:
    self.corners.show()
    image.thumbnail((max(100,self.winfo_width()-20),max(100,self.winfo_height()-110)))
    self.photo=ImageTk.PhotoImage(image);self.preview.configure(image=self.photo)
    self.status.configure(text='SCREEN VIEW ON · Local only · Updated every 3 seconds')
   else:
    self.corners.hide()
    self.preview.configure(image='');self.photo=None
    self.status.configure(text='Screen view paused: '+error)
  except Empty:pass
  if not self.busy:
   self.busy=True
   def capture():
    try:
     if not desktop_available():raise RuntimeError('desktop locked or unavailable')
     import pyautogui
     image=pyautogui.screenshot()
     if not desktop_available():raise RuntimeError('desktop locked or unavailable')
     result=(image,None)
    except Exception as exc:result=(None,str(exc)[:120])
    if not self.closed:self.events.put_nowait(result)
   threading.Thread(target=capture,daemon=True).start()
  self.job=self.after(3000,self.poll)
 def stop(self):
  if self.on_stop:self.on_stop()
  self.destroy()
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True;self.photo=None
   self.corners.close()
   if self.job:self.after_cancel(self.job)
