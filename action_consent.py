"""One explicit, expiring owner proposal shared by text and completed voice turns."""
import re,threading,time,uuid

def consent_reply(text):
 value=re.sub(r'[.!?।,]+',' ',text.casefold()).strip()
 value=re.sub(r'^(?:saru|सारु|सारू|सरु)\s+','',value).strip()
 yes={'ok','okay','yes','yes do it','do it','confirm','approve','हुन्छ','हुन्छ गर','हुन्छ गर्नुहोस्','गर','गर्नुहोस्','ल गर','ठीक छ','ठिक छ','अवश्य','hunxa','huncha','hunchha','hunxa gara','ok gara','okay gara','ho gara'}
 no={'no','cancel','cancel it','stop','never mind','हुँदैन','हुदैन','नगर्नु','नगर','रद्द गर','रोक','hudaina','hudena','nagara','cancel gara','nai'}
 return True if value in yes else False if value in no else None

class PendingActions:
 def __init__(self,clock=time.monotonic):self.clock=clock;self.lock=threading.RLock();self.pending=None
 def offer(self,description,callback,seconds=120):
  with self.lock:
   item={'id':uuid.uuid4().hex,'description':description,'callback':callback,'expires':self.clock()+seconds}
   self.pending=item;return item['id']
 def peek(self):
  with self.lock:
   if self.pending and self.pending['expires']<=self.clock():self.pending=None
   return dict(self.pending) if self.pending else None
 def consume(self,reply):
  answer=consent_reply(reply)
  if answer is None:return None
  with self.lock:
   item=self.peek()
   if not item:return None
   self.pending=None
  return item,answer
 def clear(self):
  with self.lock:self.pending=None

pending_actions=PendingActions()
