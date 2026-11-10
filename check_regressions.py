"""Water-entry and native-display transparency regressions (no player saves)."""
import os
os.environ['SDL_AUDIODRIVER']='dummy'
import math
import sys
from types import SimpleNamespace
from pathlib import Path
import pygame
from pygame import Vector2 as V
from physics import Handline, advance_tip_velocity, SUBMERGED_GRAVITY, WATER_DRAG
from fish_art import make_sprite, draw_fish


def check_water_entry():
    dt=1/120
    terminal=math.sqrt(SUBMERGED_GRAVITY/WATER_DRAG)
    # Even hard, oblique entries lose speed without reversing direction.
    for horizontal in (-15,0,15):
        for downward in (.1,3,8,20):
            velocity=advance_tip_velocity(V(horizontal,downward),True,dt,current=0)
            assert velocity.y>0,velocity
            assert abs(velocity.x)<=abs(horizontal),velocity
    velocity=V()
    for _ in range(1200):velocity=advance_tip_velocity(velocity,True,dt,current=0)
    assert abs(velocity.y-terminal)<.005,(velocity,terminal)
    entries=[]
    for power in (0,.25,.5,.75,1):
        anchor=V(4,-1.2);line=Handline(anchor);line.launch(anchor,power)
        entered=False;entry_count=0;minimum_downward=float('inf')
        for _ in range(120*18):
            previous=V(line.hook);line.step(dt,anchor)
            assert all(math.isfinite(p.x) and math.isfinite(p.y) for p in line.nodes)
            if previous.y<0<=line.hook.y:entry_count+=1;entered=True
            if entered:
                assert line.hook.y>=0,('Worm skipped back into air',power,line.hook)
                downward=(line.hook.y-previous.y)/dt
                minimum_downward=min(minimum_downward,downward)
                # The fixed line can lift the hook slightly as it catches the
                # end of a hard cast, but must not reflect it like a ball.
                assert downward>=-.5,('Unpulled worm bounced upward',power,downward)
        assert entry_count==1 and line.hook.y>1,(power,entry_count,line.hook)
        entries.append((power,entry_count,round(minimum_downward,4)))
    # A slack worm reaches the bed with zero rebound, and can be lifted again.
    line=Handline(V(4,-.2));line.length=6
    line.nodes=[V(4,-.2+4.33*i/(line.N-1)) for i in range(line.N)]
    line.previous=[V(p) for p in line.nodes]
    floor=3.5+line.hook.x*.16
    line.previous[-1].y-=8*dt
    for _ in range(240):
        line.step(dt,V(4,-.2))
        assert line.hook.y>=floor-.03,('Bed rebound',line.hook,floor)
    for _ in range(120*15):line.step(dt,V(4,-.2),True)
    assert line.hook.y<1 and line.length<=.46,line.hook
    print('Water entry, terminal fall, no surface skipping, bed contact and retrieval:',entries)


def check_fish_rendering(output=None):
    pygame.init()
    screen=pygame.display.set_mode((640,480),pygame.HIDDEN)
    driver=pygame.display.get_driver()
    if sys.platform=='darwin':
        assert driver=='cocoa',('Mac regression check must use the native window driver',driver)
    print('Native rendering:',sys.platform,driver,'display masks',screen.get_masks())
    # Test both opaque RGB and an alpha-bearing window-style destination.
    masks=((0xff0000,0xff00,0xff,0),(0xff,0xff00,0xff0000,0xff000000))
    for target_masks in masks:
        canvas=pygame.Surface((620,340),depth=32,masks=target_masks)
        background=pygame.Color('#438c84');canvas.fill(background)
        owner=SimpleNamespace(canvas=canvas)
        for species in ('perch','walleye','pike','sucker'):
            source=make_sprite(species)
            assert source.get_at((0,0)).a==0,(species,source.get_masks())
            for length in (14,31,80,120,300,500):
                fish=SimpleNamespace(species=species,cm=length/.82,vel=V(1,0))
                for face in (False,True):
                    # Revisit opacity values to catch fading a shared cache twice.
                    for alpha in (255,140,0,195,140,255):
                        canvas.fill(background)
                        draw_fish(owner,fish,310,170,alpha=alpha,face=face)
                        image=owner.fish_sprite_cache[(species,length,face,alpha)]
                        rect=image.get_rect(center=(310,170))
                        assert image.get_alpha()==255,(species,image.get_alpha())
                        for point in ((0,0),(image.width-1,0),(0,image.height-1),(image.width-1,image.height-1)):
                            assert image.get_at(point).a==0,(species,length,alpha,point)
                            assert canvas.get_at((rect.x+point[0],rect.y+point[1]))==background,(species,length,alpha,point)
                        if alpha==0:
                            assert pygame.image.tobytes(canvas,'RGB')==bytes(background[:3])*(620*340)
                        else:
                            assert canvas.get_at((310,170))!=background,(species,length,alpha)
    if output:
        proof=pygame.Surface((720,360),depth=32)
        for y in range(proof.height):
            pygame.draw.line(proof,(44+y//12,119-y//18,116-y//16),(0,y),(719,y))
        owner=SimpleNamespace(canvas=proof)
        for i,species in enumerate(('perch','walleye','pike','sucker')):
            fish=SimpleNamespace(species=species,cm=300/.82,vel=V(1,0))
            draw_fish(owner,fish,185,45+i*90,alpha=255,face=True)
            draw_fish(owner,fish,535,45+i*90,alpha=150,face=False)
        Path(output).parent.mkdir(parents=True,exist_ok=True)
        pygame.image.save(proof,output)
    pygame.quit()
    print('All fish: transparent corners, native compositing, both directions, six sizes and cached depth fades passed')


if __name__=='__main__':
    check_water_entry()
    check_fish_rendering(sys.argv[1] if len(sys.argv)>1 else None)
