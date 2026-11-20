# Merge the Midgard roster maker into Paper Army Standees

## Outcome

Build an army once in this project. From the same saved army, a player can edit profiles and contingents, print a battle roster, assign figures, and download foldable standees. Editing a unit updates both outputs without a JSON handoff. A player who only wants paper miniatures can still open the manual workshop and choose quantities directly, including for historical armies.

Use this repository as the home of the integrated application. Both projects already run as static browser apps with native JavaScript modules. Keep the current server, static hosting path, and local PDF library. The sibling checkout is a source for the initial port. A fresh checkout of the merged app must run without it.

## What to bring together

| Area | Existing implementation | Merge decision |
| --- | --- | --- |
| Army editing | The sibling’s shipped app is in `dist/`. Its model, catalog, rules, traits and renderer support 15 standard profiles, custom profiles, heroes, points, reputation, numbered units and contingents. | Port those modules under `src/roster/` with their profile-source notes. Use the shipped editor and sheets as the behavioral baseline. |
| Paper miniatures | This project’s `src/catalog.js`, `model.js`, `packing.js` and `render.js` choose art, make strips, pack pages and render SVG previews and downloadable PDFs. | Reuse the existing geometry and rendering pipeline. Introduce an explicit input for each physical base before calling strip generation. |
| Browser UI | Both `app.js` entry points own their DOM, autosave and event handlers. Roster print CSS also controls page size and hides editing controls. | Give the root page navigation for Army, Battle roster and Paper miniatures. Mount each editor within its own root, scope its styles and handlers, and load paper art only when needed. |
| Prior design | [Midgard import plan](MIDGARD-IMPORT-PLAN.md) specifies artwork compatibility, contingent badges and labels. | Reuse its print and mapping details. The live editor supplies the army directly. |

## One project file, two kinds of editing

Introduce a versioned portable document with `format: "midgard-army-project"`, `version: 1` and an explicit manual or roster mode. Give **Save project** and browser autosave the same serialization. Use one schema and one Open and Save workflow across both modes.

| Project state | Owner and identity |
| --- | --- |
| Roster | The army owns profiles, options, traits, spells, contingents, entry IDs, names, numbers, sequence counters and battle-sheet settings. Reuse the cost functions and profile validation rules within the new project validator. |
| Roster paper settings | Store print settings, default art by roster type ID, optional art by type and contingent, hero art by hero ID, short label overrides by entry ID, and badge styles by contingent ID. Artwork values reference the existing catalog IDs. |
| Manual project | Store the validated paper setup, including its quantities, per-artwork role choices and copy names. Creating manual bases requires no roster profiles or points. |
| Derived output | Compute totals, effective labels, base instances, strips and page layouts on demand. Keep roster paper settings independent of battle-sheet paper and column settings. |

Use one project-level edit transaction. Validate a candidate before replacing the current project or its autosave. Undo restores the prior project, including mappings removed with an entry. Preserve edits when switching screens. Document edits, project loading and undo should all trigger the same preview invalidation.

**Opening and restoring projects.** Open validates the merged project format and version before replacing the current document. Invalid files leave the active army and its autosave intact. On startup, read the merged app’s own autosave key and start a fresh project when it is absent. Files and browser saves from either predecessor are outside the scope of the merge.

## From roster entries to physical bases

