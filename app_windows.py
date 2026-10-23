"""Match a launched catalog entry to visible windows without guessing a recipient."""
import re
from pathlib import Path

def normalize(text):return re.sub(r'[^\w]+',' ',text.casefold()).strip()

def match_windows(entry,windows,target_path=None):
 exact=[];named=[];name=normalize(entry.title)
 aliases={'notepad':('notepad','नोटप्याड'),'calculator':('calculator','calc'),'microsoft word':('word',),'microsoft excel':('excel',),'google chrome':('google chrome','chrome'),'microsoft edge':('microsoft edge',)}
 names=aliases.get(name,(name,))
 expected=str(target_path or (entry.target if entry.kind=='exe' else '')).casefold()
 for window in windows:
  process=window.get('exe','').casefold()
  if expected and process and process==expected:exact.append(window);continue
  title=normalize(window['title']);stem=normalize(Path(process).stem)
  if any(value and (title==value or title.endswith(' '+value) or stem==value) for value in names):named.append(window)
 return exact or named

def visible_windows():
 import psutil,win32process
 from desktop_actions import list_windows
 result=[]
 for hwnd,title in list_windows():
  pid=win32process.GetWindowThreadProcessId(hwnd)[1]
  try:exe=psutil.Process(pid).exe()
  except psutil.Error:exe=''
  result.append({'hwnd':hwnd,'title':title,'exe':exe,'pid':pid})
 return result

def shortcut_target(entry):
 if entry.kind!='shortcut':return entry.target if entry.kind=='exe' else ''
 import pythoncom,win32com.client
 pythoncom.CoInitialize()
 try:return str(win32com.client.Dispatch('WScript.Shell').CreateShortcut(entry.target).TargetPath)
 finally:pythoncom.CoUninitialize()
