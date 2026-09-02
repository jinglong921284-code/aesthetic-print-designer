# Colour-Callout Print Specification Workflow

Use this workflow when extracting print colours, creating numbered colour-callout artwork, or creating and editing a print specification. The approved target specification remains the source of truth; this file defines a reusable structure, a bundled annotation preset, and optional Feishu controls.

## 1. Evidence and change scope

1. For an authorized external edit, fetch the live document with full detail under the required identity and record its revision or version.
2. Build a change allowlist containing the exact print names, block IDs or fields, requested values, and image replacements.
3. Read the current value of every allowlisted field before changing it. Treat all unlisted prints and fields as locked.
4. If the user edits the document during the task, refetch before the next write and use the newest confirmed value. Never overwrite a user edit with an older snapshot.

## 2. Colour extraction

For an explicitly selected print, copy `assets/colour-role-template.json`, lock the intended colour roles, and run `python3 scripts/run_print_tool.py colour-spec`. Treat its share values as composition estimates, not ink volume. Do not replace the role list with unconstrained clustering.

- Inspect the full-resolution source, not a screenshot of the document.
- Separate production colours from visual transition pixels. Dry brush, antialiasing, opacity, texture, overprint, and ground show-through usually do not justify extra inks.
- Record one representative source HEX per intended production colour. Sample from stable interior pixels, not blurred boundaries.
- Confirm the colour system from the substrate, print process, existing specification, and user request. Use Pantone FHI Cotton TCX only when it is the selected textile reference; do not impose it on every substrate or process.
- When a verified library and CIEDE2000 calculation are available, record the library, method, Pantone code, colour name, and `ΔE00`.
- When no verified calculation is available, write `screen approximation candidate`; do not invent a delta or describe the candidate as confirmed.
- Require the corresponding physical colour reference and strike-off review on the actual fabric. Call out sheen, fibre, weight, finish, optical brightener, metamerism, transparency, and dark-colour detail when relevant.
- This package contains no Pantone database. Use only a local colour library the user is authorized to use. A computed result is specific to that digital dataset and is not official certification or physical approval.

## 3. Numbered annotation artwork

Preserve the source artwork exactly. Add only callouts.

Bundled default callout preset:

- white circular outline;
- transparent interior showing the sampled colour;
- compact black Arabic numeral;
- short diagonal white double-line leader;
- small white outlined endpoint circle touching the sampled area.

Placement rules:

- Use one callout for each colour-table row and keep numbering sequential.
- Place the endpoint inside a stable representative colour region.
- Keep markers away from critical motifs where possible and distribute them without creating a visual grid.
- Preserve the exact source aspect ratio, crop, corners, edge motifs, palette, texture, and resolution whenever possible.
- Do not add a title box, border, legend, colour-code text, artwork name, size text, dimension arrows, or other decoration unless explicitly requested.
- Reject and redo any output that crops, zooms, regenerates, extends, recolours, or recomposes the source. Check pixel dimensions before upload.

The visual preset above is configurable. A user-approved or live-document annotation style overrides it. The invariants are source preservation, sequential callouts, and one callout mapped to exactly one table row in the same order.

## 4. Per-print specification section

Use this order for each print, following the live document's existing style:

1. Divider and level-one heading: `印花 N｜名称`.
2. Annotated image with caption: `印花 N — 色彩区域标注`.
3. Two-column information block:
   - left: `风格关键词`、`构图`、`用色结构`、highlighted `尺寸`;
   - right: restrained `匹配概览` callout.
4. `🎨 色板明细（N色/色阶）`.
5. Table columns in this order: `标注`、`元素`、`源图 HEX`、the named colour-system code、`色名 / ΔE00` or `色名 / 说明`. In the bundled Feishu TCX adapter, the code-column header is `Pantone TCX`.
6. One production-note callout explaining separations, weak matches, overlaps, tonal continua, material risks, and physical-review requirements.

Dimensions belong only in the highlighted `尺寸` field unless the user explicitly requests a separate technical drawing. Use the user's exact value and unit. Do not infer a repeat size from the bitmap dimensions or aspect ratio.

## 5. Document-level header and technical requirements

For a new specification, include a compact document-purpose block with:

- document purpose;
- matching system;
- candidate library;
- matching method;
- document version and date.

End with a general technical-requirements table covering, when confirmed:

- recommended print process;
- physical colour-calibration standard;
- digital candidate algorithm;
- first strike-off format;
- fabric confirmation conditions;
- standard-light review and metamerism;
- production file format, resolution, and colour-profile retention.

Finish with the confirmation sequence: physical TCX comparison → actual-fabric strike-off → standard-light review → colour correction → bulk colour approval.

## 6. Optional Feishu editing controls

- Use this adapter only when Feishu tooling is available and the user authorized the exact target and change scope. Selection of a print is not authorization to write the document.
- Use the lark document skill and user identity when the target requires it.
- Prefer targeted block replacement, insertion, movement, or media upload. Never overwrite a resource-rich specification.
- Upload a replacement image, verify it, move it to the intended heading, and only then remove the rejected image when replacement was authorized.
- Re-fetch after block replacement, deletion, insertion, or movement before reusing affected block IDs.
- Preserve image tokens and all unrelated rich blocks.

## 7. Final readback checklist

- Requested print names and ordering are correct.
- Every requested size matches the latest user-confirmed value.
- Unrequested neighboring prints and sizes are unchanged.
- Every annotation image has the correct native/displayed aspect ratio and caption.
- Callout count and numbering match the table rows exactly.
- Source HEX, Pantone code, colour name, and confidence wording are aligned by row.
- The final consistency audit parses the actual mapping table and matches each numbered row against the locked colour-role report; values merely appearing elsewhere in the section do not count as alignment.
- `ΔE00` appears only where computed.
- Production cautions and physical-review gates are present.
- For external edits, the final document revision and affected sections were read back successfully.

For the bundled Feishu TCX adapter, the final audit must parse the actual five-column mapping table and compare every row and cell with the locked colour-role report. A value appearing elsewhere in the section does not prove alignment.
