#!/usr/bin/env python3
"""Run repeat tools with a Python environment that has their dependencies."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from python_runtime import select_python


TOOLS = {
    "validate": "validate_repeat.py",
    "finalize": "finalize_repeat.py",
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
        choices = "|".join(TOOLS)
        print(
            f"Usage: {Path(sys.argv[0]).name} <{choices}> [tool arguments...]",
            file=sys.stderr,
        )
        return 2

    tool = Path(__file__).with_name(TOOLS[sys.argv[1]])
    python = select_python(require_image_dependencies=True)
    if python is not None:
        return subprocess.run(
            [str(python), str(tool), *sys.argv[2:]],
            check=False,
        ).returncode

    print(
        "No usable Python environment found. The repeat tools require Pillow and NumPy. "
        "Install requirements.txt in a Python 3.10+ environment or set "
        "PRINT_DESIGNER_PYTHON to a Python executable containing both packages.",
        file=sys.stderr,
    )
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
