import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from installer_backend import configure_api
from version import VERSION
import install_support
import update_manager

class SetupTests(unittest.TestCase):
 def test_version_shared(self):
  self.assertRegex(VERSION,r'^\d+\.\d+\.\d+$');self.assertEqual(install_support.VERSION,VERSION);self.assertEqual(update_manager.VERSION,VERSION)
 def test_skip_does_not_run_or_modify_settings(self):
  def forbidden(*args,**kwargs):raise AssertionError('Skip must not invoke configuration')
  self.assertFalse(configure_api('python','.',{},forbidden))
  self.assertFalse(configure_api('python','.',{'key':''},forbidden))
 def test_secret_stdin_only(self):
  calls=[]
  def runner(args,**kwargs):calls.append((args,kwargs));return types.SimpleNamespace(returncode=0)
  configure_api('python','.',{'provider':'OpenAI','key':'synthetic-secret'},runner)
  self.assertNotIn('synthetic-secret',str(calls[0][0]));self.assertEqual(json.loads(calls[0][1]['input'])['key'],'synthetic-secret')
 def test_api_setup_preserves_memory_and_encrypts_key(self):
  with tempfile.TemporaryDirectory() as temp,patch.dict(os.environ,{'APPDATA':temp}):
   data=Path(temp)/'SARU_AI';data.mkdir();(data/'memory.db').write_bytes(b'memory sentinel')
   from settings_store import SettingsStore
   store=SettingsStore(data/'settings.json',{'keys':{}});store.save({'keys':{'Gemini':'old-synthetic'},'owner_name':'Owner','voice_rate':180})
   configure_api(sys.executable,Path(__file__).parent,{'provider':'OpenAI','key':'new-synthetic','model':'test-model'})
   cfg=store.load();self.assertEqual(cfg['owner_name'],'Owner');self.assertEqual(cfg['keys']['Gemini'],'old-synthetic');self.assertEqual(cfg['keys']['OpenAI'],'new-synthetic')
   self.assertEqual((data/'memory.db').read_bytes(),b'memory sentinel');self.assertNotIn('new-synthetic',(data/'settings.json').read_text(encoding='utf8'))
if __name__=='__main__':unittest.main()
