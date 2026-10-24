"""SARU entry point for the attributed Advanced workspace and plugin review."""
import ast,hashlib,json,os,subprocess,threading,venv
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from neon_ui import BG,PANEL,TEXT,MUTED,CYAN,label,button
from advanced_workspace import advanced_python,bundle_manifest

class AdvancedPanel(tk.Frame):
 def __init__(self,root,manager,back):
  super().__init__(root,bg=BG);self.place(relwidth=1,relheight=1);self.manager=manager
  head=tk.Frame(self,bg=PANEL);head.pack(fill='x');button(head,'← Dashboard',back).pack(side='left',padx=16,pady=12);label(head,'SARU / ADVANCED WORKSPACE',fg=CYAN,font=('Segoe UI',20,'bold')).pack(side='left',padx=16)
  label(self,'Mark LVI integration • FatihMakes • CC BY-NC 4.0 (personal/non-commercial).\nYour main SARU interface stays intact. Advanced runs separately and pauses the main microphone. Hold Ctrl+Space to talk; closing it resumes the prior main voice.',fg=MUTED,wraplength=1100,justify='left').pack(anchor='w',padx=24,pady=14)
  actions=tk.Frame(self,bg=BG);actions.pack(fill='x',padx=24)
  for text,fn in [('Open workspace',self.start),('Close workspace',self.stop),('Check status',self.refresh),('Install dependencies',self.install),('Install browsers',self.install_browsers),('Review plugin…',self.review_plugin)]:button(actions,text,fn).pack(side='left',padx=4)
  self.status=label(self,'',fg=CYAN,wraplength=1100,justify='left');self.status.pack(anchor='w',padx=24,pady=12)
  box=tk.Frame(self,bg=BG);box.pack(fill='both',expand=True,padx=24,pady=12)
  self.details=tk.Text(box,bg=PANEL,fg=TEXT,font=('Segoe UI',11),wrap='word');self.details.pack(side='left',fill='both',expand=True);scroll=tk.Scrollbar(box,command=self.details.yview);scroll.pack(side='right',fill='y');self.details.configure(yscrollcommand=scroll.set)
  self.refresh()
 def refresh(self):
  try:
   manifest=bundle_manifest(self.manager.root);python=advanced_python(self.manager.root)
   self.status.configure(text='Running' if self.manager.active else 'Ready to open' if python else 'Separate dependencies need installation')
   text='AVAILABLE SOURCE COMPONENTS\n3D holographic face, audio/transcript lip-sync, facial expressions, text + live voice, echo guard, Ctrl+Space push-to-talk, local wake engine (optional upstream Hey Jarvis model), device picker, reconnect context, model ladder, local/hosted provider pipeline, Whisper/Piper/ElevenLabs options, undo and confirmations, topic monitoring, news/briefing, hardware telemetry, HUD video, phone QR pairing, runtime ability descriptions, and reviewed plugin discovery.\n\nBUNDLED ACTIONS\n'
   text+='\n'.join('• '+tool['name']+' — '+tool.get('description','')[:160] for tool in manifest['bundled_tools'])
   text+='\n\nSETUP / LIMITS\nLocal speech models must be selected/downloaded from Engine & Providers. ElevenLabs and external services need your own keys. The phone listener remains off until Remote Control is clicked; HTTPS is required and no firewall changes are made. A phone browser must trust your locally generated certificate before it can connect. Playwright browsers are separate downloads. Messages, screen/camera sharing, file changes, code execution and visual input have exact request review. Own SARU code changes still use Improve SARU.\n\nREADME PLUGIN PATHS NOT PROVIDED\n'
   text+='\n'.join('• '+name+(' (same named action is bundled)' if (self.manager.root/'mark_suite/actions'/name).exists() else ' (not in supplied source; not claimed installed)') for name in manifest['advertised_plugin_files_missing'])
   self.details.configure(state='normal');self.details.delete('1.0','end');self.details.insert('end',text);self.details.configure(state='disabled')
  except Exception as exc:self.status.configure(text='Advanced source validation failed: '+str(exc))
 def start(self):
  try:self.status.configure(text=self.manager.start())
  except Exception as exc:self.status.configure(text=str(exc))
 def stop(self):self.status.configure(text=self.manager.stop())
 def install(self):
  self.status.configure(text='Installing only Advanced workspace dependencies in its own environment…')
  def work():
   target=self.manager.root/'.advanced-env';log=self.manager.data/'advanced/dependency-install.log';log.parent.mkdir(parents=True,exist_ok=True)
   try:
    if not (target/'Scripts/python.exe').exists():venv.EnvBuilder(with_pip=True).create(target)
    with log.open('w',encoding='utf8') as output:
     result=subprocess.run([str(target/'Scripts/python.exe'),'-m','pip','install','-r',str(self.manager.root/'mark_suite/requirements.txt')],stdout=output,stderr=subprocess.STDOUT,timeout=1200,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    message='Advanced dependencies installed.' if result.returncode==0 else 'Dependency install failed; private log: '+str(log)
   except Exception as exc:message='Dependency install failed: '+str(exc)
   self.manager.tkroot.after(0,lambda:self.status.configure(text=message) if self.winfo_exists() else None)
  threading.Thread(target=work,daemon=True).start()
 def install_browsers(self):
  python=advanced_python(self.manager.root)
  if not python:self.status.configure(text='Install Advanced dependencies first.');return
  self.status.configure(text='Downloading Chromium and Firefox for Advanced browser tools…')
  def work():
   env=os.environ.copy();env['PLAYWRIGHT_BROWSERS_PATH']=str(self.manager.data/'advanced/browsers')
   log=self.manager.data/'advanced/browser-install.log';log.parent.mkdir(parents=True,exist_ok=True)
   try:
    with log.open('w',encoding='utf8') as output:result=subprocess.run([str(python),'-m','playwright','install','chromium','firefox'],env=env,stdout=output,stderr=subprocess.STDOUT,timeout=1200,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    message='Advanced browser engines installed.' if result.returncode==0 else 'Browser download failed; private log: '+str(log)
   except Exception as exc:message='Browser install failed: '+str(exc)
   self.manager.tkroot.after(0,lambda:self.status.configure(text=message) if self.winfo_exists() else None)
  threading.Thread(target=work,daemon=True).start()
 def review_plugin(self):
  path=filedialog.askopenfilename(parent=self,title='Choose Python plugin to review',filetypes=[('Python plugin','*.py')])
  if not path:return
  try:
   source=Path(path);content=source.read_bytes()
   if source.suffix.lower()!='.py' or source.is_symlink() or len(content)>500000:raise ValueError('Choose a regular Python source file smaller than 500 KB.')
   ast.parse(content);text=content.decode('utf8-sig');digest=hashlib.sha256(content).hexdigest()
  except Exception as exc:self.status.configure(text='Plugin was not installed: '+str(exc));return
  window=tk.Toplevel(self);window.title('Review plugin code before allowing execution');window.geometry('960x700')
  label(window,'Approving allows this exact Python source to execute in Advanced workspace on the next launch. Syntax checks do not establish that a plugin is safe.',wraplength=900,fg=MUTED).pack(padx=18,pady=12)
  code=tk.Text(window,wrap='none',bg=PANEL,fg=TEXT);code.pack(fill='both',expand=True,padx=18);code.insert('end',text);code.configure(state='disabled')
  def approve():
   if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:self.status.configure(text='Plugin changed; review it again.');window.destroy();return
   folder=self.manager.data/'advanced/approved-plugins';folder.mkdir(parents=True,exist_ok=True);(folder/source.name).write_bytes(content)
   registry=folder.parent/'plugin-approvals.json';entries=json.loads(registry.read_text(encoding='utf8')) if registry.exists() else {};entries[source.name]=digest
   temp=registry.with_suffix('.tmp');temp.write_text(json.dumps(entries,indent=2),encoding='utf8');temp.replace(registry)
   self.status.configure(text='Exact plugin source approved locally. Restart Advanced workspace to load it.');window.destroy()
  row=tk.Frame(window,bg=BG);row.pack(fill='x',padx=18,pady=12);button(row,'Cancel',window.destroy).pack(side='right');button(row,'Approve exact source',approve,True).pack(side='right',padx=10)
