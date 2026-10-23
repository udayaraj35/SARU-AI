import unittest
from unittest.mock import patch,Mock
import subprocess
import pc_telemetry as pc
class DeviceIsolationTests(unittest.TestCase):
 def test_native_crash_becomes_device_error(self):
  with patch('subprocess.run',return_value=Mock(returncode=3221225477,stdout='')):
   with self.assertRaises(RuntimeError):pc.device_request()
 def test_timeout_does_not_escape_telemetry(self):
  with patch.object(pc,'device_request',side_effect=subprocess.TimeoutExpired('device',15)):
   result=pc.isolated_snapshot();self.assertIsNone(result['volume']);self.assertIn('cpu',result)
 def test_result_plain_data(self):
  with patch('subprocess.run',return_value=Mock(returncode=0,stdout='{"volume":45,"brightness":null}')):
   self.assertEqual(pc.device_request()['volume'],45)
if __name__=='__main__':unittest.main()
