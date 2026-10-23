"""Small real device sliders; native calls stay off the Tk thread."""
import tkinter as tk
import threading
from queue import Queue, Empty
from smooth_controls import LatestControls
from pc_telemetry import device_request
from neon_ui import PANEL, TEXT, CYAN, label


class QuickDeviceControls(tk.Frame):
 def __init__(self,parent):
  super().__init__(parent,bg=PANEL)
  self.client=LatestControls();self.readings=Queue();self.closed=False;self.revisions={};self.sliders={}
  self.message=label(self,'Reading Windows controls…');self.message.pack(fill='x')
  for name,title in [('volume','Volume'),('brightness','Brightness')]:
   row=tk.Frame(self,bg=PANEL);row.pack(fill='x')
   label(row,title,width=11,anchor='w').pack(side='left')
   slider=tk.Scale(row,from_=0,to=100,orient='horizontal',state='disabled',bg=PANEL,fg=TEXT,troughcolor='#081225',activebackground=CYAN,highlightthickness=0,length=235)
   slider.pack(side='left',fill='x',expand=True);self.sliders[name]=slider
   slider.configure(command=lambda value,n=name:self.change(n,value))
  self.bind('<Destroy>',self.cleanup,add='+')
  def read():
   try:self.readings.put(device_request())
   except Exception as exc:self.readings.put({'error':str(exc)})
  threading.Thread(target=read,daemon=True).start();self.job=self.after(80,self.pump)
 def change(self,name,value):
  if not self.closed:self.revisions[name]=self.client.set(name,round(float(value)))
 def pump(self):
  if self.closed:return
  try:
   values=self.readings.get_nowait()
   for name,slider in self.sliders.items():
    value=values.get(name)
    if value is not None:
     command=slider.cget('command');slider.configure(command='',state='normal');slider.set(value);slider.configure(command=command)
   self.message.configure(text=values.get('error','Drag to change supported Windows devices.'))
  except Empty:pass
  try:
   while True:
    name,revision,result,error=self.client.events.get_nowait()
    if self.revisions.get(name)==revision:
     self.message.configure(text=error or f'{name.title()}: {result.get(name,"unavailable")}% (Windows)')
  except Empty:pass
  self.job=self.after(80,self.pump)
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True;self.after_cancel(self.job);self.client.close()
