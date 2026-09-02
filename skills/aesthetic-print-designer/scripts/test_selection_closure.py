#!/usr/bin/env python3
"""Functional test for the explicit-selection closure state machine."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("selection_closure.py")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def write(path: Path, value: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


def validation_report(root: Path, name: str, status: str) -> Path:
    tile = write(root / f"{name}.png", f"tile-{name}")
    offset = write(root / f"{name}-offset.png", "offset")
    tiled = write(root / f"{name}-3x3.png", "3x3")
    report = {
        "input": str(tile),
        "edge_lock_pass": status == "digital_seamless_repeat_passed",
        "visual_review": {
            "status": "pass" if status == "digital_seamless_repeat_passed" else "revise",
            "notes": "test evidence",
        },
        "overall_status": status,
        "offset_check": str(offset),
        "tile_3x3_check": str(tiled),
    }
    path = root / f"{name}-validation.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="selection-closure-test-") as temp:
        root = Path(temp)
        project = root / "project"
        source = write(root / "selected.png", "selected-source")
        template = write(root / "garment.png", "garment-template")
        mockup = write(root / "mockup.png", "mockup")
        colour = write(root / "colour-spec.json", "{}")
        annotation = write(root / "colour-annotation.png", "annotation")

        init = run(
            "init",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--name",
            "Test Print",
            "--source",
            str(source),
            "--approval-phrase",
            "这张定了",
            "--category",
            "sleepwear",
            "--garment-template",
            str(template),
            "--document-mode",
            "feishu",
            "--feishu-doc",
            "https://example.feishu.cn/docx/testdoc",
        )
        assert init.returncode == 0, init.stdout + init.stderr
        assert json.loads(init.stdout)["data"]["next_action"] == "garment_mockup"

        different_source = write(root / "different-selected.png", "different-source")
        duplicate = run(
            "init",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--name",
            "Test Print",
            "--source",
            str(different_source),
            "--approval-phrase",
            "这张定了",
        )
        assert duplicate.returncode == 3
        assert "different selected source" in duplicate.stdout

        blocked = run(
            "record-file",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--stage",
            "colour_spec",
            "--file",
            str(colour),
        )
        assert blocked.returncode == 3
        assert "Gate violation" in blocked.stdout

        mockup_result = run(
            "record-file",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--stage",
            "garment_mockup",
            "--file",
            str(mockup),
        )
        assert mockup_result.returncode == 0, mockup_result.stdout + mockup_result.stderr

        colour_report = {
            "status": "colour_role_spec_ready",
            "roles_locked": True,
            "source_image_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "dropped_roles": [],
            "roles": [
                {
                    "id": 1,
                    "element": "象牙底色",
                    "source_hex": "#F3ECE0",
                    "pantone_tcx": "TEST-0001",
                    "pantone_name": "Fixture Ivory",
                    "delta_e00": 0.42,
                }
            ],
            "annotation_image": str(annotation),
            "markdown_spec": str(colour),
            "physical_review": {"status": "pending"},
        }
        colour_report_path = root / "colour-role-report.json"
        colour_report_path.write_text(json.dumps(colour_report), encoding="utf-8")
        colour_result = run(
            "record-file",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--stage",
            "colour_spec",
            "--file",
            str(annotation),
            "--file",
            str(colour),
            "--colour-report",
            str(colour_report_path),
        )
        assert colour_result.returncode == 0, colour_result.stdout + colour_result.stderr

        failed_report = validation_report(root, "failed", "edge_lock_failed")
        failed = run(
            "record-validation",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--report",
            str(failed_report),
        )
        assert failed.returncode == 0, failed.stdout + failed.stderr
        assert json.loads(failed.stdout)["data"]["next_action"] == "repeat_repair"

        repaired = write(root / "repaired.png", "repaired")
        heatmap = write(root / "repair-heatmap.png", "heatmap")
        guard_report = {
            "status": "protected_repair_ready",
            "guarded_half_offset": str(repaired),
            "guarded_half_offset_sha256": hashlib.sha256(repaired.read_bytes()).hexdigest(),
            "difference_heatmap": str(heatmap),
            "outside_mask_changed_pixels": 0,
            "outside_mask_exact_match_percent": 100.0,
        }
        guard_report_path = root / "seam-guard-report.json"
        guard_report_path.write_text(json.dumps(guard_report), encoding="utf-8")
        repair = run(
            "record-file",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--stage",
            "repeat_repair",
            "--file",
            str(repaired),
            "--guard-report",
            str(guard_report_path),
        )
        assert repair.returncode == 0

        passed_report = validation_report(root, "final", "digital_seamless_repeat_passed")
        passed = run(
            "record-validation",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--report",
            str(passed_report),
        )
        assert passed.returncode == 0, passed.stdout + passed.stderr
        final_tile = root / "final.png"
        final_sha = hashlib.sha256(final_tile.read_bytes()).hexdigest()

        images = "".join(
            [
                '<img name="TST-01_selected.png"/>',
                '<img name="TST-01_mockup.png"/>',
                '<img name="TST-01_配色编号标注.png"/>',
            ]
        )
        readback = {
            "ok": True,
            "identity": "user",
            "data": {
                "document": {
                    "document_id": "testdoc",
                    "revision_id": 9,
                    "content": (
                        f'<fragment><h2>TST-01</h2>{images}'
                        f'<p>{final_sha} digital_seamless_repeat_passed</p>'
                        '<table><tr><th>标注</th><th>元素</th><th>源图 HEX</th>'
                        '<th>Pantone TCX</th><th>色名 / ΔE00</th></tr>'
                        '<tr><td>1</td><td>象牙底色</td><td>#F3ECE0</td>'
                        '<td>TEST-0001 TCX</td><td>Fixture Ivory / 0.42</td></tr>'
                        '</table></fragment>'
                    ),
                }
            },
        }
        readback_path = root / "readback.json"
        readback_path.write_text(json.dumps(readback), encoding="utf-8")
        feishu = run(
            "record-feishu",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
            "--doc-url",
            "https://example.feishu.cn/docx/testdoc",
            "--readback-file",
            str(readback_path),
        )
        assert feishu.returncode == 0, feishu.stdout + feishu.stderr

        audit = run(
            "audit",
            "--project-dir",
            str(project),
            "--print-id",
            "TST-01",
        )
        assert audit.returncode == 0, audit.stdout + audit.stderr
        payload = json.loads(audit.stdout)["data"]
        assert payload["overall_status"] == "feishu_design_closure_completed"
        assert payload["next_action"] == "closed"

        local_project = root / "local-project"
        local_source = write(root / "local-selected.png", "local-selected-source")
        local_mockup = write(root / "local-mockup.png", "local-mockup")
        local_annotation = write(root / "local-annotation.png", "local-annotation")
        local_spec = write(root / "local-spec.md", "local-spec")
        local_init = run(
            "init",
            "--project-dir",
            str(local_project),
            "--print-id",
            "LOCAL-01",
            "--name",
            "Local Test Print",
            "--source",
            str(local_source),
            "--approval-phrase",
            "selected",
            "--category",
            "shirt",
            "--garment-template",
            str(template),
        )
        assert local_init.returncode == 0, local_init.stdout + local_init.stderr
        local_state = json.loads(local_init.stdout)["data"]
        assert local_state["context"]["document_mode"] == "local"
        assert local_state["stages"]["feishu_sync"]["status"] == "not_required"

        local_mockup_result = run(
            "record-file",
            "--project-dir",
            str(local_project),
            "--print-id",
            "LOCAL-01",
            "--stage",
            "garment_mockup",
            "--file",
            str(local_mockup),
        )
        assert local_mockup_result.returncode == 0
        local_colour_report = {
            "status": "colour_role_spec_ready",
            "roles_locked": True,
            "source_image_sha256": hashlib.sha256(local_source.read_bytes()).hexdigest(),
            "dropped_roles": [],
            "roles": [
                {
                    "id": 1,
                    "element": "ground",
                    "source_hex": "#F3ECE0",
                    "pantone_tcx": "TEST-0001",
                    "pantone_name": "Fixture Ivory",
                    "delta_e00": 0.42,
                }
            ],
            "annotation_image": str(local_annotation),
            "markdown_spec": str(local_spec),
            "physical_review": {"status": "pending"},
        }
        local_colour_report_path = root / "local-colour-report.json"
        local_colour_report_path.write_text(json.dumps(local_colour_report), encoding="utf-8")
        local_colour_result = run(
            "record-file",
            "--project-dir",
            str(local_project),
            "--print-id",
            "LOCAL-01",
            "--stage",
            "colour_spec",
            "--file",
            str(local_annotation),
            "--file",
            str(local_spec),
            "--colour-report",
            str(local_colour_report_path),
        )
        assert local_colour_result.returncode == 0, local_colour_result.stdout
        local_passed_report = validation_report(
            root, "local-final", "digital_seamless_repeat_passed"
        )
        local_validation = run(
            "record-validation",
            "--project-dir",
            str(local_project),
            "--print-id",
            "LOCAL-01",
            "--report",
            str(local_passed_report),
        )
        assert local_validation.returncode == 0, local_validation.stdout
        assert json.loads(local_validation.stdout)["data"]["next_action"] == "closure_audit"
        local_audit = run(
            "audit",
            "--project-dir",
            str(local_project),
            "--print-id",
            "LOCAL-01",
        )
        assert local_audit.returncode == 0, local_audit.stdout + local_audit.stderr
        local_payload = json.loads(local_audit.stdout)["data"]
        assert local_payload["overall_status"] == "local_design_closure_completed"
        assert local_payload["next_action"] == "closed"

    print("selection closure tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
