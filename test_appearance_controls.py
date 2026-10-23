import unittest
from appearance_controls import frame_index
class AppearanceTests(unittest.TestCase):
 def test_stopped_and_muted_are_static(self):
  for state in ('STOPPED','MUTED','ERROR','IDLE'):
   self.assertEqual({frame_index(state,t/10) for t in range(100)},{7})
 def test_listening_changes_but_reduced_motion_is_static(self):
  self.assertGreater(len({frame_index('LISTENING',t/10) for t in range(100)}),3)
  self.assertEqual({frame_index('SPEAKING',t/10,True) for t in range(100)},{7})
if __name__=='__main__':unittest.main()
