#!/usr/bin/env python3
"""Finalize an already half-offset/repaired repeat candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def parse_hex(value: str) -> np.ndarray:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError(f"Invalid hex colour: {value}")
    try:
        return np.array(
            [int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)],
            dtype=np.uint8,
        )
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid hex colour: {value}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--palette",
        help="Comma-separated approved hex colours, for example #F6F1E5,#1F2122",
    )
    args = parser.parse_args()

    image = Image.open(args.input).convert("RGB")
    arr = np.asarray(image).copy()

    if args.palette:
        palette = np.stack([parse_hex(item) for item in args.palette.split(",")])
        pixels = arr.reshape(-1, 3).astype(np.int32)
        distances = ((pixels[:, None, :] - palette[None, :, :].astype(np.int32)) ** 2).sum(axis=2)
        arr = palette[distances.argmin(axis=1)].reshape(arr.shape)

    # The candidate must already be half-offset with repaired central seams.
    # Its outer boundaries therefore represent adjacent interior rows/columns.
    arr[:, -1, :] = arr[:, 0, :]
    arr[-1, :, :] = arr[0, :, :]
    arr[-1, -1, :] = arr[0, 0, :]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr.astype(np.uint8), mode="RGB").save(args.output)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
