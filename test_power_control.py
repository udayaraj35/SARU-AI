import unittest
from unittest.mock import Mock
from types import SimpleNamespace
from assistant_commands import parse_command
from voice_requests import voice_request
from power_control import request_power

class PowerTests(unittest.TestCase):
 def test_owner_commands_and_voice_route(self):
  for phrase,action in [('pc off gara','shutdown'),('पीसी बन्द गर','shutdown'),('pc luck gara','lock'),('sleep mode','sleep'),('slip mood ma rakha','sleep'),('cancel shutdown','cancel_shutdown')]:
   self.assertEqual(parse_command(phrase),('power',action))
   self.assertEqual(voice_request(phrase),('power',action))
  self.assertNotEqual(parse_command('remember shutdown pc')[0],'power')
 def test_shutdown_is_delayed_not_forced_and_cancel_is_separate(self):
  runner=Mock(return_value=SimpleNamespace(returncode=0))
  self.assertIn('30 seconds',request_power('shutdown',runner=runner))
  self.assertEqual(runner.call_args.args[0][1:],['/s','/t','30'])
  request_power('cancel_shutdown',runner=runner)
  self.assertEqual(runner.call_args.args[0][1:],['/a'])
 def test_lock_sleep_are_injected_without_affecting_pc(self):
  lock=Mock();sleep=Mock()
  request_power('lock',lock=lock);request_power('sleep',sleep=sleep)
  lock.assert_called_once_with();sleep.assert_called_once_with()
 def test_failure_and_unknown_action(self):
  runner=Mock(return_value=SimpleNamespace(returncode=5,stderr='Access denied',stdout=''))
  with self.assertRaisesRegex(RuntimeError,'Access denied'):request_power('shutdown',runner=runner)
  with self.assertRaises(ValueError):request_power('restart arbitrary command',runner=runner)
  self.assertEqual(runner.call_count,1)
if __name__=='__main__':unittest.main()
