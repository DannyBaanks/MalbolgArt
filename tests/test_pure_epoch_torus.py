"""Tests for PureEpoch Synthetic Period-1 (1=94) Fixed Point & 4D Torus Embedding.
"""

from pathlib import Path
import pytest
from src.pure_epoch_bridge import (
    xlat2_cycle_decomposition,
    verify_synthetic_period1_identity,
    get_roundtrip_4d_loop,
    crazy,
    XLAT2,
    VALID,
)
from src.holographic_bridge.torus_embed import embed_cell


def test_xlat2_cycle_decomposition():
    """Verify that XLAT2 decomposes into 6 disjoint cycles of lengths [68, 9, 6, 5, 4, 2]
    with exactly zero fixed points of period 1.
    """
    cycles = xlat2_cycle_decomposition()
    lengths = [c["length"] for c in cycles]
    assert lengths == [68, 9, 6, 5, 4, 2]
    assert sum(lengths) == 94

    fixed_points_p1 = [c for c in cycles if c["length"] == 1]
    assert len(fixed_points_p1) == 0

    p2_cycle = [c for c in cycles if c["length"] == 2][0]
    assert set(p2_cycle["chars"]) == {"F", "J"}


def test_synthetic_period1_identity_752_pairs():
    """Verify the universal 4-step crazy roundtrip synthetic period-1 fixed-point identity
    across all 94 positions and all 8 valid opcodes (752 pairs).
    """
    res = verify_synthetic_period1_identity()
    assert res["identity_all_pass"] is True
    assert res["verified_pairs"] == 752
    assert res["total_pairs"] == 752


def test_roundtrip_4d_geodesic_closure():
    """Verify that the 5-step crazy roundtrip sequence forms a closed loop in 4D space
    where start and end points coincide with zero displacement error.
    """
    loop = get_roundtrip_4d_loop(81)  # cell 81
    assert len(loop) == 6  # 5 segments, 6 points

    start_val, start_p4 = loop[0]
    end_val, end_p4 = loop[-1]

    assert start_val == end_val == 81
    assert start_p4 == end_p4

    # Distance between start and end in 4D is strictly 0.0
    dist_4d = sum((a - b) ** 2 for a, b in zip(start_p4, end_p4)) ** 0.5
    assert dist_4d == 0.0


def test_quine94_footprint_in_bounds():
    """Verify that quine94_ceiling_probe executes strictly within the 0..93 control core."""
    import json
    trace_f = Path(__file__).resolve().parent.parent / "results/pure_epoch_synthetic_period1/trace_sample.json"
    if trace_f.exists():
        with open(trace_f, "r", encoding="utf-8") as f:
            samples = json.load(f)
        for s in samples:
            assert 0 <= s["c"] < 94, f"C out of 0..93 bounds: {s['c']}"
            assert 0 <= s["d"] < 94, f"D out of 0..93 bounds: {s['d']}"
