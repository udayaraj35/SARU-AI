"""Local searchable conversation/work journal. No audio recordings or credentials."""
import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime,timezone
from pathlib import Path
from secret_handling import safe_memory_text

def clean(text,config=None):
 text=str(text or '')
 for value in (config or {}).get('keys',{}).values():
  if isinstance(value,str) and len(value)>7:text=text.replace(value,'[credential withheld]')
 return safe_memory_text(text)

class MemoryJournal:
 def __init__(self,connection,config=None):
  self.db=connection;self.config=config if config is not None else {};self.sync_warnings=[]
  connection.execute('CREATE TABLE IF NOT EXISTS memory_journal(id INTEGER PRIMARY KEY, source TEXT UNIQUE, kind TEXT, title TEXT, content TEXT, created_at TEXT, updated_at TEXT)')
  connection.execute('CREATE TABLE IF NOT EXISTS memory_sync(source TEXT PRIMARY KEY, cursor INTEGER)')
  connection.execute('CREATE INDEX IF NOT EXISTS memory_kind ON memory_journal(kind,id)')
  connection.commit()
 def record(self,kind,title,content,source=None,at=None,explicit=False):
  if not explicit and not self.config.get('remember_conversations',True):return
  title=clean(title,self.config)[:240];content=clean(content,self.config)
  if not content.strip():return
  now=datetime.now(timezone.utc).isoformat(timespec='seconds')
  self.db.execute('INSERT INTO memory_journal(source,kind,title,content,created_at,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(source) DO UPDATE SET title=excluded.title,content=excluded.content,updated_at=CASE WHEN memory_journal.content!=excluded.content OR memory_journal.title!=excluded.title THEN excluded.updated_at ELSE memory_journal.updated_at END',(source,kind,title,content,str(at)[:100] if at else now,now));self.db.commit()
 def sync(self,folder):
  self.sync_warnings=[]
  try:self._sync(folder)
  except (sqlite3.Error,OSError,ValueError,TypeError) as exc:self.sync_warnings.append(clean(str(exc),self.config)[:240])
 def _sync(self,folder):
  if not self.config.get('remember_conversations',True):return
  for table,kind in [('messages','conversation'),('notes','note')]:
   if not self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():continue
   cursor=self.db.execute('SELECT cursor FROM memory_sync WHERE source=?',(table,)).fetchone()
   cursor=cursor[0] if cursor else 0
   columns='id,role,content' if table=='messages' else 'id,title,content'
   for number,title,text in self.db.execute('SELECT '+columns+' FROM '+table+' WHERE id>? ORDER BY id',(cursor,)).fetchall():
    self.record(kind,title,text,table+':'+str(number),at='Imported; original timestamp unavailable');cursor=number
   self.db.execute('INSERT OR REPLACE INTO memory_sync VALUES(?,?)',(table,cursor));self.db.commit()
  folder=Path(folder);tasks=folder/'agent_tasks.jsonl'
  if tasks.is_file():
   row=self.db.execute("SELECT cursor FROM memory_sync WHERE source='tasks'").fetchone();offset=row[0] if row else 0
   if tasks.stat().st_size<offset:offset=0
   with tasks.open('rb') as stream:
    stream.seek(offset)
    while True:
     start=stream.tell();line=stream.readline(1024*1024)
     if not line or not line.endswith(b'\n'):break
     try:
      task=json.loads(line);self.record('task',task.get('action','Task'),str(task.get('command',''))+'\nResult: '+str(task.get('result','')),'tasks:'+str(start),task.get('at'))
     except (ValueError,UnicodeError,AttributeError):pass
     offset=stream.tell()
   self.db.execute("INSERT OR REPLACE INTO memory_sync VALUES('tasks',?)",(offset,));self.db.commit()
  office=folder/'office/office.db'
  if office.is_file():
   with closing(sqlite3.connect(office.as_uri()+'?mode=ro',uri=True,timeout=2)) as other:
    if other.execute("SELECT 1 FROM sqlite_master WHERE name='jobs'").fetchone():
     for job,task,state,result,review,error in other.execute('SELECT id,task,state,result,review,error FROM jobs'):
      self.record('office',task,'State: '+str(state)+'\nResult: '+str(result or '')+'\nReview: '+str(review or '')+'\nError: '+str(error or ''),'office:'+job)
    if other.execute("SELECT 1 FROM sqlite_master WHERE name='exports'").fetchone():
     for job,path,fmt in other.execute('SELECT job,path,format FROM exports'):
      self.record('file','Office '+str(fmt)+' export',path,'export:'+job+':'+path)
 def search(self,query='',limit=12,kind='all'):
  limit=max(1,min(int(limit),100));terms=list(dict.fromkeys(re.findall(r'[\w\u0900-\u097f]{2,}',str(query).casefold())))[:10]
  clauses=[];args=[]
  if kind!='all':clauses.append('kind=?');args.append(kind)
  if terms:
   matches=[]
   for term in terms:
    matches.append("lower(title||' '||content) LIKE ? ESCAPE '\\'");args.append('%'+term.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
   clauses.append('('+' OR '.join(matches)+')')
  elif query.strip():return []
  sql='SELECT id,kind,title,content,created_at,updated_at FROM memory_journal'
  if clauses:sql+=' WHERE '+' AND '.join(clauses)
  order='id DESC'
  if terms:
   order='('+'+'.join("CASE WHEN lower(title||' '||content) LIKE ? ESCAPE '\\' THEN 1 ELSE 0 END" for _ in terms)+') DESC,id DESC'
   args.extend('%'+term.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%' for term in terms)
  rows=self.db.execute(sql+' ORDER BY '+order+' LIMIT ?',args+[limit])
  return [{'id':row[0],'kind':row[1],'title':clean(row[2],self.config),'content':clean(row[3],self.config),'created_at':row[4],'updated_at':row[5]} for row in rows]
 def context(self,query,limit=6):
  rows=self.search(query,limit);budget=6500;result=[]
  for row in rows:
   snippet=json.dumps({key:row[key] for key in ('kind','title','content')},ensure_ascii=False)[:min(1400,budget)]
   if budget<=0:break
   result.append(snippet);budget-=len(snippet)
  return '\n'.join(result)
 def counts(self):return dict(self.db.execute('SELECT kind,count(*) FROM memory_journal GROUP BY kind'))

def live_lookup(path,config,query):
 if not config.get('remember_conversations',True):return 'Automatic memory lookup is disabled.'
 if not str(query).strip():return 'Provide a specific memory topic to search.'
 with closing(sqlite3.connect(path,timeout=3)) as db:
  journal=MemoryJournal(db,config);journal.sync(Path(path).parent)
  result=journal.context(str(query)[:500]) or 'No matching saved memory. Do not invent a memory.'
  if journal.sync_warnings:result+='\nSome local records could not be synchronized; do not assume this is complete.'
  return result
