"""Explicit section shortcuts to existing SARU callbacks, with no guessed clicks."""
import re
from ui_control import normalized

SECTIONS={
 'home':('home','dashboard','होम'), 'chat':('chat','च्याट'),
 'Voice: push to talk':('voice mode','voice','भ्वाइस मोड'),
 'PC Commands':('pc control','पीसी कन्ट्रोल'),
 'tools':('apps and tools','apps tools','app and tools','tools','एप र टुल्स'),
 'Task Console':('automation','अटोमेसन'),
 'Files: summarize':('files and documents','file and document','files','documents','फाइल'),
 'YouTube Player':('media','मिडिया','video player'),
 'Web search':('web search','google search','वेब सर्च'),
 'Website Studio':('website studio','web studio','वेबसाइट स्टुडियो'),
 'Social Media':('social media','सोसल मिडिया'),
 'SARU Office':('saru office','office','अफिस'),
 'controls':('device controls','device control','audio display control'),
 'Settings':('settings','setting','सेटिङ','सेटिङ्स'),
 'weather':('weather','मौसम'), 'Owner Profile':('owner profile','profile','प्रोफाइल'),
 'Saved memory':('memory','saved memory','मेमोरी'),
 'Clock country':('clock country','country list','timezone'),
 'API Manager':('model','models','ai model','voice model','मोडेल'),
}
TABS={'voice':'Voice','appearance':'Appearance','design':'Appearance','memory':'Memory','security':'Security','updates':'Updates','tools':'Tools','ai api':'AI & API','pc audio':'PC & Audio'}

def navigation_intent(text):
 q=text.strip().rstrip('.!?।')
 m=re.fullmatch(r'(?:open|show|go to)\s+(.{1,100})',q,re.I) or re.fullmatch(r'(.{1,100}?)\s+(?:kholnu|kholnuhos|khola|kholideu|dekhaunu|dekhau|खोल|खोल्नु|खोल्नुहोस्|देखाऊ)',q,re.I)
 if not m:return None
 target=normalized(m[1])
 tab=re.fullmatch(r'(.+?) (?:settings|setting|सेटिङ)',target) or re.fullmatch(r'settings (?:ko )?(.+)',target)
 if tab and tab[1] in TABS:return 'settings_tab',TABS[tab[1]]
 for key,aliases in SECTIONS.items():
  if target in {normalized(a) for a in (key,*aliases)}:return 'navigation',key
 return None
