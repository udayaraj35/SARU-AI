"""Accessible sizes and state-bound portrait animation helpers."""
import math
import tkinter as tk
from tkinter import font as tkfont

def frame_index(state,phase,reduced=False,count=8):
 if reduced or state not in ('LISTENING','SPEAKING'):return count-1
 return min(count-1,int((.5+.5*math.sin(phase))*(count-1)))

def apply_text_scale(widget,percent):
 factor=max(.9,min(1.4,float(percent)/100))
 def visit(item):
  if getattr(item,'_saru_independent_font',False):return
  try:
   if 'font' in item.keys():
    if not hasattr(item,'_saru_base_font'):item._saru_base_font=tkfont.Font(font=item.cget('font')).actual()
    base=item._saru_base_font;size=round(base['size']*factor)
    if getattr(item,'_saru_font_size',None)!=size:
     item._saru_font_size=size;spec=dict(base);spec['size']=size
     item._saru_scaled_font=tkfont.Font(**spec);item.configure(font=item._saru_scaled_font)
  except tk.TclError:pass
  for child in item.winfo_children():visit(child)
 visit(widget)
