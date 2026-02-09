from typing import Any, Dict, Iterable, List

from game.streamlit_compat import st

from game.data import STORY_NODES
from game.engine.state_machine import get_phase
from game.logic import check_requirements, get_node_choice_evaluations, resolve_choice_outcome


# Stat requirement specs for tooltip formatting: (requirement_key, stat_key, label)
_TOOLTIP_STAT_SPECS: List[tuple[str, str, str]] = [
    ("min_hp", "hp", "HP"),
    ("min_gold", "gold", "Gold"),
    ("min_strength", "strength", "Strength"),
    ("min_dexterity", "dexterity", "Dexterity"),
]

_PHASE_FILL_COLORS: Dict[str, str] = {
    "intro": "#94a3b8",
    "exploration": "#22c55e",
    "combat": "#ef4444",
    "council": "#facc15",
    "finale": "#f97316",
    "ending": "#38bdf8",
    "failure": "#8b5cf6",
}

_STATUS_SPRITES: Dict[str, List[tuple[int, int]]] = {
    "available": [
        (1, 0), (2, 0), (3, 0),
        (0, 1), (4, 1),
        (0, 2), (2, 2), (4, 2),
        (0, 3), (4, 3),
        (1, 4), (2, 4), (3, 4),
    ],
    "visited": [
        (0, 2), (1, 3), (2, 4), (3, 3), (4, 2),
        (2, 1),
    ],
    "locked": [
        (1, 0), (2, 0), (3, 0),
        (1, 1), (3, 1),
        (1, 2), (2, 2), (3, 2),
        (1, 3), (3, 3),
        (1, 4), (2, 4), (3, 4),
    ],
}


def _status_sprite_svg(
    x: float,
    y: float,
    status: str,
    *,
    secondary: bool = False,
) -> str:
    pixels = _STATUS_SPRITES.get(status, [])
    if not pixels:
        return ""
    size = 1.4 if secondary else 1.9
    offset = size * 2.5
    pixel_rects = "".join(
        f'<rect x="{x - offset + px * size:.2f}" y="{y - offset + py * size:.2f}" '
        f'width="{size:.2f}" height="{size:.2f}" rx="0.2" ry="0.2"/>'
        for px, py in pixels
    )
    sec_class = " secondary" if secondary else ""
    return f'<g class="status-sprite {status}{sec_class}">{pixel_rects}</g>'


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


def _build_choice_node_svg(
    choice: Dict[str, Any],
    *,
    x: float,
    y: float,
    origin_x: float,
    origin_y: float,
    origin_node_id: str,
    visited_nodes: set,
    visited_edges: set,
    node_radius: int,
    label_offset: int,
    label_class: str,
    extra_group_classes: List[str] | None = None,
    extra_line_classes: List[str] | None = None,
    icon_y_offset: int = 5,
    show_available_icon: bool = True,
) -> tuple[str, str, str]:
    """Build SVG elements for a single choice node and its connecting line.

    Returns (line_svg, node_group_svg, next_node_id).
    """
    is_unlocked, _ = check_requirements(choice.get("requirements"))
    is_locked = not is_unlocked
    _, next_node = resolve_choice_outcome(choice)
    edge_key = (origin_node_id, next_node)
    edge_visited = edge_key in visited_edges
    node_visited = next_node in visited_nodes

    # Tooltip for locked nodes - escape all content for SVG safety
    tooltip = ""
    if is_locked:
        tooltip_text = format_requirement_tooltip(
            choice.get("requirements"),
            stats=st.session_state.stats,
            inventory=st.session_state.inventory,
            flags=st.session_state.flags,
            player_class=st.session_state.player_class,
        )
        tooltip = f"<title>{_escape_svg_text(tooltip_text)}</title>"

    # Label - escape choice label text
    label_lines = _wrap_svg_label(_escape_svg_text(choice["label"]))
    label_svg = _render_svg_text_raw(
        label_lines, x=x, y=y + label_offset, class_name=label_class,
    )

    # Group CSS classes
    group_classes = ["choice-node"] + (extra_group_classes or [])
    if is_locked:
        group_classes.append("locked")
    elif not node_visited:
        group_classes.append("available")
    if node_visited:
        group_classes.append("visited")

    # Line CSS classes
    line_class_parts = ["path-line"] + (extra_line_classes or [])
    if edge_visited:
        line_class_parts.append("visited")
    if is_locked:
        line_class_parts.append("locked")
    elif not edge_visited and "secondary" not in (extra_line_classes or []):
        line_class_parts.append("available")

    # Status sprite marker
    icon_svg = ""
    is_secondary = bool(extra_group_classes and "secondary-node" in extra_group_classes)
    if is_locked:
        icon_svg = _status_sprite_svg(x, y + icon_y_offset, "locked", secondary=is_secondary)
    elif node_visited:
        icon_svg = _status_sprite_svg(x, y + icon_y_offset, "visited", secondary=is_secondary)
    elif show_available_icon:
        icon_svg = _status_sprite_svg(x, y + icon_y_offset, "available", secondary=is_secondary)

    # Determine destination phase for coloring the node border
    dest_phase = get_phase(next_node)
    phase_color = _PHASE_FILL_COLORS.get(dest_phase, "#64748b")

    # Add phase indicator ring for available nodes
    phase_ring = ""
    if not is_locked and not node_visited:
        phase_ring = (
            f'<circle cx="{x}" cy="{y}" r="{node_radius + 4}" '
            f'fill="none" stroke="{phase_color}" stroke-opacity="0.2" stroke-width="1"/>'
        )

    line_svg = (
        f'<line class="{" ".join(line_class_parts)}" '
        f'x1="{origin_x}" y1="{origin_y}" x2="{x}" y2="{y}"/>'
    )
    node_svg = (
        f'<g class="{" ".join(group_classes)}">'
        f'{tooltip}'
        f'{phase_ring}'
        f'<circle cx="{x}" cy="{y}" r="{node_radius}"/>'
        f'{icon_svg}'
        f'{label_svg}'
        f'</g>'
    )

    return line_svg, node_svg, next_node


