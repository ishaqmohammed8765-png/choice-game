from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import FACTION_KEYS, HIGH_COST_GOLD_LOSS, HIGH_COST_HP_LOSS, STAT_KEYS, STORY_NODES, TRAIT_KEYS
from game.state import add_log, snapshot_state

ALLOWED_REQUIREMENT_KEYS = {
    "class",
    "any_of",
    "min_hp",
    "min_gold",
    "min_strength",
    "min_dexterity",
    "items",
    "missing_items",
    "flag_true",
    "flag_false",
}

ALLOWED_EFFECT_KEYS = {
    *STAT_KEYS,
    "add_items",
    "remove_items",
    "set_flags",
    "trait_delta",
    "seen_events",
    "faction_delta",
    "log",
}

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
    resolved_effects, resolved_next = resolve_choice_outcome(choice)
    apply_effects(resolved_effects)
    if choice.get("irreversible"):
        st.session_state.history = []
        add_log("This decision is irreversible. You cannot undo beyond this point.")

    if choice.get("instant_death"):
        st.session_state.current_node = "death"
        add_log("This choice proves fatal. Your journey ends immediately.")
        return

    transition_to(resolved_next)


def get_choice_warnings(choice: Dict[str, Any]) -> List[str]:
    """Return warning messages for irreversible or high-cost choices."""
    warnings: List[str] = []
    effects, _ = resolve_choice_outcome(choice)

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

    if "any_of" in requirements:
        for option in requirements["any_of"]:
            ok, _ = check_requirements(option)
            if ok:
                return True, ""
        return False, "Requires one of multiple conditions"

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


