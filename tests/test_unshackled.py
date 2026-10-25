"""Unit tests for Malbolge Unshackled Galactic Projections and Provenance."""

import json
from pathlib import Path
import pytest
from src.unshackled_bridge import (
    UNSHACKLED_PROVENANCE,
    EMPIRICAL_EXECUTION_METRICS,
    UNSHACKLED_TRITS,
    UNSHACKLED_MEM_SIZE,
    UNIVERSE_MIDPOINT,
    CLASSIC_MEM_SIZE,
    SCALE_RATIO_UNSHACKLED_VS_CLASSIC,
    project_to_classic_shadow,
    project_to_macro_coords,
)


def test_unshackled_constants():
    """Verify exact trinary powers and dimensional scale factors."""
    assert UNSHACKLED_TRITS == 19
    assert UNSHACKLED_MEM_SIZE == 3**19
    assert UNSHACKLED_MEM_SIZE == 1_162_261_467
    assert UNIVERSE_MIDPOINT == (UNSHACKLED_MEM_SIZE - 1) // 2
    assert UNIVERSE_MIDPOINT == 581_130_733
    assert CLASSIC_MEM_SIZE == 3**10
    assert CLASSIC_MEM_SIZE == 59_049
    assert SCALE_RATIO_UNSHACKLED_VS_CLASSIC == 3**9
    assert SCALE_RATIO_UNSHACKLED_VS_CLASSIC == 19_683


def test_unshackled_provenance_metadata():
    """Verify that full scientific and historical attribution is preserved."""
    assert "Iczelia (2020-2021)" in UNSHACKLED_PROVENANCE["authors"]
    assert any("Palaiologos" in author for author in UNSHACKLED_PROVENANCE["authors"])
    assert UNSHACKLED_PROVENANCE["unshackled_spec_author"] == "Lou Scheffer"
    assert UNSHACKLED_PROVENANCE["original_repository"] == "https://github.com/kspalaiologos/malbolge-lisp"
    assert "Public Domain" in UNSHACKLED_PROVENANCE["original_license"]
    assert "GPLv3" in UNSHACKLED_PROVENANCE["original_license"]


def test_classic_shadow_projection():
    """Verify projection from 19-trit space to 10-trit torus coordinates."""
    c_mod, d_mod = project_to_classic_shadow(UNIVERSE_MIDPOINT, UNIVERSE_MIDPOINT)
    assert 0 <= c_mod < CLASSIC_MEM_SIZE
    assert 0 <= d_mod < CLASSIC_MEM_SIZE
    assert c_mod == UNIVERSE_MIDPOINT % CLASSIC_MEM_SIZE
    assert d_mod == UNIVERSE_MIDPOINT % CLASSIC_MEM_SIZE

    # Origin projection
    c_0, d_0 = project_to_classic_shadow(0, 0)
    assert c_0 == 0
    assert d_0 == 0


def test_macro_coords_normalization():
    """Verify that universe midpoint normalizes to exactly (0.0, 0.0)."""
    norm_c, norm_d = project_to_macro_coords(UNIVERSE_MIDPOINT, UNIVERSE_MIDPOINT)
    assert pytest.approx(norm_c, abs=1e-7) == 0.0
    assert pytest.approx(norm_d, abs=1e-7) == 0.0

    # Bounds check
    norm_c_min, norm_d_min = project_to_macro_coords(0, 0)
    assert -1.0 <= norm_c_min <= 0.0
    assert -1.0 <= norm_d_min <= 0.0


def test_execution_metrics_integrity():
    """Verify that real empirical execution counts match measured telemetry."""
    metrics = EMPIRICAL_EXECUTION_METRICS
    assert metrics["input_expression"] == "(+ 1 2)"
    assert metrics["result_output"] == "3"
    assert metrics["total_steps"] == 2_401_426_209
    assert metrics["opcodes"]["JMP_4"] == 1_086_386_934
    assert pytest.approx(metrics["jmp_percentage"], rel=1e-2) == 45.24


def test_provenance_json_files():
    """Verify on-disk JSON metadata and provenance files."""
    repo_root = Path(__file__).resolve().parent.parent
    prov_file = repo_root / "results" / "malbolgelisp_unshackled" / "provenance.json"
    metrics_file = repo_root / "results" / "malbolgelisp_unshackled" / "execution_metrics.json"

    assert prov_file.exists()
    assert metrics_file.exists()

    with open(prov_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["project"] == "MalbolgeLISP v1.2"
        assert data["provenance"]["unshackled_architecture"] == "Lou Scheffer"

    with open(metrics_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["target_expression"] == "(+ 1 2)"
        assert data["evaluation_result"] == "3"
        assert data["execution_metrics"]["total_instructions"] == 2_401_426_209


def test_visual_assets_exist():
    """Verify that high-resolution visual assets exist in assets/ directory."""
    repo_root = Path(__file__).resolve().parent.parent
    macro_png = repo_root / "assets" / "malbolgelisp_macro_phase_space.png"
    orbit_gif = repo_root / "assets" / "malbolgelisp_torus_orbit.gif"

    assert macro_png.exists()
    assert macro_png.stat().st_size > 5000
    assert orbit_gif.exists()
    assert orbit_gif.stat().st_size > 20000
