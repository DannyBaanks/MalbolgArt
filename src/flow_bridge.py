"""FLOW Bridge: converts Malbolge trace samples into valid FLOW ExecutionTrace
dictionaries and invokes FLOW render profiles (debug, trails, heatmap, orbit, cinematic).

NOTE: FLOW executes the visualization program; the Malbolge semantics were
executed by its own Classic VM.
"""

import sys
import json
import math
from pathlib import Path
from typing import Any, Dict, List

# Ensure FLOW is on python path
FLOW_DIR = Path("/home/danny/Development/ISyCo Git/FLOW")
if str(FLOW_DIR) not in sys.path:
    sys.path.insert(0, str(FLOW_DIR))

from flow.render.profiles import render_profile
from flow.render.spec import RenderSpec, RenderEntity

N = 59049
CANVAS_DIM = 243  # 243 * 243 = 59049 (3^5 x 3^5)


def convert_malbolge_sample_to_flow_trace(
    samples: List[Dict[str, Any]],
    program_name: str,
    program_sha256: str,
    max_ticks: int = 80
) -> Dict[str, Any]:
    """Convert Malbolge sampled steps into an authentic FLOW ExecutionTrace."""
    if not samples:
        return {}

    n_samples = len(samples)
    step_stride = max(1, n_samples // max_ticks)
    selected_steps = samples[::step_stride][:max_ticks]

    num_ticks = len(selected_steps)

    trace = {
        "metadata": {
            "engine": "FLOW-Malbolge-Bridge",
            "engine_version": "0.1.0",
            "program_name": program_name,
            "program_sha256": program_sha256,
            "note": "FLOW executes the visualization presentation; Malbolge was executed by Classic VM",
            "seed": 42,
            "config": {
                "image_size": [CANVAS_DIM, CANVAS_DIM],
                "max_ticks": num_ticks,
                "max_particles": 2
            },
            "ticks": num_ticks,
            "particles_spawned": 2,
            "final_alive": 2,
            "execution_order_rule": "ASCENDING_ID"
        },
        "ticks": [{"tick": t, "alive_before": 2, "alive_after": 2, "total_particles": 2} for t in range(num_ticks)],
        "events": []
    }

    # Spawn events at tick 0
    first = selected_steps[0]
    c0 = first.get("c", 0)
    d0 = first.get("d", 0)
    x_c0 = float(c0 % CANVAS_DIM)
    y_c0 = float(c0 // CANVAS_DIM)
    x_d0 = float(d0 % CANVAS_DIM)
    y_d0 = float(d0 // CANVAS_DIM)

    trace["events"].append({
        "tick": 0,
        "pid": 0,
        "type": "PARTICLE_SPAWN",
        "payload": {"x": x_c0, "y": y_c0, "src": "code_pointer_c"}
    })
    trace["events"].append({
        "tick": 1,
        "pid": 1,
        "type": "PARTICLE_SPAWN",
        "payload": {"x": x_d0, "y": y_d0, "src": "data_pointer_d"}
    })

    prev_xc, prev_yc = x_c0, y_c0
    prev_xd, prev_yd = x_d0, y_d0

    op_names = {
        "j": "MOV_D",
        "i": "JMP_C",
        "*": "ROTR_D",
        "p": "CRAZY",
        "<": "OUTPUT",
        "/": "INPUT",
        "v": "HALT",
        "o": "NOP"
    }

    for t_idx, step_data in enumerate(selected_steps):
        c_val = step_data.get("c", 0)
        d_val = step_data.get("d", 0)
        op_char = step_data.get("op", "o")
        mnemonic = op_names.get(op_char, "OP")

        xc = float(c_val % CANVAS_DIM)
        yc = float(c_val // CANVAS_DIM)
        xd = float(d_val % CANVAS_DIM)
        yd = float(d_val // CANVAS_DIM)

        # Move events
        trace["events"].append({
            "tick": t_idx,
            "pid": 0,
            "type": "PARTICLE_MOVE",
            "payload": {
                "x_from": prev_xc,
                "y_from": prev_yc,
                "x_to": xc,
                "y_to": yc
            }
        })
        trace["events"].append({
            "tick": t_idx,
            "pid": 1,
            "type": "PARTICLE_MOVE",
            "payload": {
                "x_from": prev_xd,
                "y_from": prev_yd,
                "x_to": xd,
                "y_to": yd
            }
        })

        # Trace event (memory value / encryption)
        enc_val = step_data.get("enc_val")
        if enc_val is not None:
            trace["events"].append({
                "tick": t_idx,
                "pid": 0,
                "type": "PARTICLE_TRACE",
                "payload": {"x": int(xc), "y": int(yc), "value": int(enc_val) & 0xFF}
            })

        # Instruction execution event
        trace["events"].append({
            "tick": t_idx,
            "pid": 0,
            "type": "INSTRUCTION_EXECUTED",
            "payload": {"mnemonic": mnemonic}
        })

        prev_xc, prev_yc = xc, yc
        prev_xd, prev_yd = xd, yd

    return trace


def render_all_flow_profiles(
    sample_path: Path,
    out_dir: Path,
    program_name: str,
    program_sha256: str,
    max_frames: int = 50
) -> Dict[str, str]:
    """Generate all 5 requested FLOW profile GIFs."""
    with open(sample_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    flow_trace = convert_malbolge_sample_to_flow_trace(
        samples, program_name, program_sha256, max_ticks=max_frames
    )

    rendered_files = {}
    profiles = ["debug", "trails", "heatmap", "orbit", "cinematic"]

    entities = [
        RenderEntity(id="pid_0", label="Pointer C (code)", pid=0),
        RenderEntity(id="pid_1", label="Pointer D (data)", pid=1)
    ]

    for prof in profiles:
        out_file = out_dir / f"flow_{prof}.gif"
        spec = RenderSpec(
            profile=prof,
            scale=2,
            max_frames=max_frames,
            entities=entities,
            layout={"canvas": [360, 360]}
        )
        try:
            render_profile(flow_trace, out_file, spec, program_name=program_name)
            rendered_files[prof] = str(out_file)
        except Exception as e:
            print(f"Error rendering {prof}: {e}", file=sys.stderr)

    return rendered_files
