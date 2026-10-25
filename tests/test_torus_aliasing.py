"""
Unit tests for the Two Sheets covering phenomenon and aliasing in Malbolge.
Validates:
  59049 = 2 * 29516 + 17
  embed_cell(c) == embed_cell(c + 29516) for all c in [0, 29515]
  Disambiguated coordinates restore injectivity.
"""

import math
import pytest
from src.holographic_bridge.torus_embed import (
    embed_cell,
    embed_cell_disambiguated,
)
from src.holographic_bridge.sheets import (
    sheet_of,
    SHEET_SIZE,
    TAIL_SIZE,
    TOTAL_CELLS,
    analyze_two_sheets,
)


def test_sheet_partition_constants():
    """Verify algebraic partition constants."""
    assert SHEET_SIZE == 29516
    assert TAIL_SIZE == 17
    assert TOTAL_CELLS == 59049
    assert 2 * SHEET_SIZE + TAIL_SIZE == TOTAL_CELLS
    assert SHEET_SIZE == 188 * 157
    assert 188 == 2 * 2 * 47


def test_sheet_classification():
    """Verify classification of addresses into Sheet A, B, and TAIL."""
    assert sheet_of(0) == "A"
    assert sheet_of(29515) == "A"
    assert sheet_of(29516) == "B"
    assert sheet_of(59031) == "B"
    assert sheet_of(59032) == "TAIL"
    assert sheet_of(59048) == "TAIL"


def test_exact_aliasing_sheet_a_and_b():
    """Verify that embed_cell(c) produces the EXACT same 4D coordinate as embed_cell(c + 29516)."""
    test_cases = [0, 1, 15, 47, 188, 500, 10000, 20000, 29515]
    for c in test_cases:
        p_a = embed_cell(c)
        p_b = embed_cell(c + SHEET_SIZE)

        for i in range(4):
            assert math.isclose(p_a[i], p_b[i], abs_tol=1e-12), (
                f"Aliasing failed at cell {c} coordinate {i}: {p_a[i]} != {p_b[i]}"
            )


def test_tail_triple_overlap():
    """Verify that cells in TAIL [59032..59048] alias with c in [0..16] and [29516..29532]."""
    for i in range(17):
        c_a = i
        c_b = i + SHEET_SIZE
        c_tail = i + 2 * SHEET_SIZE  # 59032 + i

        p_a = embed_cell(c_a)
        p_b = embed_cell(c_b)
        p_tail = embed_cell(c_tail)

        for dim in range(4):
            assert math.isclose(p_a[dim], p_b[dim], abs_tol=1e-12)
            assert math.isclose(p_a[dim], p_tail[dim], abs_tol=1e-12)


def test_disambiguation_restores_injectivity():
    """Verify embed_cell_disambiguated separates identical coordinates."""
    c_a = 42
    c_b = 42 + SHEET_SIZE

    p_a = embed_cell(c_a)
    p_b = embed_cell(c_b)
    assert p_a == pytest.approx(p_b, abs=1e-12)

    p_a_dis = embed_cell_disambiguated(c_a, sheet_offset=5.0)
    p_b_dis = embed_cell_disambiguated(c_b, sheet_offset=5.0)

    # Disambiguated points must NOT be equal
    dist = math.sqrt(sum((x - y) ** 2 for x, y in zip(p_a_dis, p_b_dis)))
    assert dist > 1.0


def test_analyze_two_sheets_coverage():
    """Verify analyze_two_sheets produces exactly 29,516 aliased pairs."""
    analysis = analyze_two_sheets()
    assert analysis["sheet_a_count"] == SHEET_SIZE
    assert analysis["sheet_b_count"] == SHEET_SIZE
    assert analysis["tail_count"] == TAIL_SIZE
    assert analysis["exact_aliased_pairs_count"] == SHEET_SIZE
    assert analysis["triple_overlap_count"] == TAIL_SIZE
