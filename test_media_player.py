import json
from pathlib import Path
import struct
import tempfile
import unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import wave
from media_library import MediaLibrary,youtube_id
from media_popup import MediaPopup
from voice_requests import voice_request,feature_request


class LibraryTests(unittest.TestCase):
 def test_youtube_urls_and_persistence(self):
  video='dQw4w9WgXcQ'
  for url in ('https://youtu.be/'+video,'https://www.youtube.com/watch?v='+video,'https://youtube.com/shorts/'+video):self.assertEqual(youtube_id(url),video)
  for url in ('file:///test','https://youtube.com.evil.test/watch?v='+video,'https://youtube.com/watch?v=no','https://youtu.be/'+video+';bad'):
   with self.assertRaises(ValueError):youtube_id(url)
  with tempfile.TemporaryDirectory() as temp:
   library=MediaLibrary(temp);row=library.add_youtube('https://youtu.be/'+video,'My favourite');library.add_youtube('https://youtu.be/'+video)
   self.assertEqual(MediaLibrary(temp).list(),[row])
 def test_local_import_and_real_mp3_clip(self):
  with tempfile.TemporaryDirectory() as temp:
   source=Path(temp)/'original.wav'
   with wave.open(str(source),'wb') as audio:
    audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(16000);audio.writeframes(struct.pack('<h',1000)*16000)
   library=MediaLibrary(Path(temp)/'data');row=library.import_file(source)
   self.assertEqual(library.local_path(row).read_bytes(),source.read_bytes())
   clip=library.trim_mp3(row['id'],.1,.5);self.assertGreater(library.local_path(clip).stat().st_size,100)
   self.assertTrue(source.exists())
   for start,end in ((-1,2),(1,0),(0,float('nan'))):
    with self.assertRaises(ValueError):library.trim_mp3(row['id'],start,end)
   with self.assertRaises(ValueError):library.trim_mp3(library.add_youtube('https://youtu.be/dQw4w9WgXcQ')['id'],0,1)
 def test_voice_requests_and_casual_conversation(self):
  self.assertEqual(voice_request('Saru improve saru add a player'),('self_improve','add a player'))
  self.assertEqual(voice_request('आफ्नो कोड सुधार नयाँ theme थप'),('self_improve','नयाँ theme थप'))
  self.assertEqual(voice_request('play saved video My favourite'),('media_play','My favourite'))
  for text in ('Facebook','I like youtube','the assistant said open notepad','Tell me a story'):
   self.assertEqual(voice_request(text),(None,None));self.assertFalse(feature_request(text))
  self.assertTrue(feature_request('Saru add a calendar reminder feature'))


class ServerTests(unittest.TestCase):
 def test_rapid_commands_are_queued_in_order(self):
  with tempfile.TemporaryDirectory() as temp:
   player=MediaPopup(temp)
   try:
    player.send('volume',60);player.send('next');player.send('pause')
    with urlopen(player.url+'commands?after=0') as response:rows=json.load(response)
    self.assertEqual([x['action'] for x in rows],['volume','next','pause'])
    with urlopen(player.url+'commands?after=2') as response:self.assertEqual([x['action'] for x in json.load(response)],['pause'])
    with self.assertRaises(ValueError):player.send('volume',200)
   finally:player.close()
 def test_video_commands_and_private_chat_pipe(self):
  from assistant_commands import parse_command
  from command_policy import direct_owner_action
  for phrase in ('pause video','video fullscreen','video small','video volume up','video volume down','next video'):
   action,args=parse_command(phrase);self.assertEqual(action,'media_control');self.assertTrue(direct_owner_action(action,args))
  self.assertEqual(parse_command('play youtube Nepali songs'),('media_search','Nepali songs'))
  from unittest.mock import patch,Mock
  with tempfile.TemporaryDirectory() as temp:
   player=MediaPopup(temp)
   try:
    process=Mock();process.poll.return_value=None;process.stdout=[]
    with patch('media_popup.subprocess.Popen',return_value=process) as start:
     player.open();player.open();self.assertEqual(start.call_count,1)
     self.assertIn('media_screen_host.py',start.call_args.args[0][1]);self.assertNotIn('--app=',str(start.call_args))
     player.chat('SARU: real reply\n');self.assertIn('real reply',process.stdin.write.call_args.args[0])
   finally:player.close()
 def test_session_guard_library_and_byte_ranges(self):
  with tempfile.TemporaryDirectory() as temp:
   player=MediaPopup(temp)
   try:
    with urlopen(player.url) as response:
     page=response.read().decode();self.assertIn('Save MP3 clip',page);self.assertNotIn('__BG__',page)
    with self.assertRaises(HTTPError) as error:urlopen(player.url.replace(player.token,'wrong'))
    self.assertEqual(error.exception.code,403)
    body=json.dumps({'url':'https://youtu.be/dQw4w9WgXcQ','title':'Test'}).encode()
    with self.assertRaises(HTTPError):urlopen(Request(player.url+'save',data=body))
    with urlopen(Request(player.url+'save',data=body,headers={'X-SARU-Token':player.token})) as response:self.assertEqual(json.load(response)['title'],'Test')
    source=Path(temp)/'clip.mp3';source.write_bytes(bytes(range(100)));row=player.library.import_file(source)
    with urlopen(Request(player.url+'file/'+row['id'],headers={'Range':'bytes=20-29'})) as response:
     self.assertEqual(response.status,206);self.assertEqual(response.read(),bytes(range(20,30)))
    player.send('select',row['id'])
    with urlopen(player.url+'command') as response:self.assertEqual(json.load(response)['value'],row['id'])
   finally:player.close()


if __name__=='__main__':unittest.main()
