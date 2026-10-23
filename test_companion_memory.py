import sqlite3,unittest
from companion_memory import companion_prompt,recall
from assistant_commands import parse_command
from live_voice import voice_config
class CompanionTests(unittest.TestCase):
 def test_nepali_browser_commands(self):
  self.assertEqual(parse_command('SARU, chrome kholnu.'),('browser','chrome'))
  self.assertEqual(parse_command('edge open gara'),('browser','edge'))
 def test_named_app_lookup(self):
  from app_catalog import find_apps
  from pathlib import Path
  import tempfile
  with tempfile.TemporaryDirectory() as folder:
   Path(folder,'Example App.lnk').touch()
   self.assertEqual(find_apps('Example App',[folder])[0].stem,'Example App')
   with self.assertRaises(ValueError):find_apps('cmd /c delete',[folder])
  self.assertEqual(parse_command('open Example App'),('named_app','Example App'))
 def test_persona_shared(self):
  self.assertIn('lightly romantic',companion_prompt({}))
  self.assertNotIn('lightly romantic',companion_prompt({'companion_style':'Professional'}))
  self.assertIn('lightly romantic',voice_config({})['system_instruction'])
 def test_recall_old_conversation(self):
  db=sqlite3.connect(':memory:');db.execute('create table messages(id integer primary key,role text,content text)')
  db.execute('insert into messages(role,content) values(?,?)',('Boss','My favourite colour is purple'))
  for i in range(20):db.execute('insert into messages(role,content) values(?,?)',('SARU','Unrelated turn'))
  self.assertIn('purple',recall(db,'purple colour')[0][1]);db.close()
 def test_recall_empty_and_injection(self):
  db=sqlite3.connect(':memory:');db.execute('create table messages(id integer primary key,role text,content text)')
  self.assertEqual(recall(db,"'; DROP TABLE messages; --"),[])
  self.assertEqual(recall(db,''),[]);db.close()
if __name__=='__main__':unittest.main()
