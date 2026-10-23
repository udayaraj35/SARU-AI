"""Explicit primary-screen snapshots and bounded user-selected click operations."""
import time
from PIL import ImageChops,ImageStat

def preview_to_screen(x,y,preview_box,image_size):
 left,top,width,height=preview_box
 if not left<=x<left+width or not top<=y<top+height:raise ValueError('Choose a point inside the screen image.')
 return min(image_size[0]-1,int((x-left)*image_size[0]/width)),min(image_size[1]-1,int((y-top)*image_size[1]/height))

def same_target_patch(old,new,point):
 if old.size!=new.size:return False
 x,y=point;box=(max(0,x-40),max(0,y-30),min(old.width,x+40),min(old.height,y+30))
 delta=ImageChops.difference(old.convert('RGB').crop(box),new.convert('RGB').crop(box))
 return max(ImageStat.Stat(delta).mean)<4

def checked_click(snapshot,point,captured_at,expected_window,automation,current_window):
 if time.monotonic()-captured_at>30:raise ValueError('Preview is older than 30 seconds. Capture a fresh screen first.')
 if current_window()!=expected_window:raise ValueError('The foreground app changed. Capture the screen again.')
 current=automation.screenshot()
 if current.size!=tuple(automation.size()):raise ValueError('Screen scaling mismatch. No click performed.')
 if not same_target_patch(snapshot,current,point):raise ValueError('The target changed since the preview. No click performed; capture again.')
 automation.click(*point)
 return 'One selected click performed. Capture again to verify the result.'
