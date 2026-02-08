import math
from typing import Any, Dict, Iterable, List

from game.streamlit_compat import st

from game.data import STORY_NODES
from game.engine.state_machine import get_phase
from game.logic import check_requirements, resolve_choice_outcome


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
    """Render an upgraded fantasy-themed path map of the current node and outgoing choices."""
    node_id = st.session_state.current_node
    node = STORY_NODES.get(node_id)
    if not node:
        st.error("Path map unavailable: missing current node.")
        return

    choices = node.get("choices", [])

    # Header
    current_phase = get_phase(node_id)
    phase_color = _PHASE_FILL_COLORS.get(current_phase, "#c9a54e")
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.2rem;">
            <h3 style="font-family:'Cinzel',serif;color:#c9a54e !important;letter-spacing:0.05em;margin:0;">
                Path Map
            </h3>
            <span style="
                display:inline-block;padding:1px 8px;border:1px solid {phase_color}60;
                border-radius:10px;background:{phase_color}15;
                font-family:'Cinzel',serif;font-size:0.65rem;color:{phase_color};
                letter-spacing:0.05em;text-transform:uppercase;
            ">{current_phase}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Current node centered \u2022 Available paths glow \u2022 "
        "Locked paths are dimmed \u2022 Visited paths highlighted"
    )
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
    visited_edges = {
        (edge.get("from"), edge.get("to")) for edge in st.session_state.visited_edges
    }

    # Adaptive sizing based on number of choices
    count = len(choices)
    base_size = 580
    if show_two_hop:
        # Need more room for secondary nodes
        width = max(base_size, min(800, base_size + count * 20))
        height = width
    else:
        width = base_size
        height = base_size

    center_x = width / 2
    center_y = height / 2
    radius = min(width, height) * 0.28

    # Increase radius for many choices to prevent overlap
    if count > 6:
        radius = min(width, height) * 0.32

    # -- Collect all rendering layers --
    line_elements: List[str] = []
    node_elements: List[str] = []
    first_hop_positions: List[tuple[float, float, float, str]] = []

    for idx, choice in enumerate(choices):
        angle = (2 * math.pi * idx) / count - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        line_svg, node_svg, next_node = _build_choice_node_svg(
            choice,
            x=x, y=y,
            origin_x=center_x, origin_y=center_y,
            origin_node_id=node_id,
            visited_nodes=visited_nodes,
            visited_edges=visited_edges,
            node_radius=22,
            label_offset=38,
            label_class="choice-label",
        )
        line_elements.append(line_svg)
        node_elements.append(node_svg)
        first_hop_positions.append((x, y, angle, next_node))

    # -- 2-hop secondary nodes --
    secondary_line_elements: List[str] = []
    secondary_node_elements: List[str] = []
    if show_two_hop:
        secondary_radius = radius * 1.75
        for x, y, angle, next_node in first_hop_positions:
            next_node_data = STORY_NODES.get(next_node, {})
            secondary_choices = next_node_data.get("choices", [])
            if not secondary_choices:
                continue
            # Limit secondary nodes to prevent clutter
            max_secondary = 4
            secondary_choices = secondary_choices[:max_secondary]
            spread = 0.5
            count_secondary = len(secondary_choices)
            for idx, secondary_choice in enumerate(secondary_choices):
                if count_secondary == 1:
                    offset = 0
                else:
                    offset = (idx - (count_secondary - 1) / 2) * (
                        spread / max(count_secondary - 1, 1)
                    )
                angle_secondary = angle + offset
                x2 = center_x + secondary_radius * math.cos(angle_secondary)
                y2 = center_y + secondary_radius * math.sin(angle_secondary)

                line_svg, node_svg, _ = _build_choice_node_svg(
                    secondary_choice,
                    x=x2, y=y2,
                    origin_x=x, origin_y=y,
                    origin_node_id=next_node,
                    visited_nodes=visited_nodes,
                    visited_edges=visited_edges,
                    node_radius=14,
                    label_offset=28,
                    label_class="choice-label secondary-label",
                    extra_group_classes=["secondary-node"],
                    extra_line_classes=["secondary"],
                    icon_y_offset=4,
                    show_available_icon=False,
                )
                secondary_line_elements.append(line_svg)
                secondary_node_elements.append(node_svg)

    # -- Center node --
    center_lines = _wrap_svg_label(_escape_svg_text(node.get("title", node_id)), max_chars=14)
    center_label = _render_svg_text_raw(
        center_lines, x=center_x, y=center_y + 5, class_name="center-label"
    )
    center_tooltip = f"<title>{_escape_svg_text(node_id)}</title>"

    # -- SVG CSS styles --
    svg_style = """
        /* --- Path lines --- */
        .path-line {
            stroke: #475569;
            stroke-width: 2;
            stroke-linecap: round;
        }
        .path-line.available {
            stroke: url(#lineGradient);
            stroke-width: 2.5;
            filter: url(#softGlow);
        }
        .path-line.locked {
            stroke: #334155;
            stroke-width: 1.5;
            stroke-dasharray: 5 4;
            opacity: 0.5;
        }
        .path-line.visited {
            stroke: #38bdf8;
            stroke-width: 2;
            opacity: 0.85;
        }
        .path-line.secondary {
            stroke-width: 1.2;
            opacity: 0.5;
        }
        .path-line.secondary.visited {
            stroke: #38bdf8;
            opacity: 0.6;
        }

        /* --- Choice nodes --- */
        .choice-node circle {
            fill: url(#nodeFill);
            stroke: #64748b;
            stroke-width: 2;
            transition: all 0.2s ease;
        }
        .choice-node.available circle {
            stroke: #c9a54e;
            stroke-width: 2.5;
            filter: url(#nodeGlow);
        }
        .choice-node.visited circle {
            stroke: #38bdf8;
            fill: url(#visitedFill);
        }
        .choice-node.locked {
            opacity: 0.35;
        }
        .choice-node.locked circle {
            stroke: #475569;
            stroke-dasharray: 3 3;
            fill: #0f172a;
        }

        /* --- Choice labels --- */
        .choice-label {
            fill: #cbd5e1;
            font-size: 11px;
            font-family: 'Crimson Text', Georgia, serif;
        }
        .secondary-label {
            font-size: 9px;
            fill: #94a3b8;
        }
        .choice-node.available .choice-label {
            fill: #fef3c7;
        }
        .choice-node.locked .choice-label {
            fill: #64748b;
        }
        .choice-node.visited .choice-label {
            fill: #7dd3fc;
        }

        /* --- Pixel sprite markers --- */
        .status-sprite {
            pointer-events: none;
        }
        .status-sprite.available rect {
            fill: #facc15;
            stroke: #fef3c7;
            stroke-width: 0.25;
        }
        .status-sprite.visited rect {
            fill: #38bdf8;
            stroke: #bae6fd;
            stroke-width: 0.25;
        }
        .status-sprite.locked rect {
            fill: #94a3b8;
            opacity: 0.8;
        }
        .status-sprite.secondary rect {
            opacity: 0.85;
        }

        /* --- Secondary nodes --- */
        .secondary-node circle {
            stroke-width: 1.5;
            fill: url(#secondaryFill);
        }
        .secondary-node.available circle {
            stroke: #c9a54e;
            stroke-width: 1.5;
            filter: url(#softGlow);
        }

        /* --- Center node --- */
        .center-node circle.outer {
            fill: url(#centerFill);
            stroke: #facc15;
            stroke-width: 3;
            filter: url(#centerGlow);
        }
        .center-node circle.phase-ring {
            fill: none;
            stroke-width: 1.5;
            stroke-dasharray: 4 3;
        }
        .center-label {
            fill: #fef9c3;
            font-size: 12px;
            font-weight: 600;
            font-family: 'Cinzel', 'Times New Roman', serif;
        }

        /* --- Pulse animation for available nodes --- */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.65; }
        }
        .choice-node.available circle {
            animation: pulse 2.5s ease-in-out infinite;
        }

        /* --- Hover effects --- */
        .choice-node:hover circle {
            stroke-width: 3;
            filter: url(#hoverGlow);
        }
        .choice-node:hover .choice-label {
            fill: #ffffff;
        }
    """

    # -- SVG defs (gradients and filters) --
    svg_defs = """
        <defs>
            <filter id="centerGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feFlood flood-color="#facc15" flood-opacity="0.3"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="nodeGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feFlood flood-color="#c9a54e" flood-opacity="0.35"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2" result="blur"/>
                <feFlood flood-color="#c9a54e" flood-opacity="0.2"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="hoverGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="4" result="blur"/>
                <feFlood flood-color="#ffffff" flood-opacity="0.25"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#c9a54e" stop-opacity="0.6"/>
                <stop offset="100%" stop-color="#facc15" stop-opacity="0.9"/>
            </linearGradient>
            <radialGradient id="centerFill" cx="40%" cy="35%">
                <stop offset="0%" stop-color="#1e293b"/>
                <stop offset="100%" stop-color="#0a0f1a"/>
            </radialGradient>
            <radialGradient id="nodeFill" cx="40%" cy="35%">
                <stop offset="0%" stop-color="#1e293b"/>
                <stop offset="100%" stop-color="#111827"/>
            </radialGradient>
            <radialGradient id="visitedFill" cx="40%" cy="35%">
                <stop offset="0%" stop-color="#0c2d48"/>
                <stop offset="100%" stop-color="#0a1628"/>
            </radialGradient>
            <radialGradient id="secondaryFill" cx="40%" cy="35%">
                <stop offset="0%" stop-color="#171f2e"/>
                <stop offset="100%" stop-color="#0d1117"/>
            </radialGradient>
        </defs>
    """

    # -- Assemble SVG --
    svg = f"""
        <svg viewBox="0 0 {width} {height}" width="100%" height="{height}px"
             style="max-width:{width}px; display:block; margin:0 auto;
                    background: radial-gradient(ellipse at center, rgba(15,15,30,0.4) 0%, transparent 70%);
                    border-radius: 12px;">
            <style>{svg_style}</style>
            {svg_defs}

            <!-- Decorative background rings -->
            <circle cx="{center_x}" cy="{center_y}" r="{radius + 10}"
                    fill="none" stroke="#c9a54e" stroke-opacity="0.06" stroke-width="1"/>
            <circle cx="{center_x}" cy="{center_y}" r="{radius - 5}"
                    fill="none" stroke="#c9a54e" stroke-opacity="0.04"
                    stroke-width="0.5" stroke-dasharray="3 6"/>

            <!-- Layer 1: Secondary lines -->
            {''.join(secondary_line_elements)}
            <!-- Layer 2: Primary lines -->
            {''.join(line_elements)}
            <!-- Layer 3: Secondary nodes -->
            {''.join(secondary_node_elements)}
            <!-- Layer 4: Primary nodes -->
            {''.join(node_elements)}
            <!-- Layer 5: Center node (on top) -->
            <g class="center-node">
                {center_tooltip}
                <circle class="phase-ring" cx="{center_x}" cy="{center_y}" r="40"
                        stroke="{phase_color}" stroke-opacity="0.4"/>
                <circle class="outer" cx="{center_x}" cy="{center_y}" r="34"/>
                {center_label}
            </g>
        </svg>
    """

    # Use components.html to bypass Streamlit's SVG sanitization
    try:
        import streamlit.components.v1 as components
        full_html = f"""
        <div style="background:transparent;padding:0;margin:0;">
            {svg}
            <div style="
                display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;
                margin-top: 0.5rem; padding: 0.5rem 0.75rem;
                border: 1px solid #1e293b; border-radius: 8px;
                background: rgba(10,10,20,0.5);
                font-family: 'Crimson Text', Georgia, serif;
                font-size: 0.8rem; color: #94a3b8;
            ">
                <span style="display:flex;align-items:center;gap:0.3rem;">
                    <svg width="16" height="16" viewBox="0 0 16 16" style="image-rendering:pixelated;">
                        <rect x="6" y="1" width="2" height="2" fill="#facc15"/><rect x="8" y="1" width="2" height="2" fill="#facc15"/>
                        <rect x="4" y="3" width="2" height="2" fill="#facc15"/><rect x="10" y="3" width="2" height="2" fill="#facc15"/>
                        <rect x="4" y="5" width="2" height="2" fill="#facc15"/><rect x="8" y="5" width="2" height="2" fill="#facc15"/><rect x="10" y="5" width="2" height="2" fill="#facc15"/>
                        <rect x="4" y="7" width="2" height="2" fill="#facc15"/><rect x="10" y="7" width="2" height="2" fill="#facc15"/>
                        <rect x="6" y="9" width="2" height="2" fill="#facc15"/><rect x="8" y="9" width="2" height="2" fill="#facc15"/>
                    </svg>
                    Available
                </span>
                <span style="display:flex;align-items:center;gap:0.3rem;">
                    <svg width="16" height="16" viewBox="0 0 16 16" style="image-rendering:pixelated;">
                        <rect x="4" y="5" width="2" height="2" fill="#38bdf8"/><rect x="6" y="7" width="2" height="2" fill="#38bdf8"/>
                        <rect x="8" y="9" width="2" height="2" fill="#38bdf8"/><rect x="10" y="7" width="2" height="2" fill="#38bdf8"/>
                        <rect x="12" y="5" width="2" height="2" fill="#38bdf8"/><rect x="8" y="3" width="2" height="2" fill="#38bdf8"/>
                    </svg>
                    Visited
                </span>
                <span style="display:flex;align-items:center;gap:0.3rem;">
                    <svg width="16" height="16" viewBox="0 0 16 16" style="image-rendering:pixelated;">
                        <rect x="6" y="1" width="2" height="2" fill="#94a3b8"/><rect x="8" y="1" width="2" height="2" fill="#94a3b8"/>
                        <rect x="6" y="3" width="2" height="2" fill="#94a3b8"/><rect x="10" y="3" width="2" height="2" fill="#94a3b8"/>
                        <rect x="6" y="5" width="2" height="2" fill="#94a3b8"/><rect x="8" y="5" width="2" height="2" fill="#94a3b8"/><rect x="10" y="5" width="2" height="2" fill="#94a3b8"/>
                        <rect x="6" y="7" width="2" height="2" fill="#94a3b8"/><rect x="10" y="7" width="2" height="2" fill="#94a3b8"/>
                        <rect x="6" y="9" width="2" height="2" fill="#94a3b8"/><rect x="8" y="9" width="2" height="2" fill="#94a3b8"/>
                    </svg>
                    Locked
                </span>
                <span style="display:flex;align-items:center;gap:0.3rem;">
                    <svg width="16" height="16" viewBox="0 0 16 16" style="image-rendering:pixelated;">
                        <rect x="3" y="3" width="10" height="10" fill="#0a0f1a" stroke="#facc15" stroke-width="1.5"/>
                    </svg>
                    Current
                </span>
            </div>
        </div>
        """
        components.html(full_html, height=int(height) + 80, scrolling=False)
    except (ImportError, Exception):
        # Fallback: render via st.markdown if components unavailable
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
