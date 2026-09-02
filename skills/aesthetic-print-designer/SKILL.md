---
name: aesthetic-print-designer
description: Create, iterate, validate, document, and hand off original fashion textile prints from visual references, themes, trend research, saved visual collections, or optional generation canvases. Use for 印花设计、花型设计、图案设计、定位花、满版印花、边框花、工程印花、四方连续、无缝循环、repeat tile、印花审美画像、印花审美更新、印花配色、快速色彩候选、Pantone TCX 匹配、编号取色标注、规格单图表对应、可选飞书印花规格单、motif development、印花上身预览、接版检查、原创性初筛，或经授权的选稿闭环. Do not use for garment silhouette, pattern cutting, construction, or technical flats except when a garment mockup only evaluates print placement.
---

# Aesthetic Print Designer

## Objective

Turn a changing brief and visual references into an original, coherent, textile-aware print system. Treat references as evidence of taste and technique, never as artwork to reproduce.

## Mode Routing

- When the user explicitly asks to create or update a persistent **personal print-aesthetic profile**, read `references/user-aesthetic-profile.md` and use `assets/user-aesthetic-profile-template.md`. Analysis may be read-only; do not create or update a profile file unless the user asked for that write. A newly synthesized profile remains `candidate` until the user approves it.
- For a lightweight lookup from one or more supplied or already sampled HEX values, read `references/pantone-quick-match.md` and run `python3 scripts/run_print_tool.py pantone-quick ...`. Keep the result outside closure and label it a screen-computed candidate with physical review pending.
- Numbered artwork, a colour table, a specification document, supplier use, or production work always uses the formal `references/pantone-spec-sheet.md` and role-locked `colour-spec` path. The quick route must not be promoted into a specification.
- When a local tool cannot find its dependencies, read `references/runtime-setup.md`. Do not add a host-specific Python path or bundled proprietary colour database to the reusable skill.

## Workflow

