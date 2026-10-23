"""Official video endpoints. Functions are called only for explicitly approved drafts."""
from pathlib import Path
from urllib.parse import urlparse
import re
import requests
from youtube_account import youtube_token

MAX_VIDEO_BYTES=64*1024*1024

def checked_json(response):
 if not 200<=response.status_code<300:raise RuntimeError('Platform request failed (HTTP '+str(response.status_code)+'). Check account permissions/quota; inspect the account before retrying.')
 try:body=response.json()
 except ValueError:raise RuntimeError('Platform returned an invalid response. Check the account before retrying.') from None
 if body.get('error') and (not isinstance(body['error'],dict) or body['error'].get('code') not in (None,'ok')):raise RuntimeError('Platform rejected the request. Check account authorization and publishing eligibility.')
 return body

def video_file(path):
 path=Path(path)
 if not path.is_file() or path.suffix.lower()!='.mp4':raise ValueError('Choose a local MP4 video.')
 if not 0<path.stat().st_size<=MAX_VIDEO_BYTES:raise ValueError('This release supports MP4 videos up to 64 MiB.')
 return path

def meta_base(config):
 version=config.get('meta_graph_version','');identifier=config.get('facebook_page_id','');token=config.get('keys',{}).get('Facebook Page','')
 if not re.fullmatch(r'v\d+\.\d+',version) or not re.fullmatch(r'[0-9]+',identifier) or not token:raise ValueError('Connect your Facebook Page ID, Page token and Graph version in Social accounts.')
 return 'https://graph.facebook.com/'+version+'/'+identifier,token

def account_info(platform,config,session=requests):
 if platform=='YouTube':
  token=youtube_token(config,session)
  data=checked_json(session.get('https://www.googleapis.com/youtube/v3/channels',params={'part':'snippet','mine':'true'},headers={'Authorization':'Bearer '+token},timeout=30))
  if not data.get('items'):raise ValueError('No YouTube channel found for the connected account.')
  item=data['items'][0];return {'id':item['id'],'name':item['snippet']['title'],'privacy':['private','unlisted','public']}
 if platform=='Facebook':
  base,token=meta_base(config)
  data=checked_json(session.get(base,params={'fields':'id,name'},headers={'Authorization':'Bearer '+token},timeout=30))
  return {'id':data['id'],'name':data['name'],'privacy':['Page public']}
 if platform=='TikTok':
  token=config.get('keys',{}).get('TikTok','')
  if not token:raise ValueError('Add your TikTok video.publish access token in Content Studio accounts.')
  data=checked_json(session.post('https://open.tiktokapis.com/v2/post/publish/creator_info/query/',headers={'Authorization':'Bearer '+token},json={},timeout=30))['data']
  return {'id':data.get('creator_username',data.get('creator_nickname','')),'name':data['creator_nickname'],'privacy':data['privacy_level_options'],'details':data}
 raise ValueError('Unsupported platform')

def trusted_upload(url,platform):
 host=urlparse(url).hostname or ''
 allowed=(host=='www.googleapis.com') if platform=='YouTube' else (host=='tiktokapis.com' or host.endswith('.tiktokapis.com'))
 if urlparse(url).scheme!='https' or urlparse(url).username or urlparse(url).port not in (None,443) or not allowed:raise ValueError('Untrusted upload destination rejected.')
 return url

