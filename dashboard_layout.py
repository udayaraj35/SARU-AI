"""Reference-matched SARU layout using native controls and measured values."""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from PIL import Image,ImageTk,ImageOps
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from pathlib import Path
from neon_ui import BG,PANEL,TEXT,MUTED,CYAN,PINK,label,entry
from reference_widgets import NeonButton, RoundedPanel
from portrait_assets import load_portrait
from version import VERSION

ROOT=Path(__file__).resolve().parent

def btn(parent,text,command,primary=False,width=120,height=38):return NeonButton(parent,text,command,primary,width,height)
def panel(parent,title):
 frame=RoundedPanel(parent)
 frame.title_label=label(frame,title,font=('Segoe UI',11,'bold'));frame.title_label.pack(anchor='w',padx=16,pady=(12,8))
 return frame

def build(self,root,actions,status,portrait,reference,cfg,activity_path):
 self.activity_path=activity_path;self.cfg=cfg or {};self.actions=dict(actions);self.jobs=ThreadPoolExecutor(max_workers=1);self.results=Queue();self.closed=False;self.refresh_id=None;self.pulse_id=None;self.pending=False;self.values={};self.scales={};self.commit_ids={};self.drawer_open=False;self.dock_side=None
 from smooth_controls import LatestControls
 self.controls=LatestControls();self.control_versions={};self.control_targets={};self.dragging=set();self.control_revision=0;self.control_poll_id=None;self.device_refresh_count=0;self.stream_role=None;self.hero_voice_state='STOPPED';self.hero_phase=0;self.hero_resize_job=None
 self.bind('<Destroy>',self._destroy,add='+')
 header=tk.Frame(self,bg='#061226');header.pack(fill='x',padx=4,pady=4)
 self.details_open=False;self.home_view='assistant'
 from header_status import HeaderStatus
 self.header_status=HeaderStatus(header,self.cfg);self.header_status.pack(side='left',fill='x',expand=True,padx=8)
 for child in self.header_status.winfo_children():child.pack_forget()
 self.header_status.clock.grid(row=0,column=0,sticky='w',padx=(0,20))
 self.header_status.nepali.grid(row=1,column=0,sticky='w')
 self.header_status.weather.configure(wraplength=430)
 self.header_status.weather.grid(row=0,column=1,rowspan=2,sticky='w')
 self.online=label(header,'● Checking',fg=CYAN,font=('Segoe UI',9));self.online.pack(side='right',padx=8)
 self.state=label(self,'',fg=CYAN,anchor='w',font=('Segoe UI',9));self.state.configure(textvariable=status);self.state.pack(fill='x',padx=16,pady=(0,1))
 composer=RoundedPanel(self,neon=True);self.composer=composer;composer.pack(side='bottom',fill='x',padx=(276,10),pady=(4,3))
 btn(composer,'🎙',self.actions['Start voice'],True,width=58,height=54).pack(side='left',padx=8,pady=5)
 btn(composer,'➤',lambda:self.command.event_generate('<Return>'),True,width=66,height=54).pack(side='right',padx=8,pady=5)
 btn(composer,'▧',self.actions['Files: summarize'],width=40,height=40).pack(side='right',padx=3)
 btn(composer,'📎',self.actions['Files: summarize'],width=40,height=40).pack(side='right',padx=3)
 self.command=entry(composer,tk.StringVar());self.command.pack(side='left',fill='x',expand=True,ipady=11,padx=8)
 self.placeholder=label(composer,'Ask me anything…  /  Say SARU before a voice request',fg=MUTED,font=('Segoe UI',11))
 self.placeholder.configure(bg='#081225')
 def hint(event=None):
  if self.command.get() or self.command==self.focus_get():self.placeholder.place_forget()
  else:self.placeholder.place(in_=self.command,x=8,rely=.5,anchor='w')
 self.placeholder.bind('<Button-1>',lambda e:self.command.focus_set())
 for event in ('<FocusIn>','<FocusOut>','<KeyRelease>'):self.command.bind(event,hint,add='+')
 hint()
 chips=tk.Frame(self,bg=BG);self.chips=chips;chips.pack(side='bottom',fill='x',padx=(276,10),pady=3,before=composer)
 for title,key in [('Open Chrome','Open App'),('Search on Google','Web search'),('Summarize this file','Files: summarize'),('YouTube player','YouTube Player')]:
  callback=(lambda:self.actions['Search text']('open Google Chrome')) if title=='Open Chrome' else self.actions[key]
  btn(chips,title,callback,width=135,height=30).pack(side='left',expand=True,fill='x',padx=4)
 shell=tk.Frame(self,bg=BG);self.shell=shell;shell.pack(fill='both',expand=True,padx=8)
 nav=tk.Frame(shell,bg='#071326',width=300);self.nav=nav;nav.pack(side='left',fill='y',padx=(0,10));nav.pack_propagate(False)
 brand=tk.Frame(nav,bg='#071326');brand.pack(fill='x',padx=12,pady=(16,12))
 try:
  with Image.open(ROOT/'dashboard.png') as art:self.logo=ImageTk.PhotoImage(art.crop((20,5,95,80)).resize((56,56)))
  tk.Label(brand,image=self.logo,bg='#071326').pack(side='left',padx=(0,6))
 except OSError:pass
 brandline=tk.Frame(brand,bg='#071326');brandline.pack(fill='x')
 label(brandline,'SARU',font=('Segoe UI',24,'bold')).pack(side='left');label(brandline,' AI',font=('Segoe UI',24,'bold'),fg=PINK).pack(side='left')
 label(brand,'Personal PC Assistant',font=('Segoe UI',9),fg=MUTED).pack(anchor='w')
 owner=tk.Frame(nav,bg='#071326');owner.pack(side='bottom',fill='x',pady=8,padx=12)
 btn(owner,'Owner profile',self.actions['Owner Profile'],height=28).pack(fill='x')
 label(owner,'Smarter Tools',font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(8,0))
 label(owner,'for a Better You',fg=PINK,font=('Segoe UI',12,'bold')).pack(anchor='w')
 self.settings_button=btn(nav,'⚙  Settings',self.actions['Settings'],width=190,height=37);self.settings_button.pack(side='bottom',fill='x',padx=4,pady=5)
 navcanvas=tk.Canvas(nav,bg='#071326',highlightthickness=0)
 navscroll=ttk.Scrollbar(nav,orient='vertical',command=navcanvas.yview);navscroll.pack(side='right',fill='y');navcanvas.configure(yscrollcommand=navscroll.set);navcanvas.pack(side='left',fill='both',expand=True)
 self.navcanvas=navcanvas;links=tk.Frame(navcanvas,bg='#071326');self.sidebar_links=links;navitem=navcanvas.create_window((0,0),window=links,anchor='nw');self.nav_buttons={}
 navcanvas.bind('<Configure>',lambda e:navcanvas.itemconfigure(navitem,width=e.width));links.bind('<Configure>',lambda e:navcanvas.configure(scrollregion=navcanvas.bbox('all')))
 navcanvas.bind('<MouseWheel>',lambda e:navcanvas.yview_scroll(-int(e.delta/120),'units'))
 items=[('⌂  Home',None),('▣  Chat','AI Chat'),('♩  Voice Mode','Voice: push to talk'),('▤  PC Control','PC Commands'),('▦  Apps & Tools','all'),('◎  Automation','Task Console'),('▤  Files & Documents','Files: summarize'),('▧  Media','YouTube Player'),('◉  Web & Search','Web search'),('⌘  Website Studio','Website Studio'),('♧  Social Media','Social Media')]
 for text,key in items:
  command=self.show_home if key is None else self.show_tools if key=='all' else self.actions[key]
  b=btn(links,text,command,key is None,width=190,height=35);b.pack(fill='x',padx=4,pady=3);self.nav_buttons[text]=b;b.bind('<MouseWheel>',lambda e:navcanvas.yview_scroll(-int(e.delta/120),'units'))
 self.workspace_button=btn(links,'SARU Office',self.toggle_workspace,width=190,height=35);self.workspace_button.pack(fill='x',padx=4,pady=3)
 self.details_button=btn(links,'Device & AI controls ▾',self.toggle_details,width=190,height=35);self.details_button.pack(fill='x',padx=4,pady=3)
 self.tools_menu=tk.Menu(self,tearoff=False,bg=PANEL,fg=TEXT,activebackground='#284c70',font=('Segoe UI',10))
 for title,callback in sorted(self.actions.items()):
  if title not in ('Set provider','Set home view','Search text'):self.tools_menu.add_command(label=title,command=callback)
 content=tk.Canvas(shell,bg=BG,highlightthickness=0);self.content=content;content.pack(side='left',fill='both',expand=True)
 bar=tk.Scrollbar(shell,orient='vertical',command=content.yview);bar.pack(side='right',fill='y');content.configure(yscrollcommand=bar.set)
 body=tk.Frame(content,bg=BG);item=content.create_window((0,0),window=body,anchor='nw');self.body=body
 self.body_item=item;content.bind('<Configure>',self.fit_workspace);body.bind('<Configure>',lambda e:content.configure(scrollregion=content.bbox('all')))
 body.columnconfigure(0,weight=63);body.columnconfigure(1,weight=37)
 hero=tk.Frame(body,bg='#061025',height=540);hero.grid(row=0,column=0,rowspan=3,sticky='nsew',padx=(0,8),pady=3);hero.grid_propagate(False);hero.pack_propagate(False)
 self.ring=tk.Canvas(hero,bg='#061025',highlightthickness=0);self.ring.pack(fill='both',expand=True)
 self.hero_buttons=[]
 for title,key in [('●  Chat with me','AI Chat'),('▤  Control your PC','PC Commands'),('⚙  Automate tasks','Task Console'),('⌕  Search the web','Web search'),('▤  Work with files','Files: summarize')]:
  b=btn(self.ring,title,self.actions[key],width=220,height=44);b.neon_outline=True;self.hero_buttons.append(b)
 self.hero_voice_buttons=[]
 for title,key in [('●  Wake Word','Start voice'),('♩  Tap to Talk','Voice: push to talk'),('∞  Voice Mode','Start voice'),('◉  Stop Listening','Stop voice')]:
  self.hero_voice_buttons.append(btn(self.ring,title,self.actions[key],width=150,height=34))
 self.ring.bind('<Configure>',lambda e:self.resize_hero(e.width,e.height,portrait));self.arc=self.ring.create_arc(3,3,100,100,start=0,extent=220,outline=CYAN,style='arc');draw_hero(self,500,480,portrait)
 metrics=panel(body,'◈  System Status');metrics.grid(row=0,column=1,sticky='nsew',pady=3)
 garea=tk.Frame(metrics,bg='#071326');garea.pack(fill='x',padx=8);self.gauges={}
 for i,key in enumerate(('cpu','ram','disk','battery')):
  garea.columnconfigure(i,weight=1);g=tk.Canvas(garea,width=94,height=104,bg='#071326',highlightthickness=0);g.grid(row=0,column=i,sticky='ew');self.gauges[key]=g
 self.network=label(metrics,'Reading network adapter…',fg=MUTED,font=('Segoe UI',9));self.network.pack(fill='x',padx=10,pady=5)
 controls=panel(body,'◖  Audio & Display Control');self.control_panel=controls
 selector=tk.Frame(controls,bg='#071326');selector.pack(fill='x',padx=8)
 for name,title in [('volume','Volume'),('brightness','Brightness'),('mic_gain','Microphone')]:btn(selector,title,lambda n=name:self.focus_control(n),width=90,height=30).pack(side='left',fill='x',expand=True,padx=2)
 for name,title in [('volume','◖'),('brightness','☀'),('mic_gain','🎙')]:
  row=tk.Frame(controls,bg='#071326');row.pack(fill='x',padx=10,pady=1);label(row,title).pack(side='left',padx=3)
  value=label(row,'—',fg=TEXT,width=7);value.pack(side='right');self.values[name]=value
  scale=tk.Scale(row,from_=0,to=100,orient='horizontal',resolution=1,sliderlength=24,width=13,borderwidth=0,showvalue=False,bg='#071326',troughcolor='#12345a',activebackground=CYAN,highlightthickness=0,state='disabled');scale.pack(fill='x',expand=True,padx=5);self.scales[name]=scale
  scale.bind('<Button-1>',lambda e,n=name:self.drag_slider(n,e,True));scale.bind('<B1-Motion>',lambda e,n=name:self.drag_slider(n,e));scale.bind('<ButtonRelease-1>',lambda e,n=name:self.release_slider(n,e))
  scale.bind('<KeyRelease>',lambda e,n=name:self.schedule_apply(n));scale.bind('<MouseWheel>',lambda e,n=name:self.wheel_slider(n,e))
 toggles=tk.Frame(controls,bg='#071326');toggles.pack(fill='x',padx=8,pady=6)
 self.mute_button=btn(toggles,'Mute',self.toggle_mute,width=72,height=30);self.mute_button.configure(state='disabled');self.mute_button.pack(side='left',fill='x',expand=True,padx=2)
 for title,key in [('Mic Off','Mute microphone'),('Night Light','Night Light'),('Eye Care','Eye Care')]:btn(toggles,title,self.actions[key],width=72,height=30).pack(side='left',fill='x',expand=True,padx=2)
 label(controls,'Night Light / Eye Care open Windows display settings.',fg=MUTED,font=('Segoe UI',8)).pack(anchor='w',padx=10,pady=2)
 provider=panel(body,'♫  AI Provider & Model');
 select=tk.Frame(provider,bg='#071326');select.pack(fill='x',padx=10,pady=5)
 self.provider_var=tk.StringVar(value=self.cfg.get('provider','Gemini'));self.model_var=tk.StringVar(value=self.cfg.get('model',''))
 provider_select=ttk.Combobox(select,textvariable=self.provider_var,values=['Gemini','OpenAI','OpenRouter','Custom'],state='readonly',width=14);provider_select.pack(fill='x',pady=2)
 self.model_select=ttk.Combobox(select,textvariable=self.model_var,values=[self.model_var.get()],width=21);self.model_select.pack(fill='x',pady=2)
 provider_select.bind('<<ComboboxSelected>>',lambda e:self.select_provider());self.model_select.bind('<<ComboboxSelected>>',lambda e:self.save_provider());self.model_select.bind('<Return>',lambda e:self.save_provider())
 pr=tk.Frame(provider,bg='#071326');pr.pack(fill='x',padx=8,pady=5)
 for title,key in [('Test API','API test'),('Manage Keys','API Manager'),('Switch','API Manager')]:btn(pr,title,self.actions[key],width=95,height=29).pack(side='left',expand=True,fill='x',padx=2)
 self.provider_key=label(provider,'Key saved' if self.cfg.get('keys',{}).get(self.cfg.get('provider')) else 'API key required',fg=CYAN,font=('Segoe UI',9));self.provider_key.pack(anchor='w',padx=12,pady=3)
 quick=panel(body,'♟  Quick Tools');
 qr=tk.Frame(quick,bg='#071326');qr.pack(fill='x',padx=5,pady=4)
 quickitems=[('▦\nOpen App','Open App'),('▣\nScreenshot','Screenshot'),('▤\nClipboard','Clipboard'),('◖\nVolume','volume'),('☀\nBrightness','brightness'),('▣\nLock PC','Lock PC'),('◯\nShutdown','Shutdown'),('◉\nWhatsApp','WhatsApp draft')]
 for i,(title,key) in enumerate(quickitems):
  qr.columnconfigure(i%4,weight=1,uniform='tools')
  callback=(lambda name=key:self.focus_control(name)) if key in ('volume','brightness') else self.actions[key]
  btn(qr,title,callback,width=72,height=76).grid(row=i//4,column=i%4,sticky='ew',padx=3,pady=4)
 social=panel(body,'♧  Social Media');
 sr=tk.Frame(social,bg='#071326');sr.pack(fill='x',padx=5,pady=4)
 for i,(title,key) in enumerate([('f\nFacebook','Facebook'),('◎\nInstagram','Instagram'),('♪\nTikTok','TikTok'),('▶\nYouTube','YouTube'),('◉\nWhatsApp','WhatsApp draft'),('✉\nGmail','Gmail draft'),('➤\nTelegram','Telegram'),('X\nTwitter','X Twitter')]):sr.columnconfigure(i,weight=1);btn(sr,title,self.actions[key],width=62,height=50).grid(row=0,column=i,sticky='ew',padx=2)
 def wrap_tiles(event):
  frame=event.widget;columns=4 if event.width>=280 else 3
  if getattr(frame,'tile_columns',None)==columns:return
  frame.tile_columns=columns
  for column in range(8):frame.columnconfigure(column,weight=1 if column<columns else 0,minsize=0)
  for index,child in enumerate(frame.winfo_children()):child.grid_configure(row=index//columns,column=index%columns,pady=3,sticky='ew')
 sr.bind('<Configure>',wrap_tiles,add='+')
 activity=panel(body,'SARU OFFICE  /  Mind · Memory · Team');activity.grid(row=3,column=1,rowspan=2,sticky='nsew',pady=3)
 self.activity_title=activity.title_label
 self.office_preview=tk.Canvas(activity,height=310,bg=BG,highlightthickness=0,cursor='hand2');self.office_preview.pack(fill='both',expand=True,padx=8)
 self.office_preview.bind('<Button-1>',self.office_scene_click)
 self.office_preview.bind('<Configure>',lambda event:self.refresh_office_preview())
 self.office_hint=label(activity,'Open office to assign work and review submissions.',fg=MUTED,font=('Segoe UI',9));self.office_hint.pack(anchor='w',padx=12)
 self.activity=label(activity,'No recorded tasks yet.',fg=MUTED,justify='left',anchor='nw',font=('Segoe UI',9));self.activity.pack(fill='x',padx=12,pady=8)
 chat=tk.Frame(self,bg='#071326',width=330,highlightbackground=PINK,highlightthickness=1);self.chat_dock=chat;chat.pack_propagate(False)
 cr=tk.Frame(chat,bg='#071326');cr.pack(fill='x');label(cr,'SARU / CHAT',font=('Segoe UI',12,'bold')).pack(side='left',padx=8)
 transcript=tk.Frame(chat,bg='#081225');transcript.pack(fill='both',expand=True,padx=8,pady=8)
 self.chat_output=tk.Text(transcript,height=5,bg='#081225',fg=TEXT,wrap='word',font=('Segoe UI',11),relief='flat');self.chat_output.pack(side='left',fill='both',expand=True);self.chat_output.tag_configure('speaker',font=('Segoe UI',11,'bold'),foreground=CYAN)
 chat_scroll=ttk.Scrollbar(transcript,orient='vertical',command=self.chat_output.yview);chat_scroll.pack(side='right',fill='y');self.chat_output.configure(yscrollcommand=chat_scroll.set)
 self.voice_state=label(chat,'Voice stopped',fg=CYAN,font=('Segoe UI',9));self.voice_state.pack(fill='x',padx=8)
 self.voice_meter=tk.Canvas(chat,height=5,bg='#11213a',highlightthickness=0);self.voice_meter.pack(fill='x',padx=8,pady=5)
 self.panels=(hero,metrics,controls,provider,quick,social,activity);self.compact=None;body.bind('<Configure>',lambda e:self.reflow(e.width),add='+');self.bind('<Configure>',self.layout_dock,add='+')
 self.poll();self.poll_controls();self.animate(0)

def draw_hero(self,width,height,portrait):
 if width<20 or height<20:return
 from theme_manager import palette
 import math
 p=palette(self.cfg.get('theme'));c=self.ring;c.delete('all');c.configure(bg=p['bg'])
 # Code-drawn halo: themes change its colors without altering the composition.
 cx=width*.265;cy=height*.43;r=min(width*.33,height*.47)
 for offset in range(22,0,-3):
  c.create_oval(cx-r-offset,cy-r-offset,cx+r+offset,cy+r+offset,outline=p['panel'],width=3)
 c.create_oval(cx-r,cy-r,cx+r,cy+r,outline=p['primary'],width=2)
 self.arc=c.create_arc(cx-r-8,cy-r-8,cx+r+8,cy+r+8,start=20,extent=135,outline=p['accent'],style='arc',width=3)
 try:
  photo=load_portrait(portrait,self.cfg.get('portrait_design','new')).convert('RGBA')
  percent=max(60,min(110,int(self.cfg.get('hero_photo_size',100))))/100
  self.avatar_frames=[]
  for index in range(8):
   factor=.985+.015*index/7
   rendered=ImageOps.contain(photo,(max(1,int(width*.64*percent*factor)),max(1,int(height*.97*percent*factor))))
   self.avatar_frames.append(ImageTk.PhotoImage(rendered))
  self.avatar=self.avatar_frames[-1];self.avatar_item=c.create_image(width*.28,height*.51,image=self.avatar,anchor='center')
 except OSError:c.create_text(width*.25,height*.3,text='SARU',fill=p['text'],font=('Segoe UI',28,'bold'))
 x=width*.51;f=max(22,min(40,int(width*.047)))
 c.create_text(x,height*.16,text="Hello, I'm",fill=p['text'],font=('Segoe UI',max(13,f//2),'bold'),anchor='nw')
 title_font=tkfont.Font(family='Segoe UI',size=f,weight='bold')
 c.create_text(x+2,height*.225+2,text='SARU AI',fill=p['panel'],font=title_font,anchor='nw')
 c.create_text(x,height*.225,text='SARU ',fill=p['text'],font=title_font,anchor='nw')
 c.create_text(x+title_font.measure('SARU '),height*.225,text='AI',fill=p['primary'],font=title_font,anchor='nw')
 c.create_text(x,height*.31,text='Your Personal PC Assistant',fill=p['text'],font=('Segoe UI',max(9,min(12,int(width*.017)))) ,anchor='nw',width=width*.47)
 c.create_line(x,height*.365,x+80,height*.365,fill=p['primary'],width=3)
 for i,b in enumerate(self.hero_buttons):
  b.configure(font=('Segoe UI',max(10,min(12,int(width*.016))),'bold'))
  c.create_window(x+width*.01,height*(.44+i*.085),window=b,anchor='w',width=width*.43,height=max(34,int(height*.069)))
 for i,b in enumerate(self.hero_voice_buttons):
  c.create_window(width*(.405+(i%2)*.30),height*(.88+(i//2)*.065),window=b,width=width*.285,height=32)
 # Honest voice state; the meter only moves on actual input/output level events.
 vx=width*.86;vy=height*.08;vr=min(38,width*.07)
 c.create_oval(vx-vr-5,vy-vr-5,vx+vr+5,vy+vr+5,outline=p['line'],width=2)
 c.create_oval(vx-vr,vy-vr,vx+vr,vy+vr,outline=p['primary'],width=2)
 self.hero_meter=[]
 for i in range(9):
  xx=vx+(i-4)*5
  self.hero_meter.append(c.create_line(xx,vy-2,xx,vy+2,fill=p['primary'],width=3))
 self.hero_voice_label=c.create_text(vx,vy+vr+15,text=self.hero_voice_state.replace('_',' ').title(),fill=p['muted'],font=('Segoe UI',9,'bold'))
 self.hero_meter_center=(vx,vy)
