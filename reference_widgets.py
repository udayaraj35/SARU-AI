"""Actual rounded gradient buttons, not image-only dashboard hotspots."""
import tkinter as tk
from PIL import Image,ImageTk,ImageDraw

class NeonButton(tk.Button):
 def __init__(self,parent,text,command,primary=False,width=120,height=38):
  if '\n' not in text:
   import re
   from brand_icons import NAMES
   clean=re.sub(r'^[^\w]+','',text).strip()
   if any(clean==name or clean.startswith(name+' ') for name in NAMES):text=clean
  self.primary=primary;self.hover=False;self.last_size=None;self.icon_kind=text.split('\n')[-1] if '\n' in text else None
  if self.icon_kind:text='\n'+self.icon_kind
  super().__init__(parent,text=text,command=command,compound='center',font=('Segoe UI',10,'bold'),fg='white',activeforeground='white',bg='#071326',activebackground='#071326',relief='flat',bd=0,cursor='hand2',highlightthickness=0,takefocus=True,padx=0,pady=0)
  self.configure(width=width,height=height);self.paint(width,height)
  self.bind('<Configure>',lambda e:self.paint(e.width,e.height));self.bind('<Enter>',lambda e:self.set_hover(True));self.bind('<Leave>',lambda e:self.set_hover(False))
 def set_hover(self,value):self.hover=value;self.last_size=None;self.paint(self.winfo_width(),self.winfo_height())
 def paint(self,width,height):
  width=max(20,width);height=max(20,height);key=(width,height,self.hover)
  if self.last_size==key:return
  self.last_size=key
  image=Image.new('RGB',(width,height),'#071326');draw=ImageDraw.Draw(image)
  start,end=((186,15,101),(62,21,125)) if self.primary else ((18,37,62),(7,17,35))
  palette=getattr(self,'theme_palette',None)
  if palette:
   def rgb(value):return tuple(int(value[i:i+2],16) for i in (1,3,5))
   start=rgb(palette['primary'] if self.primary else palette['panel']);end=rgb(palette['field'])
  for y in range(height):
   t=y/max(1,height-1);color=tuple(int(a*(1-t)+b*t) for a,b in zip(start,end));draw.line((2,y,width-3,y),fill=color)
  mask=Image.new('L',(width,height));ImageDraw.Draw(mask).rounded_rectangle((1,1,width-2,height-2),radius=min(height//2,24) if getattr(self,'neon_outline',False) else 12,fill=255)
  base=Image.new('RGB',(width,height),palette['bg'] if palette else '#071326');base.paste(image,mask=mask);d=ImageDraw.Draw(base)
  d.rounded_rectangle((1,1,width-2,height-2),radius=min(height//2,24) if getattr(self,'neon_outline',False) else 12,outline='#48d8ff' if self.hover else '#fd2f8c' if self.primary else '#284c70',width=2 if self.primary or self.hover else 1)
  from brand_icons import pil_icon
  brand=pil_icon(self.icon_kind or self.cget('text').strip(),22)
  if brand:
   x,y=(width//2-11,3) if self.icon_kind else (8,max(1,(height-22)//2))
   base.paste(brand,(x,y),brand)
  elif self.icon_kind:draw_icon(d,self.icon_kind,width//2,14)
  if palette:
   d.rounded_rectangle((1,1,width-2,height-2),radius=min(height//2,24) if getattr(self,'neon_outline',False) else 12,outline=palette['accent'] if self.hover else palette['primary'] if self.primary or getattr(self,'neon_outline',False) else palette['line'],width=2 if self.primary or self.hover else 1)
  self.background=ImageTk.PhotoImage(base);self.configure(image=self.background)

def draw_icon(d,name,x,y):
 color={'Facebook':'#398dff','Instagram':'#f85ec9','TikTok':'#60e8ef','YouTube':'#ff3866','WhatsApp':'#22df9b','Gmail':'#ed5ec9','Telegram':'#36caff','Shutdown':'#ff348c'}.get(name,'#57d9ff')
 if name=='Open App':
  for dx in (-8,2):
   for dy in (-7,3):d.rounded_rectangle((x+dx,y+dy,x+dx+6,y+dy+6),radius=1,outline=color,width=2)
 elif name=='Screenshot':
  for a,b,c,e in [(-9,-7,-4,-7),(-9,-7,-9,-2),(4,-7,9,-7),(9,-7,9,-2),(-9,2,-9,7),(-9,7,-4,7),(4,7,9,7),(9,2,9,7)]:d.line((x+a,y+b,x+c,y+e),fill=color,width=2)
  d.ellipse((x-4,y-4,x+4,y+4),outline=color,width=2)
 elif name=='Volume':
  d.polygon(((x-9,y-3),(x-5,y-3),(x,y-8),(x,y+8),(x-5,y+3),(x-9,y+3)),outline=color)
  d.arc((x-3,y-7,x+10,y+7),-65,65,fill=color,width=2)
 elif name=='Brightness':
  import math
  d.ellipse((x-4,y-4,x+4,y+4),outline=color,width=2)
  for angle in range(0,360,45):
   a=math.radians(angle);d.line((x+7*math.cos(a),y+7*math.sin(a),x+11*math.cos(a),y+11*math.sin(a)),fill=color,width=2)
 elif name=='Lock PC':
  d.arc((x-5,y-10,x+5,y+2),180,360,fill=color,width=2);d.rounded_rectangle((x-8,y-2,x+8,y+9),radius=2,outline=color,width=2)
 elif name in ('Clipboard','Notepad','Calculator'):
  d.rounded_rectangle((x-7,y-8,x+7,y+9),radius=2,outline=color,width=2)
  if name=='Calculator':
   d.rectangle((x-4,y-5,x+4,y-1),outline=color)
   for dx in (-3,2):
    for dy in (3,6):d.rectangle((x+dx,y+dy,x+dx+1,y+dy+1),fill=color)
  else:
   for dy in (-3,1,5):d.line((x-3,y+dy,x+4,y+dy),fill=color,width=1)
 elif name=='Task Manager':
  d.rectangle((x-9,y-7,x+9,y+8),outline=color,width=1);d.line((x-6,y+4,x-2,y,x+2,y+2,x+6,y-4),fill=color,width=2)
 elif name=='Shutdown':d.arc((x-8,y-8,x+8,y+8),-50,230,fill=color,width=2);d.line((x,y-10,x,y),fill=color,width=2)
 elif name in ('Instagram','WhatsApp'):
  d.rounded_rectangle((x-8,y-8,x+8,y+8),radius=5,outline=color,width=2)
  if name=='Instagram':d.ellipse((x-4,y-4,x+4,y+4),outline=color,width=2);d.point((x+5,y-5),fill=color)
  else:d.line((x-4,y-3,x-1,y+3,x+4,y+5),fill=color,width=2)
 elif name=='YouTube':d.rounded_rectangle((x-10,y-7,x+10,y+7),radius=4,fill=color);d.polygon(((x-2,y-4),(x-2,y+4),(x+4,y)),fill='white')
 elif name in ('Telegram','Gmail'):
  if name=='Telegram':d.polygon(((x-10,y-6),(x+10,y-8),(x+2,y+9),(x-1,y+1)),outline=color)
  else:d.rectangle((x-9,y-6,x+9,y+7),outline=color,width=2);d.line((x-8,y-5,x,y+1,x+8,y-5),fill=color,width=2)
 else:d.text((x-5,y-8),{'Translator':'A','Facebook':'f','Twitter':'X','TikTok':'♪'}.get(name,'•'),fill=color,stroke_width=1)

def skin_button(widget):
 """Give legacy workflow buttons the same skin while preserving their command."""
 if getattr(widget,'_neon_skinned',False) or isinstance(widget,NeonButton):return
 from types import MethodType
 widget._neon_skinned=True;widget.primary=False;widget.hover=False;widget.last_size=None;widget.icon_kind=None
 widget.paint=MethodType(NeonButton.paint,widget);widget.set_hover=MethodType(NeonButton.set_hover,widget)
 requested=max(150,widget.winfo_reqwidth())
 widget.configure(compound='center',width=0,height=0,padx=0,pady=0,relief='flat',bd=0,highlightthickness=0,font=('Segoe UI',10,'bold'),bg='#071326',activebackground='#071326',fg='white',activeforeground='white',cursor='hand2')
 widget.paint(requested,42)
 widget.bind('<Configure>',lambda e:widget.paint(e.width,e.height),add='+')
 widget.bind('<Enter>',lambda e:widget.set_hover(True),add='+');widget.bind('<Leave>',lambda e:widget.set_hover(False),add='+')


class RoundedPanel(tk.Frame):
 """A rounded native container; its child buttons keep their real callbacks."""
 def __init__(self,parent,neon=False):
  super().__init__(parent,bg='#071326',borderwidth=0,highlightthickness=0)
  self.neon=neon;self.last_size=None;self.background_label=tk.Label(self,bd=0,bg='#071326')
  self.background_label.place(x=0,y=0,relwidth=1,relheight=1);self.background_label.lower()
  self.bind('<Configure>',lambda e:self.paint(e.width,e.height),add='+')
 def paint(self,width,height):
  width=max(20,width);height=max(20,height)
  if self.last_size==(width,height):return
  self.last_size=(width,height)
  from theme_manager import palette
  p=getattr(self,'theme_palette',None) or palette('Neon Rose')
  art=Image.new('RGB',(width,height),p['bg']);d=ImageDraw.Draw(art)
  if self.neon:
   for inset in (1,3,5):d.rounded_rectangle((inset,inset,width-inset-1,height-inset-1),radius=height//2,outline=p['primary'],width=1)
  else:d.rounded_rectangle((1,1,width-2,height-2),radius=16,fill=p['bg'],outline=p['line'],width=1)
  self.background=ImageTk.PhotoImage(art);self.background_label.configure(image=self.background)
