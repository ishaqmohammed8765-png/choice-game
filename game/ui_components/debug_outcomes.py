from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import STAT_KEYS, STORY_NODES


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
