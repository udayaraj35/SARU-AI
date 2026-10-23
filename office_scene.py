"""Responsive office floor with finite, state-driven agent movement."""
import math
from office_motion import OfficeMotion

def person(c,x,y,color,tag=(),step=0):
 c.create_rectangle(x-7,y-21,x+7,y-9,fill='#e6b48e',outline='#553e46',tags=tag)
 c.create_rectangle(x-8,y-24,x+7,y-18,fill='#222337',outline='',tags=tag)
 c.create_rectangle(x-10,y-8,x+10,y+9,fill=color,outline='#102036',tags=tag)
 c.create_rectangle(x-8,y+9,x-2,y+19+step,fill='#263b57',outline='',tags=tag)
 c.create_rectangle(x+2,y+9,x+8,y+19-step,fill='#263b57',outline='',tags=tag)

def plant(c,x,y):
 c.create_rectangle(x-7,y,x+7,y+12,fill='#9c6770',outline='')
 for dx,dy in ((-7,-6),(5,-10),(0,-17)):
  c.create_rectangle(x+dx-5,y+dy-5,x+dx+5,y+dy+5,fill='#258e74',outline='#48c697')

def draw_office(c,colors,agents,state,phase,image=None,reduced=False):
 if reduced:phase=0
 c.delete('all');width=max(300,c.winfo_width());height=max(240,c.winfo_height())
 rows=math.ceil(len(agents)/3);world_height=400+rows*200
 sx=width/1000;sy=height/world_height;scale=min(sx,sy)
 # The full office fits the current window; room count grows the world.
 c.create_rectangle(10,10,990,world_height-10,fill=colors['panel'],outline=colors['line'],width=3)
 for y in range(24,world_height-10,22):c.create_line(12,y,988,y,fill=colors['line'],stipple='gray25')
 c.create_rectangle(20,277,980,346,fill=colors['field'],outline=colors['line'])
 c.create_line(40,310,960,310,fill=colors['accent'],dash=(5,12))
 def text(x,y,value,size=12,color=None,tag=(),anchor='center',wrap=0):
  c.create_text(x,y,text=value,font=('Segoe UI',max(7,int(size*scale)),'bold'),fill=color or colors['text'],tags=tag,anchor=anchor,width=wrap)
 def room(x,y,w,h,title,tag,color):
  c.create_rectangle(x+5,y+6,x+w+5,y+h+6,fill='#020915',outline='',tags=tag)
  c.create_rectangle(x,y,x+w,y+h,fill=colors['field'],outline=color,width=2,tags=tag)
  c.create_rectangle(x,y,x+w,y+36,fill=colors['panel'],outline='',tags=tag)
  text(x+14,y+18,title,13,tag=tag,anchor='w')
 room(330,38,340,205,'SARU · MAIN OFFICE','saru_desk',colors['primary'])
 if image:c.create_image(365,121,image=image,tags='saru_desk')
 c.create_rectangle(390,147,610,183,fill='#65516b',outline='#a58caa',tags='saru_desk')
 c.create_rectangle(455,107,535,151,fill=colors['panel'],outline=colors['accent'],width=2,tags='saru_desk')
 person(c,565,142,colors['primary'],'saru_desk')
 text(500,208,{'owner_review':'READY FOR BOSS REVIEW','sarureview':'REVIEWING SUBMISSIONS','working':'TEAM WORKING','planning':'PLANNING ASSIGNMENTS','saved':'SAVED TO PC'}.get(state['state'],state['state'].replace('_',' ').upper()) if state else 'WAITING FOR YOUR TASK',11,colors['accent'],'saru_desk')
 room(35,50,265,190,'MIND · Task routing','mind',colors['accent'])
 nodes=[(85,131,'Task'),(163,113,'SARU'),(232,154,'Team')]
 for x,y,t in nodes:
  c.create_line(x,y,163,113,fill=colors['accent'],width=2,tags='mind')
  c.create_oval(x-22,y-22,x+22,y+22,fill=colors['panel'],outline=colors['accent'],tags='mind');text(x,y,t,9,tag='mind')
 text(167,211,'Model · Plan · Review',10,colors['muted'],'mind')
 room(700,50,265,190,'MEMORY · Saved knowledge','memory',colors['accent'])
 for row in range(3):
  c.create_rectangle(730,105+row*25,936,121+row*25,fill=colors['panel'],outline=colors['line'],tags='memory')
  c.create_line(744,113+row*25,887,113+row*25,fill=colors['accent'],tags='memory')
 text(832,211,'Open saved notes / memory',10,colors['muted'],'memory')
 text(500,369,'TEAM ROOMS · Click a room to open its agent',12,colors['accent'],'team')
 homes={};positions={}
 for i,agent in enumerate(agents):
  x=38+(i%3)*320;y=400+(i//3)*200;homes[agent['id']]=(x+192,y+104);positions[agent['id']]=(x,y)
 if not hasattr(c,'office_motion'):c.office_motion=OfficeMotion()
 actors=c.office_motion.frame(agents,state.get('assignments',[]) if state else [],homes,reduced=reduced,checks=state.get('_checkins',{}) if state else {})
 for i,agent in enumerate(agents):
  key=agent['id'];x,y=positions[key];actor=actors[key];s=actor['status'];tag='room_'+key
  color=colors['primary'] if s=='working' else '#40d8a0' if s=='submitted' else '#ff985c' if s in ('error','interrupted') else colors['accent']
  room(x,y,284,166,agent['room'][:25],tag,color)
  c.create_rectangle(x+280,y+91,x+289,y+122,fill=colors['panel'],outline='',tags=tag)
  for k in range(6):c.create_rectangle(x+16+k*7,y+48,x+20+k*7,y+74,fill=('#359ca7','#b4729d','#d4ad69')[k%3],outline='',tags=tag)
  c.create_rectangle(x+206,y+48,x+264,y+77,fill='#143455',outline=colors['accent'],tags=tag)
  c.create_line(x+235,y+48,x+235,y+77,fill=colors['accent'],tags=tag)
  c.create_rectangle(x+62,y+91,x+223,y+114,fill='#665568',outline='#a08ca6',tags=tag)
  c.create_rectangle(x+86,y+61,x+145,y+97,fill=colors['panel'],outline=color,width=2,tags=tag)
  if s=='working':
   for k in range(3):c.create_line(x+94,y+70+k*8,x+119+(phase+k)%11,y+70+k*8,fill=color,tags=tag)
  plant(c,x+262,y+122)
  text(x+14,y+145,agent['name'][:19]+' · '+s,10,color,tag,anchor='w')
 # Draw people after walls and furniture so corridor movement remains visible.
 for agent in agents:
  actor=actors[agent['id']];x,y=actor['position'];color=colors['primary'] if actor['status']=='working' else '#40d8a0' if actor['status']=='submitted' else colors['accent']
  person(c,x,y,color,'room_'+agent['id'],2 if actor['moving'] and phase%4<2 else 0)
  if actor['moving']:text(x,y-39,actor['caption'],9,colors['text'],wrap=190)
 c.scale('all',0,0,sx,sy)
 c.configure(scrollregion=(0,0,width,height))
