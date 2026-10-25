"""Allowlisted SARU controls, independent of cloud chat and arbitrary code."""
import re

def system_intent(text):
 q=text.casefold().strip().rstrip('.!?।')
 if q in ('chat open gara','chat open garnu','chat khola','chat kholnu','chat kholideu','show chat','च्याट खोल','च्याट खोल्नुहोस्','च्याट खोलिदेऊ'):return ('page','chat')
 if q in ('close chat','hide chat','chat banda gara','chat banda garnu','chat बन्द गर','च्याट बन्द गर','च्याट लुकाऊ'):return ('chat','hide')
 exact={'fill password locally':('browser','fill_password'),'enter password locally':('browser','fill_password'),'open browser':('browser','open'),'control saru browser':('browser','control'),'open saru browser':('browser','open'),'saru browser':('browser','open'),'browser back':('browser','back'),'browser forward':('browser','forward'),'browser reload':('browser','reload'),'browser new tab':('browser','new_tab'),'browser close tab':('browser','close_tab'),'browser zoom in':('browser','zoom_in'),'browser zoom out':('browser','zoom_out'),'close saru browser':('browser','close'),'watch screen':('screen_watch','start'),'start screen view':('screen_watch','start'),'screen heri rakha':('screen_watch','start'),'स्क्रिन हेरिराख':('screen_watch','start'),'stop screen view':('screen_watch','stop'),'screen herna banda gara':('screen_watch','stop'),'स्क्रिन हेर्न बन्द गर':('screen_watch','stop'),'settings':('settings',None),'open settings':('settings',None),'सेटिङ खोल्नुहोस्':('settings',None),'सेटिङ खोल':('settings',None),
 'office view':('view','office'),'assistant view':('view','assistant'),'home view':('view','assistant'),'dashboard':('view','assistant'),
 'full screen':('window','fullscreen'),'fullscreen':('window','fullscreen'),'फुल स्क्रिन गर':('window','fullscreen'),'exit full screen':('window','normal'),'normal screen':('window','normal'),
 'minimize saru':('window','minimize'),'maximize saru':('window','maximize'),'saru lai sano gara':('window','minimize'),'saru lai thulo gara':('window','maximize'),
 'start listening':('voice','start'),'start voice':('voice','start'),'सुन्न सुरु गर':('voice','start'),'stop listening':('voice','stop'),'stop voice':('voice','stop'),'सुन्न बन्द गर':('voice','stop'),
 'mute mic':('voice','mute'),'unmute mic':('voice','unmute'),'show controls':('controls','show'),'hide controls':('controls','hide'),
 'capture screen':('screen','capture'),'स्क्रिन क्याप्चर गर':('screen','capture'),'next step':('screen','plan'),'अर्को स्टेप':('screen','plan'),'propose next action':('screen','plan'),'read screen':('screen','read'),'list windows':('screen','windows'),
 'use new photo':('portrait','new'),'new photo':('portrait','new'),'नयाँ फोटो राख':('portrait','new'),'naya photo rakhnu':('portrait','new'),'use original photo':('portrait','original')}
 exact.update({'controls':('control_help',None),'browser':('browser','open'),'saru controls':('control_help',None),'show saru controls':('control_help',None),'open chat':('page','chat'),'open owner profile':('page','profile'),'open social media':('page','social'),'open video studio':('page','video'),'open repository skills':('page','skills'),'open update center':('page','updates'),'show floating saru':('orb_visible',True),'hide floating saru':('orb_visible',False),'enable auto listening':('auto_listen',True),'disable auto listening':('auto_listen',False),'remember conversations':('remember_conversations',True),'stop remembering conversations':('remember_conversations',False),'enable animations':('reduced_motion',False),'disable animations':('reduced_motion',True),'speak replies':('speak',True),'silent replies':('speak',False),'romantic mode':('companion_style','Warm romantic'),'friendly mode':('companion_style','Friendly'),'professional mode':('companion_style','Professional'),'generate saru update':('edit','generate'),'apply saru update':('edit','apply'),'rollback saru update':('edit','rollback')})
 exact.update({
 'open saru':('lifecycle','show'),'show saru':('lifecycle','show'),'open yourself':('lifecycle','show'),'आफ्नो एप खोल':('lifecycle','show'),'aafno app khola':('lifecycle','show'),
 'hide saru':('lifecycle','hide'),'hide yourself':('lifecycle','hide'),'आफूलाई लुकाऊ':('lifecycle','hide'),
 'close saru':('lifecycle','exit'),'exit saru':('lifecycle','exit'),'close yourself':('lifecycle','exit'),'quit saru':('lifecycle','exit'),'आफ्नो एप बन्द गर':('lifecycle','exit'),'aafno app banda gara':('lifecycle','exit'),
 'restart saru':('lifecycle','restart'),'restart yourself':('lifecycle','restart'),'आफूलाई रिस्टार्ट गर':('lifecycle','restart'),'आफ्नो एप रिस्टार्ट गर':('lifecycle','restart'),'aafno app restart gara':('lifecycle','restart'),
 'close settings':('lifecycle','home'),'settings banda gara':('lifecycle','home'),'सेटिङ बन्द गर':('lifecycle','home'),'back home':('lifecycle','home'),'go home':('lifecycle','home'),
 'close current panel':('lifecycle','close_panel'),'close saru panel':('lifecycle','close_panel'),'close improvement studio':('lifecycle','close_improvement'),
 'update status':('edit','status'),'saru update status':('edit','status'),'self improvement status':('edit','status'),'improvement status':('edit','status'),'सुधारको अवस्था देखाऊ':('edit','status'),
 'generate improvement':('edit','generate'),'सुधार प्रस्ताव बनाऊ':('edit','generate'),'update proposal banau':('edit','generate'),
 'apply reviewed update':('edit','apply'),'समीक्षा गरेको सुधार लागू गर':('edit','apply'),'rollback saru update':('edit','rollback'),'सुधार फिर्ता गर':('edit','rollback')})
 if q in exact:return exact[q]
 setting=re.fullmatch(r'(floating size|floating text size|floating opacity|speech speed) (\d{2,3})',q)
 if setting:
  key,low,high={'floating size':('orb_size',48,240),'floating text size':('orb_text_size',10,22),'floating opacity':('orb_opacity',35,100),'speech speed':('voice_rate',80,300)}[setting[1]]
  value=int(setting[2])
  if low<=value<=high:return key,(value/100 if key=='orb_opacity' else value)
  return 'invalid_setting',f'{setting[1]} must be {low}–{high}.'
 files=re.fullmatch(r'(?:saru )?update files (.{1,600})',text,re.I)
 if files:return 'edit_files',[name.strip() for name in files[1].split(',') if name.strip()]
 request=re.fullmatch(r'(?:saru )?update request (.{1,4000})',text,re.I)
 if request:return 'edit_request',request[1]
 tab=re.fullmatch(r'browser tab (\d{1,2})',q)
 if tab:return 'browser_tab',int(tab[1])
 match=re.fullmatch(r'(?:choose window|select window|window छान)\s+(\d{1,2})',q)
 if match:return 'screen_window',int(match[1])
 match=re.fullmatch(r'(?:screen task|pc task|स्क्रिनको काम)\s+(.{1,4000})',text,flags=re.I)
 if match:return 'screen_task',match[1]
 if q in ('photo thulo gara','फोटो ठूलो बनाऊ','फोटो ठूलो गर'):return 'photo_size',110
 if q in ('photo sano gara','फोटो सानो गर'):return 'photo_size',80
 if q in ('saru ko photo naya rakha','सारुको फोटो नयाँ राख','naya photo rakhnu'):return 'portrait','new'
 match=re.fullmatch(r'(?:(?:ko|को|saru ko|सारुको)\s+)?(?:theme|theam|थिम|रङ|रंग)\s+(.+?)\s+(?:gara|banau|banaunu|गर|बनाऊ|राख)',q)
 if match:q='theme '+match[1]
 match=re.fullmatch(r'(?:theme|set theme|change theme to|थिम)\s+(.+)',q)
 if match:
  themes={'pink':'Neon Rose','neon rose':'Neon Rose','purple':'Cyber Violet','cyber violet':'Cyber Violet','blue':'Ocean Cyan','ocean cyan':'Ocean Cyan','green':'Emerald Night','emerald night':'Emerald Night','नीलो':'Ocean Cyan','गुलाबी':'Neon Rose'}
  if match[1] in themes:return 'theme',themes[match[1]]
 match=re.fullmatch(r'(?:photo size|portrait size|फोटो साइज)\s+(\d{2,3})',q)
 if match and 60<=int(match[1])<=110:return 'photo_size',int(match[1])
 match=re.fullmatch(r'(?:text size|font size|टेक्स्ट साइज)\s+(\d{2,3})',q)
 if match and 90<=int(match[1])<=140:return 'text_size',int(match[1])
 return None
