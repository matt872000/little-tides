"""Original side-profile fish art, based on documented diagnostic field marks.

Head faces right in the source art: anterior fins are on the right, posterior
fins on the left. No reference photographs or illustrations are copied.
"""
import math
import random
import pygame

FIELD_MARKS={
 'perch':'Seven dark bars, two dorsals, orange lower fins, short terminal mouth.',
 'walleye':'Elongated olive-gold body, separate dorsals, large jaw, white lower tail tip.',
 'pike':'Long narrow body, duckbill snout, pale oval spots, dorsal far back near tail.',
 'sucker':'Rounded cylindrical body, single soft dorsal, blunt snout, downward fleshy lips.',
}

def make_sprite(species):
    L=420;CY=116;HEIGHT=228
    s=pygame.Surface((L+10,HEIGHT),pygame.SRCALPHA)
    def point(u,v):return (round(5+u*L),round(CY+v*L))
    def polygon(target,c,pts):pygame.draw.polygon(target,c,[point(x,y) for x,y in pts])
    def stroke(c,pts,w=1,target=s):pygame.draw.lines(target,c,False,[point(x,y) for x,y in pts],w)
    styles={
        'perch':('#566341','#b4b15d','#e7d39b','#817849'),
        'walleye':('#4e5942','#9c945b','#d8d0a0','#77754d'),
        'pike':('#3b5543','#71845a','#c7c99a','#777f50'),
        'sucker':('#5e6559','#a5a993','#e2dcc2','#8b927a'),
    }
    back,side,belly,fincolor=styles[species]
    def fin(pts,root,spines=False,lower=False):
        c='#b1814a' if species=='perch' and lower else fincolor
        polygon(s,c,pts)
        stroke('#536044',pts+[pts[0]])
        # Fin rays converge on a root, rather than unrelated triangular fins.
        for i in range(1,10):
            a=pts[1];b=pts[-2];u=i/10
            edge=(a[0]*(1-u)+b[0]*u,a[1]*(1-u)+b[1]*u)
            pygame.draw.line(s,'#646c46' if not lower else '#946d40',point(*root),point(*edge),1)
        if spines:
            start=pts[1];end=pts[-2]
            for i in range(11):
                u=i/10;x=start[0]*(1-u)+end[0]*u;y=start[1]*(1-u)+end[1]*u
                stroke('#4d593c',[(root[0]+(x-root[0])*.35,root[1]),(x,y-.009)],1)
    # Forked caudal fin. Lower lobe marker belongs only to walleye.
    tail=[(.155,-.021),(.055,-.099),(.018,-.104),(.055,-.024),(.069,0),(.048,.043),(.018,.105),(.058,.095),(.155,.022)]
    if species=='pike':tail=[(u,v*.76) for u,v in tail]
    fin(tail,(.15,0))
    if species=='walleye':
        polygon(s,'#e9e4c7',[(.018,.105),(.058,.095),(.078,.072),(.043,.073)])
    if species in ('perch','walleye'):
        # Anterior spiny dorsal (right) and posterior soft dorsal (left).
        h=.235 if species=='perch' else .181
        fin([(.49,-.05),(.535,-h),(.60,-h-.018),(.68,-h+.01),(.755,-.05)],(.64,-.06),True)
        fin([(.267,-.05),(.30,-.145),(.37,-.154),(.445,-.133),(.47,-.085)],(.40,-.065))
        fin([(.28,.045),(.292,.128),(.36,.143),(.41,.082)],(.38,.055),lower=True)
        fin([(.52,.07),(.51,.173),(.57,.148),(.61,.08)],(.57,.07),lower=True)
        if species=='perch':
            polygon(s,'#444c34',[(.50,-.105),(.532,-.185),(.557,-.174),(.553,-.114)])
    elif species=='pike':
        fin([(.19,-.032),(.205,-.108),(.25,-.123),(.32,-.104),(.35,-.037)],(.29,-.035))
        fin([(.19,.031),(.205,.094),(.26,.108),(.33,.086),(.35,.032)],(.29,.035))
        fin([(.49,.05),(.49,.13),(.55,.106),(.59,.052)],(.55,.05))
    else:
        # Suckers have one entirely soft-rayed dorsal, not a perch crest.
        fin([(.39,-.07),(.43,-.17),(.47,-.19),(.53,-.18),(.61,-.13),(.64,-.075)],(.56,-.07))
        fin([(.26,.042),(.27,.111),(.32,.127),(.38,.082)],(.34,.05))
        fin([(.52,.073),(.51,.148),(.55,.156),(.61,.092)],(.57,.075))
    outlines={
      'perch':[(.14,-.023),(.23,-.052),(.35,-.111),(.51,-.139),(.67,-.131),(.80,-.091),(.91,-.043),(.985,-.008),(.967,.024),(.917,.054),(.80,.09),(.65,.119),(.48,.124),(.33,.094),(.23,.048),(.14,.024)],
      'walleye':[(.14,-.02),(.28,-.05),(.46,-.086),(.65,-.09),(.78,-.074),(.87,-.043),(.99,-.004),(.993,.017),(.933,.043),(.82,.065),(.67,.084),(.49,.087),(.32,.065),(.22,.033),(.14,.02)],
      'pike':[(.14,-.017),(.26,-.043),(.48,-.058),(.68,-.058),(.78,-.046),(.87,-.021),(.99,-.015),(1,.002),(.99,.021),(.87,.031),(.77,.047),(.62,.061),(.43,.055),(.26,.039),(.14,.018)],
      'sucker':[(.14,-.022),(.26,-.057),(.43,-.09),(.62,-.104),(.78,-.089),(.89,-.061),(.956,-.033),(.985,-.003),(.978,.033),(.949,.054),(.91,.064),(.82,.082),(.65,.102),(.45,.101),(.28,.062),(.14,.023)],
    }
    outline=outlines[species]
    mask=pygame.Surface(s.get_size(),pygame.SRCALPHA);polygon(mask,'white',outline)
    body=pygame.Surface(s.get_size(),pygame.SRCALPHA)
    def lerp_color(a,b,t):
        a=pygame.Color(a);b=pygame.Color(b)
        return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
    top=CY-L*.15;bottom=CY+L*.13
    for yy in range(HEIGHT):
        u=max(0,min(1,(yy-top)/(bottom-top)))
        c=lerp_color(back,side,u/.57) if u<.57 else lerp_color(side,belly,(u-.57)/.43)
        pygame.draw.line(body,c,(0,yy),(L+10,yy))
    detail=pygame.Surface(s.get_size(),pygame.SRCALPHA)
    if species=='perch':
        # Seven tapered bars, with the back continuing into each bar.
        for i in range(7):
            u=.255+i*.088+math.sin(i*2.3)*.006
            width=.019+math.cos(i*2)*.004
            polygon(detail,(53,67,39,190),[(u-width,-.16),(u+width,-.16),(u+.014,.065),(u+.001,.095),(u-.009,.045)])
    elif species=='pike':
        rng=random.Random(92)
        for row in range(3):
            for col in range(13):
                x=.22+col*.042+(row%2)*.016+rng.uniform(-.006,.006)
                y=-.033+row*.032+rng.uniform(-.005,.005)
                pygame.draw.ellipse(detail,(199,203,151,205),(*point(x,y),rng.randrange(4,8),rng.randrange(2,4)))
    elif species=='walleye':
        for row in range(5):
            for col in range(20):
                x=.25+col*.026+(row%2)*.009;y=-.055+row*.022
                pygame.draw.line(detail,(205,187,115,70),point(x,y),point(x+.006,y-.003),1)
    else:
        for row in range(7):
            for col in range(21):
                x=.22+col*.029+(row%2)*.014;y=-.07+row*.023
                xx,yy=point(x,y)
                pygame.draw.arc(detail,(70,86,69,100),(xx,yy,9,7),-.7,1.1,1)
    body.blit(detail,(0,0));body.blit(mask,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(body,(0,0));stroke(back,outline+[outline[0]],1)
    # Lateral line and gill cover remain subtle and follow the body.
    stroke('#7a835f' if species!='sucker' else '#7f8e79',[(.21,.005),(.43,.013),(.65,.015),(.79,.008)],1)
    gx=.79 if species!='pike' else .755
    stroke('#647050',[(gx,-.065),(gx-.014,-.025),(gx-.008,.022),(gx+.015,.055)],2)
    # Pectoral is just behind the gill, pelvic farther back on the belly.
    fin([(.77,.023),(.73,.104),(.66,.12),(.69,.047)],(.755,.025),lower=species=='perch')
    if species=='sucker':
        # Small inferior mouth under an overhanging blunt snout, with thick lips.
        pygame.draw.ellipse(s,'#baa98b',(*point(.944,.045),12,8))
        pygame.draw.arc(s,'#686e58',(*point(.947,.049),9,5),0,math.tau,1)
        eye=(.91,-.027);radius=3
    elif species=='pike':
        stroke('#334d3e',[(.824,.012),(.93,.008),(.992,.009)],2)
        eye=(.83,-.025);radius=3.7
    elif species=='walleye':
        # Jaw extends back under the eye, with tiny canine points at inspection scale.
        stroke('#49543d',[(.84,.032),(.925,.017),(.988,.008)],2)
        for x in [.905,.94,.962]:polygon(s,'#d7d4b2',[(x,.019),(x+.005,.009),(x+.009,.018)])
        eye=(.892,-.027);radius=5.4
    else:
        stroke('#59613d',[(.934,.019),(.98,.006)],1)
        eye=(.883,-.031);radius=4
    ex,ey=point(*eye)
    pygame.draw.circle(s,'#d5c582',(ex,ey),radius+1)
    pygame.draw.circle(s,'#1d302b',(ex,ey),radius*.62)
    pygame.draw.circle(s,'#efe8c9',(ex+1,ey-1),1)
    return s

def draw_fish(owner,fish,x,y,scale=1,alpha=255,face=None):
    if not hasattr(owner,'fish_sprite_cache'):owner.fish_sprite_cache={}
    species=fish.species
    # Shared physical scale makes a 90 cm pike visibly longer than a 25 cm perch.
    length=max(14,fish.cm*.82)*scale
    if face is None:face=fish.vel.x>=0
    key=(species,max(14,round(length)),bool(face))
    cache=owner.fish_sprite_cache
    if key not in cache:
        canonical_key=('canonical',species)
        if canonical_key not in cache:cache[canonical_key]=make_sprite(species)
        source=cache[canonical_key]
        image=pygame.transform.smoothscale(source,(key[1],max(7,round(key[1]*source.get_height()/source.get_width()))))
        if not face:image=pygame.transform.flip(image,True,False)
        cache[key]=image
    image=cache[key];image.set_alpha(alpha)
    owner.canvas.blit(image,image.get_rect(center=(x,y)))
