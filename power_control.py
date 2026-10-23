"""Allowlisted Windows power requests. Never called during startup."""
import ctypes
import os
from pathlib import Path
import subprocess


def power_intent(text):
 q=' '.join(text.casefold().strip().rstrip('.!?।').split())
 aliases={
 'shutdown':('shutdown pc','shut down pc','shutdown computer','turn off pc','turn off computer','pc off gara','pc off garnu','pc banda gara','computer banda gara','पीसी बन्द गर','कम्प्युटर बन्द गर','pc बन्द गर'),
 'lock':('lock pc','lock computer','lock my pc','pc lock gara','pc lock garnu','pc luck gara','पीसी लक गर','कम्प्युटर लक गर','pc लक गर'),
 'sleep':('sleep pc','sleep computer','put pc to sleep','put computer to sleep','sleep mode','pc sleep gara','pc sleep ma rakha','pc sleep mode ma rakha','sleep ma rakha','slip mood ma rakha','स्लीप मोडमा राख','पीसी स्लीपमा राख'),
 'cancel_shutdown':('cancel shutdown','abort shutdown','shutdown cancel gara','बन्द गर्ने रद्द गर')}
 for action,phrases in aliases.items():
  if q in phrases:return action
 return None


def native_lock():
 fn=ctypes.WinDLL('user32',use_last_error=True).LockWorkStation
 fn.argtypes=[];fn.restype=ctypes.c_int
 if not fn():raise ctypes.WinError(ctypes.get_last_error())


def native_sleep():
 import win32api,win32con,win32security
 token=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_ADJUST_PRIVILEGES|win32con.TOKEN_QUERY)
 try:
  luid=win32security.LookupPrivilegeValue(None,'SeShutdownPrivilege')
  previous=win32security.AdjustTokenPrivileges(token,False,[(luid,win32con.SE_PRIVILEGE_ENABLED)])
  try:
   fn=ctypes.WinDLL('powrprof',use_last_error=True).SetSuspendState
   fn.argtypes=[ctypes.c_ubyte,ctypes.c_ubyte,ctypes.c_ubyte];fn.restype=ctypes.c_ubyte
   if not fn(False,False,False):raise ctypes.WinError(ctypes.get_last_error())
  finally:win32security.AdjustTokenPrivileges(token,False,previous)
 finally:token.Close()


def request_power(action,runner=None,lock=None,sleep=None):
 if action not in ('shutdown','lock','sleep','cancel_shutdown'):raise ValueError('Unsupported power action')
 if os.name!='nt':raise RuntimeError('Windows power controls require Windows.')
 if action=='lock':
  (lock or native_lock)();return 'Windows lock requested.'
 if action=='sleep':
  (sleep or native_sleep)();return 'Windows sleep request completed; the PC may have resumed.'
 exe=str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32'/'shutdown.exe')
 args=[exe,'/a'] if action=='cancel_shutdown' else [exe,'/s','/t','30']
 result=(runner or subprocess.run)(args,capture_output=True,text=True,timeout=10,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if result.returncode:raise RuntimeError((result.stderr or result.stdout or 'Windows rejected the power request.').strip())
 return 'Shutdown cancelled.' if action=='cancel_shutdown' else 'Windows shutdown scheduled in 30 seconds. Say cancel shutdown to cancel. Save your work now.'
