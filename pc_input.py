"""Explicit local input commands; no model output, shell, or guessed targets."""
import re
from desktop_actions import SHORTCUTS, type_unicode


def input_intent(text, task=False):
 q=text.strip()
 prefix=re.match(r'^(?:pc|desktop)\s+',q,re.I)
 if prefix:q=q[prefix.end():]
 elif not task:return None
 if q.casefold() in ('stop','cancel'):return ('stop',None)
 m=re.fullmatch(r'(click|double click|right click)\s+(\d+)\s*[, ]\s*(\d+)',q,re.I)
 if m:return (m[1].casefold(),(int(m[2]),int(m[3])))
 m=re.fullmatch(r'(?:type|write|टाइप गर|लेख)\s+(.+)',q,re.I)
 if m:return ('type',m[1])
 m=re.fullmatch(r'scroll\s+(up|down)(?:\s+([1-9]|10))?',q,re.I)
 if m:return ('scroll',(int(m[2] or 3))*(1 if m[1].lower()=='up' else -1))
 m=re.fullmatch(r'(?:press|shortcut)\s+(.+)',q,re.I)
 if m:
  aliases={name.casefold():name for name in SHORTCUTS}
  aliases.update({'+'.join(keys):name for name,keys in SHORTCUTS.items()})
  key=aliases.get(m[1].casefold())
  if key:return ('shortcut',key)
 return None


def perform_input(command, target, automation, foreground, writer=type_unicode):
 """Caller activates its selected app; refuse focus changes before each input."""
 action,value=command
 if not target or foreground()!=target:raise ValueError('Selected app lost focus. No input performed.')
 automation.FAILSAFE=True
 automation.failSafeCheck()
 if action in ('click','double click','right click'):
  x,y=value;w,h=automation.size()
  if type(x) is not int or type(y) is not int or not 0<=x<w or not 0<=y<h:raise ValueError('Coordinates must be inside the primary screen.')
  # Do not click outside the selected app window.
  import win32gui
  window=win32gui.GetAncestor(win32gui.WindowFromPoint((x,y)),2)
  if window!=target:raise ValueError('Point belongs to another window. Select that app first.')
  if foreground()!=target:raise ValueError('Selected app lost focus.')
  if action=='double click':automation.doubleClick(x,y,interval=.15)
  else:automation.click(x,y,button='right' if action=='right click' else 'left')
 elif action=='type':
  from secret_handling import contains_secret
  if not isinstance(value,str) or not 1<=len(value)<=2000 or any(ord(c)<32 for c in value):raise ValueError('Use one line of 1–2000 characters.')
  if contains_secret(value):raise ValueError('Use local masked password entry instead.')
  writer(value)
 elif action=='shortcut':
  if value not in SHORTCUTS:raise ValueError('Unsupported shortcut.')
  automation.hotkey(*SHORTCUTS[value])
 elif action=='scroll':
  if type(value) is not int or not 0<abs(value)<=10:raise ValueError('Scroll must be 1–10 steps.')
  # Mouse wheel input is delivered under the cursor on Windows.
  import win32gui
  if win32gui.GetAncestor(win32gui.WindowFromPoint(tuple(automation.position())),2)!=target:raise ValueError('Move the pointer over the selected app before scrolling.')
  automation.scroll(value)
 else:raise ValueError('Unsupported PC input.')
 return 'Local input performed; verify the new screen before your next command.'
