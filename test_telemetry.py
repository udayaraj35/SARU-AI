import unittest
from unittest.mock import patch,MagicMock
import types
import pc_telemetry as pc
class TelemetryTests(unittest.TestCase):
 def test_values_are_measured(self):
  with patch.object(pc.psutil,'cpu_percent',return_value=21.5),patch.object(pc.psutil,'virtual_memory',return_value=types.SimpleNamespace(percent=63)),patch.object(pc.psutil,'disk_usage',return_value=types.SimpleNamespace(percent=40)),patch.object(pc.psutil,'net_if_stats',return_value={'Wi-Fi':types.SimpleNamespace(isup=True)}),patch.object(pc,'read_controls',return_value={'volume':36,'brightness':None}):
   result=pc.snapshot();self.assertEqual(result['cpu'],21.5);self.assertEqual(result['adapters'],['Wi-Fi']);self.assertEqual(result['volume'],36);self.assertIsNone(result['brightness'])
 def test_volume_bounded_and_read_back(self):
  ep=MagicMock()
  with patch.object(pc,'endpoint',return_value=ep),patch.object(pc,'read_controls',return_value={'volume':100}):
   self.assertEqual(pc.set_control('volume',120),{'volume':100});ep.SetMasterVolumeLevelScalar.assert_called_once_with(1.0,None)
 def test_unknown_control_rejected(self):
  with self.assertRaises(ValueError):pc.set_control('shell',10)
if __name__=='__main__':unittest.main()
