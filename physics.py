"""Fixed-step handline: inertial nodes, unilateral rope constraints, quadratic drag.

Positions are metres; +y is down, water surface y=0. This is a simplified
2D fluid/rope model, not a calibrated fishing simulator.
"""
import math
import pygame
V = pygame.Vector2
GRAVITY = 9.81
WATER_DENSITY = 1000.0
WORM_MASS = .0020
WORM_DENSITY = 1040.0
HOOK_MASS = .00028
HOOK_DENSITY = 7800.0
TIP_MASS = WORM_MASS + HOOK_MASS
TIP_VOLUME = WORM_MASS / WORM_DENSITY + HOOK_MASS / HOOK_DENSITY
TIP_AREA = .00018

def tip_acceleration(velocity, underwater, current=.025):
    if underwater:
        relative = velocity - V(current, 0)
        buoyancy = WATER_DENSITY * TIP_VOLUME * GRAVITY
        drag = relative * relative.length() * (.5 * WATER_DENSITY * .95 * TIP_AREA)
        return V(0, GRAVITY - buoyancy / TIP_MASS) - drag / TIP_MASS
    return V(.03, GRAVITY) - velocity * .035

class Handline:
    N = 26
    def __init__(self, anchor):
        self.max_length = 6.0
        self.reset(anchor)

    def reset(self, anchor):
        self.length = .65
        self.nodes = [V(anchor)+V(0, i*self.length/(self.N-1)) for i in range(self.N)]
        self.previous = [V(p) for p in self.nodes]
        self.tension = 0.0
        self.gathered = 0.0

    @property
    def hook(self):
        return self.nodes[-1]

    def launch(self, anchor, power):
        self.length = self.max_length
        # Uncoiled line is paid out from the free hand; it has no reel.
        for i in range(self.N):
            u = i/(self.N-1)
            self.nodes[i] = V(anchor)+V(.55*u,.12*u)
            velocity = V(4.2+power*4.2, -2.6-power*1.4)*u
            self.previous[i] = self.nodes[i] - velocity/120
        self.gathered = 0

    def step(self, dt, anchor, pull=False, fish_force=None):
        old_length=self.length
        if pull:
            self.length=max(.45,self.length-dt*(.52 if fish_force is None else .29))
        self.gathered += old_length-self.length
        self.nodes[0]=V(anchor)
        self.previous[0]=V(anchor)
        for i in range(1,self.N):
            p=self.nodes[i]
            vel=(p-self.previous[i])/dt
            self.previous[i]=V(p)
            wet=p.y>=0
            if i==self.N-1:
                # Substeps keep quadratic fluid drag numerically stable.
                acc=tip_acceleration(vel,wet)
                if fish_force is not None:
                    # A hooked fish adds inertia and the force of its swimming.
                    acc=V(fish_force)-vel*(1.7 if wet else .2)+V(0,.25)
            else:
                # Very thin nylon has a small excess submerged weight.
                acc=V(.025, .34 if wet else GRAVITY)-vel*(2.8 if wet else .15)
            self.nodes[i]=p+vel*dt+acc*dt*dt
        seg=self.length/(self.N-1)
        max_stretch=0.0
        # Rope resists extension but never pushes nodes apart: slack is real.
        for iteration in range(14):
            self.nodes[0]=V(anchor)
            for i in range(1,self.N):
                delta=self.nodes[i]-self.nodes[i-1]
                d=delta.length()
                if d>seg:
                    excess=d-seg
                    max_stretch=max(max_stretch,excess)
                    correction=delta*(excess/d)
                    # The hook/worm assembly is heavier than a nylon segment.
                    if i==1:
                        self.nodes[i]-=correction
                    elif i==self.N-1:
                        self.nodes[i-1]+=correction*.96
                        self.nodes[i]-=correction*.04
                    else:
                        self.nodes[i-1]+=correction*.5
                        self.nodes[i]-=correction*.5
            for i in range(1,self.N):
                self.nodes[i].x=max(.4,min(17.7,self.nodes[i].x))
                # Sloping lake bed, 4.7-5.8m. Wet hook rests, does not hover.
                floor=min(5.75,3.5+self.nodes[i].x*.16)
                if self.nodes[i].y>floor:
                    self.nodes[i].y=floor
                    self.previous[i].y=self.nodes[i].y
        distance=(self.hook-anchor).length()
        taut=max(0,min(1,(distance/self.length-.8)/.2))
        self.tension+=(max_stretch*350*taut-self.tension)*min(1,dt*8)
        return self.tension
