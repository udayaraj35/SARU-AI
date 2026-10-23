"""Bundled brand silhouettes from Simple Icons 16.0.0; no runtime downloads."""
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageTk
import re

NAMES={'Facebook':'facebook','Instagram':'instagram','TikTok':'tiktok','YouTube':'youtube','WhatsApp':'whatsapp','WhatsApp Web':'whatsapp','Gmail':'gmail','Telegram':'telegram','Twitter':'x','X Twitter':'x','X (Twitter)':'x','GitHub':'github','Google':'google'}

@lru_cache(maxsize=80)
def pil_icon(name,size=24):
 slug=NAMES.get(name)
 if not slug:
  clean=re.sub(r'^[^\w]+','',name).strip()
  for title,value in NAMES.items():
   if clean==title or clean.startswith(title+' '):slug=value;break
 if not slug:return None
 path=Path(__file__).with_name('brand-'+slug+'.png')
 if not path.is_file():return None
 with Image.open(path) as source:return source.convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)

def tk_icon(name,size=24):
 image=pil_icon(name,size)
 return ImageTk.PhotoImage(image) if image else None
