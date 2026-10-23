import types
import unittest
from voice_hub import VoiceHub
from portrait_assets import load_portrait
class Root:
 def after(self,*args):return 'timer'
 def after_cancel(self,*args):pass
class Engine:
 def __init__(self,cfg,emit):self.cfg=cfg;self.emit=emit;self.active=False;self.muted=types.SimpleNamespace(is_set=lambda:False);self.sent=[]
 def start(self):self.active=True;self.emit('state','LISTENING')
 def stop(self):self.active=False;self.emit('state','STOPPED')
 def send_text(self,text):self.sent.append(text);return True
 def mute(self,value):self.emit('state','MUTED' if value else 'LISTENING')
class UnifiedTests(unittest.TestCase):
 def test_voice_survives_page_navigation_and_text_uses_same_session(self):
  visual=[];display=[];hub=VoiceHub(Root(),{},lambda *e:visual.append(e),Engine);hub.sink=lambda *e:display.append(e)
  hub.start();hub.pump();self.assertEqual(hub.state,'LISTENING')
  hub.sink=None;self.assertTrue(hub.engine.active)
  self.assertTrue(hub.send_text('hello'));hub.pump();self.assertEqual(hub.engine.sent,['hello']);self.assertIn(('You','hello'),hub.history)
  hub.stop();hub.pump();self.assertEqual(hub.state,'STOPPED');hub.close()
 def test_saved_preferences_are_explicit_context(self):
  hub=VoiceHub(Root(),{},lambda *args:None,Engine,preferences=lambda:'Preferred language: Nepali')
  hub.start();self.assertEqual(hub.engine.cfg['personal_notes'],'Preferred language: Nepali');hub.close()
 def test_missing_old_portrait_falls_back(self):
  image=load_portrait('Z:/does-not-exist/old-photo.jpg');self.assertGreater(image.width,0)
if __name__=='__main__':unittest.main()
