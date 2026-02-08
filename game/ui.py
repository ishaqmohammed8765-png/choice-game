"""Backward-compatible UI API composed from smaller UI components."""

from game.ui_components import (
    format_requirement_tooltip,
    get_epilogue_aftermath_lines,
    render_log,
    render_main_panel,
    render_node,
    render_path_map,
    render_sidebar,
    should_force_injury_redirect,
)

__all__ = [
    "format_requirement_tooltip",
    "get_epilogue_aftermath_lines",
    "render_log",
    "render_main_panel",
    "render_node",
    "render_path_map",
    "render_sidebar",
    "should_force_injury_redirect",
]
