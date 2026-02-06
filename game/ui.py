import json
from typing import Any, Dict, List

import streamlit as st

from game.data import STAT_KEYS, STORY_NODES, TRAIT_KEYS
from game.logic import (
    apply_morality_flags,
    check_requirements,
    execute_choice,
    get_available_choices,
    get_choice_warnings,
    transition_to,
    transition_to_failure,
)
from game.state import add_log, load_snapshot, reset_game_state, snapshot_state

def render_sidebar() -> None:
    """Render persistent player information in the sidebar."""
    with st.sidebar:
        st.header("Adventurer")
        st.write(f"**Class:** {st.session_state.player_class}")

        st.subheader("Stats")
        st.write(f"HP: {st.session_state.stats['hp']}")
        st.write(f"Gold: {st.session_state.stats['gold']}")
        st.write(f"Strength: {st.session_state.stats['strength']}")
        st.write(f"Dexterity: {st.session_state.stats['dexterity']}")

        st.subheader("Inventory")
        if st.session_state.inventory:
            for item in st.session_state.inventory:
                st.write(f"- {item}")
        else:
            st.write("(empty)")

        st.subheader("Flags")
        if st.session_state.flags:
            for key, value in sorted(st.session_state.flags.items()):
                st.write(f"- {key}: {value}")
        else:
            st.write("(none)")

        st.subheader("Traits")
        for trait in TRAIT_KEYS:
            st.write(f"{trait.title()}: {st.session_state.traits[trait]}")

        st.subheader("Key Events Seen")
        if st.session_state.seen_events:
            for event in st.session_state.seen_events[-6:]:
                st.write(f"- {event}")
        else:
            st.write("(none)")

        st.divider()
        if st.button("⬅️ Back (undo last choice)", use_container_width=True, disabled=not st.session_state.history):
            previous = st.session_state.history.pop()
            load_snapshot(previous)
            add_log("You retrace your steps and reconsider your decision.")
            st.rerun()

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

        st.divider()
        if st.button("Restart Game", use_container_width=True):
            reset_game_state()
            st.rerun()


def render_node() -> None:
    """Render current node, narrative, choices, and edge-case handling."""
    node_id = st.session_state.current_node
    if node_id not in STORY_NODES:
        st.error(f"Missing node '{node_id}'.")
        transition_to("death")
        st.rerun()
        return

    node = STORY_NODES[node_id]

    # Gate access to nodes that have node-level requirements.
    node_ok, node_reason = check_requirements(node.get("requirements"))
    if not node_ok:
        st.error(f"You cannot access this path: {node_reason}")
        transition_to_failure("traitor")
        st.rerun()
        return

    st.title(node["title"])
    st.write(node["text"])

    if st.session_state.last_choice_feedback:
        with st.container(border=True):
            st.caption("Consequence feedback")
            for line in st.session_state.last_choice_feedback:
                st.write(f"• {line}")

    # Death can happen from previous choice effects.
    if st.session_state.stats["hp"] <= 0:
        transition_to_failure("injured")
        st.rerun()
        return

    choices = node.get("choices", [])
    available_choices = get_available_choices(node)

    if not choices:
        st.success("The story has reached an ending. Restart to explore another path.")
        return

    st.subheader("What do you do?")
    pending = st.session_state.pending_choice_confirmation

    if pending and pending.get("node") == node_id:
        with st.container(border=True):
            st.warning(f"Confirm choice: **{pending['label']}**")
            for warning in pending.get("warnings", []):
                st.write(f"- ⚠️ {warning}")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("Confirm risky choice", type="primary", key=f"confirm_{node_id}", use_container_width=True):
                    choice_index = pending["choice_index"]
                    if 0 <= choice_index < len(available_choices):
                        selected = available_choices[choice_index]
                        execute_choice(node_id, selected["label"], selected)
                    st.rerun()
            with col_cancel:
                if st.button("Cancel", key=f"cancel_{node_id}", use_container_width=True):
                    st.session_state.pending_choice_confirmation = None
                    st.rerun()

    for idx, choice in enumerate(available_choices):
        label = choice["label"]
        warnings = get_choice_warnings(choice)
        display_label = f"⚠️ {label}" if warnings else label
        if st.button(display_label, key=f"choice_{node_id}_{idx}", use_container_width=True):
            if warnings:
                st.session_state.pending_choice_confirmation = {
                    "node": node_id,
                    "choice_index": idx,
                    "label": label,
                    "warnings": warnings,
                }
            else:
                execute_choice(node_id, label, choice)
            st.rerun()

    if not available_choices:
        st.warning("No valid choices remain based on your current stats, items, and flags.")
        if st.button("Take a setback and adapt", type="primary"):
            transition_to_failure("resource_loss")
            st.rerun()


