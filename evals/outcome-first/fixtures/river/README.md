# River confluence patch (synthetic evaluation fixture)

96 × 96 cells, 4 m per cell; y increases downstream. A main stream enters the
north edge near x=49 and leaves the south edge. A smaller tributary enters the
north edge near x=9, merging from the west in the middle third. The full band
x=0..5 is a protected vehicle approach: no water there. The terrain proxy is
fixed, not a full game engine. Cells represent occupied water surface, not
depth. Preserve the output JSON contract: size, seed, water (unique [x,y]
integer pairs). The seed controls reproducible variation.

Current output has a disconnected tributary, overly uniform main width, and
an abrupt junction. Improve the actual generator, not a hand-painted image.
The main river should widen downstream, curves and banks should transition
smoothly, the junction should look like one channel system rather than
overlapping straight strokes, and seeds should give meaningful variation
without violating the approach. Keep a single connected channel network,
no isolated puddles or extra boundary outlets. Keep the main entrance within
x=40..58, tributary within x=6..18, outlet within x=35..70.
Use the supplied renderer for top-down views; inspect actual output at full
size and around the merge. The renderer is a proxy for spatial quality, not
proof of 3D terrain, flow physics, LOS, or vehicle simulation.
