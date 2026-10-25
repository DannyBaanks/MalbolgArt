"""Align verified modern traces from MalbolgArt with the HOLOGRAPHIC 4D Clifford Torus.
Analyzes sheet dynamics, transitions, and angular velocities.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np

from .torus_embed import (
    embed_cell,
    MEM_SIZE,
    SHEET_SIZE,
)
from .sheets import sheet_of, sheet_id, TAIL_START


def analyze_sheet_dynamics(trace_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute sheet distribution, transition counts, and angular metrics for a sampled trace."""
    if not trace_samples:
        return {}

    steps_in_a = 0
    steps_in_b = 0
    steps_in_tail = 0

    trans_a_to_b = 0
    trans_b_to_a = 0
    trans_within_a = 0
    trans_within_b = 0
    trans_to_tail = 0
    trans_from_tail = 0

    prev_sheet = None
    prev_z = None
    prev_w = None

    dtheta_z_list = []
    dtheta_w_list = []

    for s in trace_samples:
        c = s.get("c", 0)
        sh = sheet_of(c)
        if sh == "A":
            steps_in_a += 1
        elif sh == "B":
            steps_in_b += 1
        else:
            steps_in_tail += 1

        z = (c // 4) % 47
        w = c // 188

        if prev_sheet is not None:
            if prev_sheet == "A" and sh == "B":
                trans_a_to_b += 1
            elif prev_sheet == "B" and sh == "A":
                trans_b_to_a += 1
            elif prev_sheet == "A" and sh == "A":
                trans_within_a += 1
            elif prev_sheet == "B" and sh == "B":
                trans_within_b += 1
            elif sh == "TAIL":
                trans_to_tail += 1
            elif prev_sheet == "TAIL":
                trans_from_tail += 1

            dz = min((z - prev_z) % 47, (prev_z - z) % 47)
            dw = min((w - prev_w) % 157, (prev_w - w) % 157)
            dtheta_z_list.append(2 * math.pi * dz / 47.0)
            dtheta_w_list.append(2 * math.pi * dw / 157.0)

        prev_sheet = sh
        prev_z = z
        prev_w = w

    n_samples = len(trace_samples)
    mean_dtheta_z = float(np.mean(dtheta_z_list)) if dtheta_z_list else 0.0
    mean_dtheta_w = float(np.mean(dtheta_w_list)) if dtheta_w_list else 0.0

    return {
        "sample_count": n_samples,
        "steps_in_sheet_a": steps_in_a,
        "steps_in_sheet_b": steps_in_b,
        "steps_in_tail": steps_in_tail,
        "fraction_sheet_a": steps_in_a / max(1, n_samples),
        "fraction_sheet_b": steps_in_b / max(1, n_samples),
        "fraction_tail": steps_in_tail / max(1, n_samples),
        "transitions": {
            "within_a": trans_within_a,
            "within_b": trans_within_b,
            "a_to_b": trans_a_to_b,
            "b_to_a": trans_b_to_a,
            "to_tail": trans_to_tail,
            "from_tail": trans_from_tail,
            "total_sheet_crossings": trans_a_to_b + trans_b_to_a,
        },
        "angular_displacement": {
            "mean_dtheta_z_rad": mean_dtheta_z,
            "mean_dtheta_w_rad": mean_dtheta_w,
        },
    }


def align_verified_trace_to_4d(sample_file: Path) -> Dict[str, Any]:
    """Load trace sample JSON, embed points in 4D, and compute dynamics."""
    with open(sample_file, "r", encoding="utf-8") as f:
        samples = json.load(f)

    dynamics = analyze_sheet_dynamics(samples)
    return dynamics
