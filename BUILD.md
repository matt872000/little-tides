# Build and run Little Tides

Requires Python 3.12 on the operating system and architecture being packaged.
The bundled game itself does not require Python to be installed.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

Run deterministic checks:

```powershell
.\.venv\Scripts\python check_game.py
.\.venv\Scripts\python natural_play_check.py
.\.venv\Scripts\python check_presentation.py
.\.venv\Scripts\python check_regressions.py
```

Build the native application folder:

```powershell
.\.venv\Scripts\python -m PyInstaller --noconfirm --windowed --onedir --exclude-module numpy --exclude-module pygame.examples --exclude-module pygame.tests --name "Little Tides" main.py
```

Distribute the complete `dist/Little Tides` directory, including `_internal`,
the attached documentation, and dependency license notices. Include source
or a source link when redistributing LGPL dependencies; pygame-ce 2.5.8 is
unmodified and available at https://github.com/pygame-community/pygame-ce.

An offscreen executable smoke test is available:

```powershell
& '.\dist\Little Tides\Little Tides.exe' --smoke-test '.\preview.png'
```

`main.py` holds the desktop application, input, fishing state machine,
fish drawing, and save handling. `presentation.py` holds the full-window game
world, contextual HUD, pause menu, and notebook. `physics.py` holds the fixed-step rope and hook/worm force
model. `data.py` holds species and future regional data. Only Big Whiteshell
Lake's four native starter species are active in this prototype.

`angler_art.py` is the authored pixel-grid character. `fish_art.py` contains
the four separate fish profiles, fins, mouth features, and markings. To render
the game's character and fish identification study without opening a window,
run `python preview_art.py path/to/art-previews`.

Game saves are portable JSON beside the executable (or beside `main.py` when
running the source) on Windows. Packaged Mac apps use
`~/Library/Application Support/Little Tides/`. The checks run without writing player saves.

## Versioned native packages

Run `python build_release.py --version v0.1.0` on the target operating system.
The script builds a native app, performs an offscreen launch/render check,
and writes a ZIP and checksum manifest under `release/`. Mac ZIPs use `ditto`
to preserve application bundle symlinks, resources, and executable permissions.
The application is ad-hoc signed by PyInstaller, not Developer ID signed or
notarized. An Intel and an Apple Silicon build are provided separately.

The GitHub Actions `Desktop releases` workflow runs this on Windows x64,
macOS arm64, and macOS x64. It publishes only after all builds and checks pass.
The water-entry and transparency regressions use a hidden native window (Cocoa
on Mac), and the packaged smoke test uses `--native-display`. This catches pixel
format differences that the dummy video driver alone cannot exercise.
Use its manual version input, or push a new `v*` tag. The first GitHub release
is `v0.1.0`; local art iterations v1/v2/v3 precede that semantic version.
