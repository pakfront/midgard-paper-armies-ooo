# Paper Army Standees

A static paper-army workshop for folded standees on **40 mm wide × 20 mm deep bases**, with optional **40 × 40 mm Cavalry bases** and **20 × 20 mm Hero bases**. Choose Gondor, Rohan, or orc units, set quantities and colors, preview the cutting sheets, and download accurately sized PDFs.

Rohan adds foot spearmen and archers, mounted spearmen, horse archers, and Royal Guard, with a separate charging-rider variant (galloping horse and leveled lance), plus **Éowyn as a mounted hero on a 20 × 20 mm base**. Her single mirrored upright ignores the army rider count, uses the mounted panel height, and unfolds to 20 × 62 mm at the default height. Hero nameplates are 18 × 4 mm.

Gondor also includes generic mounted heroes: a sword-bearing captain and a standard bearer, plus dynamic variants with a charging captain and a herald on a rearing horse. Each uses one mirrored upright on a **20 × 20 mm base**, independent of the cavalry rider count, with an optional **18 × 4 mm** nameplate.

Orcs include two generic mounted heroes: an axe-wielding chieftain on a charging warg and a herald with a ragged wolf banner. Both use the same 20 × 20 mm hero bases, single mirrored upright, and optional 18 × 4 mm nameplates.

The Orc faction also has a single slovenly, human-looking Giant on a **40 × 20 mm base**, with one **35 mm tall panel** independent of infantry ranks and panel height. Its artwork keeps its proportions, and its reverse follows the infantry silhouette/blank setting. The unfolded strip is **40 × 90 mm**, with an optional **38 × 4 mm** nameplate. **Trolls** adds two smaller Trolls side by side on one **23 mm tall upright**, also on a **40 × 20 mm base**; its unfolded strip is **40 × 66 mm** and uses the same reverse and nameplate options. **Ogres** adds two bulky armored brutes guided by the original Giant design, using the same base and 23 mm panel as Trolls.

The catalog includes Gondor swordsmen, spearmen, foot archers, mounted lancers and horse archers; Isengard Uruk-hai with spears and shields and Uruk-hai crossbowmen; plus Orc axemen, mixed warriors, foot archers, warg riders and warg archers. Foot units are frontal ranks of eight figures; mounted units use side profiles mirrored on their reverse faces. The Rohan foot and Isengard ranks use simplified contours and broad color shapes for small printing; edit prompts are recorded in `output/imagegen/foot-print-simplification-notes.md`.

Gondor siege Monstrosities include a **trebuchet** and **bolt-throwing ballista**, each with one upright on a **40 × 20 mm base**. Bold outlines and simplified side profiles keep the machines readable at small print sizes. The trebuchet uses a fixed **35 mm panel** (40 × 90 mm unfolded); the ballista uses a **23 mm panel** (40 × 66 mm unfolded). Artwork retains its proportions, including the complete arm, sling, bow and bolt. Both follow the infantry silhouette/blank reverse setting and support 38 × 4 mm nameplates.

The original fantasy artwork belongs to the **Middle-earth · Third Age** era (`middle-earth-third-age`). Era and faction filters only affect browsing; selected bases remain in the print setup. Catalog entries declare their era, and the app builds the available era and faction choices from the catalog. Artwork files are organized by era, then faction: `artwork/<era-id>/<faction>/<filename>`. This lets different eras reuse faction and artwork names without conflicts.

The **American Civil War** era (`american-civil-war`) includes CSA and USA infantry, mounted and dismounted cavalry, field artillery, and mounted leaders. Infantry and dismounted cavalry use a frontal rank of eight figures on 40 × 20 mm Foot bases. Mounted cavalry uses one side-profile upright on a 40 × 20 mm Cavalry base. Each artillery unit has one gun with two crew on a 40 × 20 mm Monstrosity base with a fixed 23 mm panel. Leaders use one mounted upright on a 20 × 20 mm Hero base. CSA uniforms use grey and butternut; USA uniforms use navy and light blue. These units use the existing fold, reverse, and nameplate options. Generation notes are in `output/imagegen/american-civil-war-notes.md` and `output/imagegen/american-civil-war-expansion-notes.md`.

## Unit types

The Middle-earth expansion adds Isengard Warg riders; a Rohan foot captain; Mordor Orc spearmen, heavily armored Morannon Orcs, a banner bearer, a catapult and a Cave Troll; a Gondor foot captain and Aragorn on foot; and Haradrim spearmen, archers and cavalry. Foot Heroes use one upright on a **20 × 20 mm base**, retain artwork proportions, and follow the infantry silhouette/blank reverse setting. The Mordor catapult uses one fixed **23 mm panel** and the Cave Troll one **35 mm panel**, both on **40 × 20 mm bases**. All new artwork follows the simplified print style in [MIDDLE_EARTH_ARTWORK_TODO.md](MIDDLE_EARTH_ARTWORK_TODO.md); full prompts and asset paths are recorded in `output/imagegen/middle-earth-todo-expansion-notes.md`.

