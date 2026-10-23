import threading
import unittest
from unittest.mock import Mock
from app_catalog import AppEntry
from app_index import ApplicationIndex
from assistant_commands import parse_command
from voice_requests import voice_request


class FastLaunchTests(unittest.TestCase):
 def test_actual_spoken_nepali_command_routes_to_chrome(self):
  for text in ['मेरो पीसीमा भएको Google Chrome लाई ओपन गर त।','Google Chrome लाई खोल न','क्रोम ओपन गर','Saru, open Google Chrome']:
   self.assertEqual(parse_command(text),('browser','chrome'))
   self.assertEqual(voice_request(text),('browser','chrome'))
  self.assertIsNone(parse_command('Chrome खोल्न मिल्छ कि के हो')[0])
 def test_quick_hits_never_run_store_scan(self):
  entry=AppEntry('Google Chrome','exe','chrome.exe');loader=Mock(return_value=[entry])
  index=ApplicationIndex(loader=loader)
  for _ in range(10):self.assertEqual(index.resolve('Google Chrome'),[entry])
  loader.assert_called_once_with(include_registered=False)
 def test_store_only_apps_are_cached(self):
  entry=AppEntry('WhatsApp','registered','WhatsApp!App')
  loader=Mock(side_effect=lambda **kw:[entry] if kw['include_registered'] else [])
  index=ApplicationIndex(loader=loader)
  self.assertEqual(index.resolve('WhatsApp'),[entry]);self.assertEqual(index.resolve('WhatsApp'),[entry])
  self.assertEqual(loader.call_count,2)
 def test_store_warmup_does_not_block_quick_app(self):
  started=threading.Event();finish=threading.Event();entry=AppEntry('Chrome','exe','chrome.exe')
  def loader(**kw):
   if kw['include_registered']:started.set();finish.wait(2)
   return [entry]
  index=ApplicationIndex(loader=loader);worker=threading.Thread(target=index.warm);worker.start()
  try:
   self.assertTrue(started.wait(1));self.assertEqual(index.resolve('Chrome'),[entry])
  finally:finish.set();worker.join(2)
 def test_expired_entries_refresh(self):
  clock=[0];entry=AppEntry('Chrome','exe','chrome.exe');loader=Mock(return_value=[entry])
  index=ApplicationIndex(loader,lambda:clock[0],ttl=5)
  index.resolve('Chrome');clock[0]=6;index.resolve('Chrome')
  self.assertEqual(loader.call_count,2)

if __name__=='__main__':unittest.main()
