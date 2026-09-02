#!/usr/bin/env python3
"""Functional tests for the seam-repair protection tool."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


SCRIPT = Path(__file__).with_name("seam_repair_guard.py")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="seam-guard-test-") as temp:
        root = Path(temp)
        tile = np.zeros((40, 40, 3), dtype=np.uint8)
        tile[:, :, 0] = np.arange(40, dtype=np.uint8)[None, :] * 5
        tile[:, :, 1] = np.arange(40, dtype=np.uint8)[:, None] * 5
        tile_path = root / "tile.png"
        Image.fromarray(tile, mode="RGB").save(tile_path)

        prepared = run("prepare", "--tile", str(tile_path), "--out-dir", str(root / "guard"), "--band-px", "10")
        assert prepared.returncode == 0, prepared.stdout + prepared.stderr
        manifest = Path(json.loads(prepared.stdout)["data"]["manifest"])
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        half_offset = np.asarray(Image.open(manifest_data["half_offset"]).convert("RGB"))
        edited = np.full_like(half_offset, (20, 210, 90))
        edited_path = root / "edited.png"
        Image.fromarray(edited, mode="RGB").save(edited_path)

        output = root / "guarded.png"
        applied = run("apply", "--manifest", str(manifest), "--edited", str(edited_path), "--output", str(output), "--feather-px", "2")
        assert applied.returncode == 0, applied.stdout + applied.stderr
        report = json.loads(applied.stdout)["data"]
        assert report["status"] == "protected_repair_ready"
        assert report["outside_mask_changed_pixels"] == 0
        assert report["inside_mask_changed_pixels"] > 0
        guarded = np.asarray(Image.open(output).convert("RGB"))
        mask = np.asarray(Image.open(manifest_data["central_cross_mask"]).convert("L")) > 0
        assert np.array_equal(guarded[~mask], half_offset[~mask])
        assert Path(report["difference_heatmap"]).is_file()

    print("seam repair guard tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
