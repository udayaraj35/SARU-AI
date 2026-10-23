from pathlib import Path
import tempfile
import unittest
from shortcut_support import consolidate_desktop_shortcut


class Link:
 def __init__(self,path):self.path=path;self.TargetPath='';self.Arguments=''
 def Save(self):self.path.write_bytes(b'synthetic shortcut')

class Shell:
 def __init__(self):self.links={}
 def CreateShortcut(self,path):
  return self.links.setdefault(path,Link(Path(path)))

class ShortcutTests(unittest.TestCase):
 def fixture(self,folder):
  root=Path(folder)/'SARU';root.mkdir();(root/'admin_launcher.py').touch()
  desktop=Path(folder)/'Desktop';desktop.mkdir()
  shell=Shell();old=desktop/'SARU AI - Administrator.lnk'
  link=shell.CreateShortcut(str(old));link.TargetPath=str(root/'.venv'/'Scripts'/'pythonw.exe');link.Arguments='"'+str(root/'admin_launcher.py')+'"';link.Save()
  return root,desktop,shell,old
 def test_consolidate_and_repeat_preserves_admin_mode(self):
  with tempfile.TemporaryDirectory() as folder:
   root,desktop,shell,old=self.fixture(folder)
   result=consolidate_desktop_shortcut(shell,root,desktop)
   self.assertTrue(result['administrator']);self.assertFalse(old.exists())
   self.assertEqual(len(list(desktop.glob('*.lnk'))),1)
   self.assertEqual(len(list((root/'.saru-backups').rglob('*.lnk'))),1)
   self.assertTrue(consolidate_desktop_shortcut(shell,root,desktop)['administrator'])
 def test_foreign_duplicate_is_not_removed(self):
  with tempfile.TemporaryDirectory() as folder:
   root,desktop,shell,old=self.fixture(folder)
   shell.CreateShortcut(str(old)).TargetPath='Other Application.exe'
   result=consolidate_desktop_shortcut(shell,root,desktop)
   self.assertFalse(result['duplicate_removed']);self.assertTrue(old.exists())
 def test_missing_admin_does_not_remove_working_shortcut(self):
  with tempfile.TemporaryDirectory() as folder:
   root,desktop,shell,old=self.fixture(folder);(root/'admin_launcher.py').unlink()
   with self.assertRaises(FileNotFoundError):consolidate_desktop_shortcut(shell,root,desktop)
   self.assertTrue(old.exists())

if __name__=='__main__':unittest.main()
