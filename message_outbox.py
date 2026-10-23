"""Explicit scheduled WhatsApp Business messages; at-most-once attempts and no hidden retries."""
import hashlib,json,re,sqlite3,time
from settings_store import WindowsProtector


def schedule_intent(text,now=None):
 now=time.time() if now is None else now
 if text.casefold().strip() in ('show scheduled messages','show outbox','scheduled whatsapp'):return 'outbox_list',None
 cancel=re.fullmatch(r'cancel scheduled message (\d+)',text,re.I)
 if cancel:return 'outbox_cancel',int(cancel[1])
 match=re.fullmatch(r'schedule whatsapp in (\d+) (minutes?|hours?) to (\+?[1-9]\d{6,14}): (.{1,4096})',text,re.I|re.S)
 if match:
  delay=int(match[1])*(60 if match[2].casefold().startswith('minute') else 3600)
  if not 60<=delay<=30*86400:return 'invalid','Schedule messages 1 minute to 30 days ahead.'
  return 'outbox_add',(now+delay,match[3],match[4])
 return None


def account_signature(config):
 values=[config.get('whatsapp_phone_id',''),config.get('meta_graph_version',''),config.get('keys',{}).get('WhatsApp Business','')]
 if not str(values[0]).isdigit() or not re.fullmatch(r'v\d+\.\d+',values[1]) or not values[2]:raise ValueError('Connect your WhatsApp Business phone ID/token and Meta API version in Social accounts first. Personal WhatsApp Web is not an unattended API sender.')
 return hashlib.sha256(json.dumps(values).encode()).hexdigest()

class MessageOutbox:
 def __init__(self,path,protector=None):
  self.db=sqlite3.connect(path);self.protector=protector or WindowsProtector()
  self.db.execute('CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY,due REAL,payload TEXT,account TEXT,state TEXT,note TEXT)')
  self.db.execute('UPDATE outbox SET state="needs_check",note="Interrupted attempt; check account before any manual retry." WHERE state="sending"');self.db.commit()
 def add(self,due,target,message,config,now=None):
  now=time.time() if now is None else now
  if not now<due<=now+30*86400 or not re.fullmatch(r'\+?[1-9]\d{6,14}',target) or not 1<=len(message.strip())<=4096:raise ValueError('Specify a future time, international recipient and exact message.')
  signature=account_signature(config);payload=self.protector.protect(json.dumps({'target':target,'message':message},ensure_ascii=False).encode())
  cur=self.db.execute('INSERT INTO outbox(due,payload,account,state,note) VALUES(?,?,?,"scheduled","")',(due,payload,signature));self.db.commit();return cur.lastrowid
 def list(self):return self.db.execute('SELECT id,due,state,note FROM outbox ORDER BY id DESC LIMIT 100').fetchall()
 def claim(self,config,now=None):
  now=time.time() if now is None else now
  row=self.db.execute('SELECT id,due,payload,account FROM outbox WHERE state="scheduled" AND due<=? ORDER BY due LIMIT 1',(now,)).fetchone()
  if not row:return None
  identifier,due,payload,account=row
  if now-due>600:self.finish(identifier,'expired','Not sent: SARU was not available within ten minutes of due time.');return None
  try:signature=account_signature(config)
  except ValueError:self.finish(identifier,'blocked','Account configuration missing; not sent.');return None
  if signature!=account:self.finish(identifier,'blocked','WhatsApp account/token changed; not sent.');return None
  changed=self.db.execute('UPDATE outbox SET state="sending" WHERE id=? AND state="scheduled"',(identifier,)).rowcount;self.db.commit()
  if not changed:return None
  try:body=json.loads(self.protector.unprotect(payload).decode())
  except Exception:self.finish(identifier,'blocked','Saved message could not be decrypted; not sent.');return None
  return identifier,body
 def finish(self,identifier,state,note):
  if state not in ('accepted','needs_check','blocked','expired','cancelled'):raise ValueError('Invalid outbox state')
  self.db.execute('UPDATE outbox SET state=?,note=? WHERE id=?',(state,note[:500],identifier));self.db.commit()
 def cancel(self,identifier):
  changed=self.db.execute('UPDATE outbox SET state="cancelled",note="Cancelled by owner." WHERE id=? AND state="scheduled"',(identifier,)).rowcount;self.db.commit();return bool(changed)
 def close(self):self.db.close()
