import time
import unittest
from unittest.mock import Mock
from PIL import Image
from desktop_actions import execute_action

class DesktopActionsTests(unittest.TestCase):
 def setUp(self):
  self.image=Image.new('RGB',(200,100),'white');self.automation=Mock();self.automation.screenshot.return_value=self.image.copy();self.automation.size.return_value=(200,100);self.writer=Mock();self.focus=Mock(return_value=123)
 def run_action(self,action,payload,age=0):
  return execute_action(action,payload,self.image,(80,50),time.monotonic()-age,123,self.automation,self.focus,self.writer)
 def test_unicode_and_clipboard_unchanged(self):
  self.run_action('type','नमस्ते SARU 🙂');self.writer.assert_called_once_with('नमस्ते SARU 🙂');self.automation.click.assert_called_once_with(80,50)
 def test_expired_never_types(self):
  with self.assertRaises(ValueError):self.run_action('type','hello',31)
  self.writer.assert_not_called();self.automation.click.assert_not_called()
 def test_changed_target_never_scrolls(self):
  self.automation.screenshot.return_value=Image.new('RGB',(200,100),'black')
  with self.assertRaises(ValueError):self.run_action('scroll',3)
  self.automation.scroll.assert_not_called()
 def test_focus_change_blocks(self):
  self.focus.return_value=456
  with self.assertRaises(ValueError):self.run_action('shortcut','Paste')
  self.automation.hotkey.assert_not_called()
 def test_click_focus_change_blocks_text(self):
  self.focus.side_effect=[123,456]
  with self.assertRaises(ValueError):self.run_action('type','hello')
  self.writer.assert_not_called()
 def test_scroll_and_shortcut(self):
  self.run_action('scroll',-3);self.automation.scroll.assert_called_once_with(-3)
  self.run_action('shortcut','Find');self.automation.hotkey.assert_called_once_with('ctrl','f')
 def test_forbidden_inputs(self):
  for action,value in [('scroll',1000),('shortcut','run shell'),('type','hello\nsubmit'),('type','x'*2001),('shell','whoami')]:
   with self.assertRaises(ValueError):self.run_action(action,value)
  self.automation.click.assert_not_called();self.automation.hotkey.assert_not_called()
 def test_double_and_right_click(self):
  self.run_action('double click','');self.automation.doubleClick.assert_called_once_with(80,50,interval=0.15)
  self.run_action('right click','');self.automation.click.assert_called_once_with(80,50,button='right')

if __name__=='__main__':unittest.main()
