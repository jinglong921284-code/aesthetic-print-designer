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

        six_colours = [
            ("底色", "象牙底", (242, 236, 224), "TEST-0101"),
            ("主图色", "蓝色主体", (63, 111, 159), "TEST-0102"),
            ("强调色", "橙色星点", (223, 115, 39), "TEST-0103"),
            ("叶片色", "绿色叶片", (94, 145, 109), "TEST-0104"),
            ("花瓣色", "玫瑰花瓣", (182, 86, 117), "TEST-0105"),
            ("描边色", "深色描边", (80, 69, 91), "TEST-0106"),
        ]
        six_image = np.zeros((72, 120, 3), dtype=np.uint8)
        six_roles = []
        six_library_rows = ["name,tcx,hex,r,g,b"]
        for index, (role, element, rgb, tcx) in enumerate(six_colours, start=1):
            start_x = (index - 1) * 20
            six_image[:, start_x : start_x + 20] = rgb
            six_roles.append(
                {
                    "id": index,
                    "role": role,
                    "element": element,
                    "sample_points": [[start_x + 10, 36]],
                }
            )
            hex_value = "#%02X%02X%02X" % rgb
            six_library_rows.append(
                f"'Fixture {index}',{tcx},{hex_value},{rgb[0]},{rgb[1]},{rgb[2]}"
            )
        six_image_path = root / "six-colour-artwork.png"
        Image.fromarray(six_image, mode="RGB").save(six_image_path)
        six_roles_path = root / "six-roles.json"
        six_roles_path.write_text(
            json.dumps({"roles": six_roles}, ensure_ascii=False),
            encoding="utf-8",
        )
        six_library_path = root / "six-pantone.csv"
        six_library_path.write_text("\n".join(six_library_rows) + "\n", encoding="utf-8")
        six_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--image",
                str(six_image_path),
                "--roles",
                str(six_roles_path),
                "--pantone-csv",
                str(six_library_path),
                "--out-dir",
                str(root / "out-six"),
            ],
            text=True,
            capture_output=True,
        )
        assert six_result.returncode == 0, six_result.stdout + six_result.stderr
        six_payload = json.loads(six_result.stdout)["data"]
        assert [role["id"] for role in six_payload["roles"]] == list(range(1, 7))
        assert [role["pantone_tcx"] for role in six_payload["roles"]] == [
            colour[3] for colour in six_colours
        ]
        assert Path(six_payload["annotation_image"]).is_file()
        assert "| 6 | 描边色 | 深色描边 |" in Path(six_payload["markdown_spec"]).read_text(
            encoding="utf-8"
        )
    print("colour role spec tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
