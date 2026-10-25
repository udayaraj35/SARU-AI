"""A per-utterance wake phrase, not speaker identity or biometric verification."""
import re
import time
import threading
WAKE_GREETING='हजुर Boss, म के सेवा गरूँ?'


class ConversationGate:
 """Wake once, then accept current conversation until 60 seconds of idle.

 Typed notifications never open a microphone conversation. This is activation,
 not speaker authentication. Strict per-utterance mode remains available.
 """
 def __init__(self,required=True,followup=False,idle=60,clock=time.monotonic):
  self.required=required;self.followup=followup;self.idle=idle;self.clock=clock;self.until=0;self.generation=0;self.lock=threading.RLock()
 @property
 def active(self):
  with self.lock:return bool(self.required and self.followup and self.clock()<self.until)
 def authorize(self,text,typed=False):
  if not self.required:return True
  if not str(text).strip():return bool(typed)
  if addressed_to_saru(text):
   if self.followup:self.renew()
   return True
  return self.active
 def renew(self,generation=None):
  with self.lock:
   if generation is not None and generation!=self.generation:return False
   if self.required and self.followup:self.until=self.clock()+self.idle;return True
   return False
 def close(self):
  with self.lock:self.until=0;self.generation+=1
# Observed Gemini ASR drops the R in a full addressed question and emits
# uppercase "SAU, ...". Accept only that punctuated, nonempty ASR shape;
# ordinary sau/sau hundred, Sarah, Sorry and embedded names stay blocked.
NAME=r'(?:saru|saaru|सारु|सारू|सरु|सरू|एस\s*ए(?:\s*ए)?\s*आर\s*यू|S\s+A(?:\s+A)?\s+R\s+U|(?-i:SAU)(?=[,:]\s+\S))'
PREFIX=r'^\s*(?:(?:hey|hello|हे|हेलो)[,\s]+)?'+NAME+r'(?=$|[,!?:.।\s])'

def addressed_to_saru(text):
 return bool(re.match(PREFIX,text,re.I))

def strip_address(text):return re.sub(PREFIX+r'[,!?:.।\s]*','',text,count=1,flags=re.I).strip()

def wake_call(text):
 return addressed_to_saru(text) and bool(re.fullmatch(r'\s*(?:(?:hey|hello|हे|हेलो)[,\s]+)?'+NAME+r'(?:[,!?:.।\s]+(?:hello|hi|hey|हेलो|नमस्ते))?[,!?:.।\s]*',text,re.I))

def may_respond(text,required=True,typed=False):
 return not required or (addressed_to_saru(text) if text.strip() else bool(typed))


def merge_transcript(current,fragment):
 """Handle cumulative transcripts and a split wake token without duplicating text."""
 if not fragment:return current
 if not current:return fragment
 if fragment.startswith(current):return fragment
 if current.endswith(fragment):return current
 if addressed_to_saru(current) and current.strip().casefold() in ('saru','saaru','सारु','सारू','सरु') and not fragment[0].isspace() and fragment[0] not in ',!:।':return current+' '+fragment
 return current+fragment
