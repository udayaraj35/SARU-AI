import unittest
from voice_gate import addressed_to_saru,may_respond

class WakeTests(unittest.TestCase):
 def test_conversation_wakes_once_renews_and_expires(self):
  from voice_gate import ConversationGate
  now=[100.];gate=ConversationGate(True,True,clock=lambda:now[0])
  self.assertFalse(gate.authorize('open Chrome'))
  self.assertTrue(gate.authorize('सरू'));self.assertTrue(gate.active)
  self.assertTrue(gate.authorize('open Chrome'));self.assertTrue(gate.authorize('तिमी कस्तो छौ?'))
  now[0]+=59;gate.renew();now[0]+=59;self.assertTrue(gate.authorize('next question'))
  now[0]+=2;self.assertFalse(gate.authorize('open WhatsApp'));self.assertFalse(gate.active)
  self.assertTrue(gate.authorize('SARU hello'));gate.close();self.assertFalse(gate.authorize('next question'))
 def test_typed_notifications_do_not_open_followup_and_strict_mode_remains(self):
  from voice_gate import ConversationGate
  gate=ConversationGate(True,True)
  self.assertTrue(gate.authorize('',typed=True));self.assertFalse(gate.active)
  self.assertFalse(gate.authorize('phone conversation',typed=True))
  gate=ConversationGate(True,False);self.assertTrue(gate.authorize('SARU hello'))
  self.assertFalse(gate.authorize('next question'))
 def test_late_reply_cannot_reopen_an_explicitly_closed_conversation(self):
  from voice_gate import ConversationGate
  gate=ConversationGate(True,True);gate.authorize('SARU');epoch=gate.generation
  gate.close();self.assertFalse(gate.renew(epoch));self.assertFalse(gate.active)
  gate.authorize('SARU');deadline=gate.until
  self.assertFalse(gate.renew(epoch));self.assertEqual(gate.until,deadline)
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
