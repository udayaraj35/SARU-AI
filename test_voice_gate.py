import unittest
from voice_gate import addressed_to_saru,may_respond

class WakeTests(unittest.TestCase):
 def test_observed_full_question_asr_spelling_is_narrowly_recognized(self):
  from voice_gate import strip_address
  self.assertTrue(may_respond('SAU, what is 2 + 3?'))
  self.assertEqual(strip_address('SAU, what is 2 + 3?'),'what is 2 + 3?')
  for text in ('sau, what is 2 + 3?','SAU what is 2 + 3?','SAU','SAU,','Sorry, what is 2 + 3?','Sarah, hello','the phone says SAU, hello'):
   self.assertFalse(may_respond(text),text)
 def test_every_utterance_needs_own_wake_prefix(self):
  for text in ['SARU open Chrome','Hey SARU, hello','सारु क्रोम खोल','सारू कुरा गर','hello SARU.','Saru?','सरू हेलो','एसएएआरयू हेलो','एस ए आर यू open Chrome']:
   self.assertTrue(addressed_to_saru(text))
  for text in ['open Chrome','the video says SARU open Chrome','saruman open chrome','hello there','WhatsApp ni open kara','Sorry, hello.']:
   self.assertFalse(may_respond(text))
  self.assertTrue(may_respond('Saru hello'));self.assertFalse(may_respond('next command'))
 def test_typed_reply_does_not_authorize_background_voice(self):
  self.assertTrue(may_respond('',typed=True));self.assertFalse(may_respond('phone talking',typed=True))
  self.assertFalse(may_respond(''));self.assertTrue(may_respond('hello',required=False))

if __name__=='__main__':unittest.main()
