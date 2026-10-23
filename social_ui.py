"""Native composer and encrypted account configuration for official Meta APIs."""
import copy
import threading
import tkinter as tk
from tkinter import messagebox
from social_api import publish

def account_settings(parent,config,save):
    w=tk.Toplevel(parent);w.title('Social accounts — Meta API');w.geometry('630x540')
    tk.Label(w,text='WhatsApp Business / Facebook Page',font=('Segoe UI',16,'bold')).pack(pady=12)
    tk.Label(w,text='Requires your Meta app, approved permissions and access tokens.\nWhatsApp text requires an eligible active conversation.\nFacebook publishing targets a Page, not a personal profile.',wraplength=590).pack(pady=8)
    entries={}
    for label,key,secret in [('Graph API version','meta_graph_version',False),('WhatsApp Phone Number ID','whatsapp_phone_id',False),('WhatsApp access token','WhatsApp Business',True),('Facebook Page ID','facebook_page_id',False),('Facebook Page access token','Facebook Page',True)]:
        tk.Label(w,text=label).pack(anchor='w',padx=20)
        e=tk.Entry(w,show='*' if secret else '',width=75);e.pack(padx=20,pady=4)
        e.insert(0,config.get('keys',{}).get(key,'') if secret else config.get(key,''));entries[key]=(e,secret)
    def commit():
        previous=copy.deepcopy(config)
        try:
            for key,(entry,secret) in entries.items():
                if secret:config.setdefault('keys',{})[key]=entry.get().strip()
                else:config[key]=entry.get().strip()
            save()
        except Exception:
            config.clear();config.update(previous)
            messagebox.showerror('Save failed','Could not encrypt/save accounts. Previous settings preserved.',parent=w);return
        w.destroy()
    tk.Button(w,text='Save accounts securely',command=commit).pack(pady=16)

def add_publish_controls(w,platform,text,config,save,recipient=''):

    if platform not in ('WhatsApp','Facebook'):return
    tk.Button(w,text='Connect / configure Meta account',command=lambda:account_settings(w,config,save)).pack(fill='x',padx=12,pady=3)
    target=tk.Entry(w)
    target.insert(0,recipient)
    if platform=='WhatsApp':
        tk.Label(w,text='Recipient international phone number (+country code)').pack()
        target.pack(fill='x',padx=12,pady=4)
    result=tk.StringVar(value='Not sent');tk.Label(w,textvariable=result,wraplength=600).pack()
    def send():
        message=text.get('1.0','end').strip();recipient=target.get().strip()
        destination=recipient if platform=='WhatsApp' else config.get('facebook_page_id','(Page not configured)')
        if not message:result.set('Write a message first.');return
        if not messagebox.askyesno('Review '+platform,platform+' destination: '+destination+'\n\n'+message+'\n\nSend / publish this exact text now?',parent=w):return
        snapshot=copy.deepcopy(config);button.configure(state='disabled');result.set('Submitting…')
        def work():
            try:
                operation=publish(platform,snapshot,recipient,message)
                outcome=('Accepted by WhatsApp (delivery not yet confirmed)' if platform=='WhatsApp' else 'Published to Facebook Page')+' — ID: '+operation
            except Exception as exc:outcome=str(exc)
            def finish():
                if w.winfo_exists():result.set(outcome);button.configure(state='normal')
            w.after(0,finish)
        threading.Thread(target=work,daemon=True).start()
    button=tk.Button(w,text='Review and send via WhatsApp Business API' if platform=='WhatsApp' else 'Review and publish to Facebook Page',command=send)
    button.pack(fill='x',padx=12,pady=6)
