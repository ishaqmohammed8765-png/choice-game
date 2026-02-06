from typing import Any, Dict, List

import streamlit as st

from game.data import HIGH_COST_GOLD_LOSS, HIGH_COST_HP_LOSS, STAT_KEYS, STORY_NODES
from game.state import add_log, snapshot_state


def transition_to_failure(failure_type: str) -> None:
    """Send the player to a recoverable failure node instead of ending the run."""
    failure_nodes = {
        "injured": "failure_injured",
        "captured": "failure_captured",
        "traitor": "failure_traitor",
        "resource_loss": "failure_resource_loss",
    }
    failure_logs = {
        "injured": "You are gravely injured, but not out of the fight yet.",
        "captured": "You are captured alive and must now escape.",
        "traitor": "Word spreads that you are branded a traitor. You need to reclaim trust.",
        "resource_loss": "Setbacks cost you gear and allies, but the mission continues.",
    }

    next_node = failure_nodes.get(failure_type, "failure_injured")
    if next_node not in STORY_NODES:
        next_node = "death"

    st.session_state.current_node = next_node
    add_log(failure_logs.get(failure_type, failure_logs["injured"]))


def execute_choice(node_id: str, label: str, choice: Dict[str, Any]) -> None:
    """Apply a selected choice and transition to its next node."""
    st.session_state.pending_choice_confirmation = None
    st.session_state.history.append(snapshot_state())
    st.session_state.decision_history.append({"node": node_id, "choice": label})
    apply_effects(choice.get("effects"))
    if choice.get("irreversible"):
        st.session_state.history = []
        add_log("This decision is irreversible. You cannot undo beyond this point.")

    if choice.get("instant_death"):
        st.session_state.current_node = "death"
        add_log("This choice proves fatal. Your journey ends immediately.")
        return

    transition_to(choice["next"])


def get_choice_warnings(choice: Dict[str, Any]) -> List[str]:
    """Return warning messages for irreversible or high-cost choices."""
    warnings: List[str] = []
    effects = choice.get("effects", {})

    if choice.get("irreversible"):
        warnings.append("Irreversible choice: this clears undo history once confirmed.")
    if choice.get("instant_death"):
        warnings.append("Lethal outcome: this choice causes immediate death.")
    if effects.get("hp", 0) <= -HIGH_COST_HP_LOSS:
        warnings.append(f"High HP cost: {effects['hp']} HP")
    if effects.get("gold", 0) <= -HIGH_COST_GOLD_LOSS:
        warnings.append(f"High gold cost: {effects['gold']} gold")

    return warnings


def apply_morality_flags(flags: Dict[str, Any]) -> None:
    """Keep legacy reputation flags in sync with canonical morality value."""
    morality = flags.get("morality")
    if morality == "merciful":
        flags["mercy_reputation"] = True
        flags["cruel_reputation"] = False
    elif morality == "ruthless":
        flags["mercy_reputation"] = False
        flags["cruel_reputation"] = True


def check_requirements(requirements: Dict[str, Any] | None) -> tuple[bool, str]:
    """Validate requirements against current player state."""
    if not requirements:
        return True, ""

    stats = st.session_state.stats
    inventory = st.session_state.inventory
    flags = st.session_state.flags
    pclass = st.session_state.player_class

    if "class" in requirements and pclass not in requirements["class"]:
        return False, f"Requires class: {', '.join(requirements['class'])}"

    if "min_hp" in requirements and stats["hp"] < requirements["min_hp"]:
        return False, f"Requires HP >= {requirements['min_hp']}"
    if "min_gold" in requirements and stats["gold"] < requirements["min_gold"]:
        return False, f"Requires gold >= {requirements['min_gold']}"
    if "min_strength" in requirements and stats["strength"] < requirements["min_strength"]:
        return False, f"Requires strength >= {requirements['min_strength']}"
    if "min_dexterity" in requirements and stats["dexterity"] < requirements["min_dexterity"]:
        return False, f"Requires dexterity >= {requirements['min_dexterity']}"

    for item in requirements.get("items", []):
        if item not in inventory:
            return False, f"Missing item: {item}"

    for item in requirements.get("missing_items", []):
        if item in inventory:
            return False, f"Already have item: {item}"

    for flag in requirements.get("flag_true", []):
        if not flags.get(flag, False):
            return False, f"Requires flag: {flag}=True"

    for flag in requirements.get("flag_false", []):
        if flags.get(flag, False):
            return False, f"Requires flag: {flag}=False"

    return True, ""


def apply_effects(effects: Dict[str, Any] | None) -> None:
    """Apply deterministic choice outcomes to player state."""
    if not effects:
        return

    stats = st.session_state.stats
    inventory = st.session_state.inventory
    flags = st.session_state.flags
    traits = st.session_state.traits
    feedback: List[str] = []

    for stat in STAT_KEYS:
        if stat in effects:
            stats[stat] += effects[stat]

    for item in effects.get("add_items", []):
        if item not in inventory:
            inventory.append(item)

    for item in effects.get("remove_items", []):
        if item in inventory:
            inventory.remove(item)

    for key, value in effects.get("set_flags", {}).items():
        flags[key] = value
        feedback.append(f"World state changed: {key} → {value}")

    for trait, delta in effects.get("trait_delta", {}).items():
        if trait in traits:
            traits[trait] += delta
            sign = "+" if delta >= 0 else ""
            feedback.append(f"Trait shift: {trait} {sign}{delta}")

    for event in effects.get("seen_events", []):
        if event not in st.session_state.seen_events:
            st.session_state.seen_events.append(event)
            feedback.append(f"Key event recorded: {event}")

    apply_morality_flags(flags)

    if effects.get("log"):
        add_log(effects["log"])

    st.session_state.last_choice_feedback = feedback


def transition_to(next_node_id: str) -> None:
    """Move to the next node, redirecting hard failures to recoverable paths."""
    if st.session_state.stats["hp"] <= 0:
        transition_to_failure("injured")
        return

    if next_node_id not in STORY_NODES:
        transition_to_failure("captured")
        add_log(f"Broken path detected for '{next_node_id}'. You are rerouted to a fallback failure arc.")
        return

    st.session_state.current_node = next_node_id


def validate_story_nodes() -> List[str]:
    """Run lightweight static validation over story graph links."""
    warnings: List[str] = []
    for node_id, node in STORY_NODES.items():
        if node.get("id") != node_id:
            warnings.append(f"Node key '{node_id}' does not match its id field '{node.get('id')}'.")

        for choice in node.get("choices", []):
            next_id = choice.get("next")
            if next_id not in STORY_NODES:
                warnings.append(
                    f"Choice '{choice.get('label', 'unnamed')}' in node '{node_id}' points to missing node '{next_id}'."
                )
    return warnings


def get_available_choices(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return choices that pass requirements for display and interaction."""
    valid_choices = []
    for choice in node.get("choices", []):
        is_valid, _ = check_requirements(choice.get("requirements"))
        if is_valid:
            valid_choices.append(choice)
    return valid_choices
