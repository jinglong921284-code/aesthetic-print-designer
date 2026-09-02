#!/usr/bin/env python3
"""Select a Python runtime for the print tools."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping


IMAGE_DEPENDENCY_PROBE = "import numpy; from PIL import Image"


def _append_unique(paths: list[Path], seen: set[str], value: str | Path | None) -> None:
    if value is None:
        return
    text = str(value).strip()
    if not text:
        return
    path = Path(text).expanduser()
    key = os.path.normcase(os.path.abspath(str(path)))
    if key not in seen:
        seen.add(key)
        paths.append(path)


def candidate_pythons(
    *,
    environ: Mapping[str, str] | None = None,
    current_executable: str | Path | None = None,
) -> list[Path]:
    """Return runtime candidates in stable, de-duplicated priority order."""

    environment = os.environ if environ is None else environ
    executable = sys.executable if current_executable is None else current_executable
    paths: list[Path] = []
    seen: set[str] = set()

    _append_unique(paths, seen, environment.get("PRINT_DESIGNER_PYTHON"))
    _append_unique(paths, seen, executable)

    for variable in ("VIRTUAL_ENV", "CONDA_PREFIX"):
        prefix = environment.get(variable)
        if not prefix:
            continue
        root = Path(prefix).expanduser()
        for relative in (
            "bin/python3",
            "bin/python",
            "Scripts/python.exe",
            "python.exe",
        ):
            _append_unique(paths, seen, root / relative)

    _append_unique(paths, seen, shutil.which("python3"))
    _append_unique(paths, seen, shutil.which("python"))
    return paths


def has_image_dependencies(python: Path) -> bool:
    """Check that a Python executable can import NumPy and Pillow."""

    try:
        result = subprocess.run(
            [str(python), "-c", IMAGE_DEPENDENCY_PROBE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def select_python(
    *,
    require_image_dependencies: bool,
    environ: Mapping[str, str] | None = None,
    current_executable: str | Path | None = None,
) -> Path | None:
    """Return the first existing candidate that satisfies the tool requirements."""

    for python in candidate_pythons(
        environ=environ,
        current_executable=current_executable,
    ):
        if not python.is_file() or not os.access(python, os.X_OK):
            continue
        if require_image_dependencies and not has_image_dependencies(python):
            continue
        return python
    return None
