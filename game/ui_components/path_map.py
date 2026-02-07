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
    """Render an upgraded fantasy-themed path map of the current node and outgoing choices."""
    node_id = st.session_state.current_node
    node = STORY_NODES.get(node_id)
    if not node:
        st.error("Path map unavailable: missing current node.")
        return

    choices = node.get("choices", [])
    st.markdown(
        '<h3 style="font-family:\'Cinzel\',serif; color:#c9a54e !important; '
        'letter-spacing:0.05em; margin-bottom:0.2rem;">'
        "Path Map</h3>",
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

    width = 580
    height = 580
    center_x = width / 2
    center_y = height / 2
    radius = min(width, height) * 0.30

    # -- Collect all rendering layers --
    line_elements: List[str] = []
    node_elements: List[str] = []
    first_hop_positions: List[tuple[float, float, float, Dict[str, Any], str]] = []
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
            tooltip = f"<title>{_escape_svg_text(tooltip_text)}</title>"

        label_lines = _wrap_svg_label(choice["label"])
        label_y = y + 38
        label_svg = _render_svg_text(
            label_lines,
            x=x,
            y=label_y,
            class_name="choice-label",
        )

        # Build CSS classes
        group_classes = ["choice-node"]
        if is_locked:
            group_classes.append("locked")
        elif not node_visited:
            group_classes.append("available")
        if node_visited:
            group_classes.append("visited")

        line_class = "path-line"
        if edge_visited:
            line_class += " visited"
        if is_locked:
            line_class += " locked"
        elif not edge_visited:
            line_class += " available"

        # Status icon
        icon_svg = ""
        if is_locked:
            icon_svg = (
                f'<text x="{x}" y="{y + 5}" text-anchor="middle" '
                f'class="node-icon locked-icon">\U0001F512</text>'
            )
        elif node_visited:
            icon_svg = (
                f'<text x="{x}" y="{y + 5}" text-anchor="middle" '
                f'class="node-icon visited-icon">\u2713</text>'
            )
        else:
            icon_svg = (
                f'<text x="{x}" y="{y + 5}" text-anchor="middle" '
                f'class="node-icon available-icon">\u2726</text>'
            )

        # Lines go on a lower layer, nodes on top
        line_elements.append(
            f'<line class="{line_class}" x1="{center_x}" y1="{center_y}" '
            f'x2="{x}" y2="{y}"></line>'
        )
        node_elements.append(
            f"""<g class="{' '.join(group_classes)}">
                {tooltip}
                <circle cx="{x}" cy="{y}" r="22"></circle>
                {icon_svg}
                {label_svg}
            </g>"""
        )
        first_hop_positions.append((x, y, angle, choice, next_node))

    # -- 2-hop secondary nodes --
    secondary_line_elements: List[str] = []
    secondary_node_elements: List[str] = []
    if show_two_hop:
        secondary_radius = radius * 1.8
        for x, y, angle, choice, next_node in first_hop_positions:
            next_node_data = STORY_NODES.get(next_node, {})
            secondary_choices = next_node_data.get("choices", [])
            if not secondary_choices:
                continue
            spread = 0.55
            count_secondary = len(secondary_choices)
            for idx, secondary_choice in enumerate(secondary_choices):
                if count_secondary == 1:
                    offset = 0
                else:
                    offset = (idx - (count_secondary - 1) / 2) * (
                        spread / (count_secondary - 1)
                    )
                angle_secondary = angle + offset
                x2 = center_x + secondary_radius * math.cos(angle_secondary)
                y2 = center_y + secondary_radius * math.sin(angle_secondary)

                is_unlocked, _ = check_requirements(
                    secondary_choice.get("requirements")
                )
                is_locked = not is_unlocked
                _, next_next_node = resolve_choice_outcome(secondary_choice)
                edge_key = (next_node, next_next_node)
                edge_visited = edge_key in visited_edges
                node_visited = next_next_node in visited_nodes

                tooltip = ""
                if is_locked:
                    tooltip_text = format_requirement_tooltip(
                        secondary_choice.get("requirements"),
                        stats=st.session_state.stats,
                        inventory=st.session_state.inventory,
                        flags=st.session_state.flags,
                        player_class=st.session_state.player_class,
                    )
                    tooltip = f"<title>{_escape_svg_text(tooltip_text)}</title>"

                label_lines = _wrap_svg_label(secondary_choice["label"])
                label_y = y2 + 32
                label_svg = _render_svg_text(
                    label_lines,
                    x=x2,
                    y=label_y,
                    class_name="choice-label secondary-label",
                )

                group_classes = ["choice-node", "secondary-node"]
                if is_locked:
                    group_classes.append("locked")
                elif not node_visited:
                    group_classes.append("available")
                if node_visited:
                    group_classes.append("visited")

                line_class = "path-line secondary"
                if edge_visited:
                    line_class += " visited"
                if is_locked:
                    line_class += " locked"

                icon_svg = ""
                if is_locked:
                    icon_svg = (
                        f'<text x="{x2}" y="{y2 + 4}" text-anchor="middle" '
                        f'class="node-icon locked-icon sec">\U0001F512</text>'
                    )
                elif node_visited:
                    icon_svg = (
                        f'<text x="{x2}" y="{y2 + 4}" text-anchor="middle" '
                        f'class="node-icon visited-icon sec">\u2713</text>'
                    )

                secondary_line_elements.append(
                    f'<line class="{line_class}" x1="{x}" y1="{y}" '
                    f'x2="{x2}" y2="{y2}"></line>'
                )
                secondary_node_elements.append(
                    f"""<g class="{' '.join(group_classes)}">
                        {tooltip}
                        <circle cx="{x2}" cy="{y2}" r="16"></circle>
                        {icon_svg}
                        {label_svg}
                    </g>"""
                )

    # -- Center node (rendered last so it draws on top) --
    center_lines = _wrap_svg_label(node.get("title", node_id), max_chars=14)
    center_label = _render_svg_text(
        center_lines, x=center_x, y=center_y + 5, class_name="center-label"
    )
    center_tooltip = f"<title>{_escape_svg_text(node_id)}</title>"

    # -- SVG CSS styles --
    svg_style = """
        /* --- Definitions for glow filters --- */

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
        }
        .path-line.secondary {
            stroke-width: 1.4;
            opacity: 0.6;
        }
        .path-line.secondary.visited {
            stroke: #38bdf8;
            opacity: 0.7;
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
            font-size: 10px;
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

        /* --- Node icons --- */
        .node-icon {
            font-size: 14px;
            pointer-events: none;
        }
        .node-icon.sec {
            font-size: 11px;
        }
        .locked-icon {
            fill: #94a3b8;
            font-size: 12px;
        }
        .visited-icon {
            fill: #38bdf8;
            font-size: 16px;
            font-weight: bold;
        }
        .available-icon {
            fill: #facc15;
            font-size: 13px;
        }

        /* --- Secondary nodes --- */
        .secondary-node circle {
            stroke-width: 1.5;
            fill: url(#secondaryFill);
        }
        .secondary-node.available circle {
            stroke: #c9a54e;
            stroke-width: 2;
            filter: url(#softGlow);
        }

        /* --- Center node --- */
        .center-node circle {
            fill: url(#centerFill);
            stroke: #facc15;
            stroke-width: 3;
            filter: url(#centerGlow);
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
    svg_defs = f"""
        <defs>
            <!-- Glow filters -->
            <filter id="centerGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feFlood flood-color="#facc15" flood-opacity="0.3"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="nodeGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feFlood flood-color="#c9a54e" flood-opacity="0.35"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2" result="blur"/>
                <feFlood flood-color="#c9a54e" flood-opacity="0.2"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="hoverGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="4" result="blur"/>
                <feFlood flood-color="#ffffff" flood-opacity="0.25"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>

            <!-- Gradients -->
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

            <!-- Decorative ring around center -->
            <radialGradient id="ringGrad" cx="50%" cy="50%">
                <stop offset="85%" stop-color="transparent"/>
                <stop offset="95%" stop-color="#c9a54e" stop-opacity="0.08"/>
                <stop offset="100%" stop-color="transparent"/>
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

            <!-- Decorative background ring -->
            <circle cx="{center_x}" cy="{center_y}" r="{radius + 10}"
                    fill="none" stroke="#c9a54e" stroke-opacity="0.06"
                    stroke-width="1"/>
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
                <circle cx="{center_x}" cy="{center_y}" r="34"></circle>
                {center_label}
            </g>
        </svg>
    """

    st.markdown(svg, unsafe_allow_html=True)

    # -- Legend --
    st.markdown(
        """
        <div style="
            display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;
            margin-top: 0.5rem; padding: 0.5rem 0.75rem;
            border: 1px solid #1e293b; border-radius: 8px;
            background: rgba(10,10,20,0.5);
            font-family: 'Crimson Text', Georgia, serif;
            font-size: 0.8rem; color: #94a3b8;
        ">
            <span style="display:flex;align-items:center;gap:0.3rem;">
                <svg width="14" height="14"><circle cx="7" cy="7" r="5"
                    fill="#1e293b" stroke="#c9a54e" stroke-width="2"/></svg>
                Available
            </span>
            <span style="display:flex;align-items:center;gap:0.3rem;">
                <svg width="14" height="14"><circle cx="7" cy="7" r="5"
                    fill="#0c2d48" stroke="#38bdf8" stroke-width="2"/></svg>
                Visited
            </span>
            <span style="display:flex;align-items:center;gap:0.3rem;">
                <svg width="14" height="14"><circle cx="7" cy="7" r="5"
                    fill="#0f172a" stroke="#475569" stroke-width="1.5"
                    stroke-dasharray="2 2" opacity="0.5"/></svg>
                Locked
            </span>
            <span style="display:flex;align-items:center;gap:0.3rem;">
                <svg width="14" height="14"><circle cx="7" cy="7" r="6"
                    fill="#0a0f1a" stroke="#facc15" stroke-width="2"/></svg>
                Current
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
        f'<tspan x="{x}" y="{start_y + index * line_height}">{_escape_svg_text(line)}</tspan>'
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
