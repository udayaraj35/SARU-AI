"""Recover portraits when saved paths refer to an older install location."""
from pathlib import Path
from PIL import Image

def load_portrait(selected,design='auto'):
 fallback=Path(__file__).resolve().parent/'saru_photo.jpg'
 new=Path(__file__).resolve().parent/'saru_avatar_neon.png'
 use_new=design=='new' or (design=='auto' and (not selected or Path(selected).name=='saru_photo.jpg'))
 for path in ((new,selected,fallback) if use_new else (selected,new if design!='original' else fallback,fallback)):
  if not path:continue
  try:
   with Image.open(path) as image:return image.convert('RGBA').copy()
  except (OSError,ValueError,TypeError):continue
 raise OSError('SARU portrait asset is missing. Choose a photo in Appearance.')
