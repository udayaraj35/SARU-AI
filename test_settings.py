import json
import tempfile
import unittest
from pathlib import Path
from settings_store import SettingsStore, SettingsError, WindowsProtector

class FakeProtector:
 def protect(self,value):return value.hex()
 def unprotect(self,value):return bytes.fromhex(value)

class SettingsTests(unittest.TestCase):
 def test_legacy_migration(self):
  with tempfile.TemporaryDirectory() as temp:
   file=Path(temp)/'settings.json'
   file.write_text(json.dumps({'keys':{'OpenAI':'test-only-secret'},'owner_name':'Owner','custom':9}))
   store=SettingsStore(file,{'keys':{},'model':'old'},FakeProtector())
   cfg=store.load()
   self.assertEqual(cfg['keys']['OpenAI'],'test-only-secret')
   raw=file.read_text();self.assertNotIn('test-only-secret',raw)
   self.assertNotIn('keys',json.loads(raw));self.assertEqual(store.load()['custom'],9)
 def test_failed_migration_preserves_original(self):
  class Broken(FakeProtector):
   def protect(self,value):raise SettingsError('Unavailable')
  with tempfile.TemporaryDirectory() as temp:
   file=Path(temp)/'settings.json';original='{"keys":{"OpenAI":"test"}}';file.write_text(original)
   with self.assertRaises(SettingsError):SettingsStore(file,{},Broken()).load()
   self.assertEqual(file.read_text(),original)
 def test_corrupt_file_preserved(self):
  with tempfile.TemporaryDirectory() as temp:
   file=Path(temp)/'settings.json';file.write_text('broken')
   with self.assertRaises(SettingsError):SettingsStore(file,{},FakeProtector()).load()
   self.assertEqual(file.read_text(),'broken')
 def test_defaults_are_independent(self):
  with tempfile.TemporaryDirectory() as temp:
   store=SettingsStore(Path(temp)/'missing',{'keys':{}},FakeProtector())
   first=store.load();first['keys']['x']='x';self.assertEqual(store.load()['keys'],{})
 def test_windows_dpapi(self):
  import os
  if os.name!='nt':self.skipTest('Windows required')
  protector=WindowsProtector();data=b'SARU test secret only'
  sealed=protector.protect(data)
  self.assertNotIn(data.decode(),sealed);self.assertEqual(protector.unprotect(sealed),data)
 def test_future_schema_preserved(self):
  with tempfile.TemporaryDirectory() as temp:
   file=Path(temp)/'settings.json';file.write_text('{"schema_version":999}')
   with self.assertRaises(SettingsError):SettingsStore(file,{},FakeProtector()).load()

if __name__=='__main__':unittest.main()
