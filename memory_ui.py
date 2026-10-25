"""Read/search the owner's private local journal through the existing Memory entry."""
import tkinter as tk
import math
from pathlib import Path
from tkinter import ttk
from neon_ui import BG,PANEL,TEXT,MUTED,CYAN,label,button

class MemoryPanel(tk.Frame):
 def __init__(self,root,journal,folder,back,add_note,export):
  super().__init__(root,bg=BG);self.place(relwidth=1,relheight=1);self.journal=journal;self.folder=folder
  top=tk.Frame(self,bg=PANEL);top.pack(fill='x');button(top,'← Dashboard',back).pack(side='left',padx=16,pady=12);label(top,'SARU / MEMORY',font=('Segoe UI',21,'bold'),fg=CYAN).pack(side='left',padx=16)
  label(self,'Local conversations, notes, actual task results and office work. Memory is context, never permission. No microphone recordings are stored here.',fg=MUTED,wraplength=1000,justify='left').pack(anchor='w',padx=24,pady=12)
  self.map=tk.Canvas(self,bg=PANEL,height=170,highlightthickness=0);self.map.pack(fill='x',padx=24,pady=(0,10));self.map.bind('<Configure>',lambda event:self.draw_map())
  self.counts={};self.phase=0;self.animation=None;self.watch_job=None;self.signature=None;self.bind('<Destroy>',self.stop_animation,add='+')
  row=tk.Frame(self,bg=BG);row.pack(fill='x',padx=24)
  self.query=tk.StringVar();entry=tk.Entry(row,textvariable=self.query,bg=PANEL,fg=TEXT,insertbackground=TEXT,font=('Segoe UI',12));entry.pack(side='left',fill='x',expand=True,padx=(0,8));entry.bind('<Return>',lambda event:self.refresh())
  self.kind=tk.StringVar(value='all');choice=ttk.Combobox(row,textvariable=self.kind,values=['all','conversation','note','task','office','file'],state='readonly',width=16);choice.pack(side='left',padx=4);choice.bind('<<ComboboxSelected>>',lambda event:self.refresh())
  button(row,'Search / Refresh',self.refresh).pack(side='left',padx=4)
  self.summary=label(self,'',fg=CYAN);self.summary.pack(anchor='w',padx=24,pady=8)
  area=tk.Frame(self,bg=BG);area.pack(fill='both',expand=True,padx=24,pady=8)
  self.output=tk.Text(area,bg=PANEL,fg=TEXT,wrap='word',font=('Segoe UI',11),state='disabled',height=4);self.output.pack(side='left',fill='both',expand=True)
  scroll=ttk.Scrollbar(area,command=self.output.yview);scroll.pack(side='right',fill='y');self.output.configure(yscrollcommand=scroll.set)
  foot=tk.Frame(self,bg=BG);foot.pack(side='bottom',fill='x',padx=24,pady=12,before=area);button(foot,'Save a note',add_note).pack(side='left',padx=4);button(foot,'Export memory…',export).pack(side='left',padx=4);self.foot=foot
  self.bind('<Configure>',self.fit,add='+')
  self.refresh()
  self.animate()
  self.watch()
 def fit(self,event):
  if event.widget is self:self.map.configure(height=max(95,min(170,self.winfo_height()//5)));self.summary.configure(wraplength=max(400,self.winfo_width()-48))
 def stop_animation(self,event):
  if event.widget is self and self.animation:
   try:self.after_cancel(self.animation)
   except tk.TclError:pass
   self.animation=None
  if event.widget is self and self.watch_job:
   try:self.after_cancel(self.watch_job)
   except tk.TclError:pass
   self.watch_job=None
 def watch(self):
  self.journal.sync(self.folder)
  signature=self.journal.db.execute('SELECT count(*),max(id),max(updated_at) FROM memory_journal').fetchone()
  if signature!=self.signature:self.refresh();self.signature=signature
  self.watch_job=self.after(3000,self.watch)
 def animate(self):
  if not self.winfo_exists():return
  self.phase+=.08;self.draw_map();self.animation=self.after(120,self.animate)
 def choose(self,kind):self.kind.set(kind);self.query.set('');self.refresh()
 def draw_map(self):
  canvas=self.map;canvas.delete('all');width=max(600,canvas.winfo_width());cx=width/2;cy=80
  from theme_manager import palette
  colors=palette(self.journal.config.get('theme','Neon Rose'));canvas.configure(bg=colors['panel']);accent=colors['accent'];primary=colors['primary']
  nodes=[('conversation','Conversations',.13,45),('note','Notes',.13,125),('task','Work results',.87,45),('office','Office',.87,125),('file','Saved files',.5,145)]
  total=sum(self.counts.values());radius=28+2*math.sin(self.phase)
  for kind,title,x,y in nodes:
   x*=width;active=self.counts.get(kind,0)>0;tag='memory-'+kind
   canvas.create_line(cx,cy,x,y,fill=accent if active else MUTED,width=2 if active else 1)
   canvas.create_oval(x-7,y-7,x+7,y+7,fill=primary if active else MUTED,outline='',tags=tag)
   canvas.create_text(x,y-19,text=title+' · '+str(self.counts.get(kind,0)),fill=TEXT,font=('Segoe UI',10,'bold'),tags=tag)
   canvas.tag_bind(tag,'<Button-1>',lambda event,k=kind:self.choose(k))
  canvas.create_oval(cx-radius,cy-radius,cx+radius,cy+radius,outline=primary,width=2,tags='memory-all');canvas.create_text(cx,cy,text=str(total),fill=TEXT,font=('Segoe UI',15,'bold'),tags='memory-all');canvas.tag_bind('memory-all','<Button-1>',lambda event:self.choose('all'))
  canvas.create_text(cx,22,text='SARU MEMORY · actual saved records',fill=accent,font=('Segoe UI',12,'bold'))
 def refresh(self):
  self.journal.sync(self.folder);rows=self.journal.search(self.query.get(),100,self.kind.get());counts=self.journal.counts()
  self.counts=counts;self.draw_map()
  self.summary.configure(text=f'{sum(counts.values())} saved records • Showing {len(rows)} • '+', '.join(f'{key}: {value}' for key,value in counts.items()))
  database=Path(self.folder)/'memory.db';size=database.stat().st_size if database.is_file() else 0
  self.summary.configure(text=self.summary.cget('text')+'\nRecording '+('ON' if self.journal.config.get('remember_conversations',True) else 'OFF')+' · '+f'{size/1048576:.2f} MB · '+str(database))
  if self.journal.sync_warnings:self.summary.configure(text=self.summary.cget('text')+' • Sync incomplete: '+'; '.join(self.journal.sync_warnings))
  self.output.configure(state='normal');self.output.delete('1.0','end')
  for row in rows:self.output.insert('end',f"[{row['kind']}] {row['title']}\nSaved: {row['created_at']}  Updated: {row['updated_at']}\n{row['content']}\n\n")
  if not rows:self.output.insert('end','No matching saved memory.')
  self.output.configure(state='disabled')
