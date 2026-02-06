import math
from typing import Any, Dict, Iterable, List

from game.streamlit_compat import st

from game.data import STORY_NODES
from game.logic import check_requirements, resolve_choice_outcome


def format_requirement_tooltip(
    requirements: Dict[str, Any] | None,
    *,
    stats: Dict[str, int],
    inventory: Iterable[str],
    flags: Dict[str, Any],
    player_class: str | None,
) -> str:
    """Format requirement details with current player values for hover tooltips."""
    if not requirements:
        return "No requirements."

    lines: List[str] = []
    if "any_of" in requirements:
        lines.append("Any of:")
        for option in requirements["any_of"]:
            option_lines = _format_requirement_lines(
                option,
                stats=stats,
                inventory=inventory,
                flags=flags,
                player_class=player_class,
            )
            option_text = "; ".join(option_lines) if option_lines else "None"
            lines.append(f"- {option_text}")
    else:
        lines.extend(
            _format_requirement_lines(
                requirements,
                stats=stats,
                inventory=inventory,
                flags=flags,
                player_class=player_class,
            )
        )

    return "\n".join(lines) if lines else "No requirements."


def render_path_map() -> None:
    """Render a spider-style map of the current node and outgoing choices."""
    node_id = st.session_state.current_node
    node = STORY_NODES.get(node_id)
    if not node:
        st.error("Path map unavailable: missing current node.")
        return

    choices = node.get("choices", [])
    st.subheader("Path Map")
    st.caption("Current node centered with available and locked choices branching outward.")
    if not choices:
        st.info("This node has no outgoing choices.")
        return

    visited_nodes = set(st.session_state.visited_nodes)
    visited_edges = {(edge.get("from"), edge.get("to")) for edge in st.session_state.visited_edges}

    width = 520
    height = 520
    center_x = width / 2
    center_y = height / 2
    radius = min(width, height) * 0.32

    elements: List[str] = []
    count = len(choices)
    for idx, choice in enumerate(choices):
        angle = (2 * math.pi * idx) / count - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        is_unlocked, _ = check_requirements(choice.get("requirements"))
        is_locked = not is_unlocked
        _, next_node = resolve_choice_outcome(choice)
        edge_key = (node_id, next_node)
        edge_visited = edge_key in visited_edges
        node_visited = next_node in visited_nodes

        tooltip = ""
        if is_locked:
            tooltip_text = format_requirement_tooltip(
                choice.get("requirements"),
                stats=st.session_state.stats,
                inventory=st.session_state.inventory,
                flags=st.session_state.flags,
                player_class=st.session_state.player_class,
            )
            tooltip = f"<title>{_escape_tooltip(tooltip_text)}</title>"

        label_lines = _wrap_svg_label(choice["label"])
        label_y = y + 36
        label_svg = _render_svg_text(
            label_lines,
            x=x,
            y=label_y,
            class_name="choice-label",
        )

        group_classes = ["choice-node"]
        if is_locked:
            group_classes.append("locked")
        if node_visited:
            group_classes.append("visited")

        line_class = "path-line"
        if edge_visited:
            line_class += " visited"
        if is_locked:
            line_class += " locked"

        elements.append(
            f"""
            <line class="{line_class}" x1="{center_x}" y1="{center_y}" x2="{x}" y2="{y}"></line>
            <g class="{' '.join(group_classes)}">
                {tooltip}
                <circle cx="{x}" cy="{y}" r="20"></circle>
                {label_svg}
            </g>
            """
        )

    center_lines = _wrap_svg_label(node.get("title", node_id), max_chars=16)
    center_label = _render_svg_text(center_lines, x=center_x, y=center_y + 6, class_name="center-label")
    center_tooltip = f"<title>{_escape_tooltip(node_id)}</title>"

    svg = f"""
        <svg viewBox="0 0 {width} {height}" width="100%" height="{height}px" style="max-width:{width}px; display:block; margin:0 auto;">
            <style>
                .path-line {{
                    stroke: #94a3b8;
                    stroke-width: 2;
                }}
                .path-line.locked {{
                    stroke: #64748b;
                    stroke-dasharray: 4 4;
                }}
                .path-line.visited {{
                    stroke: #38bdf8;
                }}
                .choice-node circle {{
                    fill: #1e293b;
                    stroke: #cbd5f5;
                    stroke-width: 2;
                }}
                .choice-node.visited circle {{
                    stroke: #38bdf8;
                    fill: #0f172a;
                }}
                .choice-node.locked {{
                    opacity: 0.4;
                }}
                .choice-label {{
                    fill: #e2e8f0;
                    font-size: 11px;
                }}
                .center-node circle {{
                    fill: #0f172a;
                    stroke: #facc15;
                    stroke-width: 3;
                }}
                .center-label {{
                    fill: #f8fafc;
                    font-size: 12px;
                    font-weight: 600;
                }}
            </style>
            <g class="center-node">
                {center_tooltip}
                <circle cx="{center_x}" cy="{center_y}" r="32"></circle>
                {center_label}
            </g>
            {''.join(elements)}
        </svg>
    """

    st.markdown(svg, unsafe_allow_html=True)


def _format_requirement_lines(
    requirements: Dict[str, Any],
    *,
    stats: Dict[str, int],
    inventory: Iterable[str],
    flags: Dict[str, Any],
    player_class: str | None,
) -> List[str]:
    lines: List[str] = []
    if "class" in requirements:
        required = ", ".join(requirements["class"])
        current = player_class or "Unknown"
        lines.append(f"Class: {required} (you: {current})")
    if "min_hp" in requirements:
        lines.append(f"HP >= {requirements['min_hp']} (you: {stats['hp']})")
    if "min_gold" in requirements:
        lines.append(f"Gold >= {requirements['min_gold']} (you: {stats['gold']})")
    if "min_strength" in requirements:
        lines.append(f"Strength >= {requirements['min_strength']} (you: {stats['strength']})")
    if "min_dexterity" in requirements:
        lines.append(f"Dexterity >= {requirements['min_dexterity']} (you: {stats['dexterity']})")
    for item in requirements.get("items", []):
        status = "have" if item in inventory else "missing"
        lines.append(f"Needs item: {item} (you: {status})")
    for item in requirements.get("missing_items", []):
        status = "have" if item in inventory else "not owned"
        lines.append(f"Must not have: {item} (you: {status})")
    for flag in requirements.get("flag_true", []):
        lines.append(f"Flag {flag}=True (you: {flags.get(flag, False)})")
    for flag in requirements.get("flag_false", []):
        lines.append(f"Flag {flag}=False (you: {flags.get(flag, False)})")
    return lines


def _wrap_svg_label(text: str, max_chars: int = 14) -> List[str]:
    words = text.split()
    if not words:
        return [text]

    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _render_svg_text(lines: List[str], *, x: float, y: float, class_name: str) -> str:
    if not lines:
        return ""
    line_height = 13
    start_y = y - (len(lines) - 1) * line_height / 2
    tspan_lines = "\n".join(
        f'<tspan x="{x}" y="{start_y + index * line_height}">{_escape_tooltip(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    return f'<text text-anchor="middle" class="{class_name}">{tspan_lines}</text>'


def _escape_tooltip(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
