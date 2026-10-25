"""Per-Windows-user encrypted provider keys and signed developer identity."""
import base64
import getpass
import json
from pathlib import Path
from urllib.parse import urlsplit
import requests
from settings_store import SettingsStore

ROOT=Path(__file__).resolve().parent
PINNED_PUBLIC_KEY='EKLSDFCHbUInxMQspFfEROBPlHQAOrGlPUoGPa+U9ks='
PROVIDERS={
    'OpenAI':('https://api.openai.com/v1','gpt-4o-mini'),
    'Anthropic':('https://api.anthropic.com/v1',''),
    'DeepSeek':('https://api.deepseek.com','deepseek-chat'),
    'Groq':('https://api.groq.com/openai/v1',''),
    'OpenRouter':('https://openrouter.ai/api/v1','openai/gpt-4o-mini'),
    'Gemini':('https://generativelanguage.googleapis.com',''),
    'Custom':('https://api.openai.com/v1',''),
}


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()


def verify_signed(document,root=ROOT):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    key=json.loads((Path(root)/'developer_public_key.json').read_text(encoding='utf8'))['ed25519']
    if key!=PINNED_PUBLIC_KEY:raise ValueError('Developer signing key was changed')
    public=Ed25519PublicKey.from_public_bytes(base64.b64decode(key,validate=True))
    public.verify(base64.b64decode(document['signature'],validate=True),canonical(document['payload']))
    return document['payload']


def developer_identity(root=ROOT):
    identity=verify_signed(json.loads((Path(root)/'developer_identity.json').read_text(encoding='utf8')),root)
    if identity.get('name')!='Udaya Raj Khanal' or identity.get('product')!='SARU AI':
        raise ValueError('Developer identity does not match SARU')
    return identity


class ConfigManager:
    def __init__(self,path,defaults=None,protector=None):
        self.store=SettingsStore(path,defaults or {'keys':{}},protector)

    def load(self):return self.store.load()

    def set_provider(self,provider,key,model):
        if provider not in PROVIDERS:raise ValueError('Unknown provider')
        if not key.strip() or not model.strip():raise ValueError('Enter both an API key and model ID')
        cfg=self.load();cfg.setdefault('keys',{})[provider]=key.strip()
        cfg.setdefault('provider_models',{})[provider]=model.strip()
        cfg.update(provider=provider,model=model.strip());self.store.save(cfg)
        return provider+' saved encrypted for this Windows account'

    def console_setup(self,provider):
        # No key is echoed or passed on the command line.
        model=input('Model ID: ').strip() or PROVIDERS[provider][1]
        return self.set_provider(provider,getpass.getpass(provider+' API key (hidden): '),model)


def generate(config,messages,session=requests):
    provider=config['provider'];key=config.get('keys',{}).get(provider,'')
    if not key:raise ValueError('Save your '+provider+' API key in Settings or run config_manager.py')
    model=config.get('model','')
    if not model:raise ValueError('Choose a model ID for '+provider)
    base=PROVIDERS[provider][0]
    if provider=='Custom':base=config.get('custom_url',base).rstrip('/')
    parsed=urlsplit(base)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password:raise ValueError('Provider endpoint must use HTTPS')
    if provider=='Anthropic':
        system='\n'.join(m['content'] for m in messages if m['role']=='system')
        payload={'model':model,'max_tokens':4096,'system':system,'messages':[m for m in messages if m['role']!='system']}
        response=session.post(base+'/messages',headers={'x-api-key':key,'anthropic-version':'2023-06-01'},json=payload,timeout=65,allow_redirects=False)
        response.raise_for_status()
        return '\n'.join(c['text'] for c in response.json()['content'] if c.get('type')=='text')
    if provider=='Gemini':raise ValueError('Use the existing Gemini adapter')
    response=session.post(base+'/chat/completions',headers={'Authorization':'Bearer '+key},json={'model':model,'messages':messages},timeout=65,allow_redirects=False)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


if __name__=='__main__':
    import argparse,os
    parser=argparse.ArgumentParser();parser.add_argument('provider',choices=PROVIDERS)
    args=parser.parse_args()
    data=Path(os.getenv('SARU_DATA_DIR') or str(Path(os.getenv('APPDATA',str(Path.home())))/'SARU_AI'))
    print(ConfigManager(data/'settings.json').console_setup(args.provider))
