"""Redraw the connector lines of the Application Note Figure 1 illustration.

The raw illustration was generated with ChatGPT image generation from an author-written
specification (see docs/paper/figures-note-2026-09-09/fig1_workflow_stack.provenance.md).
Its dotted leaders between the five bands and the traceability panel were stepped; this
script clears the gap between the bands and the panel, removes the leader stubs inside the
panel and draws one straight horizontal dotted leader per band. The geometry is measured
from the raw file rather than hard-coded, so a regenerated illustration in the same layout
still works, and every measurement is checked before anything is drawn. Run:

    python scripts/straighten_note_fig1_leaders.py --raw docs/paper/figures-note-2026-09-09/fig1_workflow_stack_raw_chatgpt.png --out docs/paper/figures-note-2026-09-09/fig1_workflow_stack.png
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

BANDS_EXPECTED = 5
LEADER = (51, 151, 160)
DOT, STEP = 4, 9


def is_grey(pixel):
    return abs(pixel[0] - pixel[1]) < 8 and abs(pixel[1] - pixel[2]) < 8 and 200 < pixel[0] < 243


def is_teal(pixel):
    return pixel[1] > pixel[0] + 20 and pixel[0] < 220


def band_right_edge(pixels, width):
    """Rightmost column where a band's grey fill ends, taken as the mode over sample rows."""
    edges = []
    for y in range(int(pixels.shape[0] * 0.1), int(pixels.shape[0] * 0.9), 7):
        row = pixels[y]
        found = [x for x in range(width // 2, int(width * 0.85)) if is_grey(row[x]) and not is_grey(row[x + 1])]
        if found:
            edges.append(found[-1])
    if not edges:
        raise SystemExit("no band right edge found")
    return max(set(edges), key=edges.count)


def panel_left_edge(pixels, start, width):
    for x in range(start + 4, width):
        column = pixels[:, x]
        if sum(1 for y in range(pixels.shape[0]) if is_teal(column[y])) > pixels.shape[0] * 0.5:
            return x
    raise SystemExit("no panel left edge found")


def bands(pixels, x):
    """Vertical extents of the grey bands along one column."""
    column = pixels[:, x]
    spans, start = [], None
    for y in range(pixels.shape[0]):
        if is_grey(column[y]):
            start = y if start is None else start
        elif start is not None:
            if y - start > 60:
                spans.append((start, y - 1))
            start = None
    if start is not None and pixels.shape[0] - start > 60:
        spans.append((start, pixels.shape[0] - 1))
    merged = []
    for top, bottom in spans:
        if merged and top - merged[-1][1] <= 8:  # a thin light row inside one band
            merged[-1] = (merged[-1][0], bottom)
        else:
            merged.append((top, bottom))
    return merged


def tag_left_edge(pixels, panel, top, bottom, fill):
    """First column of the tag boxes: the leader stubs mark only a few rows, a tag border many."""
    for x in range(panel + 4, panel + 160):
        marked = int((np.abs(pixels[top:bottom, x] - np.array(fill)).sum(axis=1) > 60).sum())
        if marked > 100:
            return x
    raise SystemExit("no tag column found inside the panel")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    image = Image.open(args.raw).convert("RGB")
    pixels = np.asarray(image).astype(int)
    height, width = pixels.shape[:2]
    right = band_right_edge(pixels, width)
    panel = panel_left_edge(pixels, right, width)
    spans = bands(pixels, right - 8)
    if len(spans) != BANDS_EXPECTED:
        raise SystemExit(f"expected {BANDS_EXPECTED} bands, measured {len(spans)}: {spans}")
    if not 8 < panel - right < 200:
        raise SystemExit(f"implausible gap between bands ({right}) and panel ({panel})")
    fill = tuple(int(v) for v in pixels[(spans[1][1] + spans[2][0]) // 2, panel + 14])
    tag = tag_left_edge(pixels, panel, spans[0][0], spans[-1][1], fill)
    print(f"bands {spans} | right edge {right} | panel {panel} | fill {fill} | tags from {tag}")

    draw = ImageDraw.Draw(image)
    draw.rectangle([right + 2, 0, panel - 2, height - 1], fill=(255, 255, 255))
    draw.rectangle([panel + 3, spans[0][0] - 30, tag - 3, spans[-1][1] + 30], fill=fill)
    for top, bottom in spans:
        y = (top + bottom) // 2
        x = right + 5
        while x + DOT <= panel - 3:
            draw.rounded_rectangle([x, y - 2, x + DOT, y + 2], radius=2, fill=LEADER)
            x += STEP
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.out)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
