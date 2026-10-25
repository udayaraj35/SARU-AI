"""Tabbed settings matching the SARU command center. No decorative form controls."""
import copy
import tkinter as tk
from tkinter import ttk,messagebox
from neon_ui import *

class SettingsPanel(tk.Frame):
 def __init__(self,root,cfg,save,back,actions):
  super().__init__(root,bg=BG);self.place(relwidth=1,relheight=1);self.animation_job=None;self.closed=False;self.bind('<Destroy>',self.cleanup,add='+');self.cfg=cfg;self.save_config=save;self.actions=actions;self.fields={}
  head=tk.Frame(self,bg='#09152a');head.pack(fill='x')
  button(head,'← Dashboard',back).pack(side='left',padx=16,pady=12)
  label(head,'SARU / SETTINGS',font=('Segoe UI',21,'bold'),fg=CYAN).pack(side='left',padx=18)
  self.glow=tk.Canvas(self,height=3,bg='#132642',highlightthickness=0);self.glow.pack(fill='x');self.glowline=self.glow.create_line(0,1,160,1,fill=CYAN,width=3)
  self.animate(0)
  self.note=label(self,'Changes apply when you press Save settings.',fg=MUTED);self.note.pack(anchor='w',padx=24,pady=9)
  book=ttk.Notebook(self);book.pack(fill='both',expand=True,padx=20,pady=5);self.book=book
  self.pages={}
  for title in ['AI & API','Voice','Appearance','PC & Audio','Memory','Security','Updates','Tools']:
   page=tk.Frame(book,bg=BG);book.add(page,text=title)
   canvas=tk.Canvas(page,bg=BG,highlightthickness=0);canvas.pack(side='left',fill='both',expand=True)
   scroll=ttk.Scrollbar(page,orient='vertical',command=canvas.yview);scroll.pack(side='right',fill='y');canvas.configure(yscrollcommand=scroll.set)
   body=tk.Frame(canvas,bg=BG);item=canvas.create_window((0,0),window=body,anchor='nw')
   canvas.bind('<Configure>',lambda e,c=canvas,i=item:c.itemconfigure(i,width=e.width))
   body.bind('<Configure>',lambda e,c=canvas:c.configure(scrollregion=c.bbox('all')))
   self.pages[title]=body
  def group(page,title):
   f=card(self.pages[page],title);f.pack(fill='x',padx=12,pady=10);return f
  def field(parent,key,title,default='',secret=False,choices=None):
   label(parent,title,fg=MUTED).pack(anchor='w',padx=16,pady=(8,4))
   var=tk.StringVar(value=cfg.get(key,default));self.fields[key]=var
   widget=ttk.Combobox(parent,textvariable=var,values=choices,state='readonly') if choices else entry(parent,var,secret)
   widget.pack(fill='x',padx=16,pady=(0,8),ipady=6)
   return var
  api=group('AI & API','PROVIDER CONNECTION')
  self.provider=field(api,'provider','AI provider',choices=['Gemini','OpenAI','Anthropic','DeepSeek','Groq','OpenRouter','Custom'])
  self.model=field(api,'model','Model identifier')
  self.key=field(api,'new_key','API key • Leave blank to retain saved key',secret=True)
  self.key_entry=api.winfo_children()[-1]
  reveal=tk.BooleanVar(value=False)
  tk.Checkbutton(api,text='Show entered key',variable=reveal,command=lambda:self.key_entry.configure(show='' if reveal.get() else '*'),bg=PANEL,fg=MUTED,selectcolor=BG).pack(anchor='w',padx=16)
  self.connection=label(api,'',fg=CYAN);self.connection.pack(anchor='w',padx=16,pady=8)
  self.staged_models=copy.deepcopy(cfg.get('provider_models',{}));self.current=self.provider.get()
  def provider_changed(*args):
   previous=self.current;self.staged_models[previous]=self.model.get();self.current=self.provider.get()
   self.model.set(self.staged_models.get(self.current,''));self.key.set('');self.refresh_key_state()
  self.provider.trace_add('write',provider_changed);self.refresh_key_state()
  field(api,'custom_url','Custom compatible base URL','https://api.openai.com/v1')
  button(api,'Delete saved key for selected provider',self.delete_key).pack(fill='x',padx=16,pady=5)
  button(api,'Test saved API',actions['API test']).pack(fill='x',padx=16,pady=5)
  button(api,'Find Gemini models',actions['Models']).pack(fill='x',padx=16,pady=(5,14))
  voice=group('Voice','INPUT & SPEECH')
  field(voice,'voice_language','Recognition language (ne-NP / en-US / bg-BG)','ne-NP')
  field(voice,'mic_device','Microphone device index (-1 = system default)',-1)
  field(voice,'voice_rate','Speech speed (80–300 words/min)',170)
  field(voice,'voice_gender','Windows voice preference','Female',choices=['Female','Male'])
  field(voice,'wake_greeting','Custom SARU greeting','हजुर सर, भन्नुहोस्। म सुन्दैछु।')
  live=group('Voice','GEMINI LIVE / CLOUD CONVERSATION')
  field(live,'live_model','Gemini Live model identifier','gemini-3.8-live')
  field(live,'live_voice','Cloud conversation voice (fixed until you change it) • Aoede female / Puck male','Aoede',choices=['Aoede','Kore','Puck','Charon','Fenrir'])
  def voice_preset(gender,voice):
   self.fields['voice_gender'].set(gender);self.fields['live_voice'].set(voice);self.note.configure(text='Voice selected. Save settings; Stop voice and start again for the new cloud voice.',fg=CYAN)
  button(live,'Male voice preset • Windows Male + Gemini Puck',lambda:voice_preset('Male','Puck')).pack(fill='x',padx=16,pady=4)
  button(live,'Female voice preset • Windows Female + Gemini Aoede',lambda:voice_preset('Female','Aoede')).pack(fill='x',padx=16,pady=4)
  label(live,'Live chat and local command replies use the same selected cloud voice. Classic Windows voice preview is separate; it is not the Gemini voice.',fg=MUTED,wraplength=650,justify='left').pack(padx=16,pady=6)
  field(live,'output_device','Speaker device index (-1 = system default)',-1)
  self.auto=tk.BooleanVar(value=cfg.get('auto_listen',True));self.check(live,'Automatically listen when SARU starts • Audio goes to Gemini',self.auto)
  self.wake=tk.BooleanVar(value=cfg.get('wake_word_required',True));self.check(live,'Require SARU to activate voice conversation',self.wake)
  self.followup=tk.BooleanVar(value=cfg.get('wake_conversation',True));self.check(live,'Wake once, then continue talking • Return to wake mode after 60 seconds idle',self.followup)
  label(live,'With follow-up enabled, say SARU once; then questions/commands need no repeated name while the conversation is active. Disable follow-up for strict SARU on every request. Stop listening ends it. This is not speaker verification: nearby voices can be accepted while active. Audio goes to Gemini. Save and restart voice after changing this mode.',fg=MUTED,wraplength=650,justify='left').pack(padx=16,pady=8)
  self.headphones=tk.BooleanVar(value=cfg.get('live_headphones',False));self.check(live,'I use headphones • Allow microphone during playback',self.headphones)
  label(live,'Live audio uses your saved Gemini key, regardless of chat provider. Availability/quota depends on your account. Automatic listening is visible in the main chat and floating indicator; Stop always ends it.',fg=MUTED,wraplength=650,justify='left').pack(padx=16,pady=12)
  button(live,'Open Live Voice',actions['Live Voice']).pack(fill='x',padx=16,pady=8)
  self.speak=tk.BooleanVar(value=cfg.get('speak',True));self.check(voice,'Speak AI replies',self.speak)
  for title in ['Audio Center','Voice Studio','Test voice','Test microphone']:button(voice,title,actions[title]).pack(fill='x',padx=16,pady=4)
  look=group('Appearance','IDENTITY & MOTION')
  from theme_manager import THEMES
  field(look,'theme','Interface theme','Neon Rose',choices=list(THEMES))
  field(look,'dashboard_style','Main workspace','Holographic',choices=['Holographic','Portrait'])
  region=group('Appearance','CLOCK / COUNTRY & TIMEZONE')
  region.pack_configure(before=look)
  from clock_regions import country_catalog,country_choices,country_for_zone,country_code,zones_for_country,OTHER
  catalog=country_catalog();zone=cfg.get('display_timezone','Europe/Sofia')
  code=cfg.get('display_country',country_for_zone(zone))
  if code not in catalog or zone not in zones_for_country(code):code=country_for_zone(zone)
  country_var=field(region,'display_country','Clock country',choices=country_choices())
  country_var.set(catalog[code]['label'] if code else OTHER)
  zone_var=field(region,'display_timezone','Timezone / city',zone,choices=zones_for_country(code))
  self.country_picker=region.winfo_children()[-3];self.timezone_picker=region.winfo_children()[-1]
  def country_changed(*args):
   selected=country_code(country_var.get());choices=zones_for_country(selected)
   self.timezone_picker.configure(values=choices)
   if zone_var.get() not in choices:zone_var.set(choices[0])
  country_var.trace_add('write',country_changed)
  label(region,'Countries with several timezones also need a city/timezone choice. Save settings to apply. The PC clock and weather city are unchanged; Nepali date remains shown separately.',fg=MUTED,wraplength=650,justify='left').pack(anchor='w',padx=16,pady=10)
  def size_slider(key,title,default,low,high):
   label(look,title,fg=MUTED).pack(anchor='w',padx=16,pady=(10,2))
   var=tk.StringVar(value=cfg.get(key,default));self.fields[key]=var
   tk.Scale(look,from_=low,to=high,resolution=1,orient='horizontal',variable=var,bg=PANEL,fg=TEXT,troughcolor=BG,highlightthickness=0).pack(fill='x',padx=16,pady=4)
  size_slider('orb_size','Desktop photo size',100,48,240)
  size_slider('orb_text_size','Desktop labels and right-click menu text',12,10,22)
  size_slider('hero_photo_size','Dashboard photo size (%)',100,60,110)
  size_slider('ui_text_scale','Interface text size (%)',100,90,140)
  self.motion=tk.BooleanVar(value=cfg.get('reduced_motion',False));self.check(look,'Reduced motion • Stop decorative neon ring',self.motion)
  self.topmost=tk.BooleanVar(value=cfg.get('orb_topmost',True));self.check(look,'Keep floating SARU above other windows',self.topmost)
  self.snap=tk.BooleanVar(value=cfg.get('orb_snap',True));self.check(look,'Snap floating SARU to screen edges',self.snap)
  self.orb=tk.BooleanVar(value=cfg.get('orb_visible',True));self.check(look,'Show floating assistant',self.orb)
  for title in ['Change portrait','Change background','Change floating portrait','Create portrait icon','Shortcuts','Restore background']:button(look,title,actions[title]).pack(fill='x',padx=16,pady=4)
  label(look,'Portrait gently zooms while listening/speaking and rests when stopped. Bars use real audio levels; Reduced motion keeps the portrait still.',fg=MUTED,wraplength=600).pack(anchor='w',padx=16,pady=12)
  pc=group('PC & Audio','REAL DEVICE CONTROLS')
  label(pc,'Dashboard sliders read actual Windows speaker / first supported display values. Unsupported hardware is marked unavailable.',fg=MUTED,wraplength=650,justify='left').pack(anchor='w',padx=16,pady=10)
  for title in ['Audio Center','Brightness','PC Health','Connectivity','Commands','Emergency Stop']:button(pc,title,actions[title]).pack(fill='x',padx=16,pady=5)
  memory=group('Memory','LOCAL MEMORY')
  field(memory,'weather_city','Weather city','Kathmandu')
  field(memory,'work_folder','Default work folder — ask where to save each deliverable','D:/SARU_AI/Work')
  self.remember=tk.BooleanVar(value=cfg.get('remember_conversations',True));self.check(memory,'Keep text and completed voice conversations in local memory',self.remember)
  label(memory,'Open View notes / Memory to search conversations, notes, actual task results and office work. Use recall <topic> in chat or voice. Saving off stops new journal entries and automatic lookup; existing memory remains local. API keys/passwords and raw microphone recordings are excluded.',fg=MUTED,wraplength=650).pack(padx=16,pady=8)
  field(memory,'companion_style','Conversation style','Warm romantic',choices=['Warm romantic','Friendly','Professional'])
  for title in ['View notes','Save note','Export memory','SARU Storage & RAM']:button(memory,title,actions[title]).pack(fill='x',padx=16,pady=6)
  sec=group('Security','WINDOWS ACCOUNT PROTECTION')
  label(sec,'API keys use Windows DPAPI. Sensitive PC actions require your owner PIN and confirmation. Voice is not identity verification.',fg=MUTED,wraplength=650,justify='left').pack(padx=16,pady=12,anchor='w')
  button(sec,'Set / change owner PIN',actions['Security PIN']).pack(fill='x',padx=16,pady=8)
  updates=group('Updates','RELEASE CHANNEL')
  field(updates,'saru_release_repo','Official SARU repository (owner/repo)')
  for title in ['SARU Office','Repository Skills','Improve SARU','Update Center','MYRA Companion','Dependencies']:button(updates,title,actions[title]).pack(fill='x',padx=16,pady=6)
  tools=group('Tools','CONNECTED WORKFLOWS')
  for title in ['Advanced workspace','Social drafts','Gmail draft','YouTube Studio','Website Studio','Developer / REA','Owner Profile','Help / commands']:button(tools,title,actions[title]).pack(fill='x',padx=16,pady=5)
  foot=tk.Frame(self,bg='#09152a');foot.pack(fill='x',padx=20,pady=12)
  button(foot,'Save settings',self.commit,True).pack(side='right',padx=10,pady=5)
  label(foot,'Local settings • Changes preserved across updates',fg=MUTED).pack(side='left',padx=10)
  book.bind('<<NotebookTabChanged>>',lambda e:self.note.configure(text='Settings / '+book.tab(book.select(),'text'),fg=CYAN))
 def check(self,parent,text,var):
  tk.Checkbutton(parent,text=text,variable=var,bg=PANEL,fg=TEXT,selectcolor=BG,activebackground=PANEL,activeforeground=CYAN).pack(anchor='w',padx=16,pady=6)
 def refresh_key_state(self):self.connection.configure(text='Saved key: '+('Encrypted for this Windows account' if self.cfg.get('keys',{}).get(self.provider.get()) else 'Not configured'))
 def delete_key(self):
  provider=self.provider.get()
  if messagebox.askyesno('Delete API key','Remove the saved '+provider+' key?',parent=self):
   old=copy.deepcopy(self.cfg)
   try:self.cfg.setdefault('keys',{}).pop(provider,None);self.save_config()
   except Exception as exc:self.cfg.clear();self.cfg.update(old);messagebox.showerror('Save failed',str(exc),parent=self);return
   self.key.set('');self.refresh_key_state()
 def commit(self):
  try:
   values={k:v.get().strip() for k,v in self.fields.items() if k!='new_key'}
   for name,low,high in [('orb_size',48,240),('orb_text_size',10,22),('hero_photo_size',60,110),('ui_text_scale',90,140),('voice_rate',80,300),('mic_device',-1,10000),('output_device',-1,10000)]:
    values[name]=int(values[name])
    if not low<=values[name]<=high:raise ValueError(f'{name}: choose {low}–{high}.')
   if not values['model']:raise ValueError('Enter a model identifier for the selected provider.')
   if not values['custom_url'].startswith(('https://','http://localhost','http://127.0.0.1')):raise ValueError('Use HTTPS or a local compatible endpoint.')
   from clock_regions import country_code,validate_clock
   values['display_country'],values['display_timezone']=validate_clock(country_code(values['display_country']),values['display_timezone'])
  except ValueError as exc:self.note.configure(text=str(exc),fg=PINK);return
  old=copy.deepcopy(self.cfg)
  try:
   if values.get('voice_gender')!=self.cfg.get('voice_gender','Female'):self.cfg['voice_id']=''
   self.staged_models[self.provider.get()]=self.model.get().strip()
   self.cfg.update(values,remember_conversations=self.remember.get(),auto_listen=self.auto.get(),wake_word_required=self.wake.get(),wake_conversation=self.followup.get(),orb_topmost=self.topmost.get(),orb_snap=self.snap.get(),live_headphones=self.headphones.get(),speak=self.speak.get(),reduced_motion=self.motion.get(),orb_visible=self.orb.get(),provider_models=self.staged_models)
   if self.key.get().strip():self.cfg.setdefault('keys',{})[self.provider.get()]=self.key.get().strip()
   self.save_config();self.key.set('');self.refresh_key_state();self.note.configure(text='Settings saved • Return to Dashboard to see updated appearance.',fg=CYAN)
   self.actions['Apply appearance']()
  except Exception as exc:self.cfg.clear();self.cfg.update(old);self.note.configure(text='Save failed: '+str(exc),fg=PINK)

 def animate(self,offset):
  if self.closed or self.cfg.get('reduced_motion',False):return
  width=max(300,self.winfo_width());self.glow.coords(self.glowline,offset,1,offset+130,1)
  self.animation_job=self.after(55,lambda:self.animate((offset+8)%width))
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True
   if self.animation_job:
    try:self.after_cancel(self.animation_job)
    except tk.TclError:pass
