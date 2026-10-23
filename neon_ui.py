"""SARU neon UI primitives, shared by dashboard and settings."""
import tkinter as tk
BG='#061226';PANEL='#0b1930';LINE='#284c70';TEXT='#edf4ff';MUTED='#9cb0cf';CYAN='#18cde2';PINK='#ff2856'

def label(parent,text,**kw):
 return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=kw.pop('fg',TEXT),font=kw.pop('font',('Segoe UI',10)),**kw)

def button(parent,text,command,primary=False):
 text={'Gmail draft':'Gmail','WhatsApp draft':'WhatsApp Web','Social drafts':'Facebook','Voice: push to talk':'Voice'}.get(text,text)
 from reference_widgets import NeonButton
 b=NeonButton(parent,text,command,primary=primary,width=180,height=42)
 return b

def card(parent,title):
 f=tk.Frame(parent,bg=PANEL,highlightbackground=LINE,highlightthickness=1)
 label(f,title,font=('Segoe UI',11,'bold')).pack(anchor='w',padx=14,pady=(10,8))
 return f

def entry(parent,var,secret=False):
 e=tk.Entry(parent,textvariable=var,show='*' if secret else '',bg='#081225',fg=TEXT,insertbackground=CYAN,relief='flat',font=('Segoe UI',11),highlightthickness=1,highlightbackground=LINE,highlightcolor=CYAN)
 return e