1. Inspect all supplied references before designing. Record emotional tone, motif grammar, composition, scale hierarchy, density, negative space, colour relationships, mark character, and likely rejection signals. Separate these principles from protected artwork, recognizable layouts, logos, characters, and brand signatures.
2. Parse the brief: theme, product use, material, season, audience, motif, palette, scale, density, repeat type, quantity, output type, aspect ratio, and exclusions. Before generation, create a series identity card with `series name`, `series type`, `chapter or occasion`, `premise`, `symbolic role`, `stable anchors`, `allowed variation`, `exclusions`, and `approval state`. Treat the user's stated series assignment as authoritative. Never merge designs because they share a date, folder, palette, technique, or source board. If series ownership is unclear, label it `unassigned candidate` until confirmed. Use an approved user or project profile for low-risk stylistic omissions; without one, keep them open instead of inventing a palette, motif preference, material, or brand taste.
3. Research current cultural or trend context only when requested or when time-sensitive evidence is required. Separate sourced observations from creative inference and convert every finding into a usable print decision. When `fashion-trend-intelligence` is available and supplied a translation card, read the approved version before forming a premise; otherwise use the user-supplied evidence and do not design from a trend name or moodboard alone.
4. Apply the **reference-first gate**. If the user supplies one or more images, classify each as `reference image`, `edit target`, or `supporting image`, then create a compact reference card: mood, motif grammar, palette relationship, scale/density rhythm, edge/texture, negative space, material behavior, and likely rejection signals. Extract transferable principles only; separately list protected identifiers, brands, distinctive layouts, characters, or artwork that must not be reproduced. If no reference is supplied, mark the direction `text-led exploratory` and lower confidence; do not present it as a reliable read of the user's aesthetic unless the user explicitly asks for a no-reference exploration.
5. Choose the print architecture before writing prompts: placement, all-over, border, engineered, panel, directional repeat, half-drop, or four-way repeat. Read `references/print-systems.md` for the relevant rules.
6. State one concise series premise. Define the stable anchors—theme, core palette, material character, and mark language—and the meaningful differences among variants. Do not create a batch by changing only scale or density.
7. Build an original motif system. Assign roles such as hero, secondary, connector, texture, and negative space. For multiple references, make a feature map first and assign each selected principle a new role, hierarchy, arrangement, or palette balance; never average or trace the source layouts.
8. Route the available generation or editing surface by task stage. Prefer a tool that can use the supplied edit target directly for reference-led exploration, quick visual tests, and one-off garment mockups. Use Lovart only when it is available and the user explicitly requests it, needs same-theme canvas continuity, or already has work on that canvas; then read `references/lovart-workflow.md`. Keep concept, repeat candidate, and presentation outputs separate. If no compatible image tool is available, return a production-ready prompt and the required export constraints instead of claiming that an image was generated.
9. Write one generation prompt per direction. Specify print type, motifs, composition, scale hierarchy, density rhythm, palette, ground colour, textile/mark finish, tile logic, output ratio, reference-image roles, and negative constraints. For a repeat candidate, prohibit models, garments, text, logos, mockups, frames, shadows, and perspective.
10. Generate or export a clean concept image. Label it as concept artwork, repeat candidate, placement artwork, colourway, or garment mockup. Lovart or another image generator may propose seam logic, but never proves pixel continuity.
11. For every repeat candidate, run `python3 scripts/run_repeat_tool.py validate <input> --out-dir <directory>`. This entry point selects a Python environment containing Pillow and NumPy. Treat `edge_lock_pass` only as proof that opposite boundary pixels are locked. Inspect the offset check and 3 × 3 preview, then rerun with `--visual-status pass|revise|fail --visual-notes "<evidence>"` to record the human visual decision. If validation fails, half-offset the image so all original edges meet at the centre, repair only the central cross on the same available editing surface, preserve an outer safe zone, export again, and rerun validation.
12. When the repaired export is already in half-offset form, run `python3 scripts/run_repeat_tool.py finalize <input> --output <file>` to lock the outer boundary exactly. Use `--palette` only when the brief has an approved fixed palette. Rerun validation through the same entry point on the finalized tile. Do not use mirroring as an automatic repair because it can create diamonds, pinwheels, faces, or obvious symmetry.
13. Evaluate with `references/quality-rubric.md` and record the decision with a copy of `assets/quality-evaluation-template.md`. Apply hard gates before calculating the weighted score. Return exactly one decision: `Fail`, `Revise`, or `Pass to sample`. Reject near-copies, mechanical variations, accidental leopard rosettes, unwanted characters, broken repeat edges, muddy marks, generic stock motifs, visible grids, mirrored focal points, and print placements that ignore garment panels. For a day-end, batch, or portfolio review, read `references/series-development-review.md`; inventory original concepts, revisions, final candidates, repeat evidence, mockups, and review records separately, deduplicate technical derivatives, group only by confirmed series identity, and review each series against its own premise before comparing portfolio roles.
14. For colour work beyond the lightweight exact-HEX quick route—or whenever the task includes numbered colour annotation or a specification document—read `references/pantone-spec-sheet.md` before editing images or documents. Preserve the artwork exactly, map every numbered callout to exactly one table row in the same order, keep physical size in the specification field rather than drawing dimension arrows on the artwork, and distinguish computed matches from screen-only candidates.
15. Deliver the premise, motif hierarchy, palette, print architecture, numbered directions, assumptions, final tile, offset check, large-area repeat preview, validation report, and production caveats. Use descriptive filenames such as `print_<series>_<direction>_<version>_tile`.
16. When a direction advances to sampling, supplier handoff, or production approval, read `references/production-handoff.md` and prepare a versioned local handoff package. Treat the user-approved specification system as the technical source of truth. Uploading a document, sending email, contacting a supplier, or transferring a production file requires a separately confirmed target and authorization; preparing the package does not authorize delivery. Fill only confirmed values and keep digital-repeat validation, strike-off approval, and production-file approval as separate gates.

## Neutral Baseline Policy

- The public skill has no default palette, motif family, brand aesthetic, garment category, fabric, or target customer.
- Use this precedence: `current brief and explicit feedback → project approvals and exclusions → approved personal aesthetic profile → approved trend translation → neutral technical quality rules`.
- Neutral quality rules cover coherence, intentional hierarchy, legible scale, controlled edges, repeat or placement integrity, truthful evidence, and rights-risk screening. They do not decide whether work should be nostalgic, minimal, floral, animal-led, luxurious, playful, or restrained.
- When a stylistic value is missing and would materially change the result, keep it pending or ask one concise question. Do not turn a previous user's taste into a global default.

## Reference Handling

Before generation, return a compact reference review unless the user asks to skip it:

1. **Keep:** transferable principles that fit the brief.
2. **Avoid:** identifying, generic, off-brand, or copy-prone elements.
3. **Original expansion:** two or three new premises with different motif hierarchies.
4. **Rights screen:** protected or identifying elements that will not be carried forward.

