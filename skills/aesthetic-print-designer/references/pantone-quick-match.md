# Pantone TCX Quick Match

Use this mode only for a chat-level colour direction when the user supplies exact HEX values or colours already sampled from stable interior pixels. It is a deterministic lookup against a named local TCX database, not image segmentation and not a substitute for physical colour review.

## Boundary

- Use it for informal questions such as “这个已取样的颜色接近哪个 Pantone TCX？”
- Do not treat antialiasing, dry-brush transparency, overprint, texture, or ground show-through as separate colours.
- Do not use vision-estimated RGB as an exact sample. If the image still needs semantic colour roles or reliable sampling points, use the formal role-locked workflow.
- Numbered annotation artwork, specification documents, tracked closure, sampling, supplier handoff, and production approval always use `references/pantone-spec-sheet.md` and `python3 scripts/run_print_tool.py colour-spec`.
- This command reads the bundled or user-provided database and writes JSON to stdout only. It must not create or update closure state, files, or external documents.

## Command

```bash
python3 scripts/run_print_tool.py pantone-quick \
  --hex '#F3ECE0' --label '底色' \
  --hex '#3F6F9F' --label '主图色' \
  --top 3
```

The shared entry point selects a dependency-ready Python environment containing NumPy and Pillow; the quick tool then imports the same colour-math functions as the formal colour specification.

Repeat `--hex` for each sampled colour. Labels are optional, but when any `--label` is supplied there must be exactly one label for every HEX value, in the same order.

Database resolution order:

1. `--database <pantone-tcx-rgb.json>`;
2. `PANTONE_TCX_DB`;
3. bundled `assets/colour-libraries/pantone-tcx-rgb.json`.

The bundled fallback resolves relative to the installed skill, not the working directory. Missing bundled data or an invalid explicit override produces an error. The tool never searches a user directory or downloads a database.

The JSON database must be a non-empty array whose entries contain unique `tcx` values and the fields `tcx`, `name`, `hex`, `r`, `g`, and `b`. The result records the database filename, configuration source, entry count, and SHA-256 of the exact database used without exposing its full local path.

The bundled third-party screen approximations, source versions and licenses are documented in `assets/colour-libraries/README.md`. They are not official Pantone measurements. User overrides must come from a source the user is authorized to use. Pantone and related marks belong to their respective owner; this independent skill is not sponsored, endorsed, or certified by Pantone.

## Reading the result

- `status: screen_computed_candidate` means the candidates were computed against the named bundled or user-provided library with sRGB-to-Lab and CIEDE2000.
- Candidates are ordered deterministically by `(delta_e00, tcx)`; `rank: 1` is the nearest digital candidate.
- `physical_review.status` remains `pending` in every result.
- A computed screen candidate is not an approved physical TCX colour, strike-off result, production separation, or bulk-production approval. Confirm against a physical Pantone FHI Cotton TCX reference and the intended fabric before any production decision.
