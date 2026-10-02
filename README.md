# Paper Army Standees

A static paper-army workshop for folded standees on **40 mm wide × 20 mm deep bases**. Choose Gondor, Rohan, or orc units, set quantities and colors, preview the cutting sheets, and download accurately sized PDFs.

Rohan adds mounted spearmen, horse archers, and Royal Guard, with a separate charging-rider variant (galloping horse and leveled lance), plus **Éowyn as a mounted hero on a 20 × 20 mm base**. Her single mirrored upright ignores the army rider count, uses the mounted panel height, and unfolds to 20 × 62 mm at the default height. Hero nameplates are 18 × 4 mm.

Gondor also includes generic mounted heroes: a sword-bearing captain and a standard bearer, plus dynamic variants with a charging captain and a herald on a rearing horse. Each uses one mirrored upright on a **20 × 20 mm base**, independent of the cavalry rider count, with an optional **18 × 4 mm** nameplate.

Orcs include two generic mounted heroes: an axe-wielding chieftain on a charging warg and a herald with a ragged wolf banner. Both use the same 20 × 20 mm hero bases, single mirrored upright, and optional 18 × 4 mm nameplates.

The Orc faction also has a single slovenly, human-looking Giant on a **40 × 20 mm base**, with one **35 mm tall panel** independent of infantry ranks and panel height. Its artwork keeps its proportions, and its reverse follows the infantry silhouette/blank setting. The unfolded strip is **40 × 90 mm**, with an optional **38 × 4 mm** nameplate. **Trolls** adds two smaller Trolls side by side on one **23 mm tall upright**, also on a **40 × 20 mm base**; its unfolded strip is **40 × 66 mm** and uses the same reverse and nameplate options. **Ogres** adds two bulky armored brutes guided by the original Giant design, using the same base and 23 mm panel as Trolls.

The catalog includes Gondor swordsmen, spearmen, foot archers, mounted lancers and horse archers, plus orc axemen, mixed warriors, foot archers, warg riders and warg archers. Foot units are frontal ranks of eight figures; mounted units use side profiles mirrored on their reverse faces.

Gondor siege Monstrosities include a **trebuchet** and **bolt-throwing ballista**, each with one upright on a **40 × 20 mm base**. Bold outlines and simplified side profiles keep the machines readable at small print sizes. The trebuchet uses a fixed **35 mm panel** (40 × 90 mm unfolded); the ballista uses a **23 mm panel** (40 × 66 mm unfolded). Artwork retains its proportions, including the complete arm, sling, bow and bolt. Both follow the infantry silhouette/blank reverse setting and support 38 × 4 mm nameplates.

The original fantasy artwork belongs to the **Middle-earth · Third Age** era (`middle-earth-third-age`). Era and faction filters only affect browsing; selected bases remain in the print setup. Catalog entries declare their era, and the app builds the available era and faction choices from the catalog. Artwork files remain organized by faction.

The **American Civil War** era (`american-civil-war`) starts with **CSA infantry** and **USA infantry**, each a frontal rank of eight riflemen with bayonets on a 40 × 20 mm Foot base. CSA uses grey/butternut uniforms; USA uses dark blue coats and light blue trousers. Both use the existing infantry folds, panel-height settings, silhouettes/blank reverses, and nameplates.

## Unit types

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

1. Select an **era**, then filter by faction and set the number of bases for each unit. The initial sample contains one base each of Gondor swordsmen, Gondor cavalry, orc axemen, and warg riders.
2. Optionally enable **nameplates** under the unit catalog. Set a unit name or expand **Individual base names** for copy overrides. Each unit base gets a separate **38 × 4 mm** (heroes **18 × 4 mm**) white label with black text and a cut outline. Blank fields use the unit/artwork name. Captions match labels to artwork and base numbers. Cut and glue labels onto your bases; test the placement on your chosen base first. Text fits from 8 pt down to 6 pt; names that do not fit block export with a request to shorten them. Latin letters (including common accents), numbers and punctuation are supported.
3. Choose infantry ranks (default two), infantry reverse faces (20% grey silhouettes or blank), and cavalry riders across the frontage (default four). Cavalry always has mirrored profile artwork on opposite faces.
4. Choose two **setup-wide colors**: ground sections and the background behind figures. Every unit uses the same pair, including blank reverse panels. The background colors are vector fills; the transparent artwork sits above them.
5. Select A4 or US Letter, orientation, margins, spacing, and fold guides. Oversized strips block export with a message; reduce rider/rank count or panel height, or use a paper orientation with enough room. For example, a default four-rider strip needs portrait paper.
6. Download the PDF and print on **one side** at **100% / actual size**. Disable fit-to-page and measure the printed 40 mm ruler.

Settings are remembered in this browser. **Save setup** downloads a JSON file containing quantities, unit and individual base names, the nameplate toggle, folds, colors, and paper settings. **Load setup** restores one; this makes it possible to keep several separate armies/palettes. Artwork remains in the site rather than being duplicated into each setup file.

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

For `n` uprights of height `h` over base span `d`, unfolded length is **`d + 2nh`**. Upright spacing is `d/n`; each end foot is `d/(2n)`. The ground lengths sum to the exact base span. Real paper and glue add a small thickness, so test a base with your chosen stock before printing an army.

Infantry artwork fills its panel with 0.5 mm clearance on each edge, using the compressed miniature proportions of the earlier print tests. Cavalry keeps its aspect ratio, fits within the 20 mm-wide panel, and aligns hooves/paws 0.5 mm above the foot fold. Height includes weapons. The first face is rotated 180° and the opposite face is reflected horizontally so outlines register across the crest. Silhouettes use the source alpha, not a black rectangle.

## Assembly

1. Score the fold lines before cutting. Solid rectangles are cut outlines, brown dashes are mountain folds, and blue dots are valley folds, viewed from the printed side.
2. Cut the complete rectangular strip. Keep all connecting ground sections intact.
3. Fold at each mountain crest with the printed faces outward. Glue the unprinted backs of each pair of figure panels together.
4. Valley-fold at the feet and glue the undersides of the ground sections to the base. Infantry runs across its frontage; cavalry profiles run along its depth.

This version uses rectangular upright panels so the figure background color remains visible. It does not generate contour-cut outlines or rear-view artwork. The PDF retains 600 dpi panel images and vector backgrounds, cut lines, fold guides, labels, and a scale ruler. Preview and PDF use the same scene geometry and colors.

## Files

- `index.html`, `src/styles.css`, `src/app.js`: editor and browser storage.
- `src/model.js`: validated setup and fold-strip geometry.
- `src/packing.js`: millimetre-based page packing with space reserved for captions and ruler.
- `src/render.js`: image normalization, silhouette/mirror preparation, shared preview/PDF scenes.
- `src/catalog.js`: bundled artwork catalog.
- `vendor/`: locally bundled pdf-lib 1.17.1 and its MIT license, taken from the neighboring midgard-sticker-maker project's vendor folder.
- `examples/starter-setup.json` and `examples/starter-print.pdf`: a ready-to-print example with two infantry and two cavalry bases.
- `artwork/CSA/` and `artwork/USA/`: American Civil War infantry PNGs; prompts are recorded in `output/imagegen/american-civil-war-notes.md`.
- `artwork/Gondor/`, `artwork/Rohan/`, and `artwork/Orcs/`: approved PNGs used by the catalog, organized by faction. Rohan artwork is newly generated for this addition.
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
