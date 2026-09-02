#!/usr/bin/env python3
"""Functional tests for the role-locked Pantone specification tool."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from colour_role_spec import delta_e_2000


SCRIPT = Path(__file__).with_name("colour_role_spec.py")


def main() -> int:
    assert abs(
        delta_e_2000((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485)) - 2.0425
    ) < 0.0002
    with tempfile.TemporaryDirectory(prefix="colour-role-test-") as temp:
        root = Path(temp)
        image = np.full((80, 80, 3), (242, 236, 224), dtype=np.uint8)
        image[:, 40:] = (63, 111, 159)
        image[5:13, 5:13] = (223, 115, 39)
        image_path = root / "artwork.png"
        Image.fromarray(image, mode="RGB").save(image_path)
        roles = {
            "roles": [
                {"id": 1, "role": "主底色", "element": "象牙底", "sample_points": [[20, 40]]},
                {"id": 2, "role": "主图色", "element": "蓝色主体", "sample_points": [[60, 40]]},
                {"id": 3, "role": "强调色", "element": "橙色星点", "sample_points": [[8, 8]]},
            ]
        }
        roles_path = root / "roles.json"
        roles_path.write_text(json.dumps(roles, ensure_ascii=False), encoding="utf-8")
        csv_path = root / "pantone.csv"
        csv_path.write_text(
            "name,tcx,hex,r,g,b\n'Fixture Ivory',TEST-0001,#F3ECE0,243,236,224\n'Fixture Blue',TEST-0002,#3F6F9F,63,111,159\n'Fixture Orange',TEST-0003,#DF7327,223,115,39\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--image", str(image_path), "--roles", str(roles_path), "--pantone-csv", str(csv_path), "--out-dir", str(root / "out")],
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)["data"]
        assert payload["status"] == "colour_role_spec_ready"
        assert payload["dropped_roles"] == []
        assert len(payload["roles"]) == 3
        assert payload["roles"][2]["approx_pixel_share_percent"] > 0
        assert [role["pantone_tcx"] for role in payload["roles"]] == [
            "TEST-0001",
            "TEST-0002",
            "TEST-0003",
        ]
        assert Path(payload["annotation_image"]).is_file()
        assert Path(payload["markdown_spec"]).is_file()
        assert payload["physical_review"]["status"] == "pending"
        assert payload["fabric"] is None
        assert "confirmed fabric specification" in payload["physical_review"]["requirements"]

        fabric_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--image",
                str(image_path),
                "--roles",
                str(roles_path),
                "--pantone-csv",
                str(csv_path),
                "--out-dir",
                str(root / "out-fabric"),
                "--fabric",
                "confirmed test fabric",
            ],
            text=True,
            capture_output=True,
        )
        assert fabric_result.returncode == 0, fabric_result.stdout + fabric_result.stderr
        fabric_payload = json.loads(fabric_result.stdout)["data"]
        assert fabric_payload["fabric"] == "confirmed test fabric"
        assert "confirmed test fabric" in fabric_payload["physical_review"]["requirements"]

        incomplete_template = Path(__file__).resolve().parents[1] / "assets/colour-role-template.json"
        incomplete = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--image",
                str(image_path),
                "--roles",
                str(incomplete_template),
                "--pantone-csv",
                str(csv_path),
                "--out-dir",
                str(root / "out-incomplete"),
            ],
            text=True,
            capture_output=True,
        )
        assert incomplete.returncode == 3
        assert "role and element labels" in json.loads(incomplete.stdout)["error"]

        duplicate_csv = root / "duplicate-pantone.csv"
        duplicate_csv.write_text(
            "name,tcx,hex,r,g,b\n'One',TEST-0001,#F3ECE0,243,236,224\n'Two',TEST-0001,#3F6F9F,63,111,159\n",
            encoding="utf-8",
        )
        duplicate_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--image",
                str(image_path),
                "--roles",
                str(roles_path),
                "--pantone-csv",
                str(duplicate_csv),
                "--out-dir",
                str(root / "out-duplicate"),
            ],
            text=True,
            capture_output=True,
        )
        assert duplicate_result.returncode == 3
        assert "duplicate tcx" in json.loads(duplicate_result.stdout)["error"]
    print("colour role spec tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
