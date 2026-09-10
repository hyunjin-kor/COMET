"""Redraw the connector lines of the Application Note Figure 1 illustration.

The raw illustration was generated with ChatGPT image generation from an author-written
specification (see docs/paper/figures-note-2026-09-09/fig1_workflow_stack.provenance.md).
Its dotted leaders between the five bands and the provenance panel were stepped; this
script clears the gap between the bands and the panel, removes the leader stubs inside
the panel and draws one straight horizontal dotted leader per band. Coordinates are
measured on the 1672 x 941 raw file and asserted before drawing. Run:

    python scripts/straighten_note_fig1_leaders.py --raw docs/paper/figures-note-2026-09-09/fig1_workflow_stack_raw_chatgpt.png --out docs/paper/figures-note-2026-09-09/fig1_workflow_stack.png
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SIZE = (1672, 941)
BAND_RIGHT, PANEL_LEFT = 1209, 1297           # last grey column of the bands, first teal column of the panel
GAP = (BAND_RIGHT + 2, PANEL_LEFT - 2)         # columns cleared to white
BANDS = [(29, 184), (207, 362), (385, 543), (566, 724), (747, 910)]
PANEL_FILL = (203, 234, 235)
STUB_COLUMNS = (1300, 1321)                    # between the panel border and the first tag column (1324)
LEADER = (51, 151, 160)                        # mean colour of the original dotted leaders
DOT, STEP = 4, 9


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    image = Image.open(args.raw).convert("RGB")
    if image.size != SIZE:
        raise SystemExit(f"unexpected raw size {image.size}, expected {SIZE}")
    pixels = np.asarray(image).astype(int)
    grey = pixels[BANDS[0][0] + 30, BAND_RIGHT]
    if not (200 < grey[0] < 240 and abs(grey[0] - grey[2]) < 8):
        raise SystemExit("band right edge is not where the script expects it")
    if abs(pixels[200, 1310] - np.array(PANEL_FILL)).sum() > 12:
        raise SystemExit("panel fill colour is not where the script expects it")
    draw = ImageDraw.Draw(image)
    draw.rectangle([GAP[0], 15, GAP[1], 925], fill=(255, 255, 255))
    draw.rectangle([STUB_COLUMNS[0], 90, STUB_COLUMNS[1], 905], fill=PANEL_FILL)
    for top, bottom in BANDS:
        yc = (top + bottom) // 2
        x = GAP[0] + 3
        while x + DOT <= GAP[1] - 1:
            draw.rounded_rectangle([x, yc - 2, x + DOT, yc + 2], radius=2, fill=LEADER)
            x += STEP
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.out)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
