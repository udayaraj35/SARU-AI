"""Read actual local telemetry and supported Windows audio/display endpoints."""
import os
from pathlib import Path
import psutil

def endpoint(kind='speaker'):
 from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
 device=AudioUtilities.GetMicrophone() if kind=='microphone' else AudioUtilities.GetSpeakers()
 if hasattr(device,'EndpointVolume'):return device.EndpointVolume
 from ctypes import POINTER,cast
 from comtypes import CLSCTX_ALL
 return cast(device.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None),POINTER(IAudioEndpointVolume))

def read_controls():
 result={}
 try:
  ep=endpoint();result['volume']=round(ep.GetMasterVolumeLevelScalar()*100);result['muted']=bool(ep.GetMute())
 except Exception:result['volume']=None
 try:
  import screen_brightness_control as sbc
  values=sbc.get_brightness();result['brightness']=int(values[0]) if values else None
 except Exception:result['brightness']=None
 try:result['mic_gain']=round(endpoint('microphone').GetMasterVolumeLevelScalar()*100)
 except Exception:result['mic_gain']=None
 return result

def set_control(name,value):
 value=max(0,min(100,int(value)))
 if name=='volume':endpoint().SetMasterVolumeLevelScalar(value/100,None)
 elif name=='brightness':
  import screen_brightness_control as sbc
  sbc.set_brightness(value,display=0)
 elif name=='mic_gain':endpoint('microphone').SetMasterVolumeLevelScalar(value/100,None)
 elif name=='mute':endpoint().SetMute(bool(value),None)
 else:raise ValueError('Unsupported control')
 return read_controls()

def snapshot():
 adapters=[name for name,info in psutil.net_if_stats().items() if info.isup and not name.lower().startswith(('loopback','lo'))]
 battery=psutil.sensors_battery()
 return {'battery':battery.percent if battery else None,'cpu':psutil.cpu_percent(),'ram':psutil.virtual_memory().percent,'disk':psutil.disk_usage(Path.home().anchor).percent,'adapters':adapters,**read_controls()}


def device_request(operation='read',name=None,value=None):
 """Keep native audio/WMI pointers outside the Tk process entirely."""
 import json,subprocess,sys
 python=Path(sys.executable)
 if python.name.lower()=='pythonw.exe':python=python.with_name('python.exe')
 result=subprocess.run([str(python),str(Path(__file__).resolve()),operation,name or '',str(value if value is not None else '')],capture_output=True,text=True,timeout=15,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if result.returncode:raise RuntimeError('Windows device helper failed; SARU stayed open. Refresh or retry the device control.')
 try:payload=json.loads(result.stdout)
 except ValueError:raise RuntimeError('Windows device helper returned no valid readings.') from None
 if 'error' in payload:raise RuntimeError(payload['error'])
 return payload

def metrics_snapshot():
 adapters=[name for name,info in psutil.net_if_stats().items() if info.isup and not name.lower().startswith(('loopback','lo'))]
 battery=psutil.sensors_battery()
 return {'battery':battery.percent if battery else None,'cpu':psutil.cpu_percent(),'ram':psutil.virtual_memory().percent,'disk':psutil.disk_usage(Path.home().anchor).percent,'adapters':adapters}

def isolated_snapshot():
 result=metrics_snapshot()
 try:result.update(device_request())
 except Exception:result.update(volume=None,brightness=None,mic_gain=None)
 return result

def isolated_set_control(name,value):
 if name not in ('volume','brightness','mic_gain','mute'):raise ValueError('Unsupported control')
 return device_request('set',name,int(value))

def set_single_control(name,value):
 value=max(0,min(100,int(value)))
 if name=='brightness':
  import screen_brightness_control as sbc
  sbc.set_brightness(value,display=0)
  readings=sbc.get_brightness(display=0)
  if not readings:raise RuntimeError('Display did not return brightness.')
  return {'brightness':int(readings[0])}
 if name not in ('volume','mic_gain','mute'):raise ValueError('Unsupported control')
 ep=endpoint('microphone' if name=='mic_gain' else 'speaker')
 if name=='mute':ep.SetMute(bool(value),None)
 else:ep.SetMasterVolumeLevelScalar(value/100,None)
 result={('mic_gain' if name=='mic_gain' else 'volume'):round(ep.GetMasterVolumeLevelScalar()*100)}
 if name!='mic_gain':result['muted']=bool(ep.GetMute())
 return result

if __name__=='__main__':
 import json,sys
 import pythoncom
 pythoncom.CoInitialize()
 if len(sys.argv)>1 and sys.argv[1]=='serve':
  for line in sys.stdin:
   try:
    request=json.loads(line);output=set_single_control(request['name'],request['value'])
   except Exception:output={'error':'Windows rejected the device change. Check device availability and Windows Sound/Display settings.'}
   print(json.dumps(output),flush=True)
 else:
  try:output=set_control(sys.argv[2],int(sys.argv[3])) if len(sys.argv)>1 and sys.argv[1]=='set' else read_controls()
  except Exception as exc:output={'error':type(exc).__name__+': device unavailable'}
  print(json.dumps(output),flush=True)
