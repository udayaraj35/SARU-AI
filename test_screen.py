import time
import unittest
from unittest.mock import MagicMock
from PIL import Image
from screen_tools import preview_to_screen,same_target_patch,checked_click
class ScreenTests(unittest.TestCase):
 def test_preview_mapping_and_letterbox(self):
  self.assertEqual(preview_to_screen(250,150,(10,10,480,270),(1920,1080)),(960,560))
  with self.assertRaises(ValueError):preview_to_screen(0,0,(10,10,480,270),(1920,1080))
 def test_changed_target_rejected(self):
  self.assertFalse(same_target_patch(Image.new('RGB',(200,100),'black'),Image.new('RGB',(200,100),'white'),(70,50)))
 def test_one_click_only_after_freshness_checks(self):
  image=Image.new('RGB',(200,100),'white');automation=MagicMock();automation.screenshot.return_value=image;automation.size.return_value=(200,100)
  checked_click(image,(80,50),time.monotonic(),123,automation,lambda:123);automation.click.assert_called_once_with(80,50)
  automation.reset_mock()
  with self.assertRaises(ValueError):checked_click(image,(80,50),time.monotonic()-35,123,automation,lambda:123)
  automation.click.assert_not_called()
  with self.assertRaises(ValueError):checked_click(image,(80,50),time.monotonic(),123,automation,lambda:999)
  automation.click.assert_not_called()
if __name__=='__main__':unittest.main()
