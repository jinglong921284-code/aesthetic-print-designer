#!/usr/bin/env python3
"""Render an existing numbered artwork and supplied data as a two-page PDF.

No artwork editing, sampling, candidate computation, or approval occurs here.
Relative artwork paths resolve against the input JSON, not the working directory.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from xml.sax.saxutils import escape


DEFAULT_NOTICE = "Artwork shown is for reference only. No other use is permitted."
STATUSES = {"Draft", "Design Alignment", "Ready for Sampling", "Revise"}
TECHNICAL = {
    "print_type": "Print type", "physical_size": "Physical size", "scale": "Scale",
    "repeat_placement": "Repeat / placement", "fabric": "Fabric", "process": "Process",
    "resolution": "Resolution / DPI", "colour_mode": "Colour mode", "icc_profile": "ICC profile",
    "production_colour_count": "Production colour count", "source_artwork": "Source artwork file",
    "pixel_dimensions": "Pixel dimensions", "artwork_version": "Artwork version",
}


class SpecError(ValueError):
    """Input or layout cannot be rendered faithfully."""


def require_text(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpecError(f"{field} must be a non-empty string.")
    if any(ord(char) < 32 and char not in "\n\t" for char in value):
        raise SpecError(f"{field} contains unsupported control characters.")
    return value


def _real_record(value, field):
    value = require_text(value, field)
    if value.strip().lower() in {"pending", "to be confirmed", "tbc", "unknown", "n/a", "none"}:
        raise SpecError(f"{field} requires a recorded source or confirmation, not a placeholder.")
    return value


def _only_keys(obj, keys, field):
    if not isinstance(obj, dict):
        raise SpecError(f"{field} must be an object.")
    unknown = set(obj) - set(keys)
    if unknown:
        raise SpecError(f"Unknown {field} field(s): {', '.join(sorted(unknown))}. Nothing is silently omitted.")


def validate_spec(data: dict, base_dir: Path) -> tuple[dict, Path, bytes]:
    _only_keys(data, {"print_id", "print_name", "colourway", "edition", "version", "date", "status",
                     "artwork", "colours", "technical", "provenance", "technical_notes", "usage_notice",
                     "sampling_confirmations", "series", "composition", "style"}, "spec")
    for key in ("print_id", "print_name", "version", "status"):
        require_text(data.get(key), key)
    if data["status"] not in STATUSES:
        raise SpecError(f"status must be one of: {', '.join(sorted(STATUSES))}.")
    data.setdefault("edition", "colour")
    if data["edition"] not in {"colour", "technical"}:
        raise SpecError("edition must be colour or technical.")
    for key in ("colourway", "date"):
        data.setdefault(key, "To be confirmed")
        require_text(data[key], key)
    for key in ("series", "composition", "style"):
        if key in data:
            require_text(data[key], key)
    data.setdefault("usage_notice", DEFAULT_NOTICE)
    require_text(data["usage_notice"], "usage_notice")
    artwork = data.get("artwork")
    _only_keys(artwork, {"path", "callout_ids", "mapping_review"}, "artwork")
    path = Path(require_text(artwork.get("path"), "artwork.path")).expanduser()
    path = (base_dir / path).resolve() if not path.is_absolute() else path.resolve()
    require_text(artwork.get("mapping_review"), "artwork.mapping_review")
    rows = data.get("colours")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 12:
        raise SpecError("colours must contain 1-12 representative colours; longer sheets need a custom layout.")
    ids = list(range(1, len(rows) + 1))
    if artwork.get("callout_ids") != ids or any(type(x) is not int for x in artwork.get("callout_ids", [])):
        raise SpecError("artwork.callout_ids must declare the same sequential 1..N IDs as the colour rows; visually verify the image separately.")
    has_delta = False
    for index, row in enumerate(rows, 1):
        _only_keys(row, {"id", "element", "source_hex", "candidate"}, f"colours[{index}]")
        if type(row.get("id")) is not int or row["id"] != index:
            raise SpecError("Colour IDs must be sequential 1..N in image callout order, without gaps or duplicates.")
        require_text(row.get("element"), f"colours[{index}].element")
        if "source_hex" not in row or (row["source_hex"] is not None and
                (not isinstance(row["source_hex"], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", row["source_hex"]))):
            raise SpecError(f"colours[{index}].source_hex must be a six-digit #RRGGBB source colour or null for pending.")
        candidate = row.get("candidate")
        _only_keys(candidate, {"status", "system", "code", "name", "delta_e00"}, f"colours[{index}].candidate")
        status = candidate.get("status")
        if status not in {"pending", "screen_candidate", "computed_candidate"}:
            raise SpecError("candidate.status must be pending, screen_candidate, or computed_candidate.")
        if status == "pending":
            if set(candidate) != {"status"}:
                raise SpecError("A pending candidate must not contain a claimed code, name, system, or delta.")
        else:
            for key in ("system", "code", "name"):
                require_text(candidate.get(key), f"colours[{index}].candidate.{key}")
        if "delta_e00" in candidate:
            delta = candidate["delta_e00"]
            if status != "computed_candidate" or type(delta) not in (int, float) or not math.isfinite(delta) or delta < 0:
                raise SpecError("delta_e00 requires computed_candidate and a finite non-negative numeric value.")
            has_delta = True
        elif status == "computed_candidate":
            raise SpecError("computed_candidate requires delta_e00; use screen_candidate if no recorded computation is available.")
    technical = data.setdefault("technical", {})
    _only_keys(technical, TECHNICAL, "technical")
    for key in TECHNICAL:
        technical.setdefault(key, "To be confirmed")
        require_text(technical[key], f"technical.{key}")
    provenance = data.setdefault("provenance", {})
    _only_keys(provenance, {"source_document", "colour_library", "matching_method"}, "provenance")
    for key in ("source_document", "colour_library", "matching_method"):
        provenance.setdefault(key, "To be confirmed")
        require_text(provenance[key], f"provenance.{key}")
    if has_delta:
        for key in ("source_document", "colour_library", "matching_method"):
            _real_record(provenance[key], f"provenance.{key} (required for supplied delta_e00)")
    notes = data.setdefault("technical_notes", [])
    if not isinstance(notes, list) or any(not isinstance(note, str) or not note.strip() for note in notes):
        raise SpecError("technical_notes must be a list of non-empty strings.")
    for note in notes:
        require_text(note, "technical_notes")
    if "sampling_confirmations" in data:
        confirmations = data["sampling_confirmations"]
        _only_keys(confirmations, {"version", "design", "merchandising", "pattern_room", "sampling_blockers"}, "sampling_confirmations")
        for key in ("version", "design", "merchandising", "pattern_room"):
            _real_record(confirmations.get(key), f"sampling_confirmations.{key}")
        blockers = confirmations.get("sampling_blockers")
        if not isinstance(blockers, list):
            raise SpecError("sampling_confirmations.sampling_blockers must be a list.")
        for blocker in blockers:
            require_text(blocker, "sampling_confirmations.sampling_blockers")
    if data["status"] == "Ready for Sampling":
        confirmations = data.get("sampling_confirmations", {})
        if not confirmations or confirmations["version"] != data["version"] or confirmations["sampling_blockers"]:
            raise SpecError("Ready for Sampling requires current-version design, merchandising and pattern-room records and an empty sampling_blockers list.")
    from PIL import Image
    try:
        image_bytes = path.read_bytes()
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.verify()
        with Image.open(io.BytesIO(image_bytes)) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise SpecError("artwork.path must be a single-frame image; choose the exact existing numbered artwork.")
            if image.mode not in {"RGB", "RGBA", "L", "LA", "P"}:
                raise SpecError("Use an existing RGB/RGBA or greyscale numbered preview; this exporter does not colour-convert production artwork.")
            if image.getexif().get(274, 1) != 1:
                raise SpecError("Artwork has EXIF rotation; supply a confirmed orientation-normalized numbered preview.")
            image.load()
    except SpecError:
        raise
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise SpecError(f"Cannot read artwork.path as an image: {exc}") from exc
    return data, path, image_bytes


def _all_text(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _all_text(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _all_text(value)


def render_pdf(data: dict, image_bytes: bytes, regular: Path | None = None, bold: Path | None = None) -> bytes:
    from PIL import Image
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Flowable, Paragraph, Table, TableStyle

    font, heading = "Helvetica", "Helvetica-Bold"
    strings = list(_all_text({key: value for key, value in data.items() if key != "artwork"}))
    strings.append(data["artwork"]["mapping_review"])
    chars = set("".join(strings)) - {"\n", "\t"}
    if bold and not regular:
        raise SpecError("--font-bold requires --font-regular.")
    if regular:
        try:
            pdfmetrics.registerFont(TTFont("SpecRegular", str(regular)))
            pdfmetrics.registerFont(TTFont("SpecBold", str(bold or regular)))
        except Exception as exc:
            raise SpecError(f"Cannot load the supplied TTF font: {exc}") from exc
        font, heading = "SpecRegular", "SpecBold"
        missing = {char for name in (font, heading) for char in chars
                   if ord(char) not in pdfmetrics.getFont(name).face.charToGlyph}
    else:
        # WinAnsi Helvetica is deliberately not a silent CJK fallback.
        missing = set()
        for char in chars:
            try:
                char.encode("cp1252")
            except UnicodeEncodeError:
                missing.add(char)
    if missing:
        codes = ", ".join(f"U+{ord(char):04X}" for char in sorted(missing)[:12])
        raise SpecError(f"Font lacks required characters ({codes}); supply --font-regular and optionally --font-bold with covering TTF fonts.")
    pdfmetrics.registerFontFamily(font, normal=font, bold=heading, italic=font, boldItalic=heading)
    width, height = A4
    margin, bottom = 40, 77
    content = width - margin * 2
    ink, muted, grid, pale = [colors.HexColor(code) for code in ("#202824", "#616D65", "#D5DCD7", "#F3F5F2")]
    stream = io.BytesIO()
    page = canvas.Canvas(stream, pagesize=A4, pageCompression=1)
    page.setTitle(f"{data['print_id']} - {data['print_name']} - Print Specification Sheet")
    page.setAuthor("Print Specification Sheet")
    page.setSubject("Design-stage specification; not production approval.")

    def paragraph(text, size=9, bold=False):
        return Paragraph(escape(str(text)).replace("\n", "<br/>"), ParagraphStyle(
            "spec", fontName=heading if bold else font, fontSize=size, leading=size * 1.3,
            textColor=ink, wordWrap="CJK" if regular else None, splitLongWords=1))

    def block(text, top, size=9, bold=False, x=margin, w=content, floor=bottom):
        p = paragraph(text, size, bold)
        _, ph = p.wrap(w, height)
        if top - ph < floor:
            raise SpecError("Content exceeds the fixed two-page layout. Shorten the fields/notes or use a custom multi-page layout; no content was clipped or font-shrunk.")
        p.drawOn(page, x, top - ph)
        return top - ph

    def table(rows, widths, top, header=True, size=8.3):
        cells = [[paragraph(cell, size, header and rownum == 0) if not isinstance(cell, Flowable) else cell
                  for cell in row] for rownum, row in enumerate(rows)]
        t = Table(cells, colWidths=widths, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), .4, grid),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, int(header)), (-1, -1), [colors.white, pale]),
        ] + ([("BACKGROUND", (0, 0), (-1, 0), grid)] if header else [])))
        _, th = t.wrap(content, height)
        if top - th < bottom:
            raise SpecError("Table exceeds the fixed two-page layout. Shorten fields or use a custom multi-page layout; no rows were dropped.")
        t.drawOn(page, margin, top - th)
        return top - th

    def frame(title, number):
        kicker = f"{data['series']} / PRINT SPECIFICATION SHEET" if "series" in data else "PRINT SPECIFICATION SHEET"
        top = block(kicker, height - 32, 8.5, True)
        top = block(title, top - 12, 21, True)
        top = block(f"{data['print_id']}  |  {data['colourway']}  |  {data['status']}", top - 7, 9.5)
        # Footer is measured independently and must not collide with content.
        footer_text = f"{data['print_id']}  |  {data['version']}  |  {data['date']}  |  {number} / 2"
        block(footer_text, 62, 8, w=content, floor=41)
        block(data["usage_notice"], 37, 7.5, floor=15)
        return top - 15

    class Swatch(Flowable):
        def __init__(self, value):
            super().__init__()
            self.width, self.height, self.value = 17, 15, value
        def draw(self):
            self.canv.setFillColor(colors.HexColor(self.value) if self.value else colors.white)
            self.canv.setStrokeColor(grid)
            self.canv.rect(0, 0, self.width, self.height, stroke=1, fill=1)
            if self.value is None:
                self.canv.line(0, 0, self.width, self.height)

    tech = data["technical"]
    rows = data["colours"]
    top = frame(data["print_name"], 1)
    edition = "Colour specification edition" if data["edition"] == "colour" else "Technical specification edition"
    top = block(edition, top, 9) - 10
    top = table([
        ["Print type", tech["print_type"], "Representative colours", str(len(rows))],
        ["Physical size", tech["physical_size"], "Artwork scale", tech["scale"]],
    ], [83, content / 2 - 83, 100, content / 2 - 100], top, header=False)
    # Reserve text and palette area before calculating the intact image fit.
    art_top, art_bottom = top - 14, 222
    art_height = art_top - art_bottom
    if art_height < 230:
        raise SpecError("Page 1 metadata leaves insufficient artwork space. Shorten metadata or use a custom layout.")
    with Image.open(io.BytesIO(image_bytes)) as source:
        iw, ih = source.size
    factor = min(content / iw, art_height / ih)
    dw, dh = iw * factor, ih * factor
    page.drawImage(ImageReader(io.BytesIO(image_bytes)), (width - dw) / 2, art_bottom + (art_height - dh) / 2,
                   width=dw, height=dh, mask="auto", preserveAspectRatio=True)
    top = block(data["usage_notice"], art_bottom - 8, 8.3)
    top = block(f"Declared callouts 1-{len(rows)} match the row sequence. Image correspondence requires visual review.", top - 7, 8.1)
    top = block("PALETTE OVERVIEW - source HEX, not approved production inks", top - 12, 8.5, True) - 7
    cell_width = content / len(rows)
    for index, row in enumerate(rows):
        x = margin + index * cell_width
        page.setStrokeColor(grid)
        page.setFillColor(colors.HexColor(row["source_hex"]) if row["source_hex"] else colors.white)
        page.rect(x, top - 16, cell_width - 6, 16, fill=1, stroke=1)
        if row["source_hex"] is None:
            page.line(x, top - 16, x + cell_width - 6, top)
        block(f"{row['id']:02d}\n{row['source_hex'] or 'Pending'}", top - 20, 7.5, x=x, w=cell_width - 4)
    top -= 44
    for key in ("composition", "style"):
        if key in data:
            top = block(f"{key.capitalize()}: {data[key]}", top - 3, 8) - 1
    page.showPage()

    top = frame("Colour & technical details", 2)
    colour_table = [["No.", "Chip", "Element / role", "Source HEX", "Named-colour candidate", "Delta E00"]]
    for row in rows:
        candidate = row["candidate"]
        if candidate["status"] == "pending":
            label, delta = "Pending matching", "Not computed"
        else:
            kind = "computed" if candidate["status"] == "computed_candidate" else "screen"
            label = f"{candidate['system']} {candidate['code']}\n{candidate['name']} ({kind.lower()})"
            delta = str(candidate["delta_e00"]) if "delta_e00" in candidate else "Not computed"
        colour_table.append([str(row["id"]), Swatch(row["source_hex"]), row["element"], row["source_hex"] or "Pending", label, delta])
    top = table(colour_table, [28, 35, 100, 66, content - 283, 54], top, size=8)
    top = block("TECHNICAL FIELDS", top - 13, 9, True) - 7
    pairs = [(label, tech[key]) for key, label in TECHNICAL.items() if key not in {"print_type", "physical_size", "scale"}]
    technical_rows = []
    for start in range(0, len(pairs), 2):
        group = pairs[start:start + 2]
        technical_rows.append([item for pair in group for item in pair] + (["", ""] if len(group) == 1 else []))
    top = table(technical_rows, [77, content / 2 - 77, 77, content / 2 - 77], top, header=False, size=8)
    top = block("SOURCE, METHOD & REVIEW", top - 13, 9, True) - 6
    provenance = data["provenance"]
    for label, text in (("Source", provenance["source_document"]), ("Library", provenance["colour_library"]),
                        ("Method", provenance["matching_method"]), ("Callout review", data["artwork"]["mapping_review"])):
        top = block(f"{label}: {text}", top, 8) - 3
    for note in data["technical_notes"]:
        top = block(f"Note: {note}", top, 8) - 3
    if "sampling_confirmations" in data:
        confirmations = data["sampling_confirmations"]
        summary = "; ".join(f"{key.replace('_', ' ')}: {confirmations[key]}" for key in ("version", "design", "merchandising", "pattern_room"))
        top = block("Sampling records: " + summary, top, 8) - 3
        top = block("Sampling blockers: " + ("; ".join(confirmations["sampling_blockers"]) or "None recorded"), top, 8) - 3
    block("Supplied candidates/deltas are reproduced, not recomputed or authenticated. Physical colour, fabric and production approval are separate gates.", top - 4, 8)
    page.showPage()
    page.save()
    return stream.getvalue()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Specification JSON; relative image paths resolve here.")
    parser.add_argument("--output", type=Path, required=True, help="Two-page PDF (will not overwrite by default).")
    parser.add_argument("--font-regular", type=Path, help="Optional user-supplied TTF covering all document characters.")
    parser.add_argument("--font-bold", type=Path, help="Optional corresponding bold TTF.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output PDF after successful rendering.")
    args = parser.parse_args(argv)
    try:
        try:
            import reportlab  # noqa: F401
            import PIL  # noqa: F401
        except ImportError as exc:
            raise SpecError("Visual PDF dependencies missing. Install with: python3 -m pip install -r requirements-visual.txt; then use that interpreter or set PRINT_DESIGNER_PYTHON.") from exc
        source = args.input.expanduser().resolve()
        data = json.loads(source.read_text(encoding="utf-8"))
        data, artwork_path, image_bytes = validate_spec(data, source.parent)
        destination = args.output.expanduser().resolve()
        if destination.suffix.lower() != ".pdf":
            raise SpecError("--output must have a .pdf extension.")
        protected = {source, artwork_path}
        protected.update(path.expanduser().resolve() for path in (args.font_regular, args.font_bold) if path)
        if destination in protected:
            raise SpecError("The output must not replace an input file.")
        if destination.exists() and not args.overwrite:
            raise SpecError("Output already exists; choose another path or explicitly pass --overwrite.")
        pdf = render_pdf(data, image_bytes, args.font_regular, args.font_bold)
        destination.parent.mkdir(parents=True, exist_ok=True)
        # No partial PDF is left behind when layout validation fails.
        if args.overwrite:
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".print-spec-", suffix=".pdf", delete=False) as temp:
                    temp_path = Path(temp.name)
                    temp.write(pdf)
                os.replace(temp_path, destination)
            finally:
                if temp_path and temp_path.exists():
                    temp_path.unlink()
        else:
            with destination.open("xb") as output:
                output.write(pdf)
        print(json.dumps({"ok": True, "output": str(destination), "pages": 2,
                          "status": data["status"], "representative_colour_count": len(data["colours"]),
                          "artwork_sha256": hashlib.sha256(image_bytes).hexdigest(),
                          "mapping_verified": False, "candidate_computation_performed": False}))
        return 0
    except (SpecError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
