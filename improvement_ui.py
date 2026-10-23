"""Owner-requested self-improvement: generate, inspect, approve, back up and roll back."""
import copy,json,threading
from queue import Queue,Empty
import tkinter as tk
from tkinter import messagebox
from neon_ui import BG,TEXT,PANEL,MUTED,CYAN,label,button
from theme_manager import apply_theme
from appearance_controls import apply_text_scale
from improvement_core import ImprovementManager
from improvement_ai import generate

class ImprovementStudio(tk.Toplevel):
 def __init__(self,parent,config,root,data,request='',authorize=None,consent=None):
  super().__init__(parent);self.title('SARU • Improve My Code & Design');self.geometry('1000x780');self.minsize(820,650);self.configure(bg=BG)
  self.consent=consent
  self.authorize=authorize
  self.config_data=config;self.manager=ImprovementManager(root,data);self.events=Queue();self.busy=False;self.ready=None;self.closed=False;self.job=None;self.protocol('WM_DELETE_WINDOW',self.close)
  label(self,'IMPROVE SARU  •  Request → Source diff → Approve → Restart',font=('Segoe UI',17,'bold'),fg=CYAN).pack(anchor='w',padx=14,pady=12)
  label(self,'Selected source is sent only after confirmation. Candidate code is syntax-checked, not run or functionally tested. Your settings/keys/memory are excluded.',fg=MUTED,wraplength=940,justify='left').pack(fill='x',padx=14,pady=5)
  self.request=tk.Text(self,height=4,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word');self.request.pack(fill='x',padx=14,pady=6);self.request.insert('1.0',request)
  select=tk.Frame(self,bg=BG);select.pack(fill='x',padx=14)
  label(select,'Source files (choose 1–8)',fg=MUTED).pack(side='left',padx=4)
  self.files=tk.Listbox(select,selectmode='extended',exportselection=False,height=5,bg=PANEL,fg=TEXT);self.files.pack(side='left',fill='x',expand=True,padx=8)
  for i,name in enumerate(self.manager.available()):
   self.files.insert('end',name)
   if name in ('dashboard_layout.py','dashboard_ui.py','settings_ui.py'):self.files.selection_set(i)
  toolbar=tk.Frame(self,bg=BG);toolbar.pack(fill='x',padx=14,pady=8)
  self.generate_button=button(toolbar,'Generate improvement proposal',self.propose,True);self.generate_button.pack(side='left',padx=3)
  self.apply_button=button(toolbar,'Approve and apply reviewed diff',self.apply);self.apply_button.pack(side='left',padx=3)
  self.rollback_button=button(toolbar,'Roll back loaded change',self.rollback);self.rollback_button.pack(side='left',padx=3)
  button(toolbar,'Recent proposals',self.recent).pack(side='left',padx=3)
  self.note=tk.StringVar(value='No code has been changed.');label(self,'',textvariable=self.note,wraplength=940,justify='left',fg=CYAN).pack(fill='x',padx=14,pady=5)
  area=tk.Frame(self,bg=BG);area.pack(fill='both',expand=True,padx=14,pady=8)
  self.diff=tk.Text(area,bg=PANEL,fg=TEXT,font=('Consolas',10),wrap='none',state='disabled');self.diff.grid(row=0,column=0,sticky='nsew')
  vertical=tk.Scrollbar(area,command=self.diff.yview);vertical.grid(row=0,column=1,sticky='ns');horizontal=tk.Scrollbar(area,orient='horizontal',command=self.diff.xview);horizontal.grid(row=1,column=0,sticky='ew')
  self.diff.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set);area.rowconfigure(0,weight=1);area.columnconfigure(0,weight=1)
  self.apply_button.configure(state='disabled');self.rollback_button.configure(state='disabled')
  apply_theme(self,config.get('theme','Neon Rose'));apply_text_scale(self,config.get('ui_text_scale',100));self.pump()
 def show(self,identifier):
  proposal,state=self.manager.load(identifier);self.ready=(identifier,state['digest'])
  self.diff.configure(state='normal');self.diff.delete('1.0','end');self.diff.insert('1.0',proposal['summary']+'\n\n'+proposal['diff']);self.diff.configure(state='disabled')
  self.note.set('State: '+state['state']+' • Syntax validation only; functional behavior is not verified.')
  self.apply_button.configure(state='normal' if state['state']=='ready' and not self.busy else 'disabled');self.rollback_button.configure(state='normal' if state['state']=='applied' and not self.busy else 'disabled')
 def reviewed(self,title,description,callback,approved):
  if approved:return True
  if not self.consent:return messagebox.askyesno(title,description,parent=self)
  fingerprint=(self.request.get('1.0','end'),tuple(self.files.curselection()),self.ready)
  def execute():
   if self.closed or self.busy:raise ValueError('Improvement studio closed or busy. Request a fresh review.')
   current=(self.request.get('1.0','end'),tuple(self.files.curselection()),self.ready)
   if current!=fingerprint:raise ValueError('Improvement proposal changed. Request a fresh review.')
   callback(True)
  self.consent(title+'\n'+description,execute,seconds=90)
  return False
 def propose(self,approved=False):
  if self.busy:return
  names=[self.files.get(index) for index in self.files.curselection()];request=self.request.get('1.0','end').strip()
  try:files=self.manager.snapshot(names)
  except Exception as exc:self.note.set(str(exc));return
  if not request:self.note.set('Describe the change you want first.');return
  config=copy.deepcopy(self.config_data)
  if not self.reviewed('Send selected SARU source','Send these source files and your request to '+config.get('provider','Gemini')+' / '+config.get('model','')+'?\n\n'+', '.join(names)+'\n\nNo settings, API keys, memory or personal files are included. Review and approval will still be required before changing code.',self.propose,approved):return
  self.ready=None;self.apply_button.configure(state='disabled');self.rollback_button.configure(state='disabled')
  self.run(lambda:self.manager.stage(generate(config,request,files),files,request),lambda result:self.show(result[0]),'Generating exact edits and checking syntax…')
 def apply(self,approved=False):
  if self.busy or not self.ready:return
  if self.authorize is None or not self.authorize():
   self.note.set('Owner edit verification required. No code changed.');return
  identifier,digest=self.ready;proposal,state=self.manager.load(identifier)
  if not self.reviewed('Apply this reviewed source diff','Apply the exact displayed changes to:\n'+', '.join(change['path'] for change in proposal['changes'])+'\n\n'+proposal['summary']+'\n\nBackups will be saved first. Syntax checks are not functional tests. Restart SARU after applying; rollback is available if these files have not changed again.',self.apply,approved):return
  self.run(lambda:self.manager.apply(identifier,digest),lambda files:(self.show(identifier),self.note.set('Applied with backups: '+', '.join(files)+'. Restart SARU to load the changes. Functional testing is still required.')),'Backing up and applying the approved diff…')
 def rollback(self,approved=False):
  if self.busy or not self.ready:return
  if self.authorize is None or not self.authorize():
   self.note.set('Owner edit verification required. No rollback performed.');return
  identifier,_=self.ready
  if not self.reviewed('Roll back own-code change','Restore the backed-up files for this proposal? Rollback is rejected if someone edited these files again. Restart SARU afterwards.',self.rollback,approved):return
  self.run(lambda:self.manager.rollback(identifier),lambda result:(self.show(identifier),self.note.set('Original files restored. Restart SARU.')),'Restoring this proposal backup…')
 def recent(self):
  if self.busy:return
  rows=self.manager.recent();w=tk.Toplevel(self);w.title('SARU self-improvement proposals');w.geometry('760x420')
  listing=tk.Listbox(w);listing.pack(fill='both',expand=True,padx=12,pady=12)
  for identifier,summary,state in rows:listing.insert('end',state+' • '+summary[:110])
  def load():
   if listing.curselection():self.show(rows[listing.curselection()[0]][0]);w.destroy()
  button(w,'Load review / rollback',load).pack(fill='x',padx=12,pady=8);apply_theme(w,self.config_data.get('theme','Neon Rose'))
 def run(self,work,done,note):
  self.busy=True;self.note.set(note);self.generate_button.configure(state='disabled');self.apply_button.configure(state='disabled');self.rollback_button.configure(state='disabled');events=self.events
  def worker():
   try:events.put((done,work(),None))
   except Exception as exc:
    import requests
    error='Provider network request failed. No candidate code was executed.' if isinstance(exc,requests.RequestException) else str(exc)
    events.put((done,None,error))
  threading.Thread(target=worker,daemon=True).start()
 def pump(self):
  if self.closed:return
  try:
   while True:
    done,result,error=self.events.get_nowait();self.busy=False;self.generate_button.configure(state='normal')
    if error:self.note.set(error)
    else:done(result)
  except Empty:pass
  self.job=self.after(100,self.pump)
 def close(self):
  if self.busy and not messagebox.askyesno('Close improvement studio','An operation is still running. A code apply/rollback already started may finish. Close this window?',parent=self):return
  self.closed=True
  if self.job:self.after_cancel(self.job)
  self.destroy()
