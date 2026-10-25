"""Malbolge Unshackled & MalbolgeLISP Bridge for MalbolgArt.

Galactic Scale Projection: Visualizing 3^19 Unshackled Dynamics and the
Midpoint Universe Attractor alongside Classic 3^10 Malbolge.

PROVENANCE & ATTRIBUTION:
  - MalbolgeLISP created by Iczelia (2020-2021) and Kamila Szewczyk (kspalaiologos / Palaiologos).
  - Malbolge Unshackled specification by Lou Scheffer.
  - Original Repository: https://github.com/kspalaiologos/malbolge-lisp
  - License: Core (core.mb) is Public Domain; Runtime & Tooling governed by GNU GPLv3 / MIT.
  - Reference: "MalbolgeLisp's design and implementation", Iczelia (2021).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from PIL import Image, ImageDraw

# Provenance metadata
UNSHACKLED_PROVENANCE = {
    "project": "MalbolgeLISP v1.2",
    "authors": ["Iczelia (2020-2021)", "Kamila Szewczyk (kspalaiologos / Palaiologos)"],
    "unshackled_spec_author": "Lou Scheffer",
    "original_repository": "https://github.com/kspalaiologos/malbolge-lisp",
    "original_license": "Core (core.mb): Public Domain; Runtime & Tooling: GNU GPLv3 / MIT",
    "literature_reference": "MalbolgeLisp: Design and Implementation (Iczelia, 2021, MalbolgeLisp.pdf)",
    "target_expression": "(+ 1 2) -> 3",
}

# Mathematical Constants
UNSHACKLED_TRITS = 19
UNSHACKLED_MEM_SIZE = 3**19  # 1,162,261,467 cells
UNIVERSE_MIDPOINT = (UNSHACKLED_MEM_SIZE - 1) // 2  # 581,130,733 cells
CLASSIC_MEM_SIZE = 3**10  # 59,049 cells
SCALE_RATIO_UNSHACKLED_VS_CLASSIC = UNSHACKLED_MEM_SIZE / CLASSIC_MEM_SIZE  # ~19,683

EMPIRICAL_EXECUTION_METRICS = {
    "input_expression": "(+ 1 2)",
    "result_output": "3",
    "total_steps": 2401426209,
    "elapsed_wall_sec": 13.2,
    "instructions_per_sec": 1.82e8,
    "min_c": 0,
    "max_c": 581859196,
    "min_d": 0,
    "max_d": 582285363,
    "universe_midpoint": UNIVERSE_MIDPOINT,
    "opcodes": {
        "JMP_4": 1086386934,
        "OUT_5": 291,
        "IN_23": 9,
        "ROTR_39": 110332982,
        "MOVD_40": 188334921,
        "CRZ_62": 94693215,
        "NOP_68": 143252749,
        "HALT_81": 1,
        "MUTATED_NOPS": 778038108,
    },
    "jmp_percentage": 45.238,
}


def project_to_classic_shadow(c: int, d: int) -> Tuple[int, int]:
    """Projects 19-trit Unshackled addresses into the 10-trit Classic Torus space."""
    return c % CLASSIC_MEM_SIZE, d % CLASSIC_MEM_SIZE


def project_to_macro_coords(c: int, d: int) -> Tuple[float, float]:
    """Normalizes Unshackled addresses relative to Universe Midpoint mu."""
    norm_c = (c - UNIVERSE_MIDPOINT) / (UNSHACKLED_MEM_SIZE / 2.0)
    norm_d = (d - UNIVERSE_MIDPOINT) / (UNSHACKLED_MEM_SIZE / 2.0)
    return norm_c, norm_d


def load_sampled_csv(csv_path: Path) -> Dict[str, np.ndarray]:
    """Loads a downsampled Unshackled trajectory CSV."""
    steps, c_vals, d_vals, a_vals, ops = [], [], [], [], []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            steps.append(int(row["step"]))
            c_vals.append(int(row["c"]))
            d_vals.append(int(row["d"]))
            if "a" in row:
                a_vals.append(int(row["a"]))
            if "op" in row:
                ops.append(int(row["op"]))

    return {
        "steps": np.array(steps, dtype=np.int64),
        "c": np.array(c_vals, dtype=np.int64),
        "d": np.array(d_vals, dtype=np.int64),
        "a": np.array(a_vals, dtype=np.int64) if a_vals else np.zeros_like(steps),
        "ops": np.array(ops, dtype=np.int32) if ops else np.zeros_like(steps),
    }


def render_macro_phase_space(
    samples: Dict[str, np.ndarray],
    out_path: Path,
    width: int = 1400,
    height: int = 700,
) -> Path:
    """Renders the dual-panel Macro Phase Space vs Midpoint Lisp Attractor."""
    steps = samples["steps"]
    c_vals = samples["c"]
    d_vals = samples["d"]
    n_pts = len(steps)

    img = Image.new("RGB", (width, height), (10, 12, 16))
    draw = ImageDraw.Draw(img)

    # Bounding panels
    draw.rectangle([40, 50, 660, 650], outline=(40, 50, 70), width=1)
    draw.rectangle([740, 50, 1360, 650], outline=(40, 50, 70), width=1)

    # Panel 1: Full Macro Space (0 to 600M cells)
    max_macro = 600_000_000
    mid_x = int(40 + (UNIVERSE_MIDPOINT / max_macro) * 620)
    mid_y = int(650 - (UNIVERSE_MIDPOINT / max_macro) * 600)
    draw.line([(mid_x, 50), (mid_x, 650)], fill=(30, 80, 100), width=1)
    draw.line([(40, mid_y), (660, mid_y)], fill=(30, 80, 100), width=1)

    for i in range(0, n_pts, 2):
        t = i / n_pts
        r = int(255 * min(1.0, 2 * t))
        g = int(255 * (1.0 - abs(2 * t - 1.0)))
        b = int(255 * max(0.0, 1.0 - 2 * t))

        px1 = int(40 + (c_vals[i] / max_macro) * 620)
        py1 = int(650 - (d_vals[i] / max_macro) * 600)
        if 40 <= px1 <= 660 and 50 <= py1 <= 650:
            draw.ellipse([px1 - 1, py1 - 1, px1 + 1, py1 + 1], fill=(r, g, b))

    # Panel 2: Dense Core Around Universe Midpoint
    c_min_zoom, c_max_zoom = 581_100_000, 581_200_000
    d_min_zoom, d_max_zoom = 581_100_000, 582_300_000

    for i in range(0, n_pts):
        c = c_vals[i]
        d = d_vals[i]
        if c_min_zoom <= c <= c_max_zoom and d_min_zoom <= d <= d_max_zoom:
            t = i / n_pts
            r = int(255 * min(1.0, 2 * t))
            g = int(255 * (1.0 - abs(2 * t - 1.0)))
            b = int(255 * max(0.0, 1.0 - 2 * t))

            px2 = int(740 + ((c - c_min_zoom) / (c_max_zoom - c_min_zoom)) * 620)
            py2 = int(650 - ((d - d_min_zoom) / (d_max_zoom - d_min_zoom)) * 600)
            if 740 <= px2 <= 1360 and 50 <= py2 <= 650:
                draw.point((px2, py2), fill=(r, g, b))

    # Headers & Provenance Labels
    draw.text((40, 18), "MALBOLGELISP V1.2 (2.4 BILLION STEPS): MACRO PHASE SPACE (3^19 UNIVERSE)", fill=(240, 240, 250))
    draw.text((50, 60), "MACRO TRAJECTORY (0 to 600M Cells)", fill=(180, 200, 220))
    draw.text((50, 78), f"Midpoint: 3^19 / 2 = {UNIVERSE_MIDPOINT:,}", fill=(0, 200, 255))
    draw.text((50, 96), "Boot Phase: (0,0) -> Midpoint Jump", fill=(100, 220, 150))

    draw.text((750, 60), "LISP EVALUATION ATTRACTOR (Zoom: Midpoint)", fill=(180, 200, 220))
    draw.text((750, 78), f"c in [{c_min_zoom:,} .. {c_max_zoom:,}]", fill=(255, 180, 0))
    draw.text((750, 96), f"d in [{d_min_zoom:,} .. {d_max_zoom:,}]", fill=(255, 180, 0))
    draw.text((750, 114), "Evaluating '(+ 1 2)' -> '3'", fill=(255, 100, 200))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def render_torus_orbit_gif(
    samples: Dict[str, np.ndarray],
    out_path: Path,
    n_frames: int = 40,
    size: int = 500,
) -> Path:
    """Renders an animated GIF showing the 2.4B trajectory projected modulo 59,049."""
    steps = samples["steps"]
    c_vals = samples["c"]
    d_vals = samples["d"]

    c_mod = c_vals % CLASSIC_MEM_SIZE
    d_mod = d_vals % CLASSIC_MEM_SIZE

    frame_step = max(1, len(steps) // n_frames)
    frames = []

    for frame_idx in range(1, n_frames + 1):
        sub_len = min(len(steps), frame_idx * frame_step)
        sub_c = c_mod[:sub_len]
        sub_d = d_mod[:sub_len]
        cur_step = steps[sub_len - 1]

        img = Image.new("RGB", (size, size), (10, 12, 16))
        draw = ImageDraw.Draw(img)

        # Torus Box
        draw.rectangle([30, 30, size - 30, size - 30], outline=(40, 55, 75), width=1)

        # Render points
        stride = max(1, len(sub_c) // 4000)
        for i in range(0, len(sub_c), stride):
            ratio = i / len(sub_c)
            r = int(50 + 205 * ratio)
            g = int(120 * (1.0 - abs(2.0 * ratio - 1.0)))
            b = int(255 * (1.0 - ratio))

            px = int(30 + (sub_c[i] / float(CLASSIC_MEM_SIZE)) * (size - 60))
            py = int((size - 30) - (sub_d[i] / float(CLASSIC_MEM_SIZE)) * (size - 60))
            draw.point((px, py), fill=(r, g, b))

        # Head marker
        head_x = int(30 + (sub_c[-1] / float(CLASSIC_MEM_SIZE)) * (size - 60))
        head_y = int((size - 30) - (sub_d[-1] / float(CLASSIC_MEM_SIZE)) * (size - 60))
        draw.ellipse([head_x - 4, head_y - 4, head_x + 4, head_y + 4], fill=(255, 255, 0), outline=(255, 255, 255))

        draw.text((30, 10), f"MalbolgeLisp mod 59,049 | Step: {cur_step / 1e9:.2f}B / 2.40B", fill=(200, 220, 255))
        draw.text((30, size - 25), "Evaluating '(+ 1 2)' -> '3' (3^19 in 3^10 Shadow)", fill=(160, 180, 200))

        frames.append(img)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=100, loop=0)
    return out_path
