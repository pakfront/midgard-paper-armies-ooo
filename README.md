# Midgard Army Workshop

Run `./serve.sh` and open `http://localhost:8000`. The workshop runs entirely in the browser. One project file holds the army, paper settings and artwork assignments.

1. In **Army & battle roster**, name the army and its contingents. Create standard or custom profiles under **Unit types**, then add numbered units and heroes under **Force**. The battle sheet updates points, reputation and trackers as you edit. Choose columns and paper size and use **Print battle roster / PDF**.
2. In **Army standees**, choose artwork for each used type and hero. Expand a type’s contingent choices to give its reserve a different image. Use **Individual print labels** for short names and **Contingent badges** for colors and shapes that match the battle sheet. Badges use the rear ground band, including when names are turned off. Each force entry prints once. Download the cutting sheets with **Download print PDF** and print at actual size.
3. **Manual standees** lets you build a separate selection of bases directly from the artwork catalog, including historical armies. You can switch back to the roster and its assignments at any time.
4. Use **Save project** and **Open project** to move the entire project between browsers. **Undo** restores the preceding project edit. A native [Osgiliath example project](src/roster/osgiliath.json) includes six units and one hero.

The roster rules and editor were adapted from `midgard-roster-maker` revision `f2912cc`. See [profile sources](docs/profile-sources.md).

## Paper standees

A static paper-army workshop for folded standees on **40 mm wide × 20 mm deep bases**, with optional **40 × 30 mm and 40 × 40 mm Cavalry and Monstrosities bases** and **20 × 20 mm Hero bases**. Choose Gondor, Rohan, or orc units, set quantities and colors, preview the cutting sheets, and download accurately sized PDFs.

Rohan adds foot spearmen and archers, mounted spearmen, horse archers, and Royal Guard, with a separate charging-rider variant (galloping horse and leveled lance), plus **Éowyn as a mounted hero on a 20 × 20 mm base**. Her single mirrored upright ignores the army rider count, uses the mounted panel height, and unfolds to 20 × 62 mm at the default height. Hero nameplates are 18 × 4 mm.

New dynamic Cavalry variants add **Orc lunging warg riders**, **Mordor charging warg riders**, **Rohan sword riders**, **Rohan couched-lance riders**, and **Gondor charging lancers** alongside all existing artwork. Each uses mirrored side profiles, adjustable Heavy/Light Rider counts, and the standard **40 × 20 mm base** with optional deeper bases. Prompts and asset paths are recorded in [dynamic cavalry notes](output/imagegen/dynamic-cavalry-notes.md).

Gondor also includes generic mounted heroes: a sword-bearing captain and a standard bearer, plus dynamic variants with a charging captain and a herald on a rearing horse. Each uses one mirrored upright on a **20 × 20 mm base**, independent of the cavalry rider count, with an optional **18 × 4 mm** nameplate.

Orcs include two generic mounted heroes: an axe-wielding chieftain on a charging warg and a herald with a ragged wolf banner. Both use the same 20 × 20 mm hero bases, single mirrored upright, and optional 18 × 4 mm nameplates.

The Orc faction also has a single slovenly, human-looking Giant on a **40 × 20 mm base**, with one **35 mm tall panel** independent of infantry ranks and panel height. Its artwork keeps its proportions, and its reverse follows the infantry silhouette/blank setting. The unfolded strip is **40 × 90 mm**, with an optional **38 × 4 mm** nameplate. **Trolls** adds two smaller Trolls side by side on one **23 mm tall upright**, also on a **40 × 20 mm base**; its unfolded strip is **40 × 66 mm** and uses the same reverse and nameplate options. **Ogres** adds two bulky armored brutes guided by the original Giant design, using the same base and 23 mm panel as Trolls.

The catalog includes Gondor swordsmen, spearmen, foot archers, mounted lancers and horse archers; Isengard Uruk-hai with spears and shields and Uruk-hai crossbowmen; plus Orc axemen, mixed warriors, foot archers, warg riders and warg archers. Foot units generally use frontal ranks of eight figures; Rangers of Gondor use six in a loose skirmishing formation; mounted units use side profiles mirrored on their reverse faces. The Rohan foot and Isengard ranks use simplified contours and broad color shapes for small printing; edit prompts are recorded in `output/imagegen/foot-print-simplification-notes.md`.

