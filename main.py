"""Little Tides -- standalone Windows prototype. No network or browser code."""
import os, sys, math, json, random, time, array
from pathlib import Path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import pygame
from pygame import Vector2 as V
from physics import Handline, tip_acceleration
from data import SPECIES, achievement_key
from fish_art import draw_fish
from presentation import GameView, W, H, SCENE, PPM, SURFACE, world

CREAM='#f5f1e7'; INK='#233e40'; MUTED='#718380'; GREEN='#3f7463'; LINE='#dedfd3'; GOLD='#c19349'
SAVE_NAME='little-tides-save.json'
FISH_IDS=['perch','walleye','pike','sucker']

def storage_directory():
    if getattr(sys,'frozen',False) and sys.platform=='darwin':
        # A downloaded .app can be read-only or translocated by macOS.
        return Path.home()/'Library'/'Application Support'/'Little Tides'
    return Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent

def clamp(v,a,b): return max(a,min(b,v))
def color(c): return pygame.Color(c)
def mix(a,b,t):
    a=color(a); b=color(b)
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

class Fish:
    def __init__(self, species, rng):
        self.species=species; self.data=SPECIES[species]
        lo,hi=self.data['size']
        self.cm=round(rng.triangular(lo,hi,lo+(hi-lo)*.22),1)
        self.kg=round(self.data['kg']*(self.cm/((lo+hi)/2))**3,2)
        depths={'perch':(.7,2.6),'walleye':(2.3,4.6),'pike':(1,3.4),'sucker':(3.7,4.6)}
        self.pos=V(rng.uniform(5.0,16.4),rng.uniform(*depths[species]))
        self.home_y=self.pos.y; self.vel=V(rng.choice([-1,1])*.35,0)
        self.phase=rng.random()*math.tau; self.interest=0; self.cooldown=0
        self.stamina=1.; self.hooked=False
    def update(self,dt,t,hook,can_bite):
        self.cooldown=max(0,self.cooldown-dt)
        distance=(hook-self.pos).length()
        affinity=self.data['baits'].get('worm',0)
        attracted=can_bite and affinity>0 and self.cooldown<=0 and hook.y>.13 and distance<3.2
        if attracted:
            delta=hook-self.pos
            desired=delta.normalize()*(.34+affinity*.31) if delta.length()>.01 else V()
            self.vel=self.vel.lerp(desired,min(1,dt*2))
            self.interest+=dt
        else:
            self.vel.x+=math.sin(t*.35+self.phase)*.06*dt
            self.vel.x=clamp(self.vel.x,-.48,.48)
            if abs(self.vel.x)<.12: self.vel.x=.18 if self.pos.x<10 else -.18
            self.vel.y=math.sin(t*.7+self.phase)*.09+(self.home_y-self.pos.y)*.12
            self.interest=0
        self.pos+=self.vel*dt
        if self.pos.x<4.9: self.pos.x=4.9;self.vel.x=abs(self.vel.x)
        if self.pos.x>17.3: self.pos.x=17.3;self.vel.x=-abs(self.vel.x)
        self.pos.y=clamp(self.pos.y,.35,min(5.0,3.3+self.pos.x*.16))
        return attracted and distance<.23 and self.interest>.7

