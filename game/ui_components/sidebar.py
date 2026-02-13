import json
from html import escape

from game.streamlit_compat import st

from game.data import CLASS_TEMPLATES, FACTION_KEYS, STORY_NODES, TRAIT_KEYS
from game.engine.state_machine import get_phase
from game.logic import apply_morality_flags
from game.state import add_log, load_snapshot, normalize_meta_state, reset_game_state, snapshot_state, validate_snapshot
from game.ui_components.path_map import render_path_map
from game.ui_components.sprites import class_icon_svg, item_sprite, stat_icon_svg


_PHASE_LABELS = {
    "intro": "Prologue",
    "exploration": "Exploration",
    "combat": "Combat",
    "council": "War Council",
    "finale": "Final Assault",
    "ending": "Epilogue",
    "failure": "Setback",
}

_PHASE_COLORS = {
    "intro": "#94a3b8",
    "exploration": "#22c55e",
    "combat": "#ef4444",
    "council": "#facc15",
    "finale": "#f97316",
    "ending": "#38bdf8",
    "failure": "#8b5cf6",
}

_TRAIT_LABELS = {
    "trust": "Trust",
    "reputation": "Reputation",
    "alignment": "Alignment",
    "ember_tide": "Ember Tide",
}

_TRAIT_COLORS = {
    "trust": "#3b82f6",
    "reputation": "#facc15",
    "alignment": "#22c55e",
    "ember_tide": "#f97316",
}


