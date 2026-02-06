"""Backward-compatible UI API composed from smaller UI components."""

from game.ui_components import (
    format_outcomes,
    format_requirements,
    get_epilogue_aftermath_lines,
    render_choice_outcomes_tab,
    render_log,
    render_node,
    render_sidebar,
    should_force_injury_redirect,
)

__all__ = [
    "format_outcomes",
    "format_requirements",
    "get_epilogue_aftermath_lines",
    "render_choice_outcomes_tab",
    "render_log",
    "render_node",
    "render_sidebar",
    "should_force_injury_redirect",
]
