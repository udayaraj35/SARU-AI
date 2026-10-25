"""A per-utterance wake phrase, not speaker identity or biometric verification."""
import re
NAME=r'(?:saru|saaru|सारु|सारू|सरु|सरू|एस\s*ए(?:\s*ए)?\s*आर\s*यू|S\s+A(?:\s+A)?\s+R\s+U)'
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