Additional light troops include **Dunlending javelinmen** under Isengard, **Mordor trackers** with shortbows, **Rohan outriders**, and **Haradrim javelin skirmishers**. Dunlendings and Haradrim have eight varied figures; Mordor trackers have six in a loose skirmishing formation. All use **40 × 20 mm bases**, using bold contours, broad flat colors and minimal detail. Outriders use a lightly equipped rider and horse in mirrored profile with adjustable Cavalry rider count. The completed scope is recorded in [LIGHT_TROOPS_PLAN.md](LIGHT_TROOPS_PLAN.md); final prompts and asset paths are in [light troop artwork notes](output/imagegen/light-troops-expansion-notes.md).

Mordor artwork uses a consistent palette of iron grey, charcoal, crimson and warm brown, with muted ash-grey/grey-olive Orc skin. Broad lighter material highlights improve small-print readability. Trackers use six figures with varied standing and crouching poses, matching the faction palette. The catapult and Cave Troll retain their complete proportions and fixed panel sizes. Final edit prompts and current asset paths are recorded in [Mordor contrast notes](output/imagegen/mordor-print-contrast-notes.md).

The **Goblins** faction supplies light troops for Orc armies: **Goblin archers**, **Goblin spearmen**, and **Goblin light warg riders**. Foot artwork has eight varied figures with visible gaps, mismatched clothing, and irregular poses on **40 × 20 mm bases**. Archers and spearmen follow the Orc clean-print treatment: bold contours, broad flat colors, two or three shading tones, and minimal surface detail. Light warg riders use mirrored side profiles and the existing adjustable Cavalry rider count; choose two riders for a more spread-out base. Prompts and artwork paths are recorded in [Goblin light troop notes](output/imagegen/goblin-light-troop-notes.md).

Gondor light Foot includes **Gondor militia**, an uneven rank with varied colored clothes and mixed weapons, and **Rangers of Gondor**, six lightly equipped bowmen in woodland cloaks, with varied standing, crouching and kneeling poses in a loose formation. Militia uses eight figures; both use the existing Foot folds on **40 × 20 mm bases**. Artwork and prompts are recorded in [Gondor light unit notes](output/imagegen/gondor-light-unit-notes.md).

Gondor siege Monstrosities include a **trebuchet** and **bolt-throwing ballista**, each with one upright on a **40 × 20 mm base**. Bold outlines and simplified side profiles keep the machines readable at small print sizes. The trebuchet uses a fixed **35 mm panel** (40 × 90 mm unfolded); the ballista uses a **23 mm panel** (40 × 66 mm unfolded). Artwork retains its proportions, including the complete arm, sling, bow and bolt. Both follow the infantry silhouette/blank reverse setting and support 38 × 4 mm nameplates.

The original fantasy artwork belongs to the **Middle-earth · Third Age** era (`middle-earth-third-age`). Era and faction filters only affect browsing; selected bases remain in the print setup. Catalog entries declare their era, and the app builds the available era and faction choices from the catalog. Artwork files are organized by era, then faction: `artwork/<era-id>/<faction>/<filename>`. This lets different eras reuse faction and artwork names without conflicts.

The **American Civil War** era (`american-civil-war`) includes CSA and USA infantry, mounted and dismounted cavalry, field artillery, and mounted leaders. Infantry and dismounted cavalry use a frontal rank of eight figures on 40 × 20 mm Foot bases. Mounted cavalry uses one side-profile upright on a 40 × 20 mm Cavalry base. Each artillery unit has one gun with two crew on a 40 × 20 mm Monstrosity base with a fixed 23 mm panel. Leaders use one mounted upright on a 20 × 20 mm Hero base. CSA uniforms use grey and butternut; USA uniforms use navy and light blue. These units use the existing fold, reverse, and nameplate options. Generation notes are in `output/imagegen/american-civil-war-notes.md` and `output/imagegen/american-civil-war-expansion-notes.md`.

