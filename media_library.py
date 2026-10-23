"""Persistent YouTube bookmarks and owner-selected local media; no stream ripping."""
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
from urllib.parse import urlparse,parse_qs
import uuid


def youtube_id(url):
 parsed=urlparse(url.strip())
 host=(parsed.hostname or '').lower()
 if parsed.params or parsed.username or parsed.password:raise ValueError('Use a direct YouTube video link.')
 if parsed.scheme not in ('http','https'):raise ValueError('Paste a YouTube https URL.')
 if host=='youtu.be':value=parsed.path.strip('/')
 elif host in ('youtube.com','www.youtube.com','m.youtube.com'):
  value=parse_qs(parsed.query).get('v',[''])[0]
  if parsed.path.startswith(('/shorts/','/embed/','/live/')):value=parsed.path.split('/')[2]
 else:raise ValueError('Use a youtube.com or youtu.be link.')
 if not re.fullmatch(r'[A-Za-z0-9_-]{11}',value):raise ValueError('The link must identify one YouTube video.')
 return value


class MediaLibrary:
 def __init__(self,data):
  self.root=Path(data)/'media';self.root.mkdir(parents=True,exist_ok=True)
  self.file=self.root/'library.json';self.lock=threading.RLock()
 def list(self):
  with self.lock:
   if not self.file.exists():return []
   rows=json.loads(self.file.read_text(encoding='utf8'))
   if not isinstance(rows,list):raise ValueError('Media library is invalid; keep its file for recovery.')
   return rows
 def write(self,rows):
  temp=self.file.with_suffix('.tmp');temp.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,self.file)
 def add_youtube(self,url,title=''):
  video=youtube_id(url)
  with self.lock:
   rows=self.list()
   for row in rows:
    if row.get('video')==video:return row
   row={'id':uuid.uuid4().hex,'kind':'youtube','video':video,'title':title.strip()[:180] or 'YouTube '+video}
   rows.append(row);self.write(rows);return row
 def import_file(self,path):
  source=Path(path)
  if source.suffix.lower() not in ('.mp4','.webm','.mp3','.wav','.ogg','.m4a','.mov'):raise ValueError('Choose MP4, WebM, MP3, WAV, OGG, M4A or MOV.')
  if source.stat().st_size>1024**3:raise ValueError('Choose a file smaller than 1 GiB.')
  identifier=uuid.uuid4().hex;filename=identifier+source.suffix.lower();target=self.root/filename
  shutil.copy2(source,target)
  row={'id':identifier,'kind':'local','file':filename,'title':source.name}
  try:
   with self.lock:rows=self.list();rows.append(row);self.write(rows)
  except Exception:target.unlink(missing_ok=True);raise
  return row
 def get(self,identifier):
  return next((row for row in self.list() if row['id']==identifier),None)
 def local_path(self,row):
  if not row or row.get('kind')!='local':raise ValueError('Select a local media file.')
  target=(self.root/row['file']).resolve()
  if target.parent!=self.root.resolve() or not target.is_file():raise ValueError('Saved media file is missing.')
  return target
 def trim_mp3(self,identifier,start,end):
  start=float(start);end=float(end)
  if not all(math.isfinite(v) for v in (start,end)) or start<0 or end<=start or end-start>7200:raise ValueError('Choose a start/end range of up to two hours.')
  source=self.local_path(self.get(identifier))
  from imageio_ffmpeg import get_ffmpeg_exe
  new_id=uuid.uuid4().hex;output=self.root/(new_id+'.mp3')
  try:
   subprocess.run([get_ffmpeg_exe(),'-nostdin','-v','error','-ss',str(start),'-i',str(source),'-t',str(end-start),'-vn','-codec:a','libmp3lame',str(output)],check=True,timeout=180,capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   if not output.exists() or output.stat().st_size<100:raise ValueError('No audio found in the selected range.')
   row={'id':new_id,'kind':'local','file':output.name,'title':source.stem+' clip.mp3'}
   with self.lock:rows=self.list();rows.append(row);self.write(rows)
   return row
  except Exception:output.unlink(missing_ok=True);raise
