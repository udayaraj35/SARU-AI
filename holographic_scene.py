"""Code-drawn particle sphere and wave floor; no video assets or fake telemetry."""
import math
from PIL import Image,ImageDraw


def rgb(value):return tuple(int(value[i:i+2],16) for i in (1,3,5))
def mix(a,b,t):return tuple(round(x+(y-x)*max(0,min(1,t))) for x,y in zip(a,b))


class HolographicScene:
    def __init__(self,width,height,theme='Neon Rose',points=1800):
        self.width=max(40,int(width));self.height=max(40,int(height));self.theme=theme
        self.scale=min(1,960/self.width,760/self.height)
        self.w=max(40,round(self.width*self.scale));self.h=max(40,round(self.height*self.scale))
        self.cx=self.w*.5;self.cy=self.h*.43;self.radius=min(self.w*.32,self.h*.285)
        colors={'Neon Rose':('#b19aff','#355dff'),'Cyber Violet':('#c2a3ff','#514bff'),'Ocean Cyan':('#8feaff','#355dff'),'Emerald Night':('#86eed2','#326ad9')}
        a,b=colors.get(theme,colors['Neon Rose']);self.light=rgb(a);self.blue=rgb(b)
        self.background=Image.new('RGB',(self.w,self.h));draw=ImageDraw.Draw(self.background)
        for y in range(self.h):draw.line((0,y,self.w,y),fill=mix((6,8,19),(12,13,36),y/self.h))
        self.points=[];golden=math.pi*(3-math.sqrt(5))
        self.voice_zoom=.88
        count=max(100,min(1800,int(points)))
        for i in range(count):
            y=1-2*(i+.5)/count;r=math.sqrt(max(0,1-y*y));a=i*golden
            self.points.append((math.cos(a)*r,y,math.sin(a)*r))

    @property
    def sphere_bounds(self):
        s=self.scale
        return ((self.cx-self.radius)/s,(self.cy-self.radius)/s,(self.cx+self.radius)/s,(self.cy+self.radius)/s)

    def render(self,phase=0,level=0,state='STOPPED',reduced=False):
        phase=0 if reduced else float(phase)
        level=0 if reduced or state not in ('LISTENING','SPEAKING') else max(0,min(1,float(level)))
        target=1.04 if state in ('LISTENING','SPEAKING') else .88
        self.voice_zoom=1 if reduced else self.voice_zoom+(target-self.voice_zoom)*.2
        zoom=1 if reduced else self.voice_zoom*(1+.012*math.sin(phase*1.7) if state in ('LISTENING','SPEAKING') else 1)
        image=self.background.copy();draw=ImageDraw.Draw(image)
        horizon=self.h*.72
        # A perspective wave mesh. Motion is decorative; audio only changes
        # the sphere deformation after an actual input/output level event.
        for row in range(18):
            depth=(row+1)/18;line=[]
            for col in range(47):
                x=(col/46-.5)*self.w*(.48+depth*.8)+self.w*.5
                wave=math.sin(col*.29+phase*.8+row*.36)*self.h*.013*depth
                y=horizon+depth*depth*self.h*.32+wave
                line.extend((x,y))
            draw.line(line,fill=mix((16,20,55),self.blue,.18+depth*.28),width=1)
        for col in range(0,47,2):
            line=[]
            for row in range(18):
                depth=(row+1)/18
                x=(col/46-.5)*self.w*(.48+depth*.8)+self.w*.5
                y=horizon+depth*depth*self.h*.32+math.sin(col*.29+phase*.8+row*.36)*self.h*.013*depth
                line.extend((x,y))
            draw.line(line,fill=(22,32,88),width=1)
        angle=phase*.22;ca,sa=math.cos(angle),math.sin(angle);tilt=.18+math.sin(phase*.24)*.12
        ct,st=math.cos(tilt),math.sin(tilt);projected=[]
        for index,(x,y,z) in enumerate(self.points):
            morph=1+.065*math.sin(4*y+phase*.8)+.05*math.sin(5*x-3*z+phase*.55)
            morph+=level*.12*math.sin(7*y+phase*2.8)
            xx=x*ca+z*sa;zz=-x*sa+z*ca;yy=y*ct-zz*st;zz=y*st+zz*ct
            perspective=3.2/(3.2-zz*.36)
            px=self.cx+xx*self.radius*morph*perspective*zoom
            py=self.cy+yy*self.radius*morph*perspective*zoom
            brightness=.38+.62*(zz+1)/2
            color=mix(self.blue,self.light,(yy+1)/2)
            color=tuple(round(v*brightness) for v in color)
            dot=(.8+.6*(zz+1)/2)*max(.7,self.scale)
            projected.append((zz,px,py,dot,color,index))
        for z,x,y,size,color,index in sorted(projected):
            draw.ellipse((x-size,y-size,x+size,y+size),fill=color)
            if z>.65 and index%67==0:draw.point((round(x),round(y)),fill=(223,219,255))
        if image.size!=(self.width,self.height):image=image.resize((self.width,self.height),Image.Resampling.BILINEAR)
        return image


def draw_hologram(view,width,height):
    from PIL import ImageTk
    from theme_manager import palette
    c=view.ring;p=palette(view.cfg.get('theme'));c.delete('all');c.configure(bg='#070a18')
    view.holo_renderer=HolographicScene(width,height,view.cfg.get('theme','Neon Rose'))
    view.holo_phase=getattr(view,'holo_phase',0)
    view.holo_photo=ImageTk.PhotoImage(view.holo_renderer.render(view.holo_phase,state=view.hero_voice_state,reduced=view.cfg.get('reduced_motion',False)))
    view.holo_image_item=c.create_image(0,0,image=view.holo_photo,anchor='nw')
    view.avatar_frames=[];view.hero_meter=[];view.hero_meter_center=None
    c.create_text(20,18,text='SARU  /  INTELLIGENT WORKSPACE' if width>=560 else 'SARU AI',fill=p['text'],anchor='nw',font=('Segoe UI',11,'bold'))
    view.scene_metrics=c.create_text(width-20,22,text='CPU —   RAM —',fill='#99b9e9',anchor='ne',font=('Segoe UI',9))
    view.scene_status_dot=c.create_oval(width*.5-7,height*.125-4,width*.5+1,height*.125+4,fill='#8a96bc',outline='')
    view.hero_voice_label=c.create_text(width*.5+10,height*.125,text=view.hero_voice_state.replace('_',' ').title(),fill=p['text'],anchor='w',font=('Segoe UI',10,'bold'))
    c.create_text(width*.5,height*.748,text='SARU AI',fill=p['text'],font=('Segoe UI',18,'bold'))
    c.create_text(width*.5,height*.791,text='Click the sphere to open real saved memory',fill='#8a96bc',font=('Segoe UI',9))
    cell=min(125,(width-34)/3)
    for i,button in enumerate(view.scene_buttons):
        c.create_window(width*.5+(i-1)*(cell+5),height*.86,window=button,width=cell,height=32)
    for i,index in enumerate((0,3)):
        c.create_window(width*.5+(i-.5)*(cell+8),height*.947,window=view.hero_voice_buttons[index],width=cell,height=30)
    view.update_scene_readings({})
