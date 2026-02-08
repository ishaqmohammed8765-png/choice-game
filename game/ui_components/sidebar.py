import json

from game.streamlit_compat import st

from game.data import CLASS_TEMPLATES, FACTION_KEYS, TRAIT_KEYS
from game.engine.state_machine import get_phase
from game.logic import apply_morality_flags
from game.state import add_log, load_snapshot, reset_game_state, snapshot_state, validate_snapshot
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
    """Display an HP progress bar with color coding based on health percentage."""
    current_hp = max(0, st.session_state.stats["hp"])
    player_class = st.session_state.player_class or "Warrior"
    max_hp = CLASS_TEMPLATES.get(player_class, {}).get("hp", 14)
    pct = min(current_hp / max_hp, 1.0) if max_hp > 0 else 0
    if pct > 0.6:
        bar_color = "#22c55e"
    elif pct > 0.3:
        bar_color = "#eab308"
    else:
        bar_color = "#ef4444"

    hp_icon = stat_icon_svg("hp", size=14)
    st.markdown(
        f"""
        <div style="margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;margin-bottom:2px;">
                <span style="color:#a8a29e;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.08em;display:flex;align-items:center;gap:4px;">
                    {hp_icon} HP
                </span>
                <span style="color:{bar_color};font-family:'Cinzel',serif;font-weight:700;">{current_hp}/{max_hp}</span>
            </div>
            <div style="background:#1a1a2e;border:1px solid #2a2015;border-radius:4px;height:14px;overflow:hidden;box-shadow:inset 0 1px 3px rgba(0,0,0,0.4);">
                <div style="width:{pct*100:.0f}%;height:100%;background:linear-gradient(90deg, {bar_color}cc, {bar_color});border-radius:3px;transition:width 0.4s ease;box-shadow:0 0 8px {bar_color}40;"></div>
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
        items_html.append(
            f'<div style="display:flex;align-items:center;gap:8px;padding:4px 8px;'
            f'border:1px solid {border_color};border-radius:6px;margin-bottom:3px;'
            f'background:rgba(15,15,30,0.5);">'
            f'{sprite}'
            f'<span style="font-family:\'Crimson Text\',Georgia,serif;color:#d4d4dc;font-size:0.9rem;">'
            f'{item_name}{legacy_tag}</span>'
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
    icon = class_icon_svg(player_class, size=24)
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.3rem;">
            {icon}
            <span style="font-family:'Cinzel',serif;color:#e8d5b0;font-size:1.1rem;font-weight:600;">{player_class}</span>
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


def render_main_panel() -> None:
    """Render a compact top utility bar in the main content area."""
    render_utility_bar()


def render_utility_bar() -> None:
    """Render the compact top utility bar used during active gameplay."""
    player_class = st.session_state.player_class or "Warrior"
    icon = class_icon_svg(player_class, size=22)
    current_node = st.session_state.current_node or ""
    phase = get_phase(current_node)
    phase_label = _PHASE_LABELS.get(phase, phase.title())
    phase_color = _PHASE_COLORS.get(phase, "#94a3b8")

    with st.container(border=True):
        col_status, col_controls = st.columns([2.2, 1.2])
        with col_status:
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        {icon}
                        <span style="font-family:'Cinzel',serif;color:#e8d5b0;font-size:1.05rem;">{player_class}</span>
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
            hp = st.session_state.stats["hp"]
            gold = st.session_state.stats["gold"]
            strength = st.session_state.stats["strength"]
            dexterity = st.session_state.stats["dexterity"]
            inventory_count = len(st.session_state.inventory)
            st.markdown(
                f"""
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                    <span style="padding:3px 8px;border:1px solid #334155;border-radius:999px;">HP {hp}</span>
                    <span style="padding:3px 8px;border:1px solid #334155;border-radius:999px;">Gold {gold}</span>
                    <span style="padding:3px 8px;border:1px solid #334155;border-radius:999px;">STR {strength}</span>
                    <span style="padding:3px 8px;border:1px solid #334155;border-radius:999px;">DEX {dexterity}</span>
                    <span style="padding:3px 8px;border:1px solid #334155;border-radius:999px;">Items {inventory_count}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_controls:
            st.toggle("Show map", key="show_path_map", help="Show or hide the path map panel.")
            st.toggle(
                "Show locked",
                key="show_locked_choices",
                help="Show choices that are currently unavailable.",
            )
            undo_disabled = not st.session_state.history
            if st.button("Undo", key="top_undo", use_container_width=True, disabled=undo_disabled):
                previous = st.session_state.history.pop()
                load_snapshot(previous)
                add_log("You retrace your steps and reconsider your decision.")
                st.rerun()
            if st.button("Restart", key="top_restart", use_container_width=True):
                reset_game_state()
                st.rerun()


def render_sidebar() -> None:
    """Backward-compatible sidebar renderer."""
    with st.sidebar:
        _render_player_panel_body(button_prefix="sidebar")
