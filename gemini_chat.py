"""Bounded text-model retirement recovery; credentials and saved choices stay local."""
import hashlib,re,time
import requests

BASE='https://generativelanguage.googleapis.com/v1beta/'
_working={}

def generate(key,model,body,http=requests):
 identity=(hashlib.sha256(key.encode()).hexdigest(),model);cached=_working.get(identity)
 used=cached[0] if cached and time.monotonic()-cached[1]<900 else model
 def post(name):
  if not re.fullmatch(r'[A-Za-z0-9_.-]{1,120}',name):raise ValueError('Use a Gemini model ID, without a URL or path.')
  return http.post(BASE+'models/'+name+':generateContent',headers={'x-goog-api-key':key},json=body,timeout=65)
 response=post(used)
 if response.status_code==404:
  _working.pop(identity,None)
  available=http.get(BASE+'models',headers={'x-goog-api-key':key},params={'pageSize':100},timeout=20);available.raise_for_status()
  choices=[]
  for item in available.json().get('models',[]):
   name=item.get('name','').removeprefix('models/');match=re.fullmatch(r'gemini-(\d+)\.(\d+)-flash',name)
   if match and name!=used and 'generateContent' in item.get('supportedGenerationMethods',[]):choices.append(((int(match[1]),int(match[2])),name))
  if not choices:raise ValueError('The saved Gemini text model is unavailable and no stable Flash replacement was returned. Choose an available model in Settings.')
  used=max(choices)[1];response=post(used)
 if response.status_code in (401,403):raise ValueError('Gemini authentication/permission error. Check the saved key.')
 if response.status_code==429:raise ValueError('Gemini quota or rate limit reached. Try later or change the model/plan.')
 response.raise_for_status();payload=response.json()
 if not payload.get('candidates'):raise ValueError('Gemini returned no text candidate. No answer was invented.')
 parts=payload['candidates'][0].get('content',{}).get('parts',[]);answer=''.join(str(part['text']) for part in parts if 'text' in part and not part.get('thought'))
 if not answer.strip():raise ValueError('Gemini returned no visible text. Check the response safety/model settings.')
 _working[identity]=(used,time.monotonic());return answer,used
