"""Separate editable owner and application-creator profiles."""
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit
import uuid

CREATOR={'name':'Udaya Raj Khanal','email':'udayarajkhanal21@gmail.com','phone':'+9779864353535','facebook':'https://www.facebook.com/udayarajkhanal369','youtube':'https://www.youtube.com/@udayaraj3','role':'SARU AI Creator / Developer'}
FIELDS=(('name','Full name'),('email','Gmail / email'),('phone','Phone number'),('facebook','Facebook link'),('youtube','YouTube channel'),('role','Role / occupation'),('address','Address'),('country','Country'),('birthday','Birthday'),('website','Website'),('bio','About / biography'),('extra','Additional information'))


def get_profile(config,kind):
 if kind not in ('owner','creator'):raise ValueError('Unknown profile')
 if kind=='creator':
  from config_manager import developer_identity
  return {key:value for key,value in developer_identity().items() if key!='product'}
 result=dict(CREATOR) if kind=='creator' else {'name':config.get('owner_name','Boss')}
 saved=config.get(kind+'_profile',{})
 if isinstance(saved,dict):result.update(saved)
 if kind=='owner' and config.get('owner_photo') and not result.get('photo'):result['photo']=config['owner_photo']
 return result


def validate_profile(values):
 result={str(key):str(value).strip() for key,value in values.items()}
 if not result.get('name'):raise ValueError('Enter a full name.')
 if any(len(value)>4000 for value in result.values()):raise ValueError('Keep each field under 4,000 characters.')
 email=result.get('email','')
 if email and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):raise ValueError('Enter a valid email address.')
 for key in ('facebook','youtube','website'):
  value=result.get(key,'')
  if value:
   parsed=urlsplit(value)
   if parsed.scheme not in ('https','http') or not parsed.hostname or parsed.username or parsed.password:raise ValueError('Use a complete http/https link for '+key+'.')
 return result


def save_profile(config,kind,values):
 if kind not in ('owner','creator'):raise ValueError('Unknown profile')
 if kind=='creator':
  identity=get_profile(config,'creator')
  if any(str(value).strip()!=str(identity.get(key,'')) for key,value in values.items() if key!='photo') or values.get('photo'):raise ValueError('Original developer credits are signed and read-only. Edit the Owner profile for your own information.')
  return identity
 result=validate_profile(values)
 config[kind+'_profile']=result
 if kind=='owner':config['owner_name']=result['name'];config['owner_photo']=result.get('photo','')
 return result


def photo_path(profile,root,kind):
 path=Path(profile.get('photo') or '')
 if path.is_file():return path
 if kind=='creator' and (Path(root)/'creator_photo.jpg').is_file():return Path(root)/'creator_photo.jpg'
 return None


def copy_photo(source,data,kind):
 from PIL import Image
 source=Path(source)
 if source.stat().st_size>20*1024*1024:raise ValueError('Choose a photo smaller than 20 MiB.')
 with Image.open(source) as image:image.verify()
 folder=Path(data)/'profiles';folder.mkdir(parents=True,exist_ok=True)
 target=folder/(kind+'-'+uuid.uuid4().hex+source.suffix.lower())
 shutil.copy2(source,target);return str(target)
