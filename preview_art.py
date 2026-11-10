"""Render the exact in-game assets for visual review, without screenshots of external apps."""
import os
import sys
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import pygame
from pygame import Vector2 as V
from main import Game,Fish
from data import SPECIES
from fish_art import FIELD_MARKS
g=Game(headless=True);g.show_hints=False;g.t=12;g.draw()
out=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'art-previews'
out.mkdir(parents=True,exist_ok=True)
pygame.image.save(g.canvas,str(out/'Game art v3.png'))
# Show the small on-screen character at a legible nearest-neighbour zoom.
crop=g.canvas.subsurface(pygame.Rect(125,300,250,175)).copy()
pygame.image.save(pygame.transform.scale(crop,(750,525)),str(out/'Angler detail.png'))
g.canvas=pygame.Surface((1440,1130));g.canvas.fill('#e3dcc5')
g.text('Big Whiteshell - fish identification study',45,24,30,'#344b40',True)
g.text('Original in-game artwork. Field marks checked against fisheries identification guides.',46,68,17,'#65705a')
lengths={'perch':28,'walleye':55,'pike':90,'sucker':40}
for i,k in enumerate(['perch','walleye','pike','sucker']):
    y=280+i*228;fish=Fish(k,g.rng);fish.cm=lengths[k]
    g.fish_art(fish,380,y,scale=570/(fish.cm*.82),face=True)
    g.text(SPECIES[k]['name'],750,y-72,28,'#344b40',True)
    g.text(SPECIES[k]['latin'],752,y-31,16,'#69715d')
    g.wrap(FIELD_MARKS[k],752,y+8,625,20,'#4f614e')
    pygame.draw.line(g.canvas,'#c3bca4',(47,y+110),(1394,y+110))
pygame.image.save(g.canvas,str(out/'Fish identification study.png'))
pygame.quit()
