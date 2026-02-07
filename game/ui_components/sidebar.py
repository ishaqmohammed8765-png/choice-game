import json

from game.streamlit_compat import st

from game.data import CLASS_TEMPLATES, FACTION_KEYS, TRAIT_KEYS
from game.logic import apply_morality_flags
from game.state import add_log, load_snapshot, reset_game_state, snapshot_state, validate_snapshot


def _render_hp_bar() -> None:
    """Display an HP progress bar with color coding based on health percentage."""
    current_hp = max(0, st.session_state.stats["hp"])
    player_class = st.session_state.player_class or "Warrior"
    max_hp = CLASS_TEMPLATES.get(player_class, {}).get("hp", 14)
    # HP can exceed starting max through effects; clamp percentage at 100%
    pct = min(current_hp / max_hp, 1.0) if max_hp > 0 else 0
    if pct > 0.6:
        bar_color = "#22c55e"
    elif pct > 0.3:
        bar_color = "#eab308"
    else:
        bar_color = "#ef4444"
    st.markdown(
        f"""
        <div style="margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:2px;">
                <span style="color:#a8a29e;font-family:'Cinzel',serif;text-transform:uppercase;letter-spacing:0.08em;">HP</span>
                <span style="color:{bar_color};font-family:'Cinzel',serif;font-weight:700;">{current_hp}/{max_hp}</span>
            </div>
            <div style="background:#1a1a2e;border:1px solid #2a2015;border-radius:4px;height:12px;overflow:hidden;">
                <div style="width:{pct*100:.0f}%;height:100%;background:{bar_color};border-radius:3px;transition:width 0.3s ease;"></div>
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


def render_sidebar() -> None:
    """Render persistent player information in the sidebar."""
    with st.sidebar:
        st.header("Adventurer")
        st.write(f"**Class:** {st.session_state.player_class}")

        with st.container(border=True):
            st.subheader("Vitals")
            _render_hp_bar()
            col_gold, col_str, col_dex = st.columns(3)
            col_gold.metric("Gold", st.session_state.stats["gold"])
            col_str.metric("STR", st.session_state.stats["strength"])
            col_dex.metric("DEX", st.session_state.stats["dexterity"])

        st.subheader("Inventory")
        if st.session_state.inventory:
            for item in st.session_state.inventory:
                st.write(f"- {item}")
        else:
            st.caption("(empty)")

        with st.expander("Reputation & Factions", expanded=False):
            st.subheader("Traits")
            _trait_labels = {
                "trust": "Trust",
                "reputation": "Reputation",
                "alignment": "Alignment",
                "ember_tide": "Ember Tide",
            }
            for trait in TRAIT_KEYS:
                label = _trait_labels.get(trait, trait.replace("_", " ").title())
                st.write(f"{label}: {st.session_state.traits[trait]}")

            st.subheader("Faction Standing")
            for faction in FACTION_KEYS:
                st.write(f"{faction.title()}: {st.session_state.factions[faction]}")

        if st.session_state.decision_history:
            with st.expander("Decision History", expanded=False):
                for entry in reversed(st.session_state.decision_history[-10:]):
                    st.caption(f"{entry.get('node', '?')} → {entry.get('choice', '?')}")

        st.divider()
        if st.button("⬅️ Back (undo last choice)", use_container_width=True, disabled=not st.session_state.history):
            previous = st.session_state.history.pop()
            load_snapshot(previous)
            add_log("You retrace your steps and reconsider your decision.")
            st.rerun()

        _render_save_load_controls()

        st.divider()
        if st.button("Restart Game", use_container_width=True):
            reset_game_state()
            st.rerun()
