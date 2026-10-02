# Project instructions

## Unit types

Use these four unit types when designing, naming, and adding units:

| Type | Contents of one base | Base size |
|---|---|---|
| Heroes | A single figure, on foot or mounted | 20 mm × 20 mm |
| Monstrosities | One or two large monsters, or a single war machine or similar model | 40 mm × 20 mm |
| Foot | Multiple foot figures, following the existing infantry units | 40 mm × 20 mm |
| Cavalry | Multiple mounted figures, following the existing cavalry units | 40 mm × 20 mm |

Monstrosities is a generic category, not the name of a specific unit. Use descriptive unit and artwork names such as Giant, Trolls, or the particular war machine. Giant, the two-Troll unit, and the two-Ogre unit belong to Monstrosities.

Base dimensions and figure counts describe the assembled model. Upright layout follows the subject: heroes use a single upright; the existing Giant, Trolls, and Ogres units use one upright with fixed panel heights (35 mm for Giant; 23 mm for Trolls and Ogres). Monstrosities may be taller than ordinary foot figures. Preserve monster artwork proportions and keep complete figures and weapons within the print panel.

## Existing implementation

The catalog currently uses `kind: 'Infantry'` for Foot, `kind: 'Mounted'` for Cavalry and mounted Heroes, `hero: true` for Heroes, and `kind: 'Monster'` for Monstrosities. These internal fields control rendering and folding; the unit type definitions above also cover future foot heroes and war machines.

Keep catalog IDs stable when renaming units or artwork so saved setups retain quantities and names. The Giant retains the legacy ID `orc-troll`; Trolls retains `orc-monstrosities`. Use `artwork/Orcs/orc-trolls.png` for the two-Troll artwork.

## Validation

For changes to fold geometry or rendering, run the relevant browser/PDF tests in `tests/test_workshop.py`. Artwork and filename changes should be checked for successful loading and PDF export. Keep README descriptions and recorded artwork paths current.
