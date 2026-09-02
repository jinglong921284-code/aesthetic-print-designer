#!/usr/bin/env python3
"""Validate raster repeat edges and create offset/tiled diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops


def edge_metrics(a: np.ndarray, b: np.ndarray) -> dict[str, float | int]:
    delta = np.abs(a.astype(np.int16) - b.astype(np.int16))
    pixel_delta = delta.max(axis=-1)
    return {
        "mean_channel_difference": round(float(delta.mean()), 6),
        "max_channel_difference": int(delta.max()),
        "exact_pixel_match_percent": round(float((pixel_delta == 0).mean() * 100), 6),
        "pixels_over_10_percent": round(float((pixel_delta > 10).mean() * 100), 6),
        "pixels_over_30_percent": round(float((pixel_delta > 30).mean() * 100), 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--preview-size", type=int, default=2400)
    parser.add_argument(
        "--visual-status",
        choices=("pending", "pass", "revise", "fail"),
        default="pending",
        help="Human review result for the offset and 3x3 previews.",
    )
    parser.add_argument(
        "--visual-notes",
        default="",
        help="Short evidence-based note from the visual review.",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    image = Image.open(args.input).convert("RGB")
    arr = np.asarray(image)
    height, width = arr.shape[:2]

    stem = args.input.stem
    offset_path = args.out_dir / f"{stem}-offset-check.png"
    preview_path = args.out_dir / f"{stem}-3x3-check.png"
    report_path = args.out_dir / f"{stem}-validation.json"

    ImageChops.offset(image, width // 2, height // 2).save(offset_path)

    preview = Image.new("RGB", (width * 3, height * 3))
    for row in range(3):
        for col in range(3):
            preview.paste(image, (col * width, row * height))
    preview.thumbnail((args.preview_size, args.preview_size), Image.Resampling.NEAREST)
    preview.save(preview_path)

    unique_count = int(np.unique(arr.reshape(-1, 3), axis=0).shape[0])
    left_right = edge_metrics(arr[:, 0, :], arr[:, -1, :])
    top_bottom = edge_metrics(arr[0, :, :], arr[-1, :, :])
    edge_lock_pass = (
        left_right["exact_pixel_match_percent"] == 100.0
        and top_bottom["exact_pixel_match_percent"] == 100.0
    )
    if not edge_lock_pass:
        overall_status = "edge_lock_failed"
    elif args.visual_status == "pass":
        overall_status = "digital_seamless_repeat_passed"
    elif args.visual_status == "pending":
        overall_status = "pending_visual_review"
    else:
        overall_status = f"visual_{args.visual_status}"

    report = {
        "input": str(args.input.resolve()),
        "dimensions_px": [width, height],
        "unique_rgb_colors": unique_count,
        "left_vs_right": left_right,
        "top_vs_bottom": top_bottom,
        "edge_lock_pass": edge_lock_pass,
        "data_edge_pass": edge_lock_pass,
        "visual_review": {
            "status": args.visual_status,
            "notes": args.visual_notes,
            "checklist": [
                "central seam or clipped motif",
                "white pinhole, overlap, or width jump",
                "visible grid, track, or repeated island",
                "mirror diamond, pinwheel, face, or cross symmetry",
                "repeated focal point or uneven density rhythm",
            ],
        },
        "overall_status": overall_status,
        "offset_check": str(offset_path.resolve()),
        "tile_3x3_check": str(preview_path.resolve()),
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not edge_lock_pass:
        return 2
    if args.visual_status in {"revise", "fail"}:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
