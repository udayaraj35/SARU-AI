"""Local masked CRM setup; credentials live in SARU's DPAPI-protected key store."""
import copy,json,secrets,threading,tkinter as tk
from tkinter import messagebox
from queue import Queue,Empty
from wacrm_bridge import install_directory,install_local,local_crm,CRMClient,checked_origin

class CRMPanel(tk.Toplevel):
 def __init__(self,root,cfg,save,open_browser,consent):
  super().__init__(root);self.title('SARU • WhatsApp CRM');self.geometry('780x760');self.cfg=cfg;self.save_config=save;self.open_browser=open_browser;self.consent=consent;self.events=Queue();self.closed=False;self.job=None;self.fields={}
  tk.Label(self,text='WhatsApp CRM • WACRM 0.8.0',font=('Segoe UI',16,'bold')).pack(pady=8)
  tk.Label(self,text='Official Business API + Supabase required. Personal WhatsApp Web is separate.\nMessages/inbox data live in your configured Supabase database; connecting a cloud project sends data there.',wraplength=740,justify='left').pack(padx=12,pady=5)
  tk.Label(self,text='Local installation: '+str(install_directory(cfg)),wraplength=740).pack(pady=4)
  for key,title,secret in [('wacrm_api_url','CRM origin (local default http://127.0.0.1:3876)',False),('wacrm_supabase_url','Supabase project origin',False),('WACRM_ANON','Supabase anon key',True),('WACRM_SERVICE_ROLE','Supabase service-role key',True),('WACRM_META_SECRET','Meta App Secret',True),('WACRM_API','WACRM scoped API key (create in CRM Settings after login)',True)]:
   tk.Label(self,text=title+(' • Saved encrypted' if secret and cfg.get('keys',{}).get(key) else '')).pack(anchor='w',padx=12)
   var=tk.StringVar(value='' if secret else cfg.get(key,'http://127.0.0.1:3876' if key=='wacrm_api_url' else ''));self.fields[key]=var
   tk.Entry(self,textvariable=var,show='*' if secret else '').pack(fill='x',padx=12,pady=3)
  bar=tk.Frame(self);bar.pack(fill='x',padx=8,pady=6)
  for title,fn in [('Save setup',self.save),('Install / repair',self.install),('Start local CRM',self.start),('Open CRM',lambda:open_browser(checked_origin(cfg.get('wacrm_api_url','http://127.0.0.1:3876')))),('Stop local CRM',local_crm.stop)]:tk.Button(bar,text=title,command=fn).pack(side='left',padx=2)
  bar=tk.Frame(self);bar.pack(fill='x',padx=8)
  for title,path in [('Test API','me'),('Contacts','contacts'),('Inbox','conversations')]:tk.Button(bar,text=title,command=lambda p=path:self.worker(lambda:json.dumps(CRMClient(cfg).request('GET',p),ensure_ascii=False,indent=2))).pack(side='left',padx=3)
  self.output=tk.Text(self,height=8,wrap='word');self.output.pack(fill='both',expand=True,padx=12,pady=7)
  self.output.insert('end','Source/dependencies installed does not connect WhatsApp. Configure Supabase migrations/auth, then Meta Business number/token and public HTTPS webhook inside CRM. No message has been sent.\n')
  self.bind('<Destroy>',self.cleanup,add='+');self.pump()
 def save(self):
  old=copy.deepcopy(self.cfg)
  try:
   origin=checked_origin(self.fields['wacrm_api_url'].get().strip());supabase=self.fields['wacrm_supabase_url'].get().strip()
   if supabase:checked_origin(supabase)
   self.cfg.update(wacrm_api_url=origin,wacrm_supabase_url=supabase)
   for key,var in self.fields.items():
    if key.startswith('WACRM_') and var.get().strip():self.cfg.setdefault('keys',{})[key]=var.get().strip();var.set('')
   self.cfg.setdefault('keys',{}).setdefault('WACRM_ENCRYPTION',secrets.token_hex(32));self.save_config();self.events.put('Setup saved with Windows encryption. No account connection or message send was performed.')
  except Exception as exc:self.cfg.clear();self.cfg.update(old);messagebox.showerror('CRM setup',str(exc),parent=self)
 def install(self):self.worker(lambda:install_local(self.cfg,self.events.put))
 def start(self):self.worker(lambda:local_crm.start(self.cfg,self.events.put))
 def worker(self,fn):
  def work():
   try:result=fn()
   except Exception as exc:result=str(exc)
   for value in self.cfg.get('keys',{}).values():
    if value:result=result.replace(value,'[redacted]')
   self.events.put(result)
  threading.Thread(target=work,daemon=True).start()
 def pump(self):
  if self.closed:return
  try:
   for _ in range(40):self.output.insert('end',self.events.get_nowait()+'\n');self.output.see('end')
  except Empty:pass
  self.job=self.after(150,self.pump)
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True
   if self.job:self.after_cancel(self.job)
