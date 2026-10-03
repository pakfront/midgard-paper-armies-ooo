# Middle-earth artwork TODOs

## Required look and print style

Apply these requirements to every new asset and repeat them in its generation prompt. Follow `AGENTS.md` for unit types and base geometry, and `output/imagegen/clean-style-tests-notes.md` and `output/imagegen/foot-print-simplification-notes.md` for the approved simplified style.

- Design for the final miniature print size, not for a detailed illustration viewed at full resolution. Foot ranks print across 40 mm, with bodies roughly 10 mm high; mounted profiles fit inside a 20 mm-wide panel. Heroes use one figure on a 20 × 20 mm base. Monstrosities use a 40 × 20 mm base and a suitable fixed panel height.
- Use bold, crisp dark contours, broad flat color masses, and only two or three large shading tones per material. Keep adjacent materials distinct and dark armor readable. Smooth antialiased edges must remain clean when reduced; avoid jagged pixel-art edges.
- Omit grain, mottling, stipple, crosshatching, scratches, tiny rivets or buckles, individual chainmail rings, hair/fur strands, embroidery and ornate trim. Depict mail as a smooth grey mass and hair/fur as a few large shapes. Keep faces minimal. Do not add these details for realism.
- Use robust, recognizable weapons and thick, simple heraldic symbols. Avoid fragile strokes, densely decorated shields and tangled bow mechanisms. Faction identity should come from silhouette, equipment, broad palette and clear emblems.
- Foot units show exactly eight complete figures in a compact frontal rank. Cavalry artwork shows one rider and mount in strict side profile; the workshop repeats and mirrors that profile. Foot Heroes show one complete figure, and mounted Heroes one complete rider and mount. Do not bake multiple ranks or reverse faces into an image.
- Keep complete figures, boots, paws/hooves, tails, banners and weapon tips inside the image with transparent padding on every edge. Preserve proportions for mounted figures, Heroes and Monstrosities. Use a genuinely transparent RGBA background; no scenery, ground, cast shadow, base, captions, borders or watermark.
- Match the simplified `Rohan/rohan-foot-spearmen.png`, `Isengard/isengard-uruk-hai-infantry.png` and `Orcs/orc-warg-profile.png` assets. Older textured artwork is equipment reference only, never the rendering target.
- Before checking off an item, inspect figure counts and complete silhouettes, confirm PNG transparency, view the artwork in its intended panel, and verify browser loading and PDF export. Save final assets under `artwork/middle-earth-third-age/<Faction>/`, register the unit with a new stable catalog ID, and record full prompts and final paths in `output/imagegen/`.

## Choices for the remaining alternatives

This pass uses a Mordor catapult, a Gondor foot captain, Haradrim spearmen/archers/cavalry, Aragorn on foot, and a Cave Troll. These satisfy the corresponding alternative entries below; additional variants may be added later.

## Army additions

- [x] Add Isengard Uruk-hai infantry: eight armored warriors in a frontal rank.
- [x] Add Isengard Uruk-hai crossbowmen: eight crossbow troops in a frontal rank.
- [x] Add a mounted Isengard Warg rider unit.
- [x] Add Rohan foot warriors with spears.
- [x] Add Rohan foot warriors with bows.
- [x] Add a Rohan foot captain as a single Hero standee.
- [x] Add a Mordor Orc infantry unit with shields and spears, visually distinct from the existing Orcs faction.
- [x] Add a Morannon Orc unit with heavier armor.
- [x] Add a Mordor banner bearer Hero.
- [x] Add a Mordor war machine Monstrosity.
- [x] Add Gondor foot Heroes: a captain, banner bearer, and/or ranger.
- [x] Add Harad or Easterlings: spearmen, archers, and cavalry.
- [x] Add named Hero standees: Aragorn on foot, Théoden mounted, and/or Éomer mounted.
- [x] Add a large monster Monstrosity such as a Mumakil, Ent, or Cave Troll; choose panel dimensions that keep the full figure and weapons in frame.

## Current work

- [x] Create Isengard Uruk-hai infantry and crossbow artwork and add both units to the catalog.
- [x] Create Rohan foot spearmen and archer artwork and add both units to the catalog.

- [x] Complete the remaining additions using the choices above: twelve new assets registered in the catalog.
- [x] Inspect miniature panel previews, verify transparent PNGs, and pass browser/PDF checks for the expansion, fold geometry, reverse alignment and page dimensions.

Full prompts and final asset paths: `output/imagegen/middle-earth-todo-expansion-notes.md`. Review sheet: `output/imagegen/middle-earth-expansion-print.pdf` (print at 100% / actual size).
