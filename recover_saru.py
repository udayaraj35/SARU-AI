"""Standalone recovery: does not import candidate app/design/voice modules."""
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from improvement_core import ImprovementManager

def main():
 root=tk.Tk();root.title('SARU • Independent Code Recovery');root.geometry('820x470')
 root.option_add('*Font',('Segoe UI',12))
 data=Path(os.getenv('SARU_DATA_DIR') or str(Path(os.getenv('APPDATA',str(Path.home())))/'SARU_AI'))
 manager=ImprovementManager(Path(__file__).resolve().parent,data)
 tk.Label(root,text='Restore an approved self-improvement backup',font=('Segoe UI',18,'bold')).pack(pady=16)
 tk.Label(root,text='This recovery window runs independently even if the changed SARU app cannot open.\nYour keys, memory and personal files are not modified.',wraplength=770).pack(pady=8)
 listing=tk.Listbox(root);listing.pack(fill='both',expand=True,padx=16,pady=12);rows=[]
 status=tk.StringVar();tk.Label(root,textvariable=status,wraplength=770).pack(pady=5)
 def refresh():
  rows[:]=[row for row in manager.recent() if row[2]=='applied'];listing.delete(0,'end')
  for identifier,summary,state in rows:listing.insert('end',summary[:100]+' • '+identifier[:8])
 def restore():
  if not listing.curselection():return
  identifier=rows[listing.curselection()[0]][0];proposal,_=manager.load(identifier)
  if not messagebox.askyesno('Restore backup','Restore only these changed SARU files?\n'+', '.join(c['path'] for c in proposal['changes'])+'\n\nLater edits will be preserved by refusing a conflicting rollback.',parent=root):return
  try:manager.rollback(identifier);status.set('Original source restored. Close this window and start SARU again.');refresh()
  except Exception as exc:status.set(str(exc))
 tk.Button(root,text='Restore selected backup',command=restore).pack(fill='x',padx=16,pady=12);refresh();root.mainloop()
if __name__=='__main__':main()
