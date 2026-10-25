import unittest
from unittest.mock import Mock
from assistant_commands import parse_command
from improvement_ui import ImprovementStudio

class ControlsTests(unittest.TestCase):
 def test_chat_open_and_close_work_for_typed_and_addressed_voice(self):
  from voice_requests import voice_request
  from command_policy import direct_owner_action
  for text in ('open chat','chat open gara','chat kholnu','च्याट खोल'):
   self.assertEqual(parse_command(text),('saru_control',('page','chat')))
   self.assertEqual(voice_request('SARU '+text),('saru_control',('page','chat')))
  for text in ('close chat','chat banda gara','च्याट बन्द गर'):
   self.assertEqual(parse_command(text),('saru_control',('chat','hide')))
   self.assertEqual(voice_request('SARU '+text),('saru_control',('chat','hide')))
   self.assertTrue(direct_owner_action('saru_control',('chat','hide')))
 def test_settings_and_edit_commands(self):
  cases={'floating size 140':('orb_size',140),'floating opacity 75':('orb_opacity',.75),'disable animations':('reduced_motion',True),'romantic mode':('companion_style','Warm romantic'),'stop remembering conversations':('remember_conversations',False),'generate saru update':('edit','generate'),'apply saru update':('edit','apply'),'saru update files dashboard_ui.py, settings_ui.py':('edit_files',['dashboard_ui.py','settings_ui.py'])}
  for text,expected in cases.items():self.assertEqual(parse_command(text),('saru_control',expected))
  self.assertEqual(parse_command('floating size 999')[1][0],'invalid_setting')
 def test_changed_proposal_cannot_be_approved(self):
  from types import SimpleNamespace
  request=Mock();request.get.return_value='my precise request';files=Mock();files.curselection.return_value=(0,)
  consent=Mock();callback=Mock();view=SimpleNamespace(consent=consent,request=request,files=files,ready=('proposal','digest'),closed=False,busy=False)
  self.assertFalse(ImprovementStudio.reviewed(view,'Review','Exact diff',callback,False))
  callback.assert_not_called();execute=consent.call_args.args[1]
  view.ready=('another','digest')
  with self.assertRaises(ValueError):execute()
  callback.assert_not_called()
 def test_unchanged_review_executes_only_after_owner_confirmation(self):
  from types import SimpleNamespace
  request=Mock();request.get.return_value='specific request';files=Mock();files.curselection.return_value=(0,)
  consent=Mock();callback=Mock();view=SimpleNamespace(consent=consent,request=request,files=files,ready=('proposal','digest'),closed=False,busy=False)
  ImprovementStudio.reviewed(view,'Review','Exact diff',callback,False);callback.assert_not_called()
  consent.call_args.args[1]();callback.assert_called_once_with(True)
if __name__=='__main__':unittest.main()
