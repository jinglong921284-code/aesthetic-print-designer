# Worked example: three HEX colours to TCX screen candidates

[Back to the getting-started guide](getting-started.md) · [Raw tool output](examples/first-colour-match.json)

This records a run of the **v1.3.0 colour tool** in the maintainer's environment on 2026-09-29. It verifies digital colour matching, not first-user installation or an end-to-end print-generation workflow.

## Input

Three exact colour values: ground `#F3ECE0`, main motif `#3F6F9F` and accent `#DF7327`. The exercise uses no client images or visually estimated colour samples.

## Execution

After installing dependencies, run this from the skill folder:

```bash
.venv/bin/python scripts/run_print_tool.py pantone-quick \
  --hex '#F3ECE0' --label 'Ground' \
  --hex '#3F6F9F' --label 'Main motif' \
  --hex '#DF7327' --label 'Accent' --top 1
```

On Windows, use `.venv\Scripts\python.exe` as shown in the guide and put the arguments on one line.

The maintainer used an existing compatible Python environment rather than creating a new .venv. The tool automatically loaded the bundled `pantone-tcx-rgb.json` library with 2,800 entries, then applied sRGB-to-Lab conversion and CIEDE2000 nearest-colour matching. Library SHA-256:

```text
5e5ac131379a2a934e4291de2f11393e9c7ebcb490b079677ca427292423b7a5
```

## Output

| Role | Source HEX | Candidate code | Candidate name | Candidate HEX | Delta E 2000 |
|---|---|---|---|---|---|
| Ground | #F3ECE0 | 11-0103 | Egret | #F3ECE0 | 0.0000 |
| Main motif | #3F6F9F | 18-4141 | Campanula | #3272AF | 2.4062 |
| Accent | #DF7327 | 16-1255 | Russet Orange | #E47127 | 1.4313 |

The result status is `screen_computed_candidate`; `physical_review.status` remains `pending`. The attached JSON was saved from actual command output, with no manually entered candidates. The matching tool returns results to the terminal without creating a specification or external document; the maintainer saved this output separately for the example.

## What this verifies

The tool can load the bundled library and return reproducible digital candidates for three exact inputs. No image-generation service or separate colour-library download is needed; local Python dependencies are still required.

This run does not verify automatic skill selection by a client, first-user installation, reference-image analysis, generated-artwork quality, physical colour accuracy or fabric sampling. A full design case study would require shareable references and original artwork, with the actual direction choices, revisions and outputs recorded.
