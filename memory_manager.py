"""Private SQLite facts and local multilingual FAISS retrieval.

The journal remains the source of truth. Vectors are rebuildable, never permissions.
Heavy model work runs on one background worker, never the Tk thread.
"""
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import threading
import time
from secret_handling import safe_memory_text, contains_secret

MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
_engines = {}
_lock = threading.Lock()


def extract_facts(text):
    """Conservative self-reported facts only; retain original wording as evidence."""
    if contains_secret(text):
        return []
    rules = [
        ('profile', 'name', r'(?:my name is|mero naam|mero nam|मेरो नाम)\s+(.{1,100})'),
        ('profile', 'location', r'(?:i live in|ma basne thau|मेरो ठेगाना)\s+(.{1,150})'),
        ('preference', 'likes', r'(?:i (?:like|prefer|love)|malai man parcha|मलाई मन पर्छ)\s+(.{1,300})'),
        ('preference', 'dislikes', r'(?:i (?:dislike|hate)|malai man pardaina|मलाई मन पर्दैन)\s+(.{1,300})'),
        ('date', 'birthday', r'(?:my birthday is|mero birthday|मेरो जन्मदिन)\s+(.{1,100})'),
        ('habit', 'routine', r'(?:i (?:usually|always)|ma sadhai)\s+(.{1,300})'),
        ('relationship', 'relationship', r'(?:my (?:wife|husband|partner|girlfriend|boyfriend) is)\s+(.{1,150})'),
        ('instruction', 'remember', r'(?:remember that|yaad rakha|याद राख)\s+(.{1,400})'),
    ]
    result = []
    for category, key, pattern in rules:
        for sentence in re.split(r'[\n.!?।]+', text):
            match = re.fullmatch(pattern, sentence.strip(), re.I)
            if match:
                value = safe_memory_text(match[1].strip())
                if value and not contains_secret(value):
                    result.append((category, key, value))
    return result


