"""Researched species/habitat data. Balance values are game abstractions."""
SPECIES = {
 'perch': dict(name='Yellow perch', latin='Perca flavescens', color='#a2a85b', belly='#e0cf89', shape='perch', size=(16,38), kg=0.45, depth=(1,5), master=33, baits={'worm':1,'minnow':.8,'jig':.9,'spinner':.65}, note='Small schools near weed edges. Worms and small jigs work well.'),
 'walleye': dict(name='Walleye', latin='Sander vitreus', color='#7f8551', belly='#d9cf9a', shape='walleye', size=(28,84), kg=1.6, depth=(2,8), master=71, baits={'worm':.8,'minnow':1,'jig':1,'spoon':.4,'plug':.85}, note='Light-sensitive predator. Work a jig or worm near the bottom.'),
 'pike': dict(name='Northern pike', latin='Esox lucius', color='#647a56', belly='#c9cc9a', shape='pike', size=(35,118), kg=3.0, depth=(1,6), master=104, baits={'minnow':.85,'spoon':1,'spinner':.9,'streamer':.9,'plug':1}, note='Ambushes prey around weeds. A wire leader resists sharp teeth.'),
 'sucker': dict(name='White sucker', latin='Catostomus commersonii', color='#85866c', belly='#d9cdb2', shape='sucker', size=(22,57), kg=.85, depth=(3,8), master=46, baits={'worm':1}, note='Feeds on bottom invertebrates. Let a worm reach the lake bed.'),
 'catfish': dict(name='Channel catfish', latin='Ictalurus punctatus', color='#677b7d', belly='#c4c9b9', shape='catfish', size=(30,106), kg=4, depth=(3,8), master=88.9, baits={'worm':.65,'cutbait':1,'minnow':.7}, note='Scent-sensitive bottom feeder. Cut bait shines in river current.'),
 'sauger': dict(name='Sauger', latin='Sander canadensis', color='#9a8a60', belly='#e0d2ac', shape='walleye', size=(20,56), kg=.7, depth=(3,8), master=46, baits={'worm':.8,'minnow':1,'jig':1,'plug':.7}, note='Often in turbid rivers. Small minnows or jigs near the bottom.'),
 'drum': dict(name='Freshwater drum', latin='Aplodinotus grunniens', color='#96a39c', belly='#d5dace', shape='deep', size=(25,75), kg=2, depth=(3,8), master=61, baits={'worm':1,'cutbait':.5,'jig':.4}, note='Deep-bodied bottom feeder that eats invertebrates and small fish.'),
 'goldeye': dict(name='Goldeye', latin='Hiodon alosoides', color='#a6b7ac', belly='#e3dfc5', shape='silver', size=(18,46), kg=.5, depth=(.5,3), master=35.5, baits={'worm':1,'dryfly':.95,'spinner':.5}, note='Looks upward for drifting insects. Try a shallow worm or dry fly.'),
 'brown': dict(name='Brown trout', latin='Salmo trutta', color='#a89062', belly='#e6cf96', shape='trout', size=(22,66), kg=1.1, depth=(.4,5), master=51, baits={'worm':.65,'dryfly':1,'streamer':1,'spinner':.8,'spoon':.5}, note='Insects, larvae and small fish. Match a dry fly to surface feeding.'),
 'eperch': dict(name='European perch', latin='Perca fluviatilis', color='#8e9e5e', belly='#dec888', shape='perch', size=(15,48), kg=.65, depth=(1,6), master=38, baits={'worm':1,'minnow':.9,'jig':1,'spinner':.95}, note='Striped predator around weed beds; small spinners and worms.'),
 'cod': dict(name='Atlantic cod', latin='Gadus morhua', color='#9c9572', belly='#ded9bd', shape='cod', size=(35,110), kg=4, depth=(8,24), master=90, baits={'cutbait':1,'jig':1,'minnow':.6}, note='Bottom-oriented marine predator. Heavy jigs or cut fish bait.'),
 'pollack': dict(name='Pollack', latin='Pollachius pollachius', color='#798b7b', belly='#d2d3b5', shape='cod', size=(28,95), kg=2.5, depth=(3,16), master=75, baits={'jig':1,'spoon':.85,'minnow':.8,'plug':.9,'streamer':.8}, note='Hunts small fish along kelp and rocky ledges.'),
 'mackerel': dict(name='Atlantic mackerel', latin='Scomber scombrus', color='#529395', belly='#d5e0d7', shape='mackerel', size=(22,49), kg=.65, depth=(1,10), master=42, baits={'spoon':1,'jig':.85,'minnow':.7,'cutbait':.8,'plug':.7}, note='Fast pelagic schooling fish. Small shiny lures imitate baitfish.'),
}
BAITS = {'worm':'Worm on a hook', 'minnow':'Preserved minnow', 'jig':'Soft-plastic jig', 'spoon':'Silver spoon', 'spinner':'Inline spinner', 'cutbait':'Cut fish bait', 'dryfly':'Mayfly imitation', 'streamer':'Baitfish streamer', 'plug':'Diving plug'}
LOCATIONS = [
 dict(id='whiteshell',region='Manitoba',country='Canada',name='Big Whiteshell Lake',tag='Boreal lake',desc='Granite shores, spruce trees, and your very first cast.',fish=['perch','walleye','pike','sucker'],cost=0,theme='boreal',depth=8,current=.05,wind=1.4,temp=18),
 dict(id='redriver',region='Manitoba',country='Canada',name='Red River',tag='Prairie river',desc='Slow brown water. Big cats and bottom-feeding specialists.',fish=['catfish','sauger','drum','goldeye','walleye','pike'],cost=90,theme='river',depth=8,current=.3,wind=2.1,temp=22),
 dict(id='scotland',region='Scotland',country='United Kingdom',name='Kilbirnie Loch',tag='Scottish loch',desc='Green hills and wild trout. Bring a fly rod for surface feeders.',fish=['brown','eperch','pike'],cost=300,theme='loch',depth=8,current=.03,wind=3.2,temp=14),
 dict(id='norway',region='Southern Norway',country='Norway',name='Sorlandet Coast',tag='Rocky saltwater coast',desc='Kelp, skerries and cold saltwater. Find cod down deep.',fish=['cod','pollack','mackerel'],cost=480,theme='coast',depth=24,current=.16,wind=4.1,temp=12),
]
SOURCES = [
 ('Manitoba habitat survey','https://www.manitoba.ca/nrnd/fish-wildlife/pubs/lifa/big_whiteshell.pdf'),
 ('Red River fisheries','https://content.gov.mb.ca/mit/wm/design_fishway.pdf'),
 ('Manitoba Master Angler lengths','https://anglers.travelmanitoba.com/master-angler-program/rules/'),
 ('Kilbirnie Angling Club species','https://klmg.org.uk/pages/kilbirnie-angling-club'),
 ('Brown trout diet','https://forthriverstrust.org/rivers-wildlife/learn/wildlife/fish/brown-trout/'),
 ('Norway coastal species','https://en.visitsorlandet.com/things-to-do/nature-experiences/fishing-in-southern-norway/'),
 ('Bluegill and bait research (future Florida region)','https://myfwc.com/wildlifehabitats/profiles/freshwater/bluegill/'),
]

def achievement_key(region, species):
    return region + '|' + species

def achievement_pairs():
    return sorted({(loc['region'], f) for loc in LOCATIONS for f in loc['fish']})
