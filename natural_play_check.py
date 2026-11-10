import os,random,json
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
from main import Game
import pygame
results=[]
g=Game(headless=True)
for seed in range(5):
    g.rng=random.Random(seed);g.spawn_fish();g.reset_line();g.t=0
    g.start_charge()
    for _ in range(84):g.physics_step(1/120)
    g.release_cast()
    bite_at=None;species=None
    for i in range(120*70):
        g.physics_step(1/120)
        if g.phase=='bite':
            bite_at=round(i/120,1);species=g.hooked.species;g.set_hook();break
    assert bite_at is not None,('No natural bite',seed,g.line.hook)
    for i in range(120*70):
        g.pulling=g.line.tension<1.12
        g.physics_step(1/120)
        if g.phase in ('landed','ready'):break
    results.append(dict(seed=seed,bite_seconds=bite_at,species=species,result=g.phase))
    assert g.phase=='landed',results
    if seed==0:
        g.draw();pygame.image.save(g.canvas,'catch-test.png')
    g.release_fish()
print(json.dumps(results,indent=2))
pygame.quit()
