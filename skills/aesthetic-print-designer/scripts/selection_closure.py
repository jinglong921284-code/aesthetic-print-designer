#!/usr/bin/env python3
"""Deterministic post-selection state machine for fashion-print closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATE_DIR = ".print-closure"
STAGES = (
    "source_lock",
    "garment_mockup",
    "colour_spec",
    "initial_repeat_validation",
    "repeat_repair",
    "final_repeat_validation",
    "feishu_sync",
    "closure_audit",
)
FILE_STAGES = {"garment_mockup", "colour_spec", "repeat_repair"}
PASS_STATUS = "digital_seamless_repeat_passed"
DOCUMENT_MODES = ("local", "feishu")


class WorkflowError(RuntimeError):
    """A truthful workflow-gate failure."""


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise WorkflowError(f"{label} is not a file: {path}")
    return path


def project_root(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def state_path(project: Path, print_id: str) -> Path:
    return project / STATE_DIR / print_id / "closure-state.json"


def load_state(project: Path, print_id: str) -> dict[str, Any]:
    path = state_path(project, print_id)
    if not path.is_file():
        raise WorkflowError(
            f"No closure state for {print_id}. Run the init command after explicit selection."
        )
    with path.open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("schema_version") != SCHEMA_VERSION:
        raise WorkflowError("Unsupported closure-state schema version")
    return state


def save_state(project: Path, state: dict[str, Any]) -> Path:
    path = state_path(project, state["print_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()
    state["next_action"] = derive_next_action(state)
    if state["stages"]["closure_audit"]["status"] == "completed":
        mode = state.get("context", {}).get("document_mode", "feishu")
        state["overall_status"] = f"{mode}_design_closure_completed"
    else:
        state["overall_status"] = "in_progress"
    temp = path.with_suffix(".json.tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temp.replace(path)
    update_index(project, state)
    return path


def update_index(project: Path, state: dict[str, Any]) -> None:
    root = project / STATE_DIR
    root.mkdir(parents=True, exist_ok=True)
    path = root / "index.json"
    if path.is_file():
        with path.open("r", encoding="utf-8") as handle:
            index = json.load(handle)
    else:
        index = {"schema_version": SCHEMA_VERSION, "prints": {}}
    index["prints"][state["print_id"]] = {
        "name": state["name"],
        "state_file": str(state_path(project, state["print_id"])),
        "overall_status": state["overall_status"],
        "next_action": state["next_action"],
        "updated_at": state["updated_at"],
    }
    temp = path.with_suffix(".json.tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temp.replace(path)


def event(state: dict[str, Any], action: str, details: dict[str, Any]) -> None:
    state["events"].append(
        {"timestamp": now_iso(), "action": action, "details": details}
    )


def evidence(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}


def derive_next_action(state: dict[str, Any]) -> str:
    stages = state["stages"]
    if stages["source_lock"]["status"] != "completed":
        return "source_lock"
    if stages["garment_mockup"]["status"] != "completed":
        context = state["context"]
        if not context.get("category") or not context.get("garment_template"):
            return "resolve_garment_context"
        return "garment_mockup"
    if stages["colour_spec"]["status"] != "completed":
        return "colour_spec"
    if stages["initial_repeat_validation"]["status"] != "completed":
        return "initial_repeat_validation"
    if stages["repeat_repair"]["status"] == "required":
        return "repeat_repair"
    if stages["final_repeat_validation"]["status"] != "completed":
        return "final_repeat_validation"
    if stages["feishu_sync"]["status"] not in {"completed", "not_required"}:
        if not state["context"].get("feishu_doc"):
            return "resolve_feishu_document"
        return "feishu_sync"
    if stages["closure_audit"]["status"] != "completed":
        return "closure_audit"
    return "closed"


def require_next(state: dict[str, Any], expected: str) -> None:
    actual = derive_next_action(state)
    if actual != expected:
        raise WorkflowError(f"Gate violation: next action is {actual}, not {expected}")


def make_stage(status: str = "pending") -> dict[str, Any]:
    return {"status": status, "updated_at": None, "evidence": [], "attempts": []}


def command_init(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = project_root(args.project_dir)
    project.mkdir(parents=True, exist_ok=True)
    source = require_file(args.source, "selected source")
    document_mode = args.document_mode or ("feishu" if args.feishu_doc else "local")
    if args.document_mode == "local" and args.feishu_doc:
        raise WorkflowError("--feishu-doc cannot be used with --document-mode local")
    existing = state_path(project, args.print_id)
    if existing.is_file():
        state = load_state(project, args.print_id)
        if state["source_lock"]["source_sha256"] != sha256(source):
            raise WorkflowError(
                "Print ID already exists with a different selected source; use a new version or Print ID"
            )
        return 0, state

    work = project / STATE_DIR / args.print_id
    locked_dir = work / "source_locked"
    locked_dir.mkdir(parents=True, exist_ok=True)
    locked = locked_dir / f"{args.print_id}_selected_v1{source.suffix.lower()}"
    shutil.copy2(source, locked)
    source_hash = sha256(source)
    if sha256(locked) != source_hash:
        raise WorkflowError("Locked source checksum does not match selected source")

    stages = {name: make_stage() for name in STAGES}
    if document_mode == "local":
        stages["feishu_sync"] = make_stage("not_required")
    stages["source_lock"] = {
        "status": "completed",
        "updated_at": now_iso(),
        "evidence": [evidence(locked)],
        "attempts": [],
    }
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "print_id": args.print_id,
        "name": args.name,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "overall_status": "in_progress",
        "next_action": "garment_mockup",
        "approval": {
            "type": "explicit_selection",
            "phrase": args.approval_phrase,
            "approved_at": args.approval_date or now_iso(),
        },
        "context": {
            "category": args.category,
            "garment_template": args.garment_template,
            "fabric": args.fabric,
            "document_mode": document_mode,
            "feishu_doc": args.feishu_doc,
        },
        "source_lock": {
            "original_path": str(source),
            "locked_path": str(locked),
            "source_sha256": source_hash,
        },
        "stages": stages,
        "events": [],
    }
    event(
        state,
        "explicit_selection_initialized",
        {"source": str(source), "locked": str(locked), "sha256": source_hash},
    )
    path = save_state(project, state)
    return 0, {"state_file": str(path), **state}


def command_set_context(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = project_root(args.project_dir)
    state = load_state(project, args.print_id)
    if args.feishu_doc is not None and state["context"].get("document_mode") != "feishu":
        raise WorkflowError(
            "This closure uses local document mode; start a new version in feishu mode "
            "before recording a Feishu target."
        )
    changed: dict[str, Any] = {}
    for key in ("category", "garment_template", "fabric", "feishu_doc"):
        value = getattr(args, key)
        if value is not None:
            state["context"][key] = value
            changed[key] = value
    if not changed:
        raise WorkflowError("No context value supplied")
    event(state, "context_updated", changed)
    path = save_state(project, state)
    return 0, {"state_file": str(path), "next_action": state["next_action"]}


def command_record_file(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = project_root(args.project_dir)
    state = load_state(project, args.print_id)
    if args.stage not in FILE_STAGES:
        raise WorkflowError(f"Unsupported file stage: {args.stage}")
    require_next(state, args.stage)
    files = [require_file(value, args.stage) for value in args.file]
    records = [evidence(path) for path in files]
    if args.stage == "colour_spec":
        if not args.colour_report:
            raise WorkflowError("colour_spec requires --colour-report from colour_role_spec.py")
        colour_path = require_file(args.colour_report, "colour role specification report")
        with colour_path.open("r", encoding="utf-8") as handle:
            colour = json.load(handle)
        roles = colour.get("roles", [])
        if colour.get("status") != "colour_role_spec_ready" or colour.get("roles_locked") is not True:
            raise WorkflowError("Colour report has not locked its colour roles")
        if colour.get("source_image_sha256") != state["source_lock"]["source_sha256"]:
            raise WorkflowError("Colour report does not match the locked selected source")
        if colour.get("dropped_roles"):
            raise WorkflowError("Colour report dropped one or more locked roles")
        if [role.get("id") for role in roles] != list(range(1, len(roles) + 1)):
            raise WorkflowError("Colour callout IDs are not sequential")
        if not roles or any(not role.get("pantone_tcx") for role in roles):
            raise WorkflowError("Every locked colour role requires a Pantone TCX candidate")
        if colour.get("physical_review", {}).get("status") != "pending":
            raise WorkflowError("Physical TCX and actual-fabric review must remain pending")
        annotation = require_file(colour.get("annotation_image", ""), "colour annotation")
        markdown = require_file(colour.get("markdown_spec", ""), "colour specification")
        expected = {sha256(annotation), sha256(markdown)}
        supplied = {record["sha256"] for record in records}
        if not expected.issubset(supplied):
            raise WorkflowError("Recorded colour files must include annotation and specification")
        records.append(
            {
                "report": evidence(colour_path),
                "roles_locked": len(roles),
                "annotation": evidence(annotation),
                "specification": evidence(markdown),
                "physical_review": "pending",
            }
        )
    guard_record = None
    if args.stage == "repeat_repair":
        if not args.guard_report:
            raise WorkflowError("repeat_repair requires --guard-report from seam_repair_guard.py")
        guard_path = require_file(args.guard_report, "seam repair guard report")
        with guard_path.open("r", encoding="utf-8") as handle:
            guard = json.load(handle)
        if guard.get("status") != "protected_repair_ready":
            raise WorkflowError("Seam repair guard report is not ready")
        if guard.get("outside_mask_changed_pixels") != 0:
            raise WorkflowError("Seam repair changed protected pixels outside the central cross")
        guarded_path = require_file(guard.get("guarded_half_offset", ""), "guarded repair")
        guarded_sha = guard.get("guarded_half_offset_sha256")
        if sha256(guarded_path) != guarded_sha:
            raise WorkflowError("Guarded repair checksum does not match its report")
        if all(record["sha256"] != guarded_sha for record in records):
            raise WorkflowError("Recorded repeat repair does not include the guarded output")
        heatmap = require_file(guard.get("difference_heatmap", ""), "repair difference heatmap")
        guard_record = {
            "report": evidence(guard_path),
            "guarded_output": evidence(guarded_path),
            "difference_heatmap": evidence(heatmap),
            "outside_mask_changed_pixels": 0,
            "outside_mask_exact_match_percent": guard.get(
                "outside_mask_exact_match_percent"
            ),
        }
        records.append(guard_record)
    stage = state["stages"][args.stage]
    stage["status"] = "completed"
    stage["updated_at"] = now_iso()
    stage["evidence"] = records
    stage["attempts"].append({"timestamp": now_iso(), "evidence": records})
    event(state, f"{args.stage}_recorded", {"files": records})
    path = save_state(project, state)
    return 0, {"state_file": str(path), "next_action": state["next_action"]}


def parse_validation_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    required = ("input", "edge_lock_pass", "visual_review", "overall_status", "offset_check", "tile_3x3_check")
    missing = [key for key in required if key not in report]
    if missing:
        raise WorkflowError(f"Validation report is missing: {', '.join(missing)}")
    input_file = require_file(report["input"], "validated tile")
    offset = require_file(report["offset_check"], "offset check")
    tiled = require_file(report["tile_3x3_check"], "3x3 check")
    return {
        "report": evidence(path),
        "input": evidence(input_file),
        "offset_check": evidence(offset),
        "tile_3x3_check": evidence(tiled),
        "overall_status": report["overall_status"],
        "edge_lock_pass": bool(report["edge_lock_pass"]),
        "visual_status": report.get("visual_review", {}).get("status"),
        "visual_notes": report.get("visual_review", {}).get("notes", ""),
    }


def command_record_validation(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = project_root(args.project_dir)
    state = load_state(project, args.print_id)
    next_action = derive_next_action(state)
    if next_action not in {"initial_repeat_validation", "final_repeat_validation"}:
        raise WorkflowError(
            f"Gate violation: next action is {next_action}, not repeat validation"
        )
    report_path = require_file(args.report, "validation report")
    record = parse_validation_report(report_path)
    passed = (
        record["overall_status"] == PASS_STATUS
        and record["edge_lock_pass"] is True
        and record["visual_status"] == "pass"
    )
    stage = state["stages"][next_action]
    stage["attempts"].append({"timestamp": now_iso(), **record})
    stage["updated_at"] = now_iso()

    if next_action == "initial_repeat_validation":
        stage["status"] = "completed"
        stage["evidence"] = [record]
        if passed:
            state["stages"]["repeat_repair"]["status"] = "not_required"
            final = state["stages"]["final_repeat_validation"]
            final["status"] = "completed"
            final["updated_at"] = now_iso()
            final["evidence"] = [record]
            final["attempts"].append(
                {"timestamp": now_iso(), "reused_initial_pass": True, **record}
            )
        else:
            state["stages"]["repeat_repair"]["status"] = "required"
    else:
        if passed:
            stage["status"] = "completed"
            stage["evidence"] = [record]
        else:
            stage["status"] = "pending"
            stage["evidence"] = [record]
            state["stages"]["repeat_repair"]["status"] = "required"

    event(
        state,
        "repeat_validation_recorded",
        {"phase": next_action, "passed": passed, "report": record},
    )
    path = save_state(project, state)
    result = {
        "state_file": str(path),
        "validation_passed": passed,
        "next_action": state["next_action"],
    }
    return (0 if passed or next_action == "initial_repeat_validation" else 4), result


def final_validation_record(state: dict[str, Any]) -> dict[str, Any]:
    stage = state["stages"]["final_repeat_validation"]
    if stage["status"] != "completed" or not stage["evidence"]:
        raise WorkflowError("Final repeat validation is not complete")
    return stage["evidence"][-1]


def fetch_feishu_readback(doc_url: str, print_id: str) -> dict[str, Any]:
    try:
        from document_consistency_audit import fetch_print_section

        return fetch_print_section(doc_url, print_id)
    except (ImportError, RuntimeError) as exc:
        raise WorkflowError(f"Feishu Print-ID section readback failed: {exc}") from exc


def command_record_feishu(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = project_root(args.project_dir)
    state = load_state(project, args.print_id)
    if state["context"].get("document_mode") != "feishu":
        raise WorkflowError("record-feishu requires a closure initialized in feishu mode")
    if derive_next_action(state) == "resolve_feishu_document":
        state["context"]["feishu_doc"] = args.doc_url
    require_next(state, "feishu_sync")
    if state["context"].get("feishu_doc") != args.doc_url:
        raise WorkflowError("Feishu document does not match the closure context")

    readback = (
        require_file(args.readback_file, "Feishu readback JSON")
        if args.readback_file
        else None
    )
    if readback:
        with readback.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = fetch_feishu_readback(args.doc_url, state["print_id"])
    if payload.get("ok") is not True or payload.get("identity") != "user":
        raise WorkflowError("Feishu readback must be a successful user-identity fetch")
    document = payload.get("data", {}).get("document", {})
    revision = document.get("revision_id")
    content = document.get("content", "")
    final_record = final_validation_record(state)
    final_sha = final_record["input"]["sha256"]
    missing = [
        value
        for value in (state["print_id"], PASS_STATUS, final_sha)
        if value not in content
    ]
    if missing:
        raise WorkflowError(
            "Feishu readback is missing required closure evidence: " + ", ".join(missing)
        )
    if not isinstance(revision, int) or revision < 1:
        raise WorkflowError("Feishu readback has no valid revision_id")

    evidence_dir = project / STATE_DIR / state["print_id"] / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    snapshot = evidence_dir / f"feishu-readback-r{revision}.json"
    with snapshot.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    record = {
        "doc_url": args.doc_url,
        "document_id": document.get("document_id"),
        "revision_id": revision,
        "readback": evidence(snapshot),
        "verified_values": [state["print_id"], PASS_STATUS, final_sha],
    }
    stage = state["stages"]["feishu_sync"]
    stage["status"] = "completed"
    stage["updated_at"] = now_iso()
    stage["evidence"] = [record]
    stage["attempts"].append({"timestamp": now_iso(), **record})
    event(state, "feishu_sync_verified", record)
    path = save_state(project, state)
    return 0, {"state_file": str(path), "next_action": state["next_action"]}


def verify_evidence_files(value: Any, errors: list[str], prefix: str = "") -> None:
    if isinstance(value, dict):
        if "path" in value and "sha256" in value:
            path = Path(value["path"])
            if not path.is_file():
                errors.append(f"Missing evidence file: {path}")
            elif sha256(path) != value["sha256"]:
                errors.append(f"Evidence checksum changed: {path}")
        for key, child in value.items():
            verify_evidence_files(child, errors, f"{prefix}.{key}" if prefix else key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            verify_evidence_files(child, errors, f"{prefix}[{index}]")


def command_audit(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = project_root(args.project_dir)
    state = load_state(project, args.print_id)
    require_next(state, "closure_audit")
    errors: list[str] = []
    required_completed = [
        "source_lock",
        "garment_mockup",
        "colour_spec",
        "initial_repeat_validation",
        "final_repeat_validation",
    ]
    document_mode = state.get("context", {}).get("document_mode", "feishu")
    if document_mode == "feishu":
        required_completed.append("feishu_sync")
    for name in required_completed:
        if state["stages"][name]["status"] != "completed":
            errors.append(f"Stage is not complete: {name}")
    if state["stages"]["repeat_repair"]["status"] not in {
        "completed",
        "not_required",
    }:
        errors.append("Repeat repair is neither completed nor not_required")
    final = final_validation_record(state)
    if final["overall_status"] != PASS_STATUS or final["visual_status"] != "pass":
        errors.append("Final validation is not a recorded digital visual pass")
    verify_evidence_files(state["stages"], errors)
    locked = Path(state["source_lock"]["locked_path"])
    if not locked.is_file() or sha256(locked) != state["source_lock"]["source_sha256"]:
        errors.append("Locked selected source is missing or changed")

    document_report: dict[str, Any] | None = None
    if document_mode == "feishu":
        try:
            from document_consistency_audit import (
                READY_STATUS as DOCUMENT_PASS_STATUS,
                audit_payload_against_state,
                write_report,
            )

            sync = state["stages"]["feishu_sync"]["evidence"][-1]
            readback_path = Path(sync["readback"]["path"])
            with readback_path.open("r", encoding="utf-8") as handle:
                readback_payload = json.load(handle)
            document_report = audit_payload_against_state(readback_payload, state)
            report_dir = project / STATE_DIR / state["print_id"] / "evidence" / "document-audit"
            json_report, markdown_report = write_report(report_dir, document_report)
            document_report["json_report"] = evidence(json_report)
            document_report["markdown_report"] = evidence(markdown_report)
            if document_report["status"] != DOCUMENT_PASS_STATUS:
                errors.extend(document_report["errors"])
        except (ImportError, OSError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
            errors.append(f"Document consistency audit could not run: {exc}")
    else:
        document_report = {
            "status": "not_applicable",
            "document_mode": "local",
            "reason": "No external document synchronization was authorized for this closure.",
        }

    stage = state["stages"]["closure_audit"]
    stage["updated_at"] = now_iso()
    stage["attempts"].append({"timestamp": now_iso(), "errors": errors})
    if errors:
        stage["status"] = "revise"
        stage["evidence"] = [document_report] if document_report else []
        event(state, "closure_audit_failed", {"errors": errors})
        path = save_state(project, state)
        return 5, {"state_file": str(path), "errors": errors, "next_action": "closure_audit"}

    stage["status"] = "completed"
    closure_evidence = {
        "audited_at": now_iso(),
        "closure_scope": document_mode,
        "final_tile_sha256": final["input"]["sha256"],
        "document_consistency": document_report,
    }
    if document_mode == "feishu":
        closure_evidence["feishu_revision"] = state["stages"]["feishu_sync"][
            "evidence"
        ][-1]["revision_id"]
    stage["evidence"] = [closure_evidence]
    event(state, "design_closure_completed", stage["evidence"][-1])
    path = save_state(project, state)
    return 0, {
        "state_file": str(path),
        "overall_status": state["overall_status"],
        "next_action": state["next_action"],
    }


def command_status(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = project_root(args.project_dir)
    state = load_state(project, args.print_id)
    return 0, state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the explicit-selection print closure state machine."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Lock an explicitly selected source and start closure")
    init.add_argument("--project-dir", required=True)
    init.add_argument("--print-id", required=True)
    init.add_argument("--name", required=True)
    init.add_argument("--source", required=True)
    init.add_argument("--approval-phrase", required=True)
    init.add_argument("--approval-date")
    init.add_argument("--category")
    init.add_argument("--garment-template")
    init.add_argument("--fabric")
    init.add_argument("--document-mode", choices=DOCUMENT_MODES)
    init.add_argument("--feishu-doc")
    init.set_defaults(handler=command_init)

    context = sub.add_parser("set-context", help="Fill a missing garment or Feishu context")
    context.add_argument("--project-dir", required=True)
    context.add_argument("--print-id", required=True)
    context.add_argument("--category")
    context.add_argument("--garment-template")
    context.add_argument("--fabric")
    context.add_argument("--feishu-doc")
    context.set_defaults(handler=command_set_context)

    record = sub.add_parser("record-file", help="Record the current file-evidence gate")
    record.add_argument("--project-dir", required=True)
    record.add_argument("--print-id", required=True)
    record.add_argument("--stage", choices=sorted(FILE_STAGES), required=True)
    record.add_argument("--file", action="append", required=True)
    record.add_argument(
        "--guard-report",
        help="Required for repeat_repair; JSON from seam_repair_guard.py apply",
    )
    record.add_argument(
        "--colour-report",
        help="Required for colour_spec; JSON from colour_role_spec.py",
    )
    record.set_defaults(handler=command_record_file)

    validation = sub.add_parser("record-validation", help="Record repeat validation JSON")
    validation.add_argument("--project-dir", required=True)
    validation.add_argument("--print-id", required=True)
    validation.add_argument("--report", required=True)
    validation.set_defaults(handler=command_record_validation)

    feishu = sub.add_parser("record-feishu", help="Verify a Feishu user readback")
    feishu.add_argument("--project-dir", required=True)
    feishu.add_argument("--print-id", required=True)
    feishu.add_argument("--doc-url", required=True)
    feishu.add_argument(
        "--readback-file",
        help="Optional saved fetch JSON for offline testing; otherwise fetch live as user",
    )
    feishu.set_defaults(handler=command_record_feishu)

    audit = sub.add_parser("audit", help="Run the final evidence and checksum audit")
    audit.add_argument("--project-dir", required=True)
    audit.add_argument("--print-id", required=True)
    audit.set_defaults(handler=command_audit)

    status = sub.add_parser("status", help="Show the full state and next required action")
    status.add_argument("--project-dir", required=True)
    status.add_argument("--print-id", required=True)
    status.set_defaults(handler=command_status)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        code, payload = args.handler(args)
    except (WorkflowError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 3
    print(json.dumps({"ok": code == 0, "data": payload}, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