For two or more references, map each image by mark edge, scale hierarchy, density rhythm, palette relationship, and compositional movement. Select compatible principles, give each a new role, and create a composition not present in any source.

The rights screen is a creative risk check, not legal clearance. Do not claim ownership, licensing, trademark clearance, or freedom to operate without the appropriate records and qualified review.

## Trend Aesthetic Intake Gate

For a trend-led print, preserve the translation card ID/version and source trend ID in the design record. Before generation:

1. Check that the card separates observed evidence, inference, and candidate translation and maps retained codes to sources. If it is missing, create a bounded provisional extraction and label it `awaiting trend/planning confirmation`; do not present it as an approved trend conclusion.
2. Filter the card through this precedence: `current brief and explicit feedback → project-specific approvals/exclusions → approved personal aesthetic profile → trend aesthetic card → neutral technical quality rules`. A lower layer never overrides a higher one.
3. Convert only compatible codes into print variables: motif grammar, hero/secondary/connector roles, composition, movement, scale hierarchy, density/negative space, palette relationship, mark/edge/texture, print architecture, material affinity, and category use.
4. Return a compact decision: `retain`, `reinterpret`, `exclude`, or `explore`, with the reason and source-card field. Preserve conflicts and low-confidence signals instead of smoothing them into one generic style.
5. Create at least two original expansions by recombining general codes from multiple sources and changing their roles, hierarchy, or composition. Reject literal motifs, recognizable layouts, brand signatures, and trend-following that adds no project-specific point of view.

Keep the translation card unchanged as evidence. Store design decisions as a new print-brief version so later feedback can revise the design without silently rewriting the trend.

## Batch Rules

- Share one series premise, palette world, and mark language.
- Give every direction one stable anchor and one meaningful compositional distinction.
- Do not promote a mildly liked result into a fixed benchmark. Classify feedback as `candidate signal`, `approved direction`, or `production benchmark`.
- Preserve explicitly approved decisions in later iterations.

## Selection and Closure Authorization

An explicit decision such as `选中`, `保留`, `确认`, `selected`, or `this one is final` approves the creative direction only. It does not by itself authorize creating a tracked closure folder, updating a cloud document, uploading media, sending email, contacting a supplier, or transferring a production file. Ordinary positive feedback such as `还可以`, `不错`, `方向可以`, or `looks promising` remains a candidate signal.

Read `references/selection-closure-routing.md` when the user asks to start closure, prepare sampling or specification materials, hand off the design, or has already enabled a named automatic-closure mode. Resolve an approved project directory, existing or user-confirmed Print ID and design name, exact source bytes, print architecture, and the allowed local/external actions. Never invent a production identifier or initialize from a screenshot or re-encoded substitute.

For an authorized selected direction:

1. Lock the selected source non-destructively with Print ID, version, approval evidence, and checksum. Never overwrite it.
2. Generate a garment mockup only when the approved category and garment template exist. Change only the textile surface.
3. Build a colour-first specification draft from a completed copy of `assets/colour-role-template.json`. The numbered annotation and table must have the same count and order: callout, colour role or element, representative source HEX, named-system digital candidate, and confidence or computed delta. Fabric remains `待确认` unless the user supplied it.
4. Route by architecture. Run repeat validation and seam repair only for repeat architectures. Placement, border, engineered, and panel work require their own boundary, scale, orientation, named zone or pattern piece, seam, bleed, and registration evidence; do not force them through repeat repair.
5. For a repeat closure that needs machine-tracked local evidence, read `references/selection-closure-state-machine.md`. Its default `local` document mode can close without Feishu. Use `--document-mode feishu` only when Feishu is available, the user selected that exact target, and document access is authorized.
6. Never infer physical repeat size, DPI, colour approval, ICC profile, supplier process, shrinkage, fabric, or production tolerance. Mark unavailable values `待确认`.
7. Prepare the local handoff package and report which external gates remain. Perform a cloud-document write, upload, email, supplier contact, or file transfer only after the specific target and action are authorized.

Keep these gates separate: `direction selected`, `digital integrity passed`, `specification draft completed`, `physical sample passed`, and `production file approved`. Automation may advance authorized work; it never collapses approvals or broadens permission.

## Repeat Validation Gate

