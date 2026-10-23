"""One desktop SARU shortcut, preserving the owner's optional UAC launch mode."""
from pathlib import Path
import datetime
import shutil


def consolidate_desktop_shortcut(shell,target,desktop):
 target=Path(target).resolve();desktop=Path(desktop).resolve()
 primary=desktop/'SARU AI.lnk';legacy=desktop/'SARU AI - Administrator.lnk'
 python=target/'.venv'/'Scripts'/'pythonw.exe';admin=target/'admin_launcher.py'
 def known_admin(path):
  if not path.is_file() or path.is_symlink():return False
  link=shell.CreateShortcut(str(path))
  return str(link.TargetPath).casefold()==str(python).casefold() and str(link.Arguments).strip().strip('"').casefold()==str(admin).casefold()
 primary_admin=known_admin(primary);legacy_admin=known_admin(legacy)
 elevated=primary_admin or legacy_admin
 if elevated and not admin.is_file():raise FileNotFoundError('Administrator launcher missing; shortcuts left unchanged.')
 link=shell.CreateShortcut(str(primary))
 link.TargetPath=str(python if elevated else target/'Start SARU AI.cmd')
 link.Arguments='"'+str(admin)+'"' if elevated else ''
 link.WorkingDirectory=str(target);link.IconLocation=str(target/'saru.ico')+',0'
 link.Description='SARU AI — Windows administrator consent required' if elevated else 'SARU AI personal assistant'
 link.Save()
 check=shell.CreateShortcut(str(primary))
 if str(check.TargetPath).casefold()!=str(link.TargetPath).casefold() or check.Arguments!=link.Arguments:raise RuntimeError('Primary shortcut verification failed; duplicate left intact.')
 if legacy_admin:
  if legacy.resolve().parent!=desktop:raise ValueError('Unexpected duplicate shortcut location.')
  backup=target/'.saru-backups'/'shortcuts'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
  backup.mkdir(parents=True,exist_ok=False);shutil.copy2(legacy,backup/legacy.name)
  legacy.unlink()
 return {'primary':str(primary),'administrator':elevated,'duplicate_removed':legacy_admin}
