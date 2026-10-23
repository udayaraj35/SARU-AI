"""Finite corridor routes driven by observed assignments and local queue checks."""
import math,time

class OfficeMotion:
 def __init__(self):self.people={};self.last=None
 def frame(self,agents,assignments,homes,now=None,reduced=False,checks=None):
  now=time.monotonic() if now is None else now
  dt=min(.2,max(0,now-self.last)) if self.last is not None else 0;self.last=now
  by_agent={item['agent']:item for item in assignments};result={};checks=checks or {}
  for agent in agents:
   key=agent['id'];home=homes[key];item=by_agent.get(key);status=item['state'] if item else 'idle'
   identity=(item.get('id',item.get('job','')),status) if item else ('','idle')
   p=self.people.setdefault(key,{'pos':home,'route':[],'identity':None,'check':None,'caption':'At desk'})
   hall=(home[0]+110,310);door=(500,310);manager=(500,230)
   exit_point=(hall[0],home[1])
   origin=p['pos'];outbound=[(hall[0],origin[1]),hall] if origin[1]>346 else [(origin[0],310)]
   visit=outbound+[door,manager,door,hall,exit_point,home]
   if p['identity']!=identity:
    p['identity']=identity
    if status in ('queued','working'):
     p['route']=visit;p['caption']='Collecting assignment'
    elif status=='submitted':
     p['route']=visit;p['caption']='Delivering completed draft'
    else:p['route']=outbound+[hall,exit_point,home] if p['pos']!=home else [];p['caption']='At desk'
   check=checks.get(key)
   if status in ('idle','submitted') and not p['route'] and check is not None and p['check']!=check:
    p['check']=check;p['route']=visit;p['caption']='Checking SARU task queue'
   if reduced:
    p['route']=[];p['pos']=home
   elif p['route']:
    target=p['route'][0];dx=target[0]-p['pos'][0];dy=target[1]-p['pos'][1];distance=math.hypot(dx,dy);travel=150*dt
    if distance<=travel:p['pos']=target;p['route'].pop(0)
    elif distance:p['pos']=(p['pos'][0]+dx/distance*travel,p['pos'][1]+dy/distance*travel)
   moving=bool(p['route'])
   if not moving:p['caption']={'working':'Working on draft','queued':'Waiting for worker','submitted':'Draft submitted','error':'Needs attention','idle':'At desk · available'}.get(status,status.replace('_',' '))
   elif len(p['route'])<=3:p['caption']='Returning to own room'
   result[key]={'position':p['pos'],'moving':moving,'caption':p['caption'],'status':status}
  self.people={key:value for key,value in self.people.items() if key in homes}
  return result
