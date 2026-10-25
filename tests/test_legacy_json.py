"""
Unit tests for historical HOLOGRAPHIC JSON parsing and inventorying.
"""

import pytest
from pathlib import Path
from src.holographic_bridge.legacy_import import (
    find_holographic_sources,
    load_legacy_json_inventory,
    import_lutter_trace,
    import_lutter_outs,
)


def test_locate_holographic():
    """Verify that HOLOGRAPHIC directory is located with valid assets."""
    h_dir = find_holographic_sources()
    assert h_dir is not None
    assert h_dir.exists()
    assert (h_dir / "lutter_trace.json").exists()
    assert (h_dir / "lutter_outs.json").exists()


def test_inventory_artifacts():
    """Verify inventory metadata for all 4 legacy JSON files."""
    h_dir = find_holographic_sources()
    inv = load_legacy_json_inventory(h_dir)
    files = inv.get("files", {})
    assert len(files) >= 4
    filenames = list(files.keys())
    assert "lutter_trace.json" in filenames
    assert "lutter_outs.json" in filenames
    assert "lutter_outs2.json" in filenames
    assert "lutter_outs_watch.json" in filenames


def test_parse_lutter_trace():
    """Verify parser for lutter_trace.json."""
    h_dir = find_holographic_sources()
    data = import_lutter_trace(h_dir)

    assert "points" in data
    assert "path" in data
    assert len(data["points"]) == 27293
    assert len(data["path"]) == 13909

    # Verify first point structure
    pt = data["points"][0]
    assert "step" in pt
    assert "op" in pt
    assert "p" in pt
    assert len(pt["p"]) == 4


def test_parse_lutter_outs():
    """Verify parser for lutter_outs.json."""
    h_dir = find_holographic_sources()
    outs = import_lutter_outs(h_dir, max_events=100)

    assert isinstance(outs, list)
    assert len(outs) == 100
    first_ev = outs[0]
    assert "step" in first_ev
    assert "c" in first_ev
    assert "d" in first_ev
    assert "out" in first_ev
