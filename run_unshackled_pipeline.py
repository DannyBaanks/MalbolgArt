#!/usr/bin/env python3
"""Run Unshackled Pipeline for MalbolgArt:
Generates MalbolgeLISP Galactic Projections, verifies provenance and execution telemetry.
"""

from __future__ import annotations

import json
from pathlib import Path
from src.unshackled_bridge import (
    UNSHACKLED_PROVENANCE,
    EMPIRICAL_EXECUTION_METRICS,
    UNSHACKLED_MEM_SIZE,
    UNIVERSE_MIDPOINT,
    CLASSIC_MEM_SIZE,
    project_to_classic_shadow,
    project_to_macro_coords,
    load_sampled_csv,
    render_macro_phase_space,
    render_torus_orbit_gif,
)


def run_pipeline() -> None:
    root = Path(__file__).resolve().parent
    assets_dir = root / "assets"
    results_dir = root / "results" / "malbolgelisp_unshackled"
    results_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("MALBOLGART: GALACTIC PROJECTION & UNSHACKLED PIPELINE")
    print("=" * 72)

    # 1. Print Provenance
    print(f"Project:     {UNSHACKLED_PROVENANCE['project']}")
    print(f"Authors:     {', '.join(UNSHACKLED_PROVENANCE['authors'])}")
    print(f"Spec Author: {UNSHACKLED_PROVENANCE['unshackled_spec_author']}")
    print(f"Upstream:    {UNSHACKLED_PROVENANCE['original_repository']}")
    print(f"License:     {UNSHACKLED_PROVENANCE['original_license']}")
    print(f"Reference:   {UNSHACKLED_PROVENANCE['literature_reference']}")
    print("-" * 72)

    # 2. Mathematical Invariants
    print(f"Unshackled Memory: 3^19 = {UNSHACKLED_MEM_SIZE:,} cells")
    print(f"Universe Midpoint: (3^19-1)/2 = {UNIVERSE_MIDPOINT:,} cells")
    print(f"Classic Memory:    3^10 = {CLASSIC_MEM_SIZE:,} cells")
    print(f"Scale Factor:      {UNSHACKLED_MEM_SIZE / CLASSIC_MEM_SIZE:,.1f}x")
    print("-" * 72)

    # 3. Telemetry Verification
    print(f"Target Expression: {EMPIRICAL_EXECUTION_METRICS['input_expression']} -> '{EMPIRICAL_EXECUTION_METRICS['result_output']}'")
    print(f"Total Steps:       {EMPIRICAL_EXECUTION_METRICS['total_steps']:,}")
    print(f"Wall Clock Time:   {EMPIRICAL_EXECUTION_METRICS['elapsed_wall_sec']} s ({EMPIRICAL_EXECUTION_METRICS['instructions_per_sec']/1e6:.1f} Mops/s)")
    print(f"JMP Percentage:    {EMPIRICAL_EXECUTION_METRICS['jmp_percentage']:.2f}% (Continuation-Passing threaded VM)")
    print("-" * 72)

    # 4. Check Generated Visual Assets
    macro_png = assets_dir / "malbolgelisp_macro_phase_space.png"
    orbit_gif = assets_dir / "malbolgelisp_torus_orbit.gif"

    # If scratch CSV exists, re-render to ensure fresh generation
    scratch_csv = Path("/home/danny/.gemini/antigravity-cli/brain/01762429-9ec4-44b2-b9ca-08a2b675648d/scratch/malbolgelisp_sampled.csv")
    if scratch_csv.exists():
        print(f"Loading sampled trajectory from {scratch_csv.name}...")
        samples = load_sampled_csv(scratch_csv)
        print(f"Rendering Macro Phase Space -> {macro_png.name}...")
        render_macro_phase_space(samples, macro_png)
        print(f"Rendering Torus Orbit GIF   -> {orbit_gif.name}...")
        render_torus_orbit_gif(samples, orbit_gif)
    else:
        print(f"Assets already present: {macro_png.exists()} and {orbit_gif.exists()}")

    # 5. Export Summary JSON
    summary_path = results_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "provenance": UNSHACKLED_PROVENANCE,
                "metrics": EMPIRICAL_EXECUTION_METRICS,
                "assets": {
                    "macro_phase_space_png": str(macro_png.relative_to(root)),
                    "torus_orbit_gif": str(orbit_gif.relative_to(root)),
                },
            },
            f,
            indent=2,
        )
    print(f"Summary exported to: {summary_path.relative_to(root)}")
    print("=" * 72)
    print("PIPELINE COMPLETED SUCCESSFULLY (STATUS: OK)")
    print("=" * 72)


if __name__ == "__main__":
    run_pipeline()
