import threading,unittest
from smooth_controls import LatestControls
class SmoothTests(unittest.TestCase):
 def test_drag_coalesces_and_keeps_last_value(self):
  class Client:
   def __init__(self):self.calls=[];self.started=threading.Event();self.release=threading.Event()
   def set(self,name,value):
    self.calls.append((name,value))
    if len(self.calls)==1:self.started.set();self.release.wait(2)
    return {name:value}
   def close(self):self.release.set()
  client=Client();controls=LatestControls(client)
  try:
   controls.set('volume',10);self.assertTrue(client.started.wait(1))
   for value in range(11,91):last=controls.set('volume',value)
   client.release.set();first=controls.events.get(timeout=2);second=controls.events.get(timeout=2)
   self.assertEqual(client.calls,[('volume',10),('volume',90)])
   self.assertEqual(second[:3],('volume',last,{'volume':90}))
  finally:controls.close()
 def test_failure_is_reported_and_worker_survives(self):
  class Client:
   def set(self,name,value):raise RuntimeError('device offline')
   def close(self):pass
  controls=LatestControls(Client())
  try:
   version=controls.set('brightness',50);event=controls.events.get(timeout=2)
   self.assertEqual(event[:2],('brightness',version));self.assertEqual(event[3],'device offline')
   controls.set('volume',40);self.assertEqual(controls.events.get(timeout=2)[0],'volume')
  finally:controls.close()
 def test_bounds_and_close(self):
  class Client:
   def set(self,name,value):return {name:value}
   def close(self):pass
  controls=LatestControls(Client())
  controls.set('volume',900);self.assertEqual(controls.events.get(timeout=2)[2],{'volume':100});controls.close()
  with self.assertRaises(RuntimeError):controls.set('volume',10)
if __name__=='__main__':unittest.main()
