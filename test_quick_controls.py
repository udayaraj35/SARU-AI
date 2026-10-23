import unittest
from types import SimpleNamespace
from assistant_commands import parse_command
from floating_companion import FloatingCompanion

class DesktopRequests(unittest.TestCase):
 def test_paraphrases(self):
  cases={'could you open Chrome please':('browser','chrome'),'Saru, please open calculator for me':('app','Calculator'),'set volume to 40 percent':('volume','40'),'take a screenshot please':('screenshot',None),'show my screen':('pc_control',None),'please open Notepad':('notepad',None),'remember please call me tomorrow':('note','please call me tomorrow')}
  for text,result in cases.items():self.assertEqual(parse_command(text),result,text)
 def test_double_cancels_single(self):
  events=[]
  fake=SimpleNamespace(click_job='pending',after_cancel=lambda job:events.append('cancel'),controls=None,on_open=lambda:events.append('main'),drag=None,suppress_release=False)
  FloatingCompanion.double_click(fake)
  FloatingCompanion.up(fake,None)
  self.assertEqual(events,['cancel','main']);self.assertFalse(fake.suppress_release)
 def test_nepali_paraphrases(self):
  self.assertEqual(parse_command('Chrome खोलिदेऊ'),('browser','chrome'))
  self.assertEqual(parse_command('कृपया आवाज ४० प्रतिशत बनाइदेऊ'),('volume','40'))
  self.assertEqual(parse_command('मलाई स्क्रिन देखाऊ'),('pc_control',None))
  for text in ('could you explain how screenshots work','please write a story about Facebook','what is brightness'):
   self.assertEqual(parse_command(text),(None,None))
 def test_single_delays(self):
  events=[]
  fake=SimpleNamespace(drag=(0,0,0,0,False),suppress_release=False,click_job=None,after=lambda delay,callback:events.append(callback) or 'timer',toggle_controls=lambda:None)
  FloatingCompanion.up(fake,None)
  self.assertEqual(events,[fake.toggle_controls]);self.assertEqual(fake.click_job,'timer')
 def test_drag_does_not_open(self):
  events=[]
  fake=SimpleNamespace(drag=(0,0,0,0,True),suppress_release=False,winfo_x=lambda:100,winfo_y=lambda:100,master=SimpleNamespace(winfo_screenwidth=lambda:1920,winfo_screenheight=lambda:1080),cfg={'orb_snap':False},width=100,height=150,geometry=lambda value:None,save_config=lambda:events.append('saved'))
  FloatingCompanion.up(fake,None);self.assertEqual(events,['saved'])

if __name__=='__main__':unittest.main()
