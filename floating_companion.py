"""SARU desktop companion. Own branding, real voice state, no hidden listening."""
import math
import os
import time
import tkinter as tk
from PIL import Image,ImageTk,ImageOps,ImageDraw
from portrait_assets import load_portrait
from appearance_controls import frame_index

COLORS={'STOPPING':'#e9b44c','IDLE':'#ff286e','STOPPED':'#ff286e','CONNECTING':'#e9b44c','LISTENING':'#14d8f4','SPEAKING':'#b672ff','MUTED':'#8994a8','ERROR':'#ff4055'}

def bounds(root):
 if os.name=='nt':
  import ctypes
  metrics=ctypes.windll.user32.GetSystemMetrics
  return metrics(76),metrics(77),metrics(78),metrics(79)
 return 0,0,root.winfo_screenwidth(),root.winfo_screenheight()

def clamp_position(x,y,width,height,desktop):
 left,top,w,h=desktop
 return max(left,min(int(x),left+w-width)),max(top,min(int(y),top+h-height))

class FloatingCompanion(tk.Toplevel):
 def __init__(self,root,cfg,save,on_open,on_voice,on_stop,on_settings,on_exit,actions=None):
  super().__init__(root);self._saru_independent_font=True;self.last_owner_voice=time.monotonic();self.phase=0;self.frames=[];self.cfg=cfg;self.save_config=save;self.on_open=on_open;self.state_name='IDLE';self.level=0;self.angle=0;self.job=None;self.closed=False;self.drag=None;self.click_job=None;self.suppress_release=False;self.controls=None;self.actions=actions or {};self.on_voice=on_voice;self.on_stop=on_stop;self.on_settings=on_settings
  self.overrideredirect(True);self.attributes('-topmost',True);self.configure(bg='#020304')
  if os.name=='nt':self.wm_attributes('-transparentcolor','#020304')
  self.attributes('-alpha',float(cfg.get('orb_opacity',.96)))
  self.canvas=tk.Canvas(self,bg='#020304',highlightthickness=0,cursor='hand2');self.canvas.pack(fill='both',expand=True)
  self.canvas.bind('<ButtonPress-1>',self.down);self.canvas.bind('<B1-Motion>',self.move);self.canvas.bind('<ButtonRelease-1>',self.up)
  self.canvas.bind('<Double-Button-1>',self.double_click);self.canvas.bind('<Button-3>',self.menu_open)
  self.menu=tk.Menu(self,tearoff=False,bg='#0b1425',fg='white',activebackground='#24526b',activeforeground='white',activeborderwidth=4,borderwidth=1)
  for title,command in [('Open SARU AI',on_open),('Open Live Voice',on_voice),('Stop listening / speaking',on_stop),('Settings',on_settings),('Hide companion',self.hide),('Exit SARU',on_exit)]:self.menu.add_command(label=title,command=command)
  self.bind('<Destroy>',self.cleanup,add='+');self.reload();self.tick()
 def reload(self):
  self.size=max(48,min(240,int(self.cfg.get('orb_size',100))));self.text_size=max(10,min(22,int(self.cfg.get('orb_text_size',12))));self.width=max(self.size+32,self.text_size*11);self.height=self.size+self.text_size*3+52
  from theme_manager import palette
  colors=palette(self.cfg.get('theme','Neon Rose'))
  self.menu.configure(font=('Segoe UI',self.text_size+2,'bold'),bg=colors['panel'],fg=colors['text'],activebackground=colors['line'],activeforeground=colors['text'])
  x,y=clamp_position(self.cfg.get('orb_x',100),self.cfg.get('orb_y',100),self.width,self.height,bounds(self.master))
  self.geometry(f'{self.width}x{self.height}{x:+d}{y:+d}')
  self.attributes('-topmost',bool(self.cfg.get('orb_topmost',True)));self.attributes('-alpha',max(.35,min(1,float(self.cfg.get('orb_opacity',.96)))))
  self.photo=None;self.frames=[]
  try:
   path=self.cfg.get('orb_photo') or self.cfg.get('photo')
   original=load_portrait(path,self.cfg.get('portrait_design','new')).convert('RGBA');diameter=self.size-14
   ratio=diameter/max(original.width,original.height)
   self.frames=[]
   for index in range(8):
    factor=.91+.09*index/7
    portrait=original.resize((max(1,int(original.width*ratio*factor)),max(1,int(original.height*ratio*factor))),Image.Resampling.LANCZOS)
    frame=Image.new('RGBA',(diameter,diameter));frame.alpha_composite(portrait,((diameter-portrait.width)//2,(diameter-portrait.height)//2));self.frames.append(ImageTk.PhotoImage(frame))
   self.photo=self.frames[-1]
  except (OSError,TypeError,ValueError):pass
  self.draw()
  if self.controls and self.controls.winfo_exists():
   from theme_manager import apply_theme
   apply_theme(self.controls,self.cfg.get('theme','Neon Rose'))
 def set_state(self,state,level=None):
  self.state_name=state if state in COLORS else 'IDLE'
  if level is not None:self.level=max(0,min(1,float(level)))
  elif state in ('IDLE','STOPPED','MUTED','ERROR'):self.level=0
  if state=='LISTENING' and level is not None and self.level>.035:self.last_owner_voice=time.monotonic()
  self.draw()
  if self.controls and self.controls.winfo_exists():self.control_status.configure(text=self.state_name.title())
 def draw(self):
  c=self.canvas;c.delete('all');s=self.size;color=COLORS.get(self.state_name,COLORS['IDLE']);cx=self.width/2;cy=s/2+12
  c.create_oval(cx-s/2,cy-s/2,cx+s/2,cy+s/2,fill='#0c172c',outline='#263552',width=3)
  if self.frames:self.photo=self.frames[frame_index(self.state_name,self.phase,self.cfg.get('reduced_motion',False))]
  motion=not self.cfg.get('reduced_motion',False)
  listening=self.state_name=='LISTENING'
  bob=math.sin(self.phase)*2 if motion and listening else 0
  if self.photo:c.create_image(cx,cy+bob,image=self.photo)
  else:c.create_text(cx,cy,text='SARU',fill='white',font=('Segoe UI',max(10,s//6),'bold'))
  c.create_arc(cx-s/2,cy-s/2,cx+s/2,cy+s/2,start=self.angle,extent=255,style='arc',outline=color,width=3)
  if self.state_name in ('LISTENING','SPEAKING'):
   for i in range(7):
    h=self.level*(5+14*abs(math.sin(i+1)));x=cx+(i-3)*5
    c.create_line(x,cy+s/2-10-h,x,cy+s/2-10,fill=color,width=3)
  # A separate expression badge keeps the source portrait intact.
  bx=cx+s*.34;by=cy+s*.29;r=max(9,s*.12)
  quiet=self.state_name=='LISTENING' and time.monotonic()-self.last_owner_voice>45
  stopped=self.state_name=='STOPPED' or quiet
  c.create_oval(bx-r,by-r,bx+r,by+r,fill='#36132b' if stopped else '#082f40',outline='#ff3978' if stopped else color,width=2)
  if stopped:
   c.create_line(bx-r*.6,by-r*.4,bx-r*.16,by-r*.15,fill='#ff638c',width=2)
   c.create_line(bx+r*.16,by-r*.15,bx+r*.6,by-r*.4,fill='#ff638c',width=2)
   c.create_arc(bx-r*.4,by+r*.2,bx+r*.4,by+r*.65,start=0,extent=180,style='arc',outline='#ff638c',width=2)
  else:
   for ex in (-.34,.34):
    c.create_oval(bx+r*ex-1,by-3,bx+r*ex+1,by-1,fill=color,outline=color)
   c.create_arc(bx-r*.4,by-r*.12,bx+r*.4,by+r*.5,start=180,extent=180,style='arc',outline=color,width=2)
  label_y=s+29
  c.create_rectangle(5,label_y-self.text_size, self.width-5,label_y+self.text_size+5,fill='#180d22',outline='#7e234b',width=1)
  c.create_text(cx+1,label_y+2,text='SARU AI',fill='#8a1239',font=('Segoe UI',self.text_size+1,'bold'))
  c.create_text(cx,label_y,text='SARU AI',fill='#ff3978',font=('Segoe UI',self.text_size+1,'bold'))
  mood='Quiet · Listening' if quiet else ('Happy · Listening' if self.state_name=='LISTENING' and self.level>.035 else self.state_name.title())
  c.create_text(cx,s+28+self.text_size*1.7,text=mood,fill=color,font=('Segoe UI',self.text_size))
 def tick(self):
  if self.closed:return
  if not self.cfg.get('reduced_motion',False) and self.state_name in ('LISTENING','SPEAKING'):
   self.angle=(self.angle+4)%360;self.phase+=.16;self.draw()
  if self.controls and self.controls.winfo_exists() and self.controls.state()!='withdrawn' and not self.cfg.get('reduced_motion',False):
   from theme_manager import palette
   colors=palette(self.cfg.get('theme'));self.phase+=.08;self.controls.winfo_children()[0].configure(highlightbackground=colors['accent'] if int(self.phase)%2 else colors['primary'])
  self.job=self.after(90,self.tick)
 def down(self,event):
  if self.click_job:self.after_cancel(self.click_job);self.click_job=None
  self.drag=(event.x_root,event.y_root,self.winfo_x(),self.winfo_y(),False)
 def move(self,event):
  if not self.drag:return
  sx,sy,x,y,moved=self.drag;dx=event.x_root-sx;dy=event.y_root-sy
  if abs(dx)+abs(dy)>3:
   nx,ny=clamp_position(x+dx,y+dy,self.width,self.height,bounds(self.master));self.geometry(f'{self.width}x{self.height}{nx:+d}{ny:+d}');self.drag=(sx,sy,x,y,True)
 def up(self,event):
  if self.suppress_release:self.suppress_release=False;self.drag=None;return
  if not self.drag:return
  moved=self.drag[-1];self.drag=None
  if moved:
   x,y=self.winfo_x(),self.winfo_y();left,top,w,h=bounds(self.master)
   if self.cfg.get('orb_snap',True):
    if abs(x-left)<24:x=left
    elif abs(x+self.width-left-w)<24:x=left+w-self.width
   self.geometry(f'{self.width}x{self.height}{x:+d}{y:+d}');self.cfg.update(orb_x=x,orb_y=y);self.save_config()
  elif self.suppress_release:self.suppress_release=False
  else:
   if self.click_job:self.after_cancel(self.click_job)
   delay=500
   if os.name=='nt':
    import ctypes
    delay=max(200,int(ctypes.windll.user32.GetDoubleClickTime()))
   self.click_job=self.after(delay+30,self.toggle_controls)
 def double_click(self,event=None):
  if self.click_job:self.after_cancel(self.click_job);self.click_job=None
  self.drag=None;self.suppress_release=True
  if self.controls and self.controls.winfo_exists():self.controls.withdraw()
  self.on_open()
  return 'break'
 def toggle_controls(self):
  self.click_job=None
  if self.controls and self.controls.winfo_exists():
   if self.controls.state()!='withdrawn':self.controls.withdraw();return
   self.controls.deiconify()
  else:self.build_controls()
  from theme_manager import apply_theme
  from appearance_controls import apply_text_scale
  apply_theme(self.controls,self.cfg.get('theme','Neon Rose'));apply_text_scale(self.controls,self.cfg.get('ui_text_scale',100))
  self.controls.update_idletasks()
  width=self.controls.winfo_reqwidth();height=self.controls.winfo_reqheight()
  x=self.winfo_x()+self.width+8;y=self.winfo_y();desktop=bounds(self.master)
  if x+width>desktop[0]+desktop[2]:x=self.winfo_x()-width-8
  x,y=clamp_position(x,y,width,height,desktop)
  self.controls.geometry(f'{width}x{height}{x:+d}{y:+d}');self.controls.lift()
 def build_controls(self):
  from neon_ui import button,label,BG,PANEL,LINE
  panel=self.controls=tk.Toplevel(self);panel.title('SARU quick controls');panel.attributes('-topmost',True);panel.configure(bg=BG);panel.resizable(False,False)
  panel.protocol('WM_DELETE_WINDOW',panel.withdraw)
  body=tk.Frame(panel,bg=PANEL,highlightthickness=2,highlightbackground=LINE,relief='raised',borderwidth=3);body.pack(fill='both',expand=True,padx=5,pady=5)
  label(body,'SARU AI · Quick controls',font=('Segoe UI',15,'bold')).grid(row=0,column=0,columnspan=2,padx=12,pady=12)
  self.control_status=label(body,self.state_name.title());self.control_status.grid(row=1,column=0,columnspan=2,pady=4)
  commands=[('Start voice',self.actions.get('start_voice',self.on_voice)),('Stop voice',self.on_stop),('Mute / unmute mic',self.actions.get('mute',self.on_stop)),('Screen view / share',self.actions.get('screen',self.on_open)),('YouTube player',self.actions.get('media',self.on_open)),('Improve SARU',self.actions.get('improve',self.on_settings)),('Settings',self.on_settings),('Hide controls',panel.withdraw)]
  for index,(title,command) in enumerate(commands):button(body,title,command,index==0).grid(row=2+index//2,column=index%2,padx=7,pady=6,sticky='ew')
  from quick_device_controls import QuickDeviceControls
  self.device_controls=QuickDeviceControls(body);self.device_controls.grid(row=2+(len(commands)+1)//2,column=0,columnspan=2,sticky='ew',padx=10,pady=8)
  label(body,'Double-click portrait to open main interface.',font=('Segoe UI',10),wraplength=360).grid(row=3+(len(commands)+1)//2,column=0,columnspan=2,padx=10,pady=12)
 def menu_open(self,event):
  try:self.menu.tk_popup(event.x_root,event.y_root)
  finally:self.menu.grab_release()
 def hide(self):
  if self.master.state()=='withdrawn':self.master.deiconify()
  if self.controls and self.controls.winfo_exists():self.controls.withdraw()
  self.withdraw();self.cfg['orb_visible']=False;self.save_config()
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True
   if self.job:self.after_cancel(self.job)
   if self.click_job:self.after_cancel(self.click_job)
