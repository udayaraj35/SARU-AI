import tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
import numpy as np
from PIL import Image
from personal_reminders import ReminderStore,reminder_intent,format_due
from camera_companion import describe_frame
from voice_profiles import VoiceProfiles
from assistant_commands import parse_command

class IdentityProtector:
 def protect(self,data):return data.hex()
 def unprotect(self,data):return bytes.fromhex(data)

class PersonalTests(unittest.TestCase):
 def test_relative_due_freezes_exact_time(self):
  self.assertEqual(reminder_intent('remind me in 10 minutes to call',1000),('reminder_add',(1600,'call','reminder')))
  self.assertEqual(reminder_intent('5 minute paxi pani piu samjhau',1000)[1][0],1300)
  self.assertEqual(reminder_intent('alarm 25:00')[0],'invalid')
 def test_reminders_survive_restart_due_only_once_and_tasks_remain(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'reminders.sqlite';store=ReminderStore(path);identifier=store.add(100,'Call family');store.close();store=ReminderStore(path)
   self.assertEqual(len(store.due(101)),1);store.mark(identifier,'delivered');self.assertEqual(store.due(102),[]);self.assertEqual(len(store.outstanding()),1)
   store.mark(identifier,'cancelled');self.assertEqual(store.outstanding(),[]);store.close()
 def test_future_alarm_rolls_to_next_day(self):
  action,(due,title,kind)=reminder_intent('alarm 07:30: Wake up',1792660000)
  self.assertEqual(action,'reminder_add');self.assertGreater(due,1792660000);self.assertIn('07:30',format_due(due))
 def test_camera_sends_only_reviewed_frame_and_question(self):
  response=Mock();response.json.return_value={'candidates':[{'content':{'parts':[{'text':'A cup is visible.'}]}}]};session=Mock();session.post.return_value=response
  result=describe_frame(Image.new('RGB',(8,8)),'Where is cup?',{'keys':{'Gemini':'test-only'},'provider_models':{'Gemini':'vision'}},session)
  self.assertIn('cup',result);body=session.post.call_args.kwargs['json'];self.assertIn('absent say it is not visible',body['contents'][0]['parts'][0]['text'])
 def test_voice_sample_save_compare_delete_without_microphone(self):
  with tempfile.TemporaryDirectory() as temp:
   store=VoiceProfiles(temp,IdentityProtector());store.embedding=Mock(return_value=np.array([1.,0.,0.]))
   identifier=store.add('Test speaker',np.ones(64000,dtype=np.float32)*.1)
   self.assertNotIn('Test speaker',(Path(temp)/(identifier+'.voice')).read_text())
   self.assertIn('Possible voice match: Test speaker',store.match(np.ones(64000)))
   store.delete(identifier);self.assertEqual(store.profiles(),[])
 def test_camera_and_voice_commands(self):
  self.assertEqual(parse_command('open camera'),('camera','open'));self.assertEqual(parse_command('stop camera'),('camera','stop'))
  self.assertEqual(parse_command('save my voice as Udaya'),('voice_enroll','Udaya'))
  self.assertEqual(parse_command('compare my voice'),('voice_compare',None))
if __name__=='__main__':unittest.main()
