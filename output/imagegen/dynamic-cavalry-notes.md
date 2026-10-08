# Dynamic cavalry variants

## Rohan couched-lance riders

Final selection: the initial generated version was restored to match the user's reference, then edited to hide the extra upper bent arm. The lance remains on the rider's right (far) side, occluded by the torso, with its rear butt visible behind the shoulder. Only the near left hand holding the reins and the shield remain in front. The grip and alpha correction prompts below are historical attempts, not the selected version.

### Final extra-arm removal prompt

Use case: precise-object-edit. Remove ONLY the extra upper arm from this Rohan charging rider paper miniature. The extra arm is the bent brown sleeve/glove and green upper arm directly above the round shield, attached to the visible silver shoulder plate. Hide that entire upper bent forearm and hand: replace its area with the green cloak/torso and natural shoulder contour, no extra hand above shield. Keep the LOWER near-side left hand and silver cuff holding reins in front of the horse mane. The right lance-holding arm is on the FAR side and completely occluded by torso and shield; DO NOT move the lance to the visible side and DO NOT add a visible right arm. Preserve the horizontal lance exactly where it is, behind rider torso, forward tip left and rear butt behind shoulder. Preserve horse, all four legs, saddle, round horse-emblem shield, green cloak, helmet, face, overall pose and framing. Clean bold outlines, flat colors, minimal detail. Genuine transparent RGBA background, clear outside subject, near-opaque figure, no glow, ground, shadow, text or scenery.

The generated interior alpha is 253–254 (about 99% opaque), with zero-alpha background pixels. Browser loading and PDF export checks accept near-opaque figure pixels (alpha ≥ 250) and preserve source alpha.

### Final alpha correction

Use case: background-extraction. Preserve EXACTLY the complete horse-and-rider artwork and couched lance pose. Fix alpha only: the entire figure interior (horse, rider, shield, lance, cloak, reins, legs and all details) must be FULLY OPAQUE alpha 255. Everything outside its silhouette, including all gaps between legs and reins, must be truly transparent alpha 0. Only outer antialiased edge pixels may have intermediate alpha. Remove all translucent background glow and haze. Do not fade the subject or apply global transparency. Do not recolor, reshape, redraw or reposition the subject. Export clean transparent RGBA printable cutout.

Generated with built-in imagegen, followed by a targeted grip correction. Existing charging riders are preserved. Final asset: `artwork/middle-earth-third-age/Rohan/rohan-couched-lance-profile.png`. Catalog ID: `rohan-couched-lancers`. Standard Cavalry base and configurable rider count.

Reference: `artwork/middle-earth-third-age/Rohan/rohan-charging-rider-profile.png`.

### Initial prompt

Use case: precise-object-edit. Asset type: transparent paper Cavalry miniature, new Rohan charging rider with a COUCHED LANCE. Reference establishes chestnut horse, green cloak, bronze-trimmed helmet, silver armor, round green shield with white horse emblem and bold clean ink style. Create ONE complete rider and horse in STRICT LEFT SIDE PROFILE charging at a powerful gallop, all four anatomically coherent legs visible, cloak streaming back. Critical pose change: lance is firmly COUCHED UNDER THE RIDER'S RIGHT ARMPIT at lower chest height, elbow bent and tucked backward beside torso, right hand holding shaft near hip/ribs, rear butt of shaft extending behind elbow. Lance shaft passes under armpit and points horizontally LEFT above horse neck with fully visible spear tip. Do not use an outstretched straight arm, overhead grip, or throwing spear pose. Show the bent right elbow and hand visibly above the shield's upper rim so the couched grip reads clearly. Left arm controls reins, shield on visible side. Rider leans slightly forward braced in saddle. Compact lance suitable for miniature, overall width:height about 1.5:1. Bold contours, broad flat color masses, only two or three large shading tones, minimal face, smooth armor without fine mail texture, no hatching, scratches, tiny fittings or hair strands. Entire weapon, ears, tail, cloak and all hooves within frame with clear padding. Genuinely transparent RGBA background, zero alpha outside subject, no ground, shadow, dust, scenery, motion lines, text, borders or base.

### Grip correction prompt

Correct this transparent paper miniature's lance grip ONLY. Keep horse, rider identity, colors, shield, charging pose and complete framing. The current horizontal shaft is too high, behind the neck, and the right hand misses it. Move the ENTIRE horizontal lance DOWN to rider's lower chest, running just ABOVE the top edge of the green shield and BELOW the silver shoulder plate. The shaft must pass THROUGH the existing right gloved hand beside the torso and UNDER the right upper arm/armpit: hand visibly wraps around the wooden shaft, bent elbow braced back. Front of shaft extends horizontally left above horse neck, rear butt extends horizontally right under armpit, all one straight continuous shaft. It is a true COUCHED lance at rib height. Left hand holds reins. No lance at chin/neck level. Preserve transparent alpha background, remove any background glow/haze, zero alpha everywhere outside complete figure, no shadow or ground. Bold contours, flat colors, large simple shading, no texture.


Generated with the built-in imagegen tool. All existing artwork and catalog IDs are preserved. New entries use Cavalry (`kind: 'Mounted'`, no hero flag), mirrored faces, adjustable Heavy/Light Rider counts, default 40 × 20 mm bases and optional 30/40 mm depths. Complete profiles retain their aspect ratios and generated alpha.

