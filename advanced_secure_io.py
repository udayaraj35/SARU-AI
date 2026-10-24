"""Windows-user-bound encrypted JSON I/O for the isolated Advanced workspace."""
import builtins,io,json,os,threading
from pathlib import Path

class EncryptedFiles:
 def __init__(self,paths,protector):
  self.paths={os.path.normcase(os.path.abspath(p)) for p in paths};self.protector=protector;self.lock=threading.RLock();self.original_open=builtins.open;self.original_io_open=io.open
 def handles(self,path):
  if isinstance(path,int):return False
  try:return os.path.normcase(os.path.abspath(os.fspath(path))) in self.paths
  except TypeError:return False
 def read(self,path):
  with self.lock,self.original_open(path,'rb') as source:envelope=json.loads(source.read())
  if envelope.get('format')!='SARU-DPAPI-1':raise ValueError('Unrecognized protected workspace file; original retained.')
  return self.protector.unprotect(envelope['protected']).decode('utf8')
 def write(self,path,text):
  json.loads(text)  # partial/invalid writes never replace a valid protected file
  with self.lock:
   if Path(path).exists():self.read(path)  # preserve a file owned by another account
   envelope={'format':'SARU-DPAPI-1','protected':self.protector.protect(text.encode('utf8'))}
   temporary=str(path)+'.protected.tmp';Path(path).parent.mkdir(parents=True,exist_ok=True)
   with self.original_open(temporary,'w',encoding='utf8') as dest:json.dump(envelope,dest);dest.flush();os.fsync(dest.fileno())
   os.replace(temporary,path)
 def open(self,file,mode='r',buffering=-1,encoding=None,errors=None,newline=None,closefd=True,opener=None):
  if not self.handles(file):return self.original_io_open(file,mode,buffering,encoding,errors,newline,closefd,opener)
  if mode not in ('r','rt','rb','w','wt','wb','x','xt','xb'):raise ValueError('Protected JSON supports complete read/write only.')
  binary='b' in mode;writing=mode[0] in 'wx'
  if mode[0]=='x' and Path(file).exists():raise FileExistsError(file)
  owner=self
  if writing:
   base=io.BytesIO if binary else io.StringIO
   class Writer(base):
    def close(self):
     if not self.closed:
      value=self.getvalue();owner.write(file,value.decode(encoding or 'utf8') if binary else value)
     super().close()
    def __exit__(self,kind,value,tb):
     if kind is not None:super().close()
     else:self.close()
   return Writer()
  text=self.read(file);return io.BytesIO(text.encode(encoding or 'utf8')) if binary else io.StringIO(text)
 def install(self):builtins.open=self.open;io.open=self.open
 def restore(self):builtins.open=self.original_open;io.open=self.original_io_open
