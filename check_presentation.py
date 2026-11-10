"""Native game view/input checks without a desktop window."""
import os
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import pygame
from main import Game,SCENE,W,H
g=Game(headless=True)
g.draw()
assert SCENE==pygame.Rect(0,0,W,H)
assert not g.buttons,'Gameplay should not have dashboard or navigation buttons'
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F1))
assert not g.show_hints
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
assert g.panel=='help'
g.draw()
assert len(g.buttons)==6
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN))
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
assert g.panel=='journal'
g.draw()
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_j))
assert g.panel is None
g.open_panel('controls');g.draw()
pygame.image.save(g.canvas,'controls-v2.png')
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
assert g.panel=='help'
g.event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
assert g.panel is None
for _ in range(1440):g.physics_step(1/120)
g.draw();pygame.image.save(g.canvas,'game-view-v2.png')
pygame.quit()
print('Full-window scene, HUD toggle, pause navigation, journal and controls: passed')
