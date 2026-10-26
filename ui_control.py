"""Owner-requested native SARU controls. Exact labels, no arbitrary code or screen clicks."""
import hashlib,json,unicodedata
import tkinter as tk
from tkinter import ttk


def normalized(text):
 return ' '.join(''.join(c if unicodedata.category(c)[0] in 'LMN' else ' ' for c in str(text).casefold()).split())


def ui_intent(text):
 import re
 q=text.strip().rstrip('.!?।');low=q.casefold()
 if low in ('list buttons','show buttons','saru buttons','सबै बटन देखाऊ'):return 'buttons',None
 if low in ('list tabs','show tabs'):return 'tabs',None
 if low in ('list app options','show app options','list saru options'):return 'menu',None
 if low in ('list settings options','show settings options'):return 'fields',None
 own=re.fullmatch(r'(?:(?:saru\s+)?(?:ma|ko)|आफ्नो एपको|एपको)\s+(.{1,100}?)\s+(?:kholnu|khola|kholideu|खोल|खोल्नुहोस्)',q,re.I)
 if own:return 'action',own[1]
 patterns=[(r'(?:press button|click button|बटन थिच) (.{1,160})','press'),(r'(?:select tab|open tab|ट्याब खोल) (.{1,100})','tab'),(r'(?:open option|run option|(?:saru )?option|मेनु खोल) (.{1,160})','action')]
 for pattern,kind in patterns:
  m=re.fullmatch(pattern,q,re.I)
  if m:return kind,m[1]
 m=re.fullmatch(r'set option ([a-zA-Z_][a-zA-Z0-9_]*) to (.{1,250})',q,re.I)
 if m:return 'field',(m[1],m[2])
 return None

