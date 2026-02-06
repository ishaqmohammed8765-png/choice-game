import json

from game.streamlit_compat import st

from game.data import FACTION_KEYS, STORY_NODES, TRAIT_KEYS
from game.logic import apply_morality_flags
from game.state import add_log, load_snapshot, reset_game_state, snapshot_state


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
                required_keys = {
                    "player_class",
                    "current_node",
                    "stats",
                    "inventory",
                    "flags",
                    "event_log",
                    "traits",
                    "seen_events",
                    "factions",
                    "decision_history",
                    "last_choice_feedback",
                }
                if not required_keys.issubset(payload.keys()):
                    st.error("Invalid save: missing required keys.")
                elif payload["current_node"] not in STORY_NODES:
                    st.error("Invalid save: current node does not exist.")
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
            col_hp, col_gold = st.columns(2)
            col_hp.metric("HP", st.session_state.stats["hp"])
            col_gold.metric("Gold", st.session_state.stats["gold"])
            col_str, col_dex = st.columns(2)
            col_str.metric("Strength", st.session_state.stats["strength"])
            col_dex.metric("Dexterity", st.session_state.stats["dexterity"])

        st.subheader("Inventory")
        if st.session_state.inventory:
            for item in st.session_state.inventory:
                st.write(f"- {item}")
        else:
            st.caption("(empty)")

        with st.expander("Reputation & Factions", expanded=False):
            st.subheader("Traits")
            for trait in TRAIT_KEYS:
                st.write(f"{trait.title()}: {st.session_state.traits[trait]}")

            st.subheader("Faction Standing")
            for faction in FACTION_KEYS:
                st.write(f"{faction.title()}: {st.session_state.factions[faction]}")

        with st.expander("Debug data (flags & events)", expanded=False):
            st.caption("Quick access to runtime state while testing story branches.")
            if st.session_state.flags:
                st.write("**Flags**")
                for key, value in sorted(st.session_state.flags.items()):
                    st.write(f"- {key}: {value}")
            else:
                st.caption("No flags set.")

            st.write("**Key Events Seen**")
            if st.session_state.seen_events:
                for event in st.session_state.seen_events[-8:]:
                    st.write(f"- {event}")
            else:
                st.caption("(none)")

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
