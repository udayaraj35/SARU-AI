"""UI-owned coordinator for explicit camera, reminders and voice-profile requests."""
import datetime,threading,time
from personal_reminders import ReminderStore,format_due

class PersonalHub:
 def __init__(self,root,data,cfg,consent,report,speak,voice_hub):
  self.root=root;self.data=data;self.cfg=cfg;self.consent=consent;self.report=report;self.speak=speak;self.voice_hub=voice_hub;self.camera=None;self.voices=None;self.closed=False;self.job=None
  from message_outbox import MessageOutbox
  self.outbox=MessageOutbox(data/'outbox.sqlite');self.outbox_busy=False
  from queue import Queue
  self.outbox_results=Queue()
  self.reminders=ReminderStore(data/'reminders.sqlite');self.job=root.after(3000,self.poll)
  root.bind('<Destroy>',lambda event:self.close() if event.widget is root else None,add='+')
 def handle(self,action,arg=None):
  if action=='outbox_add':
   due,target,message=arg;identifier=self.outbox.add(due,target,message,self.cfg)
   return f'WhatsApp Business message #{identifier} scheduled for '+format_due(due)+'. Exact recipient/text saved locally encrypted. SARU must be running and PC awake; no automatic retries.'
  if action=='outbox_list':return 'Scheduled message status:\n'+'\n'.join(f'#{i} · {format_due(due)} · {state} · {note}' for i,due,state,note in self.outbox.list())
  if action=='outbox_cancel':return 'Scheduled message cancelled.' if self.outbox.cancel(arg) else 'Cannot cancel: not pending, or already attempted. Check status/account.'
  if action=='reminder_add':
   due,title,kind=arg;identifier=self.reminders.add(due,title,kind);return f'{kind.title()} #{identifier}: {title} · '+format_due(due)+' · SARU must be running; missed reminders appear when reopened.'
  if action=='reminders':
   rows=self.reminders.outstanding()
   return 'Pending reminders (Europe/Sofia):\n'+'\n'.join(f'#{i} · {format_due(due)} · {title}' for i,due,title,kind in rows) if rows else 'No pending reminders.'
  if action=='reminder_cancel':return 'Reminder cancelled/completed.' if self.reminders.mark(arg,'cancelled') else 'No matching pending reminder.'
  if action=='camera':
   if arg=='stop':
    if self.camera and self.camera.winfo_exists():self.camera.destroy()
    return 'Camera stopped.'
   if not self.camera or not self.camera.winfo_exists():
    from camera_companion import CameraCompanion
    self.camera=CameraCompanion(self.root,self.cfg,self.consent,self.report)
   self.camera.deiconify();self.camera.lift();return 'Camera preview requested. Preview status shows device availability. No frames have been shared.'
  if action=='camera_ask':
   self.handle('camera','open');camera=self.camera;camera.question.set(arg)
   def wait(attempt=0):
    if self.closed or camera.closed:return
    if camera.frame is not None:camera.analyze()
    elif attempt<20:camera.after(250,lambda:wait(attempt+1))
    else:self.report('Camera frame unavailable. Check camera permission/device before asking again.')
   camera.after(100,wait);return 'Waiting for a camera frame; sharing requires your review.'
  if action in ('voice_profiles','voice_enroll','voice_compare'):
   if not self.voices or not self.voices.winfo_exists():
    from voice_profiles import VoiceProfilePanel
    self.voices=VoiceProfilePanel(self.root,self.data,self.consent,self.report,self.microphone_free)
   self.voices.deiconify();self.voices.lift()
   if action=='voice_enroll':self.voices.name.set(arg);self.voices.enroll()
   elif action=='voice_compare':self.voices.record(False)
   return 'Voice profiles opened. Live Voice stops before approved recording; samples stay local and cannot authorize actions.'
  raise ValueError('Unsupported personal-assistant action')
 def microphone_free(self):
  if self.voice_hub.engine and self.voice_hub.engine.active:
   self.voice_hub.stop();return False
  return True
 def poll(self):
  if self.closed:return
  from queue import Empty
  try:
   while True:
    identifier,state,note=self.outbox_results.get_nowait();self.outbox.finish(identifier,state,note);self.outbox_busy=False;self.report('WhatsApp scheduled message #'+str(identifier)+': '+state+'. '+note)
  except Empty:pass
  if not self.outbox_busy:
   claimed=self.outbox.claim(self.cfg)
   if claimed:
    import copy
    identifier,body=claimed;config=copy.deepcopy(self.cfg);self.outbox_busy=True
    def send():
     try:
      from social_api import publish
      operation=publish('WhatsApp',config,body['target'],body['message']);result=(identifier,'accepted','Meta accepted the message request. Delivery is not verified.')
     except Exception:
      result=(identifier,'needs_check','No automatic retry. Check WhatsApp/account status before scheduling again.')
     self.outbox_results.put(result)
    threading.Thread(target=send,daemon=True).start()
  for identifier,due,title,kind in self.reminders.due():
   self.notify(identifier,due,title,kind)
   self.reminders.mark(identifier,'delivered')
  self.job=self.root.after(10000,self.poll)
 def notify(self,identifier,due,title,kind):
  import tkinter as tk
  text=f'{kind.title()} #{identifier}: {title} · '+format_due(due)
  self.report(text)
  popup=tk.Toplevel(self.root);popup.title('SARU · '+kind.title());popup.geometry('460x220');popup.attributes('-topmost',True)
  tk.Label(popup,text=text,font=('Segoe UI',14,'bold'),wraplength=420).pack(fill='both',expand=True,padx=12,pady=12)
  tk.Button(popup,text='Dismiss',command=popup.destroy).pack(pady=10)
  def sound():
   try:
    import winsound
    for _ in range(3 if kind=='alarm' else 1):winsound.MessageBeep();time.sleep(.6)
    if self.cfg.get('speak',True):self.speak(title)
   except Exception:pass
  threading.Thread(target=sound,daemon=True).start()
 def close(self):
  if self.closed:return
  self.closed=True
  if self.job:self.root.after_cancel(self.job)
  for window in (self.camera,self.voices):
   if window and window.winfo_exists():window.destroy()
  self.reminders.close();self.outbox.close()
