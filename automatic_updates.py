"""Automatic release discovery/staging; install remains an explicit setup action."""
import queue
import threading
from tkinter import messagebox
import update_manager as updates

def install_auto_checks(root,config,status):
    events=queue.Queue();running=False
    def check():
        nonlocal running
        repo=config.get('saru_release_repo','').strip()
        if config.get('auto_check_updates') and repo and not running:
            running=True
            download=bool(config.get('auto_download_updates'))
            def worker():
                try:
                    release=updates.latest_release(repo)
                    if updates.is_newer(release['tag']):
                        package=updates.stage_verified_release(release) if download else None
                        events.put(('ready',(release,package)))
                except Exception:events.put(('error',None))
                finally:events.put(('finished',None))
            threading.Thread(target=worker,daemon=True).start()
        root.after(6*60*60*1000,check)
    def poll():
        nonlocal running
        try:
            while True:
                kind,payload=events.get_nowait()
                if kind=='finished':running=False
                elif kind=='error':status.set('Update check unavailable; retry from Update Center.')
                else:
                    release,package=payload
                    status.set('SARU update available: '+release['tag'])
                    if package:messagebox.showinfo('SARU update downloaded','Verified download: '+str(package)+'\n\nClose SARU, extract this release and run its installer. Settings and memory remain in AppData.',parent=root)
        except queue.Empty:pass
        root.after(1000,poll)
    root.after(5000,check);root.after(1000,poll)

def settings_ui(parent,config,save):
    import tkinter as tk
    w=tk.Toplevel(parent);w.title('SARU update source');w.geometry('600x300')
    tk.Label(w,text='Your trusted SARU GitHub release repository').pack(pady=12)
    repo=tk.Entry(w,width=70);repo.insert(0,config.get('saru_release_repo',''));repo.pack(padx=16,pady=8)
    check=tk.BooleanVar(value=config.get('auto_check_updates',False));download=tk.BooleanVar(value=config.get('auto_download_updates',False))
    tk.Checkbutton(w,text='Check on launch and every six hours',variable=check).pack(anchor='w',padx=18)
    tk.Checkbutton(w,text='Automatically download and checksum-verify newer releases',variable=download).pack(anchor='w',padx=18)
    tk.Label(w,text='Only use your trusted repository. A checksum does not authenticate its publisher.\nGitHub skills are code; they are not installed or executed automatically.',wraplength=560).pack(pady=12)
    def commit():
        import copy
        previous=copy.deepcopy(config)
        try:
            config['saru_release_repo']=updates.configure_repository(repo.get())
            config['auto_check_updates']=check.get();config['auto_download_updates']=download.get();save()
        except Exception as exc:
            config.clear();config.update(previous);messagebox.showerror('Update source',str(exc),parent=w);return
        w.destroy()
    tk.Button(w,text='Save update preferences',command=commit).pack(pady=10)
