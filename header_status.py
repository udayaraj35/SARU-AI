"""Local clocks/BS calendar and actual Open-Meteo temperature, never sample values."""
import datetime,threading,time
from zoneinfo import ZoneInfo
from queue import Queue,Empty
import tkinter as tk
import requests

def clock_text(now=None,zone='Europe/Sofia'):
 now=now or datetime.datetime.now(datetime.timezone.utc)
 local=now.astimezone(ZoneInfo(zone));nepal=now.astimezone(ZoneInfo('Asia/Kathmandu'))
 try:
  import nepali_datetime
  bs=nepali_datetime.date.from_datetime_date(nepal.date()).strftime('%K %N %D')+' BS'
 except (ImportError,ValueError):bs='Nepali calendar unavailable'
 return local.strftime('%H:%M:%S  •  %a, %d %b %Y')+'  '+zone, 'नेपाल: '+bs

def fetch_weather(city,session=requests):
 if not city.strip() or len(city)>100:raise ValueError('Set a weather city in Settings.')
 r=session.get('https://geocoding-api.open-meteo.com/v1/search',params={'name':city,'count':1,'language':'en','format':'json'},timeout=10);r.raise_for_status()
 rows=r.json().get('results',[])
 if not rows:raise ValueError('Weather city not found.')
 place=rows[0]
 r=session.get('https://api.open-meteo.com/v1/forecast',params={'latitude':place['latitude'],'longitude':place['longitude'],'current':'temperature_2m,weather_code','temperature_unit':'celsius','timezone':'auto'},timeout=10);r.raise_for_status()
 current=r.json()['current'];temperature=current['temperature_2m']
 if type(temperature) not in (int,float):raise ValueError('Temperature unavailable.')
 code=current.get('weather_code');description='Clear' if code==0 else 'Cloudy' if code in (1,2,3) else 'Fog' if code in (45,48) else 'Rain' if code in (51,53,55,56,57,61,63,65,66,67,80,81,82) else 'Snow' if code in (71,73,75,77,85,86) else 'Thunderstorm' if code in (95,96,99) else 'Weather'
 return f"{place['name']} • {temperature:.1f}°C • {description} • Open-Meteo {current['time']}"

class HeaderStatus(tk.Frame):
 def __init__(self,parent,config):
  super().__init__(parent,bg='#061226');self.config_data=config;self.closed=False;self.job=None;self.next_weather=0;self.busy=False;self.events=Queue()
  self.clock=tk.Label(self,bg='#061226',fg='#e8f5ff',font=('Segoe UI',10,'bold'));self.clock.pack(anchor='w')
  self.nepali=tk.Label(self,bg='#061226',fg='#ff4c91',font=('Segoe UI',10,'bold'));self.nepali.pack(anchor='w')
  self.weather=tk.Label(self,bg='#061226',fg='#7ad9ee',font=('Segoe UI',9),wraplength=560,justify='left');self.weather.pack(anchor='w')
  self.bind('<Destroy>',self.cleanup,add='+');self.tick()
 def tick(self):
  if self.closed:return
  try:a,b=clock_text(zone=self.config_data.get('display_timezone','Europe/Sofia'))
  except Exception:a,b=clock_text()
  self.clock.configure(text=a);self.nepali.configure(text=b)
  try:self.weather.configure(text=self.events.get_nowait());self.busy=False
  except Empty:pass
  if not self.busy and time.monotonic()>=self.next_weather:
   self.busy=True;self.next_weather=time.monotonic()+900;city=self.config_data.get('weather_city','Sofia')
   self.weather.configure(text='Weather: checking '+city+'…')
   def work():
    try:value=fetch_weather(city)
    except Exception:value='Weather unavailable • '+city+' • next refresh in 15 min'
    self.events.put(value)
   threading.Thread(target=work,daemon=True).start()
  self.job=self.after(1000,self.tick)
 def cleanup(self,event):
  if event.widget is self:
   self.closed=True
   if self.job:
    try:self.after_cancel(self.job)
    except tk.TclError:pass
