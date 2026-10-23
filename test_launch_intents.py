import unittest
from assistant_commands import parse_command
from voice_requests import voice_request

class LaunchIntentTests(unittest.TestCase):
 def test_reported_mixed_language_voice_requests(self):
  cases={'Oh, mere PC mein bhago Google Chrome open kar do.':('browser','chrome'),'WhatsApp ni open kara.':('site','whatsapp'),'WhatsApp bhi open kar do':('site','whatsapp'),'WhatsApp पनि ओपन गर':('site','whatsapp'),'क्रोम ओपन कर दो':('browser','chrome')}
  for text,expected in cases.items():
   self.assertEqual(parse_command(text),expected,text)
   self.assertEqual(voice_request(text),expected,text)
  for text in ['Do not open Chrome','I said WhatsApp ni open kara yesterday','remember WhatsApp ni open kara']:
   self.assertNotIn(voice_request(text)[0],('browser','site','named_app'))
 def test_generic_app_requests_open_picker(self):
  for text in ('app khola','app kholnu','एप खोल्नुहोस्','मलाई एप खोलिदिनुस्','सारु, एउटा app खोल न','open an app','open apps'):
   self.assertEqual(parse_command(text),('app_picker',None),text)
   self.assertEqual(voice_request(text),('app_picker',None),text)
 def test_nepali_named_apps(self):
  cases={'क्रोम खोलिदिनुस्':('browser','chrome'),'सारू, नोटप्याड खोल्नुहोस्':('notepad',None),'क्याल्कुलेटर खोलिदिनुहोस्':('app','Calculator'),'VS Code kholnus':('named_app','VS Code'),'WhatsApp app खोल्नुहोस्':('named_app','WhatsApp'),'open the Notepad app':('named_app','Notepad'),'मेरो क्रोम खोलिदेऊ न':('browser','chrome')}
  for text,expected in cases.items():
   self.assertEqual(parse_command(text),expected,text)
   self.assertEqual(voice_request(text),expected,text)
 def test_discussion_and_saved_content_do_not_launch(self):
  for text in ('I wrote open Chrome in my notes','एप कसरी खोलिन्छ?','Do not open Calculator','मलाई app बारे बताऊ','Could you explain how apps work?'):
   self.assertEqual(voice_request(text),(None,None),text)
  self.assertEqual(parse_command('remember open Chrome tomorrow'),('note','open Chrome tomorrow'))

if __name__=='__main__':unittest.main()
