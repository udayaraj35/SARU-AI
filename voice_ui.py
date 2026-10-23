"""Explicit Start/Stop voice page. Network/audio events cross a queue, not Tk threads."""
import tkinter as tk
from tkinter import messagebox
from queue import Queue,Empty
from live_voice import LiveVoice
from neon_ui import *

class VoicePanel(tk.Frame):
 def __init__(self,root,cfg,back,settings,push_to_talk,visual_event=None):
  super().__init__(root,bg=BG);self.place(relwidth=1,relheight=1);self.visual_event=visual_event;self.events=Queue(maxsize=500);self.closed=False;self.job=None;self.engine=None;self.cfg=cfg
  self.bind('<Destroy>',self.cleanup,add='+')
  top=tk.Frame(self,bg=PANEL);top.pack(fill='x');button(top,'← Dashboard',back).pack(side='left',padx=15,pady=12);label(top,'SARU / LIVE VOICE',font=('Segoe UI',21,'bold'),fg=CYAN).pack(side='left',padx=15)
  box=card(self,'NATURAL CONVERSATION');box.pack(fill='x',padx=24,pady=16)
  label(box,'Start opens your microphone and streams audio to Google Gemini using SARU’s Gemini API key. Stop closes the session. Transcripts stay on this page and are not saved to memory.',fg=MUTED,wraplength=850,justify='left').pack(anchor='w',padx=16,pady=8)
  self.state=label(box,'STOPPED • Microphone closed',font=('Segoe UI',15,'bold'),fg=CYAN);self.state.pack(pady=9)
  row=tk.Frame(box,bg=PANEL);row.pack(fill='x',padx=16,pady=10)
  self.start_button=button(row,'Start conversation',self.start,True);self.start_button.pack(side='left',padx=4)
  self.stop_button=button(row,'Stop',self.stop);self.stop_button.pack(side='left',padx=4)
  self.muted=tk.BooleanVar(value=False);tk.Checkbutton(row,text='Mute microphone',variable=self.muted,command=self.mute,bg=PANEL,fg=TEXT,selectcolor=BG).pack(side='left',padx=12)
  button(row,'Voice settings',settings).pack(side='right')
  self.meter=tk.Canvas(box,height=24,bg='#071021',highlightthickness=0);self.meter.pack(fill='x',padx=20,pady=(0,12))
  label(self,'Use headphones for interruption support. Speaker mode pauses microphone transmission while SARU speaks to reduce echo. This voice channel is conversational; use PC Commands for actions.',fg=MUTED,wraplength=880,justify='left').pack(padx=24,pady=8,anchor='w')
  self.transcript=tk.Text(self,bg='#081225',fg=TEXT,wrap='word',font=('Segoe UI',12),relief='flat');self.transcript.pack(fill='both',expand=True,padx=24,pady=10)
  button(self,'Classic push-to-talk (Windows TTS)',push_to_talk).pack(anchor='w',padx=24,pady=(0,16))
  self.pump()
 def emit(self,kind,value):
  try:self.events.put_nowait((kind,value))
  except Exception:pass
 def start(self):
  if self.engine and self.engine.active:return
  try:
   self.engine=LiveVoice(self.cfg,self.emit);self.engine.start();self.start_button.configure(state='disabled');self.muted.set(False)
  except Exception as exc:self.state.configure(text=str(exc),fg=PINK)
 def stop(self):
  if self.engine:self.engine.stop()
  self.state.configure(text='STOPPING • Waiting for microphone/session cleanup',fg=MUTED)
 def mute(self):
  if self.engine and self.engine.active:self.engine.mute(self.muted.get())
 def pump(self):
  if self.closed:return
  try:
   for _ in range(100):
    kind,value=self.events.get_nowait()
    if self.visual_event:self.visual_event(kind,value)
    if kind=='state':
     self.state.configure(text=value+(' • Microphone closed' if value=='STOPPED' else ''),fg=CYAN)
     if value=='STOPPED':self.start_button.configure(state='normal')
    elif kind=='error':self.transcript.insert('end','Error: '+value+'\n');self.state.configure(text='ERROR — check key/model/device settings',fg=PINK)
    elif kind=='transcript':self.transcript.insert('end',value[0]+': '+value[1]+'\n');self.transcript.see('end')
    elif kind in ('input_level','output_level'):
     self.meter.delete('all');self.meter.create_rectangle(0,0,max(1,self.meter.winfo_width()*value),24,fill=CYAN if kind=='input_level' else PINK,outline='')
  except Empty:pass
  self.job=self.after(60,self.pump)
 def cleanup(self,event):
  if event.widget is not self:return
  self.closed=True
  if self.engine:self.engine.stop()
  if self.visual_event:
   if self.engine and self.engine.active:self.visual_event('stopping',self.engine)
   else:self.visual_event('state','STOPPED')
  if self.job:self.after_cancel(self.job)
