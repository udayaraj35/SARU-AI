import unittest
from unittest.mock import Mock,patch
from pc_input import input_intent,perform_input
from assistant_commands import parse_command
from voice_requests import voice_request
from command_policy import direct_owner_action
from types import SimpleNamespace
from screen_ui import ScreenPanel

class PCInputTests(unittest.TestCase):
 def setUp(self):
  self.mouse=Mock();self.mouse.size.return_value=(1920,1080);self.mouse.position.return_value=(100,200)
  self.focus=Mock(return_value=123);self.writer=Mock()
 def run_input(self,action,value):return perform_input((action,value),123,self.mouse,self.focus,self.writer)
 def test_text_and_voice_route_exact_inputs(self):
  for text,command in [('pc type नमस्ते',('type','नमस्ते')),('pc click 100, 200',('click',(100,200))),('pc press ctrl+s',('shortcut','Save')),('pc scroll down 4',('scroll',-4)),('pc stop',('stop',None))]:
   self.assertEqual(parse_command(text),('desktop_input',command))
   self.assertEqual(voice_request(text),('desktop_input',command))
   self.assertTrue(direct_owner_action('desktop_input',command))
  self.assertIsNone(input_intent('write a poem'))
  self.assertEqual(input_intent('write Hello',task=True),('type','Hello'))
 def test_typing_preserves_focus_and_clipboard(self):
  self.run_input('type','नमस्ते');self.writer.assert_called_once_with('नमस्ते');self.mouse.click.assert_not_called()
 def test_focus_change_and_marked_secrets_block(self):
  self.focus.return_value=456
  with self.assertRaises(ValueError):self.run_input('type','hello')
  self.focus.return_value=123
  with self.assertRaises(ValueError):self.run_input('type','my password is example-secret')
  self.writer.assert_not_called()
 def test_click_must_belong_to_target(self):
  with patch('win32gui.WindowFromPoint',return_value=222),patch('win32gui.GetAncestor',return_value=456):
   with self.assertRaises(ValueError):self.run_input('click',(100,200))
  self.mouse.click.assert_not_called()
  with patch('win32gui.WindowFromPoint',return_value=123),patch('win32gui.GetAncestor',return_value=123):self.run_input('click',(100,200))
  self.mouse.click.assert_called_once_with(100,200,button='left')
 def test_scroll_requires_pointer_over_app(self):
  with patch('win32gui.WindowFromPoint',return_value=222),patch('win32gui.GetAncestor',return_value=456):
   with self.assertRaises(ValueError):self.run_input('scroll',-3)
  self.mouse.scroll.assert_not_called()
 def test_bounds_shortcuts_and_failsafe(self):
  for action,value in [('click',(9999,100)),('type','hello\nsubmit'),('scroll',1000),('shortcut','shell')]:
   with self.assertRaises(ValueError):self.run_input(action,value)
  self.mouse.failSafeCheck.side_effect=RuntimeError('stopped')
  with self.assertRaises(RuntimeError):self.run_input('type','hello')
  self.writer.assert_not_called()
 def panel(self):
  return SimpleNamespace(closed=False,busy=False,locked_window=123,auto_plan_id=None,capture_job=None,attach_job=None,command_job=None,planned=None,captured_at=42,hide_for_capture=Mock(),restore=Mock(),after=Mock(return_value='job'),after_cancel=Mock(),steps=[],status=Mock(),report=Mock(),take_snapshot=Mock())
 def test_queued_input_reactivates_exact_window_reports_then_captures(self):
  panel=self.panel()
  ScreenPanel.command_input(panel,('type','hello'))
  self.assertTrue(panel.busy);self.assertIsNone(panel.captured_at)
  callback=panel.after.call_args.args[1]
  with patch('screen_ui.activate_window') as activate,patch('pc_input.perform_input',return_value='Performed') as perform:
   callback()
  activate.assert_called_once_with(123);perform.assert_called_once()
  self.assertFalse(panel.busy);self.assertEqual(panel.steps,['type'])
  panel.report.assert_called_once_with('Performed')
  panel.after.assert_called_with(400,panel.take_snapshot)
 def test_stop_invalidates_old_proposal_and_cancels_input(self):
  panel=self.panel();panel.command_job='pending';panel.busy=True
  ScreenPanel.command_input(panel,('stop',None))
  panel.after_cancel.assert_called_once_with('pending')
  self.assertFalse(panel.busy);self.assertIsNone(panel.captured_at)
 def test_no_target_or_pending_input_never_schedules(self):
  panel=self.panel();panel.locked_window=None
  with self.assertRaises(ValueError):ScreenPanel.command_input(panel,('type','hello'))
  panel.after.assert_not_called()
  panel.locked_window=123;panel.busy=True
  with self.assertRaises(ValueError):ScreenPanel.command_input(panel,('type','hello'))
  panel.after.assert_not_called()

if __name__=='__main__':unittest.main()
