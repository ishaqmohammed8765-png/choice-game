import math
from typing import Any, Dict, Iterable, List, Tuple

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


# ---------------------------------------------------------------------------
# Node classification helpers
# ---------------------------------------------------------------------------

def _node_type(node_id: str) -> str:
    """Classify a node id into a visual category."""
    if node_id == "death":
        return "death"
    if node_id.startswith("ending_"):
        return "ending"
    if node_id.startswith("failure_"):
        return "failure"
    return "normal"


# ---------------------------------------------------------------------------
# SVG element builders
# ---------------------------------------------------------------------------

_NODE_STYLES: Dict[str, Dict[str, str]] = {
    "normal":  {"fill": "#1e293b", "stroke": "#6b7280", "icon": ""},
    "ending":  {"fill": "#1a2e1a", "stroke": "#22c55e", "icon": "&#9733;"},  # star
    "death":   {"fill": "#2e1a1a", "stroke": "#ef4444", "icon": "&#9760;"},  # skull
    "failure": {"fill": "#2e2a1a", "stroke": "#eab308", "icon": "&#9888;"},  # warning
}


def _build_arrowhead_marker() -> str:
    """SVG <defs> block with arrow markers for path lines."""
    return """
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
                markerWidth="6" markerHeight="6" orient="auto-start-reverse"
                fill="#94a3b8">
            <path d="M 0 0 L 10 5 L 0 10 z"/>
        </marker>
        <marker id="arrow-visited" viewBox="0 0 10 10" refX="9" refY="5"
                markerWidth="6" markerHeight="6" orient="auto-start-reverse"
                fill="#38bdf8">
            <path d="M 0 0 L 10 5 L 0 10 z"/>
        </marker>
        <marker id="arrow-locked" viewBox="0 0 10 10" refX="9" refY="5"
                markerWidth="6" markerHeight="6" orient="auto-start-reverse"
                fill="#4a4a5a">
            <path d="M 0 0 L 10 5 L 0 10 z"/>
        </marker>
        <marker id="arrow-gold" viewBox="0 0 10 10" refX="9" refY="5"
                markerWidth="6" markerHeight="6" orient="auto-start-reverse"
                fill="#c9a54e">
            <path d="M 0 0 L 10 5 L 0 10 z"/>
        </marker>
    </defs>
    """


def _build_line(
    x1: float, y1: float, x2: float, y2: float,
    *,
    edge_visited: bool,
    is_locked: bool,
    is_secondary: bool = False,
    node_radius: float = 20,
) -> str:
    """Build an SVG line with an arrowhead, shortened to stop at the circle edge."""
    # Shorten the line so the arrow tip sits on the circle perimeter
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return ""
    ux, uy = dx / length, dy / length
    # Pull the endpoint back by the node radius
    x2_adj = x2 - ux * node_radius
    y2_adj = y2 - uy * node_radius

    classes = ["path-line"]
    if is_secondary:
        classes.append("secondary")
    if edge_visited:
        classes.append("visited")
    if is_locked:
        classes.append("locked")

    if is_locked:
        marker = "url(#arrow-locked)"
    elif edge_visited:
        marker = "url(#arrow-visited)"
    else:
        marker = "url(#arrow)"

    return (
        f'<line class="{" ".join(classes)}" '
        f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2_adj:.1f}" y2="{y2_adj:.1f}" '
        f'marker-end="{marker}"></line>'
    )


def _build_node_group(
    x: float, y: float,
    *,
    label_lines: List[str],
    tooltip_text: str,
    is_locked: bool,
    is_visited: bool,
    node_type: str = "normal",
    radius: float = 20,
    label_class: str = "choice-label",
) -> str:
    """Build an SVG <g> element for a choice node with typed styling."""
    style = _NODE_STYLES.get(node_type, _NODE_STYLES["normal"])

    group_classes = ["choice-node"]
    if is_locked:
        group_classes.append("locked")
    if is_visited:
        group_classes.append("visited")
    if node_type != "normal":
        group_classes.append(f"node-{node_type}")

    tooltip = f"<title>{_escape_svg_text(tooltip_text)}</title>" if tooltip_text else ""

    # Node circle with type-specific styling
    fill = style["fill"]
    stroke = style["stroke"]
    if is_visited and node_type == "normal":
        fill = "#0f172a"
        stroke = "#38bdf8"
    elif not is_locked and node_type == "normal":
        stroke = "#c9a54e"  # gold border for available choices

    circle = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"></circle>'

    # Type icon inside the circle
    icon_svg = ""
    if style["icon"]:
        icon_svg = (
            f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" '
            f'fill="{stroke}" font-size="{radius * 0.8:.0f}px">{style["icon"]}</text>'
        )

    label_y = y + radius + 16
    label_svg = _render_svg_text(label_lines, x=x, y=label_y, class_name=label_class)

    return f"""
        <g class="{' '.join(group_classes)}">
            {tooltip}
            {circle}
            {icon_svg}
            {label_svg}
        </g>
    """


