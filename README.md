# Aesthetic Print Designer

`aesthetic-print-designer` is a portable agent skill for developing original fashion-textile prints from reference analysis through digital validation, colour-callout specifications, selected-print closure, and production-handoff preparation.

## What it covers

- reference-first aesthetic and rights-risk analysis;
- placement, all-over, border, engineered, panel, directional, half-drop, and four-way print routing;
- motif hierarchy, series identity, quality review, and garment-surface mockups;
- edge lock, half-offset, 3 × 3 preview, bounded seam repair, and truthful repeat status;
- role-locked colour extraction, CIEDE2000 candidate matching, numbered callouts, and one-to-one table mapping;
- default local closure plus an optional Feishu/Lark adapter with full five-column row/cell readback auditing;
- versioned local handoff preparation with separate sampling, transfer, receipt, and production-approval gates.

The skill does not treat a generated image as production artwork, a digital colour candidate as physical approval, a selected design as permission to write or send, or a rights-risk screen as legal clearance.

## Installable folder

The reusable skill is under `skills/aesthetic-print-designer/`. A release ZIP should contain `aesthetic-print-designer/` as its only top-level folder, including its standalone `LICENSE` and `NOTICE.md`. Install or upload that folder/ZIP through the skill workflow supported by your agent client.

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

Released under the MIT License. Pantone and related marks remain the property of their respective owner; see `NOTICE.md` for the colour-data and non-endorsement boundary.

## Release status

This repository contains `v1.0.0`, the first public release of Aesthetic Print Designer. The installable ZIP published with the GitHub Release contains `aesthetic-print-designer/` as its only top-level folder.
