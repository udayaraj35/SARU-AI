"""SARU-owned browser controller. IPC is a private child stdin pipe, never a web bridge."""
import json
import re
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import urlsplit


def checked_url(value):
 value=value.strip()
 if len(value)>8192:raise ValueError('URL too long')
 if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',value) and not value.startswith(('https://','http://')):raise ValueError('Use an HTTP(S) website.')
 if '://' not in value:value='https://'+value
 parts=urlsplit(value)
 if parts.scheme not in ('https','http') or not parts.hostname or parts.username or parts.password:raise ValueError('Use an HTTP(S) URL without embedded credentials.')
 return value

class SaruBrowser:
 def __init__(self,data,report=None):self.data=Path(data);self.process=None;self.report=report or (lambda text:None);self.lock=threading.Lock()
 def command(self,action,value=None):
  if action not in ('open','back','forward','reload','new_tab','close_tab','select_tab','zoom_in','zoom_out','fill_password','close'):raise ValueError('Unsupported browser control')
  if action in ('open','new_tab'):value=checked_url(value or 'https://www.google.com/')
  if action=='fill_password' and value is not None:raise ValueError('Enter the password only in the masked local browser dialog.')
  if action=='select_tab':
   value=int(value)
   if not 1<=value<=100:raise ValueError('Tab number must be 1–100')
  with self.lock:
   if not self.process or self.process.poll() is not None:
    if action not in ('open','new_tab'):raise ValueError('Open SARU Browser first.')
    host=[sys.executable,'--saru-browser-host'] if getattr(sys,'frozen',False) else [sys.executable,str(Path(__file__).with_name('saru_browser_host.py'))]
    self.process=subprocess.Popen(host+['--data',str(self.data/'browser')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    process=self.process
    def listen():
     saw_ready=False
     for line in process.stdout:
      try:
       event=json.loads(line)
       if event.get('event')=='ready':saw_ready=True
       if event.get('event') in ('ready','error','loaded'):self.report(str(event.get('message','SARU Browser'))[:300])
      except (ValueError,TypeError):pass
     if not saw_ready:self.report('SARU Browser did not start. Check its Qt browser dependency or profile lock; no page was opened.')
    threading.Thread(target=listen,daemon=True).start()
   self.process.stdin.write(json.dumps({'action':action,'value':value})+'\n');self.process.stdin.flush()
  return 'SARU Browser request sent: '+action
