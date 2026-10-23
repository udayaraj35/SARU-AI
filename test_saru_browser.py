import io,json,tempfile,unittest
from unittest.mock import Mock,patch
from saru_browser import checked_url,SaruBrowser
from assistant_commands import parse_command

class BrowserTests(unittest.TestCase):
 def test_urls_reject_code_files_and_credentials(self):
  self.assertEqual(checked_url('web.whatsapp.com'),'https://web.whatsapp.com')
  for url in ('javascript:alert(1)','file:///C:/secret','https://user:password@example.com','data:text/html,hello'):
   with self.assertRaises(ValueError):checked_url(url)
 def test_owner_browser_commands(self):
  for text,value in [('open saru browser',('browser','open')),('browser back',('browser','back')),('browser tab 2',('browser_tab',2)),('control saru browser',('browser','control'))]:
   self.assertEqual(parse_command(text),('saru_control',value))
 def test_child_private_pipe_reused_and_no_shell(self):
  process=Mock();process.poll.return_value=None;process.stdin=io.StringIO();process.stdout=[]
  with tempfile.TemporaryDirectory() as temp,patch('saru_browser.subprocess.Popen',return_value=process) as launch:
   browser=SaruBrowser(temp);browser.command('open','https://web.whatsapp.com/');browser.command('back')
   self.assertEqual(launch.call_count,1)
   self.assertFalse(launch.call_args.kwargs.get('shell',False))
   lines=[json.loads(line) for line in process.stdin.getvalue().splitlines()]
   self.assertEqual(lines[0],{'action':'open','value':'https://web.whatsapp.com/'})
   self.assertEqual(lines[1]['action'],'back')
 def test_no_arbitrary_script_or_unopened_control(self):
  browser=SaruBrowser('.')
  with self.assertRaises(ValueError):browser.command('evaluate','document.cookie')
  with self.assertRaises(ValueError):browser.command('back')
  with self.assertRaises(ValueError):browser.command('fill_password','not-allowed-over-ipc')
if __name__=='__main__':unittest.main()