Mordor also includes **Mordor Warboss**, a foot leader with a cleaver axe and an eye-emblem shield. He uses one upright on a **20 × 20 mm Hero base**, preserves artwork proportions, and follows the infantry silhouette/blank reverse setting. The default name fits the **18 × 4 mm** Hero nameplate. Artwork and the generation prompt are recorded in [Mordor Warboss notes](output/imagegen/mordor-warboss-notes.md).

**Isengard Boss** and **Orc Warboss** add matching foot leaders for Isengard and Orcs. Isengard uses pale warm-grey skin, steel-grey armor, brick-red cloth, tan leather and a white-hand shield; Orcs uses grassy green skin, slate-blue steel, brick red, ochre and brown leather. Both use one upright on a **20 × 20 mm Hero base**, preserve artwork proportions, follow the infantry reverse setting, and have default names that fit the Hero label. Built-in imagegen prompts and paths are recorded in [Isengard Boss notes](output/imagegen/isengard-warboss-notes.md) and [Orc Warboss notes](output/imagegen/orc-warboss-notes.md).

The **Napoleonic Wars** era (`napoleonic`) starts with **French** and **Spanish** factions, each with a line infantry unit of eight figures on a **40 × 20 mm Foot base**. French Line wears blue coats and shakos; Spanish Line wears white coats and bicornes, representing early Peninsular War troops. Both use the existing rank, reverse, nameplate and PDF options. Artwork lives in `artwork/napoleonic/French/` and `artwork/napoleonic/Spanish/`; prompts are recorded in [Napoleonic artwork notes](output/imagegen/napoleonic-notes.md).

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
./serve.sh
```

Open <http://localhost:8000>. Use `./serve.sh --port 8080` to choose another port. The script requires Python 3 and works from any directory. The helper binds to localhost and disables caching while working on artwork. Press Ctrl+C to stop it.

The site also works with `python3 -m http.server 8000` or any static web host. Serve the complete directory, including `src/`, `vendor/`, and `artwork/`. Python only serves files: PDF generation, image preparation, and setup storage all run in the browser. There is no build step, backend, API key, or runtime CDN dependency. Opening `index.html` directly with `file://` is not supported because the site uses JavaScript modules.

## Use

Unit selection stays in the left column. The right column contains the print preview and download button, followed by a separately scrollable **Print options** section. Its **Settings** tab groups Foot (Warriors and Skirmishers), Cavalry, Monstrosities, and Heroes, followed by base identification, colors, and paper settings. Fixed base sizes and shared controls are explained beside the relevant units. The **Instructions** tab contains the live fold diagram and assembly instructions; the preview and download button remain visible above both tabs. Detailed label and symbol guidance expands on demand. On narrow screens, these sections stack below the catalog.