def _render_centered_delta_bar(*, label: str, value: int, color: str, max_range: int) -> None:
    normalized = max(-max_range, min(max_range, value))
    if normalized >= 0:
        left_pct = 50
        width_pct = (normalized / max_range) * 50
    else:
        width_pct = (abs(normalized) / max_range) * 50
        left_pct = 50 - width_pct
    sign = "+" if value > 0 else ""
    st.markdown(
        f"""
        <div style="margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;font-size:0.73rem;margin-bottom:2px;">
                <span style="color:#7b8fad;font-family:'Cinzel',serif;letter-spacing:0.03em;">{label}</span>
                <span style="color:{color};font-family:'Cinzel',serif;font-weight:600;text-shadow:0 0 8px {color}30;">{sign}{value}</span>
            </div>
            <div style="background:rgba(10,15,28,0.8);border:1px solid rgba(30,45,74,0.5);border-radius:4px;height:7px;position:relative;overflow:hidden;">
                <div style="position:absolute;left:50%;top:0;bottom:0;width:1px;background:rgba(50,65,90,0.6);"></div>
                <div style="position:absolute;left:{left_pct}%;top:0;height:100%;width:{width_pct}%;background:linear-gradient(90deg, {color}cc, {color});border-radius:3px;transition:all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);box-shadow:0 0 6px {color}30;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hp_bar() -> None:
    """Display an HP progress bar using the requested green style."""
    current_hp = max(0, st.session_state.stats["hp"])
    player_class = st.session_state.player_class or "Warrior"
    max_hp = CLASS_TEMPLATES.get(player_class, {}).get("hp", 14)
    pct = min(current_hp / max_hp, 1.0) if max_hp > 0 else 0

    # Color shifts based on HP percentage
    if pct > 0.5:
        bar_gradient = "linear-gradient(90deg, #16a34a, #22c55e, #34d399)"
        glow_color = "rgba(34, 197, 94, 0.3)"
        text_color = "#86efac"
    elif pct > 0.25:
        bar_gradient = "linear-gradient(90deg, #ca8a04, #eab308)"
        glow_color = "rgba(234, 179, 8, 0.3)"
        text_color = "#fde047"
    else:
        bar_gradient = "linear-gradient(90deg, #dc2626, #ef4444)"
        glow_color = "rgba(239, 68, 68, 0.3)"
        text_color = "#fca5a5"

    hp_icon = stat_icon_svg("hp", size=14)
    st.markdown(
        f"""
        <div style="margin-bottom:0.6rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:0.78rem;margin-bottom:3px;">
                <span style="color:#7b8fad;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.08em;display:flex;align-items:center;gap:5px;">
                    {hp_icon} HP
                </span>
                <span style="color:{text_color};font-family:'Cinzel',serif;font-weight:700;text-shadow:0 0 8px {glow_color};">{current_hp}/{max_hp}</span>
            </div>
            <div style="background:rgba(5,20,10,0.6);border:1px solid rgba(22,101,52,0.4);border-radius:6px;height:12px;overflow:hidden;box-shadow:inset 0 2px 4px rgba(0,0,0,0.4);position:relative;">
                <div style="
                    width:{pct*100:.0f}%;height:100%;
                    background:{bar_gradient};
                    border-radius:5px;
                    transition:width 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                    box-shadow:0 0 10px {glow_color};
                    position:relative;
                    overflow:hidden;
                ">
                    <div style="
                        position:absolute;inset:0;
                        background:linear-gradient(180deg, rgba(255,255,255,0.15) 0%, transparent 50%, rgba(0,0,0,0.1) 100%);
                    "></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_phase_badge() -> None:
    """Show the current game phase as a styled badge."""
    current_node = st.session_state.current_node or ""
    phase = get_phase(current_node)
    label = _PHASE_LABELS.get(phase, phase.title())
    color = _PHASE_COLORS.get(phase, "#94a3b8")
    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding: 3px 12px;
            border: 1px solid {color}50;
            border-radius: 999px;
            background: {color}12;
            font-family: 'Cinzel', serif;
            font-size: 0.68rem;
            color: {color};
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            box-shadow: 0 0 12px {color}10;
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
        ">{label}</div>
        """,
        unsafe_allow_html=True,
    )


def _render_inventory_with_sprites() -> None:
    """Render the inventory list with pixel art sprites for each item."""
    st.subheader("Inventory")
    if not st.session_state.inventory:
        st.caption("(empty)")
        return

    meta_state = normalize_meta_state(st.session_state.get("meta_state"))
    legacy_items = set(meta_state.get("unlocked_items", []))

    items_html = []
    for idx, item_name in enumerate(st.session_state.inventory):
        sprite = item_sprite(item_name, size=22)
        is_legacy = item_name in legacy_items
        legacy_tag = ' <span style="color:#d4a843;font-size:0.65rem;font-family:\'Cinzel\',serif;letter-spacing:0.04em;opacity:0.8;">(legacy)</span>' if is_legacy else ""
        border_color = "rgba(212, 168, 67, 0.25)" if is_legacy else "rgba(30, 45, 74, 0.5)"
        bg = "rgba(212, 168, 67, 0.04)" if is_legacy else "rgba(12, 18, 32, 0.6)"
        safe_item_name = escape(str(item_name), quote=True)
        items_html.append(
            f'<div style="display:flex;align-items:center;gap:10px;padding:6px 10px;'
            f'border:1px solid {border_color};border-radius:8px;margin-bottom:4px;'
            f'background:{bg};'
            f'backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);'
            f'transition:border-color 0.2s ease, background 0.2s ease;'
            f'">'
            f'{sprite}'
            f'<span style="font-family:\'Crimson Text\',Georgia,serif;color:#c0c8d8;font-size:0.9rem;">'
            f'{safe_item_name}{legacy_tag}</span>'
            f'</div>'
        )

    st.markdown("\n".join(items_html), unsafe_allow_html=True)


def _render_traits_panel() -> None:
    """Render traits with colored bars showing current value."""
    st.subheader("Traits")
    for trait in TRAIT_KEYS:
        label = _TRAIT_LABELS.get(trait, trait.replace("_", " ").title())
        value = st.session_state.traits[trait]
        color = _TRAIT_COLORS.get(trait, "#94a3b8")
        _render_centered_delta_bar(label=label, value=value, color=color, max_range=10)


def _render_faction_bars() -> None:
    """Render faction standing as horizontal bars."""
    st.subheader("Faction Standing")
    faction_colors = {
        "oakrest": "#22c55e",
        "ironwardens": "#3b82f6",
        "ashfang": "#f97316",
        "bandits": "#ef4444",
    }
    for faction in FACTION_KEYS:
        value = st.session_state.factions[faction]
        color = faction_colors.get(faction, "#94a3b8")
        display_name = faction.title()
        _render_centered_delta_bar(label=display_name, value=value, color=color, max_range=5)


def _render_campaign_progress() -> None:
    """Display run progress and key milestones to improve navigation feedback."""
    st.subheader("Campaign Progress")
    canonical_nodes = [node_id for node_id in STORY_NODES if not node_id.startswith("intro_")]
    visited_nodes = {
        node_id
        for node_id in st.session_state.visited_nodes
        if node_id in STORY_NODES and not node_id.startswith("intro_")
    }
    explored = len(visited_nodes)
    total = max(1, len(canonical_nodes))
    pct = explored / total
    st.progress(pct, text=f"Explored scenes: {explored}/{total}")

    branch_flags = [
        flag_name
        for flag_name, value in st.session_state.flags.items()
        if flag_name.startswith("branch_") and flag_name.endswith("_completed") and value
    ]
    major_threats = sum(
        1
        for flag_name in ("tidebound_knight_defeated", "pyre_alchemist_defeated")
        if st.session_state.flags.get(flag_name)
    )
    st.caption(f"Resolved field operations: {len(branch_flags)}")
    st.caption(f"Major threats defeated: {major_threats}/2")


def _render_save_load_controls() -> None:
    with st.expander("Save / Load", expanded=False):
        if st.button("Export current state", use_container_width=True):
            st.session_state.save_blob = json.dumps(snapshot_state(), indent=2)

        save_text = st.text_area(
            "State JSON",
            value=st.session_state.save_blob,
            height=180,
            key="save_load_text",
        )
        if st.button("Import state", use_container_width=True):
            try:
                payload = json.loads(save_text)
                is_valid, errors = validate_snapshot(payload)
                if not is_valid:
                    st.error("Invalid save: " + " ".join(errors))
                else:
                    load_snapshot(payload)
                    apply_morality_flags(st.session_state.flags)
                    st.success("State imported successfully.")
                    st.rerun()
            except json.JSONDecodeError:
                st.error("Invalid JSON. Please paste a valid exported state.")


def _render_system_controls(*, button_prefix: str) -> None:
    # Put the restart button first so we can safely reset session state before
    # any widget-backed keys (e.g. show_locked_choices) are created this run.
    if st.button("Restart Game", key=f"{button_prefix}_restart", use_container_width=True):
        reset_game_state()
        st.rerun()

    st.toggle(
        "Show locked choices",
        key="show_locked_choices",
        help="Display locked choices and their requirement details in the story panel.",
    )
    st.toggle(
        "Developer mode",
        key="dev_mode",
        help="Show debug controls (jump to nodes, endings, etc.).",
    )

    if st.session_state.get("dev_mode"):
        with st.expander("Developer Tools", expanded=True):
            ending_targets = sorted([nid for nid in STORY_NODES.keys() if str(nid).startswith("ending_")])
            quick_targets = [
                "final_confrontation",
                "ending_good",
            ]
            targets = [t for t in quick_targets if t in STORY_NODES]
            for t in ending_targets:
                if t not in targets:
                    targets.append(t)

            if targets:
                st.selectbox(
                    "Jump to node",
                    options=targets,
                    key=f"{button_prefix}_dev_jump_target",
                )
                col_jump, col_end = st.columns(2)
                with col_jump:
                    if st.button("Jump", key=f"{button_prefix}_dev_jump", use_container_width=True):
                        target = st.session_state.get(f"{button_prefix}_dev_jump_target")
                        if target in STORY_NODES:
                            st.session_state.current_node = target
                            st.session_state.pending_choice_confirmation = None
                            st.session_state.pending_auto_death = False
                            st.session_state.last_outcome_summary = None
                            st.session_state.last_choice_feedback = []
                            if "visited_nodes" in st.session_state:
                                if target not in st.session_state.visited_nodes:
                                    st.session_state.visited_nodes.append(target)
                            add_log(f"[DEV] Jumped to {target}.")
                            st.rerun()
                with col_end:
                    if st.button("Skip to end", key=f"{button_prefix}_dev_skip_end", use_container_width=True):
                        target = "ending_good" if "ending_good" in STORY_NODES else (ending_targets[0] if ending_targets else None)
                        if target:
                            st.session_state.current_node = target
                            st.session_state.pending_choice_confirmation = None
                            st.session_state.pending_auto_death = False
                            st.session_state.last_outcome_summary = None
                            st.session_state.last_choice_feedback = []
                            if "visited_nodes" in st.session_state:
                                if target not in st.session_state.visited_nodes:
                                    st.session_state.visited_nodes.append(target)
                            add_log(f"[DEV] Skipped to {target}.")
                            st.rerun()
            else:
                st.info("No ending nodes found to jump to.")
    st.divider()
    if st.button(
        "Back (undo last choice)",
        key=f"{button_prefix}_undo",
        use_container_width=True,
        disabled=not st.session_state.history,
    ):
        previous = st.session_state.history.pop()
        load_snapshot(previous)
        add_log("You retrace your steps and reconsider your decision.")
        st.rerun()
    _render_save_load_controls()
    st.divider()


def _render_player_panel_body(*, button_prefix: str) -> None:
    player_class = st.session_state.player_class or "Warrior"
    safe_player_class = escape(player_class, quote=True)
    icon = class_icon_svg(player_class, size=26)
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.4rem;">
            <div style="
                width:38px;height:38px;
                display:flex;align-items:center;justify-content:center;
                border-radius:10px;
                background:rgba(212, 168, 67, 0.06);
                border:1px solid rgba(212, 168, 67, 0.15);
            ">
                {icon}
            </div>
            <span style="font-family:'Cinzel',serif;color:#e8dcc8;font-size:1.1rem;font-weight:600;letter-spacing:0.04em;">{safe_player_class}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_phase_badge()

    with st.container(border=True):
        st.subheader("Vitals")
        _render_hp_bar()
        gold_icon = stat_icon_svg("gold", size=14)
        str_icon = stat_icon_svg("strength", size=14)
        dex_icon = stat_icon_svg("dexterity", size=14)
        st.markdown(
            f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center;margin-top:6px;">
                <div style="padding:6px 4px;border:1px solid rgba(212,168,67,0.15);border-radius:8px;background:rgba(212,168,67,0.04);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#7a6a4a;font-family:'Cinzel',serif;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.06em;">
                        {gold_icon} Gold
                    </div>
                    <div style="color:#f0c850;font-family:'Cinzel',serif;font-weight:700;font-size:1.15rem;text-shadow:0 0 10px rgba(212,168,67,0.25);">
                        {st.session_state.stats['gold']}
                    </div>
                </div>
                <div style="padding:6px 4px;border:1px solid rgba(59,130,246,0.15);border-radius:8px;background:rgba(59,130,246,0.04);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#4a6a8a;font-family:'Cinzel',serif;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.06em;">
                        {str_icon} STR
                    </div>
                    <div style="color:#93c5fd;font-family:'Cinzel',serif;font-weight:700;font-size:1.15rem;text-shadow:0 0 10px rgba(59,130,246,0.25);">
                        {st.session_state.stats['strength']}
                    </div>
                </div>
                <div style="padding:6px 4px;border:1px solid rgba(52,211,153,0.15);border-radius:8px;background:rgba(52,211,153,0.04);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#4a7a5a;font-family:'Cinzel',serif;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.06em;">
                        {dex_icon} DEX
                    </div>
                    <div style="color:#6ee7b7;font-family:'Cinzel',serif;font-weight:700;font-size:1.15rem;text-shadow:0 0 10px rgba(52,211,153,0.25);">
                        {st.session_state.stats['dexterity']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _render_inventory_with_sprites()

    with st.expander("Reputation & Factions", expanded=False):
        _render_traits_panel()
        st.divider()
        _render_faction_bars()

    st.divider()
    _render_system_controls(button_prefix=button_prefix)


def _render_side_hud_header() -> None:
    """Render compact player identity and phase at the top of the side HUD."""
    player_class = st.session_state.player_class or "Warrior"
    safe_player_class = escape(player_class, quote=True)
    icon = class_icon_svg(player_class, size=24)
    hp_icon = stat_icon_svg("hp", size=13)
    gold_icon = stat_icon_svg("gold", size=13)
    str_icon = stat_icon_svg("strength", size=13)
    dex_icon = stat_icon_svg("dexterity", size=13)
    hp = st.session_state.stats["hp"]
    gold = st.session_state.stats["gold"]
    strength = st.session_state.stats["strength"]
    dexterity = st.session_state.stats["dexterity"]
    st.markdown(
        f"""
        <div style="
            padding:0.8rem 0.85rem;
            border:1px solid rgba(30, 45, 74, 0.6);
            border-radius:12px;
            background:linear-gradient(160deg, rgba(12, 18, 32, 0.95), rgba(8, 13, 26, 0.98));
            margin-bottom:0.5rem;
            position:relative;
            overflow:hidden;
            box-shadow:0 4px 16px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.02);
            backdrop-filter:blur(8px);
            -webkit-backdrop-filter:blur(8px);
        ">
            <!-- Top accent -->
            <div style="
                position:absolute;top:0;left:10%;right:10%;height:1px;
                background:linear-gradient(90deg, transparent, rgba(212, 168, 67, 0.2), transparent);
            "></div>
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="
                        width:36px;height:36px;
                        display:flex;align-items:center;justify-content:center;
                        border-radius:10px;
                        background:rgba(212, 168, 67, 0.06);
                        border:1px solid rgba(212, 168, 67, 0.15);
                    ">
                        {icon}
                    </div>
                    <span style="font-family:'Cinzel',serif;color:#e8dcc8;font-size:1rem;letter-spacing:0.04em;">{safe_player_class}</span>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;">
                <div style="padding:5px 6px;border:1px solid rgba(34,197,94,0.2);border-radius:8px;text-align:center;background:rgba(34,197,94,0.06);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#5a7a6a;font-size:0.58rem;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.05em;">{hp_icon} HP</div>
                    <div style="color:#86efac;font-family:'Cinzel',serif;font-weight:700;font-size:1rem;text-shadow:0 0 8px rgba(34,197,94,0.2);">{hp}</div>
                </div>
                <div style="padding:5px 6px;border:1px solid rgba(212,168,67,0.2);border-radius:8px;text-align:center;background:rgba(212,168,67,0.06);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#7a6a4a;font-size:0.58rem;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.05em;">{gold_icon} Gold</div>
                    <div style="color:#f0c850;font-family:'Cinzel',serif;font-weight:700;font-size:1rem;text-shadow:0 0 8px rgba(212,168,67,0.2);">{gold}</div>
                </div>
                <div style="padding:5px 6px;border:1px solid rgba(59,130,246,0.2);border-radius:8px;text-align:center;background:rgba(59,130,246,0.06);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#4a6a8a;font-size:0.58rem;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.05em;">{str_icon} STR</div>
                    <div style="color:#93c5fd;font-family:'Cinzel',serif;font-weight:700;font-size:1rem;text-shadow:0 0 8px rgba(59,130,246,0.2);">{strength}</div>
                </div>
                <div style="padding:5px 6px;border:1px solid rgba(34,197,94,0.2);border-radius:8px;text-align:center;background:rgba(34,197,94,0.06);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#4a7a5a;font-size:0.58rem;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.05em;">{dex_icon} DEX</div>
                    <div style="color:#6ee7b7;font-family:'Cinzel',serif;font-weight:700;font-size:1rem;text-shadow:0 0 8px rgba(52,211,153,0.2);">{dexterity}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_hp_bar()
    _render_phase_badge()


