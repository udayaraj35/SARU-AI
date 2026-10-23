"""App launch results require visible-window evidence; never claim blanket success."""
import time
from app_catalog import launch_entry
from app_windows import visible_windows,match_windows,shortcut_target

def launch_and_verify(entry,launcher=launch_entry,windows=visible_windows,clock=time.monotonic,pause=time.sleep,timeout=8):
 pid=launcher(entry)
 try:target=shortcut_target(entry)
 except Exception:target=''
 deadline=clock()+timeout
 while True:
  matches=match_windows(entry,windows(),target)
  if matches:return {'state':'opened','app':entry.title,'windows':matches,'pid':pid}
  if clock()>=deadline:return {'state':'requested','app':entry.title,'windows':[],'pid':pid}
  pause(.25)
