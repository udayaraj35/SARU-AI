import json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from improvement_core import ImprovementManager
from improvement_ai import generate
class ImprovementTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'app';self.root.mkdir();(self.root/'app.py').write_bytes(b'print("old")\r\n');(self.root/'view.py').write_text('COLOR="blue"\n',encoding='utf-8');self.manager=ImprovementManager(self.root,Path(self.temp.name)/'data')
 def tearDown(self):self.temp.cleanup()
 def propose(self,name='view.py',old='blue',new='violet'):
  files=self.manager.snapshot([name]);return self.manager.stage(json.dumps({'summary':'Change theme','changes':[{'path':name,'edits':[{'old':old,'new':new}]}]}),files,'Change my theme')
 def test_stage_does_not_change_code_apply_then_rollback(self):
  identifier,proposal,digest=self.propose();self.assertIn('blue',(self.root/'view.py').read_text())
  self.manager.apply(identifier,digest);self.assertIn('violet',(self.root/'view.py').read_text())
  self.manager.rollback(identifier);self.assertIn('blue',(self.root/'view.py').read_text())
 def test_protected_and_outside_files_rejected(self):
  for name in ('../secret.py','C:\\private.py','settings_store.py','recover_saru.py','improvement_core.py'):
   with self.assertRaises(ValueError):self.manager.target(name)
 def test_syntax_error_rejected_before_proposal(self):
  with self.assertRaises(SyntaxError):self.propose(old='COLOR="blue"',new='def bad(')
  self.assertIn('blue',(self.root/'view.py').read_text())
 def test_changed_current_source_not_overwritten(self):
  identifier,_,digest=self.propose();(self.root/'view.py').write_text('USER_EDIT=True\n')
  with self.assertRaises(ValueError):self.manager.apply(identifier,digest)
  self.assertIn('USER_EDIT',(self.root/'view.py').read_text())
 def test_wrong_review_hash_rejected(self):
  identifier,_,_=self.propose()
  with self.assertRaises(ValueError):self.manager.apply(identifier,'wrong')
 def test_later_edit_not_overwritten_by_rollback(self):
  identifier,_,digest=self.propose();self.manager.apply(identifier,digest);(self.root/'view.py').write_text('USER_EDIT=True\n')
  with self.assertRaises(ValueError):self.manager.rollback(identifier)
 def test_crlf_backup_and_no_candidate_execution(self):
  identifier,_,digest=self.propose('app.py','print("old")','raise RuntimeError("candidate would fail")')
  self.manager.apply(identifier,digest)
  recovery=ImprovementManager(self.root,Path(self.temp.name)/'data');recovery.rollback(identifier)
  self.assertEqual((self.root/'app.py').read_bytes(),b'print("old")\r\n')
 def test_ambiguous_anchor_rejected(self):
  (self.root/'view.py').write_text('x="blue blue"\n')
  with self.assertRaises(ValueError):self.propose()
 def test_partial_apply_failure_restores_completed_files(self):
  (self.root/'other.py').write_text('VALUE=1\n')
  originals=self.manager.snapshot(['view.py','other.py'])
  response={'summary':'Two changes','changes':[{'path':'view.py','edits':[{'old':'blue','new':'violet'}]},{'path':'other.py','edits':[{'old':'VALUE=1','new':'VALUE=2'}]}]}
  identifier,_,digest=self.manager.stage(json.dumps(response),originals,'fixture')
  real=self.manager.write_source
  def fail(path,data):
   if path.name=='other.py':raise OSError('simulated write failure')
   return real(path,data)
  with patch.object(self.manager,'write_source',side_effect=fail):
   with self.assertRaises(OSError):self.manager.apply(identifier,digest)
  self.assertIn('blue',(self.root/'view.py').read_text());self.assertEqual(self.manager.load(identifier)[1]['state'],'apply_failed')
 def test_saved_secret_in_source_never_sent(self):
  session=Mock();config={'provider':'Gemini','model':'test','keys':{'Gemini':'private-secret-token'}}
  with self.assertRaises(ValueError):generate(config,'improve',{'view.py':'TOKEN="private-secret-token"'},session)
  session.post.assert_not_called()
if __name__=='__main__':unittest.main()
