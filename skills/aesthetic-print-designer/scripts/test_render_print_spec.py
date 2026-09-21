#!/usr/bin/env python3
"""Isolated visual exporter tests; all imagery and colour codes are fictional.

Run with the visual dependencies and pypdf installed. No sample is published.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw
from pypdf import PdfReader

from render_print_spec import DEFAULT_NOTICE, SpecError, render_pdf, validate_spec


def fixture(root: Path, count=9, size=(720, 400)):
    image_path = root / "numbered.png"
    image = Image.new("RGB", size, "white")
    drawing = ImageDraw.Draw(image)
    rows = []
    for index in range(1, count + 1):
        colour = f"#{(index * 593821) % 16777216:06X}"
        x0 = round((index - 1) * image.width / count)
        x1 = round(index * image.width / count)
        drawing.rectangle((x0, 0, x1, image.height), fill=colour)
        drawing.rectangle((x0 + 8, 14, x0 + 32, 36), fill="white")
        drawing.text((x0 + 12, 19), str(index), fill="black")
        rows.append({"id": index, "element": f"Test rectangle {index}", "source_hex": colour,
                     "candidate": {"status": "computed_candidate", "system": "Fixture", "code": f"TEST-{index:04d}",
                                   "name": f"Test colour {index}", "delta_e00": index / 10}})
    image.save(image_path)
    data = {
        "print_id": "TEST-PRINT-01", "print_name": "Abstract rectangle fixture",
        "colourway": "Synthetic test", "edition": "technical", "version": "v1", "date": "Test date",
        "status": "Draft", "artwork": {"path": "numbered.png", "callout_ids": list(range(1, count + 1)),
                                         "mapping_review": "Synthetic fixture; visual mapping review remains separate."},
        "colours": rows,
        "technical": {"source_artwork": "numbered.png", "pixel_dimensions": f"{size[0]} x {size[1]} px", "artwork_version": "fixture-v1"},
        "provenance": {"source_document": "Synthetic test record", "colour_library": "Fictional TEST codes - not Pantone",
                       "matching_method": "Carried over from test data; not recalculated by this exporter."},
        "technical_notes": ["Test values only. Physical review pending."],
    }
    return data, image_path


class VisualSpecTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="visual-spec-test-")
        self.root = Path(self.temp.name)
        self.data, self.image = fixture(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def valid(self, data=None):
        return validate_spec(copy.deepcopy(data or self.data), self.root)

    def test_nine_colours_two_pages_and_source_unchanged(self):
        before = hashlib.sha256(self.image.read_bytes()).hexdigest()
        data, _, image = self.valid()
        pdf = PdfReader(io.BytesIO(render_pdf(data, image)))
        self.assertEqual(len(pdf.pages), 2)
        text = "\n".join(page.extract_text() for page in pdf.pages)
        for row in self.data["colours"]:
            self.assertIn(row["source_hex"], text)
            self.assertIn(row["candidate"]["code"], text)
            self.assertIn(str(row["candidate"]["delta_e00"]), text)
        self.assertIn("not recalculated", text)
        self.assertGreaterEqual(text.count(DEFAULT_NOTICE), 3)
        self.assertIn("Draft", text)
        self.assertIn("fixture-v1", text)
        self.assertEqual(before, hashlib.sha256(self.image.read_bytes()).hexdigest())
        images = list(pdf.pages[0].images)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].image.size, (720, 400))
        self.assertEqual(images[0].image.convert("RGB").tobytes(), Image.open(self.image).tobytes())

    def test_pending_colours_and_null_source_hex(self):
        data, _ = fixture(self.root, 3)
        for row in data["colours"]:
            row["candidate"] = {"status": "pending"}
            row["source_hex"] = None
        data["provenance"] = {}
        verified, _, image = self.valid(data)
        text = "\n".join(page.extract_text() for page in PdfReader(io.BytesIO(render_pdf(verified, image))).pages)
        self.assertIn("Pending matching", text)
        self.assertNotIn("TEST-0001", text)
        self.assertIn("Not computed", " ".join(text.split()))

    def test_invalid_fields_fail_before_rendering(self):
        mutations = [
            lambda d: d["colours"][0].update(id=2),
            lambda d: d["artwork"].update(callout_ids=[1, 2]),
            lambda d: d["colours"][0].update(source_hex="#BAD"),
            lambda d: d.update(status="Approved for production"),
            lambda d: d["colours"][0]["candidate"].update(delta_e00=-1),
            lambda d: d["colours"][0]["candidate"].update(delta_e00=float("nan")),
            lambda d: d["colours"][0]["candidate"].update(status="pending"),
            lambda d: d["provenance"].update(matching_method="To be confirmed"),
            lambda d: d["provenance"].update(colour_library="Pending"),
            lambda d: d["artwork"].update(path="missing.png"),
            lambda d: d.update(forgotten_note="must not disappear"),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                mutation(data)
                with self.assertRaises(SpecError):
                    self.valid(data)

    def test_ready_for_sampling_requires_records(self):
        data = copy.deepcopy(self.data)
        data["status"] = "Ready for Sampling"
        with self.assertRaises(SpecError):
            self.valid(data)
        data["sampling_confirmations"] = {"version": "v1", "design": "Test reviewer A / current version",
                                           "merchandising": "Test reviewer B / current version",
                                           "pattern_room": "Test reviewer C / current version", "sampling_blockers": []}
        self.assertEqual(self.valid(data)[0]["status"], "Ready for Sampling")
        data["sampling_confirmations"]["version"] = "v0"
        with self.assertRaises(SpecError):
            self.valid(data)
        data["sampling_confirmations"]["version"] = "v1"
        data["sampling_confirmations"]["sampling_blockers"] = ["Missing required dimension"]
        with self.assertRaises(SpecError):
            self.valid(data)

    def test_overflow_and_uncovered_glyphs_fail(self):
        data, _, image = self.valid()
        data["technical_notes"] = ["Long note " * 1000]
        with self.assertRaisesRegex(SpecError, "exceeds"):
            render_pdf(data, image)
        data["technical_notes"] = []
        data["print_name"] = "测试"
        with self.assertRaisesRegex(SpecError, "Font lacks"):
            render_pdf(data, image)
        data["print_name"] = "Test"
        data["usage_notice"] = "Long notice " * 100
        with self.assertRaisesRegex(SpecError, "exceeds"):
            render_pdf(data, image)

    def test_max_colour_count(self):
        data, _ = fixture(self.root, 12)
        data, _, image = self.valid(data)
        self.assertEqual(len(PdfReader(io.BytesIO(render_pdf(data, image))).pages), 2)
        data, _ = fixture(self.root, 13)
        with self.assertRaisesRegex(SpecError, "1-12"):
            self.valid(data)

    def test_cli_relative_image_overwrite_and_atomic_failure(self):
        source = self.root / "spec.json"
        source.write_text(json.dumps(self.data), encoding="utf-8")
        destination = self.root / "sheet.pdf"
        script = Path(__file__).with_name("render_print_spec.py")
        command = [sys.executable, str(script), "--input", str(source), "--output", str(destination)]
        result = subprocess.run(command, cwd="/", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["pages"], 2)
        self.assertFalse(payload["mapping_verified"])
        self.assertFalse(payload["candidate_computation_performed"])
        before = destination.read_bytes()
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn("already exists", result.stderr)
        self.data["technical_notes"] = ["Long note " * 1000]
        source.write_text(json.dumps(self.data), encoding="utf-8")
        result = subprocess.run(command + ["--overwrite"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(destination.read_bytes(), before)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--fixture-dir":
        target = Path(sys.argv[2]).resolve()
        target.mkdir(parents=True, exist_ok=True)
        data, _ = fixture(target, size=(640, 640))
        data.update(series="Synthetic QA series", composition="Nine abstract rectangles", style="Geometric test only")
        source = target / "spec.json"
        source.write_text(json.dumps(data, indent=2), encoding="utf-8")
        validated, _, image = validate_spec(copy.deepcopy(data), target)
        pdf = target / "sheet.pdf"
        pdf.write_bytes(render_pdf(validated, image))
        print(json.dumps({"input": str(source), "output": str(pdf)}))
    else:
        unittest.main()
