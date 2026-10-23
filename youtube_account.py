"""YouTube desktop OAuth with PKCE; credentials belong in the DPAPI keys store."""
import base64,hashlib,json,secrets,time,webbrowser
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import parse_qs,urlparse,urlencode
import requests

SCOPES='https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly'

def connect_youtube(client_file,cancel=None):
 data=json.loads(open(client_file,encoding='utf-8-sig').read()).get('installed',{})
 if not data.get('client_id'):raise ValueError('Choose a Google OAuth Desktop app client JSON file.')
 state=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(48);result={}
 class Callback(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_GET(self):
   query=parse_qs(urlparse(self.path).query)
   if not secrets.compare_digest(query.get('state',[''])[0],state):
    self.send_response(400);self.end_headers();return
   result.update(code=query.get('code',[''])[0],error=query.get('error',[''])[0])
   self.send_response(200);self.end_headers();self.wfile.write(b'Authorization received. Return to SARU. You can close this tab.')
 with HTTPServer(('127.0.0.1',0),Callback) as server:
  server.timeout=1;redirect='http://127.0.0.1:'+str(server.server_port)+'/'
  challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
  webbrowser.open('https://accounts.google.com/o/oauth2/v2/auth?'+urlencode({'client_id':data['client_id'],'redirect_uri':redirect,'response_type':'code','scope':SCOPES,'access_type':'offline','prompt':'consent','state':state,'code_challenge':challenge,'code_challenge_method':'S256'}))
  deadline=time.monotonic()+180
  while not result and time.monotonic()<deadline and not (cancel and cancel.is_set()):server.handle_request()
 if not result.get('code'):raise ValueError('Google connection cancelled or timed out.')
 response=requests.post('https://oauth2.googleapis.com/token',data={'client_id':data['client_id'],'client_secret':data.get('client_secret',''),'code':result['code'],'code_verifier':verifier,'redirect_uri':redirect,'grant_type':'authorization_code'},timeout=30)
 if response.status_code!=200:raise ValueError('Google token exchange failed. Check your Desktop OAuth app and test users.')
 tokens=response.json()
 if not tokens.get('access_token'):raise ValueError('Google did not return an access token.')
 tokens.update(client_id=data['client_id'],client_secret=data.get('client_secret',''))
 return json.dumps(tokens)

def youtube_token(config,session=requests):
 try:credentials=json.loads(config.get('keys',{}).get('YouTube OAuth','{}'))
 except ValueError:raise ValueError('Reconnect YouTube in Content Studio.') from None
 if credentials.get('refresh_token'):
  r=session.post('https://oauth2.googleapis.com/token',data={'client_id':credentials['client_id'],'client_secret':credentials.get('client_secret',''),'refresh_token':credentials['refresh_token'],'grant_type':'refresh_token'},timeout=30)
  if r.status_code!=200:raise ValueError('YouTube authorization expired/revoked. Reconnect your channel.')
  token=r.json().get('access_token')
 else:token=credentials.get('access_token')
 if not token:raise ValueError('Connect your YouTube channel in Content Studio first.')
 return token
