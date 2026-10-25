"""Animation suite for HOLOGRAPHIC 4D Torus representations and historical JSON traces.

Animación A: Holographic Original (4D point cloud rotation, opcode colored)
Animación B: Toro 4D de las Dos Hojas (Sheet A vs Sheet B + Tail)
Animación C: Traza Cronológica Real (from lutter_outs.json)
Animación D: MalbolgArt vs HOLOGRAPHIC (1D vs 2D W=188 vs (c,d) vs 4D Torus)
Animación E: FLOW Original (vector field geodesic flow simulation)
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .torus_embed import (
    embed_cell,
    rotate4,
    project_stereo,
    rotate_project,
    MEM_SIZE,
    SHEET_SIZE,
)
from .sheets import sheet_of, TAIL_START

OPCODE_COLORS = {
    "JMP": (0, 220, 255),       # Cyan
    "OUT": (50, 230, 100),      # Green
    "IN": (200, 100, 255),      # Purple
    "ROT": (255, 220, 40),      # Yellow
    "DLOAD": (255, 140, 20),    # Orange
    "CRAZY": (255, 50, 140),    # Magenta
    "NOP": (100, 110, 130),     # Slate
    "END": (255, 255, 255),     # White
}


def _get_font(size: int = 14) -> ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "consola.ttf", "cour.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def render_lutter_4d_gif(
    trace_data: Dict[str, Any],
    out_path: Path,
    num_frames: int = 40,
    size: Tuple[int, int] = (480, 480)
) -> Path:
    """Animación A: Holographic Original 4D point cloud rotating across 4D planes."""
    W, H = size
    pts_raw = trace_data.get("points", [])
    if not pts_raw:
        raise ValueError("No points found in trace_data")

    # Downsample points for fast, clean rendering if large
    stride = max(1, len(pts_raw) // 3500)
    selected_pts = pts_raw[::stride]

    frames: List[Image.Image] = []
    font_sm = _get_font(12)

    cx, cy = W // 2, H // 2 + 10
    scale = 8.5

    for f_idx in range(num_frames):
        angle = 2.0 * math.pi * f_idx / num_frames
        planes = [
            ((0, 3), angle),
            ((1, 2), angle * 0.7),
            ((2, 3), angle * 0.35),
        ]

        im = Image.new("RGB", (W, H), (10, 12, 18))
        draw = ImageDraw.Draw(im)

        draw.text((15, 12), "HOLOGRAPHIC 4D Clifford Torus — Quine Lutter", fill=(220, 225, 235), font=font_sm)
        draw.text((15, 28), f"Plane rotations (0,3), (1,2), (2,3) | Frame {f_idx + 1}/{num_frames}", fill=(120, 130, 150), font=font_sm)

        for item in selected_pts:
            p4 = item.get("p", [0, 0, 0, 0])
            op = item.get("op", "NOP")
            color = OPCODE_COLORS.get(op, (120, 130, 140))

            q = p4
            for pl, a in planes:
                q = rotate4(q, pl, a)
            p3 = project_stereo(q, R=45.0)

            iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
            iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8

            px = int(cx + iso_x * scale)
            py = int(cy + iso_y * scale)

            if 0 <= px < W and 0 <= py < H:
                draw.point((px, py), fill=color)

        frames.append(im)

    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=75, loop=0)
    return out_path


def render_lutter_two_sheets_gif(
    out_path: Path,
    num_frames: int = 40,
    size: Tuple[int, int] = (480, 480)
) -> Path:
    """Animación B: 4D Torus rotating with Sheet A (cyan), Sheet B (amber), and Tail (magenta)."""
    W, H = size
    frames: List[Image.Image] = []
    font_sm = _get_font(12)

    cx, cy = W // 2, H // 2 + 10
    scale = 8.5

    # Sample addresses across memory
    sample_addrs = list(range(0, MEM_SIZE, 8))

    for f_idx in range(num_frames):
        angle = 2.0 * math.pi * f_idx / num_frames
        planes = [
            ((0, 3), angle),
            ((1, 2), angle * 0.8),
        ]

        im = Image.new("RGB", (W, H), (10, 12, 18))
        draw = ImageDraw.Draw(im)

        draw.text((15, 12), "TWO SHEETS 4D TORUS — (2 x 29,516 + 17 cells)", fill=(220, 225, 235), font=font_sm)
        draw.text((15, 28), "Cyan: Sheet A | Amber: Sheet B | Magenta: Tail (17 cells)", fill=(120, 130, 150), font=font_sm)

        for c in sample_addrs:
            sh = sheet_of(c)
            p4 = embed_cell(c)

            q = p4
            for pl, a in planes:
                q = rotate4(q, pl, a)
            p3 = project_stereo(q, R=45.0)

            iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
            iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8

            px = int(cx + iso_x * scale)
            py = int(cy + iso_y * scale)

            if 0 <= px < W and 0 <= py < H:
                if sh == "A":
                    draw.point((px, py), fill=(0, 200, 255))
                elif sh == "B":
                    draw.point((px, py), fill=(255, 170, 0))
                else:
                    draw.rectangle([px - 1, py - 1, px + 1, py + 1], fill=(255, 50, 150))

        frames.append(im)

    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=80, loop=0)
    return out_path


def render_lutter_trace_chronological_gif(
    outs_data: List[Dict[str, Any]],
    out_path: Path,
    num_frames: int = 50,
    size: Tuple[int, int] = (480, 480)
) -> Path:
    """Animación C: Chronological real execution trace from lutter_outs.json (59,852 outputs)."""
    W, H = size
    if not outs_data:
        raise ValueError("outs_data is empty")

    n_events = len(outs_data)
    step_stride = max(1, n_events // num_frames)

    frames: List[Image.Image] = []
    font_sm = _get_font(12)

    cx, cy = W // 2, H // 2 + 10
    scale = 8.5
    planes = [((0, 3), 0.8), ((1, 2), 0.6)]

    # Pre-render faint background torus
    bg_torus = Image.new("RGB", (W, H), (10, 12, 18))
    draw_bg = ImageDraw.Draw(bg_torus)
    for c in range(0, MEM_SIZE, 16):
        p4 = embed_cell(c)
        q = p4
        for pl, a in planes:
            q = rotate4(q, pl, a)
        p3 = project_stereo(q, R=45.0)
        iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
        iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8
        px = int(cx + iso_x * scale)
        py = int(cy + iso_y * scale)
        if 0 <= px < W and 0 <= py < H:
            draw_bg.point((px, py), fill=(25, 30, 42))

    # Build chronological animation
    trail_len = 250
    for f_idx in range(num_frames):
        target_idx = min(f_idx * step_stride, n_events - 1)
        ev_cur = outs_data[target_idx]

        frame = bg_torus.copy()
        draw = ImageDraw.Draw(frame)

        draw.text((15, 12), "CHRONOLOGICAL REAL TRACE — Quine Lutter Output Loop", fill=(220, 225, 235), font=font_sm)
        draw.text((15, 28), f"Step: {ev_cur.get('step', 0):,} | Output #{target_idx + 1}/{n_events} | Char: '{chr(ev_cur.get('out', 32)) if 32 <= ev_cur.get('out', 0) <= 126 else '?'}'", fill=(120, 130, 150), font=font_sm)

        # Draw active trail
        start_trail = max(0, target_idx - trail_len)
        prev_pt = None
        for i in range(start_trail, target_idx + 1):
            c_val = outs_data[i].get("c", 0)
            p4 = embed_cell(c_val)
            q = p4
            for pl, a in planes:
                q = rotate4(q, pl, a)
            p3 = project_stereo(q, R=45.0)
            iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
            iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8
            px = int(cx + iso_x * scale)
            py = int(cy + iso_y * scale)

            t_ratio = (i - start_trail) / max(1, trail_len)
            r = int(50 * (1 - t_ratio) + 255 * t_ratio)
            g = int(200 * (1 - t_ratio) + 255 * t_ratio)
            b = int(255 * (1 - t_ratio) + 50 * t_ratio)
            col = (r, g, b)

            if prev_pt and abs(px - prev_pt[0]) < 80 and abs(py - prev_pt[1]) < 80:
                draw.line([prev_pt, (px, py)], fill=col, width=1)
            prev_pt = (px, py)

        # Highlight current head position
        if prev_pt:
            draw.ellipse([prev_pt[0] - 3, prev_pt[1] - 3, prev_pt[0] + 3, prev_pt[1] + 3], fill=(255, 255, 255), outline=(0, 220, 255))

        frames.append(frame)

    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=85, loop=0)
    return out_path


def render_malbolgart_vs_holographic_gif(
    sample_path: Path,
    out_path: Path,
    num_frames: int = 40
) -> Path:
    """Animación D: Multi-view comparative animation:
    Linear Memory | Block W=188 | (c,d) Phase Space | 4D Torus Projection.
    """
    import json
    with open(sample_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    W, H = 840, 460
    frames: List[Image.Image] = []
    font_sm = _get_font(12)
    font_xs = _get_font(10)

    stride = max(1, len(samples) // num_frames)

    for f_idx in range(num_frames):
        s_idx = min(f_idx * stride, len(samples) - 1)
        cur_s = samples[s_idx]
        cur_c = cur_s.get("c", 0)
        cur_d = cur_s.get("d", 0)

        im = Image.new("RGB", (W, H), (10, 12, 18))
        draw = ImageDraw.Draw(im)

        draw.text((20, 12), f"MALBOLGART vs HOLOGRAPHIC — Step {cur_s.get('step', 0):,} (c={cur_c}, d={cur_d})", fill=(220, 225, 235), font=font_sm)

        # 4 Panels:
        # P1: Linear Memory (0..59048)
        p1_box = [30, 45, 410, 225]
        draw.rectangle(p1_box, fill=(16, 20, 28), outline=(30, 36, 50))
        draw.text((p1_box[0] + 8, p1_box[1] + 6), "1D Linear Memory (0..59048)", fill=(0, 200, 255), font=font_xs)
        cx_lin = p1_box[0] + int((cur_c / MEM_SIZE) * (p1_box[2] - p1_box[0]))
        dx_lin = p1_box[0] + int((cur_d / MEM_SIZE) * (p1_box[2] - p1_box[0]))
        draw.line([(cx_lin, p1_box[1] + 30), (cx_lin, p1_box[3] - 10)], fill=(0, 220, 255), width=2)
        draw.line([(dx_lin, p1_box[1] + 30), (dx_lin, p1_box[3] - 10)], fill=(255, 170, 0), width=2)
        draw.text((p1_box[0] + 8, p1_box[3] - 25), f"c={cur_c} (cyan) | d={cur_d} (amber)", fill=(140, 150, 170), font=font_xs)

        # P2: Block Grid W=188
        p2_box = [430, 45, 810, 225]
        draw.rectangle(p2_box, fill=(16, 20, 28), outline=(30, 36, 50))
        draw.text((p2_box[0] + 8, p2_box[1] + 6), "2D Block Grid (W=188, H=315)", fill=(255, 170, 0), font=font_xs)
        x_b = (cur_c % 188) / 188.0
        y_b = (cur_c // 188) / 315.0
        px_b = p2_box[0] + int(x_b * (p2_box[2] - p2_box[0] - 20)) + 10
        py_b = p2_box[1] + int(y_b * (p2_box[3] - p2_box[1] - 40)) + 30
        draw.ellipse([px_b - 3, py_b - 3, px_b + 3, py_b + 3], fill=(0, 220, 255), outline=(255, 255, 255))

        # P3: 2D (c,d) Modulo Space
        p3_box = [30, 245, 410, 425]
        draw.rectangle(p3_box, fill=(16, 20, 28), outline=(30, 36, 50))
        draw.text((p3_box[0] + 8, p3_box[1] + 6), "2D Phase Space (c, d) in (Z/59049Z)^2", fill=(255, 50, 150), font=font_xs)
        px_cd = p3_box[0] + int((cur_c / MEM_SIZE) * (p3_box[2] - p3_box[0] - 20)) + 10
        py_cd = p3_box[1] + int((cur_d / MEM_SIZE) * (p3_box[3] - p3_box[1] - 20)) + 10
        draw.ellipse([px_cd - 3, py_cd - 3, px_cd + 3, py_cd + 3], fill=(255, 50, 150), outline=(255, 255, 255))

        # P4: 4D Clifford Torus Holographic Projection
        p4_box = [430, 245, 810, 425]
        draw.rectangle(p4_box, fill=(16, 20, 28), outline=(30, 36, 50))
        draw.text((p4_box[0] + 8, p4_box[1] + 6), "4D Holographic Clifford Torus S^1(20) x S^1(10)", fill=(40, 230, 120), font=font_xs)
        p4_pt = embed_cell(cur_c)
        angle = 2.0 * math.pi * f_idx / num_frames
        planes = [((0, 3), angle), ((1, 2), angle * 0.7)]
        q = p4_pt
        for pl, a in planes:
            q = rotate4(q, pl, a)
        p3 = project_stereo(q, R=45.0)
        cx4 = (p4_box[0] + p4_box[2]) // 2
        cy4 = (p4_box[1] + p4_box[3]) // 2 + 10
        iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
        iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8
        px4 = int(cx4 + iso_x * 4.8)
        py4 = int(cy4 + iso_y * 4.8)
        draw.ellipse([px4 - 4, py4 - 4, px4 + 4, py4 + 4], fill=(40, 230, 120), outline=(255, 255, 255))

        frames.append(im)

    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=85, loop=0)
    return out_path


def render_flow_torus_simulation_gif(
    out_path: Path,
    num_frames: int = 40,
    size: Tuple[int, int] = (480, 480)
) -> Path:
    """Animación E: FLOW vector field simulation on the Clifford torus.
    Faithful numerical recreation of flow_torus.py / flow_torus_gif.py.
    NOTE: Epistemically labeled as NUMERICAL_RECREATION (computed via
    NumPy/Pillow vector field integration, not direct execution through FlowVM).
    """
    W, H = size
    PHI = (1.0 + math.sqrt(5.0)) / 2.0
    WZ = PHI
    WW = 1.0

    num_particles = 180
    np.random.seed(42)

    # Particles initialized on the Clifford torus
    angles_z = np.random.uniform(0, 2 * math.pi, num_particles)
    angles_w = np.random.uniform(0, 2 * math.pi, num_particles)
    dt = 0.08

    frames: List[Image.Image] = []
    font_sm = _get_font(12)
    cx, cy = W // 2, H // 2 + 15
    scale = 8.5
    planes = [((0, 3), 0.8), ((1, 2), 0.6)]

    for f_idx in range(num_frames):
        im = Image.new("RGB", (W, H), (10, 12, 18))
        draw = ImageDraw.Draw(im)

        draw.text((15, 12), "NUMERICAL RECREATION — Clifford Geodesic (NumPy/Pillow)", fill=(220, 225, 235), font=font_sm)
        draw.text((15, 28), "flow_torus.py model: v = [-wz*y, wz*x, -ww*w, ww*z] | wz/ww = PHI", fill=(120, 130, 150), font=font_sm)

        # Update particle angles along the geodesic vector field
        angles_z += WZ * dt
        angles_w += WW * dt

        for i in range(num_particles):
            th_z = angles_z[i]
            th_w = angles_w[i]
            p4 = [
                20.0 * math.cos(th_z),
                20.0 * math.sin(th_z),
                10.0 * math.cos(th_w),
                10.0 * math.sin(th_w),
            ]

            q = p4
            for pl, a in planes:
                q = rotate4(q, pl, a)
            p3 = project_stereo(q, R=45.0)

            iso_x = (p3[0] - p3[1]) * math.cos(math.radians(30))
            iso_y = (p3[0] + p3[1]) * math.sin(math.radians(30)) * 0.5 - p3[2] * 0.8

            px = int(cx + iso_x * scale)
            py = int(cy + iso_y * scale)

            if 0 <= px < W and 0 <= py < H:
                # Color by angle on second circle
                color_hue = (th_w % (2 * math.pi)) / (2 * math.pi)
                r = int(120 + 130 * math.sin(color_hue * 2 * math.pi))
                g = int(120 + 130 * math.sin(color_hue * 2 * math.pi + 2.0))
                b = int(120 + 130 * math.sin(color_hue * 2 * math.pi + 4.0))
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(r, g, b))

        frames.append(im)

    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=75, loop=0)
    return out_path
