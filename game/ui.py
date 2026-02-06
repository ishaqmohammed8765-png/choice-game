import json
from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import FACTION_KEYS, STAT_KEYS, STORY_NODES, TRAIT_KEYS
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

        st.divider()
        if st.button("Restart Game", use_container_width=True):
            reset_game_state()
            st.rerun()



def get_epilogue_aftermath_lines() -> List[str]:
    """Build ending aftermath details from key flags, events, and trait outcomes."""
    flags = st.session_state.flags
    traits = st.session_state.traits
    lines: List[str] = []

    if flags.get("final_plan_shared"):
        lines.append("Your final pre-assault briefing becomes standard doctrine for Oakrest's defenders.")
    if flags.get("charged_finale"):
        lines.append("Bards celebrate your ferocity, while elders debate the cost of your methods.")

    if flags.get("morality") == "merciful" or flags.get("mercy_reputation"):
        lines.append("Families you protected petition Elder Mara to create a standing refuge network.")
    if flags.get("morality") == "ruthless" or flags.get("cruel_reputation"):
        lines.append("Several border hamlets accept your protection, but only behind locked doors and wary silence.")

    if flags.get("tunnel_collapsed"):
        lines.append("Stone crews spend weeks clearing the sealed tunnel, searching for those trapped by your command.")
    if flags.get("rescued_prisoners"):
        lines.append("Former captives rebuild the valley road and openly credit your intervention.")

    if traits.get("trust", 0) >= 4:
        lines.append("High trust earned you a seat at future war councils, not just a hero's farewell.")
    elif traits.get("trust", 0) <= -2:
        lines.append("Low trust leaves your victories unquestioned, but your motives quietly contested.")

    if traits.get("reputation", 0) >= 5:
        lines.append("Your reputation draws recruits from distant holds, reshaping Oakrest's standing in the region.")

    factions = st.session_state.factions
    if factions.get("dawnwardens", 0) >= 2:
        lines.append("Dawnwarden captains keep a signal fire lit in your honor, promising future mutual defense.")
    if factions.get("ashfang", 0) >= 2:
        lines.append("Ashfang envoys accept a tense truce, naming you as the only outsider they'll parley with.")
    if factions.get("bandits", 0) <= -2:
        lines.append("Bandit crews fracture after your campaign, and river raids drop through the next season.")
    if traits.get("alignment", 0) >= 3:
        lines.append("Your restraint becomes the measure younger scouts are taught to emulate.")
    elif traits.get("alignment", 0) <= -3:
        lines.append("Your brutal efficiency ends the immediate threat, but hardens future conflicts across the frontier.")

    return lines[:5]


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

    st.markdown(f"### 🧭 {node['title']}")
    with st.container(border=True):
        st.write(node["text"])

    if st.session_state.last_choice_feedback:
        with st.container(border=True):
            st.caption("Outcome recap")
            for line in st.session_state.last_choice_feedback[:5]:
                st.write(f"- {line}")

    dialogue = node.get("dialogue", [])
    if dialogue:
        with st.container(border=True):
            st.caption("Dialogue")
            for line in dialogue:
                speaker = line.get("speaker", "Unknown")
                quote = line.get("line", "")
                st.markdown(f"**{speaker}:** _\"{quote}\"_")

    # Death can happen from previous choice effects.
    if st.session_state.stats["hp"] <= 0:
        transition_to_failure("injured")
        st.rerun()
        return

    choices = node.get("choices", [])
    available_choices = get_available_choices(node)

    if not choices:
        st.success("The story has reached an ending. Restart to explore another path.")
        if node_id.startswith("ending_"):
            aftermath = get_epilogue_aftermath_lines()
            if aftermath:
                with st.container(border=True):
                    st.subheader("Epilogue Aftermath")
                    for detail in aftermath:
                        st.write(f"- {detail}")
        return

    st.subheader("🎮 What do you do?")
    st.toggle("Show locked choices", key="show_locked_choices", help="Toggle off to hide paths you cannot currently take.")
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

    if st.session_state.show_locked_choices:
        locked_choices: List[tuple[Dict[str, Any], str]] = []
        for choice in choices:
            ok, reason = check_requirements(choice.get("requirements"))
            if not ok:
                locked_choices.append((choice, reason))

        if locked_choices:
            with st.expander("Locked paths", expanded=False):
                for choice, reason in locked_choices:
                    st.write(f"- **{choice['label']}** — _{reason}_")

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
    if effects.get("faction_delta"):
        shifts = ", ".join([f"{name} {('+' if delta >= 0 else '')}{delta}" for name, delta in effects["faction_delta"].items()])
        details.append(f"Faction shifts: {shifts}")
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
    st.subheader("Debug & Choice Outcomes")
    st.caption("Inspect branching logic quickly from one place.")
    show_full_spoilers = st.toggle(
        "Show spoiler-heavy routing details",
        key="spoiler_debug_mode",
        help="Debug mode reveals routing destinations and full branch structure.",
    )
    node_filter = st.text_input("Filter by node title or ID", value="", placeholder="e.g. crossroad, final_confrontation")
    if show_full_spoilers:
        st.caption("Spoilers enabled: next-node IDs are visible for every choice.")
    else:
        st.caption("Spoilers reduced: requirements and outcomes are shown, but routing IDs are hidden.")

    for node_id, node in STORY_NODES.items():
        choices = node.get("choices", [])
        if not choices:
            continue
        filter_value = node_filter.strip().lower()
        if filter_value and filter_value not in node_id.lower() and filter_value not in node["title"].lower():
            continue

        with st.expander(f"{node['title']} ({node_id})", expanded=False):
            for idx, choice in enumerate(choices, start=1):
                st.markdown(f"**{idx}. {choice['label']}**")
                st.write(f"- **Requirements:** {format_requirements(choice.get('requirements'))}")
                st.write(f"- **Outcome:** {format_outcomes(choice.get('effects'))}")
                if show_full_spoilers:
                    st.write(f"- **Next node:** `{choice['next']}`")
                st.write("---")
