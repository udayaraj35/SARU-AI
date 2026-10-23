import tempfile,unittest
from pathlib import Path
from message_outbox import MessageOutbox,schedule_intent
class Protector:
 def protect(self,data):return data.hex()
 def unprotect(self,data):return bytes.fromhex(data)
CFG={'whatsapp_phone_id':'12345','meta_graph_version':'v25.0','keys':{'WhatsApp Business':'test-only-token'}}
class OutboxTests(unittest.TestCase):
 def test_exact_schedule_and_one_attempt(self):
  self.assertEqual(schedule_intent('schedule whatsapp in 10 minutes to +9779800000000: Hello',1000),('outbox_add',(1600,'+9779800000000','Hello')))
  with tempfile.TemporaryDirectory() as temp:
   store=MessageOutbox(Path(temp)/'queue.sqlite',Protector());i=store.add(1100,'+9779800000000','Hello',CFG,now=1000)
   self.assertIsNone(store.claim(CFG,now=1099));self.assertEqual(store.claim(CFG,now=1100)[0],i);self.assertIsNone(store.claim(CFG,now=1101));store.close()
   store=MessageOutbox(Path(temp)/'queue.sqlite',Protector());self.assertEqual(store.list()[0][2],'needs_check');self.assertIsNone(store.claim(CFG,now=1102));store.close()
 def test_changed_account_expired_and_cancel_never_send(self):
  with tempfile.TemporaryDirectory() as temp:
   store=MessageOutbox(Path(temp)/'queue.sqlite',Protector());i=store.add(1100,'+9779800000000','Hello',CFG,now=1000)
   changed=dict(CFG,whatsapp_phone_id='54321');self.assertIsNone(store.claim(changed,now=1100));self.assertEqual(store.list()[0][2],'blocked')
   store.add(1200,'+9779800000000','Hello',CFG,now=1000);self.assertIsNone(store.claim(CFG,now=1900));self.assertEqual(store.list()[0][2],'expired')
   i=store.add(2000,'+9779800000000','Hello',CFG,now=1900);self.assertTrue(store.cancel(i));self.assertIsNone(store.claim(CFG,now=2000));store.close()
 def test_no_account_is_not_falsely_scheduled(self):
  with tempfile.TemporaryDirectory() as temp:
   store=MessageOutbox(Path(temp)/'queue.sqlite',Protector())
   with self.assertRaises(ValueError):store.add(2000,'+9779800000000','Hello',{},now=1000)
   self.assertEqual(store.list(),[]);store.close()
if __name__=='__main__':unittest.main()
