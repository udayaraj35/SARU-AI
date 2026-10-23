import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock,patch
import install_support as ins

class InstallTests(unittest.TestCase):
 def test_upgrade_preserves_user_files(self):
  with tempfile.TemporaryDirectory() as temp:
   src=Path(temp)/'source';dest=Path(temp)/'installed';src.mkdir();dest.mkdir()
   (src/'app.py').write_text('new');(src/'uninstall.ps1').write_text('script');(dest/'app.py').write_text('old');(dest/'my_document.txt').write_text('personal')
   paths=ins.copy_application(src,dest);ins.write_manifest(dest,paths)
   self.assertEqual((dest/'app.py').read_text(),'new');self.assertEqual((dest/'my_document.txt').read_text(),'personal')
   self.assertTrue(any(p.read_text()=='old' for p in (dest/'.saru-backups').rglob('app.py')))
   manifest=json.loads((dest/ins.MANIFEST).read_text());self.assertIn('uninstall.ps1',manifest['files']);self.assertNotIn('my_document.txt',manifest['files'])
 def test_parent_and_unrelated_destination_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   src=Path(temp)/'src';src.mkdir();other=Path(temp)/'other';other.mkdir();(other/'personal.txt').touch()
   for dest in (src,src/'nested',Path(temp),other):
    with self.assertRaises(ValueError):ins.validate_target(dest,src)
 def test_size_and_registration_fields(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'app.py').write_bytes(b'x'*2048)
   registry=MagicMock();registry.REG_DWORD=4;registry.REG_SZ=1
   ins.register_install(root,registry)
   calls={call.args[1]:call.args[4] for call in registry.SetValueEx.call_args_list}
   self.assertEqual(calls['EstimatedSize'],2);self.assertEqual(calls['DisplayName'],'SARU AI');self.assertIn('uninstall.ps1',calls['UninstallString'])
 def test_unsafe_manifest_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   with self.assertRaises(ValueError):ins.write_manifest(temp,['../outside.txt'])
 def test_copy_failure_restores_existing_files(self):
  with tempfile.TemporaryDirectory() as temp:
   src=Path(temp)/'src';dest=Path(temp)/'installed';src.mkdir();dest.mkdir()
   (src/'app.py').write_text('new');(src/'other.py').write_text('other');(dest/'app.py').write_text('old')
   real=ins.shutil.copy2
   def copy(source,target):
    if Path(source)==src/'other.py':raise OSError('simulated')
    return real(source,target)
   with patch.object(ins.shutil,'copy2',side_effect=copy):
    with self.assertRaises(OSError):ins.copy_application(src,dest)
   self.assertEqual((dest/'app.py').read_text(),'old')
if __name__=='__main__':unittest.main()