| Type | Figures per base | Base size |
|---|---|---|
| Heroes | One figure (on foot or mounted) | 20 × 20 mm |
| Monstrosities | One or two large monsters, or one war machine or similar model | 40 × 20 mm |
| Foot | Multiple figures | 40 × 20 mm |
| Cavalry | Multiple mounted figures | 40 × 20 mm |

Monstrosities is a generic unit type. Giant and Trolls are specific units within that type. Project instructions for future changes are in [AGENTS.md](AGENTS.md).

## Run

From this folder:

```sh
python3 serve.py
```

Open <http://localhost:8000>. Use `--port 8080` to choose another port. The helper binds to localhost and disables caching while working on artwork.

The site also works with `python3 -m http.server 8000` or any static web host. Serve the complete directory, including `src/`, `vendor/`, and `artwork/`. Python only serves files: PDF generation, image preparation, and setup storage all run in the browser. There is no build step, backend, API key, or runtime CDN dependency. Opening `index.html` directly with `file://` is not supported because the site uses JavaScript modules.

## Use

Unit selection stays in the left column. The right column contains the print preview and download button, followed by a separately scrollable **Print options** section for labels, folds, colors, paper settings, and assembly instructions. On narrow screens, these sections stack below the catalog.

1. Select an **era**, then filter by faction and set the number of bases for each unit. The initial sample contains one base each of Gondor swordsmen, Gondor cavalry, orc axemen, and warg riders.
2. Optionally enable **nameplates** in Print options. Set a unit name or expand **Individual base names** for copy overrides. Choose **Separate nameplates** for **38 × 4 mm** unit labels (heroes **18 × 4 mm**), or **Attached rear fold** for a uniform **5 mm tall** white label with black text. Attached labels have two 5 mm panels that fold and glue back-to-back; their width matches the base frontage. Cavalry labels attach to the side of the first ground foot, with a solid slit freeing the remainder of the label from the figure strip. Blank fields use the unit/artwork name. Captions match labels to artwork and base numbers. Cut and glue separate labels onto your bases, or fold attached labels at the rear base edge. Test the fit with your chosen paper first. Text fits from 8 pt down to 6 pt; names that do not fit block export with a request to shorten them. Latin letters (including common accents), numbers and punctuation are supported.
3. Choose infantry ranks (default two), infantry reverse faces (20% grey silhouettes or blank), and cavalry riders across the frontage (default four). Choose 40 × 20 mm or 40 × 40 mm Cavalry bases (default 40 × 20 mm). Cavalry always has mirrored profile artwork on opposite faces; the square option widens its panels while preserving artwork proportions. Heroes retain 20 × 20 mm bases.
4. Choose **setup-wide colors** for ground sections, solid or gradient figure backgrounds, and rear silhouettes. The figure background applies to both faces, including blank reverses. Transparent artwork sits above the background.
5. Select US Letter (the default for new setups) or A4, orientation, margins, spacing, and fold guides. Oversized strips block export with a message; reduce rider/rank count or panel height, or use a paper orientation with enough room. For example, a default four-rider strip needs portrait paper.
6. Download the PDF and print on **one side** at **100% / actual size**. Disable fit-to-page and measure the printed 40 mm ruler.

Figure backgrounds can be solid or a vertical gradient. Gradient mode starts with dark blue `#456b94` at the feet and very light blue `#eef7ff` at the crest; both colors are editable. The gradient follows the assembled figure orientation on both faces, including blank reverses. Solid mode remains the default.

**Fake ground shadows** optionally adds translucent black silhouettes to Foot, Cavalry, and Hero ground sections. Infantry and foot Heroes keep small shadows (at most 2.5 mm) on both sides of each upright. Cavalry and mounted Heroes cast one larger, compressed horse-and-rider silhouette to the same side of every upright, across the frontage. It fills the following ground foot up to the next rider or base edge, with 0.25 mm clearance at each edge and a height capped at 80% of the figure panel height to keep it compressed. Both cavalry base sizes are supported. Monstrosities are unaffected. The option defaults to off and is saved with the setup; older setups keep shadows off. Preview and PDF use the same transparent shadow images.

Settings are remembered in this browser. **Save setup** downloads a JSON file containing quantities, unit and individual base names, label placement, cavalry base size, folds, solid/gradient colors, fake shadows, and paper settings. Older setups load with solid backgrounds, 40 × 20 mm Cavalry bases, and separate nameplates; their saved paper choice is preserved. **Load setup** restores one; this makes it possible to keep several separate armies/palettes. Artwork remains in the site rather than being duplicated into each setup file.

**Clear setup** asks for confirmation before removing all selected bases and custom unit and base names. Fold, color, and paper settings are kept, and the cleared setup is remembered in this browser.

