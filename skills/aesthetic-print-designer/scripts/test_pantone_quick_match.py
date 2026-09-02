#!/usr/bin/env python3
"""Functional tests for deterministic chat-level Pantone TCX quick matching."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from pantone_quick_match import QuickMatchError, resolve_database


SCRIPT = Path(__file__).with_name("pantone_quick_match.py")


def write_database(path: Path, rows: list[dict]) -> Path:
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return path


def run(*arguments: str, environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("PANTONE_TCX_DB", None)
    if environment:
        env.update(environment)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def valid_rows() -> list[dict]:
    return [
        {"tcx": "TEST-1002", "name": "Fixture Tie B", "hex": "#808080", "r": 128, "g": 128, "b": 128},
        {"tcx": "TEST-1001", "name": "Fixture Tie A", "hex": "#808080", "r": 128, "g": 128, "b": 128},
        {"tcx": "TEST-1003", "name": "Fixture Light", "hex": "#F0F0F0", "r": 240, "g": 240, "b": 240},
        {"tcx": "TEST-1004", "name": "Fixture Dark", "hex": "#101010", "r": 16, "g": 16, "b": 16},
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="pantone-quick-match-test-") as temp:
        root = Path(temp)
        database = write_database(root / "pantone.json", valid_rows())
        expected_sha = hashlib.sha256(database.read_bytes()).hexdigest()

        deterministic = run(
            "--database",
            str(database),
            "--hex",
            "#808080",
            "--label",
            "中性灰",
            "--top",
            "2",
        )
        assert deterministic.returncode == 0, deterministic.stdout + deterministic.stderr
        payload = json.loads(deterministic.stdout)["data"]
        assert payload["status"] == "screen_computed_candidate"
        assert payload["database"]["source"] == "--database"
        assert payload["database"]["sha256"] == expected_sha
        assert payload["database"]["entries"] == 4
        assert payload["physical_review"]["status"] == "pending"
        assert payload["writes"] == {
            "closure": False,
            "external_document": False,
            "files": False,
        }
        query = payload["queries"][0]
        assert query["label"] == "中性灰"
        assert [item["tcx"] for item in query["matches"]] == ["TEST-1001", "TEST-1002"]
        assert [item["delta_e00"] for item in query["matches"]] == [0.0, 0.0]

        repeated = run(
            "--hex",
            "#808080",
            "--label",
            "灰",
            "--hex",
            "#F0F0F0",
            "--label",
            "白",
            "--top",
            "1",
            environment={"PANTONE_TCX_DB": str(database)},
        )
        assert repeated.returncode == 0, repeated.stdout + repeated.stderr
        repeated_payload = json.loads(repeated.stdout)["data"]
        assert repeated_payload["database"]["source"] == "PANTONE_TCX_DB"
        assert [item["label"] for item in repeated_payload["queries"]] == ["灰", "白"]
        assert repeated_payload["queries"][1]["matches"][0]["tcx"] == "TEST-1003"

        no_labels = run(
            "--database",
            str(database),
            "--hex",
            "#101010",
            "--top",
            "1",
        )
        assert no_labels.returncode == 0
        assert json.loads(no_labels.stdout)["data"]["queries"][0]["label"] is None

        bad_environment_database = root / "bad-environment.json"
        bad_environment_database.write_text("not-json", encoding="utf-8")
        explicit_precedence = run(
            "--database",
            str(database),
            "--hex",
            "#808080",
            environment={"PANTONE_TCX_DB": str(bad_environment_database)},
        )
        assert explicit_precedence.returncode == 0
        assert json.loads(explicit_precedence.stdout)["data"]["database"]["name"] == database.name

        try:
            resolve_database(None, environment={})
        except QuickMatchError as exc:
            assert "--database" in str(exc)
            assert "PANTONE_TCX_DB" in str(exc)
        else:
            raise AssertionError("Missing database configuration must fail")

        mismatched_labels = run(
            "--database",
            str(database),
            "--hex",
            "#808080",
            "--hex",
            "#F0F0F0",
            "--label",
            "只有一个标签",
        )
        assert mismatched_labels.returncode == 3
        assert "number of --label" in json.loads(mismatched_labels.stdout)["error"]

        invalid_hex = run("--database", str(database), "--hex", "808080")
        assert invalid_hex.returncode == 3
        assert "Invalid --hex" in json.loads(invalid_hex.stdout)["error"]

        invalid_top = run("--database", str(database), "--hex", "#808080", "--top", "0")
        assert invalid_top.returncode == 3
        assert "--top must be at least 1" in json.loads(invalid_top.stdout)["error"]

        duplicates = valid_rows()
        duplicates[1] = {**duplicates[1], "tcx": duplicates[0]["tcx"]}
        duplicate_database = write_database(root / "duplicate.json", duplicates)
        duplicate_result = run("--database", str(duplicate_database), "--hex", "#808080")
        assert duplicate_result.returncode == 3
        assert "duplicate tcx" in json.loads(duplicate_result.stdout)["error"]

        missing_database = write_database(
            root / "missing-field.json",
            [{"tcx": "TEST-1001", "name": "Incomplete", "hex": "#808080", "r": 128, "g": 128}],
        )
        missing_result = run("--database", str(missing_database), "--hex", "#808080")
        assert missing_result.returncode == 3
        assert "missing required fields: b" in json.loads(missing_result.stdout)["error"]

    print("pantone quick match tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
