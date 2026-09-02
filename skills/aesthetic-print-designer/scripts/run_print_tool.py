#!/usr/bin/env python3
"""Run print-pipeline tools with a compatible Python runtime."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from python_runtime import select_python


TOOLS = {
    "closure": ("selection_closure.py", False),
    "seam-guard": ("seam_repair_guard.py", True),
    "colour-spec": ("colour_role_spec.py", True),
    "pantone-quick": ("pantone_quick_match.py", True),
    "document-audit": ("document_consistency_audit.py", False),
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
        print(
            f"Usage: {Path(sys.argv[0]).name} <{'|'.join(TOOLS)}> [tool arguments...]",
            file=sys.stderr,
        )
        return 2
    script_name, needs_images = TOOLS[sys.argv[1]]
    script = Path(__file__).with_name(script_name)
    python = select_python(require_image_dependencies=needs_images)
    if python is not None:
        return subprocess.run(
            [str(python), str(script), *sys.argv[2:]],
            check=False,
        ).returncode
    print(
        "No usable Python environment found. Install requirements.txt in a Python "
        "3.10+ environment or set PRINT_DESIGNER_PYTHON to that interpreter. "
        "Image tools require Pillow and NumPy.",
        file=sys.stderr,
    )
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