def _tooltip_for_choice(
    choice: Dict[str, Any],
    next_node: str,
    is_locked: bool,
) -> str:
    """Build tooltip text for a choice node, including destination info."""
    next_node_data = STORY_NODES.get(next_node, {})
    dest_title = next_node_data.get("title", next_node)
    parts: List[str] = [f"Destination: {dest_title}"]

    if is_locked:
        req_text = format_requirement_tooltip(
            choice.get("requirements"),
            stats=st.session_state.stats,
            inventory=st.session_state.inventory,
            flags=st.session_state.flags,
            player_class=st.session_state.player_class,
        )
        parts.append(f"Locked: {req_text}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# SVG style block
# ---------------------------------------------------------------------------

def _svg_styles() -> str:
    return """
    <style>
        .path-line {
            stroke: #94a3b8;
            stroke-width: 2;
        }
        .path-line.locked {
            stroke: #4a4a5a;
            stroke-dasharray: 5 3;
            stroke-width: 1.5;
        }
        .path-line.visited {
            stroke: #38bdf8;
        }
        .path-line.secondary {
            stroke-width: 1.4;
            opacity: 0.6;
        }

        .choice-node.locked {
            opacity: 0.35;
        }

        .choice-label {
            fill: #d4d4dc;
            font-size: 10px;
            font-family: 'Crimson Text', Georgia, serif;
        }
        .secondary-label {
            font-size: 9px;
            opacity: 0.8;
        }

        .center-node circle {
            fill: #0f172a;
            stroke: #facc15;
            stroke-width: 3;
            filter: drop-shadow(0 0 6px rgba(250, 204, 21, 0.3));
        }
        .center-label {
            fill: #facc15;
            font-size: 11px;
            font-weight: 600;
            font-family: 'Cinzel', serif;
        }

        .node-ending circle {
            filter: drop-shadow(0 0 4px rgba(34, 197, 94, 0.3));
        }
        .node-death circle {
            filter: drop-shadow(0 0 4px rgba(239, 68, 68, 0.3));
        }
        .node-failure circle {
            filter: drop-shadow(0 0 4px rgba(234, 179, 8, 0.3));
        }

        .legend-text {
            fill: #9ca3af;
            font-size: 9px;
            font-family: 'Crimson Text', Georgia, serif;
        }
    </style>
    """


# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------

def _build_legend(x: float, y: float) -> str:
    """Build a compact legend in the bottom-left corner of the SVG."""
    items = [
        ("#c9a54e", "solid", "Available"),
        ("#38bdf8", "solid", "Visited"),
        ("#4a4a5a", "dashed", "Locked"),
    ]
    type_items = [
        ("#22c55e", "&#9733;", "Ending"),
        ("#ef4444", "&#9760;", "Death"),
        ("#eab308", "&#9888;", "Setback"),
    ]

    parts: List[str] = []
    row_y = y
    for color, style, label in items:
        dash = ' stroke-dasharray="5 3"' if style == "dashed" else ""
        parts.append(
            f'<line x1="{x}" y1="{row_y}" x2="{x + 18}" y2="{row_y}" '
            f'stroke="{color}" stroke-width="2"{dash}></line>'
            f'<text x="{x + 22}" y="{row_y + 3}" class="legend-text">{label}</text>'
        )
        row_y += 14

    row_y += 2
    for color, icon, label in type_items:
        parts.append(
            f'<text x="{x + 4}" y="{row_y + 4}" fill="{color}" font-size="11px">{icon}</text>'
            f'<text x="{x + 22}" y="{row_y + 3}" class="legend-text">{label}</text>'
        )
        row_y += 14

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

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
    show_two_hop = st.toggle(
        "Show 2-hop view",
        value=False,
        key="show_two_hop_map",
        help="Include the next layer of choices to preview upcoming paths.",
    )
    if not choices:
        st.info("This node has no outgoing choices.")
        return

    visited_nodes = set(st.session_state.visited_nodes)
    visited_edges = {(edge.get("from"), edge.get("to")) for edge in st.session_state.visited_edges}

    count = len(choices)
    # Scale the canvas and radius based on choice count to avoid overlap
    base_size = 520
    if count > 8:
        scale = 1.0 + (count - 8) * 0.08
    else:
        scale = 1.0
    width = int(base_size * scale)
    height = int(base_size * scale)
    center_x = width / 2
    center_y = height / 2
    radius = min(width, height) * 0.30

    line_elements: List[str] = []
    node_elements: List[str] = []
    first_hop_positions: List[Tuple[float, float, float, Dict[str, Any], str]] = []

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
        ntype = _node_type(next_node)

        tooltip_text = _tooltip_for_choice(choice, next_node, is_locked)
        label_lines = _wrap_svg_label(choice["label"])

        line_elements.append(
            _build_line(
                center_x, center_y, x, y,
                edge_visited=edge_visited,
                is_locked=is_locked,
                node_radius=20,
            )
        )
        node_elements.append(
            _build_node_group(
                x, y,
                label_lines=label_lines,
                tooltip_text=tooltip_text,
                is_locked=is_locked,
                is_visited=node_visited,
                node_type=ntype,
                radius=20,
            )
        )
        first_hop_positions.append((x, y, angle, choice, next_node))

    # Center node
    center_lines = _wrap_svg_label(node.get("title", node_id), max_chars=16)
    center_label = _render_svg_text(center_lines, x=center_x, y=center_y + 5, class_name="center-label")
    center_tooltip = f"<title>{_escape_svg_text(node_id)}</title>"

    # Two-hop secondary nodes
    if show_two_hop:
        secondary_radius = radius * 1.75
        for x, y, angle, choice, next_node in first_hop_positions:
            next_node_data = STORY_NODES.get(next_node, {})
            secondary_choices = next_node_data.get("choices", [])
            if not secondary_choices:
                continue
            spread = 0.6
            count_secondary = len(secondary_choices)
            for idx, secondary_choice in enumerate(secondary_choices):
                if count_secondary == 1:
                    offset = 0.0
                else:
                    offset = (idx - (count_secondary - 1) / 2) * (spread / (count_secondary - 1))
                angle_secondary = angle + offset
                x2 = center_x + secondary_radius * math.cos(angle_secondary)
                y2 = center_y + secondary_radius * math.sin(angle_secondary)

                is_unlocked, _ = check_requirements(secondary_choice.get("requirements"))
                is_locked = not is_unlocked
                _, next_next_node = resolve_choice_outcome(secondary_choice)
                edge_key = (next_node, next_next_node)
                edge_visited = edge_key in visited_edges
                node_visited = next_next_node in visited_nodes
                ntype = _node_type(next_next_node)

                tooltip_text = _tooltip_for_choice(secondary_choice, next_next_node, is_locked)
                label_lines = _wrap_svg_label(secondary_choice["label"])

                line_elements.append(
                    _build_line(
                        x, y, x2, y2,
                        edge_visited=edge_visited,
                        is_locked=is_locked,
                        is_secondary=True,
                        node_radius=16,
                    )
                )
                node_elements.append(
                    _build_node_group(
                        x2, y2,
                        label_lines=label_lines,
                        tooltip_text=tooltip_text,
                        is_locked=is_locked,
                        is_visited=node_visited,
                        node_type=ntype,
                        radius=16,
                        label_class="choice-label secondary-label",
                    )
                )

    # Determine if we need special node types in legend
    has_special = any(
        _node_type(resolve_choice_outcome(c)[1]) != "normal"
        for c in choices
    )
    legend_height = 90 if has_special else 50
    legend_svg = _build_legend(8, height - legend_height)

    svg = f"""
        <svg viewBox="0 0 {width} {height}" width="100%" height="{height}px"
             style="max-width:{width}px; display:block; margin:0 auto;
                    background: radial-gradient(ellipse at center, rgba(15,15,26,0.8) 0%, rgba(5,5,16,0.95) 100%);
                    border: 1px solid #2a2015; border-radius: 8px;">
            {_svg_styles()}
            {_build_arrowhead_marker()}

            <!-- Lines drawn first (behind nodes) -->
            {''.join(line_elements)}

            <!-- Center node -->
            <g class="center-node">
                {center_tooltip}
                <circle cx="{center_x}" cy="{center_y}" r="32"></circle>
                {center_label}
            </g>

            <!-- Choice nodes drawn on top -->
            {''.join(node_elements)}

            <!-- Legend -->
            {legend_svg}
        </svg>
    """

    st.markdown(svg, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    tspan_lines = "".join(
        f'<tspan x="{x:.1f}" y="{start_y + index * line_height:.1f}">{_escape_svg_text(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    return f'<text text-anchor="middle" class="{class_name}">{tspan_lines}</text>'


def _escape_svg_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
