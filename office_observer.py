"""Shared local office observation. Idle check-ins never create paid AI calls."""
import time

class OfficeObserver:
 def __init__(self,office):
  self.office=office;self.last_read=-999;self.last_checks={};self.checkins={};self.agents=[];self.state=None;self.selected=None
 def read(self,identifier=None,now=None,force=False):
  now=time.monotonic() if now is None else now
  if not force and now-self.last_read<1 and identifier==self.selected:return self.agents,self.state
  self.last_read=now;self.selected=identifier;self.agents=self.office.agents();jobs=self.office.jobs()
  if identifier:self.state=self.office.job(identifier)
  else:
   active=next((job for job in jobs if job['state'] in ('planning','working','sarureview')),jobs[0] if jobs else None)
   self.state=self.office.job(active['id']) if active else {'state':'idle','assignments':[]}
  busy={item['agent'] for item in self.state['assignments'] if item['state'] in ('queued','working')}
  for i,agent in enumerate(self.agents):
   key=agent['id']
   if key not in self.last_checks:self.last_checks[key]=now-28+i*2
   if key not in busy and now-self.last_checks[key]>=30:
    self.office.check_in(key);self.last_checks[key]=now;self.checkins[key]=now
  self.state['_checkins']=dict(self.checkins)
  return self.agents,self.state

def mind_text(office,config,state):
 lines=['SARU MIND · Operational state', 'Provider: '+config.get('provider','Gemini'),'Model: '+config.get('model','Not configured'),'',
        'Owner task → SARU plan → selected agents → SARU review → owner approval',
        'This view shows task routing and saved events, not private model reasoning.', '']
 if state:
  lines+=['Job: '+state.get('task','No job assigned'),'State: '+state['state'],'']
  for a in state.get('assignments',[]):lines += [a['name']+' · '+a['state'],a['task'],'']
  if state.get('review'):lines+=['SARU review: '+state['review'],'']
 names={a['id']:a['name'] for a in office.agents()}
 lines+=['LOCAL OFFICE EVENTS']
 for event in office.recent_events():
  lines.append(time.strftime('%H:%M:%S',time.localtime(event['at']))+' · '+names.get(event['agent'],event['agent'])+' · '+event['message'])
 return '\n'.join(lines)

def show_mind(parent,office,config,state):
 import tkinter as tk
 from theme_manager import apply_theme
 from neon_ui import BG,PANEL,TEXT,CYAN
 window=tk.Toplevel(parent);window.title('SARU Mind · Live task routing');window.geometry('750x590');window.configure(bg=BG)
 text=tk.Text(window,bg=PANEL,fg=TEXT,insertbackground=CYAN,wrap='word',font=('Segoe UI',11));text.pack(fill='both',expand=True,padx=12,pady=12)
 bar=tk.Scrollbar(text,command=text.yview);bar.pack(side='right',fill='y');text.configure(yscrollcommand=bar.set)
 text.insert('1.0',mind_text(office,config,state));text.configure(state='disabled');apply_theme(window,config.get('theme','Neon Rose'))
