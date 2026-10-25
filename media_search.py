"""Find public YouTube video links for the SARU embedded player; no media download."""
import json,re
from media_library import youtube_id

def find_videos(query):
 query=query.strip()
 if not query or len(query)>400:raise ValueError('Give a YouTube link or a title up to 400 characters.')
 if query.startswith(('https://','http://')):
  video=youtube_id(query);return [{'url':'https://www.youtube.com/watch?v='+video,'title':'YouTube '+video}]
 import requests
 with requests.get('https://www.youtube.com/results',params={'search_query':query},headers={'User-Agent':'Mozilla/5.0','Accept-Language':'en'},timeout=20,stream=True) as response:
  response.raise_for_status();content=b''
  for chunk in response.iter_content(65536):
   content+=chunk
   if len(content)>4000000:break
 text=content.decode('utf8','replace');match=re.search(r'(?:var\s+)?ytInitialData\s*=\s*',text)
 if not match:raise ValueError('YouTube search did not return usable results. Paste a direct video link in SARU.')
 data=json.JSONDecoder().raw_decode(text[match.end():])[0];rows=[];seen=set()
 def visit(node):
  if len(rows)>=8:return
  if isinstance(node,dict):
   video=node.get('videoRenderer')
   if isinstance(video,dict) and re.fullmatch(r'[\w-]{11}',video.get('videoId','')) and video['videoId'] not in seen:
    seen.add(video['videoId']);title=video.get('title',{});name=title.get('simpleText') or ''.join(run.get('text','') for run in title.get('runs',[]))
    rows.append({'url':'https://www.youtube.com/watch?v='+video['videoId'],'title':name or query})
   for item in node.values():visit(item)
  elif isinstance(node,list):
   for item in node:visit(item)
 visit(data)
 if not rows:raise ValueError('No playable video links found. Paste a direct YouTube link.')
 return rows
