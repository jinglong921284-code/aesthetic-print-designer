#!/usr/bin/env python3
"""Build a role-locked Pantone TCX colour specification without blind clustering."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


READY_STATUS = "colour_role_spec_ready"
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class ColourSpecError(RuntimeError):
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
        raise ColourSpecError(f"{label} is not a file: {path}")
    return path


def rgb_from_hex(value: str) -> tuple[int, int, int]:
    if not HEX_RE.match(value):
        raise ColourSpecError(f"Invalid source_hex: {value}")
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))


def hex_from_rgb(rgb: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def srgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    values = np.asarray(rgb, dtype=np.float64) / 255.0
    values = np.where(values <= 0.04045, values / 12.92, ((values + 0.055) / 1.055) ** 2.4)
    x, y, z = np.array(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
    ) @ values
    x, y, z = x / 0.95047, y / 1.0, z / 1.08883

    def f(value: float) -> float:
        delta = 6 / 29
        return value ** (1 / 3) if value > delta**3 else value / (3 * delta**2) + 4 / 29

    fx, fy, fz = f(float(x)), f(float(y)), f(float(z))
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e_2000(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2
    c1 = math.hypot(a1, b1)
    c2 = math.hypot(a2, b2)
    c_bar = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(c_bar**7 / (c_bar**7 + 25**7)))
    ap1, ap2 = (1 + g) * a1, (1 + g) * a2
    cp1, cp2 = math.hypot(ap1, b1), math.hypot(ap2, b2)

    def hp(ap: float, b: float) -> float:
        if ap == 0 and b == 0:
            return 0.0
        angle = math.degrees(math.atan2(b, ap))
        return angle + 360 if angle < 0 else angle

    hp1, hp2 = hp(ap1, b1), hp(ap2, b2)
    dl = l2 - l1
    dc = cp2 - cp1
    dhp = hp2 - hp1
    if cp1 * cp2 == 0:
        dhp = 0
    elif dhp > 180:
        dhp -= 360
    elif dhp < -180:
        dhp += 360
    dh = 2 * math.sqrt(cp1 * cp2) * math.sin(math.radians(dhp / 2))
    l_bar = (l1 + l2) / 2
    cp_bar = (cp1 + cp2) / 2
    if cp1 * cp2 == 0:
        hp_bar = hp1 + hp2
    elif abs(hp1 - hp2) <= 180:
        hp_bar = (hp1 + hp2) / 2
    elif hp1 + hp2 < 360:
        hp_bar = (hp1 + hp2 + 360) / 2
    else:
        hp_bar = (hp1 + hp2 - 360) / 2
    t = (
        1
        - 0.17 * math.cos(math.radians(hp_bar - 30))
        + 0.24 * math.cos(math.radians(2 * hp_bar))
        + 0.32 * math.cos(math.radians(3 * hp_bar + 6))
        - 0.20 * math.cos(math.radians(4 * hp_bar - 63))
    )
    sl = 1 + 0.015 * (l_bar - 50) ** 2 / math.sqrt(20 + (l_bar - 50) ** 2)
    sc = 1 + 0.045 * cp_bar
    sh = 1 + 0.015 * cp_bar * t
    rt = -2 * math.sqrt(cp_bar**7 / (cp_bar**7 + 25**7)) * math.sin(
        math.radians(60 * math.exp(-((hp_bar - 275) / 25) ** 2))
    )
    return math.sqrt(
        (dl / sl) ** 2
        + (dc / sc) ** 2
        + (dh / sh) ** 2
        + rt * (dc / sc) * (dh / sh)
    )


def load_library(path: Path) -> list[dict]:
    colours = []
    required = {"name", "tcx", "hex", "r", "g", "b"}
    seen_tcx: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ColourSpecError(
                "Pantone library is missing columns: " + ", ".join(sorted(missing))
            )
        for index, row in enumerate(reader, start=2):
            tcx = (row.get("tcx") or "").strip()
            name = (row.get("name") or "").strip().strip("'\"")
            if not tcx or not name:
                raise ColourSpecError(f"Pantone library row {index} needs name and tcx")
            if tcx in seen_tcx:
                raise ColourSpecError(f"Pantone library contains duplicate tcx: {tcx}")
            seen_tcx.add(tcx)
            try:
                rgb = tuple(int(row[channel_name]) for channel_name in ("r", "g", "b"))
            except (TypeError, ValueError) as exc:
                raise ColourSpecError(
                    f"Pantone library row {index} has non-integer RGB data"
                ) from exc
            if any(channel < 0 or channel > 255 for channel in rgb):
                raise ColourSpecError(
                    f"Pantone library row {index} RGB channels must be from 0 to 255"
                )
            library_hex = (row.get("hex") or "").upper()
            if rgb_from_hex(library_hex) != rgb:
                raise ColourSpecError(
                    f"Pantone library row {index} HEX does not match RGB: {tcx}"
                )
            colours.append(
                {
                    "name": name,
                    "tcx": tcx,
                    "hex": library_hex,
                    "rgb": rgb,
                    "lab": srgb_to_lab(rgb),
                }
            )
    if not colours:
        raise ColourSpecError("Pantone library is empty")
    return colours


def patch_median(array: np.ndarray, points: list[list[int]], radius: int) -> tuple[int, int, int]:
    height, width = array.shape[:2]
    pixels = []
    for point in points:
        if len(point) != 2:
            raise ColourSpecError("sample_points must contain [x, y]")
        x, y = int(point[0]), int(point[1])
        if not (0 <= x < width and 0 <= y < height):
            raise ColourSpecError(f"Sample point outside image: {point}")
        pixels.append(
            array[max(0, y - radius) : min(height, y + radius + 1), max(0, x - radius) : min(width, x + radius + 1)].reshape(-1, 3)
        )
    values = np.concatenate(pixels, axis=0)
    return tuple(int(value) for value in np.median(values, axis=0))


def nearest_point(array: np.ndarray, rgb: tuple[int, int, int]) -> tuple[int, int]:
    diff = array.astype(np.int32) - np.asarray(rgb, dtype=np.int32)
    distance = np.sum(diff * diff, axis=2)
    y, x = np.unravel_index(int(np.argmin(distance)), distance.shape)
    return int(x), int(y)


def confidence(delta: float) -> str:
    if delta <= 2.0:
        return "强数字近似；实体TCX与面料样布待复核"
    if delta <= 5.0:
        return "可参考；实体TCX与面料样布待复核"
    return "弱屏幕候选；必须实体TCX与面料样布复核"


def font(size: int) -> ImageFont.ImageFont:
    candidates = ("DejaVuSans.ttf", "Arial.ttf")
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def annotate(image: Image.Image, roles: list[dict], output: Path) -> None:
    canvas = image.convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    width, height = canvas.size
    radius = max(12, round(min(width, height) * 0.022))
    endpoint_radius = max(3, radius // 5)
    stroke = max(2, radius // 8)
    label_font = font(max(12, round(radius * 1.05)))
    directions = ((1, -1), (-1, -1), (1, 1), (-1, 1))
    offset = max(radius * 3, round(min(width, height) * 0.075))
    for index, role in enumerate(roles):
        x, y = role["sample_point"]
        dx, dy = directions[index % len(directions)]
        cx = min(max(radius + 2, x + dx * offset), width - radius - 2)
        cy = min(max(radius + 2, y + dy * offset), height - radius - 2)
        vx, vy = x - cx, y - cy
        length = max(1.0, math.hypot(vx, vy))
        px, py = -vy / length * (stroke + 1), vx / length * (stroke + 1)
        start_x, start_y = cx + vx / length * radius, cy + vy / length * radius
        for sign in (-1, 1):
            draw.line(
                [(start_x + sign * px, start_y + sign * py), (x + sign * px, y + sign * py)],
                fill="white",
                width=stroke,
            )
        draw.ellipse((x - endpoint_radius, y - endpoint_radius, x + endpoint_radius, y + endpoint_radius), outline="white", width=stroke)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline="white", width=stroke)
        text = str(role["id"])
        box = draw.textbbox((0, 0), text, font=label_font)
        tw, th = box[2] - box[0], box[3] - box[1]
        draw.text((cx - tw / 2, cy - th / 2 - box[1]), text, fill="black", font=label_font)
    canvas.save(output)


def command_build(args: argparse.Namespace) -> dict:
    image_path = require_file(args.image, "source artwork")
    roles_path = require_file(args.roles, "role definition")
    library_path = require_file(args.pantone_csv, "Pantone TCX library")
    out_dir = Path(args.out_dir).expanduser().resolve()
    fabric = args.fabric.strip() if args.fabric and args.fabric.strip() else None
    out_dir.mkdir(parents=True, exist_ok=True)
    with roles_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    roles_input = config.get("roles", [])
    ids = [role.get("id") for role in roles_input]
    if not roles_input or ids != list(range(1, len(roles_input) + 1)):
        raise ColourSpecError("Role IDs must be unique and sequential from 1")
    image = Image.open(image_path).convert("RGB")
    array = np.asarray(image)
    library = load_library(library_path)
    roles = []
    for role in roles_input:
        if not role.get("role") or not role.get("element"):
            raise ColourSpecError("Every role needs role and element labels")
        points = role.get("sample_points", [])
        sampled = patch_median(array, points, int(role.get("sample_radius_px", 3))) if points else None
        source_rgb = rgb_from_hex(role["source_hex"]) if role.get("source_hex") else sampled
        if source_rgb is None:
            raise ColourSpecError(f"Role {role['id']} needs source_hex or sample_points")
        source_lab = srgb_to_lab(source_rgb)
        match = min(library, key=lambda colour: delta_e_2000(source_lab, colour["lab"]))
        delta = delta_e_2000(source_lab, match["lab"])
        point = tuple(points[0]) if points else nearest_point(array, source_rgb)
        roles.append(
            {
                "id": role["id"],
                "role": role["role"],
                "element": role["element"],
                "source_hex": hex_from_rgb(source_rgb),
                "sampled_hex": hex_from_rgb(sampled) if sampled else None,
                "sample_point": list(point),
                "pantone_tcx": match["tcx"],
                "pantone_name": match["name"],
                "pantone_hex": match["hex"],
                "delta_e00": round(delta, 2),
                "confidence": confidence(delta),
            }
        )

    scale = min(1.0, 512 / max(image.size))
    analysis_image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))))
    pixels = np.asarray(analysis_image, dtype=np.int32).reshape(-1, 3)
    palette = np.asarray([rgb_from_hex(role["source_hex"]) for role in roles], dtype=np.int32)
    distances = np.sum((pixels[:, None, :] - palette[None, :, :]) ** 2, axis=2)
    assignment = np.argmin(distances, axis=1)
    counts = np.bincount(assignment, minlength=len(roles))
    for role, count in zip(roles, counts):
        role["approx_pixel_share_percent"] = round(float(count) / len(pixels) * 100, 2)

    annotation_path = out_dir / f"{image_path.stem}-colour-role-annotation.png"
    annotate(image, roles, annotation_path)
    report_path = out_dir / f"{image_path.stem}-colour-role-spec.json"
    report = {
        "schema_version": 1,
        "status": READY_STATUS,
        "roles_locked": True,
        "source_image": str(image_path),
        "source_image_sha256": sha256(image_path),
        "source_dimensions_px": list(image.size),
        "annotation_image": str(annotation_path),
        "annotation_image_sha256": sha256(annotation_path),
        "role_definition": str(roles_path),
        "role_definition_sha256": sha256(roles_path),
        "pantone_library": str(library_path),
        "pantone_library_sha256": sha256(library_path),
        "matching_method": "sRGB to Lab, CIEDE2000",
        "share_method": "nearest locked role on resized sRGB image; composition estimate, not ink volume",
        "fabric": fabric,
        "roles": roles,
        "dropped_roles": [],
        "physical_review": {
            "status": "pending",
            "requirements": [
                "physical colour reference for the selected colour system",
                fabric or "confirmed fabric specification",
                "actual-fabric strike-off",
                "standard-light review",
            ],
        },
    }
    write_json(report_path, report)
    markdown_path = out_dir / f"{image_path.stem}-colour-role-spec.md"
    lines = [
        f"# {image_path.stem}｜颜色角色规格",
        "",
        f"匹配方法：{report['matching_method']}  ",
        f"色库：{library_path.name}  ",
        f"面料：{fabric or '待确认'}  ",
        "",
        "| 标注 | 颜色角色 | 元素 | 源图 HEX | Pantone TCX | 色名 / ΔE00 | 近似占比 |",
        "|---:|---|---|---|---|---|---:|",
    ]
    for role in roles:
        lines.append(
            f"| {role['id']} | {role['role']} | {role['element']} | {role['source_hex']} | "
            f"{role['pantone_tcx']} TCX | {role['pantone_name']} / {role['delta_e00']:.2f} | "
            f"{role['approx_pixel_share_percent']:.2f}% |"
        )
    lines.extend(["", "Pantone为数字匹配候选；必须使用实体TCX色卡与实际面料样布复核。", ""])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    report["markdown_spec"] = str(markdown_path)
    report["markdown_spec_sha256"] = sha256(markdown_path)
    write_json(report_path, report)
    return {"report": str(report_path), **report}


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a role-locked Pantone TCX print specification")
    parser.add_argument("--image", required=True)
    parser.add_argument("--roles", required=True)
    parser.add_argument("--pantone-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--fabric")
    parser.set_defaults(handler=command_build)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = args.handler(args)
    except (ColourSpecError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 3
    print(json.dumps({"ok": True, "data": payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
