import io,json,hashlib,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from advanced_secure_io import EncryptedFiles
from advanced_workspace import bundle_manifest,prepare_runtime,AdvancedWorkspace
from advanced_bootstrap import requires_review
from settings_store import WindowsProtector
from assistant_commands import parse_command

class SecureTests(unittest.TestCase):
 def test_encrypted_read_write_pathlib_and_open_preserve_original_on_failure(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'api_keys.json';secret='synthetic-test-only-credential';secure=EncryptedFiles([path],WindowsProtector());secure.write(path,json.dumps({'key':secret}))
   with secure.original_open(path,'rb') as source:raw=source.read()
   self.assertNotIn(secret.encode(),raw)
   try:
    secure.install();self.assertEqual(json.loads(path.read_text())['key'],secret)
    with open(path,encoding='utf8') as source:self.assertEqual(json.load(source)['key'],secret)
    path.write_text(json.dumps({'key':secret,'name':'SARU'}),encoding='utf8')
    with self.assertRaises(ValueError):path.write_text('partial {')
    self.assertEqual(json.loads(path.read_text())['name'],'SARU')
    other=Path(folder)/'plain.txt';other.write_text('ordinary');self.assertEqual(other.read_text(),'ordinary')
   finally:secure.restore()
   self.assertNotIn(secret,path.read_text())
 def test_wrong_account_or_corrupt_data_is_not_overwritten(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'config.json';path.write_text('not a protected config');before=path.read_bytes();secure=EncryptedFiles([path],WindowsProtector())
   with self.assertRaises(ValueError):secure.write(path,'{}')
   self.assertEqual(path.read_bytes(),before)

class WorkspaceTests(unittest.TestCase):
 def test_real_bundle_hashes_and_capabilities_are_explicit(self):
  manifest=bundle_manifest(Path(__file__).parent);self.assertEqual(len(manifest['bundled_tools']),17);self.assertIn('whatsapp_call.py',manifest['advertised_plugin_files_missing'])
 def test_runtime_copy_retains_private_settings_and_rejects_unreviewed_source(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)/'app';bundle=root/'mark_suite';bundle.mkdir(parents=True);(bundle/'main.py').write_text('pass\n')
   entry={'path':'main.py','sha256':hashlib.sha256((bundle/'main.py').read_bytes()).hexdigest()};(bundle/'SOURCE_INVENTORY.json').write_text(json.dumps({'files':[entry]}))
   runtime=prepare_runtime(root,Path(folder)/'data');(runtime/'config').mkdir();private=runtime/'config/api_keys.json';private.write_text('private sentinel')
   prepare_runtime(root,Path(folder)/'data');self.assertEqual(private.read_text(),'private sentinel')
   (bundle/'main.py').write_text('unreviewed')
   with self.assertRaises(ValueError):prepare_runtime(root,Path(folder)/'data')
 def test_simple_open_is_direct_and_substantive_actions_have_exact_review(self):
  self.assertFalse(requires_review('open_app',{'app':'Chrome'}));self.assertFalse(requires_review('file_controller',{'action':'list'}))
  for name in ('send_message','screen_process','computer_control','code_helper','dev_agent'):self.assertTrue(requires_review(name,{}))
  self.assertTrue(requires_review('file_controller',{'action':'delete'}));self.assertEqual(parse_command('open advanced workspace'),('advanced_workspace',None))
 def test_start_does_not_open_two_engines_while_waiting_for_microphone_cleanup(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Mock();voice=Mock();voice.engine.active=True;manager=AdvancedWorkspace(Path(__file__).parent,folder,{},root,voice,Mock())
   with patch('advanced_workspace.advanced_python',return_value=Path('synthetic-pythonw.exe')),patch('advanced_workspace.prepare_runtime',return_value=Path(folder)/'advanced/runtime'):
    (Path(folder)/'advanced').mkdir();manager.start();manager.start();voice.stop.assert_called_once();self.assertTrue(manager.starting);self.assertIsNone(manager.process)
    manager.close();self.assertFalse(manager.starting)

if __name__=='__main__':unittest.main()
