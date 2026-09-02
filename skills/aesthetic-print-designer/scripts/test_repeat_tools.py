#!/usr/bin/env python3
"""Minimal functional tests for the repeat validation and finalization tools."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


SCRIPTS = Path(__file__).parent


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="print-repeat-tests-") as temp:
        root = Path(temp)

        passing = np.zeros((32, 32, 3), dtype=np.uint8)
        passing[:, :, 0] = np.arange(32, dtype=np.uint8)[None, :] * 8
        passing[:, -1] = passing[:, 0]
        passing[-1] = passing[0]
        passing_path = root / "passing.png"
        Image.fromarray(passing).save(passing_path)

        failing = passing.copy()
        failing[:, -1, 1] = 20
        failing_path = root / "failing.png"
        Image.fromarray(failing).save(failing_path)

        passing_run = run(
            str(SCRIPTS / "validate_repeat.py"),
            str(passing_path),
            "--out-dir",
            str(root / "passing-report"),
        )
        assert passing_run.returncode == 0, passing_run.stderr or passing_run.stdout
        passing_report = json.loads(passing_run.stdout)
        assert passing_report["edge_lock_pass"] is True
        assert passing_report["overall_status"] == "pending_visual_review"
        assert Path(passing_report["offset_check"]).is_file()
        assert Path(passing_report["tile_3x3_check"]).is_file()

        visual_pass_run = run(
            str(SCRIPTS / "validate_repeat.py"),
            str(passing_path),
            "--out-dir",
            str(root / "visual-pass-report"),
            "--visual-status",
            "pass",
            "--visual-notes",
            "No seam, grid, track, or repeated focal point.",
        )
        assert visual_pass_run.returncode == 0
        visual_pass_report = json.loads(visual_pass_run.stdout)
        assert (
            visual_pass_report["overall_status"]
            == "digital_seamless_repeat_passed"
        )

        visual_revise_run = run(
            str(SCRIPTS / "validate_repeat.py"),
            str(passing_path),
            "--out-dir",
            str(root / "visual-revise-report"),
            "--visual-status",
            "revise",
            "--visual-notes",
            "A repeated vertical track remains visible.",
        )
        assert visual_revise_run.returncode == 4
        assert (
            json.loads(visual_revise_run.stdout)["overall_status"]
            == "visual_revise"
        )

        failing_run = run(
            str(SCRIPTS / "validate_repeat.py"),
            str(failing_path),
            "--out-dir",
            str(root / "failing-report"),
        )
        assert failing_run.returncode == 2, failing_run.stderr or failing_run.stdout
        failing_report = json.loads(failing_run.stdout)
        assert failing_report["edge_lock_pass"] is False
        assert failing_report["overall_status"] == "edge_lock_failed"

        finalized_path = root / "finalized.png"
        finalized_run = run(
            str(SCRIPTS / "finalize_repeat.py"),
            str(failing_path),
            "--output",
            str(finalized_path),
        )
        assert finalized_run.returncode == 0, finalized_run.stderr or finalized_run.stdout
        finalized = np.asarray(Image.open(finalized_path).convert("RGB"))
        assert np.array_equal(finalized[:, 0], finalized[:, -1])
        assert np.array_equal(finalized[0], finalized[-1])

    print("repeat tool tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
