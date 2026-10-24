"""Deterministic personal-assistant commands. No shell evaluation."""
import ast
import operator
import re

SITES={'facebook':'https://www.facebook.com/','instagram':'https://www.instagram.com/','tiktok':'https://www.tiktok.com/','youtube':'https://www.youtube.com/','whatsapp':'https://web.whatsapp.com/','gmail':'https://mail.google.com/','github':'https://github.com/','google':'https://www.google.com/','telegram':'https://web.telegram.org/','twitter':'https://x.com/'}
HELP='''Open apps/sites: youtube kholnu, whatsapp खोल्नु, open calculator, open downloads
Use an app: use Notepad: write Hello SARU; open Calculator and click 7; Notepad kholera naam lekhnu
Search: search weather in Sofia; youtube search Nepali songs; youtube ma Nepali songs khojnu
PC: use Notepad: write Hello; then pc type more text; pc click 100, 200; pc press ctrl+s; pc scroll down 3; pc stop. Input runs in the selected app without an extra approval. Coordinates are primary-screen pixels. Move mouse to a corner to stop. Visual AI proposals still require screen-sharing review.
PC settings: pc control; screenshot; system status; volume 50; brightness 70; mute; lock pc; shutdown pc; sleep pc; cancel shutdown
Camera: open camera; stop camera; camera ask where is my cup?; what am i doing
Reminders: remind me in 10 minutes to call; alarm 07:30: Wake up; show reminders; complete reminder 1
Voice profiles: save my voice as Udaya; compare my voice; voice profiles
Memory: save note Buy milk; remember My preferred language is Nepali; show notes
Files: summarize file (choose a text/code file); create folder My Work
Math: calculate (12 + 8) * 5
Own app: open saru; hide saru; close settings; restart saru; close saru (fully exits voice too)
Self improvement: improve saru <code/design change>; generate saru update; saru update status; apply saru update; rollback saru update (exact review, backup and owner verification before applying)
Media: open youtube player; play saved video <name>; pause video; next video; video volume 60; save youtube <URL> as <name>
Drafts: whatsapp to +359123456789: Hello; email to user@example.com: Subject | Body
Other messages go to your configured AI provider. Social drafts need your final Send/Publish in the site.'''

def normalize_request(command):
 """Strip polite wrappers, leaving names and message bodies intact."""
 q=command.strip()
 q=re.sub(r'^(?:hey\s+|hello[, ]+)?(?:saru|सारु|सारू|सरु)[,!:।\s]+','',q,flags=re.I).strip()
 q=re.sub(r'^(?:(?:can|could|would|will) you\s+|I want you to\s+|please\s+|कृपया\s+|मलाई\s+|malai\s+)+','',q,flags=re.I).strip()
 # Only strip trailing politeness from action requests, never stored note/draft text.
 if not re.match(r'(?:remember|save note|write note|whatsapp to|email to|search|youtube search)\s',q,re.I):
  q=re.sub(r'[, ]+(?:please|for me|mero lagi|na|है|न)[.!?।]*$','',q,flags=re.I).strip()
 return q

