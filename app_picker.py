"""Search the installed Windows application catalog and keep portable launchers."""
import tkinter as tk
from tkinter import filedialog,messagebox
from queue import Queue,Empty
import threading
from pathlib import Path
from app_catalog import installed_apps,launch_entry
from neon_ui import BG,PANEL,TEXT,CYAN,label,button,entry
from theme_manager import apply_theme

class AppPicker(tk.Toplevel):
 def __init__(self,parent,config,save,control,query='',task=''):
  super().__init__(parent);self.title('SARU • Installed Apps');self.geometry('850x640');self.configure(bg=BG)
  self.cfg=config;self.save_config=save;self.control=control;self.task=task;self.items=[];self.visible=[];self.events=Queue();self.closed=False;self.launching=False;self.job=None;self.protocol('WM_DELETE_WINDOW',self.close)
  label(self,'APPS • Start Menu / Store / Registered / Portable',font=('Segoe UI',17,'bold'),fg=CYAN).pack(padx=14,pady=12)
  self.query=tk.StringVar(value=query);field=entry(self,self.query);field.pack(fill='x',padx=14,ipady=8);self.query.trace_add('write',lambda *args:self.filter())
  self.listing=tk.Listbox(self,bg=PANEL,fg=TEXT,font=('Segoe UI',12),selectbackground='#284c70',selectforeground=TEXT);self.listing.pack(fill='both',expand=True,padx=14,pady=10)
  self.listing.bind('<Double-Button-1>',lambda event:self.launch())
  toolbar=tk.Frame(self,bg=BG);toolbar.pack(fill='x',padx=10)
  for title,command in [('Open selected',self.launch),('Use app / PC Control',self.use),('Add portable EXE',self.portable),('Refresh',self.refresh)]:button(toolbar,title,command).pack(side='left',padx=3,pady=5)
  self.note=tk.StringVar(value='Loading installed applications…');label(self,'',textvariable=self.note,wraplength=790).pack(fill='x',padx=14,pady=10)
  apply_theme(self,config.get('theme','Neon Rose'));self.refresh();self.pump()
 def refresh(self):
  self.note.set('Reading registered applications…')
  def work():
   try:self.events.put(installed_apps(self.cfg.get('app_launchers',{})))
   except Exception as exc:self.events.put(exc)
  threading.Thread(target=work,daemon=True).start()
 def filter(self):
  query=self.query.get().casefold();self.visible=[item for item in self.items if query in item.title.casefold()];self.listing.delete(0,'end')
  for item in self.visible:self.listing.insert('end',item.title+'   · '+item.kind)
 def selected(self):
  selection=self.listing.curselection()
  if not selection:raise ValueError('Select an application first.')
  return self.visible[selection[0]]
 def launch(self,use=False):
  if self.launching:return
  try:item=self.selected()
  except Exception as exc:self.note.set(str(exc));return
  self.launching=True;self.note.set('Opening '+item.title+'…')
  def work():
   try:launch_entry(item);self.events.put({'launched':item,'use':use})
   except Exception as exc:self.events.put({'launch_error':str(exc)})
  threading.Thread(target=work,daemon=True).start()
 def use(self):
  self.launch(True)
 def portable(self):
  path=filedialog.askopenfilename(parent=self,title='Select an application executable',filetypes=[('Windows executable','*.exe')])
  if path and messagebox.askyesno('Remember portable application','Add this executable to SARU launchers?\n'+path,parent=self):
   self.cfg.setdefault('app_launchers',{})[Path(path).stem]=path;self.save_config();self.refresh()
 def pump(self):
  if self.closed:return
  try:
   while True:
    result=self.events.get_nowait()
    if isinstance(result,dict):
     self.launching=False
     if 'launch_error' in result:self.note.set(result['launch_error'])
     elif result.get('use'):self.close();self.control(result['launched'],self.task);return
     else:self.note.set('Launch requested: '+result['launched'].title+'. Use PC Control to operate its visible controls.')
    elif isinstance(result,Exception):self.note.set(str(result))
    else:self.items=result;self.filter();self.note.set(str(len(result))+' registered application entries. Missing portable apps can be added by choosing their EXE.')
  except Empty:pass
  self.job=self.after(100,self.pump)
 def close(self):
  self.closed=True
  if self.job:self.after_cancel(self.job)
  self.destroy()
