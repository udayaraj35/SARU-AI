import unittest
from startup_screen import StartupProgress,STAGES

class StartupTests(unittest.TestCase):
 def test_progress_tracks_completed_checks_only(self):
  progress=StartupProgress();self.assertEqual(progress.percent,0);self.assertFalse(progress.ready())
  with self.assertRaises(ValueError):progress.complete('interface')
  for index,(key,_) in enumerate(STAGES):
   progress.complete(key);self.assertEqual(progress.percent,round((index+1)*100/len(STAGES)))
  self.assertTrue(progress.ready())
  with self.assertRaises(ValueError):progress.complete('runtime')
 def test_error_never_counts_as_ready(self):
  progress=StartupProgress()
  for key,_ in STAGES:progress.complete(key)
  progress.error='A startup check failed';self.assertFalse(progress.ready())

if __name__=='__main__':unittest.main()