1. Select an **era**, then filter by faction and set the number of bases for each unit. The initial sample contains one base each of Gondor swordsmen, Gondor cavalry, orc axemen, and warg riders.
2. Optionally enable **nameplates** in Print options. Set a unit name or expand **Individual base names** for copy overrides. **Separate nameplates** prints 38 × 4 mm unit labels (Heroes 18 × 4 mm). **Wraparound tabs** replaces the former upright attached labels: Foot, foot Heroes, and Monstrosities get 10 mm extensions at both strip ends. Names are printed in the 3 mm bands next to the base seams, facing upright on the front and rear edges; the remaining 7 mm wraps underneath for tape. Cavalry and mounted Heroes get two broad 10 mm tongues at the ends of the long unfolded strip, spanning the full base depth. These wrap over the left and right base edges; there are no small tabs between riders. They also get two separate full-frontage name strips, marked front and back: a front strip with a 3 mm label band between 3 mm top and underside flaps (9 mm total), and a back strip with a 3 mm label band followed by a 7 mm underside tongue (10 mm total, no top flap). These fit a 3 mm thick base. Wraparound text uses 6 pt; separate labels fit from 8 pt down to 6 pt. Names that do not fit block export with a request to shorten them. Blank names use the artwork name. Latin letters (including common accents), numbers and punctuation are supported. Test the wrap with your base and paper before printing an army.
3. Choose a unit type beside each Foot or Cavalry base quantity: **Warriors** or **Skirmishers** for Foot; **Heavy Riders** or **Light Riders** for Cavalry. Set **Warriors ranks deep** (default 2), **Skirmishers ranks deep** (default 1), **Heavy Riders across** (default 4), and **Light Riders across** (default 3) independently. Every base of a catalog unit uses its chosen type. Heroes and Monstrosities retain their fixed uprights. Infantry reverse faces may be grey silhouettes or blank. Choose 40 × 20, 40 × 30, or 40 × 40 mm bases independently for Cavalry and Monstrosities (default 40 × 20 mm). Monstrosities retain their fixed upright count, artwork proportions and panel height; only their ground sections deepen. Cavalry always has mirrored profile artwork on opposite faces; deeper bases widen the panels with blank space while keeping figures at their 20 mm-depth size and proportions. Heroes retain 20 × 20 mm bases.
4. Choose **By faction** ground colors or one ground color for the setup, plus setup-wide solid or gradient figure backgrounds and rear silhouettes. The figure background applies to both faces, including blank reverses. Transparent artwork sits above the background.
5. Select US Letter (the default for new setups) or A4, orientation, margins, spacing, and fold guides. Oversized strips block export with a message; reduce rider/rank count or panel height, or use a paper orientation with enough room. For example, a default four-rider strip needs portrait paper.
6. Download the PDF and print on **one side** at **100% / actual size**. Disable fit-to-page and measure the printed 40 mm ruler.

Sheet packing tries several arrangements, fills spare space below shorter units with other pieces and labels, and chooses the candidate with the fewest sheets. It preserves the selected margin and gap, reserves captions and the scale ruler, and includes complete wraparound tab bounds. The former row layout remains a fallback.

Figure backgrounds can be solid or a vertical gradient. Gradient mode starts with dark blue `#456b94` at the feet and very light blue `#eef7ff` at the crest; both colors are editable. The gradient follows the assembled figure orientation on both faces, including blank reverses. Solid mode remains the default.

**Fake ground shadows** optionally adds translucent black silhouettes to Foot, Cavalry, and Hero ground sections. Infantry and foot Heroes keep small shadows (at most 2.5 mm) on both sides of each upright. Cavalry and mounted Heroes cast one larger, compressed horse-and-rider silhouette to the same side of every upright, across the frontage. It fills the following ground foot up to the next rider or base edge, with 0.25 mm clearance at each edge and a height capped at 80% of the figure panel height to keep it compressed. Both cavalry base sizes are supported. Monstrosities are unaffected. The option defaults to off and is saved with the project. Preview and PDF use the same transparent shadow images.

Ground colors default to **By faction**, with distinct, bold colors within each era. The faction filter swatches and catalog bands match the printed ground sections and attached ground tabs. Choose **One color for the setup** to use the custom ground color instead.

| Era | Faction ground colors |
|---|---|
| Middle-earth · Third Age | Gondor: royal blue; Rohan: forest green; Mordor: crimson; Isengard: amethyst; Harad: ochre gold; Orcs: burnt orange; Goblins: warm brown |
| American Civil War | USA: Union blue; CSA: copper |
| Napoleonic Wars | French: imperial blue; Spanish: ochre gold |

**Base identification** has independent **Print faction symbols on the ground** and **Print base labels** options. Both are optional and saved with the setup. Symbols use bold vector shapes: Gondor tree, Rohan horse head, Mordor eye, Isengard hand, Harad serpent, Orc axe, and Goblin spearhead; Civil War uses a USA star and CSA crossed sabres; Napoleonic uses a French eagle and Spanish tower. They print in contrasting white or dark ink on the ground color. Foot, Heroes, and Monstrosities use the last ground foot; Cavalry uses a central gap between riders, with its emblem rotated to face along the base depth. Symbols are 3–8 mm square with clearance from folds and cuts. Dense Foot formations with insufficient rear space omit the symbol. A small patch behind each symbol clears fake shadows without removing them elsewhere. Symbols add no paper pieces and do not change fold dimensions.

