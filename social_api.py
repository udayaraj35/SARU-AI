"""Official Meta text publishing; credentials stay in the encrypted keys store."""
import re
import requests

class SocialError(RuntimeError):
    pass

def publish(platform, config, target, message, session=requests):
    version=config.get('meta_graph_version','').strip()
    if not re.fullmatch(r'v\d+\.\d+',version):
        raise SocialError('Set the supported Graph API version from your Meta app dashboard (for example v25.0).')
    if not message.strip():raise SocialError('Message is empty.')
    if platform=='WhatsApp':
        identifier=config.get('whatsapp_phone_id','').strip()
        token=config.get('keys',{}).get('WhatsApp Business','').strip()
        if not re.fullmatch(r'\+?[1-9]\d{6,14}',target):raise SocialError('Use an international recipient number, including country code.')
        if len(message)>4096:raise SocialError('WhatsApp text must be at most 4096 characters.')
        endpoint='messages'
        payload={'messaging_product':'whatsapp','to':target.lstrip('+'),'type':'text','text':{'body':message}}
    elif platform=='Facebook':
        identifier=config.get('facebook_page_id','').strip()
        token=config.get('keys',{}).get('Facebook Page','').strip()
        endpoint='feed';payload={'message':message}
    else:raise SocialError('This platform does not have a publishing integration.')
    if not identifier.isascii() or not identifier.isdigit() or not token:
        raise SocialError('Save the account ID and access token first.')
    try:
        response=session.post(f'https://graph.facebook.com/{version}/{identifier}/{endpoint}',headers={'Authorization':'Bearer '+token},json=payload,timeout=30,allow_redirects=False)
    except requests.RequestException:
        raise SocialError('Network result unknown. Check the account before retrying; SARU will not retry automatically.') from None
    try:body=response.json()
    except ValueError:raise SocialError('Unexpected server response. Check the account before retrying.') from None
    if not 200<=response.status_code<300 or 'error' in body:
        code=body.get('error',{}).get('code','unknown')
        raise SocialError(f'Meta rejected the request (HTTP {response.status_code}, code {code}). Check token, permissions, recipient eligibility and account configuration.')
    identifier=body.get('id') if platform=='Facebook' else next((m.get('id') for m in body.get('messages',[]) if m.get('id')),None)
    if not identifier:raise SocialError('No operation ID returned. Check the account before retrying.')
    return str(identifier)
