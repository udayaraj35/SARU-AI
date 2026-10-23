import unittest
import ast
from pathlib import Path
from unittest.mock import Mock,patch
from wacrm_bridge import CRMClient,LocalCRM,checked_origin,runtime_environment
from assistant_commands import parse_command
from command_policy import direct_owner_action

class CRMTests(unittest.TestCase):
 def function(self,name,namespace):
  tree=ast.parse(Path('app.py').read_text(encoding='utf-8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'app.py','exec'),namespace)
  return namespace[name]
 def test_console_cannot_send_without_review(self):
  propose=Mock(return_value='review pending');ns={'interpret_task':parse_command,'propose_owner_command':propose}
  run=self.function('run_agent_task',ns)
  self.assertEqual(run('crm send to +9779800000000: Hello',quiet=True),'review pending')
  propose.assert_called_once()
 def test_changed_crm_account_invalidates_review(self):
  cfg={'keys':{'WACRM_API':'synthetic'},'wacrm_api_url':'http://127.0.0.1:3876'};offer=Mock();run=Mock()
  propose=self.function('propose_owner_command',{'interpret_task':parse_command,'cfg':cfg,'offer_pending_action':offer,'run_agent_task':run})
  propose('crm send to +9779800000000: Hello');callback=offer.call_args.args[1]
  cfg['keys']['WACRM_API']='changed'
  with self.assertRaises(ValueError):callback()
  run.assert_not_called()
 def test_credentials_required_before_process_launch(self):
  with patch('wacrm_bridge.subprocess.Popen') as process:
   with self.assertRaises(ValueError):LocalCRM().start({})
  process.assert_not_called()
 def test_origin_protects_bearer_from_http_remote_and_redirects(self):
  for value in ['http://example.com','https://user:pass@example.com','file:///secret','https://example.com/path','https://example.com?token=secret']:
   with self.assertRaises(ValueError):checked_origin(value)
  self.assertEqual(checked_origin('http://127.0.0.1:3876/'),'http://127.0.0.1:3876')
 def test_read_and_exact_send_use_scoped_api_and_never_retry(self):
  session=Mock();session.request.return_value.status_code=201;session.request.return_value.json.return_value={'data':{'message_id':'synthetic'}}
  client=CRMClient({'keys':{'WACRM_API':'synthetic'}},session)
  client.send('+9779800000000','Hello')
  call=session.request.call_args
  self.assertEqual(call.args,('POST','http://127.0.0.1:3876/api/v1/messages'))
  self.assertEqual(call.kwargs['json'],{'to':'+9779800000000','type':'text','text':'Hello'})
  self.assertFalse(call.kwargs['allow_redirects']);session.request.assert_called_once()
 def test_no_false_success_or_token_leak(self):
  session=Mock();session.request.return_value.status_code=403;client=CRMClient({'keys':{'WACRM_API':'secret-token'}},session)
  with self.assertRaises(RuntimeError) as error:client.request('GET','contacts')
  self.assertNotIn('secret-token',str(error.exception))
  with self.assertRaises(ValueError):client.send('9800000000','Hello')
 def test_commands_and_send_is_reviewed(self):
  self.assertEqual(parse_command('SARU, open WhatsApp CRM'),('wacrm_panel',None))
  self.assertEqual(parse_command('crm inbox'),('wacrm_read','conversations'))
  self.assertEqual(parse_command('crm send to +9779800000000: Hello'),('wacrm_send',('+9779800000000','Hello')))
  self.assertTrue(direct_owner_action('wacrm_read'));self.assertFalse(direct_owner_action('wacrm_send'))

if __name__=='__main__':unittest.main()
