"""Explicit voice/text tasks routed to existing media and social executors."""
import re

YOUTUBE=r'(?:youtube|युट्युब|यूट्यूब|युट्यूब)'
WHATSAPP=r'(?:whatsapp|whats\s+app|व्हाट्सएप|ह्वाट्सएप|वाट्सएप)'
PLAY=r'(?:play|bajau|bajaunu|chalaunu|chalau|kholnu|khola|खोल|खोल्नु|खोल्नुहोस्|चलाऊ|चलाउनुहोस्|बजाऊ|बजाउनुहोस्)'

def task_shortcut(text):
 from voice_gate import strip_address
 q=strip_address(str(text)).strip()
 q=re.sub(r'^(?:please|कृपया)\s+','',q,flags=re.I)
 # Explicit channel and recipient delimiters keep contact names/message bodies intact.
 patterns=[
  r'(?:send|write|draft)\s+(?:a\s+)?(?:whatsapp|whats app)\s+(?:message\s+)?to\s+([^:\n]{1,100}):\s*([\s\S]{1,3000})',
  WHATSAPP+r'\s+(?:ma|मा)\s+(.{1,100}?)\s+(?:lai|लाई)\s*:\s*([\s\S]{1,3000})',
  WHATSAPP+r'\s+(?:ma|मा)\s+(.{1,100}?)\s+(?:lai|लाई)\s+(.{1,3000}?)\s+(?:(?:message|msg|मेसेज|म्यासेज|सन्देश)\s+)?(?:pathau|pathaunu|pathaidinu|pathaideu|पठाऊ|पठाउनुहोस्|पठाइदेऊ)',
 ]
 for pattern in patterns:
  m=re.fullmatch(pattern,q,re.I)
  if m:
   target,body=m[1].strip(),m[2].strip()
   if target and body:return 'backend',('social',{'platform':'whatsapp','action':'send','target':target,'text':body})
 for pattern in (
  YOUTUBE+r'\s*(?:ma|मा)\s+(.{1,400}?)\s+'+PLAY,
  r'(?:play|open)\s+(.{1,400}?)\s+(?:on|in)\s+'+YOUTUBE,
  r'(?:play|open)\s+'+YOUTUBE+r'\s+(?:video\s+)?(.{1,400})',
 ):
  m=re.fullmatch(pattern,q,re.I)
  if m:return 'media_search',m[1].strip()
 # Follow-up input remains locked to the app selected in PC Control.
 m=re.fullmatch(r'(?:current app|selected app|अहिलेको एप)\s*:?\s+(.+)',q,re.I)
 if m:
  from pc_input import input_intent
  command=input_intent(m[1],task=True)
  if command:return 'desktop_input',command
 return None
