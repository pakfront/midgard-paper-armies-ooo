# Light troops expansion plan

Status: implemented and validated. All four units are integrated; changes are uncommitted.

## Scope

Implement the four suggested starting units for Middle-earth factions lacking dedicated light troops. These are visual unit designs for the workshop.

| Faction | Unit | Type | Catalog ID | Artwork filename |
|---|---|---|---|---|
| Isengard | Dunlending javelinmen | Foot | isengard-dunlending-javelinmen | dunlending-javelinmen.png |
| Mordor | Mordor trackers | Foot | mordor-trackers | mordor-trackers.png |
| Rohan | Rohan outriders | Cavalry | rohan-outriders | rohan-outrider-profile.png |
| Harad | Haradrim javelin skirmishers | Foot | harad-javelin-skirmishers | harad-javelin-skirmishers.png |

## Artwork requirements

- Use built-in imagegen and the existing Orc clean-print instructions: bold contours, broad flat colors, only two or three large shading tones per material, minimal faces, no grain, hatching, scratches, mail rings, fine hair, stitching or tiny fittings.
- Foot units have eight distinct full figures, varied builds, head heights, poses and clothing; visible gaps between bodies; all feet share a baseline. Maintain compact proportions readable at 40 mm frontage.
- Dunlendings: lightly equipped human hillmen with javelins and small shields; earthy mixed clothes, bare heads and simple caps.
- Trackers: wiry Orc bowmen with shortbows and light leather gear; mixed muted skin tones, ragged clothing and uneven poses.
- Haradrim: human javelin skirmishers with small shields, mixed red/ochre/cream clothes and varied headwraps.
- Outriders: one lightly equipped human rider and horse in strict side profile, with light spear and small shield; green/brown clothing, minimal armor. Use existing Cavalry repetition and configurable rider spacing; two riders gives a loose base.
- All assets have genuine transparency, opaque figures, complete feet and weapons, and clear margins. No scenery, ground, shadow, text or base.
- Save assets under `artwork/middle-earth-third-age/<Faction>/`; record final prompts and reference roles in `output/imagegen/light-troops-expansion-notes.md`.

## Execution

1. Write this plan before implementation.
2. Generate and inspect each asset, iterating if detail, figure counts or framing fail the requirements.
3. Add new catalog IDs using existing Foot (`Infantry`) and Cavalry (`Mounted`) rendering on 40 × 20 mm bases. Keep existing IDs and starter quantities stable.
4. Update README and artwork notes.
5. Validate faction filtering, transparent image loading, base dimensions, adjustable mounted spacing and browser/PDF export in `tests/test_workshop.py`. Run relevant existing faction and cavalry checks.
6. Record completion and validation here. Leave changes reviewable in the working tree.

## Acceptance

- All four units appear under their intended faction and use the existing fold layouts.
- Each Foot image contains eight varied figures with sparse detail and visible spacing.
- Outrider artwork preserves proportions and complete horse, rider and spear.
- New artwork loads successfully and exports into a valid PDF; existing selections survive faction filtering.
- README, catalog paths and recorded prompts agree.

## Completion and validation

- Generated and visually inspected all four transparent PNGs using built-in imagegen. Foot ranks contain eight figures with varied colors, uneven poses and sparse shading; the outrider retains a complete side profile and simplified horse/tack.
- Added the four stable catalog IDs, README descriptions and final prompt/asset notes. Existing render and fold geometry is reused.
- Browser/PDF checks passed: `test_light_troop_expansion_factions_artwork_and_export`, `test_era_and_faction_filters_preserve_selected_bases`, `test_rohan_hero_square_base_and_export`, and `test_letter_square_cavalry_and_new_settings_round_trip` (4 tests).
- Confirmed genuine alpha transparency, opaque figure interiors, faction filtering, valid PDF export with nameplates, 40 × 20 mm bases, and two/four-rider spacing. Updated the Rohan catalog-count expectation for the new outriders.
- `git diff --check` passed.
