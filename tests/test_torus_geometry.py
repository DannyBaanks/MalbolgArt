"""
Unit tests for 4D Clifford Torus embedding in MalbolgArt.
Tests mathematical properties: norms, radii, 4D rotation, stereographic projection.
"""

import math
import pytest
from src.holographic_bridge.torus_embed import (
    embed_cell,
    embed_cell_disambiguated,
    rotate4,
    project_stereo,
    verify_embedding_properties,
)


def test_embedding_radii_and_norms():
    """Verify that every cell embeds onto S^1(20) x S^1(10) in R^4."""
    for c in [0, 1, 47, 188, 1000, 29515, 29516, 59031, 59048]:
        p = embed_cell(c)
        assert len(p) == 4

        # Circle 1 norm (first two coordinates)
        norm1 = math.sqrt(p[0] ** 2 + p[1] ** 2)
        assert math.isclose(norm1, 20.0, rel_tol=1e-5), f"Cell {c} circle 1 norm failed: {norm1}"

        # Circle 2 norm (last two coordinates)
        norm2 = math.sqrt(p[2] ** 2 + p[3] ** 2)
        assert math.isclose(norm2, 10.0, rel_tol=1e-5), f"Cell {c} circle 2 norm failed: {norm2}"

        # Total 4D distance from origin = sqrt(20^2 + 10^2) = sqrt(500)
        norm_total = math.sqrt(sum(x ** 2 for x in p))
        assert math.isclose(norm_total, math.sqrt(500.0), rel_tol=1e-5)


def test_rotation_isometry():
    """Verify that 4D rotation preserves Euclidean distances in R^4."""
    p = embed_cell(188)
    p_rot = rotate4(p, plane=(0, 3), ang=0.45)
    p_rot = rotate4(p_rot, plane=(1, 2), ang=1.23)

    norm_orig = math.sqrt(sum(x ** 2 for x in p))
    norm_rot = math.sqrt(sum(x ** 2 for x in p_rot))
    assert math.isclose(norm_orig, norm_rot, rel_tol=1e-5)


def test_stereographic_projection():
    """Verify 4D to 3D stereographic projection."""
    p = embed_cell(42)
    p3 = project_stereo(p, R=40.0)
    assert len(p3) == 3
    assert all(math.isfinite(x) for x in p3)


def test_embedding_properties_suite():
    """Run full embedding verification suite on sampled space."""
    res = verify_embedding_properties()
    assert res["norm_c1_expected"] == 20.0
    assert res["norm_c2_expected"] == 10.0
    assert res["norm_c1_errors"] == 0
    assert res["norm_c2_errors"] == 0
    assert res["is_two_sheeted_covering"] is True
