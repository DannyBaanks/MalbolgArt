"""Importer and cataloger for historical HOLOGRAPHIC JSON artifacts.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional

HOLOGRAPHIC_SEARCH_DIRS = [
    Path("/home/danny/Development/ISyCo/workspace/assembly/holographic"),
    Path("/home/danny/Development/ISyCo/4D/holographic"),
    Path("/home/danny/Development/ISyCo-worktrees/malbolge-flow-torus/workspace/assembly/holographic"),
    Path("/home/danny/Development/ISyCo-worktrees/malbolge-flow-torus/4D/holographic"),
]


def find_holographic_sources() -> Optional[Path]:
    """Find the active local directory containing HOLOGRAPHIC artifacts."""
    for d in HOLOGRAPHIC_SEARCH_DIRS:
        if d.exists() and (d / "lutter_trace.json").exists():
            return d
    return None


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_legacy_json_inventory(src_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Catalog all historical Malbolge JSON files from HOLOGRAPHIC."""
    if src_dir is None:
        src_dir = find_holographic_sources()

    if src_dir is None or not src_dir.exists():
        return {"error": "HOLOGRAPHIC source directory not found"}

    inventory: Dict[str, Any] = {
        "holographic_source_dir": str(src_dir),
        "files": {},
    }

    targets = [
        ("lutter_trace.json", "HISTORICAL_4D_SAMPLED_TRACE"),
        ("lutter_outs.json", "HISTORICAL_CHRONOLOGICAL_OUTPUT_EVENTS"),
        ("lutter_outs2.json", "HISTORICAL_OUTPUTS_AND_TOP_CELLS"),
        ("lutter_outs_watch.json", "HISTORICAL_MEMORY_WATCH_EVENTS"),
    ]

    for fname, data_type in targets:
        fpath = src_dir / fname
        if not fpath.exists():
            continue

        sz = fpath.stat().st_size
        sha = _file_sha256(fpath)

        meta: Dict[str, Any] = {
            "path": str(fpath),
            "size_bytes": sz,
            "sha256": sha,
            "data_type": data_type,
        }

        # Inspect lightweight structure
        if fname == "lutter_trace.json":
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            meta["steps_declared"] = d.get("steps")
            meta["output_bytes_declared"] = d.get("output_bytes")
            meta["status_declared"] = d.get("status")
            meta["points_count"] = len(d.get("points", []))
            meta["path_sample_count"] = len(d.get("path", []))
            meta["sample_stride"] = 5000

        elif fname == "lutter_outs.json":
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            meta["event_count"] = len(d)
            if d:
                meta["first_event_step"] = d[0].get("step")
                meta["last_event_step"] = d[-1].get("step")
                meta["has_registers"] = all(k in d[0] for k in ["a", "c", "d", "out"])

        elif fname == "lutter_outs2.json":
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            meta["keys"] = list(d.keys())
            meta["outs_count"] = len(d.get("outs", []))
            meta["top_cells_count"] = len(d.get("top_cells", []))

        elif fname == "lutter_outs_watch.json":
            meta["description"] = "Per-output memory snapshots across 59,852 outputs (40.5 MB)"

        inventory["files"][fname] = meta

    return inventory


def import_lutter_trace(src_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Import and return the contents of lutter_trace.json."""
    if src_dir is None:
        src_dir = find_holographic_sources()
    if src_dir is None:
        raise FileNotFoundError("HOLOGRAPHIC directory not found")

    p = src_dir / "lutter_trace.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def import_lutter_outs(src_dir: Optional[Path] = None, max_events: Optional[int] = None) -> List[Dict[str, Any]]:
    """Import and return the output event sequence from lutter_outs.json."""
    if src_dir is None:
        src_dir = find_holographic_sources()
    if src_dir is None:
        raise FileNotFoundError("HOLOGRAPHIC directory not found")

    p = src_dir / "lutter_outs.json"
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if max_events is not None:
        return data[:max_events]
    return data
