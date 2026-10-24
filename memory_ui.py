"""Read/search the owner's private local journal through the existing Memory entry."""
import tkinter as tk
from tkinter import ttk
from neon_ui import BG,PANEL,TEXT,MUTED,CYAN,label,button

class MemoryPanel(tk.Frame):
 def __init__(self,root,journal,folder,back,add_note,export):
  super().__init__(root,bg=BG);self.place(relwidth=1,relheight=1);self.journal=journal;self.folder=folder
  top=tk.Frame(self,bg=PANEL);top.pack(fill='x');button(top,'← Dashboard',back).pack(side='left',padx=16,pady=12);label(top,'SARU / MEMORY',font=('Segoe UI',21,'bold'),fg=CYAN).pack(side='left',padx=16)
  label(self,'Local conversations, notes, actual task results and office work. Memory is context, never permission. No microphone recordings are stored here.',fg=MUTED,wraplength=1000,justify='left').pack(anchor='w',padx=24,pady=12)
  row=tk.Frame(self,bg=BG);row.pack(fill='x',padx=24)
  self.query=tk.StringVar();entry=tk.Entry(row,textvariable=self.query,bg=PANEL,fg=TEXT,insertbackground=TEXT,font=('Segoe UI',12));entry.pack(side='left',fill='x',expand=True,padx=(0,8));entry.bind('<Return>',lambda event:self.refresh())
  self.kind=tk.StringVar(value='all');choice=ttk.Combobox(row,textvariable=self.kind,values=['all','conversation','note','task','office','file'],state='readonly',width=16);choice.pack(side='left',padx=4);choice.bind('<<ComboboxSelected>>',lambda event:self.refresh())
  button(row,'Search / Refresh',self.refresh).pack(side='left',padx=4)
  self.summary=label(self,'',fg=CYAN);self.summary.pack(anchor='w',padx=24,pady=8)
  area=tk.Frame(self,bg=BG);area.pack(fill='both',expand=True,padx=24,pady=8)
  self.output=tk.Text(area,bg=PANEL,fg=TEXT,wrap='word',font=('Segoe UI',11),state='disabled');self.output.pack(side='left',fill='both',expand=True)
  scroll=ttk.Scrollbar(area,command=self.output.yview);scroll.pack(side='right',fill='y');self.output.configure(yscrollcommand=scroll.set)
  foot=tk.Frame(self,bg=BG);foot.pack(fill='x',padx=24,pady=12);button(foot,'Save a note',add_note).pack(side='left',padx=4);button(foot,'Export memory…',export).pack(side='left',padx=4)
  self.refresh()
 def refresh(self):
  self.journal.sync(self.folder);rows=self.journal.search(self.query.get(),100,self.kind.get());counts=self.journal.counts()
  self.summary.configure(text=f'{sum(counts.values())} saved records • Showing {len(rows)} • '+', '.join(f'{key}: {value}' for key,value in counts.items()))
  if self.journal.sync_warnings:self.summary.configure(text=self.summary.cget('text')+' • Sync incomplete: '+'; '.join(self.journal.sync_warnings))
  self.output.configure(state='normal');self.output.delete('1.0','end')
  for row in rows:self.output.insert('end',f"[{row['kind']}] {row['title']}\nSaved: {row['created_at']}  Updated: {row['updated_at']}\n{row['content']}\n\n")
  if not rows:self.output.insert('end','No matching saved memory.')
  self.output.configure(state='disabled')
