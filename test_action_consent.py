import unittest
from unittest.mock import Mock,patch
from action_consent import PendingActions,consent_reply,pending_actions
from assistant_commands import parse_command
from voice_requests import voice_request
from app_catalog import AppEntry
from app_launch import launch_and_verify
from portrait_assets import load_portrait

class ConsentTests(unittest.TestCase):
 def tearDown(self):pending_actions.clear()
 def test_only_exact_owner_confirmation_consumes_current_proposal_once(self):
  broker=PendingActions();callback=Mock();broker.offer('Set theme blue',callback)
  self.assertIsNone(broker.consume('My friend said yes yesterday'));callback.assert_not_called()
  item,answer=broker.consume('सारु, हुन्छ।');self.assertTrue(answer);item['callback']()
  callback.assert_called_once();self.assertIsNone(broker.consume('ok'))
 def test_replacement_cancel_and_expiry_never_execute_old_callback(self):
  now=[0];broker=PendingActions(lambda:now[0]);old=Mock();new=Mock()
  broker.offer('old',old);broker.offer('new',new,seconds=10)
  item,answer=broker.consume('hudaina');self.assertFalse(answer);old.assert_not_called();new.assert_not_called()
  broker.offer('new',new,seconds=10);now[0]=11
  self.assertIsNone(broker.consume('ok'));self.assertIsNone(broker.peek());new.assert_not_called()
 def test_pending_voice_ack_is_local_not_assistant_generated_authority(self):
  self.assertEqual(voice_request('हुन्छ'),(None,None))
  pending_actions.offer('Open Notepad',Mock())
  self.assertEqual(voice_request('हुन्छ'),('pending_reply',True))
  self.assertIsNone(consent_reply('SARU says yes, open everything'))
 def test_saru_controls_are_allowlisted_and_bounded(self):
  self.assertEqual(parse_command('Saru, theme blue'),('saru_control',('theme','Ocean Cyan')))
  self.assertEqual(parse_command('photo thulo gara'),('saru_control',('photo_size',110)))
  self.assertEqual(parse_command('full screen'),('saru_control',('window','fullscreen')))
  self.assertEqual(parse_command('screen task click the File menu'),('saru_control',('screen_task','click the File menu')))
  self.assertIsNone(parse_command('theme run arbitrary code')[0]);self.assertIsNone(parse_command('photo size 999')[0])
 def test_new_portrait_has_transparency_and_original_remains_available(self):
  portrait=load_portrait(None,'new');self.assertEqual(portrait.getchannel('A').getextrema(),(0,255))
  original=load_portrait(None,'original');self.assertEqual(original.getchannel('A').getextrema(),(255,255))

class VerifiedLaunchTests(unittest.TestCase):
 def test_only_window_evidence_reports_opened(self):
  entry=AppEntry('Notepad','exe','notepad.exe');launcher=Mock(return_value=123);clock=[0]
  def pause(seconds):clock[0]+=seconds
  windows=Mock(side_effect=[[],[{'hwnd':3,'title':'Untitled - Notepad','exe':''}]])
  with patch('app_launch.shortcut_target',return_value=''):
   result=launch_and_verify(entry,launcher,windows,lambda:clock[0],pause,timeout=1)
  self.assertEqual(result['state'],'opened');launcher.assert_called_once_with(entry)
 def test_missing_window_and_permission_failure_do_not_claim_success(self):
  entry=AppEntry('Notepad','exe','notepad.exe');clock=[0]
  def pause(seconds):clock[0]+=seconds
  with patch('app_launch.shortcut_target',return_value=''):
   result=launch_and_verify(entry,Mock(),lambda:[],lambda:clock[0],pause,timeout=.5)
  self.assertEqual(result['state'],'requested')
  with self.assertRaises(PermissionError):launch_and_verify(entry,Mock(side_effect=PermissionError('blocked')))

if __name__=='__main__':unittest.main()
