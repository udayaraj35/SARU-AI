import unittest
import threading
from queue import Queue
from types import SimpleNamespace
from unittest.mock import Mock,patch
from screen_watch import ScreenWatch
from assistant_commands import parse_command

class WatchTests(unittest.TestCase):
 def test_commands_are_allowlisted(self):
  self.assertEqual(parse_command('watch screen'),('saru_control',('screen_watch','start')))
  self.assertEqual(parse_command('stop screen view'),('saru_control',('screen_watch','stop')))
 def test_locked_desktop_never_captures(self):
  finished=threading.Event()
  class Events(Queue):
   def put_nowait(self,value):super().put_nowait(value);finished.set()
  view=SimpleNamespace(closed=False,busy=False,events=Events(),after=Mock(return_value='timer'),poll=Mock())
  with patch('screen_watch.desktop_available',return_value=False),patch('pyautogui.screenshot') as capture:
   ScreenWatch.poll(view)
   self.assertTrue(finished.wait(2))
   capture.assert_not_called()
   image,error=view.events.get_nowait();self.assertIsNone(image);self.assertIn('locked',error)
   view.after.assert_called_once_with(3000,view.poll)
 def test_closed_watch_does_not_schedule_work(self):
  view=SimpleNamespace(closed=True,after=Mock())
  ScreenWatch.poll(view);view.after.assert_not_called()
if __name__=='__main__':unittest.main()
