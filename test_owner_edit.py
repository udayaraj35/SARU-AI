import unittest
from owner_edit import hash_code,EditAuthorization
class OwnerEditTests(unittest.TestCase):
 def test_salted_hash_and_expiry(self):
  code='test-owner-only';first=hash_code(code);self.assertNotIn(code,first);self.assertNotEqual(first,hash_code(code))
  now=[10];auth=EditAuthorization(lambda:now[0]);self.assertFalse(auth.active());self.assertTrue(auth.verify(code,first));self.assertTrue(auth.active());now[0]=611;self.assertFalse(auth.active())
 def test_wrong_code_rate_limit_and_malformed_hash(self):
  now=[0];auth=EditAuthorization(lambda:now[0]);encoded=hash_code('test-only')
  for _ in range(5):self.assertFalse(auth.verify('wrong',encoded))
  self.assertFalse(auth.verify('test-only',encoded));now[0]=61;self.assertTrue(auth.verify('test-only',encoded))
  self.assertFalse(auth.verify('test-only','malformed'))
if __name__=='__main__':unittest.main()
