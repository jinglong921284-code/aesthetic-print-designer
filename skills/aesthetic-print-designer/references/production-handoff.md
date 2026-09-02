# Print Production Handoff

Use this reference when a print direction advances beyond concept approval. The user-approved specification system explains the design and technical intent; a versioned local package is prepared first. The transfer channel may be email, Feishu/Lark, another approved system, or a manual handoff. Preparing the package never authorizes sending, uploading, contacting a supplier, or recording receipt.

## Ordered workflow

1. Complete the local print specification with artwork, palette, repeat or placement dimensions, fabric, process, and known technical requirements.
2. Lock the approved design direction and generate a versioned final file. Do not call a concept render or garment mockup a production file.
3. Validate a repeat digitally when applicable. Record edge-lock data, offset review, 3 × 3 review, and the final visual decision.
4. Confirm that filename, version, pixel dimensions, physical dimensions, DPI, colour mode, and the approved specification agree.
5. Prepare a transfer manifest containing the exact filename, version, checksum, intended recipient, and pending/authorized channel. Do not send yet unless the user authorized that target and action.
6. After an authorized transfer, record the actual channel, message or subject identifier, date, recipient, and receipt evidence. Never infer delivery or receipt from package preparation.
7. Complete the physical strike-off or sample review on the intended fabric. Record colour, scale, clarity, bleed, show-through, shrinkage, deformation, migration, and colourfastness status as applicable.
8. Revise through a new version when required, obtain authorization for any new transfer, and decide whether a new sample is necessary.
9. Approve bulk production only after the latest transferred version, receipt evidence, sample result, open risks, and responsible owners all agree.

## Truthful status rules

- Copy `assets/production-handoff-template.md` into the approved project or specification target; do not overwrite the asset.
- Use only `已确认`, `待确认`, or `不适用` for confirmation fields.
- Name the source of every confirmed production value: user, supplier, approved standard, lab result, or file metadata.
- Leave an item pending when the value is unavailable. Never infer a physical repeat size from a square aspect ratio.
- Keep `digital seamless repeat passed`, strike-off approval, and production-file approval as separate gates.
- Treat the transfer manifest plus channel evidence as the record of the transferred artifact. Never claim that a file was sent or received without evidence.

## Dimension consistency

Check that pixel dimensions, physical dimensions, and DPI agree:

`physical centimetres = pixels / DPI × 2.54`

Flag differences caused by rounding, scaling, or a supplier template. Confirm whether dimensions describe the repeat tile, placement-art boundary, border depth, or full engineered panel.

## Colour and process

- Record the intended printing process before final colour preparation.
- Record the colour mode, ICC profile or spot-colour definition, ground colour, approved colour count, and physical colour reference.
- Treat a generated RGB value as a design reference, not an approved production colour.
- For a fixed palette, verify the finalized file colour count and preserve the approved hierarchy.
- Require a strike-off when the substrate, ink system, finish, or colour behavior is not already approved.

## Fabric and garment coordination

- Record fabric composition, construction, weight, grain direction, shrinkage, and likely distortion.
- For placement, border, or engineered prints, confirm named pattern pieces, seam crossings, bleed, orientation, mirrored pieces, and placement tolerance with the garment workflow.
- For deep/light colour combinations, mixed materials, or spliced construction, add a visible colour-migration and overall-colourfastness warning.
- Do not invent a pass grade without the destination market, end use, care method, and applicable company, customer, or regulatory standard.

## Approval gate

Do not label a file `production approved` until design, garment/technical, material/process, project owner, and supplier responsibilities are either signed off or explicitly marked not applicable. Record every post-approval artwork, scale, colour, substrate, or process change and decide whether it requires a new strike-off. External transfer remains a separate authorized action at every new version.
