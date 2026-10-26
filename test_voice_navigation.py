import unittest
from assistant_commands import parse_command
from voice_requests import voice_request
from action_consent import consent_reply,PendingActions
from command_policy import direct_owner_action

class NavigationTests(unittest.TestCase):
 def test_sections_route_without_application_name_guessing(self):
  cases={'home kholnu':'home','apps and tools kholnu':'tools','device control dekhaunu':'controls','weather kholnu':'weather','memory kholnu':'Saved memory','social media kholnu':'Social Media','web studio kholnu':'Website Studio','owner profile kholnu':'Owner Profile','voice mode kholnu':'Voice: push to talk','media kholnu':'YouTube Player'}
  for phrase,target in cases.items():
   expected=('saru_control',('navigation',target))
   self.assertEqual(parse_command(phrase),expected)
   self.assertEqual(voice_request('SARU '+phrase),expected)
   self.assertTrue(direct_owner_action(*expected))
 def test_settings_tab_and_negation(self):
  self.assertEqual(parse_command('voice setting kholnu'),('saru_control',('settings_tab','Voice')))
  self.assertEqual(parse_command('open settings appearance'),('saru_control',('settings_tab','Appearance')))
  from voice_navigation import navigation_intent
  self.assertIsNone(navigation_intent('do not open memory'))
 def test_confirmation_is_exact_pending_once_and_expires(self):
  for phrase in ('अँ हुन्छ','ठिक छ गर','yes go ahead','la hunxa'):
   self.assertTrue(consent_reply(phrase))
   pending=PendingActions();self.assertIsNone(pending.consume(phrase))
   pending.offer('Exact synthetic task',lambda:None);self.assertTrue(pending.consume(phrase)[1]);self.assertIsNone(pending.consume(phrase))
  for phrase in ('अँ','maybe okay','हुन्छ तर अहिले नगर','do it later'):
   self.assertIsNone(consent_reply(phrase))
  for phrase in ('अहिले नगर','not now','पर्दैन'):self.assertFalse(consent_reply(phrase))
  now=[0];pending=PendingActions(clock=lambda:now[0]);pending.offer('task',lambda:None,seconds=1);now[0]=2;self.assertIsNone(pending.consume('okay'))

if __name__=='__main__':unittest.main()
