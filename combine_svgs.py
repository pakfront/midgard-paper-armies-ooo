#!/usr/bin/env python3
"""Pack SVG files onto a single printable page, preserving their physical size.

Each input SVG keeps its declared width/height (mm, cm, in, pt, pc, px), so a
44mm-wide standee is still 44mm wide on the combined sheet when printed at 100%.

Usage:
    python3 combine_svgs.py                      # all SVGs under output/, Letter portrait
    python3 combine_svgs.py output/imagegen/*.svg -o sheet.svg --page a4
    python3 combine_svgs.py --landscape --margin 8 --gap 3 --labels
"""

import argparse
import re
import sys
from pathlib import Path

MM_PER_UNIT = {
    "mm": 1.0,
    "cm": 10.0,
    "in": 25.4,
    "pt": 25.4 / 72,
    "pc": 25.4 / 6,
    "px": 25.4 / 96,
    "": 25.4 / 96,  # unitless = CSS px
}

PAGES_MM = {
    "a4": (210.0, 297.0),
    "a3": (297.0, 420.0),
    "letter": (215.9, 279.4),
    "legal": (215.9, 355.6),
}

ROOT_TAG_RE = re.compile(r"<svg\b[^>]*>", re.S)
ATTR_RE = r'\b{}\s*=\s*"([^"]*)"'


def get_attr(tag, name):
    m = re.search(ATTR_RE.format(name), tag)
    return m.group(1) if m else None


def drop_attr(tag, name):
    return re.sub(r"\s" + ATTR_RE.format(name), "", tag)


def to_mm(value):
    m = re.fullmatch(r"\s*([0-9.eE+-]+)\s*([a-z]*)\s*", value or "")
    if not m or m.group(2) not in MM_PER_UNIT:
        raise ValueError(f"unsupported length {value!r}")
    return float(m.group(1)) * MM_PER_UNIT[m.group(2)]


def fmt(n):
    return f"{n:.4f}".rstrip("0").rstrip(".")


class Item:
    def __init__(self, path, prefix):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"<\?xml[^>]*\?>", "", text)
        text = re.sub(r"<!DOCTYPE[^>]*>", "", text, flags=re.S)
        m = ROOT_TAG_RE.search(text)
        if not m:
            raise ValueError("no <svg> root element")
        tag = m.group(0)

        width, height = get_attr(tag, "width"), get_attr(tag, "height")
        view_box = get_attr(tag, "viewBox")
        if width is None or height is None or "%" in width + height:
            if not view_box:
                raise ValueError("needs absolute width/height or a viewBox")
            _, _, vw, vh = map(float, view_box.replace(",", " ").split())
            width, height = width or f"{vw}px", height or f"{vh}px"
            if "%" in width + height:
                width, height = f"{vw}px", f"{vh}px"
        self.w = to_mm(width)
        self.h = to_mm(height)
        if not view_box:
            # Without a viewBox, user units are CSS px at the declared size.
            view_box = f"0 0 {fmt(self.w / MM_PER_UNIT['px'])} {fmt(self.h / MM_PER_UNIT['px'])}"

        for name in ("width", "height", "x", "y", "viewBox"):
            tag = drop_attr(tag, name)
        self.open_tag = tag
        self.view_box = view_box
        self.body = text[m.end():]
        self.path = path
        self._prefix_ids(prefix)

    def _prefix_ids(self, prefix):
        """Namespace ids so defs from different files can't collide."""
        ids = set(re.findall(r'\bid\s*=\s*"([^"]+)"', self.body))
        if not ids:
            return
        body = self.body
        for old in sorted(ids, key=len, reverse=True):
            new = prefix + old
            esc = re.escape(old)
            body = re.sub(rf'(\bid\s*=\s*"){esc}"', rf'\g<1>{new}"', body)
            body = re.sub(rf"url\(\s*#{esc}\s*\)", f"url(#{new})", body)
            body = re.sub(rf'(href\s*=\s*"#){esc}"', rf'\g<1>{new}"', body)
        self.body = body

    def render(self, x, y):
        tag = self.open_tag[:-1].rstrip("/").rstrip()
        attrs = (f' x="{fmt(x)}" y="{fmt(y)}" width="{fmt(self.w)}" '
                 f'height="{fmt(self.h)}" viewBox="{self.view_box}"')
        return f"{tag}{attrs}>{self.body.rstrip()}\n"