def render_log() -> None:
    """Show the most recent narrative events."""
    with st.expander("Recent Event Log (last 10)", expanded=False):
        recent = st.session_state.event_log[-10:]
        if not recent:
            st.write("No events yet.")
        else:
            for entry in recent:
                st.write(f"- {entry}")


def format_requirements(requirements: Dict[str, Any] | None) -> str:
    """Convert requirements dict into readable bullet-style text."""
    if not requirements:
        return "None"

    details: List[str] = []
    if "class" in requirements:
        details.append(f"Class: {', '.join(requirements['class'])}")
    if "min_hp" in requirements:
        details.append(f"HP >= {requirements['min_hp']}")
    if "min_gold" in requirements:
        details.append(f"Gold >= {requirements['min_gold']}")
    if "min_strength" in requirements:
        details.append(f"Strength >= {requirements['min_strength']}")
    if "min_dexterity" in requirements:
        details.append(f"Dexterity >= {requirements['min_dexterity']}")
    if requirements.get("items"):
        details.append(f"Needs items: {', '.join(requirements['items'])}")
    if requirements.get("missing_items"):
        details.append(f"Must not have: {', '.join(requirements['missing_items'])}")
    if requirements.get("flag_true"):
        details.append(f"Flags true: {', '.join(requirements['flag_true'])}")
    if requirements.get("flag_false"):
        details.append(f"Flags false: {', '.join(requirements['flag_false'])}")

    return " | ".join(details) if details else "None"


def format_outcomes(effects: Dict[str, Any] | None) -> str:
    """Convert effects dict into readable outcome summary."""
    if not effects:
        return "No direct effect"

    details: List[str] = []
    for stat in STAT_KEYS:
        if stat in effects:
            value = effects[stat]
            sign = "+" if value >= 0 else ""
            details.append(f"{stat.upper()} {sign}{value}")

    if effects.get("add_items"):
        details.append(f"Add items: {', '.join(effects['add_items'])}")
    if effects.get("remove_items"):
        details.append(f"Remove items: {', '.join(effects['remove_items'])}")
    if effects.get("set_flags"):
        spoiler_flags = {"ending_quality", "warrior_best_ending", "rogue_best_ending"}
        visible_flags = {k: v for k, v in effects["set_flags"].items() if k not in spoiler_flags}
        hidden_flag_count = len(effects["set_flags"]) - len(visible_flags)

        if visible_flags:
            flag_updates = ", ".join([f"{k}={v}" for k, v in visible_flags.items()])
            details.append(f"Set flags: {flag_updates}")
        if hidden_flag_count:
            details.append("Ending impact: hidden to avoid spoilers")
    if effects.get("log"):
        details.append(f"Narrative: {effects['log']}")

    return " | ".join(details) if details else "No direct effect"


def render_choice_outcomes_tab() -> None:
    """Render a separate tab that lists every node choice and its outcomes."""
    st.subheader("All Choices & Outcomes")
    st.caption("A full reference of every choice path and requirements. Ending-impact spoilers are hidden.")

    for node_id, node in STORY_NODES.items():
        choices = node.get("choices", [])
        if not choices:
            continue

        with st.expander(f"{node['title']} ({node_id})", expanded=False):
            for idx, choice in enumerate(choices, start=1):
                st.markdown(f"**{idx}. {choice['label']}**")
                st.write(f"- **Requirements:** {format_requirements(choice.get('requirements'))}")
                st.write(f"- **Outcome:** {format_outcomes(choice.get('effects'))}")
                st.write(f"- **Next node:** `{choice['next']}`")
                st.write("---")
