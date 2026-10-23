"""Bounded desktop input, with fresh screenshot and foreground-window checks."""
import time
from screen_tools import same_target_patch

SHORTCUTS={
 'Copy':('ctrl','c'),'Paste':('ctrl','v'),'Select all':('ctrl','a'),
 'Undo':('ctrl','z'),'Find':('ctrl','f'),'Save':('ctrl','s'),
 'Next field':('tab',),'Previous field':('shift','tab'),
 'Escape':('esc',),'Enter':('enter',),'Page down':('pagedown',),'Page up':('pageup',),
}

def validate_context(snapshot,point,captured_at,expected_window,automation,current_window):
 if time.monotonic()-captured_at>30:raise ValueError('Capture a fresh screen: preview expired after 30 seconds.')
 if current_window()!=expected_window:raise ValueError('Foreground app changed. Capture again.')
 current=automation.screenshot()
 if current.size!=tuple(automation.size()):raise ValueError('Screen scaling mismatch.')
 if not same_target_patch(snapshot,current,point):raise ValueError('Selected target changed. Capture again.')

def execute_action(action,payload,snapshot,point,captured_at,expected_window,automation,current_window,unicode_writer):
 if point is None:raise ValueError('Select a point in a fresh screenshot first.')
 if action not in ('double click','right click','scroll','type','shortcut'):raise ValueError('Unsupported input action.')
 if action=='scroll' and (type(payload) is not int or not -10<=payload<=10 or payload==0):raise ValueError('Scroll must be between -10 and 10, excluding zero.')
 if action=='type' and (not isinstance(payload,str) or not payload or len(payload)>2000 or any(ord(c)<32 for c in payload)):
  raise ValueError('Type 1–2000 characters on one line; Enter is a separate shortcut.')
 if action=='shortcut' and payload not in SHORTCUTS:raise ValueError('Choose a supported shortcut.')
 validate_context(snapshot,point,captured_at,expected_window,automation,current_window)
 automation.FAILSAFE=True
 if action=='double click':automation.doubleClick(*point,interval=0.15)
 elif action=='right click':automation.click(*point,button='right')
 elif action=='scroll':automation.moveTo(*point);automation.scroll(payload)
 elif action=='type':
  automation.click(*point)
  if current_window()!=expected_window:raise ValueError('Click changed the app. No text entered; capture again.')
  unicode_writer(payload)
 elif action=='shortcut':automation.hotkey(*SHORTCUTS[payload])
 return 'Input performed. Capture again to verify the result.'

def type_unicode(text):
 """Send UTF-16 keyboard input without touching the user's clipboard."""
 import ctypes
 from ctypes import wintypes
 class KEYBDINPUT(ctypes.Structure):
  _fields_=[('wVk',wintypes.WORD),('wScan',wintypes.WORD),('dwFlags',wintypes.DWORD),('time',wintypes.DWORD),('dwExtraInfo',ctypes.c_size_t)]
 class MOUSEINPUT(ctypes.Structure):
  _fields_=[('dx',wintypes.LONG),('dy',wintypes.LONG),('mouseData',wintypes.DWORD),('dwFlags',wintypes.DWORD),('time',wintypes.DWORD),('dwExtraInfo',ctypes.c_size_t)]
 class HARDWAREINPUT(ctypes.Structure):
  _fields_=[('uMsg',wintypes.DWORD),('wParamL',wintypes.WORD),('wParamH',wintypes.WORD)]
 class UNION(ctypes.Union):_fields_=[('ki',KEYBDINPUT),('mi',MOUSEINPUT),('hi',HARDWAREINPUT)]
 class INPUT(ctypes.Structure):_fields_=[('type',wintypes.DWORD),('u',UNION)]
 send=ctypes.WinDLL('user32',use_last_error=True).SendInput
 send.argtypes=[wintypes.UINT,ctypes.POINTER(INPUT),ctypes.c_int];send.restype=wintypes.UINT
 raw=text.encode('utf-16-le')
 for i in range(0,len(raw),2):
  import pyautogui
  pyautogui.failSafeCheck()
  unit=int.from_bytes(raw[i:i+2],'little')
  events=(INPUT*2)(INPUT(1,UNION(ki=KEYBDINPUT(0,unit,4,0,0))),INPUT(1,UNION(ki=KEYBDINPUT(0,unit,6,0,0))))
  if send(2,events,ctypes.sizeof(INPUT))!=2:raise RuntimeError('Windows blocked input. Partial text may have been entered; check before retrying.')

def list_windows():
 import win32gui,win32process,os
 result=[]
 def add(hwnd,_):
  title=win32gui.GetWindowText(hwnd)
  if title and win32gui.IsWindowVisible(hwnd) and win32process.GetWindowThreadProcessId(hwnd)[1]!=os.getpid():result.append((hwnd,title))
 win32gui.EnumWindows(add,None)
 return result

def activate_window(hwnd):
 import win32gui,win32con,win32process,win32api
 if not win32gui.IsWindow(hwnd):raise ValueError('Window closed. Refresh the window list.')
 if win32gui.IsIconic(hwnd):win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)
 try:win32gui.SetForegroundWindow(hwnd)
 except Exception:
  # A user-triggered switch can require temporarily joining the foreground
  # input thread. This does not grant elevation or input into protected UI.
  import ctypes
  foreground=win32gui.GetForegroundWindow();current=win32api.GetCurrentThreadId()
  thread=win32process.GetWindowThreadProcessId(foreground)[0] if foreground else current
  attached=False
  try:
   if thread!=current:attached=bool(ctypes.windll.user32.AttachThreadInput(current,thread,True))
   win32gui.BringWindowToTop(hwnd);win32gui.SetForegroundWindow(hwnd)
  finally:
   if attached:ctypes.windll.user32.AttachThreadInput(current,thread,False)
 if win32gui.GetForegroundWindow()!=hwnd:raise RuntimeError('Windows did not allow focus. Select the app on the taskbar, then capture again.')
