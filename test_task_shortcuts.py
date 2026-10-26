import unittest
from assistant_commands import parse_command
from voice_requests import voice_request

class TaskShortcutTests(unittest.TestCase):
 def test_compound_launch_and_message_preserves_target_and_body(self):
  for text in ('open WhatsApp and send a message to Test Contact: Hello please','WhatsApp kholera Test Contact lai Hello please message pathau'):
   action,request=parse_command(text)
   self.assertEqual(action,'backend');self.assertEqual(request[1]['target'],'Test Contact');self.assertEqual(request[1]['text'],'Hello please')
 def test_youtube_controls_do_not_become_video_searches(self):
  for text,expected in {'YouTube ma pause gara':('pause',None),'YouTube ko volume badhau':('volume_delta',10),'YouTube ma arko video chalau':('next',None)}.items():
   self.assertEqual(parse_command(text),('media_control',expected))
 def test_natural_whatsapp_uses_actual_draft_executor(self):
  for text in ('send WhatsApp message to Test Contact: Hello please', 'WhatsApp ma Test Contact lai: Hello please','WhatsApp ma Test Contact lai Hello please message pathau'):
   expected=('backend',('social',{'platform':'whatsapp','action':'send','target':'Test Contact','text':'Hello please'}))
   self.assertEqual(parse_command(text),expected)
   self.assertEqual(voice_request('SARU '+text),expected)
 def test_video_queries_route_to_embedded_player(self):
  for text in ('YouTube ma Nepali folk music bajau','play Nepali folk music on YouTube','open YouTube video Nepali folk music','युट्युबमा नेपाली गीत बजाऊ'):
   result=parse_command(text)
   self.assertEqual(result[0],'media_search',text)
   self.assertEqual(voice_request('SARU '+text),result)
   self.assertEqual(voice_request(text),result)
 def test_mentions_and_negation_are_not_actions(self):
  for text in ('do not play music on YouTube','I said WhatsApp ma Udaya lai hello pathau','remember send WhatsApp message to Udaya: hi'):
   from task_shortcuts import task_shortcut
   self.assertIsNone(task_shortcut(text))
 def test_selected_app_input_preserves_existing_target_guard(self):
  self.assertEqual(parse_command('current app type Hello SARU'),('desktop_input',('type','Hello SARU')))
  self.assertEqual(parse_command('selected app press ctrl+s')[0],'desktop_input')
 def test_whatsapp_payload_reaches_real_prepare_contract_without_sending(self):
  import tempfile
  from unittest.mock import Mock,patch
  from social_bot import SocialBot
  with tempfile.TemporaryDirectory() as folder:
   bot=SocialBot(folder);page=Mock();page.url='https://web.whatsapp.com/'
   page.locator.return_value.inner_text.return_value='Test Contact'
   operation=parse_command('send WhatsApp message to Test Contact: Hello')[1][1]
   with patch.object(bot,'_page',return_value=page),patch.object(bot,'_whatsapp_target',return_value=page),patch.object(bot,'_one',side_effect=lambda locator,what:locator):
    review=bot.prepare(operation)
   self.assertEqual(review['action'],'send');self.assertEqual(review['target'],'Test Contact')
   page.locator.return_value.fill.assert_called_once_with('Hello')
   page.locator.return_value.click.assert_not_called()
   bot.executor.shutdown(wait=True)
 def test_missing_recipient_is_clarified_without_invented_windows_denial(self):
  from companion_memory import companion_prompt
  prompt=companion_prompt({})
  self.assertIn('Do not blame Windows permissions',prompt)
  self.assertIn('exact contact name/phone and message',prompt)

if __name__=='__main__':unittest.main()
