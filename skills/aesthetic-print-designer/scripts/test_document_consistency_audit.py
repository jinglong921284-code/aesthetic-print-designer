#!/usr/bin/env python3
"""Functional tests for structural Feishu print-document consistency auditing."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("document_consistency_audit.py")


def run(state: Path, readback: Path, out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--state", str(state), "--readback-file", str(readback), "--out-dir", str(out_dir)],
        text=True,
        capture_output=True,
    )


def mapping_table(rows: list[str]) -> str:
    header = (
        "<tr><th><strong>ID</strong><br> / 标注</th><th><span>元</span>素</th>"
        "<th>源图<br><code>HEX</code></th><th>Pantone<br><span>TCX</span></th>"
        "<th><em>色名</em> /<br> ΔE00</th></tr>"
    )
    return '<table class="colour-map">' + header + "".join(rows) + "</table>"


def role_one_row(role_id: int = 1) -> str:
    return (
        f"<tr><td><strong>{role_id}</strong></td>"
        "<td><span>象牙&nbsp;&amp; 底</span></td>"
        "<td><code>#F3ECE0</code></td>"
        "<td><span>TEST-0001</span> TCX</td>"
        "<td><em>Fixture Ivory</em> / 0.42</td></tr>"
    )


def role_two_row(role_id: int = 2, element: str = "蓝色主体") -> str:
    return (
        f"<tr><td>{role_id}</td><td><span>{element}</span></td>"
        "<td>#3F6F9F</td><td>TEST-0002 TCX</td><td>Fixture Blue / 1.10</td></tr>"
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="doc-audit-test-") as temp:
        root = Path(temp)
        tile = root / "final.png"
        tile.write_bytes(b"final")
        tile_sha = hashlib.sha256(tile.read_bytes()).hexdigest()
        colour_report = root / "colour.json"
        colour_report.write_text(
            json.dumps(
                {
                    "status": "colour_role_spec_ready",
                    "roles": [
                        {
                            "id": 1,
                            "element": "象牙 & 底",
                            "source_hex": "#F3ECE0",
                            "pantone_tcx": "TEST-0001",
                            "pantone_name": "Fixture Ivory",
                            "delta_e00": 0.42,
                        },
                        {
                            "id": 2,
                            "element": "蓝色主体",
                            "source_hex": "#3F6F9F",
                            "pantone_tcx": "TEST-0002",
                            "pantone_name": "Fixture Blue",
                            "delta_e00": 1.10,
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        state = {
            "print_id": "TST-01",
            "stages": {
                "final_repeat_validation": {"evidence": [{"input": {"sha256": tile_sha}}]},
                "colour_spec": {"evidence": [{"report": {"path": str(colour_report)}}]},
            },
        }
        state_path = root / "state.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")

        missing_cli = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--state",
                str(state_path),
                "--doc-url",
                "https://example.invalid/docx/test",
                "--out-dir",
                str(root / "missing-cli"),
            ],
            text=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(root)},
        )
        assert missing_cli.returncode == 3
        assert "requires lark-cli" in json.loads(missing_cli.stdout)["error"]
        images = "".join(
            [
                '<img name="TST-01_selected.png"/>',
                '<img name="TST-01_mockup.png"/>',
                '<img name="TST-01_配色编号标注.png"/>',
            ]
        )
        unrelated_table = (
            "<table><tr><th>项目</th><th>内容</th></tr>"
            "<tr><td>1</td><td>unrelated technical note</td></tr></table>"
        )
        prefix = (
            f'<fragment><h2>TST-01｜Test</h2>{images}'
            f'<p>digital_seamless_repeat_passed {tile_sha}</p>{unrelated_table}'
        )
        content = prefix + mapping_table([role_one_row(), role_two_row()]) + "</fragment>"
        readback = {
            "ok": True,
            "identity": "user",
            "data": {
                "document": {
                    "document_id": "doc",
                    "revision_id": 12,
                    "content": content,
                }
            },
        }
        readback_path = root / "readback.json"

        def audit(case: str, case_content: str) -> tuple[subprocess.CompletedProcess[str], dict]:
            readback["data"]["document"]["content"] = case_content
            readback_path.write_text(json.dumps(readback), encoding="utf-8")
            result = run(state_path, readback_path, root / case)
            return result, json.loads(result.stdout)["data"]

        passed, passed_payload = audit("pass", content)
        assert passed.returncode == 0, passed.stdout + passed.stderr
        assert passed_payload["status"] == "document_consistency_passed"
        assert passed_payload["counts"]["tables"] == 2
        assert passed_payload["counts"]["colour_mapping_candidates"] == 1
        assert passed_payload["counts"]["colour_mapping_rows"] == 2
        assert all(item["passed"] for item in passed_payload["checks"])

        split_hex_table = mapping_table(
            [
                (
                    "<tr><td>1</td><td>象牙 &amp; 底</td><td>#F3<br>ECE0</td>"
                    "<td>TEST-0001 TCX</td><td>Fixture Ivory / 0.42</td></tr>"
                ),
                role_two_row(),
            ]
        )
        split_hex_result, split_hex_payload = audit(
            "split-hex", prefix + split_hex_table + "</fragment>"
        )
        assert split_hex_result.returncode == 5
        assert any(
            "Role 1" in error and "source_hex column mismatch" in error
            for error in split_hex_payload["errors"]
        )

        wrong_delta_table = mapping_table(
            [
                (
                    "<tr><td>1</td><td>象牙 &amp; 底</td><td>#F3ECE0</td>"
                    "<td>TEST-0001 TCX</td><td>Fixture Ivory / 99.99</td></tr>"
                ),
                role_two_row(),
            ]
        )
        wrong_delta_result, wrong_delta_payload = audit(
            "wrong-delta", prefix + wrong_delta_table + "</fragment>"
        )
        assert wrong_delta_result.returncode == 5
        assert any(
            "Role 1" in error and "pantone_name column mismatch" in error
            for error in wrong_delta_payload["errors"]
        )

        missing_delta_table = mapping_table(
            [
                (
                    "<tr><td>1</td><td>象牙 &amp; 底</td><td>#F3ECE0</td>"
                    "<td>TEST-0001 TCX</td><td>Fixture Ivory</td></tr>"
                ),
                role_two_row(),
            ]
        )
        missing_delta_result, missing_delta_payload = audit(
            "missing-delta", prefix + missing_delta_table + "</fragment>"
        )
        assert missing_delta_result.returncode == 5
        assert any(
            "Role 1" in error and "pantone_name column mismatch" in error
            for error in missing_delta_payload["errors"]
        )

        swapped_columns_table = mapping_table(
            [
                (
                    "<tr><td>1</td><td>象牙 &amp; 底</td><td>TEST-0001 TCX</td>"
                    "<td>#F3ECE0</td><td>Fixture Ivory / 0.42</td></tr>"
                ),
                role_two_row(),
            ]
        )
        swapped_columns_result, swapped_columns_payload = audit(
            "swapped-columns", prefix + swapped_columns_table + "</fragment>"
        )
        assert swapped_columns_result.returncode == 5
        assert any(
            "Role 1" in error and "source_hex column mismatch" in error
            for error in swapped_columns_payload["errors"]
        )
        assert any(
            "Role 1" in error and "pantone_tcx column mismatch" in error
            for error in swapped_columns_payload["errors"]
        )

        squeezed_table = mapping_table(
            [
                (
                    "<tr><td>1</td><td>象牙 &amp; 底 #F3ECE0 TEST-0001 TCX Fixture Ivory</td>"
                    "<td></td><td></td><td></td></tr>"
                ),
                role_two_row(),
            ]
        )
        squeezed_result, squeezed_payload = audit(
            "squeezed-cell", prefix + squeezed_table + "</fragment>"
        )
        assert squeezed_result.returncode == 5
        squeezed_errors = squeezed_payload["errors"]
        assert any("element column mismatch" in error for error in squeezed_errors)
        assert any("source_hex column mismatch" in error for error in squeezed_errors)
        assert any("pantone_tcx column mismatch" in error for error in squeezed_errors)
        assert any("pantone_name column mismatch" in error for error in squeezed_errors)

        reversed_content = prefix + mapping_table([role_two_row(), role_one_row()]) + "</fragment>"
        reversed_result, reversed_payload = audit("reversed", reversed_content)
        assert reversed_result.returncode == 5
        assert any("row order" in error for error in reversed_payload["errors"])

        swapped_values = mapping_table(
            [
                (
                    "<tr><td>1</td><td>象牙 &amp; 底</td><td>#3F6F9F</td>"
                    "<td>TEST-0002</td><td>Fixture Ivory</td></tr>"
                ),
                (
                    "<tr><td>2</td><td>蓝色主体</td><td>#F3ECE0</td>"
                    "<td>TEST-0001</td><td>Fixture Blue</td></tr>"
                ),
            ]
        )
        swapped_result, swapped_payload = audit(
            "swapped-values", prefix + swapped_values + "</fragment>"
        )
        assert swapped_result.returncode == 5
        assert any(
            "Role 1" in error and "source_hex column mismatch" in error
            for error in swapped_payload["errors"]
        )
        assert any(
            "Role 2" in error and "pantone_tcx column mismatch" in error
            for error in swapped_payload["errors"]
        )

        duplicate_content = prefix + mapping_table(
            [role_one_row(), role_two_row(role_id=1)]
        ) + "</fragment>"
        duplicate_result, duplicate_payload = audit("duplicate", duplicate_content)
        assert duplicate_result.returncode == 5
        assert any("Duplicate colour mapping ID 1" in error for error in duplicate_payload["errors"])
        assert any("Missing colour mapping row for role ID 2" in error for error in duplicate_payload["errors"])

        wrong_element_content = prefix + mapping_table(
            [role_one_row(), role_two_row(element="错误元素")]
        ) + "</fragment>"
        wrong_element_result, wrong_element_payload = audit(
            "wrong-element", wrong_element_content
        )
        assert wrong_element_result.returncode == 5
        assert any(
            "Role 2" in error and "element column mismatch" in error
            for error in wrong_element_payload["errors"]
        )

        bad_header = (
            '<table class="colour-map"><tr><th>标注</th><th>元素</th>'
            "<th>源图 HEX</th><th>Pantone TCX</th><th>Pantone TCX</th></tr>"
            + role_one_row()
            + role_two_row()
            + "</table>"
        )
        bad_header_result, bad_header_payload = audit(
            "bad-header", prefix + bad_header + "</fragment>"
        )
        assert bad_header_result.returncode == 5
        assert any(
            "missing required columns: 色名" in error
            for error in bad_header_payload["errors"]
        )
        assert any(
            "Pantone TCX must be unique" in error
            for error in bad_header_payload["errors"]
        )

        missing_table_result, missing_table_payload = audit(
            "missing-table", prefix + "</fragment>"
        )
        assert missing_table_result.returncode == 5
        assert any(
            "Expected exactly one colour mapping table" in error
            for error in missing_table_payload["errors"]
        )

        failed, failed_payload = audit(
            "stale", content.replace("digital_seamless_repeat_passed", "edge_lock_failed")
        )
        assert failed.returncode == 5, failed.stdout + failed.stderr
        errors = failed_payload["errors"]
        assert any("Stale" in error for error in errors)
        assert any("final status" in error for error in errors)
    print("document consistency audit tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
