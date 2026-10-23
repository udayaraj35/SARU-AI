"""Explicit encrypted voice enrollment and uncertain local speaker comparison."""
import base64,json,threading,uuid,time
from pathlib import Path
from queue import Queue,Empty
import tkinter as tk
import numpy as np
from settings_store import WindowsProtector

class VoiceProfiles:
 def __init__(self,directory,protector=None):self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True);self.protector=protector or WindowsProtector();self.encoder=None
 def embedding(self,audio):
  from resemblyzer import VoiceEncoder,preprocess_wav
  audio=np.asarray(audio,dtype=np.float32).flatten()
  if len(audio)<16000*4 or not np.isfinite(audio).all() or np.sqrt(np.mean(audio**2))<.005:raise ValueError('Record at least 4 seconds of clear speech, not silence.')
  clean=preprocess_wav(audio,source_sr=16000)
  if len(clean)<16000*3:raise ValueError('Too little detected speech. Speak clearly for the full recording.')
  if self.encoder is None:self.encoder=VoiceEncoder(device='cpu',verbose=False)
  return self.encoder.embed_utterance(clean)
 def add(self,name,audio,cancel=None):
  if not name.strip() or len(name)>80:raise ValueError('Use a voice profile name up to 80 characters.')
  embedding=self.embedding(audio)
  if cancel and cancel():raise RuntimeError('Recording cancelled; sample not saved.')
  identifier=uuid.uuid4().hex
  pcm=(np.clip(audio,-1,1)*32767).astype('<i2').tobytes()
  payload={'name':name.strip(),'created':time.time(),'sample_rate':16000,'pcm16':base64.b64encode(pcm).decode('ascii'),'embedding':embedding.tolist()}
  path=self.directory/(identifier+'.voice');path.write_text(self.protector.protect(json.dumps(payload).encode('utf-8')),encoding='ascii');return identifier
 def profiles(self):
  rows=[]
  for path in self.directory.glob('*.voice'):
   data=json.loads(self.protector.unprotect(path.read_text(encoding='ascii')).decode('utf-8'));rows.append((path.stem,data))
  return rows
 def delete(self,identifier):
  if len(identifier)!=32 or any(c not in '0123456789abcdef' for c in identifier):raise ValueError('Invalid voice profile ID')
  (self.directory/(identifier+'.voice')).unlink()
 def match(self,audio):
  embedding=self.embedding(audio);scores=[]
  for identifier,data in self.profiles():
   other=np.asarray(data['embedding']);score=float(np.dot(embedding,other)/(np.linalg.norm(embedding)*np.linalg.norm(other)));scores.append((score,data['name']))
  scores.sort(reverse=True)
  if not scores:return 'No enrolled voices. Save a consenting speaker sample first.'
  score,name=scores[0];margin=score-scores[1][0] if len(scores)>1 else 1
  if score<.75 or margin<.05:return 'Unknown or ambiguous voice. No identity verified.'
  return f'Possible voice match: {name} (similarity {score:.2f}). Unverified; noise, recordings or another speaker can fool this comparison.'

class VoiceProfilePanel(tk.Toplevel):
 def __init__(self,root,data,consent,report,mic_free):
  super().__init__(root);self.title('SARU · Voice profiles');self.geometry('650x500');self.store=VoiceProfiles(Path(data)/'voice_profiles');self.consent=consent;self.report=report;self.mic_free=mic_free;self.events=Queue();self.busy=False;self.closed=False;self.stop_event=threading.Event();self.job=None
  tk.Label(self,text='Local voice samples · Not security verification',font=('Segoe UI',14,'bold')).pack(pady=12)
  self.name=tk.StringVar();tk.Entry(self,textvariable=self.name).pack(fill='x',padx=12)
  tk.Button(self,text='Record 12 seconds and save voice',command=self.enroll).pack(pady=8)
  tk.Button(self,text='Record 12 seconds and compare voice',command=lambda:self.record(False)).pack(pady=4)
  tk.Button(self,text='Stop recording',command=self.stop_event.set).pack(pady=4)
  self.listing=tk.Listbox(self);self.listing.pack(fill='both',expand=True,padx=12,pady=8)
  tk.Button(self,text='Delete selected saved voice',command=self.delete).pack(pady=4)
  self.status=tk.Label(self,text='Only enroll your own voice or a speaker who agrees.',wraplength=600);self.status.pack(fill='x',pady=10)
  self.bind('<Destroy>',self.cleanup,add='+');self.refresh();self.pump()
 def refresh(self):
  self.rows=self.store.profiles();self.listing.delete(0,'end')
  for identifier,data in self.rows:self.listing.insert('end',data['name']+' · '+identifier[:8])
 def enroll(self):self.record(True)
 def record(self,enroll):
  if self.busy:return
  self.stop_event.clear()
  name=self.name.get().strip()
  if enroll and not name:self.status.configure(text='Enter a consenting speaker name.');return
  def approved(attempt=0):
   if self.closed or self.busy:return
   if self.stop_event.is_set():self.status.configure(text='Recording cancelled; nothing saved.');return
   if not self.mic_free():
    if attempt>=30:raise ValueError('Live Voice microphone did not stop; no sample recorded.')
    self.status.configure(text='Stopping Live Voice before local recording…')
    self.after(250,lambda:approved(attempt+1));return
   self.busy=True;self.status.configure(text='MIC RECORDING · Speak naturally for 12 seconds · Local only')
   def worker():
    try:
     import sounddevice as sd
     chunks=[]
     with sd.InputStream(samplerate=16000,channels=1,dtype='float32') as stream:
      for _ in range(120):
       if self.stop_event.is_set():raise RuntimeError('Recording cancelled; sample was not saved.')
       chunk,overflow=stream.read(1600)
       if overflow:raise RuntimeError('Microphone overflow. Try again.')
       chunks.append(chunk[:,0].copy())
     audio=np.concatenate(chunks)
     if self.stop_event.is_set():raise RuntimeError('Recording cancelled; sample was not saved.')
     result='Voice saved locally with Windows encryption: '+name if enroll and self.store.add(name,audio,cancel=self.stop_event.is_set) else self.store.match(audio)
    except Exception as exc:result='Voice profile: '+str(exc)
    if not self.closed:self.events.put(result)
   threading.Thread(target=worker,daemon=True).start()
  self.consent(('Record and save an encrypted 12-second voice sample for '+name+'? The speaker must agree.' if enroll else 'Record 12 seconds locally and compare against saved voices? This does not grant permissions.'),approved,seconds=45)
 def delete(self):
  if self.busy or not self.listing.curselection():return
  identifier,data=self.rows[self.listing.curselection()[0]]
  def approved():
   if self.closed or self.busy:return
   self.store.delete(identifier);self.refresh();self.report('Saved voice deleted: '+data['name'])
  self.consent('Delete saved voice sample for '+data['name']+'?',approved,seconds=30)
 def pump(self):
  if self.closed:return
  try:
   result=self.events.get_nowait();self.busy=False;self.status.configure(text=result);self.refresh();self.report(result)
  except Empty:pass
  self.job=self.after(150,self.pump)
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True;self.stop_event.set()
   if self.job:self.after_cancel(self.job)
