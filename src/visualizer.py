"""Scientific visualization module for Malbolge execution geometry and traces.
Generates:
  - linear_memory.png
  - block_W.png (W=47, 94, 188, 376)
  - modular_circular.png
  - cd_trajectory.png (2D and 3D torus projection)
  - mutation_heatmap.png
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
from PIL import Image, ImageDraw, ImageFont

N = 59049

# Palette
BG_COLOR = (10, 12, 18)
PANEL_BG = (16, 20, 28)
TEXT_COLOR = (220, 226, 240)
MUTED_TEXT = (120, 130, 150)
ACCENT_CYAN = (0, 220, 255)
ACCENT_AMBER = (255, 170, 0)
ACCENT_MAGENTA = (255, 50, 130)
ACCENT_GREEN = (40, 230, 120)
GRID_LINE = (30, 36, 50)


def _get_font(size: int = 14) -> ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "consola.ttf", "cour.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def render_linear_memory(csv_path: Path, out_path: Path, metrics: Dict[str, Any], title: str = "Linear Memory"):
    """Render 0..59048 linear memory profile showing C visits, D visits, and mutations."""
    W, H = 1000, 380
    im = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(im)

    font_title = _get_font(18)
    font_sm = _get_font(12)

    # Header
    draw.text((20, 15), f"{title} — Address Space 0..59048", fill=TEXT_COLOR, font=font_title)
    sub = (
        f"Steps: {metrics.get('steps', 0):,} | C: {metrics.get('visited_c', 0):,} | "
        f"D: {metrics.get('visited_d', 0):,} | C∩D: {metrics.get('intersection_c_d', 0)} | "
        f"DiagFrac: {metrics.get('diagonal_fraction', 0.0):.6f}"
    )
    draw.text((20, 42), sub, fill=MUTED_TEXT, font=font_sm)

    # Graph areas
    plot_x0, plot_x1 = 50, W - 30
    plot_w = plot_x1 - plot_x0

    # Panel C visits
    y0_c, y1_c = 80, 170
    draw.rectangle([plot_x0, y0_c, plot_x1, y1_c], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((plot_x0 + 8, y0_c + 5), "Code Pointer (c) Footprint & Density", fill=ACCENT_CYAN, font=font_sm)

    # Panel D visits
    y0_d, y1_d = 185, 275
    draw.rectangle([plot_x0, y0_d, plot_x1, y1_d], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((plot_x0 + 8, y0_d + 5), "Data Pointer (d) Footprint & Density", fill=ACCENT_AMBER, font=font_sm)

    # Panel Mutations
    y0_m, y1_m = 290, 340
    draw.rectangle([plot_x0, y0_m, plot_x1, y1_m], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((plot_x0 + 8, y0_m + 5), "Mutations & Writes (* / p / xlat2)", fill=ACCENT_MAGENTA, font=font_sm)

    # Bin the 59049 cells into plot_w bins
    c_bins = np.zeros(plot_w, dtype=np.float64)
    d_bins = np.zeros(plot_w, dtype=np.float64)
    m_bins = np.zeros(plot_w, dtype=np.float64)

    import csv
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = int(row["address"])
            bin_idx = int((addr * plot_w) / N)
            if bin_idx >= plot_w:
                bin_idx = plot_w - 1
            c_v = float(row["c_visits"])
            d_v = float(row["d_visits"])
            w_v = float(row["writes"])
            e_v = float(row["encryptions"])
            c_bins[bin_idx] += c_v
            d_bins[bin_idx] += d_v
            m_bins[bin_idx] += (w_v + e_v)

    # Normalize log scales
    c_max = max(1.0, float(np.max(c_bins)))
    d_max = max(1.0, float(np.max(d_bins)))
    m_max = max(1.0, float(np.max(m_bins)))

    log_c = np.log1p(c_bins) / math.log1p(c_max)
    log_d = np.log1p(d_bins) / math.log1p(d_max)
    log_m = np.log1p(m_bins) / math.log1p(m_max)

    # Plot bars
    for i in range(plot_w):
        x = plot_x0 + i
        # C plot
        hc = int(log_c[i] * (y1_c - y0_c - 20))
        if hc > 0:
            draw.line([(x, y1_c - 1), (x, y1_c - 1 - hc)], fill=ACCENT_CYAN, width=1)
        # D plot
        hd = int(log_d[i] * (y1_d - y0_d - 20))
        if hd > 0:
            draw.line([(x, y1_d - 1), (x, y1_d - 1 - hd)], fill=ACCENT_AMBER, width=1)
        # M plot
        hm = int(log_m[i] * (y1_m - y0_m - 18))
        if hm > 0:
            draw.line([(x, y1_m - 1), (x, y1_m - 1 - hm)], fill=ACCENT_MAGENTA, width=1)

    # X axis marks
    for mark in [0, 10000, 20000, 30000, 40000, 50000, 59048]:
        mx = plot_x0 + int((mark * plot_w) / N)
        draw.line([(mx, y1_m), (mx, y1_m + 5)], fill=MUTED_TEXT, width=1)
        draw.text((mx - 12, y1_m + 8), str(mark), fill=MUTED_TEXT, font=font_sm)

    im.save(out_path)


def render_block_grid(csv_path: Path, out_path: Path, W: int, title: str = "Block Grid"):
    """Render memory as a 2D block grid of width W, showing c/d/mutation footprints."""
    H = math.ceil(N / W)
    scale = 3 if W <= 94 else (2 if W <= 188 else 1)
    
    pad_top = 60
    pad_side = 30
    canvas_w = W * scale + pad_side * 2
    canvas_h = H * scale + pad_top + 40

    im = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
    draw = ImageDraw.Draw(im)

    font_title = _get_font(16)
    font_sm = _get_font(12)

    draw.text((pad_side, 15), f"{title} (W={W}, H={H})", fill=TEXT_COLOR, font=font_title)
    draw.text((pad_side, 38), "Cyan: C only | Amber: D only | Magenta: C∩D | Green: Mutations", fill=MUTED_TEXT, font=font_sm)

    grid = np.zeros((H, W, 3), dtype=np.uint8)

    import csv
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = int(row["address"])
            if addr >= N:
                break
            x = addr % W
            y = addr // W
            c_v = int(row["c_visits"]) > 0
            d_v = int(row["d_visits"]) > 0
            mut = int(row["mutated"]) > 0

            if c_v and d_v:
                grid[y, x] = [255, 50, 150]  # Magenta
            elif c_v:
                grid[y, x] = [0, 200, 255]   # Cyan
            elif d_v:
                grid[y, x] = [255, 170, 0]   # Amber
            elif mut:
                grid[y, x] = [50, 220, 100]  # Green
            else:
                grid[y, x] = [18, 22, 32]    # Dark empty

    grid_img = Image.fromarray(grid)
    if scale > 1:
        grid_img = grid_img.resize((W * scale, H * scale), Image.NEAREST)

    im.paste(grid_img, (pad_side, pad_top))
    draw.rectangle([pad_side - 1, pad_top - 1, pad_side + W * scale, pad_top + H * scale], outline=GRID_LINE)

    im.save(out_path)


def render_modular_circular(csv_path: Path, sample_path: Path, out_path: Path, metrics: Dict[str, Any], title: str = "Circular Modular Projection"):
    """Render modular circular projection theta = 2*pi*address/59049 with jump chords."""
    size = 600
    im = Image.new("RGB", (size, size), BG_COLOR)
    draw = ImageDraw.Draw(im)

    font_title = _get_font(16)
    font_sm = _get_font(12)

    draw.text((20, 15), title, fill=TEXT_COLOR, font=font_title)
    draw.text((20, 38), "theta = 2*pi*address / 59049 (Circular geometry imposed by projection)", fill=MUTED_TEXT, font=font_sm)

    cx, cy = size // 2, size // 2 + 15
    r_outer = size * 0.38
    r_inner = size * 0.30

    # Draw reference circles
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], outline=(40, 48, 65), width=2)
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], outline=(30, 36, 50), width=1)

    # Angle markers
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg) - math.pi / 2
        x1 = cx + (r_outer + 4) * math.cos(rad)
        y1 = cy + (r_outer + 4) * math.sin(rad)
        x2 = cx + (r_outer + 12) * math.cos(rad)
        y2 = cy + (r_outer + 12) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=MUTED_TEXT, width=1)
        addr_mark = int((angle_deg / 360.0) * N)
        tx = cx + (r_outer + 24) * math.cos(rad)
        ty = cy + (r_outer + 24) * math.sin(rad)
        draw.text((tx - 12, ty - 6), str(addr_mark), fill=MUTED_TEXT, font=font_sm)

    # Read sampled jumps from trace_sample.json and draw chords
    with open(sample_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    # Draw subset of jumps as chords
    jumps_drawn = 0
    for s in samples:
        if s.get("op") == "i" and jumps_drawn < 600:
            c_from = s.get("c", 0)
            c_to = s.get("next_c", 0)
            th1 = 2 * math.pi * c_from / N - math.pi / 2
            th2 = 2 * math.pi * c_to / N - math.pi / 2
            x1 = cx + r_inner * math.cos(th1)
            y1 = cy + r_inner * math.sin(th1)
            x2 = cx + r_inner * math.cos(th2)
            y2 = cy + r_inner * math.sin(th2)
            draw.line([(x1, y1), (x2, y2)], fill=(0, 160, 220, 60), width=1)
            jumps_drawn += 1

    # Plot C and D address presence on the rings
    import csv
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = int(row["address"])
            th = 2 * math.pi * addr / N - math.pi / 2
            cos_t = math.cos(th)
            sin_t = math.sin(th)
            c_v = int(row["c_visits"]) > 0
            d_v = int(row["d_visits"]) > 0
            if c_v:
                x = cx + r_outer * cos_t
                y = cy + r_outer * sin_t
                draw.point((x, y), fill=ACCENT_CYAN)
            if d_v:
                x = cx + r_inner * cos_t
                y = cy + r_inner * sin_t
                draw.point((x, y), fill=ACCENT_AMBER)

    draw.text((cx - 80, cy - 10), "Ring 1 (outer): C", fill=ACCENT_CYAN, font=font_sm)
    draw.text((cx - 80, cy + 10), "Ring 2 (inner): D", fill=ACCENT_AMBER, font=font_sm)
    draw.text((cx - 80, cy + 30), f"Jumps: {metrics.get('breaks_i', 0):,}", fill=(100, 180, 255), font=font_sm)

    im.save(out_path)


def render_cd_trajectory(sample_path: Path, out_path: Path, metrics: Dict[str, Any], title: str = "(c, d) Trajectory & Torus Space"):
    """Render 2D (c, d) state space trajectory and 3D torus isometric embedding."""
    W, H = 1000, 520
    im = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(im)

    font_title = _get_font(16)
    font_sm = _get_font(12)

    draw.text((20, 15), title, fill=TEXT_COLOR, font=font_title)
    draw.text((20, 38), "Left: 2D (c, d) Modulo Space | Right: 3D Torus Isometric Embedding", fill=MUTED_TEXT, font=font_sm)

    # Left: 2D (c, d) plot in 420x420 panel
    p2_x0, p2_y0, p2_size = 40, 70, 420
    draw.rectangle([p2_x0, p2_y0, p2_x0 + p2_size, p2_y0 + p2_size], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((p2_x0 + 10, p2_y0 + 10), "c axis (0..59048) ->", fill=ACCENT_CYAN, font=font_sm)
    draw.text((p2_x0 + 10, p2_y0 + 26), "d axis (0..59048) v", fill=ACCENT_AMBER, font=font_sm)

    # Diagonal guide line
    draw.line([(p2_x0, p2_y0), (p2_x0 + p2_size, p2_y0 + p2_size)], fill=(45, 52, 70), width=1)
    draw.text((p2_x0 + p2_size - 130, p2_y0 + p2_size - 20), "c == d (diagonal)", fill=MUTED_TEXT, font=font_sm)

    # Right: 3D Torus embedding in 460x420 panel
    p3_x0, p3_y0, p3_w, p3_h = 510, 70, 450, 420
    draw.rectangle([p3_x0, p3_y0, p3_x0 + p3_w, p3_y0 + p3_h], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((p3_x0 + 10, p3_y0 + 10), "3D Torus Projection: (theta_c, theta_d) in (S1 x S1)", fill=TEXT_COLOR, font=font_sm)
    draw.text((p3_x0 + 10, p3_y0 + 26), "Isometric projection of embedded torus", fill=MUTED_TEXT, font=font_sm)

    # Render torus wireframe background
    cx3, cy3 = p3_x0 + p3_w // 2, p3_y0 + p3_h // 2 + 10
    R_major = 130.0
    r_minor = 50.0

    # Draw torus rings
    for u_deg in range(0, 360, 30):
        u = math.radians(u_deg)
        pts = []
        for v_deg in range(0, 360, 10):
            v = math.radians(v_deg)
            x3d = (R_major + r_minor * math.cos(v)) * math.cos(u)
            y3d = (R_major + r_minor * math.cos(v)) * math.sin(u)
            z3d = r_minor * math.sin(v)
            # isometric rotation
            iso_x = (x3d - y3d) * math.cos(math.radians(30))
            iso_y = (x3d + y3d) * math.sin(math.radians(30)) * 0.5 - z3d * 0.8
            pts.append((cx3 + iso_x, cy3 + iso_y))
        for k in range(len(pts) - 1):
            draw.line([pts[k], pts[k + 1]], fill=(25, 32, 45), width=1)

    # Load samples and plot trajectories
    with open(sample_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    n_samples = len(samples)
    prev_2d = None
    prev_3d = None

    for idx, s in enumerate(samples):
        c_val = s.get("c", 0)
        d_val = s.get("d", 0)
        t_ratio = idx / max(1, n_samples)

        # Color gradient by time: purple -> cyan -> yellow
        r = int(120 * (1 - t_ratio) + 255 * t_ratio)
        g = int(50 * (1 - t_ratio) + 200 * t_ratio)
        b = int(255 * (1 - t_ratio) + 50 * t_ratio)
        color = (r, g, b)

        # Left 2D point
        px = p2_x0 + int((c_val * p2_size) / N)
        py = p2_y0 + int((d_val * p2_size) / N)
        if prev_2d:
            # draw line if not a huge modular wrap
            if abs(px - prev_2d[0]) < p2_size // 3 and abs(py - prev_2d[1]) < p2_size // 3:
                draw.line([prev_2d, (px, py)], fill=color, width=1)
        prev_2d = (px, py)
        draw.point((px, py), fill=color)

        # Right 3D torus point
        th_c = 2 * math.pi * c_val / N
        th_d = 2 * math.pi * d_val / N
        x3d = (R_major + r_minor * math.cos(th_c)) * math.cos(th_d)
        y3d = (R_major + r_minor * math.cos(th_c)) * math.sin(th_d)
        z3d = r_minor * math.sin(th_c)
        iso_x = (x3d - y3d) * math.cos(math.radians(30))
        iso_y = (x3d + y3d) * math.sin(math.radians(30)) * 0.5 - z3d * 0.8
        p3_pt = (cx3 + iso_x, cy3 + iso_y)

        if prev_3d and abs(p3_pt[0] - prev_3d[0]) < 80 and abs(p3_pt[1] - prev_3d[1]) < 80:
            draw.line([prev_3d, p3_pt], fill=color, width=1)
        prev_3d = p3_pt
        draw.point(p3_pt, fill=color)

    im.save(out_path)


def render_mutation_heatmap(csv_path: Path, sample_path: Path, out_path: Path, metrics: Dict[str, Any], title: str = "Self-Modification Analysis"):
    """Render self-modification heatmap: initial vs modified vs encrypted vs timeline."""
    W, H = 1000, 400
    im = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(im)

    font_title = _get_font(16)
    font_sm = _get_font(12)

    draw.text((20, 15), title, fill=TEXT_COLOR, font=font_title)
    sub = (
        f"Total Writes: {metrics.get('total_writes', 0):,} | "
        f"Encryptions: {metrics.get('total_encryptions', 0):,} | "
        f"Mutated Cells: {metrics.get('mutated_cells', 0):,}"
    )
    draw.text((20, 38), sub, fill=MUTED_TEXT, font=font_sm)

    # 1. Spatial mutation map (0..59048) in top panel
    p1_x0, p1_x1 = 50, W - 30
    p1_w = p1_x1 - p1_x0
    p1_y0, p1_y1 = 75, 185
    draw.rectangle([p1_x0, p1_y0, p1_x1, p1_y1], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((p1_x0 + 8, p1_y0 + 6), "Spatial Distribution of Writes (* and p opcodes)", fill=ACCENT_MAGENTA, font=font_sm)

    # 2. Encryption map (0..59048) in middle panel
    p2_y0, p2_y1 = 195, 290
    draw.rectangle([p1_x0, p2_y0, p1_x1, p2_y1], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((p1_x0 + 8, p2_y0 + 6), "Spatial Distribution of xlat2 Encryptions", fill=ACCENT_CYAN, font=font_sm)

    # 3. Timeline of writes across sampled steps
    p3_y0, p3_y1 = 300, 370
    draw.rectangle([p1_x0, p3_y0, p1_x1, p3_y1], fill=PANEL_BG, outline=GRID_LINE)
    draw.text((p1_x0 + 8, p3_y0 + 6), "Temporal Timeline of Writes & Encryptions across Execution", fill=ACCENT_GREEN, font=font_sm)

    w_bins = np.zeros(p1_w, dtype=np.float64)
    e_bins = np.zeros(p1_w, dtype=np.float64)

    import csv
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = int(row["address"])
            bin_idx = int((addr * p1_w) / N)
            if bin_idx >= p1_w:
                bin_idx = p1_w - 1
            w_bins[bin_idx] += float(row["writes"])
            e_bins[bin_idx] += float(row["encryptions"])

    log_w = np.log1p(w_bins) / math.log1p(max(1.0, float(np.max(w_bins))))
    log_e = np.log1p(e_bins) / math.log1p(max(1.0, float(np.max(e_bins))))

    for i in range(p1_w):
        x = p1_x0 + i
        hw = int(log_w[i] * (p1_y1 - p1_y0 - 24))
        if hw > 0:
            draw.line([(x, p1_y1 - 1), (x, p1_y1 - 1 - hw)], fill=ACCENT_MAGENTA, width=1)
        he = int(log_e[i] * (p2_y1 - p2_y0 - 24))
        if he > 0:
            draw.line([(x, p2_y1 - 1), (x, p2_y1 - 1 - he)], fill=ACCENT_CYAN, width=1)

    # Sampled timeline
    with open(sample_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    total_steps = metrics.get("steps", 1)
    for s in samples:
        st = s.get("step", 0)
        tx = p1_x0 + int((st * p1_w) / max(1, total_steps))
        if tx < p1_x1:
            if s.get("write") is not None:
                draw.line([(tx, p3_y1 - 1), (tx, p3_y0 + 20)], fill=ACCENT_MAGENTA, width=1)
            elif s.get("enc_addr") is not None:
                draw.line([(tx, p3_y1 - 1), (tx, p3_y1 - 10)], fill=ACCENT_CYAN, width=1)

    im.save(out_path)
