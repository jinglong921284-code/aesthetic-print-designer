# Aesthetic Print Designer

`aesthetic-print-designer` is a portable, **end-to-end fashion textile print workflow skill**.

> From visual references to original print design, seamless-repeat validation, colour specification, **production-oriented print specification sheets**, and supplier handoff preparation.

[View the sample](#sample-output) · [Workflow](#workflow-at-a-glance) · [Try it](#try-it) · [Download v1.2.0](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/tag/v1.2.0) · [Commercial licensing](COMMERCIAL-LICENSING.md)

[Plugin submission guide](docs/SUBMISSION.md) · [Submission tests](docs/SUBMISSION_TESTS.md) · [Privacy](PRIVACY.md) · [Support](SUPPORT.md)

The root `plugin.json` prepares a skills-only plugin package for OpenAI submission. This is separate from the existing standalone skill ZIP and does not mean the plugin has been submitted, approved, or published in the directory.

## Sample output

**Garden Reverie — Herons by the Stream · GDN-LY-01**

An English, two-page **design-stage draft**: numbered artwork and source-colour swatches, followed by a full colour table, technical fields, notes, and status.

| Page 1 — Artwork and colour callouts | Page 2 — Colour and technical details |
|---|---|
| [![English print specification sheet, page 1: numbered artwork and source-colour swatches. Reference only; no other use permitted.](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.2.0/GDN-LY-01_English_Artwork_Page.png)](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.2.0/GDN-LY-01_English_Artwork_Page.png) | [![English print specification sheet, page 2: colour table, candidate references, technical fields and draft status. Reference only; no other use permitted.](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.2.0/GDN-LY-01_English_Colour_Technical_Page.png)](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.2.0/GDN-LY-01_English_Colour_Technical_Page.png) |

[View the full sample](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/tag/v1.2.0#print-specification-sheet-preview) · [Download the two-page PDF](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.2.0/GDN-LY-01_English_Print_Spec_Sheet_Preview_v0.1.pdf)

> **Artwork shown is for reference only. No other use is permitted.**

The sample demonstrates the visual specification-sheet format, not an end-to-end runtime test or production approval. Its existing colour data and stated provenance were retained; unverified technical fields remain pending. Pantone entries are digital candidates, not physical colour approvals. The sample is separate from the installable skill ZIP and is not offered under the skill's software licence.

## Workflow at a glance

Start at the stage your task needs. Existing artwork can go straight to a specification draft; a request for a sheet does not trigger the entire workflow.

| Stage | What you receive |
|---|---|
| **1. Reference analysis** | A reference review: motif grammar, palette relationships, composition, mark-making, and elements to avoid reproducing. |
| **2. Original print and series development** | Direction proposals, a motif hierarchy, and original concepts or coordinated designs using an available image tool. Without one, the deliverable is a prompt and export brief. |
| **3. Repeat or placement checks** | For repeat artwork: tile, half-offset check, 3 × 3 preview, and validation report. For placement, border, engineered, or panel work: applicable scale, orientation, boundary, and garment-zone checks. |
| **4. Colour and print specification** | Numbered artwork, a one-to-one colour table, and a specification sheet with confirmed values, candidate references, version, status, and open items. |
| **Optional next stage: supplier handoff preparation** | A versioned local package and outstanding sampling/approval items, when requested. Sending, uploading, or contacting a supplier requires a confirmed target and separate authorization. |

Digital repeat checks, physical colour/fabric sampling, and production approval are separate decisions. A passed pixel-edge check alone is not a passed visual repeat review.

## Try it

### Get ready

1. Download the skill ZIP from [v1.2.0](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/tag/v1.2.0) and install its single `aesthetic-print-designer/` folder through your agent client's skill workflow. See [installable folder](#installable-folder).
2. For local image/repeat tools, prepare [the Python runtime](#local-runtime). For the two-page PDF, also install the optional [visual dependencies](skills/aesthetic-print-designer/requirements-visual.txt) in that environment. Image generation needs an available image-generation/editing tool; it is not bundled with the skill. Tool/provider charges, if any, are separate.
3. Attach your own references or artwork that you are authorized to use, then copy one of the requests below. The published sample is for viewing only, not reusable input artwork. See [licensing](#license) before commercial use.

### 1. Explore original directions

**Provide:** reference images and a short product, theme, or collection brief.

```text
Use aesthetic-print-designer to review the attached references and my brief.
Extract the motif grammar, composition, mark-making and palette relationships.
Propose three original print directions with distinct motif hierarchies.
Explain what to retain, reinterpret and avoid copying. Do not generate images yet.
```

**You get:** a reference review and three direction proposals to choose from, not three finished artworks.

### 2. Check an existing repeat tile

**Provide:** the source repeat tile, not a garment mockup or screenshot.

```text
Use aesthetic-print-designer to check the attached repeat tile.
Save the results in outputs/repeat-check/ and leave the source unchanged.
Return the half-offset check, 3 x 3 repeat preview and validation report.
Separate pixel-edge results from visual seam and motif checks.
Identify anything that needs revision; do not repair the artwork yet.
```

**You get:** repeat-check images and a report. If visual inspection cannot be completed, its status stays pending; no sampling or production approval is implied.

### 3. Generate an English print specification sheet

**Provide:** selected artwork and any existing Print ID, version, colour table, or technical metadata. Unknown values may stay pending.

```text
Use aesthetic-print-designer to create an English two-page colour specification
sheet as a PDF for this selected print. Save new files in outputs/print-spec-demo/.
Preserve the artwork and keep each numbered callout matched to one colour-table row.
If I supplied an existing specification, retain its colour values and provenance.
For new extraction, use only a colour library I am authorized to use; without one,
keep source HEX values and mark Pantone matching pending. Do not invent matches.
Keep unknown technical fields pending and set the document status to Draft.
Include: "Artwork shown is for reference only. No other use is permitted."
Do not upload, send, contact a supplier, or start production handoff.
```

**You get:** a local two-page PDF draft with artwork, colour table, technical fields, and notes. The [visual specification workflow](skills/aesthetic-print-designer/references/visual-print-spec-sheet.md) describes the input template and renderer. This format does not replace the production artwork master.

> **Tried it?** Leave a ⭐ if it was useful, or open an issue to share feedback, bugs, or workflow suggestions.

## What it covers

- reference-first aesthetic and rights-risk analysis;
- placement, all-over, border, engineered, panel, directional, half-drop, and four-way print routing;
- motif hierarchy, series identity, quality review, and garment-surface mockups;
- edge lock, half-offset, 3 × 3 preview, bounded seam repair, and truthful repeat status;
- role-locked colour extraction, CIEDE2000 candidate matching, numbered callouts, and one-to-one table mapping;
- standardized Print Specification Sheets for design, merchandising, and pattern-room alignment, with Print ID, source lock, repeat or placement, colour, material/process, file-technical, status, and open-item fields;
- an English two-page visual PDF preset: numbered artwork and source-colour swatches on page 1; an intact colour table, technical fields, notes, and status on page 2;
- default local closure plus an optional Feishu/Lark adapter with full five-column row/cell readback auditing;
- a separate versioned supplier-handoff path with sampling, transfer, receipt, and production-approval gates.

## Two documentation levels

| Output | Primary stage and users | What it does not imply |
|---|---|---|
| **Print Specification Sheet / 印花规格单** | Designer, merchandising, and pattern room; align artwork, colour, scale, repeat or placement, material/process assumptions, and technical fields. | Supplier contact, file transfer, physical sample approval, or production approval. |
| **Production Handoff / 生产交接** | Supplier, sample, and bulk-production stage; add versioned package, authorized transfer, receipt, sample, and approval evidence. | That a pending value or a locally prepared file has been sent, received, or approved. |

Specification status uses `Draft / Design Alignment / Ready for Sampling / Revise`. `Ready for Sampling` records completed design, merchandising, and pattern-room confirmation of the current version, with no unresolved issue blocking sampling. Physical colour/fabric approval and production approval remain separate.

The skill does not treat a generated image as production artwork, a digital colour candidate as physical approval, a selected design as permission to write or send, or a rights-risk screen as legal clearance.

## Visual print specification sheets

Within Print Specification Sheet mode, choose **Colour Specification** for palette alignment or **Full Technical Specification** for broader design-to-production alignment. Choose the format separately: Markdown, editable DOCX using available document tools, or the bundled English PDF renderer. Visual presentation is not a third approval stage.

The PDF preset accepts an existing numbered image and a structured colour table. It preserves the image's aspect ratio, keeps source HEX swatches separate from physical colour standards, and retains candidate provenance and pending fields. It does not generate new artwork, calculate Pantone matches, validate repeats, or approve production. Translating an existing sheet does not require recomputing its colour data.

Copy and fill `skills/aesthetic-print-designer/assets/print-spec-sheet-visual-template.json`, then follow [the visual specification workflow](skills/aesthetic-print-designer/references/visual-print-spec-sheet.md). The optional PDF dependencies are in `requirements-visual.txt`.

The preview preset includes a configurable notice: **“Artwork shown is for reference only. No other use is permitted.”** Preserve any user-required notice; document creation never grants artwork reuse or publication permission. No client artwork, client specification, real colour-library data, or generated client preview is distributed with the template.

## Installable folder

The reusable skill is under `skills/aesthetic-print-designer/`. A release ZIP should contain `aesthetic-print-designer/` as its only top-level folder, including its standalone `LICENSE`, `NOTICE.md`, and `COMMERCIAL-LICENSING.md`. Install or upload that folder/ZIP through the skill workflow supported by your agent client.

## Local runtime

The image and repeat tools require Python 3.10+ and the packages in `requirements.txt`. Use an isolated environment and set `PRINT_DESIGNER_PYTHON` when the entry point cannot use the current interpreter.

Run these commands **inside the extracted `aesthetic-print-designer/` folder**, or inside `skills/aesthetic-print-designer/` in a repository checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export PRINT_DESIGNER_PYTHON="$PWD/.venv/bin/python"
```

For the optional two-page PDF renderer, run this in the same folder and environment:

```bash
.venv/bin/python -m pip install -r requirements-visual.txt
```

The runtime is host-neutral: it does not search private Codex, Hermes, desktop, or user-directory paths.

## Colour-data boundary

No Pantone database, ICC profile, proprietary colour library, or user aesthetic profile is distributed with this repository. Users must supply local data they are authorized to use. Computed matches remain dataset-specific digital candidates pending the appropriate physical reference, intended-fabric strike-off, and standard-light review.

## Optional integrations

Lovart, Feishu/Lark, image-generation tools, and garment-design skills are optional adapters. Core local work remains usable without them. External document writes, uploads, messages, supplier contact, and file transfers require a confirmed target and authorization.

## License

`v1.1.0` and later are released under the Polyform Noncommercial License 1.0.0. Noncommercial use is available under that license; commercial licensing, exclusive licensing, or a rights buyout requires a separate written agreement. See [COMMERCIAL-LICENSING.md](COMMERCIAL-LICENSING.md) or open a [commercial-license issue](https://github.com/jinglong921284-code/aesthetic-print-designer/issues/new?template=commercial-license.yml).

`v1.0.0` and `v1.0.1` remain governed by the MIT License published with those tagged releases. Previously granted rights are not revoked. Pantone and related marks remain the property of their respective owner; see `NOTICE.md` for the colour-data and non-endorsement boundary.

## Release status

The current public release is [v1.2.0](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/tag/v1.2.0). Its installable ZIP contains `aesthetic-print-designer/` as its only top-level folder, including the standalone license, notices, and commercial-contact terms.

See the [release test report](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.2.0/TEST_REPORT-v1.2.0.md) for bundled-tool regression checks. These are program and synthetic-fixture checks, not evidence of physical sampling, customer outcomes, or production approval.
