# Portable Runtime Setup

The local image and repeat tools require Python 3.10 or newer plus the packages listed in `requirements.txt`.

Create any isolated environment you control, install the requirements, and either run the entry points with that environment's Python or set `PRINT_DESIGNER_PYTHON` to its executable. The runtime selector checks, in order:

1. `PRINT_DESIGNER_PYTHON`;
2. the interpreter currently running the entry point;
3. interpreters exposed by `VIRTUAL_ENV` or `CONDA_PREFIX`;
4. `python3` and `python` on `PATH`.

Do not depend on a host-specific Codex, Hermes, operating-system, or user-directory path. If no candidate can import both NumPy and Pillow, the entry point stops with setup guidance instead of silently choosing another project environment.

## Colour-library boundary

This skill does not include, sublicense, or download a Pantone database. Supply `--database` or `PANTONE_TCX_DB` for quick JSON matching, and `--pantone-csv` for the formal role-locked specification. The user is responsible for providing a local data source they are authorized to use.

Computed results are candidates derived from the supplied digital data. They are not official Pantone certification, physical colour approval, strike-off approval, or production approval. Confirm the colour system, substrate, process, physical reference, intended fabric, and standard-light review for each project.

## Optional integrations

Lovart, Feishu/Lark, image-generation tools, and garment-design skills are optional adapters. Use one only when it is available, the user placed it in scope, and any external read or write has a confirmed target and authorization. The local concept, repeat, colour-report, and handoff-preparation paths must remain usable without those adapters.
