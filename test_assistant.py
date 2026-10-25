import ast
import pathlib
import tempfile
import types
import unittest
from assistant_commands import parse_command,calculate,SITES

class AssistantTests(unittest.TestCase):
 def test_languages(self):
  for text,expected in [('youtube kholnu',('site','youtube')),('whatsapp खोल्नु',('site','whatsapp')),('hello, saru open calculator',('app','Calculator')),('volume 50',('volume','50')),('brightness 101',('invalid','Use a value from 0 to 100.')),('youtube ma Nepali song khojnu',('youtube_search','nepali song')),('save note Buy milk',('note','Buy milk')),('Saru search Sofia',('search','Sofia'))]:
   with self.subTest(text=text):self.assertEqual(parse_command(text),expected)
 def test_conversation_not_action(self):
  for text in ['How does CPU work?','Can you explain screenshot formats?','write a story about youtube','delete everything']:
   self.assertEqual(parse_command(text),(None,None))
 def test_named_app_has_no_shell_evaluation(self):
  self.assertEqual(parse_command('open powershell'),('named_app','powershell'))
  from app_catalog import find_apps
  with self.assertRaises(ValueError):find_apps('powershell -c whoami; exit',[])
 def test_math(self):
  self.assertEqual(calculate('(12 + 8) * 5'),100)
  for expr in ["__import__('os').system('whoami')",'2 ** 99999','True + 2']:
   with self.assertRaises(ValueError):calculate(expr)
 def test_syntax(self):
  for file in pathlib.Path('.').glob('*.py'):compile(file.read_text(encoding='utf-8-sig'),str(file),'exec')
 def test_actions(self):
  tree=ast.parse(pathlib.Path('app.py').read_text(encoding='utf8'))
  fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_agent_task')
  calls=[]
  ns={'open_saru_browser':lambda url:calls.append(url),'interpret_task':parse_command,'calculate':calculate,'SITES':SITES,'HELP':'help','webbrowser':types.SimpleNamespace(open=lambda url:calls.append(url)),'urllib':__import__('urllib.parse'),'log_task':lambda *a:None,'status':types.SimpleNamespace(set=lambda *a:None),'cfg':{'speak':False},'show_dialog':lambda *args:calls.append(args),'adjust_volume':lambda n:calls.append(n),'adjust_brightness':lambda n:calls.append(n),'notes':lambda:[('test','saved note')]}
  player=types.SimpleNamespace(play_request=lambda query:calls.append(('video-query',query)))
  ns['media_player']=lambda *args:(calls.append('native-video-screen') or player)
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'app.py','exec'),ns)
  for command in ['open youtube','youtube search Nepali songs','volume 40','brightness 60','calculate 2+2','show notes']:ns['run_agent_task'](command)
  self.assertIn('native-video-screen',calls)
  self.assertIn(('video-query','Nepali songs'),calls)
  self.assertFalse(any(isinstance(item,str) and item.startswith('https://www.youtube.com') for item in calls))
  self.assertIn(40,calls);self.assertIn(60,calls)
  self.assertIn(('SARU Agent','Result: 4'),calls)

if __name__=='__main__':unittest.main(verbosity=2)

