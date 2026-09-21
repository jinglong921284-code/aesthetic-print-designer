# Aesthetic Print Designer

`aesthetic-print-designer` is a portable, **end-to-end fashion textile print workflow skill**.

> From visual references to original print design, seamless-repeat validation, colour specification, **production-oriented print specification sheets**, and supplier handoff preparation.

## What it covers

- reference-first aesthetic and rights-risk analysis;
- placement, all-over, border, engineered, panel, directional, half-drop, and four-way print routing;
- motif hierarchy, series identity, quality review, and garment-surface mockups;
- edge lock, half-offset, 3 × 3 preview, bounded seam repair, and truthful repeat status;
- role-locked colour extraction, CIEDE2000 candidate matching, numbered callouts, and one-to-one table mapping;
- standardized Print Specification Sheets for design, merchandising, and pattern-room alignment, with Print ID, source lock, repeat or placement, colour, material/process, file-technical, status, and open-item fields;
- default local closure plus an optional Feishu/Lark adapter with full five-column row/cell readback auditing;
- a separate versioned supplier-handoff path with sampling, transfer, receipt, and production-approval gates.

## Two documentation levels

| Output | Primary stage and users | What it does not imply |
|---|---|---|
| **Print Specification Sheet / 印花规格单** | Designer, merchandising, and pattern room; align artwork, colour, scale, repeat or placement, material/process assumptions, and technical fields. | Supplier contact, file transfer, physical sample approval, or production approval. |
| **Production Handoff / 生产交接** | Supplier, sample, and bulk-production stage; add versioned package, authorized transfer, receipt, sample, and approval evidence. | That a pending value or a locally prepared file has been sent, received, or approved. |

Specification status uses `Draft / Design Alignment / Ready for Sampling / Revise`. `Ready for Sampling` records completed design, merchandising, and pattern-room confirmation of the current version, with no unresolved issue blocking sampling. Physical colour/fabric approval and production approval remain separate.

The skill does not treat a generated image as production artwork, a digital colour candidate as physical approval, a selected design as permission to write or send, or a rights-risk screen as legal clearance.

## Installable folder

The reusable skill is under `skills/aesthetic-print-designer/`. A release ZIP should contain `aesthetic-print-designer/` as its only top-level folder, including its standalone `LICENSE`, `NOTICE.md`, and `COMMERCIAL-LICENSING.md`. Install or upload that folder/ZIP through the skill workflow supported by your agent client.

## Local runtime

The image and repeat tools require Python 3.10+ and the packages in `requirements.txt`. Use an isolated environment and set `PRINT_DESIGNER_PYTHON` when the entry point cannot use the current interpreter.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/aesthetic-print-designer/requirements.txt
export PRINT_DESIGNER_PYTHON="$PWD/.venv/bin/python"
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

The current public release is `v1.1.0`. Its installable ZIP contains `aesthetic-print-designer/` as its only top-level folder, including the standalone license, notices, and commercial-contact terms.
