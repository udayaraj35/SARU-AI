"""Owner-selected local work folder; always ask before exporting a deliverable."""
from pathlib import Path
from tkinter import filedialog

def work_directory(config):
 value=config.get('work_folder','').strip()
 folder=Path(value).expanduser() if value else (Path('D:/SARU_AI/Work') if Path('D:/').is_dir() else Path.home()/'Documents'/'SARU_AI'/'Work')
 folder.mkdir(parents=True,exist_ok=True)
 return folder

def ask_work_save(config,**options):
 options.setdefault('initialdir',str(work_directory(config)))
 options.setdefault('title','File ready — where should SARU save it?')
 options['confirmoverwrite']=True
 return filedialog.asksaveasfilename(**options)