def shelf_pack(items, page_w, page_h, margin, gap, label_h):
    """Simple shelf packing: tallest first, fill rows left-to-right."""
    placed, overflow = [], []
    x, y, row_h = margin, margin, 0.0
    usable_w = page_w - 2 * margin
    for it in sorted(items, key=lambda i: (-i.h, -i.w)):
        cell_h = it.h + label_h
        if it.w > usable_w:
            overflow.append(it)
            continue
        if x + it.w > page_w - margin:
            x, y, row_h = margin, y + row_h + gap, 0.0
        if y + cell_h > page_h - margin:
            overflow.append(it)
            continue
        placed.append((it, x, y))
        x += it.w + gap
        row_h = max(row_h, cell_h)
    return placed, overflow


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", type=Path, help="SVG files (default: all *.svg under output/)")
    ap.add_argument("-o", "--output", type=Path, default=Path("output/print-sheet.svg"))
    ap.add_argument("--page", default="letter", help=f"{', '.join(PAGES_MM)} or WxH in mm, e.g. 200x280")
    ap.add_argument("--landscape", action="store_true")
    ap.add_argument("--margin", type=float, default=10.0, help="page margin in mm (default 10)")
    ap.add_argument("--gap", type=float, default=4.0, help="spacing between items in mm (default 4)")
    ap.add_argument("--labels", action="store_true", help="print each file name under its image")
    ap.add_argument("--outline", action="store_true", help="draw a thin cut outline around each item")
    args = ap.parse_args()

    if args.page.lower() in PAGES_MM:
        page_w, page_h = PAGES_MM[args.page.lower()]
    else:
        page_w, page_h = map(float, args.page.lower().split("x"))
    if args.landscape:
        page_w, page_h = page_h, page_w

    inputs = args.inputs or sorted(Path("output").rglob("*.svg"))
    out_resolved = args.output.resolve()
    inputs = [p for p in inputs if p.resolve() != out_resolved]
    if not inputs:
        sys.exit("No SVG files found.")

    items = []
    for i, path in enumerate(inputs):
        try:
            items.append(Item(path, prefix=f"s{i}_"))
        except (ValueError, OSError) as e:
            print(f"skip {path}: {e}", file=sys.stderr)

    label_h = 3.5 if args.labels else 0.0
    placed, overflow = shelf_pack(items, page_w, page_h, args.margin, args.gap, label_h)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{fmt(page_w)}mm" height="{fmt(page_h)}mm" viewBox="0 0 {fmt(page_w)} {fmt(page_h)}">\n',
        f'<rect width="{fmt(page_w)}" height="{fmt(page_h)}" fill="white"/>\n',
    ]
    for it, x, y in placed:
        parts.append(it.render(x, y))
        if args.outline:
            parts.append(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(it.w)}" height="{fmt(it.h)}" '
                         f'fill="none" stroke="#999" stroke-width="0.1"/>\n')
        if args.labels:
            parts.append(f'<text x="{fmt(x)}" y="{fmt(y + it.h + 2.5)}" font-family="sans-serif" '
                         f'font-size="2">{it.path.stem}</text>\n')
    parts.append("</svg>\n")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(parts), encoding="utf-8")

    print(f"Wrote {args.output} ({fmt(page_w)} x {fmt(page_h)} mm) with {len(placed)} item(s).")
    for it, x, y in placed:
        print(f"  {it.path}  {fmt(it.w)} x {fmt(it.h)} mm at ({fmt(x)}, {fmt(y)})")
    if overflow:
        print(f"\n{len(overflow)} item(s) did not fit on one page:", file=sys.stderr)
        for it in overflow:
            print(f"  {it.path}  {fmt(it.w)} x {fmt(it.h)} mm", file=sys.stderr)
        print("Try --landscape, a larger --page, or smaller --margin/--gap.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
