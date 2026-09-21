# Visual Print Specification Sheets

Use this guide for visual, English, one-page or two-page print specifications, or for translating/reformatting an existing sheet. This is a presentation route inside Print Specification Sheet mode, not Production Handoff.

## Scope before format

Choose **Colour Specification** for colour-focused alignment or **Full Technical Specification** for the additional fields in `assets/print-spec-sheet-template.md`. The full data record remains the source of truth. Do not drop confirmed fields or open risks to fit a visual page budget; use a linked continuation or a different layout when necessary.

Keep Markdown for structured review, use available document tools for editable DOCX, and use the bundled renderer for the English two-page PDF preset. The bundled script is not a DOCX exporter or a one-page layout engine. A concise one-page version is an optional manually composed format when the artwork and table remain readable.

## Existing sheet or new artwork

- For an existing sheet, extract the exact embedded numbered image and corresponding colour rows. Retain Print ID, name, source version/date, HEX values, codes, names, and recorded deltas. Translate descriptive fields only. Use working English translations for names unless approved English names exist.
- Do not treat an embedded numbered preview as a production master, derive physical print dimensions from its display size, or turn a historical designer verification into a fresh repeat test.
- Carry over a delta only with the original matching provenance; state that it was not recalculated. If that evidence is absent, use a screen-candidate note instead of presenting an unverified delta as a new result.
- For new extraction, first follow `references/pantone-spec-sheet.md` and the role-locked colour workflow. The PDF renderer consumes the result; it does not sample colours or supply a colour database.
- Reuse the original annotation when no annotation edit was requested. If clean artwork is unavailable, do not erase callouts or regenerate the design merely to make a second preview image.

## Approved two-page preset

Use one pair of pages per Print ID and colourway. Eight or nine representative colours usually warrant two pages; do not merge colourways into a shared table.

**Page 1 — Artwork and identification**

- Series, print name, colourway, Print ID, specification version/date, and design-stage status.
- Compact print type, physical size, representative colour count, and scale fields.
- Large numbered artwork, contained without stretching or cropping.
- Caption linking the callout sequence to page 2; the applicable artwork-use notice beneath it.
- Source-HEX swatches in the same order, followed by concise composition/style text.

**Page 2 — Colour and technical detail**

- The same Print ID and version/date.
- One uninterrupted table: callout, source-HEX swatch, colour role/element, HEX, named-colour candidate/code/name, and supported delta or candidate note.
- Matching source/version and method, clearly distinguishing carried-over values from newly computed results.
- Fabric, process, physical repeat/placement, artwork version, pixel dimensions/DPI, colour mode/ICC, production separation count, confirmation and status fields as applicable. Unknowns remain `To be confirmed`; missing master files remain `To be supplied`.
- Technical risks and open items, historical repeat/sample statuses attributed to their source, and the artwork-use notice in the footer.

Keep type, number, and table text comfortably legible. If a table or note cannot fit, stop the fixed two-page export and use a longer layout; never truncate, hide text, or silently remove colours. For placement artwork, replace repeat-only fields with the applicable boundary, scale, orientation, anchor, and garment/pattern-piece fields.

## Artwork-use notices

The blank preview preset uses:

> Artwork shown is for reference only. No other use is permitted.

This is a configurable preview notice, not a universal assertion about every user's licence. Preserve explicit user restrictions verbatim. For an authorized production document, use the user's applicable notice and approval evidence rather than inventing new rights. Put the notice outside the artwork unless the user explicitly requests a watermark. Do not publish a client's source image, completed sheet, or preview as an example without separate permission; a template release does not authorize those disclosures.

## Export and review

### Input contract

- Set `edition` to `colour` or `technical`. The three starter colour rows are placeholders, not a required colour count: add/remove rows and set both `colours[].id` and `artwork.callout_ids` to the same sequential `1..N` list. The preset accepts 1-12 rows, subject to the actual content fitting two readable pages.
- `artwork.path` is the existing numbered image; relative paths resolve next to the input JSON. `artwork.mapping_review` records the separate visual check. Declared IDs and a successful export do not prove that the image endpoints match the colour roles.
- Each row has `element`, `source_hex` (`#RRGGBB` or `null` when pending), and `candidate`. Use `{"status": "pending"}` when no candidate is available. For a screen candidate, supply `status: screen_candidate` plus `system`, `code`, and `name`. For a recorded computed candidate, use `status: computed_candidate` with those fields and numeric `delta_e00`.
- Recorded deltas require `provenance.source_document`, `colour_library`, and `matching_method`. For inherited values, name the original source/version and state that values are carried over, not recalculated. The renderer does not authenticate that source or query a colour library.
- Keep unknown `technical` fields pending. Use `technical_notes` for additional supplied risks, owners, or review evidence. Unknown JSON keys are rejected rather than silently omitted; when the full technical record needs more space or fields, use a custom layout and retain the full record.
- Keep `status` unchanged unless a real status change was requested and evidenced. `Ready for Sampling` additionally requires `sampling_confirmations` with the current `version`, recorded `design`, `merchandising`, and `pattern_room` confirmations, and an empty `sampling_blockers` list. The renderer neither supplies nor validates the underlying business approval.

### Commands

1. Copy `assets/print-spec-sheet-visual-template.json` into an authorized project output area and fill it from the source record. Keep source/annotation files unchanged. Paths in the input refer to local files; do not place private absolute paths into a public template.
2. Install the optional requirements into the environment used by the renderer:

   ```bash
   python3 -m pip install -r requirements-visual.txt
   ```

3. From the installed skill folder, export the filled input:

   ```bash
   python3 scripts/run_print_tool.py visual-spec --input /path/to/filled-spec.json --output /path/to/print-spec.pdf
   ```

4. Render every PDF page to images with an available PDF renderer and inspect all pages. Check fonts, clipping, row wrapping, intact image aspect ratio, page numbering, use notices, and one-to-one callout/table order. The script validates input structure; it cannot establish that an image's callout endpoint samples the intended colour.
5. Compare the exported colour rows against the source record, verify that unknown values remain pending, and distinguish layout review from design confirmation, physical review, and production approval. A successful export never promotes the status or publishes the file.

Existing output files are protected by default. Choose a new output version, or use `--overwrite` only when replacing that exact file was authorized. Layout errors leave an existing output unchanged.

The bundled preset uses English labels and portable fonts. For supported custom TrueType fonts, supply `--font-regular` and `--font-bold`; fonts are local user inputs, not downloaded or distributed. Do not force unsupported scripts through a Latin-only font. Use a suitable licensed font or an available document/PDF tool and inspect the actual output. No font files or colour libraries are bundled.