class UiControl:
 def __init__(self,root,consent,report,actions,page):self.root=root;self.consent=consent;self.report=report;self.actions=actions;self.page=page;self.listed=[]
 def widgets(self,parent=None):
  parent=parent or self.root
  if getattr(parent,'_saru_consent_ui',False):return
  for child in parent.winfo_children():
   if getattr(child,'_saru_consent_ui',False):continue
   yield child
   yield from self.widgets(child)
 def enabled(self,widget):
  try:
   if isinstance(widget,ttk.Widget) and widget.instate(['disabled']):return False
   return bool(widget.winfo_exists() and widget.winfo_viewable()) and str(widget.cget('state'))!='disabled'
  except tk.TclError:return False
 def buttons(self):
  result=[]
  for widget in self.widgets():
   if isinstance(widget,(tk.Button,ttk.Button,tk.Checkbutton,ttk.Checkbutton)) and self.enabled(widget):
    label=str(widget.cget('text')).strip() or 'Image button '+str(widget)
    result.append((label,widget))
  return result
 def snapshot(self):
  fields=[]
  for widget in self.widgets():
   try:
    if widget is getattr(self.page(),'chat_output',None):continue
    if isinstance(widget,(tk.Checkbutton,ttk.Checkbutton)) and widget.winfo_viewable():fields.append((str(widget),str(widget.getvar(widget.cget('variable')))))
    if widget.winfo_viewable() and isinstance(widget,(tk.Entry,ttk.Entry,ttk.Combobox,tk.Text)):
     value=widget.get('1.0','end') if isinstance(widget,tk.Text) else widget.get()
     # Record only a digest: entered secrets are never shown in control listings.
     fields.append((str(widget),str(value)))
   except tk.TclError:pass
  return hashlib.sha256(json.dumps(fields,ensure_ascii=False).encode()).hexdigest()
 def request(self,kind,arg=None):
  self.root.update_idletasks()
  if kind=='buttons':
   self.listed=self.buttons();return 'Available buttons:\n'+'\n'.join(f'{i+1}. {name}' for i,(name,_) in enumerate(self.listed))+'\nSay press button followed by exact label or this list number.'
  if kind=='tabs':
   return 'Available tabs:\n'+'\n'.join(str(book.tab(tab,'text')) for book in self.widgets() if isinstance(book,ttk.Notebook) and book.winfo_viewable() for tab in book.tabs() if book.tab(tab,'state')!='hidden')
  if kind=='menu':return 'SARU app options:\n'+'\n'.join(sorted(self.actions()))+'\nSay open option followed by exact label.'
  if kind=='fields':
   fields=getattr(self.page(),'fields',{})
   return 'Settings keys (changes are staged until Save settings): '+', '.join(key for key in fields if key not in ('new_key','keys','owner_pin_hash','owner_edit_hash'))
  if kind=='press':
   if str(arg).isdigit():
    index=int(arg)-1
    if not 0<=index<len(self.listed):raise ValueError('Say list buttons first, then use a listed number.')
    label,widget=self.listed[index]
   else:
    matches=[item for item in self.buttons() if normalized(item[0])==normalized(arg)]
    if len(matches)!=1:raise ValueError('Button is missing or ambiguous. Say list buttons and use its number.')
    label,widget=matches[0]
   if not self.enabled(widget):raise ValueError('Button closed, hidden or disabled. Ask for a fresh list.')
   command=str(widget.cget('command'));original_label=str(widget.cget('text'));signature=self.snapshot()
   def execute():
    if not self.enabled(widget) or str(widget.cget('command'))!=command or str(widget.cget('text'))!=original_label or self.snapshot()!=signature:raise ValueError('View/fields changed. Review this button again.')
    widget.invoke();return 'Invoked SARU button: '+label+'. Check its resulting status; any further review still applies.'
   description='Invoke this enabled SARU button: '+label+'? Existing file/account/security reviews still apply.'
  elif kind=='tab':
   matches=[(book,tab) for book in self.widgets() if isinstance(book,ttk.Notebook) and book.winfo_viewable() for tab in book.tabs() if normalized(book.tab(tab,'text'))==normalized(arg) and book.tab(tab,'state')=='normal']
   if len(matches)!=1:raise ValueError('Tab is missing or ambiguous. Say list tabs first.')
   book,tab=matches[0]
   def execute():
    if not book.winfo_exists() or not book.winfo_viewable() or tab not in book.tabs():raise ValueError('Tab view changed.')
    book.select(tab);return 'Selected SARU tab: '+str(arg)
   description='Open SARU tab: '+str(arg)+'?'
  elif kind=='action':
   matches=[(name,callback) for name,callback in self.actions().items() if normalized(name)==normalized(arg)]
   if len(matches)!=1:raise ValueError('Unknown/ambiguous app option. Say list app options.')
   label,callback=matches[0]
   def execute():
    if self.actions().get(label) is not callback:raise ValueError('App option changed. Review it again.')
    callback();return 'Invoked SARU option: '+label+'. Check its resulting status.'
   description='Run SARU app option: '+label+'? Its existing review/permission checks remain.'
  elif kind=='field':
   key,value=arg;page=self.page();fields=getattr(page,'fields',{})
   if key not in fields or key in ('new_key','keys','owner_pin_hash','owner_edit_hash'):raise ValueError('Open Settings and use a listed non-secret settings key. Enter API keys/security codes in their protected fields.')
   variable=fields[key];old=variable.get()
   def execute():
    if self.page() is not page or not page.winfo_exists() or fields[key].get()!=old:raise ValueError('Settings view/value changed. Review again.')
    if isinstance(variable,tk.BooleanVar):
     if value.casefold() not in ('true','false','on','off','yes','no'):raise ValueError('Use true/false.')
     variable.set(value.casefold() in ('true','on','yes'))
    else:variable.set(value)
    return 'Staged setting '+key+'. Use the Save settings button to validate and persist.'
   description='Stage non-secret Settings field '+key+' = '+value+'? Save settings is a separate action.'
  else:raise ValueError('Unsupported SARU UI control')
  # The exact owner command is authorization to invoke the existing UI callback.
  # Sensitive workflows retain their own intrinsic review, not an extra generic prompt.
  return execute()
