"""Manual local PC-control QA: opens Calculator; no cloud requests or stored keys."""
import tkinter as tk
from app_catalog import installed_apps,match_entries,launch_entry
from screen_ui import ScreenPanel

if __name__=='__main__':
 matches=match_entries('Calculator',installed_apps())
 if len(matches)!=1:raise RuntimeError('Choose an unambiguous Calculator entry for this local QA fixture.')
 app=matches[0];launch_entry(app)
 root=tk.Tk();root.title('SARU PC Control Preview · Local QA');root.geometry('1280x900')
 panel=ScreenPanel(root,{},root.destroy,app=app,task='Local QA: click a number in Calculator; no files or messages.')
 root.after(180000,root.destroy);root.mainloop()
