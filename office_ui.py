"""Animated office rooms with real persistent job and agent states."""
import copy,json,threading
from queue import Queue,Empty
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from office_core import Office,FORMATS,requested_format
from neon_ui import BG,PANEL,TEXT,CYAN,MUTED,label,button,entry
from theme_manager import apply_theme,palette
from appearance_controls import apply_text_scale

class OfficePanel(tk.Frame):
 def __init__(self,parent,config,data,back,task='',memory=None):
  super().__init__(parent,bg=BG);self.place(relwidth=1,relheight=1);self.cfg=config;self.office=Office(data);self.events=Queue();self.cancel=threading.Event();self.closed=False;self.job_id=None;self.busy=False;self.phase=0;self.timer=None;self.bind('<Destroy>',self.cleanup,add='+')
  from office_observer import OfficeObserver
  self.observer=OfficeObserver(self.office);self.memory_action=memory
  top=tk.Frame(self,bg=PANEL);top.pack(fill='x')
  button(top,'← Dashboard',back).pack(side='left',padx=8,pady=8);label(top,'SARU OFFICE · Agent Rooms',font=('Segoe UI',19,'bold'),fg=CYAN).pack(side='left',padx=10)
  tools=tk.Frame(self,bg=PANEL);tools.pack(fill='x',pady=2)
  for title,action in [('Mind',self.open_mind),('Memory',lambda:memory() if memory else self.note.set('Open saved memory from the dashboard.')),('Team',self.open_team),('Task desk',self.toggle_desk),('+ Room',self.new_agent),('Full screen',lambda:parent.attributes('-fullscreen',not bool(parent.attributes('-fullscreen'))))]:
   control=button(tools,title,action,title=='Task desk');control.configure(width=115,height=34);control.pack(side='left',padx=4,pady=3)
  self.note=tk.StringVar(value='Assign a job → agents submit → SARU reviews → you approve → save the result.')
  self.saru_image=None
  try:
   from PIL import ImageTk,ImageOps
   from portrait_assets import load_portrait
   self.saru_image=ImageTk.PhotoImage(ImageOps.contain(load_portrait(config.get('photo'),config.get('portrait_design','new')).convert('RGBA'),(48,64)))
  except (OSError,ValueError):pass
  label(self,'',textvariable=self.note,fg=MUTED,wraplength=1100).pack(fill='x',padx=12,pady=4)
  split=tk.PanedWindow(self,orient='horizontal',bg=BG,sashwidth=6);self.split=split;split.pack(fill='both',expand=True,padx=8,pady=5)
  left=tk.Frame(split,bg=BG);right=tk.Frame(split,bg=BG);split.add(left,minsize=310,width=490);split.add(right,minsize=420);self.desk=right;self.desk_open=True
  rooms=tk.Frame(left,bg=BG);rooms.pack(fill='both',expand=True)
  self.canvas=tk.Canvas(rooms,bg=BG,highlightthickness=0);self.canvas.pack(side='left',fill='both',expand=True);scroll=tk.Scrollbar(rooms,command=self.canvas.yview);scroll.pack(side='right',fill='y');self.canvas.configure(yscrollcommand=scroll.set)
  self.canvas.bind('<Configure>',lambda event:self.draw());self.canvas.bind('<MouseWheel>',lambda event:self.canvas.yview_scroll(-int(event.delta/120),'units'))
  self.canvas.bind('<Button-1>',self.room_click)
  label(left,'Live job status · Finite walking routes · Idle agents check the local task queue every 30 seconds.',fg=MUTED,wraplength=440).pack(fill='x',padx=8,pady=3)
  label(left,'Office jobs',fg=CYAN).pack(anchor='w',padx=8)
  self.jobs=tk.Listbox(left,height=3,bg=PANEL,fg=TEXT,selectbackground='#284c70',selectforeground=TEXT);self.jobs.pack(fill='x',padx=4,pady=4);self.jobs.bind('<<ListboxSelect>>',lambda event:self.select_job())
  self.book=ttk.Notebook(right);self.book.pack(fill='both',expand=True)
  assign=tk.Frame(self.book,bg=BG);review=tk.Frame(self.book,bg=BG);self.book.add(assign,text='Assign job');self.book.add(review,text='SARU desk / review / save')
  label(assign,'What should SARU and the team produce?',fg=CYAN).pack(anchor='w',padx=8,pady=6)
  self.task=tk.Text(assign,height=4,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word');self.task.pack(fill='x',padx=8);self.task.insert('1.0',task)
  label(assign,'Select rooms / agents (at most six per job)',fg=MUTED).pack(anchor='w',padx=8,pady=6)
  self.agents=tk.Listbox(assign,selectmode='extended',exportselection=False,height=4,bg=PANEL,fg=TEXT,selectbackground='#284c70',selectforeground=TEXT);self.agents.pack(fill='x',padx=8)
  label(assign,'Resources / notes to share with the selected AI provider',fg=MUTED).pack(anchor='w',padx=8,pady=6)
  self.context=tk.Text(assign,height=4,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word');self.context.pack(fill='both',expand=True,padx=8)
  row=tk.Frame(assign,bg=BG);row.pack(fill='x',pady=8)
  button(row,'Attach resources',self.attach).pack(side='left',padx=4);button(row,'Review / start job',self.start,True).pack(side='left',padx=4);button(row,'Cancel job',self.cancel_current).pack(side='left',padx=4)
  for child in row.winfo_children():child.configure(width=125)
  self.output=tk.Text(review,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word');self.output.pack(fill='both',expand=True,padx=8,pady=8)
  savebar=tk.Frame(review,bg=BG);savebar.pack(fill='x')
  approvalbar=tk.Frame(review,bg=BG);approvalbar.pack(fill='x')
  self.format=tk.StringVar(value=requested_format(task) or 'docx');ttk.Combobox(savebar,textvariable=self.format,values=FORMATS,state='readonly',width=8).pack(side='left',padx=4)
  button(approvalbar,'Approve reviewed draft',self.approve,True).pack(side='left',padx=4,pady=8);button(approvalbar,'Save to my PC',self.export).pack(side='left',padx=4)
  label(review,'MP4 exports a short text-slide video. PDF uses rendered text pages. The stored reviewed result is exported; editing this preview does not change it.',fg=MUTED,wraplength=650).pack(fill='x',padx=8,pady=5)
  if not task:self.toggle_desk()
  self.refresh();apply_theme(self,config.get('theme','Neon Rose'));apply_text_scale(self,config.get('ui_text_scale',100));self.pump()
 def refresh(self):
  self.agent_rows=self.office.agents();self.agents.delete(0,'end')
  for agent in self.agent_rows:self.agents.insert('end',agent['room']+' · '+agent['name'])
  self.agents.selection_set(0,max(0,min(5,len(self.agent_rows)-1)))
  self.job_rows=self.office.jobs();self.jobs.delete(0,'end')
  for job in self.job_rows:self.jobs.insert('end',job['state']+' · '+job['task'][:60])
  self.draw()
 def toggle_desk(self):
  if self.desk_open:self.split.forget(self.desk);self.desk_open=False
  else:self.split.add(self.desk,minsize=420,width=440);self.desk_open=True
 def cancel_current(self):
  _,state=self.observer.read(self.job_id,force=True)
  identifier=self.job_id or state.get('id')
  if identifier and self.office.cancel_job(identifier):self.note.set('Cancellation requested. Waiting for in-flight AI requests to return.')
  else:self.note.set('No running office job selected.')
 def open_team(self):
  if not self.desk_open:self.toggle_desk()
  self.book.select(0);self.agents.focus_set()
 def open_mind(self):
  from office_observer import show_mind
  _,state=self.observer.read(self.job_id,force=True)
  show_mind(self,self.office,self.cfg,state)
 def draw(self):
  if self.closed:return
  from office_scene import draw_office
  agents,state=self.observer.read(self.job_id)
  draw_office(self.canvas,palette(self.cfg.get('theme')),agents,state,self.phase,self.saru_image,self.cfg.get('reduced_motion',False))
 def room_click(self,event):
  for tag in self.canvas.gettags('current'):
   if tag=='mind':self.open_mind();return
   if tag=='memory':
    if self.memory_action:self.memory_action()
    return
   if tag=='team':self.open_team();return
   if tag=='saru_desk':
    if not self.desk_open:self.toggle_desk()
    return
   if tag.startswith('room_'):
    agent=next((agent for agent in self.office.agents() if agent['id']==tag[5:]),None)
    if agent:self.agent_details(agent)
    break
 def agent_details(self,agent):
  self.new_agent(agent)
 def new_agent(self,agent=None):
  window=tk.Toplevel(self);window.title('Edit office room / agent' if agent else 'New office room / agent');window.geometry('560x500');window.configure(bg=BG);fields={}
  for key,title in (('room','Room name'),('name','Agent name'),('instructions','Role, instructions and resources')):
   label(window,title).pack(anchor='w',padx=12,pady=7)
   if key=='instructions':field=tk.Text(window,height=7,bg=PANEL,fg=TEXT,insertbackground=CYAN);field.pack(fill='both',expand=True,padx=12);fields[key]=field;field.insert('1.0',agent.get(key,'') if agent else '')
   else:variable=tk.StringVar(value=agent.get(key,'') if agent else '');entry(window,variable).pack(fill='x',padx=12,ipady=5);fields[key]=variable
  format=tk.StringVar(value=agent.get('format','txt') if agent else 'txt');ttk.Combobox(window,textvariable=format,values=FORMATS,state='readonly').pack(fill='x',padx=12,pady=8)
  def save():
   try:
    values=(fields['room'].get(),fields['name'].get(),fields['instructions'].get('1.0','end').strip(),format.get())
    if agent:self.office.update_agent(agent['id'],*values)
    else:self.office.add_agent(*values)
    self.refresh();window.destroy()
   except Exception as exc:messagebox.showerror('New agent',str(exc),parent=window)
  button(window,'Save room / agent',save,True).pack(pady=10);apply_theme(window,self.cfg.get('theme','Neon Rose'))
 def attach(self):
  paths=filedialog.askopenfilenames(parent=self,title='Choose resources for this job',filetypes=[('Documents','*.txt *.md *.csv *.json *.docx *.xlsx *.pdf')])
  if len(paths)>10:self.note.set('Choose at most ten documents.');return
  try:
   from office_resources import extract
   for path in paths:
    text=extract(path);self.context.insert('end','\nRESOURCE '+Path(path).name+' (excerpt)\n'+text[:12000]+'\n')
   self.note.set('Review attached excerpts before sharing with the AI provider. Maximum shared context: 30,000 characters.')
  except Exception as exc:self.note.set(str(exc))
 def start(self):
  if self.busy:self.note.set('Wait for the active operation.');return
  task=self.task.get('1.0','end').strip();context=self.context.get('1.0','end').strip();ids=[self.agent_rows[i]['id'] for i in self.agents.curselection()]
  if not ids or len(ids)>6:self.note.set('Select 1–6 agents.');return
  if len(context)>30000:self.note.set('Trim shared resource context to 30,000 characters.');return
  if not messagebox.askyesno('Start the SARU office job','Send the task, selected agent instructions and displayed resource text to '+self.cfg.get('provider','Gemini')+'? This makes several model requests and may use paid API quota.\n\nJob: '+task+'\n\nNo PC input, publication or file export happens automatically.',parent=self):return
  try:
   self.job_id=self.office.create(task)
   if requested_format(task):self.format.set(requested_format(task))
  except Exception as exc:self.note.set(str(exc));return
  self.busy=True;self.cancel.clear();config=copy.deepcopy(self.cfg);identifier=self.job_id
  def work():
   try:self.office.run(identifier,config,lambda:self.events.put('refresh'),self.cancel,agent_ids=ids,context=context)
   except Exception as exc:self.events.put(('error',str(exc)))
   finally:self.events.put('finished')
  threading.Thread(target=work,daemon=True).start();self.book.select(1);self.refresh()
 def select_job(self):
  selection=self.jobs.curselection()
  if selection:self.job_id=self.job_rows[selection[0]]['id'];self.show_job();self.draw()
 def show_job(self):
  if not self.job_id:return
  job=self.office.job(self.job_id)
  if requested_format(job['task']):self.format.set(requested_format(job['task']))
  self.output.delete('1.0','end');self.output.insert('end','JOB: '+job['task']+'\nSTATE: '+job['state']+'\n\n')
  for item in job['assignments']:self.output.insert('end',item['room']+' / '+item['name']+' → '+item['state']+'\n')
  self.output.insert('end','\nSARU REVIEW:\n'+job['review']+'\n'+job['error']+'\n')
  if job['result']:
   result=json.loads(job['result']);self.output.insert('end','\n'+result['title']+'\n\n'+result['body'])
   for table in result.get('tables',[]):self.output.insert('end','\n\n'+str(table.get('name','Table'))+'\n'+'\n'.join(' | '.join(map(str,row)) for row in table['rows']))
  for item in job['assignments']:
   if item['result']:
    submission=json.loads(item['result']);self.output.insert('end','\n\n──────── SUBAGENT SUBMISSION ────────\n'+item['name']+' / '+item['room']+'\nTask: '+item['task']+'\n\n'+submission['title']+'\n'+submission['body'])
 def approve(self):
  try:
   if not self.job_id:raise ValueError('Choose a completed job first.')
   if messagebox.askyesno('Approve this reviewed result','Approve the stored SARU-reviewed result for local export? Check facts and tables first.',parent=self):self.office.approve(self.job_id);self.refresh();self.show_job()
  except Exception as exc:self.note.set(str(exc))
 def export(self):
  if self.busy:self.note.set('Wait for the active operation.');return
  try:
   if not self.job_id or self.office.job(self.job_id)['state'] not in ('approved','saved'):raise ValueError('Approve the reviewed job first.')
   from work_storage import ask_work_save
   format=self.format.get();path=ask_work_save(self.cfg,parent=self,title='File ready — save SARU deliverable',defaultextension='.'+format,filetypes=[(format.upper(),'*.'+format)])
   if not path:return
   self.busy=True;identifier=self.job_id
   def work():
    try:self.events.put(('saved',self.office.export(identifier,format,path)))
    except Exception as exc:self.events.put(('error',str(exc)))
    finally:self.events.put('finished')
   threading.Thread(target=work,daemon=True).start()
  except Exception as exc:self.note.set(str(exc))
 def pump(self):
  if self.closed:return
  try:
   while True:
    event=self.events.get_nowait()
    if event=='refresh':self.refresh();self.show_job()
    elif event=='finished':self.busy=False;self.refresh();self.show_job()
    elif isinstance(event,tuple):self.note.set(('Saved: ' if event[0]=='saved' else 'Office error: ')+event[1])
  except Empty:pass
  _,observed=self.observer.read(self.job_id)
  signature=(observed.get('id'),observed['state'],tuple((a['id'],a['state']) for a in observed['assignments']))
  if signature!=getattr(self,'observed_signature',None):
   self.observed_signature=signature
   self.job_rows=self.office.jobs();self.jobs.delete(0,'end')
   for job in self.job_rows:self.jobs.insert('end',job['state']+' · '+job['task'][:60])
   if self.job_id:self.show_job()
  self.phase+=1;self.draw();self.timer=self.after(100,self.pump)
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True
   if self.timer:self.after_cancel(self.timer)
