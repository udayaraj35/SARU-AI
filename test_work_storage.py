from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from work_storage import ask_work_save,work_directory

class WorkStorageTests(unittest.TestCase):
 def test_cancel_creates_no_deliverable(self):
  with tempfile.TemporaryDirectory() as folder:
   cfg={'work_folder':str(Path(folder)/'Work')}
   with patch('work_storage.filedialog.asksaveasfilename',return_value='') as ask:
    self.assertEqual(ask_work_save(cfg,defaultextension='.pdf'),'')
   self.assertTrue(ask.call_args.kwargs['confirmoverwrite'])
   self.assertEqual(ask.call_args.kwargs['initialdir'],cfg['work_folder'])
   self.assertEqual(list(work_directory(cfg).iterdir()),[])
 def test_user_can_choose_another_folder(self):
  with tempfile.TemporaryDirectory() as folder:
   output=str(Path(folder)/'elsewhere.pdf')
   with patch('work_storage.filedialog.asksaveasfilename',return_value=output):
    self.assertEqual(ask_work_save({'work_folder':folder}),output)
   self.assertFalse(Path(output).exists())

if __name__=='__main__':unittest.main()
