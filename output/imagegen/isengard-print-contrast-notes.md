# Isengard print contrast refresh

Built-in imagegen edit mode, one referenced original per edit, transparent_background=true. Originals retained; catalog IDs unchanged.

- Input: artwork/middle-earth-third-age/Isengard/isengard-uruk-hai-infantry.png
  Current output: artwork/middle-earth-third-age/Isengard/isengard-uruk-hai-infantry-contrast.png
- Input: artwork/middle-earth-third-age/Isengard/isengard-uruk-hai-crossbowmen.png
  Current output: artwork/middle-earth-third-age/Isengard/isengard-uruk-hai-crossbowmen-contrast.png
- Input: artwork/middle-earth-third-age/Isengard/isengard-warg-rider-profile.png
  Current output: artwork/middle-earth-third-age/Isengard/isengard-warg-rider-profile-contrast.png

## Exact prompt used for each edit

Edit target: the attached existing Isengard miniature artwork. Minor print-readability color and contrast rework ONLY. Preserve composition, exact figure count (eight for a rank; one rider and one warg for the profile), poses, equipment, shields and white hand symbols, full figures and weapons, original proportions and silhouette. Keep transparent background and generous clear border. Designed to print at 40mm frontage and 14.5mm panel height for foot ranks or 21mm panel height for mounted profile. Lift muddy charcoal armor midtones to clean medium cool steel gray with broad bright silver highlight planes and strong dark seams; keep dark shields contrasting with crisp white hand emblems. Make crimson cloth a clearer moderately brighter brick red with broad flat color shapes. Separate warm tan leather and wooden shafts/crossbows from gray armor; if mounted, lighten warg fur to readable warm medium brown with broad golden brown highlights so rider armor and beast remain distinct. Faces pale warm gray clearly contrast helmets. Simplify tiny shading into large readable color blocks; retain bold crisp dark contours. No new details, no embellishments, no glow, no background, no floor or shadow, no text, no changes to design, pose, model count or weapon layout. This is a modest palette refinement, not a redesign.

## Validation

Visually compared originals and revisions at approximate print size (96 dpi). Both foot ranks retain eight figures; the Warg rider retains its pose and equipment. All three images decode with transparency and export together to a one-page PDF. The Middle-earth artwork/foot-Hero browser and PDF regression test passes.

Comparison: output/imagegen/isengard-print-comparison.png (original left, revised right).
Print test: output/isengard-print-contrast-test.pdf; print at 100% / actual size. Physical printer results have not been tested.
