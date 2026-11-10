"""Game presentation: an uninterrupted lake, contextual HUD, and diegetic journal."""
import math
import random
import pygame
from pygame import Vector2 as V
from data import SPECIES
from angler_art import draw_angler_character

W,H=1440,900
SCENE=pygame.Rect(0,0,W,H)
PPM=78
SURFACE=430
PAPER='#dfd2ae'
WHITE='#f5ebce'
INK='#354239'

def world(p):return V(p.x*PPM,SURFACE+p.y*PPM)
def blend(a,b,t):
    a=pygame.Color(a);b=pygame.Color(b)
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

class GameView:
    def font(self,size,bold=False,serif=False):
        key=(size,bold,serif)
        if key not in self.fonts:
            self.fonts[key]=pygame.font.SysFont(('segoeprint','noteworthy','helvetica') if serif else ('bahnschrift','arial','helvetica'),size,bold=bold)
        return self.fonts[key]

    def hud_text(self,txt,x,y,size=20,c=WHITE,bold=False,center=False,alpha=255):
        f=self.font(size,bold)
        text=f.render(str(txt),True,c)
        shadow=f.render(str(txt),True,'#182d2d')
        text.set_alpha(alpha);shadow.set_alpha(int(alpha*.8))
        rect=text.get_rect(center=(x,y)) if center else text.get_rect(topleft=(x,y))
        self.canvas.blit(shadow,rect.move(1,2));self.canvas.blit(text,rect)
        return rect

    def button(self,rect,label,action,primary=False,enabled=True):
        rect=pygame.Rect(rect)
        hover=rect.collidepoint(self.mouse) and enabled
        if hover:
            self.hud_text('>',rect.x+8,rect.centery,25,'#eac47a',True,center=True)
        self.hud_text(label,rect.centerx,rect.centery,24,'#eac47a' if hover else WHITE,center=True,alpha=255 if enabled else 90)
        self.buttons.append((rect,action,enabled))

    def make_background(self):
        s=pygame.Surface((W,H));r=random.Random(193)
        for y in range(SURFACE):
            pygame.draw.line(s,blend('#89b5bc','#f1dca9',y/SURFACE),(0,y),(W,y))
        # Low early-morning sun and small, broken cloud banks.
        glow=pygame.Surface((W,H),pygame.SRCALPHA)
        for radius in range(120,32,-4):
            pygame.draw.circle(glow,(255,230,173,2),(1040,166),radius)
        s.blit(glow,(0,0));pygame.draw.circle(s,'#ffedb6',(1040,166),35)
        for x,y,stretch in [(88,112,1.1),(543,65,.85),(1172,93,.9),(816,131,.6)]:
            cloud=pygame.Surface((250,65),pygame.SRCALPHA)
            for k in range(18):
                xx=r.randrange(18,220);yy=r.randrange(21,42)
                pygame.draw.ellipse(cloud,(244,232,196,60),(xx,yy,r.randrange(20,67),r.randrange(6,18)))
            s.blit(pygame.transform.smoothscale(cloud,(int(250*stretch),int(65*stretch))),(x,y))
        # Receding granite ridges. Several tree layers create actual scenic depth.
        for base,height,c,seed in [(333,67,'#9cb7ae',10),(358,52,'#82a397',29),(382,32,'#628c7c',41)]:
            rr=random.Random(seed);points=[(0,base+25)]
            for x in range(-30,W+40,35):
                points.append((x,base-math.sin(x*.008+seed)*height*.4-rr.randrange(0,15)))
            points.extend([(W,435),(0,435)]);pygame.draw.polygon(s,c,points)
        def spruce(x,y,h,c):
            pygame.draw.line(s,blend(c,'#4c5741',.4),(x,y-h),(x,y),max(1,int(h*.023)))
            for j in range(8):
                u=j/8;yy=y-h+h*(.18+u*.76);half=h*(.025+u*.13)
                pygame.draw.polygon(s,c,[(x,yy-h*.2),(x-half,yy+h*.08),(x+half,yy+h*.06)])
        for layer,c,base,maxh,spacing in [(0,'#6d9381',391,45,14),(1,'#527f6b',414,64,22),(2,'#3e6c56',425,71,31)]:
            rr=random.Random(100+layer)
            for x in range(-20,W+20,spacing):
                if 670<x<855 and layer==2:continue
                spruce(x+rr.randrange(-8,8),base-rr.randrange(0,13),rr.randrange(20,maxh),c)
        pygame.draw.polygon(s,'#5a705c',[(0,413),(190,408),(365,422),(610,417),(851,426),(1100,409),(1440,418),(1440,437),(0,437)])
        for _ in range(92):
            x=r.randrange(W);y=r.randrange(419,432)
            pygame.draw.ellipse(s,r.choice(['#8a9376','#b1ad87','#6f8167']),(x,y,r.randrange(7,34),r.randrange(3,8)))
        for y in range(SURFACE,H):
            pygame.draw.line(s,blend('#5d9a8d','#143d46',(y-SURFACE)/(H-SURFACE)),(0,y),(W,y))
        # Broken distant forest reflections, rather than a flat water fill.
        reflection=pygame.Surface((W,H),pygame.SRCALPHA)
        for _ in range(1300):
            x=r.randrange(W);yy=SURFACE+r.randrange(0,110)
            alpha=int(16*(1-(yy-SURFACE)/110))
            pygame.draw.line(reflection,(21,67,60,alpha),(x,yy),(x+r.randrange(2,23),yy),r.choice([1,1,2]))
        for x in [430,690,950,1110,1300]:
            pygame.draw.polygon(reflection,(206,223,174,10),[(x,SURFACE),(x+24,SURFACE),(x-80,H),(x-180,H)])
        s.blit(reflection,(0,0))
        # The bottom follows the physics collision profile.
        bed=[(x,int(SURFACE+min(5.75,3.5+(x/PPM)*.16)*PPM)) for x in range(0,W+1,20)]
        pygame.draw.polygon(s,'#324f45',bed+[(W,H),(0,H)])
        for _ in range(1300):
            x=r.randrange(W);bed_y=int(SURFACE+min(5.75,3.5+(x/PPM)*.16)*PPM)
            y=r.randrange(min(H-1,bed_y),H)
            c=r.choice(['#506650','#4a5e4a','#627359','#728066','#3b5446'])
            pygame.draw.ellipse(s,c,(x,y,r.randrange(2,16),r.randrange(1,5)))
        # Foreground shore -- angular granite, moss, roots, spruce and birch.
        shore=[(0,329),(65,334),(122,359),(171,394),(190,441),(220,514),(242,606),(260,726),(241,900),(0,900)]
        pygame.draw.polygon(s,'#3d5747',shore)
        for pts,c in [([(0,426),(77,412),(151,436),(185,494),(126,518),(0,499)],'#8d927d'), ([(0,500),(130,478),(209,531),(221,587),(135,616),(0,581)],'#6b7c6a'), ([(0,612),(143,598),(227,654),(228,738),(118,760),(0,714)],'#798470'), ([(0,759),(164,731),(247,805),(236,900),(0,900)],'#5b6f5c')]:
            pygame.draw.polygon(s,c,pts)
            pygame.draw.lines(s,blend(c,'#d6c8a1',.35),False,pts[:3],3)
        for _ in range(460):
            x=r.randrange(0,180);y=r.randrange(405,H)
            pygame.draw.circle(s,r.choice(['#5e7652','#66845a','#8b9364','#354d3c']),(x,y),r.randrange(1,4))
        for x,y,h in [(23,406,254),(69,391,215),(112,412,170)]:
            spruce(x,y,h,'#294d3e')
            for j in range(7):
                yy=y-h*.15-j*h*.10
                pygame.draw.line(s,'#547452',(x,yy),(x-18-j*2,yy+10),2)
        # A slanting birch and exposed roots frame the angler.
        pygame.draw.line(s,'#bfc0a0',(19,496),(90,184),10)
        pygame.draw.line(s,'#ded5b2',(15,494),(86,183),4)
        for y in range(209,480,29):
            x=90-(y-184)*71/312
            pygame.draw.line(s,'#5b6956',(x-4,y),(x+4,y+2),3)
        for x,y in [(54,290),(75,240),(28,402)]:
            pygame.draw.line(s,'#8e9f7c',(x,y),(x+41,y-52),3)
            for k in range(20):
                pygame.draw.ellipse(s,r.choice(['#8ca475','#a7b781','#6b8f64']),(x+r.randrange(13,69),y-r.randrange(35,90),r.randrange(4,11),5))
        # Fine grain prevents large computer-flat color fields.
        grain=pygame.Surface((W,H),pygame.SRCALPHA)
        for _ in range(22000):
            x=r.randrange(W);y=r.randrange(H)
            grain.set_at((x,y),(245,231,185,r.randrange(2,9)))
        s.blit(grain,(0,0))
        self.vignette=pygame.Surface((W,H),pygame.SRCALPHA)
        for i in range(45):
            pygame.draw.rect(self.vignette,(9,31,28,max(0,2-int(i/24))),(i*2,i*2,W-i*4,H-i*4),2)
        self.bed=bed
        return s

    def draw_angler(self):
        bx,by=world(self.base)
        # A weathered little fishing platform is part of the world.
        pygame.draw.polygon(self.canvas,'#5b5540',[(111,by+9),(247,by+9),(260,by+22),(112,by+25)])
        pygame.draw.polygon(self.canvas,'#ab9670',[(108,by+3),(245,by+3),(259,by+10),(109,by+12)])
        for xx in range(119,250,18):pygame.draw.line(self.canvas,'#6e684e',(xx,by+3),(xx+5,by+11),1)
        for xx in [145,230]:
            pygame.draw.line(self.canvas,'#615c44',(xx,by+19),(xx+1,by+78),7)
            pygame.draw.line(self.canvas,'#8b8361',(xx-2,by+19),(xx-1,by+74),2)
        draw_angler_character(self.canvas,V(bx,by),world(self.anchor),self.t,
                              self.pulling,self.hand_phase,self.line.gathered)
        # Worm tin and a canvas shoulder bag, rather than an equipment panel.
        pygame.draw.ellipse(self.canvas,'#879078',(120,by-7,23,9))
        pygame.draw.rect(self.canvas,'#77816b',(120,by-5,23,13),border_radius=3)
        pygame.draw.ellipse(self.canvas,'#b5b797',(120,by-8,23,7))
        pygame.draw.rect(self.canvas,'#927f52',(96,by-18,23,25),border_radius=5)
        pygame.draw.arc(self.canvas,'#796b47',(98,by-25,18,16),0,math.pi,3)

    def draw_scene(self):
        self.canvas.blit(self.background,(0,0))
        # Surface shimmers and occasional jumping insects.
        for i in range(100):
            x=280+(i*109+self.t*4)%1160;y=SURFACE+3+(i*29)%123
            a=(1-(y-SURFACE)/150)
            pygame.draw.line(self.canvas,blend('#5c9585','#b5c6a2',a*.36),(x,y),(x+5+(i%5)*7,y),1)
        for i in range(6):
            x=340+i*173+math.sin(self.t+i)*9;y=SURFACE-15+math.cos(self.t*1.2+i)*7
            pygame.draw.line(self.canvas,'#d3d8b0',(x-2,y-2),(x+2,y),1)
        for f in self.fish:
            if f is not self.catch:
                p=world(f.pos)
                self.fish_art(f,p.x,p.y,scale=1.35,alpha=int(195-f.pos.y*14))
        # Submerged weeds are rooted in the physical lake floor.
        for k,x in enumerate([335,365,390,417,825,852,890,1196,1223,1255,1350,1380]):
            floor=SURFACE+min(5.75,3.5+x/PPM*.16)*PPM
            h=42+(k*19)%78;pts=[]
            for j in range(15):
                yy=floor-h*j/14;xx=x+math.sin(self.t*.9+j*.26+k)*j*.6
                pts.append((xx,yy))
            pygame.draw.lines(self.canvas,'#3d7058',False,pts,3)
            for j in [4,7,10,13]:
                xx,yy=pts[j];side=1 if j%2 else -1
                pygame.draw.polygon(self.canvas,'#4a7b5c',[(xx,yy+3),(xx+side*15,yy-10),(xx+side*4,yy-6)])
        self.draw_angler()
        if self.phase!='landed':
            pts=[world(p) for p in self.line.nodes]
            line_color='#cbd6bc'
            if self.phase=='fight':
                line_color=blend('#d6d7b5','#e0a075',min(1,self.line.tension/1.25))
            if self.grip>0:
                tip=world(self.anchor);active=world(self.line_anchor)
                pygame.draw.aalines(self.canvas,'#aaba9c',False,[tip,tip.lerp(active,.5)+V(0,9*self.grip),active])
            pygame.draw.aalines(self.canvas,line_color,False,pts)
            h=pts[-1]
            pygame.draw.arc(self.canvas,'#c0cebc',(h.x-3,h.y-2,7,10),2.8,6.1,1)
            worm=[(h.x+math.sin(i*.62+self.t*1.7)*3,h.y+2+i*.9) for i in range(12)]
            pygame.draw.lines(self.canvas,'#704b41',False,[(x+1,y+1) for x,y in worm],4)
            pygame.draw.lines(self.canvas,'#d69c81',False,worm,3)
            if self.phase=='bite':
                pulse=1+math.sin(self.t*10)*.12
                self.hud_text('!',h.x,h.y-43*pulse,42,'#f3d184',True,center=True)
        for pos,age in self.splash:
            p=world(pos);rr=age*34
            pygame.draw.ellipse(self.canvas,'#bfcead',(p.x-rr,p.y-rr*.17,rr*2+1,rr*.34+1),1)
        # Slow drifting underwater particles and a soft edge vignette.
        for i in range(30):
            x=300+(i*67+math.sin(self.t*.23+i)*17)%1130
            y=488+(i*47+self.t*1.3)%390
            pygame.draw.circle(self.canvas,'#688d7c',(int(x),int(y)),1)
        self.canvas.blit(self.vignette,(0,0))

    def draw(self):
        self.buttons=[];self.draw_scene()
        if not self.panel and self.phase!='landed':self.draw_hud()
        if self.phase=='landed':self.draw_catch()
        if self.panel:self.draw_panel()
        size=self.screen.get_size();factor=min(size[0]/W,size[1]/H)
        scaled=pygame.transform.smoothscale(self.canvas,(int(W*factor),int(H*factor)))
        self.screen.fill('#152d2c');self.screen.blit(scaled,((size[0]-scaled.get_width())//2,(size[1]-scaled.get_height())//2))
        pygame.display.flip()

    def draw_hud(self):
        # No permanent panels. A location arrival fades into the world.
        if self.t<10:
            opacity=int(min(1,(10-self.t)/2)*235)
            self.hud_text('BIG WHITESHELL LAKE',W//2,51,23,WHITE,True,center=True,alpha=opacity)
            self.hud_text('Manitoba',W//2,79,17,WHITE,center=True,alpha=opacity)
        hints=getattr(self,'show_hints',True)
        if hints:
            self.hud_text('J  Journal     Esc  Pause     F1  Hide hints',W-362,25,16,alpha=190)
            self.hud_text('W / S  Lift stick',38,H-39,17,alpha=185)
        if self.phase=='ready' and hints:
            self.hud_text('Hold left click, then release to cast',W//2,H-58,22,center=True)
        elif self.phase=='charge':
            p=world(self.base)+V(85,-116)
            pygame.draw.arc(self.canvas,'#284c40',(p.x-19,p.y-19,38,38),0,math.tau,4)
            pygame.draw.arc(self.canvas,'#ead49b',(p.x-19,p.y-19,38,38),math.pi/2,math.pi/2+max(.01,self.charge)*math.tau,4)
            self.hud_text('Release',p.x+45,p.y-10,16)
        elif self.phase=='soak':
            if hints:self.hud_text('Hold Space or right click to gather line',W//2,H-49,19,center=True,alpha=190)
        elif self.phase=='bite':
            self.hud_text('LEFT CLICK  -  Lift!',W//2,H-62,26,'#f5d48b',True,center=True)
        elif self.phase=='fight':
            tension=max(0,min(1,self.line.tension/1.3));x=W//2-110;y=H-69
            pygame.draw.line(self.canvas,'#233e34',(x,y),(x+220,y),6)
            pygame.draw.line(self.canvas,'#dc9c69' if tension>.78 else '#ded6a0',(x,y),(x+max(1,220*tension),y),4)
            self.hud_text('Ease off' if tension>.78 else 'Hand over hand',W//2,y-27,19,center=True)
        if self.phase in ('soak','flight') and hints:
            self.hud_text(f'{max(0,self.line.hook.y):.1f} m',W-88,H-42,17,alpha=170)
        if self.toast_time>0 and self.casts>0 and self.phase not in ('bite','fight'):
            # Short-lived feedback belongs beside play, without a toast card.
            message=self.toast
            if self.font(16).size(message)[0]<1100:
                self.hud_text(message,W//2,H-91,16,center=True,alpha=int(min(1,self.toast_time)*210))

    def overlay(self):
        dim=pygame.Surface((W,H),pygame.SRCALPHA);dim.fill((9,26,25,155));self.canvas.blit(dim,(0,0));self.buttons=[]

    def draw_catch(self):
        self.overlay();f=self.catch
        self.hud_text('CAUGHT',W//2,178,18,'#d5c392',center=True)
        self.hud_text(f.data['name'],W//2,226,43,WHITE,True,center=True)
        # Fish floats above the paused world, with a gentle warm spotlight.
        halo=pygame.Surface((720,300),pygame.SRCALPHA)
        for radius in range(145,20,-4):
            pygame.draw.ellipse(halo,(228,210,153,2),(360-radius*1.8,150-radius*.65,radius*3.6,radius*1.3))
        self.canvas.blit(halo,(360,285))
        self.fish_art(f,W//2,421,scale=300/max(14,f.cm*.82),face=True)
        self.hud_text(f'{f.cm:.1f} cm    /    {f.kg:.2f} kg',W//2,554,28,center=True)
        if f.cm>=f.data['master']:
            self.hud_text('MASTER ANGLER  -  MANITOBA',W//2,611,21,'#e4bb6c',True,center=True)
        else:self.hud_text('Recorded in your journal',W//2,610,18,center=True,alpha=180)
        self.button((W//2-195,685,390,55),'[ Enter ]  Release fish',self.release_fish)

    def draw_panel(self):
        if self.panel=='journal':self.draw_journal();return
        self.overlay()
        self.hud_text('Paused',W//2,182,45,WHITE,True,center=True)
        entries=[
            ('Resume',lambda:self.open_panel(None)),
            ('Field journal',lambda:self.open_panel('journal')),
            ('Controls',lambda:self.open_panel('controls')),
            ('Sound: '+('off' if self.muted else 'on'),self.toggle_sound),
            ('Fullscreen',self.toggle_fullscreen),
            ('Save and quit',self.quit),
        ]
        self.menu_actions=[action for name,action in entries]
        for i,(name,action) in enumerate(entries):
            if i==getattr(self,'menu_index',0):
                self.hud_text('>',W//2-147,300+i*56,22,'#eac47a',True,center=True)
            self.button((W//2-170,277+i*56,340,46),name,action)
        if self.panel=='controls':
            # The paused control list is contextual game help, never a dashboard.
            self.draw_scene();self.overlay()
            self.hud_text('Controls',W//2,160,40,center=True)
            rows=[('Cast','Hold and release left click'),('Hook a nibble','Tap left click or Space'),('Gather line','Hold Space or right click'),('Lift / lower stick','W / S or mouse wheel'),('Journal','J'),('Hide hints','F1'),('Fullscreen','F11')]
            for i,(a,b) in enumerate(rows):
                self.hud_text(a,377,252+i*47,20,'#e1c48b')
                self.hud_text(b,690,252+i*47,20)
            self.button((W//2-150,663,300,50),'Back',lambda:self.open_panel('help'))
        self.hud_text('Up / Down  Select     Enter  Confirm     Esc  Resume',W//2,H-96,16,center=True,alpha=160)

    def draw_journal(self):
        self.overlay()
        r=random.Random(31)
        # A physical field notebook, opened only by J or from pause.
        pygame.draw.polygon(self.canvas,'#182923',[(209,116),(1239,103),(1255,789),(213,800)])
        pygame.draw.polygon(self.canvas,'#776b47',[(200,102),(1227,94),(1238,780),(206,790)])
        pygame.draw.polygon(self.canvas,PAPER,[(211,110),(1219,105),(1226,768),(216,777)])
        for _ in range(3500):
            x=r.randrange(221,1211);y=r.randrange(119,758)
            pygame.draw.line(self.canvas,r.choice(['#d9cca8','#e4d7b4']),(x,y),(x+r.randrange(1,4),y),1)
        pygame.draw.line(self.canvas,'#b29d75',(263,119),(269,760),2)
        for y in range(143,747,43):
            pygame.draw.circle(self.canvas,'#7c7354',(242,y),5)
            pygame.draw.arc(self.canvas,'#575b47',(218,y-7,25,15),.3,math.tau-.4,2)
        self.text('Big Whiteshell',300,132,31,INK,serif=True)
        self.text('Manitoba  /  Field notes',302,184,16,'#6d7359')
        self.buttons=[]
        self.text('[ J / Esc ] close',1028,142,14,'#6d7359')
        self.buttons.append((pygame.Rect(1000,123,198,58),lambda:self.open_panel(None),True))
        for i,k in enumerate(['perch','walleye','pike','sucker']):
            d=SPECIES[k];rec=self.record(k);y=242+i*113
            pygame.draw.line(self.canvas,'#beaf88',(298,y+103),(1184,y+103),1)
            fake=next(f for f in self.fish if f.species==k)
            self.fish_art(fake,375,y+47,120/max(14,fake.cm*.82),face=True)
            self.text(d['name'],470,y+7,23,INK,True)
            self.text(d['latin'],471,y+37,14,'#6c7257')
            self.text(d['note'],471,y+65,14,'#59664f')
            self.text(f'Best  {rec.get("best",0):g} cm',1008,y+11,17,INK)
            self.text(f'Trophy  {d["master"]:g} cm',1008,y+39,15,'#6c7257')
            if rec.get('master'):
                pygame.draw.circle(self.canvas,'#9d7c3b',(1149,y+81),16,2)
                self.text('*',1149,y+83,25,'#9d7c3b',True,center=True)
        self.text('A separate trophy record for every species in every region.',302,720,16,'#697157',serif=True)

    def toggle_fullscreen(self):
        self.fullscreen=not getattr(self,'fullscreen',False)
        self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN) if self.fullscreen else pygame.display.set_mode((1280,800),pygame.RESIZABLE)
