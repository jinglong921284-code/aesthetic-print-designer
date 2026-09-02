#!/usr/bin/env python3
"""Match exact or already-sampled HEX colours to a named Pantone TCX JSON library."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from colour_role_spec import (
    ColourSpecError,
    delta_e_2000,
    rgb_from_hex,
    srgb_to_lab,
)


STATUS = "screen_computed_candidate"
REQUIRED_FIELDS = ("tcx", "name", "hex", "r", "g", "b")


class QuickMatchError(RuntimeError):
    """A truthful quick-match input or database failure."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_database(path: Path, source: str) -> tuple[Path, str]:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise QuickMatchError(f"Pantone TCX database from {source} is not a file: {resolved}")
    return resolved, source


def resolve_database(
    argument: str | None,
    *,
    environment: Mapping[str, str] | None = None,
) -> tuple[Path, str]:
    env = os.environ if environment is None else environment
    if argument:
        return require_database(Path(argument), "--database")
    configured = env.get("PANTONE_TCX_DB")
    if configured:
        return require_database(Path(configured), "PANTONE_TCX_DB")
    raise QuickMatchError(
        "No Pantone TCX database configured. Supply --database or set PANTONE_TCX_DB "
        "to a local database you are authorized to use."
    )


def channel(value: Any, *, field: str, index: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255:
        raise QuickMatchError(
            f"Database entry {index} field {field} must be an integer from 0 to 255"
        )
    return value


def load_database(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise QuickMatchError(f"Pantone TCX database is not valid JSON: {exc}") from exc

    if not isinstance(payload, list) or not payload:
        raise QuickMatchError("Pantone TCX database must be a non-empty JSON array")

    colours: list[dict[str, Any]] = []
    seen_tcx: set[str] = set()
    for index, row in enumerate(payload, start=1):
        if not isinstance(row, dict):
            raise QuickMatchError(f"Database entry {index} must be an object")
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            raise QuickMatchError(
                f"Database entry {index} is missing required fields: {', '.join(missing)}"
            )

        tcx = row["tcx"]
        name = row["name"]
        if not isinstance(tcx, str) or not tcx.strip():
            raise QuickMatchError(f"Database entry {index} has an invalid tcx value")
        tcx = tcx.strip()
        if tcx in seen_tcx:
            raise QuickMatchError(f"Pantone TCX database contains duplicate tcx: {tcx}")
        seen_tcx.add(tcx)
        if not isinstance(name, str) or not name.strip():
            raise QuickMatchError(f"Database entry {index} has an invalid name")

        database_hex = row["hex"]
        if not isinstance(database_hex, str):
            raise QuickMatchError(f"Database entry {index} field hex must be a string")
        try:
            hex_rgb = rgb_from_hex(database_hex)
        except ColourSpecError as exc:
            raise QuickMatchError(f"Database entry {index} has invalid hex: {database_hex}") from exc
        rgb = tuple(
            channel(row[field], field=field, index=index) for field in ("r", "g", "b")
        )
        if rgb != hex_rgb:
            raise QuickMatchError(
                f"Database entry {index} hex does not match its r/g/b values: {tcx}"
            )

        colours.append(
            {
                "tcx": tcx,
                "name": name.strip().strip("'\""),
                "hex": database_hex.upper(),
                "rgb": rgb,
                "lab": srgb_to_lab(rgb),
            }
        )
    return colours


def match_colour(source_hex: str, colours: list[dict[str, Any]], top: int) -> dict[str, Any]:
    try:
        source_rgb = rgb_from_hex(source_hex)
    except ColourSpecError as exc:
        raise QuickMatchError(f"Invalid --hex value: {source_hex}") from exc
    source_lab = srgb_to_lab(source_rgb)
    ranked = sorted(
        (
            (delta_e_2000(source_lab, colour["lab"]), colour["tcx"], colour)
            for colour in colours
        ),
        key=lambda item: (item[0], item[1]),
    )
    matches = []
    for rank, (delta, _tcx, colour) in enumerate(ranked[:top], start=1):
        matches.append(
            {
                "rank": rank,
                "tcx": colour["tcx"],
                "name": colour["name"],
                "hex": colour["hex"],
                "rgb": list(colour["rgb"]),
                "delta_e00": round(float(delta), 4),
            }
        )
    return {
        "source_hex": source_hex.upper(),
        "source_rgb": list(source_rgb),
        "matches": matches,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Quickly match exact or already-sampled HEX colours to Pantone TCX candidates"
    )
    parser.add_argument("--database", help="Pantone TCX JSON database; overrides PANTONE_TCX_DB")
    parser.add_argument("--hex", dest="hex_values", action="append", required=True)
    parser.add_argument("--label", action="append")
    parser.add_argument("--top", type=int, default=3)
    return parser


def command_match(args: argparse.Namespace) -> dict[str, Any]:
    if args.top < 1:
        raise QuickMatchError("--top must be at least 1")
    if args.label is not None and len(args.label) != len(args.hex_values):
        raise QuickMatchError("The number of --label values must match the number of --hex values")
    if args.label is not None and any(not value.strip() for value in args.label):
        raise QuickMatchError("--label values must not be empty")

    database_path, database_source = resolve_database(args.database)
    colours = load_database(database_path)
    queries = []
    for index, source_hex in enumerate(args.hex_values):
        query = match_colour(source_hex, colours, args.top)
        query["label"] = args.label[index] if args.label is not None else None
        queries.append(query)

    return {
        "schema_version": 1,
        "status": STATUS,
        "scope": "chat_level_exact_hex_or_sampled_colour",
        "matching_method": "sRGB to Lab, CIEDE2000",
        "candidate_basis": (
            "Computed against the named local database; digital screen candidates only"
        ),
        "database": {
            "name": database_path.name,
            "source": database_source,
            "sha256": sha256(database_path),
            "entries": len(colours),
        },
        "requested_top": args.top,
        "queries": queries,
        "physical_review": {
            "status": "pending",
            "requirements": [
                "physical Pantone FHI Cotton TCX reference",
                "intended-fabric strike-off",
                "standard-light review",
            ],
        },
        "approval_boundary": (
            "Not a physical TCX approval, strike-off approval, production separation, "
            "or bulk-production approval"
        ),
        "writes": {"closure": False, "external_document": False, "files": False},
    }


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = command_match(args)
    except (QuickMatchError, OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 3
    print(json.dumps({"ok": True, "data": payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
