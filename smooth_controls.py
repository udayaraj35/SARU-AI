"""Latest-value device writes in a crash-isolated, reusable native helper."""
import json
from pathlib import Path
from queue import Queue,Empty
import subprocess
import sys
import threading

class DeviceClient:
 def __init__(self):self.process=None;self.responses=Queue();self.closed=False;self.start_lock=threading.Lock()
 def start(self):
  with self.start_lock:
   if self.closed:raise RuntimeError('Device controls closed.')
   if self.process and self.process.poll() is None:return
   python=Path(sys.executable)
   if python.name.lower()=='pythonw.exe':python=python.with_name('python.exe')
   self.responses=Queue();responses=self.responses
   self.process=subprocess.Popen([str(python),'-u',str(Path(__file__).with_name('pc_telemetry.py')),'serve'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   process=self.process
   def read():
    try:
     for line in process.stdout:
      try:responses.put(json.loads(line))
      except ValueError:continue
    finally:responses.put({'error':'Windows device helper stopped. Try the control again.'})
   threading.Thread(target=read,daemon=True).start()
 def set(self,name,value):
  self.start()
  try:
   self.process.stdin.write(json.dumps({'name':name,'value':value})+'\n');self.process.stdin.flush()
   result=self.responses.get(timeout=8)
  except (OSError,Empty):
   self.terminate();raise RuntimeError('Device did not respond. Check Windows device support and retry.') from None
  if 'error' in result:raise RuntimeError(result['error'])
  return result
 def terminate(self):
  if self.process and self.process.poll() is None:
   try:self.process.terminate()
   except OSError:pass
 def close(self):
  with self.start_lock:self.closed=True;self.terminate()

class LatestControls:
 def __init__(self,client=None):
  self.client=client or DeviceClient();self.lock=threading.Lock();self.pending={};self.events=Queue();self.wake=threading.Event();self.closed=False;self.serial=0
  self.worker=threading.Thread(target=self.run,daemon=True);self.worker.start()
 def set(self,name,value):
  if name not in ('volume','brightness','mic_gain','mute'):raise ValueError('Unsupported control')
  value=max(0,min(100,int(value)))
  with self.lock:
   if self.closed:raise RuntimeError('Controls closed')
   self.serial+=1;version=self.serial;self.pending[name]=(version,value)
  self.wake.set();return version
 def run(self):
  while True:
   self.wake.wait()
   with self.lock:
    if self.closed:return
    if not self.pending:self.wake.clear();continue
    name=next(iter(self.pending));version,value=self.pending.pop(name)
   try:result=self.client.set(name,value);self.events.put((name,version,result,None))
   except Exception as exc:self.events.put((name,version,None,str(exc)))
 def close(self):
  with self.lock:self.closed=True;self.pending.clear()
  self.wake.set();self.client.close()