class Game(GameView):
    def __init__(self,headless=False):
        pygame.init()
        self.headless=headless
        self.screen=pygame.display.set_mode((1280,800),pygame.RESIZABLE)
        pygame.display.set_caption('Little Tides')
        self.canvas=pygame.Surface((W,H))
        self.clock=pygame.time.Clock();self.running=True
        self.fonts={};self.buttons=[];self.mouse=(0,0);self.t=0.;self.accumulator=0
        self.rng=random.Random();self.angle=-.62;self.target_angle=-.62
        self.base=V(2.65,-.13);self.line=Handline(self.anchor)
        self.phase='ready';self.charge=0;self.holding=False;self.pulling=False;self.grip=0.
        self.bite_left=0;self.hooked=None;self.catch=None;self.break_time=0;self.slack_time=0
        self.panel=None;self.toast='';self.toast_time=0;self.scroll=0;self.splash=[]
        self.last_depth=0;self.session=0;self.casts=0;self.hand_phase=0
        self.show_hints=True;self.fullscreen=False
        self.sfx={};self.muted=False;self.load();self.init_audio()
        self.fish=[];self.spawn_fish()
        self.background=self.make_background()
        self.show_toast('Welcome to Big Whiteshell. Your first adventure starts with a worm.',7)
        icon=pygame.Surface((64,64),pygame.SRCALPHA)
        pygame.draw.circle(icon,GREEN,(32,32),30)
        pygame.draw.arc(icon,CREAM,(13,12,37,33),.1,3.1,3)
        pygame.draw.line(icon,CREAM,(49,26),(49,44),3)
        pygame.draw.arc(icon,CREAM,(32,34,18,19),math.pi,math.tau,3)
        pygame.display.set_icon(icon)

    @property
    def anchor(self): return self.base+V(math.cos(self.angle),math.sin(self.angle))*1.9

    @property
    def line_anchor(self):
        # Once the free hand takes the line, the active section starts there.
        # The tied section still runs from the stick tip to that hand.
        hand=self.base+V(.08,-.65)
        return self.anchor.lerp(hand,self.grip)

    def text(self,txt,x,y,size=18,c=INK,bold=False,serif=False,center=False):
        image=self.font(size,bold,serif).render(str(txt),True,c)
        rect=image.get_rect(center=(x,y)) if center else image.get_rect(topleft=(x,y))
        self.canvas.blit(image,rect);return rect
    def wrap(self,txt,x,y,width,size=18,c=MUTED,line_height=None):
        line_height=line_height or size+8;line=''
        for word in txt.split():
            if self.font(size).size(line+word)[0]>width and line:
                self.text(line,x,y,size,c);y+=line_height;line=''
            line+=word+' '
        if line:self.text(line,x,y,size,c)
        return y+line_height
    def show_toast(self,msg,duration=4):self.toast=msg;self.toast_time=duration
    def save_path(self):
        return storage_directory()/SAVE_NAME
    def load(self):
        self.save={'version':1,'records':{},'released':0,'casts':0,'notes':False}
        try:
            raw=json.loads(self.save_path().read_text(encoding='utf-8'))
            if isinstance(raw,dict) and raw.get('version')==1 and isinstance(raw.get('records'),dict):
                self.save.update(raw)
        except (OSError,ValueError,TypeError):pass
    def persist(self):
        if self.headless:return
        try:
            path=self.save_path();path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp')
            tmp.write_text(json.dumps(self.save,indent=2),encoding='utf-8');tmp.replace(path)
        except OSError:self.show_toast('Could not save here. Move the game folder to a writable location.',6)
    def init_audio(self):
        try:
            pygame.mixer.init(frequency=22050,size=-16,channels=1,buffer=512)
            for name,freq in [('cast',370),('bite',740),('catch',980),('miss',210)]:
                n=6500 if name=='catch' else 2400
                samples=array.array('h',(int(1800*math.sin(math.tau*(freq+(i/n)*180)*i/22050)*(1-i/n)**2) for i in range(n)))
                self.sfx[name]=pygame.mixer.Sound(buffer=samples)
        except pygame.error:pass
    def sound(self,name):
        if not self.muted and name in self.sfx:self.sfx[name].play()
    def spawn_fish(self):
        self.fish=[Fish(k,self.rng) for k in FISH_IDS for _ in range(3 if k=='perch' else 2)]
        # A nearby perch makes the first worm-only lesson approachable.
        self.fish[0].pos=V(6.8,1.7);self.fish[0].home_y=1.7

    def start_charge(self):
        if self.phase=='ready':self.phase='charge';self.charge=0;self.holding=True
        elif self.phase=='bite':self.set_hook()
        elif self.phase in ('soak','flight'):
            self.show_toast('Hold SPACE or the right mouse button to gather the line by hand.')
    def release_cast(self):
        if self.phase=='charge':
            self.angle=-.62;self.target_angle=-.62
            self.line.launch(self.anchor,self.charge)
            self.phase='flight';self.casts+=1;self.save['casts']+=1
            self.holding=False;self.sound('cast')
            self.show_toast('Let it settle. A bare hook and worm sink slowly through the water.',5)
    def set_hook(self):
        if self.phase!='bite':return
        self.phase='fight';self.hooked.hooked=True;self.hooked.stamina=1
        self.target_angle=-1.05
        self.hooked.pos=V(self.line.hook);self.break_time=0;self.slack_time=0
        self.sound('bite');self.show_toast('Hook set! Hold SPACE to hand-pull. Rest when tension is high.',5)
    def reset_line(self,msg=None):
        if self.hooked:
            self.hooked.hooked=False;self.hooked.cooldown=10
            self.hooked.vel=V(.65,.2)
        self.hooked=None;self.phase='ready';self.pulling=False;self.grip=0.;self.line.reset(self.anchor)
        if msg:self.show_toast(msg,4)
    def land_fish(self):
        f=self.hooked;self.catch=f;self.phase='landed';self.pulling=False
        key=achievement_key('Manitoba',f.species)
        previous=self.save['records'].get(key,{'best':0,'count':0,'master':False})
        self.new_master=f.cm>=f.data['master'] and not previous['master']
        previous.update(best=max(previous['best'],f.cm),count=previous['count']+1,master=previous['master'] or f.cm>=f.data['master'])
        self.save['records'][key]=previous;self.session+=1;self.persist();self.sound('catch')
    def release_fish(self):
        if self.catch:
            self.save['released']+=1
            self.fish.remove(self.catch)
            self.fish.append(Fish(self.catch.species,self.rng))
        self.catch=None;self.hooked=None;self.reset_line('Released safely. Your catch is saved in the field journal.');self.persist()

    def physics_step(self,dt):
        if self.panel or self.phase=='landed':return
        self.t+=dt;self.toast_time=max(0,self.toast_time-dt)
        if self.phase=='charge':
            self.charge=clamp(self.charge+dt*.6,0,1)
            self.angle=-.62-self.charge*.85
        else:self.angle+=(self.target_angle-self.angle)*min(1,dt*6)
        if self.phase in ('ready','charge'):
            self.line.step(dt,self.anchor)
        else:
            if self.pulling and self.grip<1:
                old_grip=self.grip
                self.grip=min(1,self.grip+dt*1.5)
                # Taking hold does not create extra line: the tied section
                # between stick and hand consumes part of the fixed 6 m.
                taken=(self.anchor-(self.base+V(.08,-.65))).length()*(self.grip-old_grip)
                self.line.length=max(.45,self.line.length-taken)
            force=None
            if self.phase=='fight' and self.hooked:
                f=self.hooked
                run=max(0,math.sin(self.t*2.1+f.phase))**5
                strength=(.85+f.kg*.15)*(.3+.7*f.stamina)
                force=V((1.4+run*4.0)*strength,math.sin(self.t*1.7+f.phase)*strength)
                if self.line.hook.y<.15:force.y+=3
            was_wet=self.line.hook.y>=0
            self.line.step(dt,self.line_anchor,self.pulling,force)
            if self.phase=='flight' and not was_wet and self.line.hook.y>=0:
                self.phase='soak';self.splash.append([V(self.line.hook.x,0),0])
                self.sound('cast')
            if self.phase=='flight' and self.line.hook.y>=0:self.phase='soak'
            if self.phase=='bite':
                self.bite_left-=dt
                # A nibble displaces the submerged hook: visible on the line.
                self.line.nodes[-1].x+=math.sin(self.t*32)*dt*.17
                if self.bite_left<=0:
                    self.hooked.cooldown=12;self.hooked=None;self.phase='soak'
                    self.show_toast('That nibble got away. Wait for another, then tap LEFT CLICK.');self.sound('miss')
            if self.phase=='fight':
                f=self.hooked;f.pos=V(self.line.hook)
                self.break_time=max(0,self.break_time+(dt if self.line.tension>1.25 else -dt*2))
                self.slack_time=max(0,self.slack_time+(dt if self.line.tension<.012 and not self.pulling else -dt*2))
                # Hand gathering tires the fish; free runs allow a little recovery.
                if self.pulling and self.line.tension>.04:f.stamina=max(0,f.stamina-dt*(.075/(1+f.kg*.14)))
                else:f.stamina=min(1,f.stamina+dt*.018)
                if self.break_time>1.1:self.reset_line('The old line snapped. A fresh length is tied on for the next cast.');self.sound('miss')
                elif self.slack_time>8:self.reset_line('Too much slack for too long. The fish shook the hook.');self.sound('miss')
                elif self.line.length<1.05 and f.stamina<.35:self.land_fish()
                elif self.line.length<1.05 and f.stamina>=.35:
                    self.line.length=min(6,self.line.length+dt*.65)
            elif self.phase in ('soak','flight') and self.line.length<.55:
                self.reset_line('Line gathered. Hold LEFT CLICK over the lake for your next cast.')
        for f in self.fish:
            if f is self.hooked:continue
            if f.update(dt,self.t,self.line.hook,self.phase=='soak'):
                self.phase='bite';self.hooked=f;self.bite_left=2.5
                self.show_toast('A nibble! Tap LEFT CLICK or SPACE to lift the stick and set the hook.',3)
                self.sound('bite')
        for s in self.splash:s[1]+=dt
        self.splash=[s for s in self.splash if s[1]<1.4]
        if self.pulling:self.hand_phase+=dt*6

    def fish_art(self,fish,x,y,scale=1,alpha=255,face=None):
        return draw_fish(self,fish,x,y,scale,alpha,face)


    def record(self,k):return self.save['records'].get(achievement_key('Manitoba',k),{})

    def open_panel(self,panel):
        self.panel=panel;self.pulling=False;self.holding=False;self.menu_index=0
        if self.phase=='charge':self.phase='ready';self.line.reset(self.anchor)


    def toggle_sound(self):self.muted=not self.muted
    def quit(self):self.persist();self.running=False
    def mouse_position(self,pos):
        w,h=self.screen.get_size();f=min(w/W,h/H)
        return ((pos[0]-(w-W*f)/2)/f,(pos[1]-(h-H*f)/2)/f)
    def event(self,event):
        if event.type==pygame.QUIT:self.quit()
        elif event.type==pygame.WINDOWFOCUSLOST:
            self.pulling=False
            if not self.panel and self.phase!='landed':self.open_panel('help')
        elif event.type==pygame.MOUSEMOTION:self.mouse=self.mouse_position(event.pos)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            self.mouse=self.mouse_position(event.pos)
            if event.button==1:
                for rect,action,enabled in reversed(self.buttons):
                    if rect.collidepoint(self.mouse):
                        if enabled:action()
                        return
                if not self.panel and SCENE.collidepoint(self.mouse) and self.phase!='landed':self.start_charge()
            elif event.button==3 and not self.panel and self.phase not in ('landed','ready','charge'):
                if self.phase=='bite':self.set_hook()
                self.pulling=True
        elif event.type==pygame.MOUSEBUTTONUP:
            if event.button==1:self.release_cast()
            elif event.button==3:self.pulling=False
        elif event.type==pygame.MOUSEWHEEL and not self.panel:
            self.target_angle=clamp(self.target_angle-event.y*.1,-1.35,-.15)
        elif event.type==pygame.KEYDOWN:
            if self.panel in ('help','roadmap') and event.key in (pygame.K_UP,pygame.K_DOWN,pygame.K_RETURN):
                if event.key==pygame.K_UP:self.menu_index=(self.menu_index-1)%6
                elif event.key==pygame.K_DOWN:self.menu_index=(self.menu_index+1)%6
                elif getattr(self,'menu_actions',None):self.menu_actions[self.menu_index]()
                return
            if self.panel=='controls' and event.key==pygame.K_RETURN:
                self.open_panel('help');return
            if event.key==pygame.K_ESCAPE:
                if self.phase=='landed':self.release_fish()
                else:self.open_panel(None if self.panel else 'help')
            elif event.key==pygame.K_j and self.phase!='landed':self.open_panel(None if self.panel=='journal' else 'journal')
            elif event.key==pygame.K_h and self.phase!='landed':self.open_panel(None if self.panel else 'help')
            elif event.key==pygame.K_m:self.toggle_sound()
            elif event.key==pygame.K_F1:self.show_hints=not self.show_hints
            elif event.key==pygame.K_F11:self.toggle_fullscreen()
            elif event.key==pygame.K_SPACE and not self.panel:
                if self.phase=='bite':self.set_hook()
                if self.phase in ('soak','fight','flight'):self.pulling=True
            elif event.key==pygame.K_RETURN and self.phase=='landed':self.release_fish()
        elif event.type==pygame.KEYUP:
            if event.key==pygame.K_SPACE:self.pulling=False

    def run(self):
        while self.running:
            frame_dt=min(.05,self.clock.tick(60)/1000)
            for event in pygame.event.get():self.event(event)
            if not self.panel and self.phase!='landed':
                keys=pygame.key.get_pressed()
                if keys[pygame.K_w] or keys[pygame.K_UP]:self.target_angle=max(-1.35,self.target_angle-frame_dt*.6)
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:self.target_angle=min(-.15,self.target_angle+frame_dt*.6)
            self.accumulator+=frame_dt
            while self.accumulator>=1/120:
                self.physics_step(1/120);self.accumulator-=1/120
            self.draw()
        pygame.quit()

def main():
    if '--smoke-test' in sys.argv:
        os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
        g=Game(headless=True)
        for _ in range(120):g.physics_step(1/120)
        g.draw()
        out=Path(sys.argv[sys.argv.index('--smoke-test')+1])
        pygame.image.save(g.canvas,str(out))
        pygame.quit();return
    try:Game().run()
    except Exception:
        import traceback
        target=storage_directory();target.mkdir(parents=True,exist_ok=True)
        (target/'little-tides-error.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise

if __name__=='__main__':main()
