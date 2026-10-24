"""Cached Internet reachability checks, separate from adapter link state."""
import threading,time
import requests

class InternetStatus:
 def __init__(self,session=requests,clock=time.monotonic,interval=30):
  self.session=session;self.clock=clock;self.interval=interval;self.next_check=0;self.result={'internet_online':None,'internet_detail':'Checking Internet connection…'};self.lock=threading.Lock()
 def snapshot(self):
  with self.lock:
   if self.clock()<self.next_check:return dict(self.result)
   online=False
   for url,expected in [('https://www.google.com/generate_204',204),('https://www.msftconnecttest.com/connecttest.txt',200)]:
    try:
     response=self.session.get(url,timeout=(2,3),allow_redirects=False)
     if response.status_code==expected and (expected==204 or response.text.strip()=='Microsoft Connect Test'):online=True;break
    except requests.RequestException:pass
   self.result={'internet_online':online,'internet_detail':'Internet connection verified' if online else 'Internet not reachable • check Wi-Fi, captive login or connection'}
   self.next_check=self.clock()+self.interval
   return dict(self.result)

status=InternetStatus()
