import json
from html import escape

from game.streamlit_compat import st

from game.data import CLASS_TEMPLATES, FACTION_KEYS, TRAIT_KEYS
from game.engine.state_machine import get_phase
from game.logic import apply_morality_flags
from game.state import add_log, load_snapshot, reset_game_state, snapshot_state, validate_snapshot
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


def _render_hp_bar() -> None:
    """Display an HP progress bar using the requested green style."""
    current_hp = max(0, st.session_state.stats["hp"])
    player_class = st.session_state.player_class or "Warrior"
    max_hp = CLASS_TEMPLATES.get(player_class, {}).get("hp", 14)
    pct = min(current_hp / max_hp, 1.0) if max_hp > 0 else 0
    bar_color = "#22c55e"

    hp_icon = stat_icon_svg("hp", size=14)
    st.markdown(
        f"""
        <div style="margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;margin-bottom:2px;">
                <span style="color:#a8a29e;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.08em;display:flex;align-items:center;gap:4px;">
                    {hp_icon} HP
                </span>
                <span style="color:#86efac;font-family:'Cinzel',serif;font-weight:700;">{current_hp}/{max_hp}</span>
            </div>
            <div style="background:#052e16;border:1px solid #166534;border-radius:4px;height:14px;overflow:hidden;box-shadow:inset 0 1px 3px rgba(0,0,0,0.4);">
                <div style="width:{pct*100:.0f}%;height:100%;background:linear-gradient(90deg, #16a34a, #22c55e);border-radius:3px;transition:width 0.4s ease;box-shadow:0 0 8px #22c55e40;"></div>
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
            padding: 2px 10px;
            border: 1px solid {color}60;
            border-radius: 12px;
            background: {color}15;
            font-family: 'Cinzel', serif;
            font-size: 0.7rem;
            color: {color};
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
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

    meta_state = st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})
    legacy_items = set(meta_state.get("unlocked_items", []))

    items_html = []
    for item_name in st.session_state.inventory:
        sprite = item_sprite(item_name, size=22)
        is_legacy = item_name in legacy_items
        legacy_tag = ' <span style="color:#c9a54e;font-size:0.7rem;font-family:\'Cinzel\',serif;">(legacy)</span>' if is_legacy else ""
        border_color = "#c9a54e40" if is_legacy else "#1e293b"
        safe_item_name = escape(str(item_name), quote=True)
        items_html.append(
            f'<div style="display:flex;align-items:center;gap:8px;padding:4px 8px;'
            f'border:1px solid {border_color};border-radius:6px;margin-bottom:3px;'
            f'background:rgba(15,15,30,0.5);">'
            f'{sprite}'
            f'<span style="font-family:\'Crimson Text\',Georgia,serif;color:#d4d4dc;font-size:0.9rem;">'
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
        max_range = 10
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
            <div style="margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:1px;">
                    <span style="color:#a8a29e;font-family:'Cinzel',serif;">{label}</span>
                    <span style="color:{color};font-family:'Cinzel',serif;font-weight:600;">{sign}{value}</span>
                </div>
                <div style="background:#1a1a2e;border:1px solid #1e293b;border-radius:3px;height:6px;position:relative;overflow:hidden;">
                    <div style="position:absolute;left:50%;top:0;bottom:0;width:1px;background:#334155;"></div>
                    <div style="position:absolute;left:{left_pct}%;top:0;height:100%;width:{width_pct}%;background:{color};border-radius:2px;transition:all 0.3s ease;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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
        max_range = 5
        normalized = max(-max_range, min(max_range, value))
        if normalized >= 0:
            left_pct = 50
            width_pct = (normalized / max_range) * 50
        else:
            width_pct = (abs(normalized) / max_range) * 50
            left_pct = 50 - width_pct

        sign = "+" if value > 0 else ""
        display_name = faction.title()
        st.markdown(
            f"""
            <div style="margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:1px;">
                    <span style="color:#a8a29e;font-family:'Cinzel',serif;">{display_name}</span>
                    <span style="color:{color};font-family:'Cinzel',serif;font-weight:600;">{sign}{value}</span>
                </div>
                <div style="background:#1a1a2e;border:1px solid #1e293b;border-radius:3px;height:6px;position:relative;overflow:hidden;">
                    <div style="position:absolute;left:50%;top:0;bottom:0;width:1px;background:#334155;"></div>
                    <div style="position:absolute;left:{left_pct}%;top:0;height:100%;width:{width_pct}%;background:{color};border-radius:2px;transition:all 0.3s ease;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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


def _render_player_panel_body(*, button_prefix: str) -> None:
    player_class = st.session_state.player_class or "Warrior"
    safe_player_class = escape(player_class, quote=True)
    icon = class_icon_svg(player_class, size=24)
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.3rem;">
            {icon}
            <span style="font-family:'Cinzel',serif;color:#e8d5b0;font-size:1.1rem;font-weight:600;">{safe_player_class}</span>
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
            <div style="display:flex;justify-content:space-around;text-align:center;margin-top:4px;">
                <div>
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#a8a29e;font-family:'Cinzel',serif;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;">
                        {gold_icon} Gold
                    </div>
                    <div style="color:#facc15;font-family:'Cinzel',serif;font-weight:700;font-size:1.2rem;text-shadow:0 0 8px rgba(250,204,21,0.3);">
                        {st.session_state.stats['gold']}
                    </div>
                </div>
                <div>
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#a8a29e;font-family:'Cinzel',serif;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;">
                        {str_icon} STR
                    </div>
                    <div style="color:#facc15;font-family:'Cinzel',serif;font-weight:700;font-size:1.2rem;text-shadow:0 0 8px rgba(250,204,21,0.3);">
                        {st.session_state.stats['strength']}
                    </div>
                </div>
                <div>
                    <div style="display:flex;align-items:center;justify-content:center;gap:3px;color:#a8a29e;font-family:'Cinzel',serif;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;">
                        {dex_icon} DEX
                    </div>
                    <div style="color:#facc15;font-family:'Cinzel',serif;font-weight:700;font-size:1.2rem;text-shadow:0 0 8px rgba(250,204,21,0.3);">
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
    if st.button("Restart Game", key=f"{button_prefix}_restart", use_container_width=True):
        reset_game_state()
        st.rerun()


def _render_side_hud_header() -> None:
    """Render compact player identity and phase at the top of the side HUD."""
    player_class = st.session_state.player_class or "Warrior"
    safe_player_class = escape(player_class, quote=True)
    icon = class_icon_svg(player_class, size=22)
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
            padding:0.7rem 0.75rem;
            border:1px solid #2b3449;
            border-radius:10px;
            background:linear-gradient(160deg, rgba(11,15,28,0.96), rgba(16,22,36,0.92));
            margin-bottom:0.45rem;
        ">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    {icon}
                    <span style="font-family:'Cinzel',serif;color:#f3e9d2;font-size:0.98rem;">{safe_player_class}</span>
                </div>
                <span style="color:#93a4c4;font-size:0.75rem;">Status</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin-top:7px;">
                <span style="padding:3px 8px;border:1px solid #275348;border-radius:8px;font-size:0.74rem;display:flex;align-items:center;gap:5px;background:rgba(22,163,74,0.10);">
                    {hp_icon} HP {hp}
                </span>
                <span style="padding:3px 8px;border:1px solid #5f4b1f;border-radius:8px;font-size:0.74rem;display:flex;align-items:center;gap:5px;background:rgba(202,138,4,0.12);">
                    {gold_icon} Gold {gold}
                </span>
                <span style="padding:3px 8px;border:1px solid #2f4f83;border-radius:8px;font-size:0.74rem;display:flex;align-items:center;gap:5px;background:rgba(59,130,246,0.12);">
                    {str_icon} STR {strength}
                </span>
                <span style="padding:3px 8px;border:1px solid #2f5f4a;border-radius:8px;font-size:0.74rem;display:flex;align-items:center;gap:5px;background:rgba(34,197,94,0.12);">
                    {dex_icon} DEX {dexterity}
                </span>
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
        _render_traits_panel()
        st.divider()
        _render_faction_bars()

    with system_tab:
        st.toggle(
            "Show locked choices",
            key="show_locked_choices",
            help="Display locked choices and their requirement details in the story panel.",
        )
        st.divider()
        if st.button(
            "Back (undo last choice)",
            key="panel_undo",
            use_container_width=True,
            disabled=not st.session_state.history,
        ):
            previous = st.session_state.history.pop()
            load_snapshot(previous)
            add_log("You retrace your steps and reconsider your decision.")
            st.rerun()
        _render_save_load_controls()
        st.divider()
        if st.button("Restart Game", key="panel_restart", use_container_width=True):
            reset_game_state()
            st.rerun()


def render_main_panel() -> None:
    """Render a compact top utility bar in the main content area."""
    render_utility_bar()


def render_utility_bar() -> None:
    """Render a compact top status bar for active gameplay."""
    player_class = st.session_state.player_class or "Warrior"
    safe_player_class = escape(player_class, quote=True)
    icon = class_icon_svg(player_class, size=22)
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
                    <span style="font-family:'Cinzel',serif;color:#e8d5b0;font-size:1.05rem;">{safe_player_class}</span>
                </div>
                <span style="
                    border:1px solid {phase_color}60;
                    background:{phase_color}14;
                    color:{phase_color};
                    border-radius:999px;
                    padding:2px 10px;
                    font-family:'Cinzel',serif;
                    font-size:0.68rem;
                    letter-spacing:0.05em;
                    text-transform:uppercase;
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
