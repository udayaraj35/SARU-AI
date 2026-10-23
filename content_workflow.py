"""Durable drafts with exact-content approval and no automatic publish retries."""
import hashlib,json,shutil,sqlite3,uuid
from contextlib import contextmanager
from pathlib import Path
from video_publishers import video_file,upload_video

def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as source:
  for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def safe_error(exc):
 import requests
 if isinstance(exc,requests.RequestException):return 'Network outcome uncertain. Check the destination before creating another upload.'
 if isinstance(exc,(ValueError,RuntimeError)):return str(exc)
 return type(exc).__name__+': operation failed; no automatic retry.'

class PublishStore:
 def __init__(self,data):
  self.root=Path(data)/'content_studio';self.root.mkdir(parents=True,exist_ok=True);self.db=self.root/'drafts.db'
  with self.connect() as con:
   con.execute('create table if not exists drafts(id text primary key, payload text, state text, receipt text default \'\', approval_hash text default \'\')')
   if 'approval_hash' not in {row[1] for row in con.execute('pragma table_info(drafts)')}:con.execute("alter table drafts add column approval_hash text default ''")
 @contextmanager
 def connect(self):
  connection=sqlite3.connect(self.db)
  try:
   with connection:yield connection
  finally:connection.close()
 def create(self,path,platform,title,description,privacy,account,kids,flags):
  path=video_file(path)
  if not title.strip() or len(title)>100:raise ValueError('Enter a title of 1–100 characters.')
  if len(description)>5000:raise ValueError('Description is too long (maximum 5000).')
  if platform=='TikTok':
   if len((title+'\n'+description).encode('utf-16-le'))//2>2200:raise ValueError('TikTok title/caption exceeds 2200 characters.')
   if flags.get('brand_content') and privacy=='SELF_ONLY':raise ValueError('Paid partnership content cannot use private visibility.')
  if privacy not in account['privacy']:raise ValueError('Choose one of the connected account visibility options.')
  identifier=uuid.uuid4().hex;staged=self.root/(identifier+'.mp4')
  try:
   shutil.copyfile(path,staged)
   payload={'path':str(staged),'original_name':path.name,'platform':platform,'title':title.strip(),'description':description,'privacy':privacy,'destination_id':str(account['id']),'destination_name':account['name'],'kids':bool(kids),'flags':dict(flags),'sha256':digest(staged)}
   with self.connect() as con:con.execute('insert into drafts(id,payload,state) values(?,?,?)',(identifier,json.dumps(payload,ensure_ascii=False),'ready'))
  except Exception:staged.unlink(missing_ok=True);raise
  return identifier,payload
 def get(self,identifier):
  with self.connect() as con:row=con.execute('select payload,state,receipt from drafts where id=?',(identifier,)).fetchone()
  if not row:raise ValueError('Draft not found.')
  return json.loads(row[0]),row[1],json.loads(row[2]) if row[2] else None
 def fingerprint(self,payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
 def approve(self,identifier):
  payload,state,_=self.get(identifier)
  if state!='ready':raise ValueError('Only a new ready draft can be approved.')
  if digest(payload['path'])!=payload['sha256']:raise ValueError('Video changed. Create a new draft and review it again.')
  with self.connect() as con:
   if con.execute("update drafts set state='approved',approval_hash=? where id=? and state='ready'",(self.fingerprint(payload),identifier)).rowcount!=1:raise ValueError('Draft is already in use.')
 def publish(self,identifier,config,publisher=upload_video):
  payload,state,_=self.get(identifier)
  if state!='approved':raise ValueError('Explicit approval is required; this draft cannot be uploaded again.')
  with self.connect() as con:approved_hash=con.execute('select approval_hash from drafts where id=?',(identifier,)).fetchone()[0]
  if approved_hash!=self.fingerprint(payload):raise ValueError('Approved details changed. Prepare and approve a new draft.')
  if digest(payload['path'])!=payload['sha256']:raise ValueError('Reviewed video changed. Prepare a new draft.')
  with self.connect() as con:
   if con.execute("update drafts set state='uploading' where id=? and state='approved'",(identifier,)).rowcount!=1:raise ValueError('Draft already submitted.')
  try:
   receipt=publisher(payload,config)
   with self.connect() as con:con.execute('update drafts set state=?,receipt=? where id=?',(receipt['state'],json.dumps(receipt),identifier))
   return receipt
  except Exception as exc:
   # An HTTP timeout can happen after the server accepted the video. Never resend.
   with self.connect() as con:con.execute("update drafts set state='needs_check',receipt=? where id=?",(json.dumps({'error':safe_error(exc)}),identifier))
   raise
 def recent(self):
  with self.connect() as con:rows=con.execute('select id,payload,state,receipt from drafts order by rowid desc limit 20').fetchall()
  return [(identifier,json.loads(payload),state,json.loads(receipt) if receipt else {}) for identifier,payload,state,receipt in rows]
