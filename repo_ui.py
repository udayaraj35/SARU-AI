"""Reviewable repository imports, prompt selection and optional video backend."""
import json
from pathlib import Path
from queue import Queue,Empty
import threading
import tkinter as tk
from tkinter import ttk,messagebox
import os
import webbrowser
from repo_library import RepoLibrary
from moneyprinter_bridge import MoneyPrinter,install as install_engine
from neon_ui import BG,PANEL,TEXT,CYAN,MUTED,label,button,entry
from theme_manager import apply_theme
from appearance_controls import apply_text_scale

class RepoCenter(tk.Toplevel):
 def __init__(self,parent,config,save,data,url=''):
  super().__init__(parent);self.title('SARU • Repository Skills & Video Engine');self.geometry('1050x820');self.minsize(850,650);self.configure(bg=BG)
  self.cfg=config;self.save_config=save;self.library=RepoLibrary(data);self.data=data;self.engine=MoneyPrinter(data);self.events=Queue();self.closed=False;self.busy=False;self.staged=None;self.rows=[];self.job=None;self.protocol('WM_DELETE_WINDOW',self.close)
  self.note=tk.StringVar(value='Repository references do not grant tools, permissions or automatic code execution.')
  label(self,'REPOSITORIES • PROMPTS • VIDEO ENGINE',font=('Segoe UI',18,'bold'),fg=CYAN).pack(anchor='w',padx=14,pady=12)
  label(self,'',textvariable=self.note,wraplength=990,fg=MUTED).pack(fill='x',padx=14,pady=5)
  book=ttk.Notebook(self);book.pack(fill='both',expand=True,padx=12,pady=12)
  library=tk.Frame(book,bg=BG);repo=tk.Frame(book,bg=BG);video=tk.Frame(book,bg=BG)
  book.add(library,text='Search installed prompts / skills');book.add(repo,text='Add / update GitHub repo');book.add(video,text='MoneyPrinterTurbo')
  self.search=tk.StringVar();entry(library,self.search).pack(fill='x',padx=8,pady=8,ipady=6);self.search.trace_add('write',lambda *args:self.refresh())
  split=tk.PanedWindow(library,orient='horizontal',bg=BG);split.pack(fill='both',expand=True)
  self.listing=tk.Listbox(split,bg=PANEL,fg=TEXT,width=35,selectbackground='#284c70',selectforeground=TEXT);split.add(self.listing)
  self.preview=tk.Text(split,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word',state='disabled');split.add(self.preview)
  self.listing.bind('<<ListboxSelect>>',lambda event:self.preview_card())
  bar=tk.Frame(library,bg=BG);bar.pack(fill='x')
  button(bar,'Use selected reference',self.activate,True).pack(side='left',padx=4,pady=8);button(bar,'Clear selected reference',self.clear).pack(side='left',padx=4)
  self.url=tk.StringVar(value=url or 'https://github.com/f/prompts.chat');entry(repo,self.url).pack(fill='x',padx=10,pady=10,ipady=8)
  toolbar=tk.Frame(repo,bg=BG);toolbar.pack(fill='x',padx=6)
  button(toolbar,'Fetch pinned preview',self.fetch,True).pack(side='left',padx=4);button(toolbar,'Install reviewed text',self.approve).pack(side='left',padx=4)
  for name in ('f/prompts.chat','harry0703/MoneyPrinterTurbo'):button(repo,name,lambda n=name:self.url.set('https://github.com/'+n)).pack(anchor='w',padx=10,pady=5)
  self.review=tk.Text(repo,bg=PANEL,fg=TEXT,wrap='word');self.review.pack(fill='both',expand=True,padx=10,pady=10)
  label(video,'Separate video engine: topic → script → footage → narration → subtitles. Configure providers in its own config.toml. Publishing remains a separate approval.',wraplength=960).pack(fill='x',padx=12,pady=10)
  enginebar=tk.Frame(video,bg=BG);enginebar.pack(fill='x')
  for title,command in [('Install / repair engine',self.setup_engine),('Start engine',self.start_engine),('Edit engine config',self.edit_engine),('Stop engine',self.engine.stop)]:button(enginebar,title,command).pack(side='left',padx=4,pady=5)
  helpbar=tk.Frame(video,bg=BG);helpbar.pack(fill='x')
  button(helpbar,'Microsoft runtime help',lambda:webbrowser.open('https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170')).pack(anchor='w',padx=12,pady=3)
  self.subject=tk.StringVar();label(video,'Video topic',fg=CYAN).pack(anchor='w',padx=12);entry(video,self.subject).pack(fill='x',padx=12,pady=5,ipady=5)
  label(video,'Optional script (blank: backend writes it using its configured LLM)',fg=MUTED).pack(anchor='w',padx=12)
  self.script=tk.Text(video,height=5,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word');self.script.pack(fill='x',padx=12,pady=5)
  self.voice=tk.StringVar(value='en-US-AriaNeural-Female');entry(video,self.voice).pack(fill='x',padx=12,pady=5)
  button(video,'Review / generate video',self.generate,True).pack(anchor='w',padx=12,pady=5)
  self.task=tk.StringVar();entry(video,self.task).pack(fill='x',padx=12,pady=5)
  button(video,'Check task status',lambda:self.run(lambda:self.engine.task(self.task.get()),self.show_result)).pack(anchor='w',padx=12)
  self.result=tk.Text(video,height=8,bg=PANEL,fg=TEXT,wrap='word');self.result.pack(fill='both',expand=True,padx=12,pady=8)
  self.refresh();apply_theme(self,config.get('theme','Neon Rose'));apply_text_scale(self,config.get('ui_text_scale',100));self.pump()
  if url:book.select(repo);self.after(200,lambda:None if self.closed else self.fetch())
 def refresh(self):
  self.rows=self.library.search(self.search.get());self.listing.delete(0,'end')
  for _,repo,title,kind in self.rows:self.listing.insert('end',title+' · '+kind)
 def selected(self):
  selection=self.listing.curselection()
  if not selection:raise ValueError('Choose a prompt or reference first.')
  return self.rows[selection[0]][0]
 def preview_card(self):
  try:
   row=self.library.card(self.selected());self.preview.configure(state='normal');self.preview.delete('1.0','end');self.preview.insert('1.0',row[0]+'\nSource: '+row[2]+'\nType: '+row[3]+'\n\n'+row[1]);self.preview.configure(state='disabled')
  except ValueError:pass
 def activate(self):
  try:
   identifier=self.selected();row=self.library.card(identifier)
   if messagebox.askyesno('Use reviewed reference','Use this reviewed text as context for future AI requests? It does not add executable tools.\n\n'+row[0]+'\nSource: '+row[2],parent=self):self.cfg['selected_repo_card']=identifier;self.save_config();self.note.set('Selected: '+row[0]+'. Reconnect Live Voice to use it there.')
  except Exception as exc:self.note.set(str(exc))
 def clear(self):self.cfg.pop('selected_repo_card',None);self.save_config();self.note.set('Reference cleared. Reconnect Live Voice to refresh its context.')
 def fetch(self):
  url=self.url.get();self.staged=None
  def done(folder):
   self.staged=folder;manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'));self.review.delete('1.0','end');self.review.insert('end',json.dumps(manifest,indent=2)+'\n\n')
   for item in manifest['files']:
    if item['path'].startswith(('README','LICENSE')):self.review.insert('end','\n'+item['path']+'\n'+(folder/item['file']).read_text(encoding='utf8',errors='replace')[:18000]+'\n')
   self.note.set('Pinned content downloaded. Review source, license and text before installation.')
  self.run(lambda:self.library.stage(url),done)
 def approve(self):
  if self.staged is None:self.note.set('Fetch and review a repository first.');return
  manifest=json.loads((self.staged/'manifest.json').read_text(encoding='utf8'))
  if messagebox.askyesno('Install repository references','Import the displayed text/prompts from '+manifest['repo']+' at '+manifest['sha']+'?\n\nScripts, installers and remote tools will not be executed. Compatible engines need their separate adapter.',parent=self):
   self.run(lambda:self.library.install(self.staged),lambda count:(self.refresh(),self.note.set(str(count)+' prompt/reference entries installed.')))
 def setup_engine(self):
  if messagebox.askyesno('Install MoneyPrinterTurbo engine','Download the pinned MoneyPrinterTurbo source and install its Python requirements in a separate environment? This downloads third-party executable dependencies and may use substantial disk space. It is not a security sandbox. SARU voice dependencies remain separate.',parent=self):self.run(lambda:install_engine(self.data,lambda text:self.events.put(('status',text))),lambda result:self.note.set('Engine installed. Edit its provider config, then Start engine.'))
 def start_engine(self):
  def start():self.engine.start();return self.engine.wait_ready()
  self.run(start,lambda result:self.note.set('Backend API is ready. Configure providers before generating.'))
 def edit_engine(self):
  try:
   import subprocess
   path=Path(self.engine.info()['root'])/'config.toml';subprocess.Popen(['notepad.exe',str(path)])
  except Exception as exc:self.note.set('Open the backend config with a text editor: '+str(exc))
 def generate(self):
  subject=self.subject.get();script=self.script.get('1.0','end').strip();voice=self.voice.get()
  if messagebox.askyesno('Review video generation','Generate one portrait video with MoneyPrinterTurbo? It can contact its configured LLM, footage and voice providers, which may charge usage.\n\nTopic: '+subject+'\nVoice: '+voice+'\n\nNo social-media publication is requested.',parent=self):self.run(lambda:self.engine.create(subject,script,voice),self.show_result)
 def show_result(self,result):
  self.result.delete('1.0','end');self.result.insert('end',json.dumps(result,ensure_ascii=False,indent=2))
  identifier=result.get('data',{}).get('task_id') if isinstance(result,dict) else None
  if identifier:self.task.set(identifier)
 def run(self,operation,done):
  if self.busy:self.note.set('Wait for the current operation.');return
  self.busy=True;self.note.set('Working…')
  def work():
   try:self.events.put(('done',done,operation()))
   except Exception as exc:self.events.put(('error',str(exc)))
  threading.Thread(target=work,daemon=True).start()
 def pump(self):
  if self.closed:return
  try:
   while True:
    event=self.events.get_nowait()
    if event[0]=='status':self.note.set(event[1])
    elif event[0]=='error':self.busy=False;self.note.set(event[1])
    else:self.busy=False;self.note.set('Operation completed.');event[1](event[2])
  except Empty:pass
  self.job=self.after(100,self.pump)
 def close(self):
  if self.busy:self.note.set('Wait for the current operation to finish before closing.');return
  self.engine.stop();self.closed=True
  if self.job:self.after_cancel(self.job)
  self.destroy()
