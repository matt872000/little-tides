# Little Tides project instructions

- Build a standalone desktop fishing game. Keep gameplay in a full-window scene with minimal contextual feedback. Do not reintroduce website navigation, dashboard cards, or permanent sidebars.
- Preserve the agreed starter kit: a stick with fixed line, a bare hook, and a worm; casting and hand retrieval come before equipment expansion.
- Start in Manitoba with fish verified for the selected real water. Give every species a distinct anatomical outline, fin layout, mouth, and identifying markings. Cite research in docs/SOURCES.md.
- Preserve the authored angler style and notebook journal. Keep the equipment, travel, and regional achievement plans in docs/GAME_DESIGN.md.
- Master Angler records are separate for each species and each region where it occurs.
- Every delivered version uploaded to GitHub must have compiled, downloadable Windows x64, Mac Apple Silicon, and Mac Intel packages on its GitHub Release. Do not call a version released when only source or a workflow exists.
- Use a new semantic version and the Desktop releases workflow. Wait for all native builds, tests, packaged launch/render checks, and release upload to succeed. Report the release link and any material limitation.
- Keep Mac saves outside the application bundle. Mac builds currently have ad-hoc signatures without Developer ID signing or notarization; never describe them as notarized.
- Run the existing relevant checks for changes. Keep player saves, credentials, virtual environments, build directories, and runtime binaries out of source commits.
