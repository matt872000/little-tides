# Little Tides changes

## v0.1.1

- Fixed the hook and worm bouncing off the water. Quadratic water drag now dissipates casting velocity without reversing it; the bare hooked worm settles and sinks under its weight and buoyancy.
- Made fish sprite buffers explicitly transparent, baked depth fades into pixel alpha, and gave the lake canvas an opaque RGB format to avoid black sprite rectangles on Mac.
- Added regressions for water entry across five casting powers, drag-limited sinking, bottom contact, and hand retrieval.
- Added fish transparency checks on the native window driver, including both directions, six sizes, depth fades and repeated cached draws. Packaged launch checks now also use the native window driver on Windows and both Mac architectures.

## v0.1.0

- First standalone desktop prototype: authored angler, four distinct Manitoba fish, stick-and-worm casting, hand retrieval, local journal and regional Master Angler records.
- Compiled Windows x64, Mac Apple Silicon and Mac Intel downloads.
