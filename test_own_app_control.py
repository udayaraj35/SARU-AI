import ast,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import psutil
from assistant_commands import parse_command
from command_policy import direct_owner_action
from voice_requests import voice_request
from improvement_core import ImprovementManager
from saru_restart import schedule_restart,restart_after_exit

class OwnAppTests(unittest.TestCase):
 def test_text_and_voice_lifecycle_and_proposal_intents(self):
  cases={'open saru':('lifecycle','show'),'hide saru':('lifecycle','hide'),'close saru':('lifecycle','exit'),'restart saru':('lifecycle','restart'),'close settings':('lifecycle','home'),'आफ्नो एप बन्द गर':('lifecycle','exit'),'सारु आफूलाई रिस्टार्ट गर':('lifecycle','restart'),'saru update status':('edit','status'),'generate saru update':('edit','generate')}
  for command,expected in cases.items():
   self.assertEqual(parse_command(command),('saru_control',expected))
   self.assertEqual(voice_request(command),('saru_control',expected))
   self.assertTrue(direct_owner_action('saru_control',expected))
  self.assertEqual(parse_command('aafu lai improve gara voice stop bug fix'),('self_improve','voice stop bug fix'))
  self.assertIsNone(parse_command('my friend might close saru tomorrow')[0])
 def lifecycle(self,busy=False):
  node=next(n for n in ast.parse(Path('app.py').read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='control_own_app')
  root=Mock();window=Mock();window.winfo_exists.return_value=True;window.busy=busy
  env={'root':root,'orb':Mock(),'back_home':Mock(),'show_saru_main':Mock(),'improvement_window':window,'exit_saru':Mock()}
  exec(compile(ast.Module(body=[node],type_ignores=[]),'app.py','exec'),env)
  return env
 def test_exit_uses_graceful_callback_and_busy_edit_blocks_exit(self):
  env=self.lifecycle();result=env['control_own_app']('exit');self.assertIn('exit completely',result)
  env['root'].after.assert_called_once_with(350,env['exit_saru']);env['exit_saru'].assert_not_called()
  env=self.lifecycle(True)
  with self.assertRaises(ValueError):env['control_own_app']('exit')
  env['root'].after.assert_not_called()
 def test_hide_keeps_process_and_voice_alive(self):
  env=self.lifecycle();env['control_own_app']('hide');env['orb'].deiconify.assert_called_once();env['root'].withdraw.assert_called_once();env['exit_saru'].assert_not_called()
 def test_feature_selection_is_bounded_and_existing_only(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)/'app';root.mkdir()
   for name in ('app.py','dashboard_ui.py','theme_manager.py','live_voice.py','voice_hub.py','settings_store.py'): (root/name).write_text('VALUE=1\n',encoding='utf8')
   manager=ImprovementManager(root,Path(temp)/'data')
   self.assertEqual(manager.suggest_files('change interface theme'),['dashboard_ui.py','theme_manager.py'])
   self.assertEqual(manager.suggest_files('fix voice'),['live_voice.py','voice_hub.py'])
   self.assertNotIn('settings_store.py',manager.suggest_files('settings'))
   self.assertLessEqual(len(manager.suggest_files('interface voice settings office command')),8)
 def test_restart_waits_and_never_kills_parent(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'launch_saru.py').write_text('pass');process=Mock();factory=Mock(return_value=process);popen=Mock()
   self.assertTrue(restart_after_exit(12345,root,process_factory=factory,popen=popen));process.wait.assert_called_once_with(timeout=45);process.kill.assert_not_called();self.assertEqual(popen.call_args.args[0][-1],str(root/'launch_saru.py'))
   process.wait.side_effect=psutil.TimeoutExpired(45);popen.reset_mock()
   self.assertFalse(restart_after_exit(12345,root,process_factory=factory,popen=popen));popen.assert_not_called()
 def test_apply_without_owner_verification_never_changes_source(self):
  from improvement_ui import ImprovementStudio
  view=SimpleNamespace(busy=False,ready=('id','digest'),authorize=Mock(return_value=False),manager=Mock(),note=Mock())
  ImprovementStudio.apply(view,approved=True)
  view.manager.apply.assert_not_called();view.manager.load.assert_not_called()
 def test_incomplete_install_does_not_schedule_restart(self):
  with tempfile.TemporaryDirectory() as temp:
   popen=Mock()
   with self.assertRaises(ValueError):schedule_restart(temp,12345,popen=popen)
   popen.assert_not_called()

if __name__=='__main__':unittest.main()
