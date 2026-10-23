import unittest
from ui_control import ui_intent,normalized
from assistant_commands import parse_command
from voice_requests import voice_request
class IntentTests(unittest.TestCase):
 def test_exact_button_tabs_options_and_settings(self):
  cases={'list buttons':('buttons',None),'press button Save settings':('press','Save settings'),'click button 12':('press','12'),'select tab Voice':('tab','Voice'),'open option Audio Center':('action','Audio Center'),'set option voice_rate to 180':('field',('voice_rate','180'))}
  for text,intent in cases.items():
   self.assertEqual(ui_intent(text),intent);self.assertEqual(parse_command(text),('ui_control',intent));self.assertEqual(voice_request(text),('ui_control',intent))
 def test_normal_requests_and_names_are_not_code(self):
  self.assertIsNone(ui_intent('open calculator'));self.assertIsNone(ui_intent('my friend said click yesterday'))
  self.assertEqual(normalized('⚙ Settings'),normalized('settings'))
  self.assertNotEqual(normalized('सेटिङ'),normalized('सेटिग'))
if __name__=='__main__':unittest.main()
