"""Composable UI building blocks for the Streamlit app."""

from .debug_outcomes import format_outcomes, format_requirements, render_choice_outcomes_tab
from .epilogue import get_epilogue_aftermath_lines
from .log_view import render_log
from .node_view import render_node, should_force_injury_redirect
from .sidebar import render_sidebar

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