class MemoryManager:
    def __init__(self, database, config=None, embedder=None):
        self.path = Path(database).resolve()
        self.config = config if config is not None else {}
        self.embedder = embedder
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='saru-memory')
        self.status = 'Local semantic memory waiting'
        self.index = None
        self.ids = []
        self._scheduled = False
        self._dirty = False
        self._pending_lock = threading.Lock()
        self._retry_after = 0
        self._schema()

    def _schema(self):
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS memory_facts(category TEXT, name TEXT, value TEXT, source_id INTEGER, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(category,name,value))')
            db.execute('CREATE TABLE IF NOT EXISTS memory_vectors(id INTEGER PRIMARY KEY, digest TEXT, model TEXT, vector BLOB)')

    def _embed(self, texts):
        import numpy as np
        if self.embedder is None:
            if time.monotonic()<self._retry_after:raise RuntimeError('Local model setup required; retry is paused')
            from fastembed import TextEmbedding
            # Download explicitly during setup; normal chat never starts a model download.
            try:self.embedder = TextEmbedding(MODEL, cache_dir=str(self.path.parent/'embedding_models'), threads=2, local_files_only=True)
            except Exception:
                self._retry_after=time.monotonic()+300
                raise
        vectors = np.asarray(list(self.embedder.embed(texts)), dtype='float32')
        if vectors.ndim != 2 or not np.isfinite(vectors).all():
            raise ValueError('Invalid embedding output')
        import faiss
        faiss.normalize_L2(vectors)
        return vectors

    def schedule(self):
        if not self.config.get('remember_conversations', True):
            return
        with self._pending_lock:
            self._dirty = True
            if self._scheduled:
                return
            self._scheduled = True
        def work():
            try:
                while True:
                    with self._pending_lock:self._dirty=False
                    self._sync()
                    with self._pending_lock:
                        if not self._dirty:break
            except Exception as exc:
                self.status = 'Semantic memory unavailable ('+type(exc).__name__+'); keyword memory remains available'
            finally:
                with self._pending_lock:
                    self._scheduled = False
        self.executor.submit(work)

    def _sync(self):
        if not self.config.get('remember_conversations', True):
            return
        self.status = 'Indexing local memory'
        with closing(sqlite3.connect(self.path, timeout=10)) as db:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE name='memory_journal'").fetchone():
                return
            rows = db.execute('SELECT id,title,content,kind FROM memory_journal ORDER BY id').fetchall()
            old = {r[0]:r[1] for r in db.execute('SELECT id,digest FROM memory_vectors WHERE model=?', (MODEL,))}
            pending = []
            for number, title, content, kind in rows:
                text = safe_memory_text(title+'\n'+content)
                digest = hashlib.sha256(text.encode()).hexdigest()
                if old.get(number) == digest:
                    continue
                with db:
                    db.execute('DELETE FROM memory_facts WHERE source_id=?', (number,))
                    if kind == 'conversation' and title.casefold() in ('boss','user','owner'):
                        for category,key,value in extract_facts(content):
                            if key in ('name','location','birthday'):
                                db.execute('DELETE FROM memory_facts WHERE category=? AND name=?', (category,key))
                            db.execute('INSERT OR REPLACE INTO memory_facts(category,name,value,source_id) VALUES(?,?,?,?)', (category,key,value,number))
                pending.append((number,digest,text))
            for start in range(0,len(pending),24):
                if not self.config.get('remember_conversations',True):
                    return
                batch=pending[start:start+24]
                vectors=self._embed([r[2][:6000] for r in batch])
                with db:
                    db.executemany('INSERT OR REPLACE INTO memory_vectors VALUES(?,?,?,?)', [(row[0],row[1],MODEL,vector.tobytes()) for row,vector in zip(batch,vectors)])
            with db:
                db.execute('DELETE FROM memory_vectors WHERE id NOT IN (SELECT id FROM memory_journal)')
                db.execute('DELETE FROM memory_facts WHERE source_id NOT IN (SELECT id FROM memory_journal)')
            stored=db.execute('SELECT id,vector FROM memory_vectors WHERE model=? ORDER BY id',(MODEL,)).fetchall()
        if stored:
            import numpy as np
            import faiss
            matrix=np.stack([np.frombuffer(row[1],dtype='float32') for row in stored])
            if not np.isfinite(matrix).all():raise ValueError('Corrupt vector cache')
            index=faiss.IndexFlatIP(matrix.shape[1]);index.add(matrix)
            self.index=index;self.ids=[row[0] for row in stored]
        else:
            self.index=None;self.ids=[]
        self.status='Local semantic memory ready: '+str(len(self.ids))+' records'

    def _query(self, query, limit):
        if not self.config.get('remember_conversations',True):return []
        self._sync()
        if self.index is None:return []
        vector=self._embed([query[:1000]])
        scores,positions=self.index.search(vector,min(limit,len(self.ids)))
        with closing(sqlite3.connect(self.path,timeout=5)) as db:
            result=[]
            for score,position in zip(scores[0],positions[0]):
                if position<0 or score<.30:continue
                row=db.execute('SELECT kind,title,content FROM memory_journal WHERE id=?',(self.ids[position],)).fetchone()
                if row:result.append({'kind':row[0],'title':row[1],'content':safe_memory_text(row[2])[:1400]})
            return result

    def context(self,query,limit=6,timeout=3):
        if not self.config.get('remember_conversations',True):return ''
        future=self.executor.submit(self._query,str(query),limit)
        try:rows=future.result(timeout=timeout)
        except Exception:
            future.cancel();rows=[]
        with closing(sqlite3.connect(self.path,timeout=3)) as db:
            facts=[{'category':r[0],'name':r[1],'value':r[2]} for r in db.execute('SELECT category,name,value FROM memory_facts ORDER BY updated_at DESC LIMIT 20')]
        return json.dumps({'self_reported_facts':facts,'semantic_matches':rows},ensure_ascii=False)[:8500] if facts or rows else ''


def manager(database,config=None):
    key=str(Path(database).resolve())
    with _lock:
        if key not in _engines:_engines[key]=MemoryManager(database,config)
        elif config is not None:_engines[key].config=config
        return _engines[key]


def schedule_connection(connection,config):
    row=connection.execute('PRAGMA database_list').fetchone()
    if row and row[2] and config.get('semantic_memory',False):manager(row[2],config).schedule()