def render_path_map() -> None:
    """Render a compact tactical map with readable destination cards."""
    node_id = st.session_state.current_node
    node = STORY_NODES.get(node_id)
    if not node:
        st.error("Path map unavailable: missing current node.")
        return

    choices = node.get("choices", [])
    phase = get_phase(node_id)
    phase_color = _PHASE_FILL_COLORS.get(phase, "#94a3b8")

    st.markdown(
        f"""
        <div style="
            padding: 0.55rem 0.8rem;
            border: 1px solid #1e293b;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(20,15,10,0.55), rgba(10,10,20,0.5));
            margin-bottom: 0.5rem;
        ">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
                <div>
                    <div style="font-family:'Cinzel',serif;color:#facc15;font-size:0.95rem;letter-spacing:0.05em;">
                        Tactical Path Map
                    </div>
                    <div style="font-family:'Crimson Text',serif;color:#94a3b8;font-size:0.82rem;">
                        Current scene: {_escape_svg_text(node.get("title", node_id))}
                    </div>
                </div>
                <span style="
                    border:1px solid {phase_color}65;
                    background:{phase_color}18;
                    color:{phase_color};
                    border-radius:999px;
                    padding:2px 10px;
                    font-family:'Cinzel',serif;
                    font-size:0.66rem;
                    letter-spacing:0.04em;
                    text-transform:uppercase;
                ">{phase}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not choices:
        st.info("No outgoing paths from this scene.")
        return

    evaluations = get_node_choice_evaluations(node_id, node)
    visited_nodes = set(st.session_state.visited_nodes)
    visited_edges = {(edge.get("from"), edge.get("to")) for edge in st.session_state.visited_edges}

    columns_per_row = 3 if len(evaluations) >= 6 else 2
    choice_columns = st.columns(columns_per_row)
    for index, entry in enumerate(evaluations):
        choice = entry["choice"]
        is_unlocked = entry["is_available"]
        locked_reason = entry["locked_reason"]
        next_node_id = entry["resolved_next"]
        destination = STORY_NODES.get(next_node_id, {}).get("title", next_node_id or "Unknown")
        is_visited = next_node_id in visited_nodes
        edge_visited = (node_id, next_node_id) in visited_edges

        status_text = "AVAILABLE"
        status_color = "#22c55e"
        if not is_unlocked:
            status_text = "LOCKED"
            status_color = "#94a3b8"
        elif edge_visited or is_visited:
            status_text = "VISITED"
            status_color = "#38bdf8"

        connector = "->"
        card_html = f"""
        <div style="
            height: 100%;
            min-height: 126px;
            padding: 0.55rem 0.65rem;
            border: 1px solid #1e293b;
            border-left: 3px solid {status_color}90;
            border-radius: 8px;
            background: rgba(8, 11, 20, 0.72);
        ">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="font-family:'Cinzel',serif;color:#e8d5b0;font-size:0.78rem;">Path {index + 1}</span>
                <span style="
                    border:1px solid {status_color}66;
                    color:{status_color};
                    background:{status_color}16;
                    border-radius:999px;
                    padding:1px 8px;
                    font-size:0.62rem;
                    font-family:'Cinzel',serif;
                    letter-spacing:0.05em;
                ">{status_text}</span>
            </div>
            <div style="color:#d4d4dc;font-size:0.9rem;line-height:1.35;margin-bottom:4px;">
                {_escape_svg_text(choice.get("label", "Unknown choice"))}
            </div>
            <div style="font-size:0.8rem;color:#94a3b8;">
                {_escape_svg_text(node.get("title", node_id))} {connector} {_escape_svg_text(destination)}
            </div>
            {f'<div style="margin-top:4px;color:#fda4af;font-size:0.76rem;">Req: {_escape_svg_text(locked_reason)}</div>' if not is_unlocked and locked_reason else ''}
        </div>
        """
        with choice_columns[index % columns_per_row]:
            st.markdown(card_html, unsafe_allow_html=True)


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
    for req_key, stat_key, label in _TOOLTIP_STAT_SPECS:
        if req_key in requirements:
            lines.append(f"{label} >= {requirements[req_key]} (you: {stats[stat_key]})")
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


def _render_svg_text_raw(lines: List[str], *, x: float, y: float, class_name: str) -> str:
    """Render pre-escaped text lines into SVG tspan elements."""
    if not lines:
        return ""
    line_height = 13
    start_y = y - (len(lines) - 1) * line_height / 2
    tspan_lines = "".join(
        f'<tspan x="{x}" y="{start_y + index * line_height}">{line}</tspan>'
        for index, line in enumerate(lines)
    )
    return f'<text text-anchor="middle" class="{class_name}">{tspan_lines}</text>'


def _escape_svg_text(text: str) -> str:
    """Escape text for safe embedding in SVG elements."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
