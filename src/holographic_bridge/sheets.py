"""Investigation and visualization of the Two-Sheets phenomenon (2 x 29,516 + 17 cells).

Sheet A: 0..29,515      (w = 0..156)
Sheet B: 29,516..59,031 (w = 157..313)
Tail:    59,032..59,048 (w = 314, 17 cells)
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .torus_embed import (
    embed_cell,
    embed_cell_disambiguated,
    rotate4,
    project_stereo,
    MEM_SIZE,
    SHEET_SIZE,
)

TAIL_START = 2 * SHEET_SIZE  # 59032
TAIL_SIZE = MEM_SIZE - TAIL_START  # 17
TOTAL_CELLS = MEM_SIZE  # 59049


def sheet_of(c: int) -> str:
    """Return the sheet name for a memory address c."""
    if c < SHEET_SIZE:
        return "A"
    elif c < TAIL_START:
        return "B"
    return "TAIL"


def sheet_id(c: int) -> int:
    """Return numeric sheet identifier: 0 for A, 1 for B, 2 for TAIL."""
    if c < SHEET_SIZE:
        return 0
    elif c < TAIL_START:
        return 1
    return 2


def analyze_two_sheets(active_cells: set[int] | None = None) -> Dict[str, Any]:
    """Analyze cell distribution, overlap, and aliasing between Sheet A, Sheet B, and Tail."""
    sheet_a_cells = set(range(0, SHEET_SIZE))
    sheet_b_cells = set(range(SHEET_SIZE, TAIL_START))
    tail_cells = set(range(TAIL_START, MEM_SIZE))

    aliased_pairs = []
    for c in range(SHEET_SIZE):
        aliased_pairs.append((c, c + SHEET_SIZE))

    triple_overlaps = []
    for c in range(TAIL_START, MEM_SIZE):
        offset = c - TAIL_START
        triple_overlaps.append((offset, offset + SHEET_SIZE, c))

    res = {
        "sheet_a_count": len(sheet_a_cells),
        "sheet_b_count": len(sheet_b_cells),
        "tail_count": len(tail_cells),
        "total_cells": MEM_SIZE,
        "sheet_size_factorization": "188 * 157 = 2 * 2 * 47 * 157 = 29516",
        "two_sheets_sum": 2 * SHEET_SIZE,
        "tail_formula": "59049 - 59032 = 17",
        "exact_aliased_pairs_count": len(aliased_pairs),
        "triple_overlap_count": len(triple_overlaps),
        "triple_overlap_cells": list(range(TAIL_START, MEM_SIZE)),
        "tail_aliases_with": list(range(17)),
    }

    if active_cells is not None:
        active_a = active_cells & sheet_a_cells
        active_b = active_cells & sheet_b_cells
        active_tail = active_cells & tail_cells

        # How many aliased positions had activity on BOTH Sheet A and Sheet B?
        both_active = 0
        for ca, cb in aliased_pairs:
            if ca in active_cells and cb in active_cells:
                both_active += 1

        res["active_analysis"] = {
            "total_active": len(active_cells),
            "active_in_a": len(active_a),
            "active_in_b": len(active_b),
            "active_in_tail": len(active_tail),
            "positions_active_in_both_sheets": both_active,
            "positions_active_only_in_a": len(active_a) - both_active,
            "positions_active_only_in_b": len(active_b) - both_active,
        }

    return res


def _get_font(size: int = 14) -> ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "consola.ttf", "cour.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def render_sheets_overlay(out_path: Path, active_cells: set[int] | None = None, title: str = "Two Sheets Overlay (Mode 1)"):
    """Render Mode 1: Superimposed exact historical embedding.
    Shows Sheet A in Cyan, Sheet B in Amber, and overlapping points in White.
    """
    W, H = 700, 700
    im = Image.new("RGB", (W, H), (10, 12, 18))
    draw = ImageDraw.Draw(im)

    font_title = _get_font(16)
    font_sm = _get_font(12)

    draw.text((20, 15), title, fill=(230, 235, 245), font=font_title)
    draw.text((20, 38), "Exact Historical Clifford Torus Projection: S^1(20) x S^1(10)", fill=(130, 140, 160), font=font_sm)

    # 4D rotation and stereographic projection
    planes = [((0, 3), 0.8), ((1, 2), 0.6)]
    cx, cy = W // 2, H // 2 + 15
    scale_3d = 8.5

    # Sample cells to draw
    step = 4
    for c in range(0, MEM_SIZE, step):
        sh = sheet_of(c)
        is_active = (active_cells is None or c in active_cells)
        if not is_active:
            continue

        p4 = embed_cell(c)
        q = p4
        for pl, ang in planes:
            q = rotate4(q, pl, ang)
        p3 = project_stereo(q, R=45.0)

        # 3D to 2D isometric projection
        iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
        iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8

        px = int(cx + iso_x * scale_3d)
        py = int(cy + iso_y * scale_3d)

        if 0 <= px < W and 0 <= py < H:
            if sh == "A":
                color = (0, 200, 255)
            elif sh == "B":
                color = (255, 170, 0)
            else:
                color = (255, 50, 150)  # TAIL in magenta
            draw.point((px, py), fill=color)

    # Legend
    draw.rectangle([W - 220, 20, W - 20, 100], fill=(16, 20, 28), outline=(40, 48, 65))
    draw.point((W - 205, 38), fill=(0, 200, 255))
    draw.text((W - 195, 32), "Sheet A (0..29,515)", fill=(0, 200, 255), font=font_sm)
    draw.point((W - 205, 58), fill=(255, 170, 0))
    draw.text((W - 195, 52), "Sheet B (29,516..59,031)", fill=(255, 170, 0), font=font_sm)
    draw.point((W - 205, 78), fill=(255, 50, 150))
    draw.text((W - 195, 72), "Tail (59,032..59,048) [17]", fill=(255, 50, 150), font=font_sm)

    im.save(out_path)


def render_sheets_separated(out_path: Path, active_cells: set[int] | None = None, title: str = "Two Sheets Separated (Mode 2)"):
    """Render Mode 2: Visually separated sheets.
    Renders Sheet A and Sheet B side by side with the Tail highlighted.
    """
    W, H = 1000, 520
    im = Image.new("RGB", (W, H), (10, 12, 18))
    draw = ImageDraw.Draw(im)

    font_title = _get_font(16)
    font_sm = _get_font(12)

    draw.text((20, 15), title, fill=(230, 235, 245), font=font_title)
    draw.text((20, 38), "Left: Sheet A (0..29,515) | Right: Sheet B (29,516..59,031) + Tail (17 cells)", fill=(130, 140, 160), font=font_sm)

    # Panel A on left, Panel B on right
    p1_x0, p1_y0, p_w, p_h = 30, 70, 450, 420
    p2_x0, p2_y0 = 520, 70
    draw.rectangle([p1_x0, p1_y0, p1_x0 + p_w, p1_y0 + p_h], fill=(16, 20, 28), outline=(30, 36, 50))
    draw.rectangle([p2_x0, p2_y0, p2_x0 + p_w, p2_y0 + p_h], fill=(16, 20, 28), outline=(30, 36, 50))

    draw.text((p1_x0 + 10, p1_y0 + 10), "SHEET A: 29,516 cells (2x2x47x157)", fill=(0, 200, 255), font=font_sm)
    draw.text((p2_x0 + 10, p2_y0 + 10), "SHEET B: 29,516 cells + TAIL: 17 cells", fill=(255, 170, 0), font=font_sm)

    planes = [((0, 3), 0.8), ((1, 2), 0.6)]
    cx_a, cy_a = p1_x0 + p_w // 2, p1_y0 + p_h // 2 + 10
    cx_b, cy_b = p2_x0 + p_w // 2, p2_y0 + p_h // 2 + 10
    scale_3d = 6.2

    step = 4
    for c in range(0, MEM_SIZE, step):
        sh = sheet_of(c)
        is_active = (active_cells is None or c in active_cells)
        if not is_active:
            continue

        p4 = embed_cell(c)
        q = p4
        for pl, ang in planes:
            q = rotate4(q, pl, ang)
        p3 = project_stereo(q, R=45.0)

        iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
        iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8

        if sh == "A":
            px = int(cx_a + iso_x * scale_3d)
            py = int(cy_a + iso_y * scale_3d)
            if p1_x0 <= px < p1_x0 + p_w and p1_y0 <= py < p1_y0 + p_h:
                draw.point((px, py), fill=(0, 200, 255))
        else:
            px = int(cx_b + iso_x * scale_3d)
            py = int(cy_b + iso_y * scale_3d)
            if p2_x0 <= px < p2_x0 + p_w and p2_y0 <= py < p2_y0 + p_h:
                color = (255, 170, 0) if sh == "B" else (255, 50, 150)
                draw.point((px, py), fill=color)

    im.save(out_path)
