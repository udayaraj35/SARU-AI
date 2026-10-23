"""Create, preview, approve and submit videos through connected official accounts."""
import copy,json,os,threading
from pathlib import Path
from queue import Queue,Empty
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from neon_ui import BG,PANEL,TEXT,MUTED,CYAN,label,button,entry
from theme_manager import apply_theme
from content_workflow import PublishStore,safe_error
from video_publishers import account_info,post_status,video_file
from video_creator import create_video,video_duration
from youtube_account import connect_youtube

class ContentStudio(tk.Toplevel):
 def __init__(self,parent,config,save,data,platform='YouTube'):
  super().__init__(parent);self.title('SARU • Video & Publishing Studio');self.geometry('940x760');self.minsize(780,620);self.configure(bg=BG)
  self.config_data=config;self.save_config=save;self.store=PublishStore(data);self.events=Queue();self.cancel=threading.Event();self.closed=False;self.busy=False;self.account=None;self.ready=None;self.previewed=None;self.credentials=None;self.photos=[];self.job=None;self.action_buttons=[]
  self.protocol('WM_DELETE_WINDOW',self.close)
  label(self,'VIDEO STUDIO  •  Create → Preview → Approve → Upload',font=('Segoe UI',17,'bold'),fg=CYAN).pack(anchor='w',padx=18,pady=12)
  self.note=tk.StringVar(value='Nothing will be uploaded until you approve the exact draft.');label(self,'',textvariable=self.note,fg=MUTED,wraplength=880,justify='left').pack(fill='x',padx=18,pady=5)
  self.book=ttk.Notebook(self);self.book.pack(fill='both',expand=True,padx=14,pady=10)
  self.create_page=self.page('Create MP4');self.publish_page=self.page('Review & publish');self.accounts_page=self.page('Accounts')
  self.build_create();self.build_publish(platform);self.build_accounts()
  self.book.select(self.publish_page.master.master);self.refresh_theme();self.pump()
 def page(self,title):
  page=tk.Frame(self.book,bg=BG);self.book.add(page,text=title)
  canvas=tk.Canvas(page,bg=BG,highlightthickness=0);canvas.pack(side='left',fill='both',expand=True)
  bar=ttk.Scrollbar(page,orient='vertical',command=canvas.yview);bar.pack(side='right',fill='y');canvas.configure(yscrollcommand=bar.set)
  body=tk.Frame(canvas,bg=BG);item=canvas.create_window(0,0,window=body,anchor='nw')
  canvas.bind('<Configure>',lambda e:canvas.itemconfigure(item,width=e.width));body.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
  return body
 def refresh_theme(self):apply_theme(self,self.config_data.get('theme','Neon Rose'))
 def field(self,parent,title,default='',choices=None,secret=False):
  label(parent,title,fg=MUTED).pack(anchor='w',padx=14,pady=(9,3));var=tk.StringVar(value=default)
  item=ttk.Combobox(parent,textvariable=var,values=choices,state='readonly') if choices else entry(parent,var,secret)
  item.pack(fill='x',padx=14,pady=3,ipady=5);return var,item
 def action(self,parent,title,fn,primary=False):
  item=button(parent,title,fn,primary);item.pack(fill='x',padx=14,pady=5);self.action_buttons.append(item);return item
 def build_create(self):
  body=self.create_page
  label(body,'Build a local slideshow video from your own photos, captions and optional audio.',wraplength=840).pack(anchor='w',padx=14,pady=12)
  self.photo_list=tk.Listbox(body,height=5,bg=PANEL,fg=TEXT);self.photo_list.pack(fill='x',padx=14,pady=5)
  def photos():
   chosen=filedialog.askopenfilenames(parent=self,title='Choose up to 30 photos in slideshow order',filetypes=[('Photos','*.png *.jpg *.jpeg *.webp')])
   if chosen:
    self.photos=list(chosen);self.photo_list.delete(0,'end')
    for path in chosen:self.photo_list.insert('end',Path(path).name)
  self.action(body,'Choose photos',photos)
  label(body,'Caption for each photo (one line per photo)',fg=MUTED).pack(anchor='w',padx=14,pady=6)
  self.captions=tk.Text(body,height=4,bg=PANEL,fg=TEXT,insertbackground=CYAN);self.captions.pack(fill='x',padx=14)
  self.seconds,_=self.field(body,'Seconds per photo (1–15)','3')
  self.aspect,_=self.field(body,'Video shape','Landscape 16:9',['Landscape 16:9','Portrait 9:16'])
  self.audio,_=self.field(body,'Optional audio path (your own WAV / MP3 file)')
  self.action(body,'Choose optional audio',lambda:self.choose_audio())
  self.action(body,'Create MP4 locally',self.render_video,True)
 def choose_audio(self):
  path=filedialog.askopenfilename(parent=self,filetypes=[('Audio','*.wav *.mp3 *.m4a')])
  if path:self.audio.set(path)
 def render_video(self):
  if not self.photos:self.note.set('Choose photos first.');return
  from work_storage import ask_work_save
  target=ask_work_save(self.config_data,parent=self,defaultextension='.mp4',filetypes=[('MP4 video','*.mp4')],title='Choose where SARU should save the video')
  if not target:return
  photos=list(self.photos);captions=self.captions.get('1.0','end').splitlines();seconds=self.seconds.get();portrait=self.aspect.get().startswith('Portrait');audio=self.audio.get().strip() or None
  def done(path):self.video_path.set(str(path));self.note.set('Video created locally. Preview it, then load a publishing account and prepare a review.');self.book.select(self.publish_page.master.master)
  self.run(lambda:create_video(photos,captions,target,seconds,portrait,audio,self.cancel),done,'Rendering MP4…')
 def build_publish(self,platform):
  body=self.publish_page
  self.platform,selector=self.field(body,'Destination platform',platform,['YouTube','Facebook','TikTok']);selector.bind('<<ComboboxSelected>>',lambda e:self.platform_changed())
  self.video_path,_=self.field(body,'Local MP4 (up to 64 MiB)')
  def choose_video():
   path=filedialog.askopenfilename(parent=self,filetypes=[('MP4','*.mp4')])
   if path:self.video_path.set(path)
  self.action(body,'Choose video',choose_video)
  self.account_note=label(body,'Account not loaded',fg=CYAN,wraplength=840);self.account_note.pack(anchor='w',padx=14,pady=7)
  self.action(body,'Load connected account / available visibility',self.load_account)
  self.title_var,_=self.field(body,'Video title (1–100 characters)')
  label(body,'Description / caption',fg=MUTED).pack(anchor='w',padx=14,pady=6)
  self.description=tk.Text(body,height=4,bg=PANEL,fg=TEXT,insertbackground=CYAN);self.description.pack(fill='x',padx=14)
  self.privacy,self.privacy_box=self.field(body,'Visibility • choose after loading your account','',[])
  # An empty choices list still needs a readonly selector.
  self.privacy_box.destroy();self.privacy_box=ttk.Combobox(body,textvariable=self.privacy,state='readonly');self.privacy_box.pack(fill='x',padx=14,pady=3)
  self.kids,_=self.field(body,'YouTube audience • choose explicitly','',['Not made for kids','Made for kids'])
  self.flags={}
  for title,key,default in [('Disable TikTok comments','disable_comment',False),('Disable TikTok duet','disable_duet',False),('Disable TikTok stitch','disable_stitch',False),('Paid partnership / third-party branded content','brand_content',False),('Promotes my own brand','brand_organic',False),('AI-generated content disclosure','is_aigc',False)]:
   var=tk.BooleanVar(value=default);self.flags[key]=var
   tk.Checkbutton(body,text=title,variable=var,bg=BG,fg=TEXT,selectcolor=PANEL,activebackground=BG).pack(anchor='w',padx=14,pady=2)
  label(body,'TikTok: your developer app needs video.publish authorization. Unaudited apps are limited to private posting. Creator restrictions are applied to interactions.',fg=MUTED,wraplength=830,justify='left').pack(anchor='w',padx=14,pady=8)
  self.action(body,'Prepare exact draft for review • no upload',self.prepare,True)
  self.review=tk.Text(body,height=10,bg=PANEL,fg=TEXT,wrap='word',state='disabled');self.review.pack(fill='x',padx=14,pady=8)
  self.action(body,'Preview prepared video in local player',self.preview)
  self.action(body,'I reviewed it — approve and upload this draft',self.approve,True)
  self.action(body,'Check submitted video processing/status',self.check_status)
  self.action(body,'Show recent drafts / submission receipts',self.show_recent)
 def platform_changed(self):
  self.account=None;self.ready=None;self.privacy.set('');self.privacy_box.configure(values=[]);self.account_note.configure(text='Load the account for '+self.platform.get());self.write_review('Platform changed. Prepare a fresh draft.')
 def load_account(self):
  platform=self.platform.get();config=copy.deepcopy(self.config_data)
  def done(account):
   self.account=(platform,account,config);self.privacy.set('');self.privacy_box.configure(values=account['privacy']);self.account_note.configure(text=account['name']+' • '+str(account['id']));self.note.set('Account loaded. Choose visibility, prepare the draft and preview the exact video.')
  self.run(lambda:account_info(platform,config),done,'Reading account information…')
 def prepare(self):
  if not self.account or self.account[0]!=self.platform.get():self.note.set('Load the connected account first.');return
  platform,account,config=copy.deepcopy(self.account)
  if platform=='YouTube' and not self.kids.get():self.note.set('Choose whether this YouTube video is made for kids.');return
  path=self.video_path.get();title=self.title_var.get();description=self.description.get('1.0','end').strip();privacy=self.privacy.get();kids=self.kids.get()=='Made for kids';flags={key:var.get() for key,var in self.flags.items()}
  for key in ('comment','duet','stitch'):
   if account.get('details',{}).get(key+'_disabled'):flags['disable_'+key]=True
  def work():
   video_file(path);duration=video_duration(path)
   if platform=='TikTok' and duration>account.get('details',{}).get('max_video_post_duration_sec',0):raise ValueError('Video exceeds this creator duration limit.')
   return self.store.create(path,platform,title,description,privacy,account,kids,flags)
  def done(result):
   identifier,payload=result;self.ready=(identifier,payload,config);self.previewed=None;self.write_review(self.summary(payload));self.note.set('Ready for review. Watch the prepared video before approving. Nothing has been uploaded.')
  self.run(work,done,'Preparing and hashing a separate review copy…')
 def summary(self,post):
  return 'Platform: '+post['platform']+'\nAccount: '+post['destination_name']+' ('+post['destination_id']+')\nVisibility: '+post['privacy']+'\nFile: '+post['original_name']+'\nTitle: '+post['title']+'\nDescription: '+post['description']+'\nMade for kids: '+str(post['kids'])+'\nDisclosures/interactions: '+json.dumps(post['flags'])+'\nSHA256: '+post['sha256']+'\n\nThis is the frozen review copy. Form changes require a new Prepare review.'
 def write_review(self,text):self.review.configure(state='normal');self.review.delete('1.0','end');self.review.insert('1.0',text);self.review.configure(state='disabled')
 def preview(self):
  path=self.ready[1]['path'] if self.ready else self.video_path.get()
  if not Path(path).is_file():self.note.set('Choose or prepare a video first.');return
  os.startfile(str(Path(path).resolve()))
  if self.ready:self.previewed=self.ready[0]
 def approve(self):
  if not self.ready:self.note.set('Prepare and preview the draft first.');return
  identifier,payload,config=self.ready
  if self.previewed!=identifier:self.note.set('Open Preview prepared video and review it before approving.');return
  if not messagebox.askyesno('Approve exact video upload',self.summary(payload)+'\n\nI checked this video and approve uploading/publishing it to this exact account now?',parent=self):return
  def work():self.store.approve(identifier);return self.store.publish(identifier,config)
  def done(receipt):self.note.set(receipt['detail']+' • ID: '+receipt['id']);self.write_review(self.summary(payload)+'\n\nReceipt: '+json.dumps(receipt));self.ready=(identifier,payload,config)
  self.run(work,done,'Submitting approved draft. Do not create a duplicate upload…')
 def check_status(self):
  if not self.ready:self.note.set('Select a submitted draft first.');return
  identifier,post,config=self.ready;_,state,receipt=self.store.get(identifier)
  if not receipt or not receipt.get('id'):self.note.set('No server operation ID. Inspect the platform account before retrying.');return
  self.run(lambda:post_status(post['platform'],receipt['id'],config),lambda result:self.write_review('Server status:\n'+json.dumps(result,indent=2,ensure_ascii=False)),'Checking server processing status…')
 def show_recent(self):
  rows=self.store.recent();w=tk.Toplevel(self);w.title('Publishing receipts');w.geometry('780x460')
  listing=tk.Listbox(w,height=12);listing.pack(fill='both',expand=True,padx=12,pady=12)
  for identifier,payload,state,receipt in rows:listing.insert('end',payload['platform']+' • '+payload['title']+' • '+state+' • '+str(receipt.get('id','')))
  def select():
   if not listing.curselection():return
   identifier,payload,state,receipt=rows[listing.curselection()[0]];self.ready=(identifier,payload,copy.deepcopy(self.config_data));self.previewed=None;self.write_review(self.summary(payload)+'\n\nState: '+state+'\n'+json.dumps(receipt));w.destroy()
  button(w,'Load selected review / receipt',select).pack(fill='x',padx=12,pady=8);apply_theme(w,self.config_data.get('theme','Neon Rose'))
 def build_accounts(self):
  body=self.accounts_page
  label(body,'Credentials stay in your Windows DPAPI-encrypted settings. SARU does not collect your social passwords.',wraplength=830).pack(anchor='w',padx=14,pady=12)
  self.action(body,'Connect YouTube • choose Google Desktop OAuth client JSON',self.connect_google,True)
  label(body,'Enable YouTube Data API v3 in your Google project, create Desktop app OAuth credentials and add your account as a test user if applicable. You complete Google sign-in/consent yourself.',fg=MUTED,wraplength=830,justify='left').pack(anchor='w',padx=14,pady=12)
  def meta():
   from social_ui import account_settings
   account_settings(self,self.config_data,self.save_config)
  self.action(body,'Connect Facebook Page / WhatsApp Business',meta)
  self.tiktok,_=self.field(body,'TikTok access token • requires video.publish scope',self.config_data.get('keys',{}).get('TikTok',''),secret=True)
  def save_tiktok():
   old=copy.deepcopy(self.config_data)
   try:self.config_data.setdefault('keys',{})['TikTok']=self.tiktok.get().strip();self.save_config();self.note.set('TikTok token saved securely. Load its creator account before preparing a post.')
   except Exception:self.config_data.clear();self.config_data.update(old);self.note.set('Could not encrypt/save token; previous settings preserved.')
  self.action(body,'Save TikTok token securely',save_tiktok)
 def connect_google(self):
  path=filedialog.askopenfilename(parent=self,title='Choose Google Desktop OAuth client JSON',filetypes=[('JSON','*.json')])
  if not path:return
  def done(credentials):
   old=copy.deepcopy(self.config_data)
   try:self.config_data.setdefault('keys',{})['YouTube OAuth']=credentials;self.save_config();self.note.set('YouTube connected securely. Load the channel in Review & publish.')
   except Exception:self.config_data.clear();self.config_data.update(old);self.note.set('Could not encrypt/save Google authorization; previous settings preserved.')
  self.run(lambda:connect_youtube(path,self.cancel),done,'Complete Google sign-in/consent in your browser (3 minute timeout)…')
 def run(self,work,done,message):
  if self.busy:self.note.set('Wait for the current operation to finish.');return
  self.busy=True;self.note.set(message)
  for control in self.action_buttons:control.configure(state='disabled')
  events=self.events
  def worker():
   try:events.put((done,work(),None))
   except Exception as exc:events.put((done,None,safe_error(exc)))
  threading.Thread(target=worker,daemon=True).start()
 def pump(self):
  if self.closed:return
  try:
   while True:
    done,result,error=self.events.get_nowait();self.busy=False
    for control in self.action_buttons:control.configure(state='normal')
    if error:self.note.set(error)
    else:done(result)
    self.refresh_theme()
  except Empty:pass
  self.job=self.after(100,self.pump)
 def close(self):
  if self.busy and not messagebox.askyesno('Close studio','An operation is running. Closing cancels local rendering, but an upload already sent may still complete. Its receipt/state remains in recent submissions. Close?',parent=self):return
  self.closed=True;self.cancel.set()
  if self.job:self.after_cancel(self.job)
  self.destroy()
