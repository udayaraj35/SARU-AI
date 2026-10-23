import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from admin_launcher import launch_admin


class AdminLauncherTests(unittest.TestCase):
 def fixture(self,root):
  python=root/'.venv'/'Scripts'/'pythonw.exe';python.parent.mkdir(parents=True);python.touch()
  (root/'launch_saru.py').touch()
  return python
 def test_only_fixed_local_launcher_requests_normal_uac(self):
  with tempfile.TemporaryDirectory(prefix='SARU test ') as folder:
   root=Path(folder).resolve();python=self.fixture(root);shell=Mock(return_value=42)
   self.assertIn('accepted',launch_admin(root,shell))
   args=shell.call_args.args
   self.assertEqual(args[:3],(None,'runas',str(python)))
   self.assertIn('launch_saru.py',args[3]);self.assertEqual(args[4],str(root))
 def test_denial_is_not_success_and_never_retries(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);self.fixture(root);shell=Mock(return_value=5)
   with self.assertRaises(RuntimeError):launch_admin(root,shell)
   shell.assert_called_once()
 def test_missing_installation_never_requests_elevation(self):
  with tempfile.TemporaryDirectory() as folder:
   shell=Mock()
   with self.assertRaises(FileNotFoundError):launch_admin(folder,shell)
   shell.assert_not_called()

if __name__=='__main__':unittest.main()
