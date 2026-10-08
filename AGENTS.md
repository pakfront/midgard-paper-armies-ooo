# Project instructions

## Unit types

Use these four unit types when designing, naming, and adding units:

| Type | Contents of one base | Base size |
|---|---|---|
| Heroes | A single figure, on foot or mounted | 20 mm × 20 mm |
| Monstrosities | One or two large monsters, or a single war machine or similar model | 40 mm × 20 mm |
| Foot | Multiple foot figures, following the existing infantry units | 40 mm × 20 mm |
| Cavalry | Multiple mounted figures, following the existing cavalry units | 40 mm × 20 mm |

Cavalry and Monstrosities may optionally use 40 × 30 mm or 40 × 40 mm bases via setup-wide depth settings; 40 × 20 mm remains the default. Foot and Heroes retain their standard bases. Monstrosities keep their upright counts and fixed panel heights at all depths.

Monstrosities is a generic category, not the name of a specific unit. Use descriptive unit and artwork names such as Giant, Trolls, or the particular war machine. Giant, the two-Troll unit, and the two-Ogre unit belong to Monstrosities.

Base dimensions and figure counts describe the assembled model. Upright layout follows the subject: heroes use a single upright; the existing Giant, Trolls, and Ogres units use one upright with fixed panel heights (35 mm for Giant; 23 mm for Trolls and Ogres). Monstrosities may be taller than ordinary foot figures. Preserve monster artwork proportions and keep complete figures and weapons within the print panel.

## Light troops and skirmishers

Light troops and skirmishers are roles within Foot or Cavalry, not additional unit types. Keep their normal base dimensions.

- Light Foot troops use **7–8 figures as the baseline density**. Give them varied poses, uneven head heights, and individual differences in clothing and equipment rather than a regimented identical rank. Light equipment alone is not a reason to reduce figure count.
- Skirmish Foot units use **fewer figures, normally 4–6**, with visible gaps, irregular spacing, and strongly varied poses. Mix standing, crouching, kneeling, aiming, reloading, or moving poses as appropriate to the weapons. Rangers of Gondor are the six-figure example.
- When a unit is both light and a skirmisher, follow the skirmisher density. These Foot counts describe the figures in the artwork, not the configurable number of upright ranks. Cavalry continues to use individual side profiles and the existing configurable rider count.
- For both roles, use the Orc clean-print style: bold contours, broad flat colors, only two or three large shading tones, minimal faces, and no fine texture, hatching, scratches, hair strands, or tiny fittings. Preserve complete figures and weapons within the print panel. Follow `output/imagegen/clean-style-tests-notes.md` and `output/imagegen/foot-print-simplification-notes.md` for prompt guidance.

## Existing implementation

The catalog currently uses `kind: 'Infantry'` for Foot, `kind: 'Mounted'` for Cavalry and mounted Heroes, `hero: true` for Heroes, and `kind: 'Monster'` for Monstrosities. These internal fields control rendering and folding; the unit type definitions above also cover future foot heroes and war machines.

Keep catalog IDs stable when renaming units or artwork so saved setups retain quantities and names. The Giant retains the legacy ID `orc-troll`; Trolls retains `orc-monstrosities`. Use `artwork/middle-earth-third-age/Orcs/orc-trolls.png` for the two-Troll artwork.

## Validation

For changes to fold geometry or rendering, run the relevant browser/PDF tests in `tests/test_workshop.py`. Artwork and filename changes should be checked for successful loading and PDF export. Keep README descriptions and recorded artwork paths current.