def resolve_choice_outcome(choice: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
    """Return the effective effects and next node for a choice based on current state."""
    effects = dict(choice.get("effects", {}))
    next_node = choice.get("next")

    for variant in choice.get("conditional_effects", []):
        ok, _ = check_requirements(variant.get("requirements"))
        if not ok:
            continue
        effects = merge_effects(effects, variant.get("effects", {}))
        if variant.get("next"):
            next_node = variant["next"]
        break

    return effects, next_node


def merge_effects(base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two effect dicts deterministically, favoring incoming for log text."""
    merged = dict(base)
    for stat in STAT_KEYS:
        if stat in incoming:
            merged[stat] = merged.get(stat, 0) + incoming[stat]

    if incoming.get("add_items"):
        merged.setdefault("add_items", [])
        merged["add_items"] = list({*merged["add_items"], *incoming["add_items"]})

    if incoming.get("remove_items"):
        merged.setdefault("remove_items", [])
        merged["remove_items"] = list({*merged["remove_items"], *incoming["remove_items"]})

    if incoming.get("set_flags"):
        merged.setdefault("set_flags", {})
        merged["set_flags"].update(incoming["set_flags"])

    if incoming.get("trait_delta"):
        merged.setdefault("trait_delta", {})
        for trait, delta in incoming["trait_delta"].items():
            merged["trait_delta"][trait] = merged["trait_delta"].get(trait, 0) + delta

    if incoming.get("faction_delta"):
        merged.setdefault("faction_delta", {})
        for faction, delta in incoming["faction_delta"].items():
            merged["faction_delta"][faction] = merged["faction_delta"].get(faction, 0) + delta

    if incoming.get("seen_events"):
        merged.setdefault("seen_events", [])
        merged["seen_events"] = list({*merged["seen_events"], *incoming["seen_events"]})

    if "log" in incoming:
        merged["log"] = incoming["log"]

    return merged


def apply_effects(effects: Dict[str, Any] | None) -> None:
    """Apply deterministic choice outcomes to player state."""
    if not effects:
        return

    stats = st.session_state.stats
    inventory = st.session_state.inventory
    flags = st.session_state.flags
    traits = st.session_state.traits
    factions = st.session_state.factions
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

    completed_branches = [
        flag_name
        for flag_name, is_done in flags.items()
        if flag_name.startswith("branch_") and flag_name.endswith("_completed") and is_done
    ]
    if completed_branches:
        flags["any_branch_completed"] = True

    for trait, delta in effects.get("trait_delta", {}).items():
        if trait in traits:
            traits[trait] += delta
            sign = "+" if delta >= 0 else ""
            feedback.append(f"Trait shift: {trait} {sign}{delta}")

    for faction, delta in effects.get("faction_delta", {}).items():
        if faction in factions:
            factions[faction] += delta
            sign = "+" if delta >= 0 else ""
            feedback.append(f"Faction shift: {faction} {sign}{delta}")

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
        st.session_state.current_node = "death"
        add_log("You collapse from your wounds. Your journey ends here.")
        return

    if next_node_id not in STORY_NODES:
        transition_to_failure("captured")
        add_log(f"Broken path detected for '{next_node_id}'. You are rerouted to a fallback failure arc.")
        return

    st.session_state.current_node = next_node_id


def validate_story_nodes() -> List[str]:
    """Run static validation over story structure, links, and choice schemas."""
    warnings: List[str] = []
    for node_id, node in STORY_NODES.items():
        if node.get("id") != node_id:
            warnings.append(f"Node key '{node_id}' does not match its id field '{node.get('id')}'.")

        for idx, choice in enumerate(node.get("choices", []), start=1):
            label = choice.get("label", f"unnamed-{idx}")
            next_id = choice.get("next")
            if next_id not in STORY_NODES:
                warnings.append(f"Choice '{label}' in node '{node_id}' points to missing node '{next_id}'.")

            requirements = choice.get("requirements", {})
            if "any_of" in requirements:
                for option in requirements["any_of"]:
                    unknown_any_of = sorted(set(option) - ALLOWED_REQUIREMENT_KEYS)
                    if unknown_any_of:
                        warnings.append(
                            f"Choice '{label}' in node '{node_id}' has unknown requirement keys: {', '.join(unknown_any_of)}."
                        )
            unknown_req_keys = sorted(set(requirements) - ALLOWED_REQUIREMENT_KEYS)
            if unknown_req_keys:
                warnings.append(
                    f"Choice '{label}' in node '{node_id}' has unknown requirement keys: {', '.join(unknown_req_keys)}."
                )

            effects = choice.get("effects", {})
            unknown_effect_keys = sorted(set(effects) - ALLOWED_EFFECT_KEYS)
            if unknown_effect_keys:
                warnings.append(
                    f"Choice '{label}' in node '{node_id}' has unknown effect keys: {', '.join(unknown_effect_keys)}."
                )

            if "trait_delta" in effects:
                unknown_traits = sorted(set(effects["trait_delta"]) - set(TRAIT_KEYS))
                if unknown_traits:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' uses unknown traits in trait_delta: {', '.join(unknown_traits)}."
                    )

            if "faction_delta" in effects:
                unknown_factions = sorted(set(effects["faction_delta"]) - set(FACTION_KEYS))
                if unknown_factions:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' uses unknown factions in faction_delta: {', '.join(unknown_factions)}."
                    )

            for variant in choice.get("conditional_effects", []):
                variant_req = variant.get("requirements", {})
                if "any_of" in variant_req:
                    for option in variant_req["any_of"]:
                        unknown_any_of = sorted(set(option) - ALLOWED_REQUIREMENT_KEYS)
                        if unknown_any_of:
                            warnings.append(
                                f"Choice '{label}' in node '{node_id}' has unknown requirement keys: {', '.join(unknown_any_of)}."
                            )
                unknown_variant_req = sorted(set(variant_req) - ALLOWED_REQUIREMENT_KEYS)
                if unknown_variant_req:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' has unknown requirement keys: {', '.join(unknown_variant_req)}."
                    )
                variant_effects = variant.get("effects", {})
                unknown_variant_effects = sorted(set(variant_effects) - ALLOWED_EFFECT_KEYS)
                if unknown_variant_effects:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' has unknown effect keys: {', '.join(unknown_variant_effects)}."
                    )
                if "next" in variant and variant["next"] not in STORY_NODES:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' has conditional next pointing to missing node '{variant['next']}'."
                    )

            if "class" in requirements and not requirements["class"]:
                warnings.append(f"Choice '{label}' in node '{node_id}' has empty class requirements list.")

    return warnings


def get_available_choices(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return choices that pass requirements for display and interaction."""
    valid_choices = []
    for choice in node.get("choices", []):
        is_valid, _ = check_requirements(choice.get("requirements"))
        if is_valid:
            valid_choices.append(choice)
    return valid_choices


def apply_node_auto_choices(node_id: str, node: Dict[str, Any]) -> bool:
    """Apply auto-choices once when entering a node. Returns True if any auto choice applied."""
    applied_any = False
    for idx, choice in enumerate(node.get("auto_choices", [])):
        marker = f"auto_choice::{node_id}::{idx}"
        if st.session_state.flags.get(marker):
            continue
        is_valid, _ = check_requirements(choice.get("requirements"))
        if not is_valid:
            continue
        effects, _ = resolve_choice_outcome(choice)
        apply_effects(effects)
        st.session_state.flags[marker] = True
        applied_any = True
    return applied_any
