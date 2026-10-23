"""Fast local application lookup; slow Store discovery is cached and prewarmed."""
import threading
import time
from app_catalog import installed_apps,match_entries,_unique_entries


class ApplicationIndex:
 def __init__(self,loader=installed_apps,clock=time.monotonic,ttl=300):
  self.loader=loader;self.clock=clock;self.ttl=ttl;self.quick=None;self.full=None
  self.quick_at=float('-inf');self.full_at=float('-inf');self.lock=threading.RLock()
 def warm(self):
  with self.lock:
   if self.full is not None and self.clock()-self.full_at<self.ttl:return
   entries=self.loader(include_registered=True)
   self.full=entries;self.full_at=self.clock()
 def resolve(self,name,extra=None):
  # A warm Store scan must never block an already discoverable desktop app.
  if self.quick is None or self.clock()-self.quick_at>=self.ttl:
   self.quick=self.loader(include_registered=False);self.quick_at=self.clock()
  matches=match_entries(name,_unique_entries(self.quick,extra))
  if matches:return matches
  cached=self.full
  if cached is not None and self.clock()-self.full_at<self.ttl:
   return match_entries(name,_unique_entries(cached,extra))
  self.warm()
  return match_entries(name,_unique_entries(self.full or [],extra))


application_index=ApplicationIndex()

def warm_application_index():
 try:
  application_index.quick=installed_apps(include_registered=False)
  application_index.quick_at=time.monotonic()
  application_index.warm()
 except Exception:pass  # Requests still get their own concrete lookup/error.
