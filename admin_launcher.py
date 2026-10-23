"""Optional owner-requested administrator launch through the normal Windows UAC prompt.

No UAC policy, credentials, tasks, services or startup preferences are modified.
"""
from pathlib import Path
import ctypes
import os
import subprocess


def launch_admin(root=None, shell_execute=None):
 root=Path(root or Path(__file__).resolve().parent).resolve()
 python=root/'.venv'/'Scripts'/'pythonw.exe'
 entry=root/'launch_saru.py'
 if not python.is_file() or not entry.is_file():
  raise FileNotFoundError('Install SARU first: its private Python runtime and launcher are required.')
 if python.is_symlink() or entry.is_symlink():raise ValueError('Linked launch files are not supported.')
 if shell_execute is None:
  if os.name!='nt':raise RuntimeError('Administrator launch requires Windows.')
  shell_execute=ctypes.windll.shell32.ShellExecuteW
  shell_execute.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_int]
  shell_execute.restype=ctypes.c_void_p
 result=shell_execute(None,'runas',str(python),subprocess.list2cmdline([str(entry)]),str(root),1)
 if not result or result<=32:
  raise RuntimeError('Administrator launch was not accepted (Windows code '+str(result or 0)+'). Approve the Windows UAC prompt or continue with normal SARU. No security settings were changed.')
 return 'Windows accepted the administrator launch request. This does not confirm app startup or PC input; check the SARU window.'


if __name__=='__main__':
 try:print(launch_admin())
 except Exception as exc:
  import sys
  if sys.stderr:print(str(exc),file=sys.stderr)
  else:
   import tkinter as tk
   from tkinter import messagebox
   window=tk.Tk();window.withdraw();messagebox.showerror('SARU Administrator',str(exc));window.destroy()
  raise SystemExit(1)