## orc

Final asset: `artwork/middle-earth-third-age/Orcs/orc-lunging-warg-profile.png`

Reference: `artwork/middle-earth-third-age/Orcs/orc-warg-profile.png`

Use case: stylized-concept. Asset type: transparent printable paper Cavalry miniature. Generate ONE rider and mount in strict LEFT SIDE PROFILE, orthographic elevation. Reference is for faction equipment, palette and clean ink style, not pose. Bold black contours, broad flat colors, only 2–3 large shading tones, minimal face, no fine texture, hatching, scratches, hair strands or tiny fittings. Dynamic anatomically coherent pose, four complete legs, complete weapon, ears and tail within frame with generous clear padding. Compact total silhouette approximately 1.3:1 width to height, legible fitted to a 19 mm-wide print panel. Genuine transparent RGBA background; no ground, cast shadow, scenery, dust, motion lines, lettering, border or base. Grassy green Orc in blue-grey armor, rust-red cloth and brown leather, crude red shield without heraldry, on tawny wolf-like warg. Warg lunges left with front legs reaching and hind legs pushing off, jaws open. Rider leans forward and raises a short sturdy cleaver diagonally overhead to strike. Fur only broad planes and a few silhouette tufts.

## mordor

Final asset: `artwork/middle-earth-third-age/Mordor/mordor-charging-warg-profile.png`

Reference: `artwork/middle-earth-third-age/Mordor/morannon-orcs.png`

Use case: stylized-concept. Asset type: transparent printable paper Cavalry miniature. Generate ONE rider and mount in strict LEFT SIDE PROFILE, orthographic elevation. Reference is for faction equipment, palette and clean ink style, not pose. Bold black contours, broad flat colors, only 2–3 large shading tones, minimal face, no fine texture, hatching, scratches, hair strands or tiny fittings. Dynamic anatomically coherent pose, four complete legs, complete weapon, ears and tail within frame with generous clear padding. Compact total silhouette approximately 1.3:1 width to height, legible fitted to a 19 mm-wide print panel. Genuine transparent RGBA background; no ground, cast shadow, scenery, dust, motion lines, lettering, border or base. ONE heavily armored Mordor Orc with ash-grey/grey-olive skin, bright iron-grey armor midtones, charcoal and crimson cloth, warm brown leather, angular charcoal shield with a simple large crimson eye emblem. Mount is a warm dark-brown wolf-like warg with lighter tan muzzle and broad fur planes. Warg bounds forward left, front paws curled and hind legs pushing back. Rider crouches aggressively in saddle thrusting a short robust spear diagonally forward above the warg head. Keep weapon modest so silhouette stays compact. Reference infantry establishes Mordor identity only; create cavalry.

## rohan

Final asset: `artwork/middle-earth-third-age/Rohan/rohan-sword-rider-profile.png`

Reference: `artwork/middle-earth-third-age/Rohan/rohan-charging-rider-profile.png`

Use case: stylized-concept. Asset type: transparent printable paper Cavalry miniature. Generate ONE rider and mount in strict LEFT SIDE PROFILE, orthographic elevation. Reference is for faction equipment, palette and clean ink style, not pose. Bold black contours, broad flat colors, only 2–3 large shading tones, minimal face, no fine texture, hatching, scratches, hair strands or tiny fittings. Dynamic anatomically coherent pose, four complete legs, complete weapon, ears and tail within frame with generous clear padding. Compact total silhouette approximately 1.3:1 width to height, legible fitted to a 19 mm-wide print panel. Genuine transparent RGBA background; no ground, cast shadow, scenery, dust, motion lines, lettering, border or base. ONE Rohan rider on a chestnut horse, green cloak sweeping back, silver armor simplified without mail texture, bronze-trimmed helmet, round green shield with large simple white horse emblem. Horse in energetic collected canter, one foreleg extended and the other bent, hind legs driving. Rider twists slightly at waist while remaining side-on, raises a short broad sword diagonally forward overhead for a downward slash. No spear. Complete sword and four hooves.

## gondor

Final asset: `artwork/middle-earth-third-age/Gondor/gondor-charging-lancer-profile.png`

Reference: `artwork/middle-earth-third-age/Gondor/gondor-lancer-profile.png`

Use case: stylized-concept. Asset type: transparent printable paper Cavalry miniature. Generate ONE rider and mount in strict LEFT SIDE PROFILE, orthographic elevation. Reference is for faction equipment, palette and clean ink style, not pose. Bold black contours, broad flat colors, only 2–3 large shading tones, minimal face, no fine texture, hatching, scratches, hair strands or tiny fittings. Dynamic anatomically coherent pose, four complete legs, complete weapon, ears and tail within frame with generous clear padding. Compact total silhouette approximately 1.3:1 width to height, legible fitted to a 19 mm-wide print panel. Genuine transparent RGBA background; no ground, cast shadow, scenery, dust, motion lines, lettering, border or base. ONE Gondor lancer in bright silver-blue plate armor, black cloak streaming backward, brown leather tack, black shield with bold simple white tree, on chestnut horse with white blaze and socks. Horse gallops left, neck stretched, forelegs reaching and hind legs kicking back. Rider leans forward holding a short stout lance leveled almost horizontally left just above horse head, full tip visible. Keep lance modest in length and silhouette compact.
