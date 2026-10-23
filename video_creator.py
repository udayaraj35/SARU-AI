"""Local photo/caption slideshow MP4 creation, optionally with a user-selected audio file."""
from pathlib import Path
import os,subprocess,tempfile,textwrap
from PIL import Image,ImageOps,ImageDraw,ImageFont

def ffmpeg():
 import imageio_ffmpeg
 return imageio_ffmpeg.get_ffmpeg_exe()

def video_duration(path):
 import imageio_ffmpeg
 return imageio_ffmpeg.count_frames_and_secs(str(path))[1]

def create_video(images,captions,output,seconds=3,portrait=False,audio=None,cancel=None):
 if not 1<=len(images)<=30:raise ValueError('Choose 1–30 photos.')
 seconds=float(seconds)
 if not 1<=seconds<=15:raise ValueError('Use 1–15 seconds per photo.')
 output=Path(output)
 if output.suffix.lower()!='.mp4':raise ValueError('Output must be MP4.')
 if output.resolve() in [Path(p).resolve() for p in images]:raise ValueError('Output cannot overwrite a source image.')
 width,height=(720,1280) if portrait else (1280,720);fps=24
 font_path=Path(os.environ.get('WINDIR',r'C:\Windows'))/'Fonts'/'Nirmala.ttf'
 if not font_path.is_file():font_path=font_path.with_name('arial.ttf')
 try:font=ImageFont.truetype(str(font_path),36)
 except OSError:font=ImageFont.load_default()
 fd,temp=tempfile.mkstemp(suffix='.mp4',prefix='.saru-render-',dir=output.parent);os.close(fd)
 process=None
 try:
  command=[ffmpeg(),'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(fps),'-i','-']
  if audio:command+=['-i',str(Path(audio).resolve()),'-map','0:v:0','-map','1:a:0','-c:a','aac','-af','apad']
  command+=['-threads','2','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-t',str(len(images)*seconds),'-movflags','+faststart',temp]
  # Keep encoder output out of a bounded stderr pipe while feeding frames.
  with tempfile.TemporaryFile() as error_log:
   process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=error_log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   for index,path in enumerate(images):
    with Image.open(path) as source:frame=ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'),(width,height))
    caption=captions[index] if index<len(captions) else ''
    if caption:
     draw=ImageDraw.Draw(frame);lines=textwrap.fill(caption[:300],width=30 if portrait else 55);box=draw.multiline_textbbox((0,0),lines,font=font,spacing=8)
     band=box[3]-box[1]+50;draw.rectangle((0,height-band,width,height),fill='#071326');draw.multiline_text((30,height-band+18),lines,font=font,fill='white',spacing=8)
    raw=frame.tobytes()
    for _ in range(round(seconds*fps)):
     if cancel and cancel.is_set():raise RuntimeError('Video creation cancelled.')
     process.stdin.write(raw)
   process.stdin.close()
   if process.wait(timeout=120)!=0:raise RuntimeError('Video encoder failed. Check source photos/audio and output space.')
  os.replace(temp,output)
  return output
 finally:
  if process and process.poll() is None:process.kill();process.wait(timeout=5)
  if process and process.stdin and not process.stdin.closed:
   try:process.stdin.close()
   except OSError:pass
  Path(temp).unlink(missing_ok=True)
