# Little Tides

A cute, standalone 2D fishing game with real fish, real habitats, and physical tackle behavior.

## Agreed starting point

- Start in Manitoba with native Manitoba fish.
- Start with a worm on a bare hook. No bobber or added sinker.
- The first rod is a stick with fixed line tied to its end. There is no reel; retrieve by lifting and gathering line by hand.
- Establish casting, natural sinking, slack line, and retrieval before adding the broader equipment and travel systems.
- Use gravity, buoyancy, water drag, current, flexible line, tension, and fish movement as the foundation. Calibrate the feel through playtesting.

## First playable prototype

Big Whiteshell Lake has yellow perch, walleye, northern pike, and white sucker, supported by the provincial fisheries survey. Worm attraction varies by species; pike ignore this starter bait in the game model.

The playable loop is cast, let the worm descend, respond to a nibble, lift to set the hook, hand-pull while managing fish runs, land, measure, record, and release. The line visibly transfers from the stick tip to the gathering hand, while a tied section remains attached to the stick.

The model is a first approximation: a 120 Hz position-based flexible rope with unilateral length constraints and a hook/worm tip affected by gravity, buoyancy, and quadratic fluid drag. Worm and hook properties are estimates. Water is represented as a 2D cutaway. The next iteration should tune the casting swing, line pickup, and tactile feedback with the user.

## Master Angler achievements

Every real fish species receives an achievement in **each region where that species occurs**. A pike achievement in Manitoba is separate from a pike achievement in Scotland. Fish living in multiple waters within the same region share that regional record; individual water records can be added later.

Records use a region-and-species key, such as `Manitoba|pike`, and store catch count, personal best length, and whether the trophy threshold has been reached. For the starter Manitoba fish, current published length targets are yellow perch 33 cm, walleye 71 cm, northern pike 104 cm, and sucker 46 cm. These are game achievements, not real award submissions.

Future additions should define the geographic scale of each region explicitly and verify species presence before creating a species-region achievement. Native and introduced populations should be distinguished in the data.

## Future equipment progression

- Bobbers with real flotation, buoyancy limits, and adjustable fishing depth.
- Stronger rods and lines, with rod flex, breaking strength, fish drag, and appropriate leaders.
- Species-specific baits and lures, with size, action, scent, depth, and habitat affecting strikes.
- Fly fishing gear and a separate fly-casting model.
- Spearfishing gear with its own aiming, underwater movement, and range mechanics.
- Trolling gear tied to boat motion, lure action, and running depth.
- Larger and faster boats, opening water that cannot be reached from shore.
- Larger coolers with meaningful storage and expedition capacity.
- In-game licenses for different waters, areas, regions, and countries.

## Future environments

Expand Manitoba waters first, using species and habitats confirmed for each water. The Red River is a researched candidate for channel catfish, sauger, freshwater drum, goldeye, walleye, and northern pike.

Scotland and Norway are possible later destinations. They are research candidates rather than committed content. Each new destination needs local habitat, fish identification, prey pairing, and method research before implementation. License prices and unlocks are game systems; current local fishing rules require separate verification if represented.

## Visual and technical direction

The game must look and feel like a game: an uninterrupted world that fills the window, minimal contextual feedback, and keyboard-accessible pause and journal screens. No website layout, navigation tabs, permanent sidebars, cards, dashboard, or promotional branding during play. F11 toggles fullscreen and F1 hides the control hints.

Soft boreal colors, a friendly angler, recognizable fish anatomy and markings, and a clear underwater view. The journal is presented as a physical notebook. Keep the game playable offline as a native desktop application. The current implementation uses Python with pygame-ce / SDL and is bundled as a Windows executable. Art and sound are generated locally by game code. No website, server, or web view is used.

The angler should look deliberately drawn, with a coherent seated pose and restrained pixel details. The current character wears a cap, faded flannel, jeans, and boots, with articulated hand movement. Every fish needs its own recognizable outline, fin placement, mouth anatomy, and markings based on a real identification reference. Color alone must not distinguish species. Fish length now uses a common rendering scale so large pike are appropriately longer than perch. Journal and catch close-ups normalize image size for inspection.

## Release requirement

Every version must include native Windows and Mac downloads. Build Windows x64, Mac Apple Silicon arm64, and Mac Intel x64 from the same commit. Publish the release only after all three builds and launch/render checks pass. The current Mac distribution is ad-hoc signed without Apple notarization; add Developer ID signing when credentials are available. Keep player saves outside the Mac application bundle.