## Fold geometry

Each upright consists of two panels folded at their shared crest and glued back-to-back. Flat ground sections connect the uprights and glue onto the base, colored side up. End feet are half the spacing of the intermediate feet, centering the uprights evenly.

| | Infantry | Cavalry |
|---|---|---|
| Fold direction on the base | Parallel to the long, 40 mm edge | Parallel to the short, 20 mm edge |
| Strip width | 40 mm | 20 mm |
| Flat ground sections total | 20 mm | 40 mm |
| Default uprights | 2 ranks deep | 4 riders across |
| Default upright panel height | 14.5 mm | 21 mm |
| Default unfolded strip | 40 × 78 mm | 20 × 208 mm |

The table describes default 40 × 20 mm unit bases. Square Cavalry bases use a 40 mm strip width and the same 208 mm default unfolded length. Attached labels add 10 mm to the strip length for Foot, Monstrosities, and foot Heroes, or a 10 mm-wide side flap for Cavalry and mounted Heroes. Packing reserves the complete net bounds, including each flap.

For `n` uprights of height `h` over base span `d`, unfolded length is **`d + 2nh`**. Upright spacing is `d/n`; each end foot is `d/(2n)`. The ground lengths sum to the exact base span. Real paper and glue add a small thickness, so test a base with your chosen stock before printing an army.

Infantry artwork fills its panel with 0.5 mm clearance on each edge, using the compressed miniature proportions of the earlier print tests. Cavalry keeps its aspect ratio, fits within the selected 20 or 40 mm-wide panel, and aligns hooves/paws 0.5 mm above the foot fold. Height includes weapons. The first face is rotated 180° and the opposite face is reflected horizontally so outlines register across the crest. Silhouettes use the source alpha, not a black rectangle.

## Assembly

1. Score the fold lines before cutting. Solid rectangles are cut outlines, brown dashes are mountain folds, and blue dots are valley folds, viewed from the printed side.
2. Cut the complete rectangular strip. Keep all connecting ground sections intact.
3. Fold at each mountain crest with the printed faces outward. Glue the unprinted backs of each pair of figure panels together.
4. Valley-fold at the feet and glue the undersides of the ground sections to the base. Infantry runs across its frontage; cavalry profiles run along its depth.

For attached labels, keep the rear flap connected, cut the solid slit on mounted nets, valley-fold at the base attachment, then mountain-fold the label crest and glue its backs together. This yields a 5 mm rear nameplate without changing the ground footprint. A physical fold check is still needed to confirm this new attachment with your paper stock.

This version uses rectangular upright panels so the figure background color remains visible. It does not generate contour-cut outlines or rear-view artwork. The PDF retains 600 dpi panel images and vector solid backgrounds, 600 dpi gradient backgrounds, cut lines, fold guides, labels, and a scale ruler. Preview and PDF use the same scene geometry and colors.

## Files

- `index.html`, `src/styles.css`, `src/app.js`: editor and browser storage.
- `src/model.js`: validated setup and fold-strip geometry.
- `src/packing.js`: millimetre-based page packing with space reserved for captions and ruler.
- `src/render.js`: image normalization, silhouette/mirror preparation, shared preview/PDF scenes.
- `src/catalog.js`: bundled artwork catalog.
- `vendor/`: locally bundled pdf-lib 1.17.1 and its MIT license, taken from the neighboring midgard-sticker-maker project's vendor folder.
- `examples/starter-setup.json` and `examples/starter-print.pdf`: a ready-to-print example with two infantry and two cavalry bases.
- `artwork/american-civil-war/CSA/` and `artwork/american-civil-war/USA/`: American Civil War unit PNGs; prompts are recorded in `output/imagegen/american-civil-war-notes.md` and `output/imagegen/american-civil-war-expansion-notes.md`.
- `artwork/middle-earth-third-age/`: Middle-earth PNG artwork used by the catalog, organized by faction within the era, including Gondor, Isengard, Orcs, and Rohan.
- `output/imagegen/`: artwork prompt notes. Cavalry profile prompts are recorded in `cavalry-profile-notes.md`, and foot/mounted archer prompts in `archer-notes.md`; superseded artwork and prototype print sheets are kept in Git history.

The design takes inspiration from `../midgard-sticker-maker/`: a local artwork catalog, browser-only export, physical dimensions, and setup files. The fold geometry and editor are specific to Paper Army Standees.

## Checks

Development-only dependencies:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/playwright install chromium
.venv/bin/python -m unittest discover -s tests -v
```

Tests start their own local static server and check fold directions and ground totals, pixel alignment of mirrored faces, grey silhouette alpha, pagination and overlap, setup color save/load, PDF page dimensions and color commands, invalid/empty setups, and mobile layout. A physical fold test is still needed to assess your paper and printer.
