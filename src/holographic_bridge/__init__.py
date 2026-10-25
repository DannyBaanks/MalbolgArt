"""Holographic Bridge: Integration of HOLOGRAPHIC 4D Torus Geometry into MalbolgArt.
"""

from .torus_embed import (
    embed_cell,
    embed_cell_disambiguated,
    rotate4,
    project_stereo,
    rotate_project,
    verify_embedding_properties,
)
from .sheets import (
    sheet_of,
    sheet_id,
    analyze_two_sheets,
    render_sheets_overlay,
    render_sheets_separated,
)
from .legacy_import import (
    find_holographic_sources,
    load_legacy_json_inventory,
    import_lutter_trace,
    import_lutter_outs,
)
from .animation import (
    render_lutter_4d_gif,
    render_lutter_two_sheets_gif,
    render_lutter_trace_chronological_gif,
    render_malbolgart_vs_holographic_gif,
    render_flow_torus_simulation_gif,
)
from .trace_alignment import (
    align_verified_trace_to_4d,
    analyze_sheet_dynamics,
)

__all__ = [
    "embed_cell",
    "embed_cell_disambiguated",
    "rotate4",
    "project_stereo",
    "rotate_project",
    "verify_embedding_properties",
    "sheet_of",
    "sheet_id",
    "analyze_two_sheets",
    "render_sheets_overlay",
    "render_sheets_separated",
    "find_holographic_sources",
    "load_legacy_json_inventory",
    "import_lutter_trace",
    "import_lutter_outs",
    "render_lutter_4d_gif",
    "render_lutter_two_sheets_gif",
    "render_lutter_trace_chronological_gif",
    "render_malbolgart_vs_holographic_gif",
    "render_flow_torus_simulation_gif",
    "align_verified_trace_to_4d",
    "analyze_sheet_dynamics",
]
