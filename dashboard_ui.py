"""Responsive neon command center with real, asynchronously refreshed PC readings."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps, ImageDraw
from concurrent.futures import ThreadPoolExecutor
from queue import Queue,Empty
from neon_ui import *
from version import VERSION
import json
from pathlib import Path
import pc_telemetry
from portrait_assets import load_portrait

class Dashboard(tk.Frame):
 def __init__(self,root,actions,status,portrait,reference,cfg=None,activity_path=None):
  super().__init__(root,bg=BG);self.place(relwidth=1,relheight=1)
  from dashboard_layout import build
  build(self,root,actions,status,portrait,reference,cfg,activity_path)
 def select_provider(self):
  model=self.cfg.get('provider_models',{}).get(self.provider_var.get(),'')
  self.model_var.set(model);self.model_select.configure(values=[model] if model else [])
  self.save_provider()
 def save_provider(self):
  self.actions['Set provider'](self.provider_var.get(),self.model_var.get().strip())
  self.provider_key.configure(text='Key saved' if self.cfg.get('keys',{}).get(self.provider_var.get()) else 'API key required')
 def toggle_chat(self):
  if self.drawer_open:self.hide_chat()
  else:self.focus_chat()
 def cancel_chat_idle(self):
  job=getattr(self,'chat_idle_job',None)
  if job:
   try:self.after_cancel(job)
   except tk.TclError:pass
  self.chat_idle_job=None
 def chat_activity(self,complete=True):
  self.cancel_chat_idle()
  if not getattr(self,'chat_dismissed',False):
   if not self.drawer_open:self.drawer_open=True;self.layout_dock()
  self.chat_busy=not complete
  if complete and self.drawer_open:self.chat_idle_job=self.after(30000,self.chat_idle)
 def chat_idle(self):
  self.chat_idle_job=None
  if self.closed or not self.drawer_open:return
  # Keep an in-progress reply, unsent text, or a transcript being read visible.
  x,y=self.winfo_pointerxy();dock=self.chat_dock
  reading=dock.winfo_rootx()<=x<dock.winfo_rootx()+dock.winfo_width() and dock.winfo_rooty()<=y<dock.winfo_rooty()+dock.winfo_height()
  if getattr(self,'chat_busy',False) or self.hero_voice_state=='SPEAKING' or self.command.get().strip() or reading:
   self.chat_idle_job=self.after(30000,self.chat_idle);return
  self.hide_chat(manual=False)
 def hide_chat(self,manual=True):
  self.cancel_chat_idle();self.chat_dismissed=manual;self.drawer_open=False;self.layout_dock()
 def layout_dock(self,event=None):
  if event is not None and event.widget not in (self,self.composer):return
  nav_width=230 if self.winfo_width()<1400 else 280
  if self.nav.cget('width')!=nav_width:self.nav.configure(width=nav_width)
  inset=nav_width+16
  top=self.state.winfo_y()+self.state.winfo_height()+3
  self.nav.place_configure(x=8,y=top,width=nav_width,height=max(100,self.winfo_height()-top-8))
  available=max(1,self.winfo_width()-inset-10)
  width=min(380,max(280,int(available*.34)))
  self.shell.pack_configure(padx=(inset,width+18 if self.drawer_open else 8))
  if hasattr(self,'sidebar_navigation'):self.sidebar_navigation.fit(self.navcanvas.winfo_height())
  self.composer.pack_configure(padx=(inset,10));self.chips.pack_configure(padx=(inset,10))
  self.chat_dock.pack_forget()
  self.chat_dock.place_forget()
  if not self.drawer_open:self.dock_side='closed';return
  self.dock_side='right'
  bottom=self.composer.winfo_y()
  self.chat_dock.place(x=self.winfo_width()-width-10,y=top,width=width,height=max(100,bottom-top-8))
  self.chat_dock.lift()
 def voice_event(self,kind,value):
  if self.closed:return
  if kind=='state':
   self.hero_voice_state=value;self.voice_state.configure(text='Microphone / Voice: '+value)
   if hasattr(self,'hero_voice_label'):self.ring.itemconfigure(self.hero_voice_label,text=value.replace('_',' ').title())
   if value not in ('LISTENING','SPEAKING'):self.update_hero_meter(0)
   if value not in ('LISTENING','SPEAKING') and getattr(self,'avatar_frames',None):self.ring.itemconfigure(self.avatar_item,image=self.avatar_frames[-1])
   if value in ('STOPPED','ERROR'):
    self.chat_busy=False
    if self.drawer_open:self.chat_activity()
  elif kind=='transcript':
   if value[0] in ('Boss','User','user'):self.chat_dismissed=False
   self.chat_activity(complete=False)
   if self.stream_role!=value[0]:
    if self.stream_role:self.chat_output.insert('end','\n')
    self.chat_output.insert('end',value[0]+': ',('speaker',));self.stream_role=value[0]
   self.chat_output.insert('end',value[1]);self.chat_output.see('end')
  elif kind=='conversation_turn':
   if self.stream_role:self.chat_output.insert('end','\n\n');self.stream_role=None
   self.chat_activity()
  elif kind=='wake_wait':
   self.voice_state.configure(text='सुन्दैछु • हरेक request सुरु गर्दा SARU भन्नुहोस्।')
  elif kind=='error':
   self.chat_activity();self.chat_output.insert('end','Voice setup: '+value+'\n');self.chat_output.see('end')
  elif kind in ('input_level','output_level'):
   self.update_hero_meter(value)
   self.voice_meter.delete('all');self.voice_meter.create_rectangle(0,0,self.voice_meter.winfo_width()*value,5,fill=CYAN if kind=='input_level' else PINK,outline='')
 def update_hero_meter(self,value):
  if not hasattr(self,'hero_meter_center'):return
  import math
  vx,vy=self.hero_meter_center
  for i,item in enumerate(self.hero_meter):
   h=2+max(0,min(1,float(value)))*22*(.4+.6*abs(math.sin(i*1.7)))
   self.ring.coords(item,vx+(i-4)*5,vy-h,vx+(i-4)*5,vy+h)
 def focus_chat(self):
  self.chat_dismissed=False;self.chat_activity();self.command.focus_set();self.chat_output.see('end')
 def show_tools(self):
  self.tools_menu.tk_popup(self.nav.winfo_rootx()+self.nav.winfo_width(),self.nav.winfo_rooty()+100)
 def show_home(self):
  if self.home_view!='assistant':self.toggle_workspace()
  self.content.yview_moveto(0)
 def focus_control(self,name):
  if not self.details_open:self.toggle_details()
  self.update_idletasks()
  self.content.yview_moveto(self.control_panel.winfo_y()/max(1,self.body.winfo_height()))
  self.scales[name].focus_set();self.values[name].configure(fg=PINK)
 def toggle_workspace(self):
  self.home_view='office' if self.home_view=='assistant' else 'assistant'
  self.workspace_button.configure(text='SARU Office' if self.home_view=='assistant' else 'Assistant home')
  if 'Set home view' in self.actions:self.actions['Set home view'](self.home_view)
  self.compact=None;self.reflow(self.body.winfo_width())
 def toggle_details(self):
  self.details_open=not self.details_open
  self.details_button.configure(text='Device & AI controls ▴' if self.details_open else 'Device & AI controls ▾')
  self.compact=None;self.reflow(self.body.winfo_width())
 def reflow(self,width):
  compact=width<850
  available=max(560,self.content.winfo_height()-10)
  signature=(compact,available,self.home_view,self.details_open)
  if signature==getattr(self,'layout_signature',None):return
  self.layout_signature=signature;self.compact=compact
  hero,metrics,controls,provider,quick,social,activity=self.panels
  for section in self.panels:section.grid_remove()
  for row in range(8):self.body.rowconfigure(row,weight=0,minsize=0)
  self.body.columnconfigure(0,weight=63,uniform='main' if not compact else '')
  self.body.columnconfigure(1,weight=37,uniform='main' if not compact else '')
  hero.configure(height=available)
  self.activity.configure(wraplength=max(200,int(width*(.35 if not compact else .9))))
  if self.home_view=='assistant':
   self.office_preview.pack_forget();self.office_hint.pack_forget();self.activity_title.configure(text='◷  Recent Activity')
  else:
   self.office_preview.pack(fill='both',expand=True,padx=8,before=self.activity)
   self.office_hint.pack(anchor='w',padx=12,before=self.activity);self.activity_title.configure(text='SARU OFFICE / Mind · Memory · Team')
  if self.home_view=='office':
   activity.grid(row=0,column=0,columnspan=2,sticky='nsew',pady=3);self.body.rowconfigure(0,weight=1)
  elif compact:
   for row,section in enumerate((hero,metrics,quick,activity)):section.grid(row=row,column=0,columnspan=2,rowspan=1,sticky='nsew',padx=2,pady=6)
  else:
   hero.grid(row=0,column=0,rowspan=3,columnspan=1,sticky='nsew',padx=(0,12),pady=3)
   for row,section in enumerate((metrics,quick,activity)):section.grid(row=row,column=1,rowspan=1,columnspan=1,sticky='nsew',pady=6)
   self.body.rowconfigure(2,weight=1)
  if self.details_open:
   controls.grid(row=4,column=0,columnspan=2,sticky='ew',pady=6)
   provider.grid(row=5,column=0,columnspan=2,sticky='ew',pady=6)
   social.grid(row=6,column=0,columnspan=2,sticky='ew',pady=6)
  self.fit_workspace()
 def submit(self,fn):
  if not self.closed:self.jobs.submit(self._work,fn,self.results,-1 if self.control_versions else self.control_revision)
 @staticmethod
 def _work(fn,results,revision):
  try:results.put(('ok',fn(),revision))
  except Exception as exc:results.put(('error',str(exc),revision))
 def poll(self):
  if self.closed:return
  try:
   while True:
    kind,result,revision=self.results.get_nowait();self.pending=False
    if kind=='ok':
     if revision!=self.control_revision:result={k:v for k,v in result.items() if k not in ('volume','brightness','mic_gain','muted')}
     self.render(result)
    else:self.network.configure(text='Device operation failed: '+result[:100])
  except Empty:pass
  if not self.pending:
   self.pending=True;self.submit(pc_telemetry.isolated_snapshot if self.device_refresh_count%3==0 else pc_telemetry.metrics_snapshot);self.device_refresh_count+=1
  self.refresh_id=self.after(2000,self.poll)
 def render(self,data):
  if 'muted' in data and 'mute' not in self.control_versions:

   self.muted=data['muted'];self.mute_button.configure(state='normal',text='Unmute speakers' if self.muted else 'Mute speakers')
  for key,g in self.gauges.items():
   if key not in data:continue
   g.delete('all');value=data[key]
   if value is None:g.create_text(42,41,text='N/A',fill=MUTED);g.create_text(42,94,text=key.upper(),fill=MUTED);continue
   g.create_oval(12,5,84,77,outline='#193a55',width=7);g.create_arc(12,5,84,77,start=90,extent=-360*value/100,outline=PINK if key=='disk' else CYAN,width=7,style='arc');g.create_text(48,41,text=f'{value:.0f}%',fill=TEXT,font=('Segoe UI',15,'bold'));g.create_text(48,94,text={'disk':'STORAGE','battery':'BATTERY'}.get(key,key.upper()),fill=MUTED)
  from theme_manager import apply_theme
  apply_theme(self,self.cfg.get('theme','Neon Rose'))
  theme=self.cfg.get('theme','Neon Rose')
  if getattr(self,'hero_theme',None)!=theme:
   self.hero_theme=theme;self.resize_hero(self.ring.winfo_width(),self.ring.winfo_height(),self.cfg.get('photo'))
  self.refresh_activity()
  if 'internet_online' in data:
   online=data['internet_online'];self.online.configure(text='● Online' if online is True else '● Offline' if online is False else '● Checking',fg='#00e676' if online is True else '#ff3b30' if online is False else MUTED)
   self.network.configure(text=data.get('internet_detail','Internet status unavailable'),fg=MUTED)
  for name,scale in self.scales.items():
   if name not in data or name in self.dragging or name in self.control_versions:continue
   value=data[name]
   if value is None:scale.configure(state='disabled');self.values[name].configure(text='Unavailable on this device',fg=MUTED)
   else:
    scale.configure(state='normal')
    scale.set(value)
    self.values[name].configure(text=f'{value}%'+(' • Muted' if name=='volume' and data.get('muted') else ''),fg=CYAN)
 def refresh_activity(self):
  self.refresh_office_preview()
  if not self.activity_path:return
  try:
   with Path(self.activity_path).open('rb') as stream:
    stream.seek(0,2);size=stream.tell();stream.seek(max(0,size-16384));records=stream.read().decode('utf8',errors='replace').splitlines()
   if size>16384:records=records[1:]
   records=records[-5:]
   rows=[]
   for line in reversed(records):
    record=json.loads(line);rows.append(str(record.get('at',''))+'   •   '+str(record.get('action','Task')))
   self.activity.configure(text='\n'.join(rows) or 'No recorded tasks yet.')
  except (OSError,ValueError):self.activity.configure(text='No recorded tasks yet.')
 def fit_workspace(self,event=None):
  if not hasattr(self,'body_item'):return
  self.content.itemconfigure(self.body_item,width=self.content.winfo_width(),height=max(560,self.content.winfo_height()) if self.home_view=='office' else 0)
  if event is not None:self.reflow(self.content.winfo_width())
 def refresh_office_preview(self):
  if self.closed or not hasattr(self,'office_preview') or not self.activity_path:return
  from office_core import Office
  from office_scene import draw_office
  from office_observer import OfficeObserver
  from theme_manager import palette
  if not hasattr(self,'office_observer'):self.office_observer=OfficeObserver(Office(Path(self.activity_path).parent))
  agents,state=self.office_observer.read()
  draw_office(self.office_preview,palette(self.cfg.get('theme')),agents,state,int(getattr(self,'office_phase',0)),reduced=self.cfg.get('reduced_motion',False))
 def office_scene_click(self,event):
  tags=self.office_preview.gettags('current')
  if 'memory' in tags:self.actions['Saved memory']();return
  if 'mind' in tags:
   from office_observer import show_mind
   show_mind(self,self.office_observer.office,self.cfg,self.office_observer.state);return
  self.actions['SARU Office']()
 def toggle_mute(self):
  self.control_revision+=1;self.control_versions['mute']=self.controls.set('mute',not self.muted)
 def drag_slider(self,name,event,start=False):
  scale=self.scales[name]
  if str(scale.cget('state'))=='disabled':return 'break'
  if start:self.dragging.add(name);scale.focus_set()
  left=scale.coords(0)[0];right=scale.coords(100)[0]
  scale.set(round(max(0,min(1,(event.x-left)/max(1,right-left)))*100))
  self.schedule_apply(name);return 'break'
 def release_slider(self,name,event):
  if str(self.scales[name].cget('state'))=='disabled':return 'break'
  self.drag_slider(name,event);self.dragging.discard(name);self.apply(name);return 'break'
 def wheel_slider(self,name,event):
  scale=self.scales[name]
  if str(scale.cget('state'))!='disabled':
   scale.set(scale.get()+(1 if event.delta>0 else -1));self.schedule_apply(name)
  return 'break'
 def schedule_apply(self,name):
  if str(self.scales[name].cget('state'))=='disabled':return
  self.values[name].configure(text=str(self.scales[name].get())+'% …',fg=CYAN)
  if name not in self.commit_ids:self.commit_ids[name]=self.after(100,lambda:self.apply(name))
 def apply(self,name):
  job=self.commit_ids.pop(name,None)
  if job:
   try:self.after_cancel(job)
   except tk.TclError:pass
  if self.closed or str(self.scales[name].cget('state'))=='disabled':return
  value=self.scales[name].get()
  if self.control_targets.get(name)==value and name in self.control_versions:return
  self.control_targets[name]=value;self.control_revision+=1
  self.control_versions[name]=self.controls.set(name,value)
  self.values[name].configure(text=str(value)+'% …',fg=CYAN)
 def poll_controls(self):
  if self.closed:return
  try:
   while True:
    name,version,result,error=self.controls.events.get_nowait()
    if self.control_versions.get(name)!=version:continue
    self.control_versions.pop(name,None);self.control_targets.pop(name,None)
    if error:
     target=self.values.get(name)
     if target:target.configure(text='Failed',fg=PINK)
     self.network.configure(text=error)
    else:self.render(result)
  except Empty:pass
  self.control_poll_id=self.after(50,self.poll_controls)
 def resize_hero(self,width,height,portrait):
  if self.hero_resize_job:self.after_cancel(self.hero_resize_job)
  def draw():
   self.hero_resize_job=None
   from dashboard_layout import draw_hero
   draw_hero(self,width,height,portrait)
  self.hero_resize_job=self.after(80,draw)
 def animate(self,angle):
  if self.closed:return
  if not self.cfg.get('reduced_motion',False) and self.hero_voice_state in ('LISTENING','SPEAKING'):
   from appearance_controls import frame_index
   self.hero_phase+=.14;self.ring.itemconfigure(self.arc,start=angle)
   if getattr(self,'avatar_frames',None):self.ring.itemconfigure(self.avatar_item,image=self.avatar_frames[frame_index(self.hero_voice_state,self.hero_phase)])
  self.office_phase=getattr(self,'office_phase',0)+1
  if not self.details_open:self.refresh_office_preview()
  self.pulse_id=self.after(100,lambda:self.animate((angle+3)%360))
 def _destroy(self,event):
  if event.widget is not self:return
  self.closed=True
  self.cancel_chat_idle()
  self.controls.close()
  for job in (self.refresh_id,self.pulse_id,self.control_poll_id,self.hero_resize_job,*self.commit_ids.values()):
   if job:
    try:self.after_cancel(job)
    except tk.TclError:pass
  self.jobs.shutdown(wait=False,cancel_futures=True)