Enable **Number bases of the same unit** for automatic labels such as “Gondor Spears 1” and “Gondor Spears 2”. Numbering starts at 1 for each catalog unit with multiple bases; single bases and Heroes remain unnumbered. A custom unit name keeps its number; an individual base name replaces the entire automatic label. Separate labels and both sides of wraparound labels use the same name. Existing label dimensions and minimum readable text size are retained; shorten a name if it does not fit.

**Rear ground band** is the default label placement for new setups. It reserves a **7 mm** rear identification band when labels or faction symbols are enabled. Symbols remain independently selectable and sit beside the text; symbols alone also reserve the band. Short labels use one line, with a two-line fallback for narrower Hero bases (minimum 6 pt). Hero names are centered across the full rear band when they fit beside the faction symbol; longer names use the available space beside it. Symbol-only Hero bands center the symbol. The ground color forms the label background and shadows are cleared behind it.

For Foot, two ranks move from 5/15 mm to **3/13 mm** from the front, preserving their 10 mm spacing. Three/four ranks compress to 5 mm / 3⅓ mm spacing with a 3 mm front foot and a 7 mm rear foot. Single-upright Foot Heroes and Monstrosities center within the depth ahead of the rear band, preserving their fixed panel heights and counts. Their label prints directly on the final ground foot, with no separate label. Two ground-colored 10 mm tongues extend the strip at both ends: fold 3 mm down the base edge and tape the remaining 7 mm underneath. These secure the base while leaving the rear label on top. When labels are enabled, the front tongue also prints the same name in a white 3 mm band at 6 pt, like wraparound mode; the rear tongue stays ground-colored.

Cavalry retains its rider spacing across the frontage. Complete horse/rider artwork moves toward the front in a narrower region, preserving proportions. On 20 mm bases the available panel depth is 13 mm, so artwork shrinks; on 30/40 mm bases the normal artwork size is retained and moved forward. Mounted Heroes retain their 20 mm bases and use the narrower artwork too. Purple cut lines mark the rear 7 mm of each paired panel, even when fold guides are disabled. **Fold and glue the upright pairs first, bend the ground feet away, then trim only the doubled upright panels at the purple marks before mounting. Keep every ground foot intact.** Glue the single full-frontage 40 × 7 mm rear label (20 × 7 mm for mounted Heroes) flat across the assembled rear ground. The label includes an extension below the band: fold 3 mm down the rear base edge and glue the remaining 7 mm underneath (17 mm total height). This creates one continuous readable band behind the riders, with no tongue above the label. When labels are enabled, Cavalry also prints one front wrap label: a white 3 mm name band between ground-colored 3 mm top/underside flaps. Fold it at both guides and attach it to the front base edge. Cavalry retains two plain ground-colored 10 mm end tongues to wrap over the left/right base edges and underneath. Base footprints, panel heights, and upright counts remain unchanged; the tongues add 20 mm to the unfolded strip length.

The [rear ground band test PDF](output/rear-ground-band-test.pdf) compares **20 mm cavalry on page 1** with **30 mm cavalry on page 2**, including Foot, Skirmishers, a mounted Hero, and a Giant. See the [20 mm preview](output/rear-ground-band-20mm.png) and [30 mm preview](output/rear-ground-band-30mm.png); see the [recorded settings](output/rear-ground-band-test.json) for the controls. Print at 100% and fold a sample to assess the trimmed cavalry and rear label visibility before printing an army.

A [printable identification sample](output/identification-sample.pdf) compares two numbered Foot bases, Skirmishers, three- and four-rider Cavalry, a Hero, and a Giant with symbols and shadows. The [first-page preview](output/identification-sample.png) shows the placements. Print at 100% to assess recognition and the viewing angles around the upright figures before printing an army.

Settings are remembered in this browser and included in **Save project**. Open a saved project to restore both workshops.

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

