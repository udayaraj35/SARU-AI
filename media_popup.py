"""Loopback-only media app served to an Edge/Chrome popup, independent of Tk."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import subprocess
import threading
from queue import Queue
import webbrowser
from urllib.parse import urlsplit
from media_library import MediaLibrary

PAGE=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="referrer" content="strict-origin-when-cross-origin"><title>SARU Media Player</title>
<style>body{background:__BG__;color:__TEXT__;font:16px 'Segoe UI',sans-serif;margin:20px}h1{color:__ACCENT__;font-size:25px}button,input{font:inherit;color:inherit;background:__PANEL__;border:1px solid __ACCENT__;border-radius:12px;padding:10px;margin:4px}button{cursor:pointer}button:hover{filter:brightness(1.35)}input[type=range]{padding:0}#stage{background:#000;border-radius:14px;overflow:hidden;aspect-ratio:16/9;max-height:65vh}#youtube,#local{width:100%;height:100%;object-fit:contain}#library{display:flex;flex-wrap:wrap;gap:6px}#message{min-height:25px;color:__ACCENT__}label{display:inline-block}#url{width:min(440px,80vw)}:focus-visible{outline:3px solid __ACCENT__}</style></head><body>
<h1>SARU · YouTube & Local Media</h1><p>Save favourite YouTube links, or import your own video/audio from SARU. Use the window buttons to minimize or maximize.</p>
<div><input id="url" placeholder="YouTube video URL"><input id="title" placeholder="Favourite name"><button onclick="saveLink()">Save YouTube link</button><button onclick="importFile()">Import local file</button><button onclick="refresh()">Refresh library</button></div>
<div id="message" role="status"></div><div id="stage"><div id="youtube"></div><video id="local" controls hidden></video></div>
<div><button onclick="back()">← Library</button><button onclick="previous()">Previous</button><button onclick="seek(-10)">−10 sec</button><button onclick="play()">Play</button><button onclick="pause()">Pause</button><button onclick="seek(10)">+10 sec</button><button onclick="next()">Next</button><button onclick="full()">Fullscreen</button><label>Volume <input aria-label="Volume" id="volume" type="range" min="0" max="100" value="70" oninput="volume(this.value)"></label></div>
<div><label>Local MP3 clip: start <input id="start" type="number" min="0" value="0" style="width:80px"></label><label>end seconds <input id="end" type="number" min="1" value="30" style="width:80px"></label><button id="clip" onclick="clip()">Save MP3 clip</button></div>
<p>YouTube favourites save links, not offline copies. MP3 clips use imported local files.</p><div id="library"></div>
<script>
const base=location.pathname.replace(/\/$/,'');let items=[],current=null,yt=null,ready=false,sequence=0;
const local=document.getElementById('local'),msg=document.getElementById('message');
async function api(path,body){let response=await fetch(base+path,body?{method:'POST',headers:{'Content-Type':'application/json','X-SARU-Token':base.slice(1)},body:JSON.stringify(body)}:{});let result=await response.json();if(!response.ok)throw Error(result.error||'Request failed');return result}
function error(e){msg.textContent=e.message||String(e)}
async function refresh(){try{items=await api('/library');let box=document.getElementById('library');box.replaceChildren();for(let item of items){let button=document.createElement('button');button.textContent=(item.kind==='youtube'?'▶ YouTube: ':'♫ Local: ')+item.title;button.onclick=()=>select(item.id);box.append(button)}}catch(e){error(e)}}
async function saveLink(){try{let item=await api('/save',{url:document.getElementById('url').value,title:document.getElementById('title').value});await refresh();select(item.id)}catch(e){error(e)}}
async function importFile(){try{await api('/import',{});msg.textContent='Choose your media file in the SARU file dialog, then refresh the library.'}catch(e){error(e)}}
function onYouTubeIframeAPIReady(){yt=new YT.Player('youtube',{width:'100%',height:'100%',playerVars:{origin:location.origin,playsinline:1},events:{onReady:()=>{ready=true;if(current?.kind==='youtube')loadYT()},onError:event=>{msg.textContent='YouTube playback error '+event.data+'. This video may restrict embedded playback.'},onStateChange:event=>{if(event.data===0)next()}}})}
function loadYT(){if(ready&&current?.kind==='youtube'){yt.loadVideoById(current.video);yt.setVolume(+document.getElementById('volume').value)}}
function select(id){let item=items.find(row=>row.id===id);if(!item)return;pause();current=item;msg.textContent=item.title;let youtube=document.getElementById('youtube');youtube.hidden=item.kind!=='youtube';local.hidden=item.kind==='youtube';document.getElementById('clip').disabled=item.kind!=='local';if(item.kind==='youtube')loadYT();else{local.src=base+'/file/'+item.id;local.volume=+document.getElementById('volume').value/100;local.play().catch(error)}}
function play(){if(!current){if(items.length)select(items[0].id);return}if(current.kind==='youtube'){if(ready)yt.playVideo()}else local.play().catch(error)}
function pause(){local.pause();if(ready)yt.pauseVideo()}
function seek(delta){if(current?.kind==='youtube'){if(ready)yt.seekTo(Math.max(0,yt.getCurrentTime()+delta),true)}else if(current)local.currentTime=Math.max(0,local.currentTime+delta)}
function volume(value){local.volume=value/100;if(ready)yt.setVolume(+value)}
function previous(){if(items.length)select(items[(Math.max(0,items.findIndex(i=>i.id===current?.id))-1+items.length)%items.length].id)}
function next(){if(items.length)select(items[(items.findIndex(i=>i.id===current?.id)+1)%items.length].id)}
function back(){pause();document.getElementById('library').scrollIntoView({behavior:'smooth'})}
function full(){document.getElementById('stage').requestFullscreen().catch(error)}
async function clip(){if(current?.kind!=='local'){msg.textContent='Choose an imported local file first.';return}let button=document.getElementById('clip');button.disabled=true;msg.textContent='Creating local MP3 clip…';try{let item=await api('/clip',{id:current.id,start:document.getElementById('start').value,end:document.getElementById('end').value});await refresh();msg.textContent='Saved: '+item.title}catch(e){error(e)}finally{button.disabled=current?.kind!=='local'}}
local.addEventListener('ended',next);
async function poll(){try{let result=await api('/command');if(result.sequence>sequence){sequence=result.sequence;await refresh();if(result.action==='select')select(result.value);else if(result.action==='play')play();else if(result.action==='pause')pause();else if(result.action==='next')next();else if(result.action==='previous')previous();else if(result.action==='seek')seek(result.value);else if(result.action==='volume'){document.getElementById('volume').value=result.value;volume(result.value)}}}catch(e){}setTimeout(poll,700)}
refresh();poll();let tag=document.createElement('script');tag.src='https://www.youtube.com/iframe_api';document.head.append(tag);
</script></body></html>'''


class MediaPopup:
 def __init__(self,data,theme='Neon Rose'):
  from theme_manager import palette
  self.library=MediaLibrary(data);self.token=secrets.token_urlsafe(32);self.command={'sequence':0};self.command_lock=threading.Lock();self.requests=Queue(maxsize=8)
  self.page=PAGE
  for key,value in palette(theme).items():self.page=self.page.replace('__'+key.upper()+'__',value)
  owner=self
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def authorized(self):
    expected='127.0.0.1:'+str(self.server.server_port)
    return self.headers.get('Host')==expected and urlsplit(self.path).path.startswith('/'+owner.token+'/')
   def reply(self,status,payload,kind='application/json'):
    data=json.dumps(payload).encode() if kind=='application/json' else payload
    self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','strict-origin-when-cross-origin');self.end_headers();self.wfile.write(data)
   def do_GET(self):
    if not self.authorized():self.reply(403,{'error':'Invalid player session'});return
    route=urlsplit(self.path).path[len(owner.token)+1:]
    try:
     if route=='/':self.reply(200,owner.page.encode(),'text/html; charset=utf-8')
     elif route=='/library':self.reply(200,owner.library.list())
     elif route=='/command':
      with owner.command_lock:self.reply(200,dict(owner.command))
     elif route.startswith('/file/'):self.media_file(owner.library.local_path(owner.library.get(route[6:])))
     else:self.reply(404,{'error':'Not found'})
    except (BrokenPipeError,ConnectionResetError):pass
    except Exception as exc:self.reply(400,{'error':str(exc)[:300]})
   def do_POST(self):
    if not self.authorized() or self.headers.get('X-SARU-Token')!=owner.token:self.reply(403,{'error':'Invalid player session'});return
    try:
     size=int(self.headers.get('Content-Length','0'))
     if size<=0 or size>8192:raise ValueError('Invalid request size')
     body=json.loads(self.rfile.read(size));route=urlsplit(self.path).path[len(owner.token)+1:]
     if route=='/save':result=owner.library.add_youtube(body['url'],body.get('title',''))
     elif route=='/clip':
      if owner.requests.full():raise ValueError('Finish the pending SARU file dialog before creating another clip.')
      result=owner.library.trim_mp3(body['id'],body['start'],body['end'])
      owner.requests.put_nowait({'export':result['id']})
     elif route=='/import':
      if owner.requests.empty():owner.requests.put_nowait('import')
      result={'queued':True}
     else:self.reply(404,{'error':'Not found'});return
     self.reply(200,result)
    except Exception as exc:self.reply(400,{'error':str(exc)[:300]})
   def media_file(self,path):
    size=path.stat().st_size;start=0;end=size-1;status=200
    request=self.headers.get('Range')
    if request:
     match=re.fullmatch(r'bytes=(\d+)-(\d*)',request)
     if not match or int(match[1])>=size:self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return
     start=int(match[1]);end=min(int(match[2]) if match[2] else end,end);status=206
     if end<start:self.reply(416,{'error':'Invalid range'});return
    length=end-start+1;self.send_response(status);self.send_header('Content-Type',mimetypes.guess_type(path.name)[0] or 'application/octet-stream');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(length))
    if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
    self.end_headers()
    with path.open('rb') as source:
     source.seek(start)
     while length:
      chunk=source.read(min(65536,length))
      if not chunk:break
      self.wfile.write(chunk);length-=len(chunk)
  self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.daemon_threads=True
  self.url=f'http://127.0.0.1:{self.server.server_port}/{self.token}/'
  threading.Thread(target=self.server.serve_forever,daemon=True).start()
 def send(self,action,value=None):
  if action not in ('select','play','pause','next','previous','seek','volume'):raise ValueError('Unknown playback action')
  with self.command_lock:self.command={'sequence':self.command['sequence']+1,'action':action,'value':value}
 def open(self):
  for base in (os.environ.get('ProgramFiles(x86)',''),os.environ.get('ProgramFiles',''),os.environ.get('LOCALAPPDATA','')):
   for relative in ('Microsoft/Edge/Application/msedge.exe','Google/Chrome/Application/chrome.exe'):
    executable=Path(base)/relative
    if executable.is_file():
     subprocess.Popen([str(executable),'--app='+self.url,'--window-size=1100,850'],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));return
  webbrowser.open(self.url)
 def close(self):self.server.shutdown();self.server.server_close()
