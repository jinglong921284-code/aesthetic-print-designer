#!/usr/bin/env python3
"""Audit a Feishu print section against one selected-print closure state."""

from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PASS_STATUS = "digital_seamless_repeat_passed"
READY_STATUS = "document_consistency_passed"
STALE_TERMS = (
    "edge_lock_failed",
    "pending_visual_review",
    "visual_revise",
    "待修复",
    "接版失败",
    "四方连续未通过",
)


class DocumentAuditError(RuntimeError):
    pass


def require_file(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise DocumentAuditError(f"{label} is not a file: {path}")
    return path


def lark_fetch(arguments: list[str]) -> dict[str, Any]:
    executable = shutil.which("lark-cli")
    if executable is None:
        raise DocumentAuditError(
            "Feishu integration requires lark-cli on PATH; use local document mode "
            "when Feishu synchronization is not configured."
        )
    environment = os.environ.copy()
    environment["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"] = "1"
    environment["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"] = "1"
    try:
        result = subprocess.run(
            [executable, "docs", "+fetch", *arguments, "--as", "user"],
            text=True,
            capture_output=True,
            check=False,
            env=environment,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DocumentAuditError(f"Feishu readback could not run: {exc}") from exc
    if result.returncode != 0:
        raise DocumentAuditError(
            "Feishu readback failed: " + (result.stderr.strip() or result.stdout.strip())
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise DocumentAuditError("Feishu readback did not return JSON") from exc


def fetch_print_section(doc_url: str, print_id: str) -> dict[str, Any]:
    outline = lark_fetch(
        ["--doc", doc_url, "--scope", "outline", "--max-depth", "4", "--detail", "with-ids"]
    )
    content = outline.get("data", {}).get("document", {}).get("content", "")
    headings = re.findall(r'<h[1-6]\s+id="([^"]+)">([^<]*)</h[1-6]>', content)
    matches = [block_id for block_id, text in headings if print_id in text]
    if len(matches) != 1:
        raise DocumentAuditError(
            f"Expected one heading containing {print_id}, found {len(matches)}"
        )
    return lark_fetch(
        [
            "--doc",
            doc_url,
            "--scope",
            "section",
            "--start-block-id",
            matches[0],
            "--detail",
            "full",
        ]
    )


def find_colour_report(state: dict[str, Any]) -> dict[str, Any] | None:
    evidence = state.get("stages", {}).get("colour_spec", {}).get("evidence", [])
    for item in evidence:
        if isinstance(item, dict) and isinstance(item.get("report"), dict):
            path = Path(item["report"].get("path", ""))
            if path.is_file():
                with path.open("r", encoding="utf-8") as handle:
                    report = json.load(handle)
                if report.get("status") == "colour_role_spec_ready":
                    return report
    return None


def final_record(state: dict[str, Any]) -> dict[str, Any]:
    evidence = state.get("stages", {}).get("final_repeat_validation", {}).get("evidence", [])
    if not evidence:
        raise DocumentAuditError("State has no final repeat validation evidence")
    return evidence[-1]


def normalize_cell_text(value: str) -> str:
    # HTMLParser decodes character references once; only whitespace remains to normalize.
    return " ".join(value.split())


class TableContentParser(HTMLParser):
    """Extract visible cell text while preserving table and row boundaries."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._table_depth = 0
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def _finish_cell(self) -> None:
        if self._cell is not None and self._row is not None:
            self._row.append(normalize_cell_text("".join(self._cell)))
        self._cell = None

    def _finish_row(self) -> None:
        self._finish_cell()
        if self._row is not None and self._table is not None:
            self._table.append(self._row)
        self._row = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        tag = tag.lower()
        if tag == "table":
            if self._table_depth == 0:
                self._table = []
            self._table_depth += 1
            return
        if self._table_depth != 1:
            return
        if tag == "tr":
            self._finish_row()
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._finish_cell()
            self._cell = []
        elif self._cell is not None and tag in {"br", "div", "li", "p"}:
            self._cell.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "table":
            if self._table_depth == 1:
                self._finish_row()
                if self._table is not None:
                    self.tables.append(self._table)
                self._table = None
            if self._table_depth > 0:
                self._table_depth -= 1
            return
        if self._table_depth != 1:
            return
        if tag in {"td", "th"}:
            self._finish_cell()
        elif tag == "tr":
            self._finish_row()
        elif self._cell is not None and tag in {"div", "li", "p"}:
            self._cell.append(" ")

    def handle_data(self, data: str) -> None:
        if self._table_depth == 1 and self._cell is not None:
            self._cell.append(data)


def parse_tables(content: str) -> list[list[list[str]]]:
    parser = TableContentParser()
    parser.feed(content)
    parser.close()
    return parser.tables


def role_field(role: dict[str, Any], name: str) -> str:
    value = role.get(name)
    return normalize_cell_text(str(value)) if value is not None else ""


HEADER_FIELDS = ("id", "element", "source_hex", "pantone_tcx", "pantone_name")
HEADER_DISPLAY = {
    "id": "ID / 标注",
    "element": "元素",
    "source_hex": "源图 HEX",
    "pantone_tcx": "Pantone TCX",
    "pantone_name": "色名",
}


def normalize_header_text(value: str) -> str:
    text = normalize_cell_text(value).replace("／", "/").casefold()
    return re.sub(r"\s*/\s*", " / ", text)


def header_field(value: str) -> str | None:
    """Return a canonical field only for an unambiguous complete header label."""

    text = normalize_header_text(value)
    if text in {
        "id",
        "标注",
        "编号",
        "id / 标注",
        "标注 / id",
        "id / 编号",
        "编号 / id",
    }:
        return "id"
    if text in {"元素", "element"}:
        return "element"
    if text in {"源图 hex", "source hex"}:
        return "source_hex"
    if text in {"pantone tcx", "tcx"}:
        return "pantone_tcx"
    if re.fullmatch(
        r"(?:pantone )?(?:色名|name|colou?r name)"
        r"(?: / (?:δe00|∆e00|de00|说明))?",
        text,
    ):
        return "pantone_name"
    return None


def header_row_fields(row: list[str]) -> dict[str, list[int]]:
    fields: dict[str, list[int]] = {name: [] for name in HEADER_FIELDS}
    for column_index, cell in enumerate(row):
        field = header_field(cell)
        if field is not None:
            fields[field].append(column_index)
    return fields


def is_header_like(fields: dict[str, list[int]]) -> bool:
    present = {field for field, indexes in fields.items() if indexes}
    colour_fields = present & {"source_hex", "pantone_tcx", "pantone_name"}
    return len(present) >= 3 and len(colour_fields) >= 2


def cell_at(row: list[str], column_index: int) -> str:
    return row[column_index] if column_index < len(row) else ""


def exact_normalized(actual: str, expected: str, *, casefold: bool = False) -> bool:
    actual_normalized = normalize_cell_text(actual)
    expected_normalized = normalize_cell_text(expected)
    if casefold:
        return actual_normalized.casefold() == expected_normalized.casefold()
    return actual_normalized == expected_normalized


def exact_tcx(actual: str, expected: str) -> bool:
    actual_normalized = normalize_cell_text(actual)
    expected_normalized = normalize_cell_text(expected)
    if not expected_normalized:
        return False
    return re.fullmatch(
        rf"{re.escape(expected_normalized)}(?:\s+TCX)?",
        actual_normalized,
        flags=re.IGNORECASE,
    ) is not None


def reasonable_name_cell(
    actual: str,
    expected: str,
    forbidden_role_values: list[str],
    expected_delta_e00: Any = None,
) -> bool:
    """Accept a name or a name followed by a bounded Delta-E value/explanation."""

    actual_normalized = normalize_cell_text(actual)
    expected_normalized = normalize_cell_text(expected)
    if not expected_normalized:
        return False
    if actual_normalized.casefold() == expected_normalized.casefold():
        return expected_delta_e00 is None
    suffix_match = re.fullmatch(
        rf"{re.escape(expected_normalized)}\s*/\s*(.+)",
        actual_normalized,
        flags=re.IGNORECASE,
    )
    if suffix_match is None:
        return False
    suffix = normalize_cell_text(suffix_match.group(1))
    if not suffix or len(suffix) > 120:
        return False

    suffix_folded = suffix.casefold()
    if re.search(r"#[0-9a-f]{6}\b", suffix_folded):
        return False
    if re.search(r"\b[0-9]{2}-[0-9]{4}(?:\s+tcx)?\b", suffix_folded):
        return False
    for value in forbidden_role_values:
        normalized = normalize_cell_text(value).casefold()
        if normalized and normalized in suffix_folded:
            return False

    delta_match = re.fullmatch(
        r"(?:δe00\s*(?:[:=：]\s*)?)?([0-9]+(?:\.[0-9]+)?)",
        suffix_folded,
    )
    if delta_match is not None:
        actual_delta = float(delta_match.group(1))
        if not 0.0 <= actual_delta <= 200.0:
            return False
        if expected_delta_e00 is None:
            return True
        try:
            expected_delta = float(expected_delta_e00)
        except (TypeError, ValueError):
            return False
        return abs(actual_delta - expected_delta) <= 0.0051
    if expected_delta_e00 is not None:
        return False
    return re.search(r"[a-z\u3400-\u9fff]", suffix_folded) is not None


def audit_colour_mapping_tables(content: str, roles: list[dict[str, Any]]) -> dict[str, Any]:
    tables = parse_tables(content)
    candidates: list[tuple[list[list[str]], list[tuple[int, dict[str, list[int]]]]]] = []
    for table in tables:
        header_rows = [
            (row_index, fields)
            for row_index, row in enumerate(table)
            if is_header_like(fields := header_row_fields(row))
        ]
        if header_rows:
            candidates.append((table, header_rows))

    result: dict[str, Any] = {
        "tables": len(tables),
        "candidates": len(candidates),
        "mapping_rows": 0,
        "table_errors": [],
        "row_errors": [],
        "value_errors": [],
    }
    if len(candidates) != 1:
        result["table_errors"].append(
            "Expected exactly one colour mapping table containing the role rows; "
            f"found {len(candidates)} candidates among {len(tables)} parsed tables"
        )
        return result

    table, header_rows = candidates[0]
    if len(header_rows) != 1:
        result["table_errors"].append(
            "Expected exactly one colour mapping header row in the identified table; "
            f"found {len(header_rows)}"
        )
        return result

    header_index, header_fields = header_rows[0]
    missing_headers = [
        HEADER_DISPLAY[field] for field in HEADER_FIELDS if not header_fields[field]
    ]
    duplicate_headers = [
        (field, indexes)
        for field, indexes in header_fields.items()
        if len(indexes) > 1
    ]
    if missing_headers:
        result["table_errors"].append(
            "Colour mapping header is missing required columns: " + ", ".join(missing_headers)
        )
    for field, indexes in duplicate_headers:
        columns = ", ".join(str(index + 1) for index in indexes)
        result["table_errors"].append(
            f"Colour mapping header column {HEADER_DISPLAY[field]} must be unique; "
            f"found at columns {columns}"
        )
    if result["table_errors"]:
        return result

    columns = {field: indexes[0] for field, indexes in header_fields.items()}
    mapping_rows: list[tuple[int, int, list[str]]] = []
    for row_index, row in enumerate(table):
        if row_index == header_index:
            continue
        row_number = row_index + 1
        id_cell = normalize_cell_text(cell_at(row, columns["id"]))
        if re.fullmatch(r"[0-9]+", id_cell):
            mapping_rows.append((int(id_cell), row_number, row))
        elif any(cell for cell in row):
            result["row_errors"].append(
                f"Colour mapping table row {row_number} has content, but its ID cell is not "
                "an exact Arabic numeral"
            )
    result["mapping_rows"] = len(mapping_rows)

    expected_ids = list(range(1, len(roles) + 1))
    actual_ids = [role_id for role_id, _row_number, _row in mapping_rows]
    id_counts = Counter(actual_ids)
    for role_id in expected_ids:
        count = id_counts.get(role_id, 0)
        if count == 0:
            result["row_errors"].append(f"Missing colour mapping row for role ID {role_id}")
        elif count > 1:
            result["row_errors"].append(
                f"Duplicate colour mapping ID {role_id}: found {count} rows"
            )
    unexpected = [role_id for role_id in actual_ids if role_id not in expected_ids]
    if unexpected:
        result["row_errors"].append(
            "Unexpected colour mapping IDs: " + ", ".join(str(value) for value in unexpected)
        )
    if actual_ids != expected_ids:
        result["row_errors"].append(
            f"Colour mapping row order must be {expected_ids}; found {actual_ids}"
        )

    rows_by_id: dict[int, list[tuple[int, list[str]]]] = {}
    for role_id, row_number, row in mapping_rows:
        rows_by_id.setdefault(role_id, []).append((row_number, row))
    forbidden_name_values = [
        role_field(role, field)
        for role in roles
        for field in ("element", "source_hex", "pantone_tcx")
        if role_field(role, field)
    ]
    for role in roles:
        role_id = int(role["id"])
        matching_rows = rows_by_id.get(role_id, [])
        if len(matching_rows) != 1:
            continue
        row_number, row = matching_rows[0]
        id_cell = cell_at(row, columns["id"])
        if not exact_normalized(id_cell, str(role_id)):
            result["value_errors"].append(
                f"Role {role_id} row {row_number} ID column must equal {role_id}; "
                f"found {normalize_cell_text(id_cell)!r}"
            )

        element = role_field(role, "element")
        if element and not exact_normalized(cell_at(row, columns["element"]), element):
            result["value_errors"].append(
                f"Role {role_id} row {row_number} element column mismatch: expected "
                f"{element!r}, found {cell_at(row, columns['element'])!r}"
            )

        source_hex = role_field(role, "source_hex")
        if not source_hex:
            result["value_errors"].append(
                f"Role {role_id} colour report is missing required field source_hex"
            )
        elif not exact_normalized(
            cell_at(row, columns["source_hex"]), source_hex, casefold=True
        ):
            result["value_errors"].append(
                f"Role {role_id} row {row_number} source_hex column mismatch: expected "
                f"{source_hex!r}, found {cell_at(row, columns['source_hex'])!r}"
            )

        pantone_tcx = role_field(role, "pantone_tcx")
        if not pantone_tcx:
            result["value_errors"].append(
                f"Role {role_id} colour report is missing required field pantone_tcx"
            )
        elif not exact_tcx(cell_at(row, columns["pantone_tcx"]), pantone_tcx):
            result["value_errors"].append(
                f"Role {role_id} row {row_number} pantone_tcx column mismatch: expected "
                f"{pantone_tcx!r} or {pantone_tcx + ' TCX'!r}, "
                f"found {cell_at(row, columns['pantone_tcx'])!r}"
            )

        pantone_name = role_field(role, "pantone_name")
        if pantone_name and not reasonable_name_cell(
            cell_at(row, columns["pantone_name"]),
            pantone_name,
            forbidden_name_values,
            role.get("delta_e00"),
        ):
            result["value_errors"].append(
                f"Role {role_id} row {row_number} pantone_name column mismatch: expected "
                f"{pantone_name!r} with only an optional Delta-E value or explanation, "
                f"found {cell_at(row, columns['pantone_name'])!r}"
            )
    return result


def audit_payload_against_state(payload: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            errors.append(detail)

    check(
        "user_readback",
        payload.get("ok") is True and payload.get("identity") == "user",
        "Feishu readback must be successful and use user identity",
    )
    document = payload.get("data", {}).get("document", {})
    revision = document.get("revision_id")
    content = document.get("content", "")
    print_id = state["print_id"]
    final = final_record(state)
    final_sha = final.get("input", {}).get("sha256", "")
    check("print_id", print_id in content, f"Missing Print ID: {print_id}")
    check("final_status", PASS_STATUS in content, f"Missing final status: {PASS_STATUS}")
    check("final_sha", bool(final_sha) and final_sha in content, f"Missing final tile SHA-256: {final_sha}")
    check("revision", isinstance(revision, int) and revision > 0, "Missing valid Feishu revision_id")

    stale_found = [term for term in STALE_TERMS if term in content]
    check(
        "no_stale_status",
        not stale_found,
        "Stale failure or repair terms remain: " + ", ".join(stale_found),
    )

    image_tags = re.findall(r"<img\b[^>]*>", content)
    id_images = [tag for tag in image_tags if print_id in tag]
    check(
        "required_images",
        len(id_images) >= 3,
        f"Expected at least 3 Print-ID images (selected, mockup, colour annotation); found {len(id_images)}",
    )
    colour_images = [tag for tag in id_images if "配色" in tag or "colour" in tag.lower()]
    check("colour_annotation", bool(colour_images), "Missing Print-ID colour annotation image")

    colour_counts = {"tables": 0, "candidates": 0, "mapping_rows": 0}
    colour = find_colour_report(state)
    if colour is None:
        check(
            "colour_report",
            False,
            "Closure state has no readable colour-role report",
        )
    else:
        roles = colour.get("roles", [])
        ids = [role.get("id") for role in roles if isinstance(role, dict)]
        sequence_passed = (
            isinstance(roles, list)
            and bool(roles)
            and len(ids) == len(roles)
            and ids == list(range(1, len(roles) + 1))
        )
        check(
            "colour_sequence",
            sequence_passed,
            "Colour report roles must be non-empty and sequential from 1",
        )
        if sequence_passed:
            table_audit = audit_colour_mapping_tables(content, roles)
            colour_counts = {
                key: table_audit[key] for key in ("tables", "candidates", "mapping_rows")
            }
            check(
                "colour_mapping_table",
                not table_audit["table_errors"],
                "; ".join(table_audit["table_errors"])
                or "Colour mapping table was not uniquely identified",
            )
            if not table_audit["table_errors"]:
                check(
                    "colour_mapping_rows",
                    not table_audit["row_errors"],
                    "; ".join(table_audit["row_errors"])
                    or "Colour mapping row IDs are missing, duplicated, or out of order",
                )
                check(
                    "colour_mapping_values",
                    not table_audit["value_errors"],
                    "; ".join(table_audit["value_errors"])
                    or "Colour mapping values are not aligned within their role rows",
                )

    if "<excerpt" in content:
        warnings.append("Readback contains an excerpt; use a full Print-ID section for final closure")
        errors.append("Feishu readback is a partial excerpt, not a full Print-ID section")

    return {
        "schema_version": 1,
        "status": READY_STATUS if not errors else "document_consistency_revise",
        "print_id": print_id,
        "document_id": document.get("document_id"),
        "revision_id": revision,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "image_tags": len(image_tags),
            "print_id_images": len(id_images),
            "tables": colour_counts["tables"],
            "colour_mapping_candidates": colour_counts["candidates"],
            "colour_mapping_rows": colour_counts["mapping_rows"],
        },
    }


def write_report(out_dir: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{report['print_id']}-document-consistency-audit.json"
    markdown_path = out_dir / f"{report['print_id']}-document-consistency-audit.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# {report['print_id']}｜飞书文档一致性审计",
        "",
        f"状态：`{report['status']}`  ",
        f"Revision：{report.get('revision_id')}  ",
        "",
        "| 检查项 | 结果 |",
        "|---|---|",
    ]
    for item in report["checks"]:
        lines.append(f"| {item['name']} | {'通过' if item['passed'] else item['detail']} |")
    if report["errors"]:
        lines.extend(["", "## 必须修复", ""] + [f"- {error}" for error in report["errors"]])
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit one Feishu print section against closure state")
    parser.add_argument("--state", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--doc-url")
    source.add_argument("--readback-file")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    try:
        state_path = require_file(args.state, "closure state")
        with state_path.open("r", encoding="utf-8") as handle:
            state = json.load(handle)
        if args.readback_file:
            readback_path = require_file(args.readback_file, "Feishu readback")
            with readback_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        else:
            payload = fetch_print_section(args.doc_url, state["print_id"])
        report = audit_payload_against_state(payload, state)
        json_path, markdown_path = write_report(Path(args.out_dir).expanduser().resolve(), report)
        output = {"ok": report["status"] == READY_STATUS, "data": {**report, "json_report": str(json_path), "markdown_report": str(markdown_path)}}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0 if output["ok"] else 5
    except (DocumentAuditError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
