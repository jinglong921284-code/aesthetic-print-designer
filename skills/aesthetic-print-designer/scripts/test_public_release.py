#!/usr/bin/env python3
"""Static checks for a portable, de-identified public skill package."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    forbidden = (
        "/" + "Users" + "/",
        "." + "codex" + "/",
        "." + "hermes" + "/",
        "Desktop" + "/",
        "19" + "mm素绉缎",
        "19" + "mm silk",
    )
    ignored_suffixes = {".pyc", ".pyo"}
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        assert "__pycache__" not in relative.parts, relative
        assert path.name != ".DS_Store", relative
        assert path.suffix not in ignored_suffixes, relative
        if not path.is_file():
            continue
        if path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json", ".txt"}:
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                assert marker not in text, f"private or host-specific marker {marker!r} in {relative}"

    colour_data = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".csv", ".icc", ".icm"}
        and "test" not in path.name.lower()
    ]
    assert not colour_data, f"unexpected colour-library or profile data: {colour_data}"

    template = json.loads((ROOT / "assets/colour-role-template.json").read_text(encoding="utf-8"))
    for role in template["roles"]:
        assert role["element"] == ""
        assert role["sample_points"] == []
        assert role["source_hex"] is None

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert requirements == ["numpy>=1.24,<3", "Pillow>=10.1,<13"]

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert license_text.startswith("# Polyform Noncommercial License 1.0.0\n")
    assert "https://polyformproject.org/licenses/noncommercial/1.0.0" in license_text
    assert "Required Notice: Copyright (c) 2026 Lialynn." in license_text
    assert "Required Notice: Commercial licensing, exclusive licensing, or rights-buyout inquiries:" in license_text
    assert "MIT License" not in license_text

    commercial_terms = (ROOT / "COMMERCIAL-LICENSING.md").read_text(encoding="utf-8")
    assert "v1.0.0" in commercial_terms and "v1.0.1" in commercial_terms
    assert "remain governed by their original MIT terms" in commercial_terms
    assert "issues/new?template=commercial-license.yml" in commercial_terms
    print("public release static tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
