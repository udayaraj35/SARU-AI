"""Fit sidebar links to available height; scroll locally when they cannot fit."""
import math
from tkinter import font as tkfont

class SidebarNavigation:
 def __init__(self,canvas,links,scrollbar,buttons):
  self.canvas=canvas;self.links=links;self.scrollbar=scrollbar;self.buttons=buttons;self.wheel_remainder=0;self.height=None;self.job=None
  self.item=canvas.create_window((0,0),window=links,anchor='nw')
  canvas.bind('<Configure>',self.resize);links.bind('<Configure>',self.region)
  for widget in [canvas,links,*buttons]:
   widget.bind('<MouseWheel>',self.wheel,add='+');widget.bind('<Button-4>',lambda event:self.scroll(-1),add='+');widget.bind('<Button-5>',lambda event:self.scroll(1),add='+')
 def resize(self,event):
  self.canvas.itemconfigure(self.item,width=max(1,event.width));self.fit(event.height)
 def fit(self,height):
  if not self.buttons:return
  line=max(tkfont.Font(font=button.cget('font')).metrics('linespace') for button in self.buttons)
  minimum=max(28,line+8);row=max(minimum,math.floor(height/len(self.buttons))-4)
  if self.height!=row:
   self.height=row
   for button in self.buttons:button.configure(height=row);button.pack_configure(pady=2)
  overflow=(row+4)*len(self.buttons)>height
  if overflow and not self.scrollbar.winfo_manager():self.scrollbar.pack(side='right',fill='y',before=self.canvas)
  elif not overflow and self.scrollbar.winfo_manager():self.scrollbar.pack_forget();self.canvas.yview_moveto(0)
 def region(self,event=None):
  self.canvas.configure(scrollregion=self.canvas.bbox('all'))
 def scroll(self,steps):
  self.canvas.yview_scroll(steps,'units');return 'break'
 def wheel(self,event):
  self.wheel_remainder-=event.delta/120
  steps=math.trunc(self.wheel_remainder)
  if steps:self.wheel_remainder-=steps;self.scroll(steps)
  return 'break'
