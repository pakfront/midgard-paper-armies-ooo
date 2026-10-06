# Print and base options plan

Status: implemented. All 21 browser/PDF tests pass; combined print preview visually inspected. Physical label fold validation remains pending.

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

## 4. Label integrated into a rear fold

- Add a label placement choice alongside the existing nameplate toggle: Separate (default) or Attached rear fold. Disabled nameplates produce neither kind of label.
- Reuse unit names, individual base overrides, fallback artwork names, and existing readable-text validation.
- Use a uniform 5 mm rear label upright for every unit type, independent of figure panel height, with a matching 5 mm return panel so it folds and glues back-to-back (10 mm of unfolded label material). Existing 6–8 pt single-line text should fit with vertical clearance; verify readability with a physical sample.
- Attach the flap at the assembled rear edge of the base. For Foot and Monstrosities this can extend the terminal ground section. Cavalry folds run across the frontage, so its rear edge is along the side of the strip: use a full-frontage side flap anchored to the first end foot, with a slit freeing the rest of its shared edge from the figure strip. Include Heroes in the geometry review.
- Keep the ground sections' assembled footprint unchanged. Add label panels and fold guides explicitly, orient the text to read correctly after folding, and avoid redundant separate labels in attached mode.
- Extend packing to account for the complete flap bounds and provide cut outlines that follow the resulting shape. Reserve space so attached labels never overlap neighboring strips or captions.
- Extend the shared scene, SVG preview, and PDF export to render label faces, outlines, and folds consistently. Update the fold diagram and assembly instructions with the attachment and folding sequence.
- Extend validation and persistence; older setups retain their separate-nameplate behavior.

## Implementation order

1. Add validated settings, backward-compatible defaults, and editor controls; implement Letter and square cavalry geometry.
2. Add gradient rendering and persistence.
3. Sketch the uniform 5 mm rear-flap net for both fold directions, then implement attached labels and packing.
4. Update README and run the relevant browser/PDF checks in `tests/test_workshop.py`, followed by the full existing suite.

## Acceptance checks

- Fresh setups default to Letter; existing A4 setups round-trip unchanged.
- Both cavalry sizes have the correct assembled dimensions, ground totals, rider counts, and non-overlapping page placements. Mounted and foot Heroes retain their single uprights and 20 × 20 mm bases.
- Gradients run dark-to-light from feet to crest on both assembled faces, match in preview and PDF, and persist through save/load. Solid mode remains available.
- Attached labels preserve the base footprint, fold at the actual rear edge, display the intended base name, and remain readable. Cover Foot, both cavalry sizes, Heroes, and fixed-height Monstrosities.
- Separate labels retain their 38 × 4 mm unit and 18 × 4 mm Hero sizes. Disabled labels print no label components.
- Exercise combined options, multiple pages, both paper sizes/orientations, oversized-strip errors, long names, legacy JSON, browser reload, and mobile controls.
- Confirm artwork loads and PDF export succeeds without clipped figures or weapons. Perform a physical cut-and-fold check of the attached flap before calling its geometry complete.

Validation command: `.venv/bin/python -m unittest discover -s tests -v` (use the README development setup if dependencies are missing).

## Validation result

- `.venv/bin/python -m unittest discover -s tests -v`: 21 tests passed.
- Combined square Cavalry, mounted Hero, Foot, and Giant preview inspected with gradients and attached labels.
- Starter quantities and fold-diagram examples now use stable catalog IDs so artwork additions cannot displace them. Existing catalog-count assertions were brought up to date.
- Physical cut-and-fold trial of the label flap remains outstanding.
