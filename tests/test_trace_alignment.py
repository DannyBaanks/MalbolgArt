"""
Unit tests for trace alignment to 4D Clifford Torus and sheet dynamics.
"""

import math
import pytest
from src.holographic_bridge.trace_alignment import (
    analyze_sheet_dynamics,
)


def test_sheet_dynamics_synthetic():
    """Verify sheet dynamics calculation on a known trajectory."""
    # Trajectory alternating between Sheet A and Sheet B
    steps = [
        {"c": 10, "d": 20},          # A
        {"c": 20, "d": 30},          # A
        {"c": 30000, "d": 35000},    # B (cross 1: A -> B)
        {"c": 30010, "d": 35010},    # B
        {"c": 50, "d": 60},          # A (cross 2: B -> A)
        {"c": 59035, "d": 59040},    # TAIL (cross 3: A -> TAIL)
    ]

    dyn = analyze_sheet_dynamics(steps)
    assert dyn["sample_count"] == 6
    assert dyn["steps_in_sheet_a"] == 3
    assert dyn["steps_in_sheet_b"] == 2
    assert dyn["steps_in_tail"] == 1
    assert dyn["transitions"]["a_to_b"] == 1
    assert dyn["transitions"]["b_to_a"] == 1
    assert dyn["transitions"]["to_tail"] == 1
