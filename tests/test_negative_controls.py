"""
Unit tests for negative controls (falsification tests) in MalbolgArt.
Tests:
  N1: Renderer circularity falsification
  N4: Synthetic periodic sequence comparison
  N7: False loop / full state cycle refutation
"""

import json
from pathlib import Path
import pytest
from src.negative_controls import (
    run_n1_circular_renderer_control,
    run_n4_synthetic_sequence_control,
    run_n7_false_loop_control,
)


def test_n1_renderer_circularity(tmp_path):
    """Verify N1 control shows FLOW orbit profile produces circular layout on random walks."""
    res = run_n1_circular_renderer_control(tmp_path / "n1")
    assert res["control"] == "N1_RENDERER_CIRCULAR"
    assert res["verdict"] == "DEMONSTRATED"
    assert (tmp_path / "n1" / "n1_orbit_artificial_circle.gif").exists()


def test_n4_synthetic_sequence(tmp_path):
    """Verify N4 control distinguishes true algebraic periodicity from chaotic/irregular motion."""
    res = run_n4_synthetic_sequence_control(tmp_path / "n4")
    assert res["control"] == "N4_SYNTHETIC_SEQUENCE"
    assert res["known_period"] == 729
    assert res["detected_period"] == 729
    assert res["verdict"] == "DEMONSTRATED"


def test_n7_false_loop_refutation(tmp_path):
    """Verify N7 control refutes that returning to address c implies a full state cycle."""
    sample_file = Path("results/quine_m281/trace_sample.json")
    if not sample_file.exists():
        pytest.skip("Trace sample for m281 not found")

    res = run_n7_false_loop_control(sample_file, sample_file, tmp_path / "n7")
    assert res["control"] == "N7_FALSE_LOOP"
    assert res["full_state_identical"] is False
    assert res["verdict"] == "DEMONSTRATED"
