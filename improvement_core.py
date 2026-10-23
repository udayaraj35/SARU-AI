"""Reviewed, bounded self-edit proposals. Candidate code is never executed by validation."""
import ast,difflib,hashlib,json,os,shutil,uuid,tempfile
from pathlib import Path

PROTECTED={'owner_edit.py','improvement_core.py','improvement_ui.py','improvement_ai.py','settings_store.py','install_support.py','installer.py','installer_backend.py','launch_saru.py','update_manager.py','automatic_updates.py','version.py','recover_saru.py'}

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True).encode('utf-8')

class ImprovementManager:
 def __init__(self,root,data):
  self.root=Path(root).resolve();self.directory=Path(data)/'improvements';self.directory.mkdir(parents=True,exist_ok=True)
  if not (self.root/'app.py').is_file():raise ValueError('Choose the SARU application folder.')
 def target(self,name):
  if not isinstance(name,str) or Path(name).name!=name or any(c in name for c in ('/','\\',':')):raise ValueError('Only files directly inside SARU can be changed.')
  if name.casefold() in PROTECTED or name.startswith(('test_','smoke_','preview_')) or Path(name).suffix.lower() not in ('.py','.md'):raise ValueError('This file is not editable through Self Improvement: '+name)
  path=self.root/name
  if path.is_symlink() or path.resolve().parent!=self.root or not path.is_file():raise ValueError('Choose an existing regular SARU source file.')
  return path
 def available(self):
  result=[]
  for path in self.root.iterdir():
   try:self.target(path.name);result.append(path.name)
   except ValueError:pass
  return sorted(result)
 def snapshot(self,names):
  if not 1<=len(names)<=8:raise ValueError('Select 1–8 source files.')
  files={name:self.target(name).read_text(encoding='utf-8-sig') for name in names}
  if sum(len(text) for text in files.values())>180000:raise ValueError('Selected source exceeds 180,000 characters; select fewer files.')
  return files
 def folder(self,identifier):
  if not isinstance(identifier,str) or len(identifier)!=32 or any(c not in '0123456789abcdef' for c in identifier):raise ValueError('Invalid proposal identifier.')
  path=self.directory/identifier
  if path.is_symlink():raise ValueError('Invalid proposal directory.')
  return path
 def stage(self,response,originals,request):
  if len(response)>250000:raise ValueError('Proposal response is too large.')
  text=response.strip()
  if text.startswith('```'):text='\n'.join(text.splitlines()[1:-1])
  result=json.loads(text);changes=result.get('changes')
  if not isinstance(changes,list) or not 1<=len(changes)<=8:raise ValueError('Proposal needs 1–8 changed files.')
  staged=[];seen=set();diff=[]
  for change in changes:
   name=change['path'];path=self.target(name)
   if name not in originals or name in seen:raise ValueError('A proposal may only edit selected files, once per file.')
   seen.add(name);before=originals[name]
   if path.read_text(encoding='utf-8-sig')!=before:raise ValueError('Source changed while generating. Generate a fresh proposal.')
   after=before;edits=change.get('edits',[])
   if not isinstance(edits,list) or not 1<=len(edits)<=30:raise ValueError('Each file needs 1–30 exact edits.')
   for edit in edits:
    old=edit['old'];new=edit['new']
    if not isinstance(old,str) or not old or not isinstance(new,str) or after.count(old)!=1:raise ValueError('Edit anchor is missing or ambiguous in '+name)
    after=after.replace(old,new,1)
   if after==before:raise ValueError('Proposal made no change to '+name)
   if len(after)>300000:raise ValueError('Changed file is too large.')
   if path.suffix.lower()=='.py':ast.parse(after,filename=name);compile(after,name,'exec')
   staged.append({'path':name,'before':before,'after':after,'base_hash':sha(path.read_bytes()),'new_hash':sha(after.encode('utf-8'))})
   diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/'+name,tofile='after/'+name))
  identifier=uuid.uuid4().hex;folder=self.folder(identifier);folder.mkdir()
  proposal={'root':str(self.root),'request':request,'summary':str(result.get('summary',''))[:4000],'changes':staged,'diff':''.join(diff)}
  checksum=sha(canonical(proposal));(folder/'proposal.json').write_bytes(canonical(proposal));(folder/'review.diff').write_text(''.join(diff),encoding='utf-8')
  self.state(folder,{'state':'ready','digest':checksum})
  return identifier,proposal,checksum
 def state(self,folder,value):
  temporary=folder/'state.tmp';temporary.write_bytes(canonical(value));temporary.replace(folder/'state.json')
 def load(self,identifier):
  folder=self.folder(identifier);proposal=json.loads((folder/'proposal.json').read_text(encoding='utf-8'));state=json.loads((folder/'state.json').read_text(encoding='utf-8'))
  if proposal['root']!=str(self.root) or sha(canonical(proposal))!=state['digest']:raise ValueError('Proposal integrity/root mismatch. Generate a new proposal.')
  return proposal,state
 def write_source(self,path,data):
  descriptor,name=tempfile.mkstemp(prefix='.saru-edit-',suffix='.tmp',dir=self.root)
  temporary=Path(name)
  try:
   with os.fdopen(descriptor,'wb') as output:output.write(data);output.flush();os.fsync(output.fileno())
   os.replace(temporary,path)
  finally:temporary.unlink(missing_ok=True)
 def apply(self,identifier,reviewed_digest):
  folder=self.folder(identifier);proposal,state=self.load(identifier)
  if state['state']!='ready' or state['digest']!=reviewed_digest:raise ValueError('This exact proposal must be reviewed before applying.')
  for change in proposal['changes']:
   path=self.target(change['path'])
   if sha(path.read_bytes())!=change['base_hash'] or path.read_text(encoding='utf-8-sig')!=change['before']:raise ValueError('Current source changed. Regenerate instead of overwriting it.')
   if path.suffix.lower()=='.py':compile(change['after'],change['path'],'exec')
  backup=folder/'backup';backup.mkdir(exist_ok=False);written=[]
  try:
   for change in proposal['changes']:
    path=self.target(change['path']);shutil.copy2(path,backup/change['path'])
   self.state(folder,{**state,'state':'applying'})
   for change in proposal['changes']:
    path=self.target(change['path'])
    if sha(path.read_bytes())!=change['base_hash']:raise ValueError('Source changed during apply; no concurrent edits will be overwritten.')
    self.write_source(path,change['after'].encode('utf-8'));written.append(change)
  except Exception:
   for change in reversed(written):
    path=self.root/change['path']
    if sha(path.read_bytes())==change['new_hash']:self.write_source(path,(backup/change['path']).read_bytes())
   self.state(folder,{**state,'state':'apply_failed'});raise
  self.state(folder,{**state,'state':'applied'})
  return [change['path'] for change in proposal['changes']]
 def rollback(self,identifier):
  folder=self.folder(identifier);proposal,state=self.load(identifier)
  if state['state']!='applied':raise ValueError('Only an applied change can be rolled back.')
  for change in proposal['changes']:
   path=self.target(change['path']);saved=folder/'backup'/change['path']
   if sha(path.read_bytes())!=change['new_hash'] or sha(saved.read_bytes())!=change['base_hash']:raise ValueError('Files changed after applying, or backup integrity failed. Rollback refused to preserve your edits.')
  restored=[]
  try:
   for change in proposal['changes']:
    self.write_source(self.target(change['path']),(folder/'backup'/change['path']).read_bytes());restored.append(change)
  except Exception:
   for change in reversed(restored):
    path=self.target(change['path'])
    if sha(path.read_bytes())==change['base_hash']:self.write_source(path,change['after'].encode('utf-8'))
   self.state(folder,{**state,'state':'rollback_failed'});raise
  self.state(folder,{**state,'state':'rolled_back'})
 def recent(self):
  found=[]
  for folder in sorted(self.directory.iterdir(),key=lambda p:p.stat().st_mtime,reverse=True):
   try:
    proposal,state=self.load(folder.name);found.append((folder.name,proposal['summary'],state['state']))
   except (ValueError,OSError,KeyError):continue
  return found[:30]
