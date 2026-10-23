import unittest
from assistant_commands import parse_command
from command_policy import direct_owner_action
from secret_handling import contains_secret,safe_memory_text

class DirectTests(unittest.TestCase):
 def test_web_and_native_destinations(self):
  cases={'open YouTube':('site','youtube'),'open Facebook':('site','facebook'),'open Google Chrome':('browser','chrome'),'open WhatsApp web':('site','whatsapp'),'open WhatsApp in PC':('named_app','WhatsApp'),'open WhatsApp desktop':('named_app','WhatsApp')}
  for text,expected in cases.items():self.assertEqual(parse_command(text),expected);self.assertTrue(direct_owner_action(*expected))
 def test_inner_reviews_not_broadly_bypassed(self):
  # Opening a planning studio is direct; sending source and applying retain their own reviews.
  self.assertTrue(direct_owner_action('self_improve'))
  self.assertTrue(direct_owner_action('saru_control',('theme','Ocean Cyan')))
  self.assertTrue(direct_owner_action('desktop_task',('Notepad','write hello')))
  for action in ('whatsapp','email','camera_ask','voice_enroll'):self.assertFalse(direct_owner_action(action))
 def test_marked_secrets_do_not_become_memory(self):
  self.assertTrue(contains_secret('my password is synthetic-secret'))
  self.assertNotIn('synthetic-secret',safe_memory_text('my password is synthetic-secret'))
  self.assertFalse(contains_secret('fill password locally'));self.assertEqual(safe_memory_text('hello'),'hello')
if __name__=='__main__':unittest.main()
