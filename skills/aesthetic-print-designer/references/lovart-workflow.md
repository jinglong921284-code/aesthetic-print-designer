# Lovart Print Workflow

Use this adapter only when Lovart is available and the user explicitly requests it or already has the project on a Lovart canvas. Otherwise apply the same concept/repeat/technical separation with an available image editor or return the edit prompt and export constraints for manual use.

## Canvas continuity

- Continue on the current Lovart canvas for the same print theme.
- Keep colourways, repeat repairs, scale variants, and garment previews on that canvas.
- Create or switch canvas only when the user explicitly asks or the theme genuinely changes.

## Three-layer workflow

1. **Concept layer**
   - Develop motif grammar, scale, density, palette, and mark quality.
   - Preserve approved decisions between iterations.
2. **Repeat-candidate layer**
   - Export a flat square artwork only.
   - Remove model, garment, typography, logo, mockup, frame, paper shadow, perspective, and lighting.
   - Ask for deliberate left/right and top/bottom motif continuation, but label the result as a candidate.
3. **Technical layer**
   - Run local edge, offset, palette, and tiled-preview validation.
   - Return the half-offset diagnostic to the same Lovart canvas when repair is required.
   - Repair only the central cross and preserve the outer 20%-25% safe zone.
   - Finalize and validate locally again.

## Prompt structure for repeat candidates

State:

- print architecture and directionality
- motif roles and scale hierarchy
- density and negative-space rhythm
- exact palette and ground colour
- required square flat artwork
- deliberate edge-crossing continuity
- prohibited presentation elements
- prohibited symmetry, grids, mirror diamonds, and repeated focal points

## Prompt structure for seam repair

Use the half-offset diagnostic as the edit target:

> Repair only the central vertical and horizontal seam region. Continue every stripe or motif through the centre with matching width, angle, curvature, colour, and mark character. Preserve the outer 20%-25% of the image unchanged because it is the periodic boundary safe zone. Do not add motifs, colours, symmetry, text, garments, mockups, shadows, frames, or perspective.

## Lovart limitations

- A visually smooth Lovart export can still fail pixel continuity.
- A generated "seamless" label is not evidence.
- Lovart may alter untouched edges during an edit; local finalization must restore periodic edge identity.
- Repeated regeneration can drift approved motifs. Prefer targeted edit on the same canvas over full rerender.
- Garment mockups and campaign text belong after tile approval and must be separate outputs.

## Required Lovart deliverables

- clean concept artwork
- clean repeat candidate
- repaired half-offset candidate when needed
- optional colourways with composition locked
- separate garment or campaign mockup after validation
