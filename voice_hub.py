"""Persistent voice session, independent of dashboard/settings navigation."""
from collections import deque
from queue import Queue,Empty
from live_voice import LiveVoice

class VoiceHub:
 def __init__(self,root,cfg,visual,engine_factory=LiveVoice,preferences=None):
  self.auto_enabled=bool(cfg.get('auto_listen',True));self.root=root;self.cfg=cfg;self.visual=visual;self.factory=engine_factory;self.preferences=preferences;self.engine=None;self.events=Queue(maxsize=500);self.sink=None;self.history=deque(maxlen=120);self.closed=False;self.last_error='';self.state='STOPPED';self.job=root.after(60,self.pump)
 def emit(self,kind,value):
  try:self.events.put_nowait((kind,value))
  except Exception:pass
 def start(self):
  if self.engine and self.engine.active:return
  try:
   self.last_error=''
   settings=dict(self.cfg)
   if self.preferences:settings['personal_notes']=self.preferences()
   self.engine=self.factory(settings,self.emit);self.engine.start()
  except Exception as exc:self.emit('error',str(exc));self.emit('state','ERROR')
 def send_text(self,text):
  if self.engine and self.engine.active and self.engine.send_text(text):
   self.emit('transcript',('You',text));return True
  return False
 def speak_reply(self,text):
  """Application result feedback stays in the selected Live voice, not Windows TTS."""
  if not self.cfg.get('speak',True) or not self.engine or not self.engine.active:return False
  from secret_handling import contains_secret
  if contains_secret(text) or any(isinstance(key,str) and len(key)>7 and key in text for key in self.cfg.get('keys',{}).values()):return False
  method=getattr(self.engine,'speak_reply',None)
  return bool(method(text)) if method else False
 def stop(self):
  self.last_error=''
  if self.engine:self.engine.stop()
  self.emit('state','STOPPING' if self.engine and self.engine.active else 'STOPPED')
 def toggle_mute(self):
  if self.engine and self.engine.active:self.engine.mute(not self.engine.muted.is_set())
 def pump(self):
  if self.closed:return
  try:
   for _ in range(120):
    kind,value=self.events.get_nowait()
    if kind=='conversation_turn':
     from secret_handling import contains_secret
     if contains_secret(value[0]) or contains_secret(value[1]):self.history.clear()
    if kind=='error':self.last_error=str(value)
    if kind=='state':
     if value=='STOPPED' and self.last_error:value='ERROR'
     self.state=value
    if kind=='transcript':
     from secret_handling import safe_memory_text
     value=(value[0],safe_memory_text(value[1]));self.history.append(value)
    self.visual(kind,value)
    if self.sink:self.sink(kind,value)
  except Empty:pass
  self.job=self.root.after(60,self.pump)
 def close(self):
  self.closed=True;self.stop();self.sink=None
  if self.job:
   try:self.root.after_cancel(self.job)
   except Exception:pass
