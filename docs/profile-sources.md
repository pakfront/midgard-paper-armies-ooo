# Profile data

The local `../midgard-sticker-maker/src/forces.js` identifies the fifteen standard profiles, role mappings, armour/stamina values, and relevant option deltas. Its comments point to the original force builder as the source for the remaining stats.

The numeric catalog in `src/roster/catalog.js` was checked against the public force builder at https://apps.iwouldliketorage.com/midgard-forces/ on 2026-10-25 (bundle `index-CJCWAYeo.js`). It contains profile values, option deltas, trait names/costs, missile choices and hero trait costs. Application code is not bundled. Concise trait reminders in `src/roster/traits.js` are paraphrased from the builder’s trait data, retaining its rulebook page references. Shared unit and hero traits use the same reminder; this also supplies the description missing from the builder’s hero Hel’s Breath entry. The calculator in `src/roster/rules.js` is independently implemented from those data relationships.

- Unit reputation: rounded points / 10, minimum 1.
- Hero reputation: same baseline, plus trait reputation modifiers.
- Heroes: base costs 5/15/25/35 for levels 1–4; armour changes cost 2 points per step; stamina 1 for level 1, otherwise 2.
- Conditional bonuses from traits stay as traits; they are not added permanently to printed base dice.
- Split armour preserves melee / shooting order from the profile data.
- Spell names/costs are recorded in `src/roster/app.js`.

This is a roster builder, not a complete rules adjudicator. Scenario-specific restrictions and conditional trait effects still use the rulebook. Custom profiles explicitly take user-supplied values.