1. In Paper miniatures, show each used roster type with its role, count and artwork picker. Offer compatible art filtered by era and faction, an optional per-contingent override, and an individual picker for each hero. Mark missing or ambiguous choices visibly. Unused profile definitions require no art.
2. Produce exactly one base per unit or hero. Carry entry ID, contingent ID, type ID where applicable, source name and number, effective print label, artwork ID and effective formation into layout. Resolve contingent art before type art. Editing quantity in a roster project means adding or removing entries in the Force editor.
3. Map Warriors and Skirmishers to Foot using their respective rank settings. Map Heavy Riders and Light Riders to Cavalry using their respective rider counts. Use the catalog’s hero flag for foot or mounted Heroes and its Monster kind for Monstrosities. For custom or unrecognized roles, ask for a compatible print formation and remember it per type. A change in role rechecks the mapping. Artwork density never determines rank count.
4. Derive default labels from roster names, including their existing numbering. Short print labels stay attached to entry IDs through renames and moves. Show the effective badge and label in preview using the same placement logic as PDF. Let the user correct unsupported characters, overlong text or labels that fail the current fit check without changing the army name or unit name.
5. Keep the full roster editable, saveable and printable with unresolved artwork or more than 100 bases. For the first release, explain any blockers before standee export, including missing art, label errors, page fit or exceeding the 100-base layout limit. Never drop entries to make a PDF fit. The manual limit of 50 copies per artwork belongs to manual quantity entry.
6. When moving an entry, resolve its destination contingent’s style and artwork. When deleting it, remove its base and obsolete entry-specific settings in the same transaction. Duplicating a type creates a distinct mapping key. Two types can share an image and still use different formations.

## Implementation order and acceptance gates

| Stage | Work in this repository | Gate before moving on |
| --- | --- | --- |
| 1. Establish the baseline | Record the source revision being ported. Run both current test suites in their original locations. Bring over the production roster modules and profile-source documentation. Adapt the sibling browser suite, which currently serves `dist/`, to this project’s root and module paths. | Standard and custom profile edits, hero options, totals, contingent moves, undo and roster print pass here. Manual catalog selection and paper geometry checks pass. |
| 2. Introduce the project shell | Replace the two persistence paths with project-level Open, Save, autosave and undo. Implement both document modes. Wire navigation and scope DOM IDs, dialogs, keyboard handling and print CSS. | Create a project in each mode, switch views, refresh, save and reopen. Invalid JSON and unsupported versions leave the current project intact. A manual setup reopens with the same counts, roles, labels and dimensions. |
| 3. Connect force to artwork | Implement mapping controls and a pure function that derives base instances from the current roster and paper settings. Route manual setup through an adapter yielding the same layout input. Update `makeStrip`, label generation and packing inputs to consume each instance’s effective role and label. | Map two types to one image with different formations. Rename, move, delete and undo entries. Check distinct labels, counts and stable assignments after every operation and after reload. |
| 4. Finish both print paths | Keep browser Print / Save PDF for the roster and the vendored pdf-lib download for standees. Isolate roster print styles from the application shell. Apply badges and short labels through the shared paper scene. Reuse existing formation controls, assembly guidance and preview. | Roster output includes only the battle sheet in one or two columns on Letter or A4. Standee output matches preview for names, badges and number of bases. Verify real artwork, fold dimensions and page boundaries in the downloaded PDF. |
| 5. Release the integrated site | Update README with army creation, manual selection, project saves and both print workflows. Review `export-site.sh`, which exports a committed tree containing only `index.html`, `src`, `vendor` and `artwork`. Include any user-loadable example in the exported paths. | Stage an export in a disposable Pages checkout, serve it under `/paper-army-standees/`, open both views and generate both outputs. Verify module paths, decoded PNGs and no runtime requests to the sibling or external hosts. |

## End-to-end release fixture

Create a native project fixture using the force described in the sibling’s `dist/example-army.json`, *The defence of Osgiliath*. Give it six numbered Gondor Spears split four and two between two contingents, plus one hero. Open it, map the spears once, assign the hero, and give the reserve an artwork override. Both previews must account for seven entries. The battle sheet must show 147 points and 16 reputation. Move one spear to the reserve and check that its number stays fixed and its printed artwork changes. Save the project, close it, reopen it and generate both outputs again.

Replace predecessor save-format and storage-key assertions with native project round-trip checks. Run the adapted roster tests and `tests/test_workshop.py` together with `python -m unittest discover -s tests -v`. Add cross-view checks for that fixture, native autosave restoration, invalid project files, unresolved mappings and large rosters. Exercise the existing Hero 20 × 20 mm base, default 40 × 20 mm troop bases, configurable Cavalry and Monstrosity depths, and the fixed 35 mm Giant and 23 mm Troll and Ogre panels. Verify a historical manual setup separately. Release when a fresh checkout can complete both journeys using only this project.