- Treat `1:1` as physical print scale, not merely a square image ratio.
- A square candidate is not a repeat until left/right and top/bottom continuity are verified.
- Require exact edge-lock data, half-offset visual inspection, and a minimum 3 × 3 tiled preview. Never interpret edge locking alone as proof of visual continuity.
- For an approved fixed palette, require the intended number of output colours after finalization.
- Reject a tile with visible seams, clipped tips, white pinholes, overlaps, width jumps, grid tracks, repeated focal points, mirror diamonds, or cross-shaped symmetry even when edge pixels match.
- Label a tile `digital seamless repeat passed` only when `overall_status` is `digital_seamless_repeat_passed`, which requires both edge locking and a recorded visual pass.
- Keep physical repeat size, DPI, colour mode, separations, print process, fabric behavior, registration, and supplier requirements open until confirmed.

## Specification Integrity Gate

- Treat a supplied or approved specification as the source of truth for section order, labels, dimensions, colour rows, and technical notes.
- Before any external write, confirm the target and authorization, fetch the live document under the required identity, record the current revision or version, and state an explicit allowlist of prints and fields that may change. Do not modify a print, size, colour, image, or note outside that allowlist.
- Preserve the source artwork's aspect ratio, crop, motif placement, colour, texture, and edge content. A colour-annotation image may add callouts only; reject outputs that crop, regenerate, extend, or recompose the artwork.
- Unless the user or live specification defines another style, use the bundled annotation preset: white outlined numbered circle with transparent interior, compact black numeral, short white double-line leader, and a small white outlined endpoint circle placed on the sampled colour. This is a configurable presentation preset, not an industry standard. Do not add title boxes, borders, legends, colour-code text, or dimension arrows to the artwork unless the selected template requests them.
- Keep physical dimensions in the highlighted specification field. Never infer or change a dimension from image aspect ratio. Read back every requested dimension after writing.
- Keep image callout numbers, colour-table rows, element names, source HEX values, Pantone codes, colour names, and confidence notes in one-to-one order. Do not count antialiasing, dry-brush transparency, overprint, texture, or ground show-through as separate inks unless production requires a separation.
- Treat a missing, duplicated, reordered, or many-to-one callout/table mapping as a blocking specification failure. Do not write or hand off the specification until the numbered artwork and table pass the same one-to-one sequence check.
- Report `ΔE00` only when it was actually computed against a named colour library. Otherwise label the result `screen approximation candidate` and require physical Pantone FHI Cotton TCX and fabric strike-off review.
- After every authorized image upload, verify native and displayed aspect ratio, dimensions, caption, token uniqueness, and section placement. Remove rejected uploads only when replacement was authorized.
- After all authorized writes, refetch the affected sections and confirm the allowlisted changes, untouched neighboring prints, image dimensions, number-to-table mapping, and final revision. In Feishu mode, the five-column row/cell audit must return `document_consistency_passed`; a write response or partial excerpt is insufficient.

## Cross-Skill Boundary

- Use this skill when the central question is what appears on the textile surface.
- Use `$aesthetic-fashion-designer` when available and the central question is garment silhouette, construction, proportion, pattern cutting, or technical flats.
- For an end-to-end printed collection, complete the print system first, then pass its palette, scale, directionality, repeat type, and placement constraints to `$aesthetic-fashion-designer`. If that skill is not installed, return those five handoff fields explicitly for a human or another garment-design workflow; do not invent a skill-discovery tool.
- For a mixed request that changes garment construction and applies a print, resolve the construction change with `$aesthetic-fashion-designer` first, approve and lock the resulting garment template, and only then apply the print as a textile-surface edit. Never change a neckline, silhouette, seam, trim, or pattern piece inside a print-mockup step whose garment construction is supposed to remain locked.

## Output Modes

- **Print concept:** premise, motif hierarchy, palette, print architecture, and prompt.
- **Repeat candidate:** square tile plus repeat preview; state that edge and production checks remain required.
- **Validated digital repeat:** final tile, edge metrics, half-offset check, 3 × 3 preview, palette count, and validation report.
- **Placement artwork:** artwork boundary, orientation, scale, anchor point, and intended garment zone.
- **Colourways:** keep composition fixed and change palette hierarchy deliberately.
- **Garment mockup:** evaluate print scale and placement only; do not present the garment as a resolved fashion design.
- **Production handoff:** versioned local specification and control record, transfer manifest, open risks, approvals, and named next owner; add delivery-channel and supplier-receipt evidence only after an authorized transfer, and never convert pending values into assumptions.
