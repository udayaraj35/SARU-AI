import unittest
from pathlib import Path
from unittest.mock import Mock,patch,call
from backend_runtime import BackendRuntime
from ui_control import ui_intent

class DirectWhatsAppTests(unittest.TestCase):
 def runtime(self,enabled=True):
  runtime=BackendRuntime.__new__(BackendRuntime)
  runtime.config={'whatsapp_direct_send':enabled};runtime.integrity_error='';runtime.source=Path('.')
  runtime.social=Mock();runtime.reviewed=Mock()
  def job(work,done=None):
   result=work()
   if done:done(result)
  runtime.job=job
  return runtime
 def test_exact_request_prepares_and_commits_once_when_enabled(self):
  runtime=self.runtime();op={'platform':'whatsapp','action':'send','target':'Test Contact','text':'Hello'};review={**op,'preview_id':'synthetic'}
  runtime.social.submit.return_value.result.side_effect=[review,{'state':'submitted_unconfirmed'}]
  with patch('backend_runtime.developer_identity'),patch('backend_runtime.gate.grant',return_value='synthetic-token'):
   runtime.handle(('whatsapp_request',op))
  runtime.social.submit.assert_has_calls([call('prepare',op),call().result(timeout=90),call('commit',review,'synthetic-token'),call().result(timeout=30)])
  self.assertEqual(runtime.social.submit.call_count,2);runtime.reviewed.assert_not_called()
 def test_default_mode_and_raw_social_commands_keep_review(self):
  op={'platform':'whatsapp','action':'send','target':'Test Contact','text':'Hello'}
  for enabled,kind in ((False,'whatsapp_request'),(True,'social')):
   runtime=self.runtime(enabled);runtime.social.submit.return_value.result.return_value=op
   runtime.handle((kind,op));runtime.reviewed.assert_called_once();self.assertEqual(runtime.social.submit.call_count,1)
 def test_changed_recipient_never_auto_commits(self):
  runtime=self.runtime();op={'platform':'whatsapp','action':'send','target':'Test Contact','text':'Hello'}
  runtime.social.submit.return_value.result.return_value={**op,'target':'Different Contact'}
  with patch('backend_runtime.developer_identity'),self.assertRaises(ValueError):runtime.handle(('whatsapp_request',op))
  self.assertEqual(runtime.social.submit.call_count,1)
 def test_own_app_named_controls_are_not_desktop_coordinates(self):
  self.assertEqual(ui_intent('ma Owner Profile kholnu'),('action','Owner Profile'))
  self.assertEqual(ui_intent('saru ko API Manager khola'),('action','API Manager'))
  self.assertIsNone(ui_intent('my friend said ma Owner Profile kholnu'))

if __name__=='__main__':unittest.main()