def render_side_panel() -> None:
    """Render the right-side HUD with inventory, map, progression, and system tabs."""
    _render_side_hud_header()
    inventory_tab, map_tab, progress_tab, system_tab = st.tabs(
        ["Inventory", "Path Map", "Progress", "System"]
    )

    with inventory_tab:
        _render_inventory_with_sprites()

    with map_tab:
        render_path_map()

    with progress_tab:
        _render_campaign_progress()
        st.divider()
        _render_traits_panel()
        st.divider()
        _render_faction_bars()

    with system_tab:
        _render_system_controls(button_prefix="panel")


def render_main_panel() -> None:
    """Render a compact top utility bar in the main content area."""
    render_utility_bar()


def render_utility_bar() -> None:
    """Render a compact top status bar for active gameplay."""
    player_class = st.session_state.player_class or "Warrior"
    safe_player_class = escape(player_class, quote=True)
    icon = class_icon_svg(player_class, size=20)
    current_node = st.session_state.current_node or ""
    phase = get_phase(current_node)
    phase_label = _PHASE_LABELS.get(phase, phase.title())
    phase_color = _PHASE_COLORS.get(phase, "#94a3b8")

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    {icon}
                    <span style="font-family:'Cinzel',serif;color:#e8dcc8;font-size:0.95rem;letter-spacing:0.03em;">{safe_player_class}</span>
                </div>
                <span style="
                    border:1px solid {phase_color}45;
                    background:{phase_color}10;
                    color:{phase_color};
                    border-radius:999px;
                    padding:3px 12px;
                    font-family:'Cinzel',serif;
                    font-size:0.65rem;
                    letter-spacing:0.06em;
                    text-transform:uppercase;
                    box-shadow:0 0 10px {phase_color}08;
                ">{phase_label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Undo/Restart moved to the System tab in the right panel.")


def render_sidebar() -> None:
    """Backward-compatible sidebar renderer."""
    with st.sidebar:
        _render_player_panel_body(button_prefix="sidebar")