The table describes default 40 × 20 mm unit bases. Cavalry bases use their selected 20, 30 or 40 mm depth as strip width and the same 208 mm default unfolded length. Monstrosities retain 40 mm strip width; 30/40 mm depths add 10/20 mm to their default unfolded length. Wraparound mode adds 20 mm to the strip length for every unit type; strip width stays unchanged. Mounted units also print separate front and back name wraps. Packing reserves the complete tab bounds and the extra labels.

For `n` uprights of height `h` over base span `d`, unfolded length is **`d + 2nh`**. Upright spacing is `d/n`; each end foot is `d/(2n)`. The ground lengths sum to the exact base span. Real paper and glue add a small thickness, so test a base with your chosen stock before printing an army.

Infantry artwork fills its panel with 0.5 mm clearance on each edge, using the compressed miniature proportions of the earlier print tests. Mounted figures keep their aspect ratio and the artwork size used on a 20 mm-deep base. Increasing Cavalry base depth to 30 or 40 mm adds equal blank space on either side of the figure, while hooves/paws stay 0.5 mm above the foot fold. Height includes weapons. The first face is rotated 180° and the opposite face is reflected horizontally so outlines register across the crest. Silhouettes use the source alpha, not a black rectangle.

## Assembly

1. Score the fold lines before cutting. Solid rectangles are cut outlines, brown dashes are mountain folds, and blue dots are valley folds, viewed from the printed side.
2. Cut the complete rectangular strip. Keep all connecting ground sections intact.
3. Fold at each mountain crest with the printed faces outward. Glue the unprinted backs of each pair of figure panels together.
4. Valley-fold at the feet and glue the undersides of the ground sections to the base. Infantry runs across its frontage; cavalry profiles run along its depth.

For wraparound mode, keep the two broad end tongues connected to the ground sections. Cavalry strips now have straight sides with no notches; fold their end tongues over the left and right base edges. Mountain-fold at the base seam and again 3 mm farther out: the first 3 mm covers the base edge, and the remaining 7 mm tapes underneath. Foot names sit on both exposed edge bands. Fold cavalry's separate front/back name strips at both guides, place the central name band on the corresponding base edge, and tape the 3 mm flaps onto the top and underside. The previous 5 mm upright label flap has been replaced following a physical test. Verify these new wraps with your own 3 mm base before printing an army. Saved setups using `labelPlacement: 'attached'` now use wraparound geometry. An updated [US Letter test sheet](output/wraparound-test.pdf) includes square Cavalry with broad end tongues, a mounted Hero, Foot, and a Giant; print at 100% / actual size. A [first-page preview](output/wraparound-test.svg) shows the new cavalry layout.

This version uses rectangular upright panels so the figure background color remains visible. It does not generate contour-cut outlines or rear-view artwork. Rear ground band mode adds straight post-fold trim marks to cavalry panels. The PDF retains 600 dpi panel images and vector solid backgrounds, 600 dpi gradient backgrounds, cut lines, fold guides, labels, and a scale ruler. Preview and PDF use the same scene geometry and colors.

Default catalog names use terse title casing, generally **Faction Shortname** (for example, **Gondor Lancers**, **Gondor Militia**, and **Mordor Catapult**). Names are limited to **20 characters including spaces**, or **14 for Heroes** with smaller nameplates. Every default name is checked against the printable label width. Variant details remain in the unit descriptions. Custom names and saved unit IDs are preserved; custom names still use the existing readable-font fit check.

## Files

- `index.html`, `src/styles.css`, `src/app.js`: editor and browser storage.
- `src/model.js`: validated setup and fold-strip geometry.
- `src/packing.js`: millimetre-based packing into free sheet space, with multiple candidate layouts and space reserved for captions and ruler.
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

Isengard Uruk-hai, crossbowmen, and Warg riders use brighter steel midtones, clearer red cloth, and warmer wood/leather/fur for small-scale printing. Current artwork uses the three `*-contrast.png` variants in `artwork/middle-earth-third-age/Isengard/`; originals remain available. Exact edit prompts and paths are recorded in [Isengard contrast notes](output/imagegen/isengard-print-contrast-notes.md).
