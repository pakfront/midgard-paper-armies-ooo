# Print and base options plan

Status: implemented. All 22 browser/PDF tests pass; revised wraparound preview inspected. A physical trial of the new tabs on a 3 mm base remains pending.

## 1. Default to US Letter

- Set the new-setup paper default to `letter` in `src/model.js`, align the fallback in `src/packing.js`, and make Letter the initial selection in `index.html`.
- Keep A4 available. Preserve the paper choice in saved browser setups and imported JSON.
- Verify a fresh browser opens with Letter and exported portrait pages measure 215.9 × 279.4 mm (612 × 792 pt).

## 2. Optional 40 × 40 mm cavalry bases

- Add a setup-wide cavalry base selector: 40 × 20 mm (default) or 40 × 40 mm.
- Apply the option to Cavalry (`kind: 'Mounted'` without `hero: true`). Heroes retain their 20 × 20 mm bases; Foot and Monstrosities retain their catalog dimensions.
- Extend setup validation, browser persistence, and JSON save/load with a cavalry base-depth field. Older setups use 20 mm.
- In `makeStrip`, use the selected depth for cavalry strip width. Keep the 40 mm frontage, rider count, panel height, and rider spacing unchanged. At four riders and the default 21 mm panel height, square-base cavalry unfolds to 40 × 208 mm.
- Preserve mounted artwork proportions and complete figures/weapons within the wider panels.
- Update the fold diagram, dimensions, assembly text, page headings, PDF metadata, and README to describe both base sizes. Keep catalog IDs and artwork paths stable.

## 3. Optional gradient behind figures

- Add a Solid / Gradient background selector. Keep Solid as the initial mode and preserve the existing solid color.
- Give Gradient editable bottom and top colors, initially dark blue `#456b94` and very light blue `#eef7ff`.
- Apply the gradient behind every figure panel, including silhouette and blank reverses. Ground sections keep their separate ground color.
- Orient the gradient in assembled coordinates: dark at the feet and light at the crest on both faces. The rotated front panel needs the opposite sheet direction from its paired back panel.
- Extend validation and persistence for the mode and two colors; older setups remain solid.
- Extend the shared scene/rendering pipeline so SVG preview and PDF use matching colors and direction. Choose a shared gradient representation compatible with the bundled PDF library; a reusable high-resolution background image is an option. Keep transparent artwork over the background and cache keys sensitive to any baked-in colors.

## 4. Wraparound base labels (revised after physical testing)

- Replace the former attached upright labels while keeping `labelPlacement: 'attached'` compatible with saved setups.
- Foot, foot Heroes, and Monstrosities have 10 mm tabs at both strip ends: 3 mm printed name bands at the front/rear base edges, plus 7 mm underneath for tape.
- Cavalry and mounted Heroes have 10 mm side tabs attached to each ground section, leaving figure panels free. They print two separate front/back name wraps, each with a 3 mm name band and 3 mm top/underside flaps.
- Edge labels use 6 pt text and preserve unit/copy names. Separate flat labels remain available.
- Ground totals, base dimensions, artwork sizes, and shadows stay unchanged; packing includes every tab and label piece.
- Fold guides show downward mountain folds at each 3 mm base edge and underside transition. Preview and PDF share the same net.
- Update instructions, geometry tests, and PDF export checks. Physically test the revised wraps on a 3 mm thick base.

## Implementation order

1. Add validated settings, backward-compatible defaults, and editor controls; implement Letter and square cavalry geometry.
2. Add gradient rendering and persistence.
3. Implement wraparound nets for both fold directions and separate mounted front/back name wraps.
4. Update README and run the relevant browser/PDF checks in `tests/test_workshop.py`, followed by the full existing suite.

## Acceptance checks

- Fresh setups default to Letter; existing A4 setups round-trip unchanged.
- Both cavalry sizes have the correct assembled dimensions, ground totals, rider counts, and non-overlapping page placements. Mounted and foot Heroes retain their single uprights and 20 × 20 mm bases.
- Gradients run dark-to-light from feet to crest on both assembled faces, match in preview and PDF, and persist through save/load. Solid mode remains available.
- Wraparound tabs preserve the base footprint, cover the 3 mm base edges, provide 7 mm underneath for tape, and display front/rear names. Mounted name wraps have separate top and underside flaps. Cover Foot, both cavalry sizes, Heroes, and fixed-height Monstrosities.
- Separate labels retain their 38 × 4 mm unit and 18 × 4 mm Hero sizes. Disabled labels print no label components.
- Exercise combined options, multiple pages, both paper sizes/orientations, oversized-strip errors, long names, legacy JSON, browser reload, and mobile controls.
- Confirm artwork loads and PDF export succeeds without clipped figures or weapons. Perform a physical cut-and-fold check of the wraparound tabs before calling its geometry complete.

Validation command: `.venv/bin/python -m unittest discover -s tests -v` (use the README development setup if dependencies are missing).

## Validation result

- `.venv/bin/python -m unittest discover -s tests -v`: 22 tests passed.
- Combined square Cavalry, mounted Hero, Foot, and Giant preview inspected with gradients, shadows, wraparound tabs, and front/back mounted name strips.
- Starter quantities and fold-diagram examples now use stable catalog IDs so artwork additions cannot displace them. Existing catalog-count assertions were brought up to date.
- Physical cut-and-fold trial of the revised wraparound tabs remains outstanding.

Physical test sample: [output/wraparound-test.pdf](output/wraparound-test.pdf), US Letter; print at 100% / actual size.
