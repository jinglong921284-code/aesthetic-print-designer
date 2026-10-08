# Bundled digital colour references

These third-party datasets are screen approximations, not official Pantone measurements or an official Pantone-licensed database. Keep TCX textile references separate from Solid Coated / Uncoated references. A digital match is a candidate only; verify against the appropriate physical reference and substrate before production.

| File | Contents | Published source / declared license |
|---|---|---|
| `pantone-tcx-full.json` | 2,800 TCX names, codes and HEX values | [pantone-tcx 2.2.4](https://www.npmjs.com/package/pantone-tcx/v/2.2.4), ISC |
| `pantone-tcx-rgb.json` | Same TCX records, with derived RGB channels; quick-match default | Same source |
| `pantone-tcx.csv` | Same TCX records as CSV, regenerated with standard CSV quoting to preserve apostrophes in names; colour-spec default | Same source |
| `pantone-solid-all.json` | 1,831 Coated, 1,341 Uncoated and 45 colour-of-year aliases | [pantone-table 1.0.0-rc1](https://www.npmjs.com/package/pantone-table/v/1.0.0-rc1), MIT |
| `pantone-colours-com.json` | 907 `{code, hex}` records; character-index representation repaired without changing values | [pantone-colors 1.0.3](https://www.npmjs.com/package/pantone-colors/v/1.0.3), declares MIT; no standalone license shipped upstream |
| `pantone-chromonym.json` | 907 Coated references, for on-screen identification only | [chromonym 3.5.0](https://www.npmjs.com/package/chromonym/v/3.5.0), MIT; palette derived from color_library 0.0.2 |

Upstream license texts, attribution metadata and the relevant chromonym notice are retained in `licenses/`. Third-party materials retain their upstream terms and are not relicensed under this skill's Polyform Noncommercial license. Package license declarations do not imply Pantone endorsement or certification.

The original collection was dated 2026-06-16. Bundled values were checked against the named npm releases on 2026-09-28. `manifest.json` records packaged-file SHA-256 values. JSON / CSV conversion and RGB derivation do not add physical measurement accuracy. Solid and chromonym references are included for lookup only; the bundled matching tools use TCX and do not mix these systems.

Run from the skill folder:

```bash
python3 scripts/run_print_tool.py pantone-quick --hex '#F3ECE0' --top 3
python3 scripts/run_print_tool.py colour-spec --image artwork.png --roles roles.json --out-dir output
```

Use `--database` (or `PANTONE_TCX_DB`) to override the quick-match JSON, and `--pantone-csv` to override the specification CSV. An invalid explicit input fails rather than falling back. Existing specifications keep their original colour values and provenance unless recalculation is requested.
