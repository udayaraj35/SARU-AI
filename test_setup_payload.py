import os,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from installer_backend import prepare_python

class RuntimeTests(unittest.TestCase):
 def test_bundled_runtime_becomes_persistent_venv_base(self):
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp);target=folder/'SARU';target.mkdir();archive=folder/'runtime.zip'
   with zipfile.ZipFile(archive,'w') as output:output.writestr('python.exe',b'test');output.writestr('Lib/encodings/__init__.py',b'')
   with patch.dict(os.environ,{'SARU_BUNDLED_PYTHON_ZIP':str(archive)}),patch('installer_backend.subprocess.run') as runner:
    runner.return_value.returncode=0
    python=prepare_python(target,lambda line:None)
   self.assertEqual(runner.call_args.args[0][0],str(target/'.python-runtime'/'python.exe'))
   self.assertTrue((target/'.python-runtime'/'.complete').exists());self.assertEqual(python,target/'.venv'/'Scripts'/'python.exe')
 def test_runtime_traversal_is_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp);target=folder/'SARU';target.mkdir();archive=folder/'bad.zip'
   with zipfile.ZipFile(archive,'w') as output:output.writestr('../outside.txt',b'no')
   with patch.dict(os.environ,{'SARU_BUNDLED_PYTHON_ZIP':str(archive)}),patch('installer_backend.subprocess.run') as runner:
    with self.assertRaises(ValueError):prepare_python(target,lambda line:None)
   self.assertFalse((target/'outside.txt').exists());runner.assert_not_called()
if __name__=='__main__':unittest.main()
