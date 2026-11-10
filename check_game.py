"""Deterministic physics and gameplay checks. Run with the bundled Python."""
import os, random, math, json
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import pygame
from pygame import Vector2 as V
from physics import Handline,tip_acceleration
from data import achievement_key
from main import Game

dt=1/120
# Force balance: an unweighted hooked worm sinks, with drag-limited speed.
v=V();p=V(0,.1)
for _ in range(1200):
    v+=tip_acceleration(v,True)*dt;p+=v*dt
assert .05<v.y<.5,(p,v)
assert p.y>.6
assert tip_acceleration(V(0,1),True).y<0

# Casting uses gravity in air, then the worm descends through the water.
rope=Handline(V(4,-1.2));rope.launch(V(4,-1.2),.5)
trajectory=[]
for i in range(3600):
    rope.step(dt,V(4,-1.2))
    if i in (59,119,599,1199,2399,3599):
        trajectory.append([round((i+1)*dt,1),[round(x,3) for x in rope.hook],round(rope.tension,3)])
    assert all(math.isfinite(p.x) and math.isfinite(p.y) for p in rope.nodes)
assert rope.hook.y>.5,trajectory
assert (rope.hook-V(4,-1.2)).length()<6.5,trajectory
length=rope.length
for _ in range(3000):rope.step(dt,V(4,-1.2),True)
assert rope.length<=.46 and rope.gathered>5

# Real event-driven gameplay: charge, cast, soak, fish detection, hook, hand land.
g=Game(headless=True);g.rng=random.Random(11);g.spawn_fish()
g.mouse=(500,480)
g.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(444,427)))
assert g.phase=='charge'
for _ in range(84):g.physics_step(dt)
g.event(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=(444,427)))
assert g.phase=='flight' and g.casts==1
for other in g.fish:other.cooldown=60
for _ in range(720):g.physics_step(dt)
assert g.phase in ('soak','bite'),g.phase
g.phase='soak';g.hooked=None
f=g.fish[0];f.cm=34.0;f.kg=.6
f.pos=V(g.line.hook)+V(.1,.01);f.cooldown=0;f.interest=1
g.physics_step(dt)
assert g.phase=='bite',g.phase
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
assert g.phase=='fight' and g.pulling
fight=[]
for i in range(120*55):
    # Sensible player: rest briefly in a strong run, then gather again.
    g.pulling=g.line.tension<.9
    g.physics_step(dt)
    if i%120==0 and g.hooked:
        fight.append([i//120,round(g.line.length,2),round(g.line.tension,3),round(g.hooked.stamina,2)])
    if g.phase in ('landed','ready'):break
assert g.phase=='landed',(g.phase,fight)
assert g.record('perch')['master']
assert not g.record('walleye').get('master',False)
assert achievement_key('Manitoba','pike')!=achievement_key('Scotland','pike')
g.release_fish();assert g.save['released']>=1 and g.phase=='ready'
g.open_panel('journal');before=g.t;g.physics_step(dt);assert before==g.t
g.draw();pygame.image.save(g.canvas,'journal-test.png')
g.open_panel('roadmap');g.draw();pygame.image.save(g.canvas,'roadmap-test.png')
g.open_panel('help');g.draw();pygame.image.save(g.canvas,'help-test.png')
g.open_panel(None)
# Pike has zero worm attraction, even beside the bait.
pike=next(x for x in g.fish if x.species=='pike')
pike.pos=V(7,2);pike.interest=0
assert not pike.update(dt,g.t,V(7,2),True) and pike.interest==0
g.draw()
print(json.dumps({'status':'passed','terminal_speed_m_s':round(v.y,3),'trajectory':trajectory,'fight':fight,'master_key':achievement_key('Manitoba','perch')},indent=2))
pygame.quit()
