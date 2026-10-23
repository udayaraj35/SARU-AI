"""Normalize explicit app-opening requests; do not interpret ordinary conversation."""
import re

ALIASES={'क्रोम':'chrome','गुगल क्रोम':'google chrome','नोटप्याड':'notepad','नोटपैड':'notepad','क्याल्कुलेटर':'calculator','क्यालकुलेटर':'calculator','क्याल्कुलेटर एप':'calculator','फेसबुक':'facebook','व्हाट्सएप':'WhatsApp','ह्वाट्सएप':'WhatsApp','वाट्सएप':'WhatsApp','व्हाट्सएप':'WhatsApp','युट्युब':'youtube','यूट्यूब':'youtube','जीमेल':'gmail','एज':'edge','भिएस कोड':'Visual Studio Code','वीएस कोड':'Visual Studio Code'}
VERB=r'(?:खोलिदिनुहोस्|खोलिदिनुहोस|खोलिदिनुस्|खोलिदिनुस|खोल्नुहोस्|खोल्नुहोस|खोल्नुस्|खोल्नुस|खोलिदिन्छौ|खोलिदेऊ|खोलिदेउ|खोलिदे|खोलिदिनु|खोल्नु|खोला|खोल|चलाउनुहोस्|चलाउनुस्|चलाऊ|kholnuhos|kholnuhosh|kholnus|kholidinus|kholidinu|kholideuna|kholideu|kholnu|khola|khol|open\s+(?:gara|garnu|gardinu|gardinus))'

def normalize_launch(text):
 q=text.strip().rstrip('.!?।').strip()
 if re.match(r"^(?:remember|save note|write note|search|youtube search|do not|don't|never|I said|I wrote)\b",q,re.I):return text
 q=re.sub(r'^(?:oh|okay|ok|achha|अच्छा)[,\s]+','',q,flags=re.I)
 q=re.sub(r'^(?:mere|meray|merey)\s+(?:pc|computer)\s+(?:mein|me|mai)\s+(?:(?:bhago|bhako|bhayko|vayko|bhayeko|jo\s+hai)\s+)?','',q,flags=re.I)
 # Hindi/Romanized voice transcription: retain the app name, normalize only
 # an anchored command ending. Never interpret a mention inside a sentence.
 q=re.sub(r'\s+(?:ni|bhi|pani)\s+(?=open\s+(?:kar|karo|kara))',' ',q,flags=re.I)
 q=re.sub(r'\s+open\s+(?:kar\s+(?:do|de|dena|dijiye)|kara|karo|karna)$',' kholnu',q,flags=re.I)
 q=re.sub(r'\s+(?:भी|पनि)\s+(?=(?:ओपन|खोल))',' ',q)
 q=re.sub(r'ओपन\s+(?:कर\s+दो|करो|करना)$','खोल',q)
 # Spoken Nepali often uses a dative particle and the English loan verb.
 # Keep this anchored to an explicit final opening verb, not casual mentions.
 q=re.sub(r'\s+(?:त|न|ना|है|होला|सर)\s*$','',q,flags=re.I)
 q=re.sub(r'\s+(?:लाई|लाइ)\s+(?=(?:ओपन|खोल|चलाउ))',' ',q)
 q=re.sub(r'ओपन\s+(?:गरिदिनुहोस्|गरिदिनुस्|गरिदेऊ|गरिदेउ|गर्नुहोस्|गर्नुस्|गर्नु|गर)$','खोल',q)
 q=re.sub(r'^(?:सर[, ]+|boss[, ]+|sir[, ]+|मेरो\s+(?:पीसी|कम्प्युटर)\s*मा\s*(?:भएको\s*)?|mero\s+pc\s+ma\s+(?:vayeko\s+|vayko\s+|bhayeko\s+)?)','',q,flags=re.I)
 q=re.sub(r'\s+(?:न|ना|है|होला|सर|please|na)\s*$','',q,flags=re.I)
 match=re.fullmatch(r'(?:open|launch|start)\s+(.+)',q,re.I) or re.fullmatch(r'(.+?)\s+'+VERB,q,re.I) or re.fullmatch(VERB+r'\s+(.+)',q,re.I)
 if not match:return text
 name=match[1].strip().strip('"“”\'')
 installed=bool(re.search(r'(?:\bapp\b|\bapplication\b|एप|ऐप)',name,re.I))
 name=re.sub(r'^(?:the\s+|an?\s+|my\s+|मेरो\s+|यो\s+|एउटा\s+|कुनै\s+|mero\s+|euta\s+|kunai\s+)','',name,flags=re.I)
 name=re.sub(r'^(?:app|application|एप|ऐप)\s+','',name,flags=re.I).strip()
 suffix=re.fullmatch(r'(.+?)\s+(?:app|application|एप|ऐप)',name,re.I)
 if suffix:
  known=set(ALIASES)|{value.casefold() for value in ALIASES.values()}|{'word','excel','powerpoint','spotify','discord','telegram','calculator','notepad','chrome','edge','whatsapp','facebook','youtube','gmail'}
  if suffix[1].casefold() in known:name=suffix[1]
  else:installed=False
 if name.casefold() in ('app','apps','application','applications','एप','एपहरू','ऐप','installed apps','installed app') or not name:return 'open installed apps'
 name=ALIASES.get(name.casefold(),name)
 return ('launch installed ' if installed else 'open ')+name
