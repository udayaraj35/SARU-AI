"""Theme-aware profile editor with independent owner and creator tabs."""
import tkinter as tk
from tkinter import ttk,filedialog
from PIL import Image,ImageTk,ImageOps
import webbrowser
from pathlib import Path
from urllib.parse import quote
from neon_ui import BG,PANEL,TEXT,MUTED,CYAN,button,label,entry
from profiles import FIELDS,get_profile,save_profile,photo_path,copy_photo,validate_profile
from theme_manager import apply_theme
from appearance_controls import apply_text_scale


class ProfilePanel(tk.Frame):
 def __init__(self,parent,config,save,back,root,data,security):
  super().__init__(parent,bg=BG);self.place(relwidth=1,relheight=1)
  self.cfg=config;self.save_config=save;self.root_path=Path(root);self.data=data;self.fields={};self.photos={};self.images={};self.photo_widgets={}
  top=tk.Frame(self,bg=PANEL);top.pack(fill='x')
  button(top,'← Dashboard',back).pack(side='left',padx=10,pady=10)
  label(top,'OWNER & CREATOR PROFILE',font=('Segoe UI',18,'bold'),fg=CYAN).pack(side='left',padx=10)
  footer=tk.Frame(self,bg=PANEL);footer.pack(side='bottom',fill='x')
  button(footer,'Save selected profile',self.commit,True).pack(side='left',padx=12,pady=10)
  button(footer,'Owner security code',security).pack(side='right',padx=12,pady=10)
  self.status=tk.StringVar(value='Profiles are saved locally. Contact details are not automatically included in AI requests.')
  label(self,'',textvariable=self.status,fg=MUTED,anchor='w',wraplength=1000).pack(side='bottom',fill='x',padx=14,pady=5)
  self.book=ttk.Notebook(self);self.book.pack(fill='both',expand=True,padx=12,pady=12)
  self.tabs={}
  for kind,title in (('owner','Owner · Personal information'),('creator','Creator · About SARU')):
   outer=tk.Frame(self.book,bg=BG);self.book.add(outer,text=title);self.tabs[str(outer)]=kind
   canvas=tk.Canvas(outer,bg=BG,highlightthickness=0);scroll=tk.Scrollbar(outer,command=canvas.yview);scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True);canvas.configure(yscrollcommand=scroll.set)
   body=tk.Frame(canvas,bg=BG);window=canvas.create_window(0,0,window=body,anchor='nw')
   canvas.bind('<Configure>',lambda event,c=canvas,w=window:c.itemconfigure(w,width=event.width))
   body.bind('<Configure>',lambda event,c=canvas:c.configure(scrollregion=c.bbox('all')))
   profile=get_profile(config,kind);self.fields[kind]={};self.photos[kind]=profile.get('photo','')
   identity=tk.Frame(body,bg=PANEL);identity.pack(fill='x',padx=8,pady=8)
   portrait=label(identity,'No profile photo',width=24);portrait.pack(side='left',padx=14,pady=12);self.photo_widgets[kind]=portrait
   details=tk.Frame(identity,bg=PANEL);details.pack(side='left',fill='both',expand=True,padx=8)
   label(details,profile.get('name',''),font=('Segoe UI',21,'bold')).pack(anchor='w',pady=8)
   label(details,'App creator / developer' if kind=='creator' else 'Person using this SARU installation',fg=MUTED).pack(anchor='w')
   button(details,'Choose profile photo',lambda k=kind:self.choose_photo(k)).pack(anchor='w',pady=8)
   links=tk.Frame(details,bg=PANEL);links.pack(fill='x',pady=6)
   for title,key in (('Gmail','email'),('Facebook','facebook'),('YouTube','youtube')):
    b=button(links,title,lambda k=kind,f=key:self.open_contact(k,f));b.pack(side='left',padx=3)
   grid=tk.Frame(body,bg=BG);grid.pack(fill='x',padx=14,pady=8);grid.columnconfigure(1,weight=1)
   for row,(key,title) in enumerate(FIELDS):
    label(grid,title,anchor='w').grid(row=row,column=0,sticky='nw',padx=(0,16),pady=8)
    if key in ('bio','extra'):
     field=tk.Text(grid,height=3,bg='#081225',fg=TEXT,insertbackground=CYAN,wrap='word',font=('Segoe UI',11));field.insert('1.0',profile.get(key,''));field.grid(row=row,column=1,sticky='ew',pady=6);self.fields[kind][key]=field
    else:
     variable=tk.StringVar(value=profile.get(key,''));field=entry(grid,variable);field.grid(row=row,column=1,sticky='ew',pady=6,ipady=7);self.fields[kind][key]=variable
   def wheel(event,c=canvas):c.yview_scroll(-int(event.delta/120),'units');return 'break'
   def bind_wheel(item):
    item.bind('<MouseWheel>',wheel,add='+')
    for child in item.winfo_children():bind_wheel(child)
   bind_wheel(body);canvas.bind('<MouseWheel>',wheel)
   self.show_photo(kind)
  apply_theme(self,config.get('theme','Neon Rose'));apply_text_scale(self,config.get('ui_text_scale',100))
 def values(self,kind):
  return {**{key:(field.get('1.0','end').strip() if isinstance(field,tk.Text) else field.get()) for key,field in self.fields[kind].items()},'photo':self.photos[kind]}
 def show_photo(self,kind):
  path=photo_path({'photo':self.photos[kind]},self.root_path,kind)
  if not path:return
  try:
   with Image.open(path) as source:image=ImageOps.contain(source.convert('RGB'),(170,190),Image.Resampling.LANCZOS)
   self.images[kind]=ImageTk.PhotoImage(image);self.photo_widgets[kind].configure(image=self.images[kind],text='',width=180,height=195)
  except (OSError,ValueError):self.status.set('Saved photo is unavailable. Choose another image.')
 def choose_photo(self,kind):
  path=filedialog.askopenfilename(parent=self,title='Choose '+kind+' photo',filetypes=[('Images','*.jpg *.jpeg *.png *.webp')])
  if not path:return
  try:self.photos[kind]=copy_photo(path,self.data,kind);self.show_photo(kind);self.status.set('Photo selected. Save this profile to keep it.')
  except Exception as exc:self.status.set(str(exc))
 def commit(self):
  kind=self.tabs[self.book.select()]
  try:
   values=validate_profile(self.values(kind));previous=dict(self.cfg)
   save_profile(self.cfg,kind,values)
   try:self.save_config()
   except Exception:self.cfg.clear();self.cfg.update(previous);raise
   self.status.set(kind.title()+' profile saved. Return to Dashboard to refresh its owner card.')
  except Exception as exc:self.status.set(str(exc))
 def open_contact(self,kind,key):
  try:
   values=validate_profile(self.values(kind));value=values.get(key,'')
   if not value:self.status.set('Add this contact first.');return
   webbrowser.open('https://mail.google.com/mail/?view=cm&fs=1&to='+quote(value) if key=='email' else value)
  except Exception as exc:self.status.set(str(exc))
