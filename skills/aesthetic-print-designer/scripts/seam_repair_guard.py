#!/usr/bin/env python3
"""Prepare and enforce a protected central-cross repair for seamless repeats."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


STATUS_READY = "protected_repair_ready"


class GuardError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise GuardError(f"{label} is not a file: {path}")
    return path


def image_for_work(path: Path) -> Image.Image:
    image = Image.open(path)
    return image.convert("RGBA" if image.mode == "RGBA" else "RGB")


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def central_cross_mask(width: int, height: int, band_px: int) -> np.ndarray:
    if band_px < 2 or band_px >= min(width, height):
        raise GuardError("band-px must be at least 2 and smaller than the image")
    x0 = width // 2 - band_px // 2
    x1 = x0 + band_px
    y0 = height // 2 - band_px // 2
    y1 = y0 + band_px
    mask = np.zeros((height, width), dtype=np.uint8)
    mask[:, x0:x1] = 255
    mask[y0:y1, :] = 255
    return mask


def command_prepare(args: argparse.Namespace) -> dict:
    tile_path = require_file(args.tile, "source tile")
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    image = image_for_work(tile_path)
    array = np.asarray(image)
    height, width = array.shape[:2]
    band_px = args.band_px or max(8, round(min(width, height) * args.band_percent / 100))
    mask_array = central_cross_mask(width, height, band_px)

    offset_array = np.roll(array, shift=(height // 2, width // 2), axis=(0, 1))
    offset_path = out_dir / f"{tile_path.stem}-half-offset.png"
    Image.fromarray(offset_array, mode=image.mode).save(offset_path)

    mask_path = out_dir / f"{tile_path.stem}-central-cross-mask.png"
    Image.fromarray(mask_array, mode="L").save(mask_path)

    overlay = Image.fromarray(offset_array, mode=image.mode).convert("RGBA")
    protected = np.zeros((height, width, 4), dtype=np.uint8)
    protected[mask_array == 0] = (220, 35, 55, 82)
    overlay = Image.alpha_composite(overlay, Image.fromarray(protected, mode="RGBA"))
    overlay_path = out_dir / f"{tile_path.stem}-protected-zone-preview.png"
    overlay.save(overlay_path)

    manifest_path = out_dir / f"{tile_path.stem}-seam-guard-manifest.json"
    manifest = {
        "schema_version": 1,
        "status": "repair_mask_prepared",
        "source_tile": str(tile_path),
        "source_tile_sha256": sha256(tile_path),
        "dimensions_px": [width, height],
        "mode": image.mode,
        "band_px": band_px,
        "band_percent_actual": round(band_px / min(width, height) * 100, 3),
        "half_offset": str(offset_path),
        "half_offset_sha256": sha256(offset_path),
        "central_cross_mask": str(mask_path),
        "central_cross_mask_sha256": sha256(mask_path),
        "protected_zone_preview": str(overlay_path),
        "instruction": "Edit only the white central cross. Red protected pixels are locked.",
    }
    write_json(manifest_path, manifest)
    return {"manifest": str(manifest_path), **manifest}


def command_apply(args: argparse.Namespace) -> dict:
    manifest_path = require_file(args.manifest, "seam guard manifest")
    edited_path = require_file(args.edited, "edited half-offset image")
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    original_path = require_file(manifest["half_offset"], "locked half-offset image")
    mask_path = require_file(manifest["central_cross_mask"], "central-cross mask")
    if sha256(original_path) != manifest["half_offset_sha256"]:
        raise GuardError("Locked half-offset image changed after mask preparation")
    if sha256(mask_path) != manifest["central_cross_mask_sha256"]:
        raise GuardError("Central-cross mask changed after preparation")

    original_image = image_for_work(original_path)
    edited_image = image_for_work(edited_path).convert(original_image.mode)
    if edited_image.size != original_image.size:
        raise GuardError("Edited image dimensions do not match the locked half-offset image")
    mask_image = Image.open(mask_path).convert("L")
    if mask_image.size != original_image.size:
        raise GuardError("Mask dimensions do not match the repair image")

    binary = np.asarray(mask_image, dtype=np.float32) / 255.0
    if args.feather_px > 0:
        blurred = np.asarray(
            mask_image.filter(ImageFilter.GaussianBlur(radius=args.feather_px)),
            dtype=np.float32,
        ) / 255.0
        alpha = blurred * binary
    else:
        alpha = binary
    alpha = alpha[:, :, None]
    original = np.asarray(original_image, dtype=np.float32)
    edited = np.asarray(edited_image, dtype=np.float32)
    guarded = np.rint(original * (1.0 - alpha) + edited * alpha).clip(0, 255).astype(np.uint8)
    outside = binary == 0
    inside = ~outside
    outside_changed = int(np.any(guarded != original.astype(np.uint8), axis=2)[outside].sum())
    inside_changed = int(np.any(guarded != original.astype(np.uint8), axis=2)[inside].sum())
    if outside_changed != 0:
        raise GuardError("Protected pixels changed outside the central-cross mask")

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(guarded, mode=original_image.mode).save(output_path)

    delta = np.max(np.abs(guarded.astype(np.int16) - original.astype(np.int16)), axis=2).astype(np.uint8)
    heat = np.zeros((guarded.shape[0], guarded.shape[1], 3), dtype=np.uint8)
    heat[:, :, 0] = delta
    heat[:, :, 2] = delta // 2
    heat[inside & (delta == 0)] = (30, 30, 30)
    heatmap_path = output_path.with_name(f"{output_path.stem}-difference-heatmap.png")
    Image.fromarray(heat, mode="RGB").save(heatmap_path)

    report_path = output_path.with_name(f"{output_path.stem}-seam-guard-report.json")
    report = {
        "schema_version": 1,
        "status": STATUS_READY,
        "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "edited_half_offset": str(edited_path),
        "edited_half_offset_sha256": sha256(edited_path),
        "guarded_half_offset": str(output_path),
        "guarded_half_offset_sha256": sha256(output_path),
        "difference_heatmap": str(heatmap_path),
        "difference_heatmap_sha256": sha256(heatmap_path),
        "dimensions_px": list(original_image.size),
        "band_px": manifest["band_px"],
        "feather_px": args.feather_px,
        "inside_mask_changed_pixels": inside_changed,
        "outside_mask_changed_pixels": outside_changed,
        "outside_mask_exact_match_percent": 100.0,
        "next_action": "finalize the guarded half-offset, then rerun repeat validation",
    }
    write_json(report_path, report)
    return {"report": str(report_path), **report}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Protect non-seam pixels during repeat repair")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="Create half-offset, central-cross mask, and preview")
    prepare.add_argument("--tile", required=True)
    prepare.add_argument("--out-dir", required=True)
    prepare.add_argument("--band-px", type=int)
    prepare.add_argument("--band-percent", type=float, default=8.0)
    prepare.set_defaults(handler=command_prepare)

    apply = sub.add_parser("apply", help="Composite only the permitted repair zone")
    apply.add_argument("--manifest", required=True)
    apply.add_argument("--edited", required=True)
    apply.add_argument("--output", required=True)
    apply.add_argument("--feather-px", type=float, default=4.0)
    apply.set_defaults(handler=command_apply)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = args.handler(args)
    except (GuardError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 3
    print(json.dumps({"ok": True, "data": payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
