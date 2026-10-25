"""SARU first-run/upgrade wizard. Optional API setup can be skipped safely."""
import os
from pathlib import Path
from queue import Queue,Empty
import subprocess
import threading
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from install_support import installed_location,validate_target
from installer_backend import install_application,runtime_environment
from version import VERSION

BG='#080e1d';PANEL='#101b30';FG='#eef3ff';ACCENT='#ff286e'

class SetupWizard:
 def __init__(self,root,source=None,backend=install_application):
  self.root=root;self.source=Path(source or Path(__file__).resolve().parent);self.backend=backend
  self.page=0;self.busy=False;self.success=False;self.events=Queue();self.poll_id=None
  self.previous=installed_location()
  default=Path(os.getenv('LOCALAPPDATA',Path.home()))/'Programs'/'SARU AI'
  if self.previous is None and (default/'app.py').is_file():self.previous=default
  self.mode='Update' if self.previous else 'Install'
  self.destination=tk.StringVar(value=str(self.previous or Path(os.getenv('LOCALAPPDATA',Path.home()))/'Programs'/'SARU AI'))
  self.desktop=tk.BooleanVar(value=True);self.startmenu=tk.BooleanVar(value=True);self.startup=tk.BooleanVar(value=False);self.auto_voice=tk.BooleanVar(value=True)
  self.voice_profiles=tk.BooleanVar(value=True)
  if self.previous:
   try:
    from settings_store import SettingsStore
    previous_cfg=SettingsStore(Path(os.getenv('APPDATA',Path.home()))/'SARU_AI'/'settings.json',{'keys':{}}).load()
    self.auto_voice.set(bool(previous_cfg.get('auto_listen',True)))
   except Exception:pass
  self.initial_auto_voice=self.auto_voice.get()
  self.provider=tk.StringVar(value='Gemini');self.api_key=tk.StringVar();self.model=tk.StringVar();self.custom_url=tk.StringVar(value='https://api.openai.com/v1');self.launch=tk.BooleanVar(value=True)
  root.title(f'SARU AI {VERSION} — Setup');root.geometry('760x650');root.minsize(700,600);root.configure(bg=BG)
  root.protocol('WM_DELETE_WINDOW',self.close)
  tk.Label(root,text=f'SARU AI  /  {VERSION}',font=('Segoe UI',25,'bold'),bg=BG,fg=ACCENT).pack(anchor='w',padx=28,pady=(22,8))
  self.step=tk.Label(root,bg=BG,fg='#86dfff',font=('Segoe UI',11));self.step.pack(anchor='w',padx=28,pady=(0,15))
  self.body=tk.Frame(root,bg=PANEL);self.body.pack(fill='both',expand=True,padx=25,pady=5)
  self.footer=tk.Frame(root,bg=BG);self.footer.pack(fill='x',padx=25,pady=18)
  self.cancel=tk.Button(self.footer,text='Cancel',command=self.close,padx=16,pady=9);self.cancel.pack(side='left')
  self.next_button=tk.Button(self.footer,text='Next →',command=self.next,bg=ACCENT,fg='white',padx=22,pady=9);self.next_button.pack(side='right')
  self.skip_button=tk.Button(self.footer,text='Skip API setup',command=self.skip,padx=16,pady=9)
  self.back_button=tk.Button(self.footer,text='← Back',command=self.back,padx=16,pady=9);self.back_button.pack(side='right',padx=10)
  self.show()
 def text(self,value,big=False):
  tk.Label(self.body,text=value,bg=PANEL,fg=FG,font=('Segoe UI',16,'bold') if big else ('Segoe UI',11),wraplength=650,justify='left').pack(anchor='w',padx=22,pady=10)
 def field(self,title,var,secret=False):
  self.text(title);e=tk.Entry(self.body,textvariable=var,show='*' if secret else '',font=('Segoe UI',11),bg='#071021',fg=FG,insertbackground='white');e.pack(fill='x',padx=22,ipady=7);return e
 def check(self,title,var):tk.Checkbutton(self.body,text=title,variable=var,bg=PANEL,fg=FG,selectcolor=BG,activebackground=PANEL,activeforeground=FG).pack(anchor='w',padx=22,pady=7)
 def show(self):
  for child in self.body.winfo_children():child.destroy()
  self.skip_button.pack_forget()
  self.back_button.configure(state='normal' if self.page in (1,2,3) else 'disabled')
  self.next_button.configure(state='normal',command=self.next,text=self.mode if self.page==3 else 'Finish' if self.page==5 else 'Next →')
  titles=['Welcome','Location & shortcuts','Optional API key','Review','Installing','Complete']
  self.step.configure(text=f'Step {min(self.page+1,5)} of 5  •  {titles[self.page]}')
  if self.page==0:
   self.text(('Update existing SARU AI' if self.previous else 'Install SARU AI on this PC'),True)
   self.text('Install or update your personal Windows assistant. Existing settings, memory and portraits are preserved. Close the old SARU window and floating assistant before continuing.')
   self.text('Requirements: 64-bit Windows 10/11 and Internet access for dependencies. '+('Python runtime is included in this installer. ' if os.getenv('SARU_BUNDLED_PYTHON_ZIP') else 'Source setup requires Python 3.11+. ')+'API setup is optional; configure keys later in Settings.')
   if self.previous:self.text('Existing installation found:\n'+str(self.previous))
  elif self.page==1:
   self.text('Choose installation folder',True);self.field('Application folder',self.destination)
   tk.Button(self.body,text='Browse…',command=lambda:self.destination.set(filedialog.askdirectory(parent=self.root) or self.destination.get())).pack(anchor='e',padx=22,pady=8)
   self.check('Create Desktop shortcut',self.desktop);self.check('Create Start Menu shortcut',self.startmenu);self.check('Start SARU when I sign in to Windows',self.startup);self.check('Automatically listen when SARU opens (audio to Gemini)',self.auto_voice);self.check('Install local voice-profile comparison model (larger download)',self.voice_profiles)
  elif self.page==2:
   self.text('Connect AI now or later',True)
   self.text('Your key is optional and encrypted for your Windows account. It is not tested or sent to the provider during setup. Skip keeps all existing provider settings unchanged.')
   ttk.Combobox(self.body,textvariable=self.provider,values=['Gemini','OpenAI','Anthropic','DeepSeek','Groq','OpenRouter','Custom'],state='readonly').pack(fill='x',padx=22,pady=5)
   self.field('API key',self.api_key,True);self.field('Model identifier (blank = choose in Settings before AI chat)',self.model)
   self.field('Custom base URL (used only for Custom provider)',self.custom_url)
   self.skip_button.pack(side='right',padx=8)
  elif self.page==3:
   self.text('Ready to '+self.mode.lower()+' SARU AI',True);self.text('Location: '+self.destination.get())
   self.text('API: '+(self.provider.get()+' key will be encrypted locally' if self.api_key.get().strip() else 'Skipped — configure later in Settings → AI & API'))
   self.text('SARU will appear in Control Panel / Installed apps with uninstall and size information. Replaced application files are backed up. Personal AppData is kept.')
  elif self.page==4:
   self.text('Installing SARU…',True);self.progress=ttk.Progressbar(self.body,mode='indeterminate');self.progress.pack(fill='x',padx=22,pady=10);self.progress.start(12)
   self.log=tk.Text(self.body,bg='#070d19',fg=FG,height=12,wrap='word');self.log.pack(fill='both',expand=True,padx=22,pady=10)
   self.next_button.configure(state='disabled');self.back_button.configure(state='disabled');self.cancel.configure(state='disabled')
  else:
   self.text('SARU AI '+('updated' if self.mode=='Update' else 'installed'),True);self.text('Version '+VERSION+'\n'+self.destination.get())
   self.text('You can add/change your API key later in Settings → AI & API. Uninstall is available from Windows Installed apps / Control Panel.')
   for warning in getattr(self,'warnings',[]):self.text(warning)
   self.check('Launch SARU after Finish',self.launch);self.cancel.configure(state='disabled')
 def next(self):
  if self.page==1:
   try:
    target=validate_target(Path(self.destination.get()).expanduser(),self.source)
    if self.previous and target!=self.previous:raise ValueError('Update the existing registered location: '+str(self.previous))
    self.destination.set(str(target))
    self.mode='Update' if (target/'app.py').is_file() else 'Install'
   except ValueError as exc:messagebox.showerror('Installation folder',str(exc),parent=self.root);return
  if self.page==2 and self.api_key.get().strip() and self.provider.get()=='Custom' and not self.custom_url.get().startswith(('https://','http://localhost','http://127.0.0.1')):
   messagebox.showerror('Custom endpoint','Use HTTPS or a local compatible endpoint.',parent=self.root);return
  if self.page==3:self.start_install();return
  if self.page==5:
   if self.launch.get():subprocess.Popen([str(Path(self.destination.get())/'.venv'/'Scripts'/'pythonw.exe'),str(Path(self.destination.get())/'launch_saru.py')],cwd=self.destination.get(),env=runtime_environment())
   self.root.destroy();return
  self.page+=1;self.show()
 def back(self):
  if not self.busy and self.page in (1,2,3,4):self.page-=1;self.show()
 def skip(self):
  if self.page==2:self.api_key.set('');self.page=3;self.show()
 def start_install(self):
  self.busy=True;self.page=4;self.show()
  target=Path(self.destination.get());options={'desktop':self.desktop.get(),'startmenu':self.startmenu.get(),'startup':self.startup.get(),'auto_listen':self.auto_voice.get(),'voice_profiles':self.voice_profiles.get()}
  if self.previous and self.auto_voice.get()==self.initial_auto_voice:options.pop('auto_listen',None)
  api={'provider':self.provider.get(),'key':self.api_key.get().strip(),'model':self.model.get().strip(),'custom_url':self.custom_url.get() if self.provider.get()=='Custom' else ''}
  def work():
   try:self.events.put(('done',self.backend(self.source,target,options,api,lambda line:self.events.put(('log',line)))))
   except Exception as exc:self.events.put(('error',str(exc)))
   finally:api.clear()
  threading.Thread(target=work,daemon=True).start();self.poll()
 def poll(self):
  try:
   while True:
    kind,value=self.events.get_nowait()
    if kind=='log':self.log.insert('end',value+'\n');self.log.see('end')
    elif kind=='done':
     self.busy=False;self.success=True;self.warnings=value or [];self.api_key.set('');self.progress.stop();self.page=5;self.show();return
    else:
     self.busy=False;self.progress.stop();self.cancel.configure(state='normal');self.back_button.configure(state='normal');self.next_button.configure(state='normal',text='Retry',command=self.start_install);self.log.insert('end','Installation failed: '+value+'\n');return
  except Empty:pass
  self.poll_id=self.root.after(100,self.poll)
 def close(self):
  if self.busy:return
  self.api_key.set('');self.root.destroy()

if __name__=='__main__':
 root=tk.Tk();SetupWizard(root);root.mainloop()
