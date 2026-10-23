"""Time-limited owner verification for reviewed SARU source edits."""
import hashlib,hmac,secrets,time


def hash_code(code):
 salt=secrets.token_bytes(16)
 return salt.hex()+':'+hashlib.pbkdf2_hmac('sha256',code.encode(),salt,250000).hex()

class EditAuthorization:
 def __init__(self,clock=time.monotonic):self.clock=clock;self.until=0;self.failures=0;self.blocked_until=0
 def active(self):return self.clock()<self.until
 def verify(self,code,encoded):
  if self.clock()<self.blocked_until:return False
  try:
   salt,digest=encoded.split(':');actual=hashlib.pbkdf2_hmac('sha256',code.encode(),bytes.fromhex(salt),250000)
   valid=hmac.compare_digest(actual,bytes.fromhex(digest))
  except (ValueError,TypeError,AttributeError):valid=False
  if valid:self.failures=0;self.until=self.clock()+600
  else:
   self.failures+=1
   if self.failures>=5:self.blocked_until=self.clock()+60;self.failures=0
  return valid