def parse_command(command):
 q=normalize_request(command);low=q.casefold()
 if low in ('advanced workspace','open advanced workspace','open advanced','mark lvi','open mark lvi','advanced tools'):return 'advanced_workspace',None
 if low in ('whatsapp crm','open whatsapp crm','wacrm','open wacrm','crm setup'):return 'wacrm_panel',None
 if low in ('crm contacts','crm inbox','crm status'):return 'wacrm_read',{'crm contacts':'contacts','crm inbox':'conversations','crm status':'me'}[low]
 crm_send=re.fullmatch(r'crm send to (\+[1-9]\d{7,14}):\s*(.{1,4096})',q,re.I)
 if crm_send:return 'wacrm_send',(crm_send[1],crm_send[2])
 from pc_input import input_intent
 local_input=input_intent(q)
 if local_input:return 'desktop_input',local_input
 from message_outbox import schedule_intent
 scheduled=schedule_intent(q)
 if scheduled:return scheduled
 from ui_control import ui_intent
 ui=ui_intent(q)
 if ui:return 'ui_control',ui
 if low in ('document editor','open document editor','edit pdf','pdf edit','edit word','word edit','pdf ra word edit'):return 'document_editor',None
 from personal_reminders import reminder_intent
 reminder=reminder_intent(q)
 if reminder[0]:return reminder
 if low in ('open camera','start camera','camera hera','camera kholnu','क्यामेरा खोल'):return 'camera','open'
 if low in ('stop camera','close camera','camera banda gara','क्यामेरा बन्द गर'):return 'camera','stop'
 if low in ('what am i doing','ma k gardai xu','म के गर्दै छु'):return 'camera_ask','Describe my visible activity using only the current frame. Reply in Nepali.'
 camera_query=re.fullmatch(r'(?:camera ask|camera herera bhana) (.{1,1500})',q,re.I)
 if camera_query:return 'camera_ask',camera_query[1]
 if low in ('voice profiles','open voice profiles'):return 'voice_profiles',None
 if low in ('compare my voice','recognize my voice'):return 'voice_compare',None
 enrollment=re.fullmatch(r'(?:save my voice as|enroll voice) (.{1,80})',q,re.I)
 if enrollment:return 'voice_enroll',enrollment[1]
 from power_control import power_intent
 power=power_intent(q)
 if power:return 'power',power
 from system_intents import system_intent
 control=system_intent(q)
 if control:return 'saru_control',control
 choice=re.fullmatch(r'(?:select app|choose app|app छान|एप छान)\s+(\d{1,2})',q,re.I)
 if choice:return 'select_app',int(choice[1])
 m=re.fullmatch(r'(?:use|control|open|launch)\s+([^:]{1,100}):\s*(.{1,4000})',q,re.I)
 if not m:m=re.fullmatch(r'(?:open|launch|use)\s+(.{1,100}?)\s+(?:and|ani|अनि)\s+((?:type|write|click|scroll|find|search|लेख|टाइप).{1,3900})',q,re.I)
 if not m:m=re.fullmatch(r'(.{1,100}?)\s+(?:kholera|खोलेर)\s+(.{1,4000})',q,re.I)
 if m:return 'desktop_task',(m[1].strip(),m[2].strip())
 from launch_intents import normalize_launch
 q=normalize_launch(q);low=q.casefold()
 # Explicit destination beats the default web-service shortcut.
 web=re.fullmatch(r'(?:open|launch) whatsapp (?:web|in (?:the )?browser|on (?:the )?web)',low)
 if web:return 'site','whatsapp'
 native=re.fullmatch(r'(?:open|launch) (.+?) (?:in|on) (?:my |the )?(?:pc|desktop|computer)',q,re.I) or re.fullmatch(r'(?:open|launch) (.+?) desktop',q,re.I) or re.fullmatch(r'pc ma (.+?)(?: kholnu| khola)?',q,re.I)
 if native:return 'named_app',native[1].strip()
 if low=='open installed apps':return 'app_picker',None
 if low.startswith('launch installed '):return 'named_app',q[len('launch installed '):]
 if low in ('office','saru office','open office','open saru office','office kholnu','office खोल्नु','अफिस खोल्नु'):return 'office',None
 if low in ('office status','job status','mero kam ke bhayo','mero kam ke vayo','yo kam ke bhayo','मेरो काम के भयो','यो काम के भयो'):return 'office_status',None
 for prefix in ('office task ','office job ','delegate task ','अफिसको काम '):
  if low.startswith(prefix):return 'office',q[len(prefix):].strip()
 if low in ('repository skills','skills','open skills','repo skills','skill library'):return 'repo_center',None
 m=re.fullmatch(r'(?:add repo|install repo|learn repo|repo add gara|यो रिपो थप)\s+(https://github\.com/\S+|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)',q,re.I)
 if m:return 'repo_add',m[1]
 if low.rstrip('.!?।') in ('youtube player','open youtube player','media player','open media player','saved videos','youtube player kholnu','youtube player खोल्नु','युट्युब प्लेयर खोल्नु'):return 'media_player',None
 for prefix in ('play saved video ','play saved ','saved video bajau ','सेभ गरेको भिडियो बजाऊ '):
  if low.startswith(prefix):return 'media_play',q[len(prefix):].strip()
 if low in ('pause video','video pause gara','भिडियो रोक'):return 'media_control',('pause',None)
 if low in ('play video','resume video','video bajau','भिडियो बजाऊ'):return 'media_control',('play',None)
 if low in ('next video','अर्को भिडियो'):return 'media_control',('next',None)
 if low in ('previous video','अघिल्लो भिडियो'):return 'media_control',('previous',None)
 m=re.fullmatch(r'video volume\s+(\d{1,3})\s*%?',low)
 if m:return ('media_control',('volume',int(m[1]))) if int(m[1])<=100 else ('invalid','Use a value from 0 to 100.')
 m=re.fullmatch(r'save youtube\s+(https?://\S+)(?:\s+as\s+(.+))?',q,re.I)
 if m:return 'media_save',(m[1],m[2] or '')
 m=re.fullmatch(r'(?:आफ्नो कोड सुधार|आफूलाई अपडेट गर|aafno code update gara|aafu lai update gara|aafu lai improve gara|aafno app update gara|आफूलाई सुधार गर)\s*[:：]?\s*(.*)',q,re.I)
 if m:return 'self_improve',m[1].strip() or None
 m=re.fullmatch(r'(?:change your code to|improve yourself by|update saru to)\s+(.+)',q,re.I)
 if m:return 'self_improve',m[1].strip()
 if re.fullmatch(r'(?:take|capture|grab)(?:\s+(?:a|the))?\s+(?:screenshot|screen shot)(?:\s+for me)?[.!?।]*',low) or low in ('स्क्रिनसट लेऊ','स्क्रिनसट लिनु','screen ko photo leu','screenshot linu'):return 'screenshot',None
 if low in ('show my screen','view my screen','screen dekhaunu','screen hernu','स्क्रिन देखाऊ','स्क्रिन हेर','मेरो स्क्रिन हेर'):return 'pc_control',None
 m=re.fullmatch(r'(?:set\s+)?(volume|brightness|आवाज|उज्यालो)\s*(?:to\s*)?(\d{1,3})\s*(?:%|percent|प्रतिशत)?\s*(?:gara|garnu|banau|banaideu|गर|गर्नु|बनाऊ|बनाइदेऊ)?[.!?।]*',low)
 if m:
  value=int(m[2])
  if value>100:return 'invalid','Use a value from 0 to 100.'
  return ('volume' if m[1] in ('volume','आवाज') else 'brightness'),str(value)
 # Common request variants normalize to the same allowlisted app/site action.
 low=re.sub(r'\s+(?:खोलिदेऊ|खोलिदिनु|खोलिदेउ|kholidinu|kholera deu|open gardinu)[.!?।]*$',' kholnu',low)
 q=re.sub(r'\s+(?:खोलिदेऊ|खोलिदिनु|खोलिदेउ|kholidinu|kholera deu|open gardinu)[.!?।]*$',' kholnu',q,flags=re.I)
 m=re.fullmatch(r'(?:recall|memory search|samjhana khoja)\s+(.+)',q,re.I)
 if m:return 'recall',m[1]
 if low in ('improve saru','self improve','self improvement','आफूलाई सुधार'):return 'self_improve',None
 if low.startswith('improve saru '):return 'self_improve',q[len(q)-len(low)+len('improve saru '):].strip()
 if low in ('create video','make video','video banaunu','video banaideu','youtube studio','publish video','video studio'):return 'video_studio',None
 if low in ('facebook post','post to facebook','facebook ma post gara'):return 'facebook_post',None
 if low in ('pc control','control pc','screen control','pc control kholnu','स्क्रिन कन्ट्रोल'):return 'pc_control',None
 if low in ('update check gara','check updates','update check'):return 'updates',None
 if low in ('mero wi-fi dekhaena. check gara.','mero wifi dekhaena','wifi check gara'):return 'diagnostics',None
 if low in ('help','commands','के गर्न सक्छौ','सहायता'):return 'help',None
 if low in ('show notes','my notes','memory','notes dekhaunu','मेरो नोट'):return 'notes',None
 if low in ('summarize file','read file','file padhnu','फाइल पढ्नु'):return 'summarize',None
 if low in ('mute','mute sound','आवाज बन्द'):return 'volume','0'
 m=re.fullmatch(r'(volume|brightness|आवाज|उज्यालो)\s*(?:to\s*)?(\d{1,3})\s*(?:%|percent)?\s*(?:gara|गर्नु)?',low)
 if m:
  if int(m[2])>100:return 'invalid','Use a value from 0 to 100.'
  return ('volume' if m[1] in ('volume','आवाज') else 'brightness'),m[2]
 for prefix,action in [('remember ','note'),('yaad gara ','note'),('याद गर ','note'),('calculate ','calculate'),('हिसाब ','calculate'),('youtube search ','youtube_search'),('search youtube ','youtube_search'),('search ','search'),('google search ','search'),('create folder ','folder'),('make folder ','folder'),('write note ','note'),('save note ','note'),('whatsapp to ','whatsapp'),('email to ','email')]:
  if low.startswith(prefix):return action,q[len(q)-len(low)+len(prefix):].strip()
 m=re.fullmatch(r'youtube\s+(?:ma\s+)?(.+?)\s+(?:khojnu|khoja|खोज्नु|खोज)',low)
 if m:return 'youtube_search',m[1]
 for phrase,action in [('screenshot','screenshot'),('स्क्रिनसट','screenshot'),('system status','status'),('pc status','status'),('lock pc','lock'),('lock computer','lock')]:
  if low==phrase:return action,None
 targets={**{name:('site',name) for name in SITES},'downloads':('downloads',None),'डाउनलोड':('downloads',None),'notepad':('notepad',None),'नोटप्याड':('notepad',None),'settings':('settings',None),'calculator':('app','Calculator'),'task manager':('app','Task Manager'),'chrome':('browser','chrome'),'google chrome':('browser','chrome'),'edge':('browser','edge')}
 for name,result in targets.items():
  if low.rstrip('.!?।') in (name,'open '+name,'launch '+name,'visit '+name,name+' kholnu',name+' khola',name+' खोल्नु',name+' खोल',name+' open gara',name+' khol',name+' kholideu'):return result
 m=re.fullmatch(r'(?:open|launch)\s+(.+)',q,re.I) or re.fullmatch(r'(.+?)\s+(?:kholnu|khola|kholideu|open gara|खोल्नु|खोल)',q,re.I)
 if m:return 'named_app',m[1].strip().rstrip('.!?।')
 return None,None

def calculate(expression):
 if len(expression)>200:raise ValueError('Expression is too long.')
 operations={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Mod:operator.mod}
 def value(node):
  if isinstance(node,ast.Constant) and type(node.value) in (int,float):return node.value
  if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):return value(node.operand)*(1 if isinstance(node.op,ast.UAdd) else -1)
  if isinstance(node,ast.BinOp) and type(node.op) in operations:
   result=operations[type(node.op)](value(node.left),value(node.right))
   if abs(result)>1e100:raise ValueError('Result is too large.')
   return result
  raise ValueError('Use numbers, parentheses and + - * / % only.')
 return value(ast.parse(expression,mode='eval').body)