def upload_video(post,config,session=requests):
 path=video_file(post['path']);platform=post['platform']
 # Confirm the connected account has not changed since the exact draft was reviewed.
 account=account_info(platform,config,session)
 if account['id']!=post['destination_id']:raise ValueError('Connected account changed. Prepare and review a new draft.')
 if post['privacy'] not in account['privacy']:raise ValueError('Visibility is no longer available. Prepare a new review.')
 if platform=='YouTube':
  token=youtube_token(config,session);auth={'Authorization':'Bearer '+token}
  metadata={'snippet':{'title':post['title'],'description':post['description'],'categoryId':'22'},'status':{'privacyStatus':post['privacy'],'selfDeclaredMadeForKids':post['kids']}}
  start=session.post('https://www.googleapis.com/upload/youtube/v3/videos',params={'uploadType':'resumable','part':'snippet,status'},headers={**auth,'X-Upload-Content-Length':str(path.stat().st_size),'X-Upload-Content-Type':'video/mp4'},json=metadata,timeout=30,allow_redirects=False)
  if start.status_code not in (200,201):checked_json(start)
  url=trusted_upload(start.headers.get('Location',''),'YouTube')
  with path.open('rb') as source:result=checked_json(session.put(url,headers={**auth,'Content-Type':'video/mp4','Content-Length':str(path.stat().st_size)},data=source,timeout=180,allow_redirects=False))
  if not result.get('id'):raise RuntimeError('No YouTube video ID returned. Check your channel before retrying.')
  return {'id':result['id'],'state':'accepted','detail':'Uploaded; YouTube processing/visibility: '+result.get('status',{}).get('privacyStatus',post['privacy'])}
 if platform=='Facebook':
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  base,token=meta_base(config)
  with path.open('rb') as source:
   body=MultipartEncoder(fields={'title':post['title'],'description':post['description'],'published':'true','source':(path.name,source,'video/mp4')})
   data=checked_json(session.post(base+'/videos',headers={'Authorization':'Bearer '+token,'Content-Type':body.content_type},data=body,timeout=180,allow_redirects=False))
  if not data.get('id'):raise RuntimeError('No Facebook video ID returned. Check your Page before retrying.')
  return {'id':data['id'],'state':'accepted','detail':'Video accepted by Facebook; processing/publication still needs confirmation.'}
 if platform=='TikTok':
  from video_creator import video_duration
  duration=video_duration(path)
  if duration>account['details'].get('max_video_post_duration_sec',0):raise ValueError('Video exceeds this TikTok creator duration limit.')
  token=config['keys']['TikTok'];size=path.stat().st_size
  fields={'title':post['title']+'\n'+post['description'],'privacy_level':post['privacy'],'disable_comment':post['flags']['disable_comment'],'disable_duet':post['flags']['disable_duet'],'disable_stitch':post['flags']['disable_stitch'],'brand_content_toggle':post['flags']['brand_content'],'brand_organic_toggle':post['flags']['brand_organic'],'is_aigc':post['flags']['is_aigc']}
  details=account['details']
  for key in ('comment','duet','stitch'):
   if details.get(key+'_disabled'):fields['disable_'+key]=True
  if fields['brand_content_toggle'] and post['privacy']=='SELF_ONLY':raise ValueError('Paid partnership content cannot use private visibility.')
  if len(fields['title'].encode('utf-16-le'))//2>2200:raise ValueError('TikTok title/caption exceeds 2200 UTF-16 characters.')
  data=checked_json(session.post('https://open.tiktokapis.com/v2/post/publish/video/init/',headers={'Authorization':'Bearer '+token},json={'post_info':fields,'source_info':{'source':'FILE_UPLOAD','video_size':size,'chunk_size':size,'total_chunk_count':1}},timeout=30))['data']
  url=trusted_upload(data['upload_url'],'TikTok')
  with path.open('rb') as source:
   result=session.put(url,headers={'Content-Type':'video/mp4','Content-Length':str(size),'Content-Range':f'bytes 0-{size-1}/{size}'},data=source,timeout=180,allow_redirects=False)
   if not 200<=result.status_code<300:raise RuntimeError('TikTok upload incomplete; check post status before retrying.')
  return {'id':data['publish_id'],'state':'accepted','detail':'Uploaded to TikTok; processing/publication still needs confirmation.'}
 raise ValueError('Unsupported platform')

def post_status(platform,identifier,config,session=requests):
 if platform=='TikTok':return checked_json(session.post('https://open.tiktokapis.com/v2/post/publish/status/fetch/',headers={'Authorization':'Bearer '+config['keys']['TikTok']},json={'publish_id':identifier},timeout=30)).get('data',{})
 if platform=='YouTube':return checked_json(session.get('https://www.googleapis.com/youtube/v3/videos',headers={'Authorization':'Bearer '+youtube_token(config,session)},params={'part':'status,processingDetails','id':identifier},timeout=30)).get('items',[])
 base,token=meta_base(config);url=base.rsplit('/',1)[0]+'/'+identifier
 return checked_json(session.get(url,headers={'Authorization':'Bearer '+token},params={'fields':'status'},timeout=30))
