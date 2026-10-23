import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from profiles import CREATOR,get_profile,save_profile,validate_profile,copy_photo,photo_path
from repo_library import RepoLibrary,repository_name,selected_reference
from screen_agent import validate_plan
from app_catalog import AppEntry,match_entries
from PIL import Image

class ProfileTests(unittest.TestCase):
 def test_owner_and_creator_remain_separate(self):
  config={'owner_name':'Buyer'}
  self.assertEqual(get_profile(config,'creator')['name'],'Udaya Raj Khanal')
  save_profile(config,'owner',{'name':'New owner','email':'buyer@example.com'})
  self.assertEqual(config['owner_name'],'New owner');self.assertEqual(get_profile(config,'creator')['email'],CREATOR['email'])
  self.assertNotIn('email',get_profile({'owner_name':'Buyer'},'owner'))
 def test_profile_links_and_photo_copy(self):
  for values in ({'name':''},{'name':'Owner','youtube':'javascript:alert(1)'},{'name':'Owner','email':'bad'}):
   with self.assertRaises(ValueError):validate_profile(values)
  with tempfile.TemporaryDirectory() as temp:
   image=Path(temp)/'photo.jpg';Image.new('RGB',(50,70),'blue').save(image)
   copied=copy_photo(image,Path(temp)/'data','owner')
   self.assertEqual(Path(copied).read_bytes(),image.read_bytes());self.assertTrue(photo_path({'photo':copied},temp,'owner'))

class RepositoryTests(unittest.TestCase):
 def staged(self,library):
  folder=library.root/'staged'/'test';folder.mkdir(parents=True)
  content=b'"act","prompt"\n"Writer","Help write a video script"\n';(folder/'0.txt').write_bytes(content)
  manifest={'repo':'f/prompts.chat','sha':'a'*40,'files':[{'path':'prompts.csv','file':'0.txt','sha256':hashlib.sha256(content).hexdigest()}]}
  (folder/'manifest.json').write_text(json.dumps(manifest));return folder
 def test_parse_tracked_links(self):
  self.assertEqual(repository_name('https://github.com/f/prompts.chat?fbclid=ignored'),'f/prompts.chat')
  self.assertEqual(repository_name('https://github.com/harry0703/MoneyPrinterTurbo/blob/main/README-en.md'),'harry0703/MoneyPrinterTurbo')
  for value in ('https://evil.test/f/repo','../bad','owner/repo;cmd','https://github.com@evil.test/f/repo'):
   with self.assertRaises(ValueError):repository_name(value)
 def test_import_search_and_selected_reference(self):
  with tempfile.TemporaryDirectory() as temp:
   library=RepoLibrary(temp);folder=self.staged(library);self.assertEqual(library.install(folder),1)
   rows=library.search('video');self.assertEqual(rows[0][2],'Writer')
   self.assertEqual(selected_reference(temp,{}),'');self.assertIn('not permission',selected_reference(temp,{'selected_repo_card':rows[0][0]}))
   (folder/'0.txt').write_text('tampered')
   with self.assertRaises(ValueError):library.install(folder)
   self.assertEqual(len(library.search()),1)
 def test_outside_folder_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   with self.assertRaises(ValueError):RepoLibrary(temp).install(temp)

class DesktopPlanTests(unittest.TestCase):
 def test_screen_plan_validation(self):
  self.assertEqual(validate_plan({'action':'click','x':5,'y':10},(100,100))['x'],5)
  for plan in ({'action':'shell','text':'x'},{'action':'click','x':100,'y':1},{'action':'type','x':1,'y':1,'text':'hello\nenter'},{'action':'shortcut','x':1,'y':1,'shortcut':'run command'}):
   with self.assertRaises(ValueError):validate_plan(plan,(100,100))
  self.assertEqual(validate_plan({'action':'clarify','reason':'Choose a recipient'},(100,100))['action'],'clarify')
 def test_matching_prefers_shortcut_and_rejects_commands(self):
  entries=[AppEntry('Example','registered','App!Id'),AppEntry('Example','shortcut','example.lnk'),AppEntry('Example Beta','exe','example.exe')]
  self.assertEqual(match_entries('example',entries)[0].kind,'shortcut')
  with self.assertRaises(ValueError):match_entries('app; whoami',entries)

if __name__=='__main__':unittest.main()
