"""Original, deliberately placed pixel shapes for the seated shore angler."""
import math
import pygame
from pygame import Vector2 as V

def draw_angler_character(canvas,base,tip,t,pulling,hand_phase,gathered):
    # Art is authored on a 64 x 80 grid, then enlarged with nearest-neighbour
    # sampling. There is one coherent side-view anatomy, not stacked ellipses.
    s=pygame.Surface((64,80),pygame.SRCALPHA)
    outline='#2c4039';pants='#47616a';denim='#58747b';skin='#d2ac80'
    rust='#9b6249';light='#b47a55';dark='#754d3e';boot='#474735'
    def poly(c,p):pygame.draw.polygon(s,c,p)
    def rect(c,r):pygame.draw.rect(s,c,r)
    def line(c,a,b,w=1):pygame.draw.line(s,c,a,b,w)
    # Far leg and boot, then the near thigh, hanging shin and boot.
    poly(outline,[(21,52),(34,52),(37,58),(36,70),(42,72),(43,75),(32,75),(30,70),(29,59),(20,58)])
    poly(pants,[(23,53),(33,54),(34,59),(33,70),(31,70),(30,58),(22,57)])
    poly(boot,[(31,69),(36,69),(37,71),(42,72),(42,74),(32,74)])
    line('#6e6b4c',(34,71),(40,72))
    poly(outline,[(20,50),(29,51),(40,53),(43,57),(43,69),(48,71),(51,72),(51,76),(40,76),(38,72),(37,60),(25,59),(20,57)])
    poly(pants,[(22,52),(29,53),(39,55),(41,58),(41,70),(39,70),(38,59),(26,57),(22,56)])
    line(denim,(27,54),(39,56),2);line(denim,(40,59),(40,68))
    poly(boot,[(39,69),(43,69),(44,71),(50,73),(50,75),(41,75),(39,73)])
    line('#76714e',(42,72),(48,73));line('#252f29',(41,75),(51,75))
    # Faded flannel has an actual shoulder, forward lean, waist and hem.
    poly(outline,[(21,30),(26,30),(30,34),(30,43),(32,48),(30,53),(22,56),(17,54),(16,49),(17,39),(18,34)])
    poly(rust,[(21,32),(26,32),(28,35),(28,44),(30,49),(29,52),(22,54),(18,52),(18,44),(19,36)])
    poly(light,[(21,34),(24,34),(23,45),(24,52),(20,52),(19,47),(20,38)])
    line(dark,(19,39),(28,39));line(dark,(18,46),(29,46));line(dark,(24,34),(25,52))
    line('#c49165',(20,40),(23,40));line('#c49165',(19,47),(23,47))
    rect('#b88c61',(27,38,1,2));rect('#c5a578',(28,45,1,1));line('#5b4635',(20,54),(29,52))
    # Neck, ear, profile and cap. The eye is one pixel, the nose two.
    poly('#a67f5c',[(24,27),(29,27),(29,32),(26,34),(23,32)])
    poly('#5b4c38',[(22,16),(30,16),(32,19),(31,26),(28,29),(23,27),(21,23)])
    poly(skin,[(25,17),(31,18),(32,20),(32,22),(34,23),(34,24),(32,24),(32,27),(29,29),(26,28),(24,25),(23,22)])
    poly('#e0ba8b',[(27,18),(31,19),(31,22),(33,23),(31,24),(31,26),(28,27),(26,25),(25,21)])
    rect('#b58b64',(24,22,2,3));rect('#e2bb8c',(24,22,1,2))
    rect(outline,(30,21,1,1));line('#9a7957',(30,26),(32,26))
    poly('#8c7456',[(27,27),(31,27),(29,29),(26,28)])
    poly(outline,[(19,15),(20,11),(23,9),(30,9),(33,12),(33,15),(38,16),(38,18),(20,18),(18,17)])
    poly('#65764b',[(21,14),(22,11),(25,10),(29,10),(31,12),(32,15)])
    line('#8c9460',(23,11),(29,11));rect('#4b5f40',(20,15,13,2))
    poly('#718153',[(29,16),(37,16),(36,17),(28,17)])
    # Far sleeve and free forearm. Movement is restrained and jointed.
    poly(dark,[(20,34),(23,35),(26,44),(24,47),(21,45),(18,38)])
    hand_x=28;hand_y=34
    if pulling:
        hand_x+=int(math.sin(hand_phase)*2)
        hand_y+=int(math.cos(hand_phase)*2)
    line('#aa835e',(24,45),(hand_x,hand_y),3)
    rect(skin,(hand_x-1,hand_y-1,3,3))
    # Near sleeve and bent elbow, then bare forearm to the stick grip.
    poly(outline,[(25,33),(28,34),(31,40),(32,43),(30,46),(27,45),(24,40)])
    poly(light,[(25,34),(27,35),(29,40),(30,43),(28,44),(25,39)])
    line('#c0966a',(28,43),(33,36),3);line(skin,(29,42),(34,35),2)
    rect('#d9b58a',(33,34,3,3));line('#7b654a',(34,36),(36,36))
    # A blink is two low-key frames in an otherwise quiet idle.
    if t%7.3>7.17:rect('#b18b63',(30,21,1,1))
    origin=V(round(base.x)-50,round(base.y)-114)
    canvas.blit(pygame.transform.scale(s,(128,160)),origin)
    grip=origin+V(69,71)
    pygame.draw.line(canvas,'#4e422e',grip,tip,5)
    pygame.draw.line(canvas,'#a89060',grip+V(0,-1),tip+V(0,-1),2)
    for u in [.28,.49,.72]:
        p=grip.lerp(tip,u);pygame.draw.line(canvas,'#6f5c3d',p-V(1,2),p+V(1,2),2)
    # Fingers lie over the wood; gathered line hangs from the free hand.
    pygame.draw.rect(canvas,'#d6b184',(grip.x-1,grip.y-2,5,3))
    free_hand=origin+V(hand_x*2,hand_y*2)
    for i in range(min(5,int(gathered))):
        pygame.draw.ellipse(canvas,'#b7bda0',(free_hand.x-3-i,free_hand.y+2,10+i*2,18+i*2),1)
