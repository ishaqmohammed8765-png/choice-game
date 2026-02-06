from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import FACTION_KEYS, HIGH_COST_GOLD_LOSS, HIGH_COST_HP_LOSS, STAT_KEYS, STORY_NODES, TRAIT_KEYS
from game.state import add_log, snapshot_state
from game.validation import validate_story_nodes

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
    summary = apply_effects(resolved_effects, label=label)
    st.session_state.last_outcome_summary = summary
    if summary:
        add_log(f"Recent changes: {format_outcome_summary(summary)}")
    actual_next = _resolve_transition_node(resolved_next, choice.get("instant_death", False))
    _record_visit(node_id, actual_next)
    if choice.get("irreversible"):
        st.session_state.history = []
        add_log("This decision is irreversible. You cannot undo beyond this point.")

    if choice.get("instant_death"):
        st.session_state.current_node = "death"
        add_log("This choice proves fatal. Your journey ends immediately.")
        return

    transition_to(actual_next)


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
    meta_state = st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})
    unlocked_meta_items = meta_state.get("unlocked_items", [])
    removed_meta_nodes = meta_state.get("removed_nodes", [])

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

    for item in requirements.get("meta_items", []):
        if item not in unlocked_meta_items:
            return False, f"Requires legacy item unlocked: {item}"

    for item in requirements.get("meta_missing_items", []):
        if item in unlocked_meta_items:
            return False, f"Legacy item already unlocked: {item}"

    for node_id in requirements.get("meta_nodes_present", []):
        if node_id in removed_meta_nodes:
            return False, "That legacy site has already vanished."

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

    if incoming.get("unlock_meta_items"):
        merged.setdefault("unlock_meta_items", [])
        merged["unlock_meta_items"] = list({*merged["unlock_meta_items"], *incoming["unlock_meta_items"]})

    if incoming.get("remove_meta_nodes"):
        merged.setdefault("remove_meta_nodes", [])
        merged["remove_meta_nodes"] = list({*merged["remove_meta_nodes"], *incoming["remove_meta_nodes"]})

    if "log" in incoming:
        merged["log"] = incoming["log"]

    return merged


def apply_effects(effects: Dict[str, Any] | None, *, label: str | None = None) -> Dict[str, Any]:
    """Apply deterministic choice outcomes to player state."""
    if not effects:
        return {}

    stats = st.session_state.stats
    inventory = st.session_state.inventory
    flags = st.session_state.flags
    traits = st.session_state.traits
    factions = st.session_state.factions
    meta_state = st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})
    feedback: List[str] = []
    before_stats = dict(stats)
    before_inventory = list(inventory)
    before_flags = dict(flags)

    for stat in STAT_KEYS:
        if stat in effects:
            stats[stat] += effects[stat]

    if stats["gold"] < 0:
        stats["gold"] = 0

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

    for item in effects.get("unlock_meta_items", []):
        if item not in meta_state["unlocked_items"]:
            meta_state["unlocked_items"].append(item)
            feedback.append(f"Legacy item unlocked: {item}")

    for node_id in effects.get("remove_meta_nodes", []):
        if node_id not in meta_state["removed_nodes"]:
            meta_state["removed_nodes"].append(node_id)

    apply_morality_flags(flags)

    if effects.get("log"):
        add_log(effects["log"])

    st.session_state.last_choice_feedback = feedback
    return _build_outcome_summary(
        before_stats=before_stats,
        before_inventory=before_inventory,
        before_flags=before_flags,
        label=label,
        effects=effects,
    )


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


def _resolve_transition_node(next_node_id: str, instant_death: bool) -> str:
    if instant_death:
        return "death"
    if st.session_state.stats["hp"] <= 0:
        return "death"
    if next_node_id not in STORY_NODES:
        return "failure_captured" if "failure_captured" in STORY_NODES else "death"
    return next_node_id


def _record_visit(from_node: str, to_node: str) -> None:
    visited_nodes = st.session_state.visited_nodes
    visited_edges = st.session_state.visited_edges
    if from_node not in visited_nodes:
        visited_nodes.append(from_node)
    if to_node not in visited_nodes:
        visited_nodes.append(to_node)
    edge = {"from": from_node, "to": to_node}
    if edge not in visited_edges:
        visited_edges.append(edge)


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
    summaries: List[Dict[str, Any]] = []
    death_triggered = False
    for idx, choice in enumerate(node.get("auto_choices", [])):
        marker = f"auto_choice::{node_id}::{idx}"
        if st.session_state.flags.get(marker):
            continue
        is_valid, _ = check_requirements(choice.get("requirements"))
        if not is_valid:
            continue
        effects, _ = resolve_choice_outcome(choice)
        label = choice.get("label") or "Auto event"
        summary = apply_effects(effects, label=label)
        if summary:
            summaries.append(summary)
            add_log(f"Auto event ({label}): {format_outcome_summary(summary)}")
        st.session_state.flags[marker] = True
        applied_any = True
        if st.session_state.stats["hp"] <= 0:
            death_triggered = True
            break
    if summaries:
        st.session_state.auto_event_summary = summaries
    if death_triggered:
        st.session_state.pending_auto_death = True
    return applied_any


def _is_public_flag(flag_name: str) -> bool:
    internal_prefixes = ("auto_choice::", "branch_", "system_", "internal_", "visited_")
    if flag_name == "any_branch_completed":
        return False
    return not flag_name.startswith(internal_prefixes)


def _build_outcome_summary(
    *,
    before_stats: Dict[str, int],
    before_inventory: List[str],
    before_flags: Dict[str, Any],
    label: str | None,
    effects: Dict[str, Any],
) -> Dict[str, Any]:
    after_stats = st.session_state.stats
    after_inventory = st.session_state.inventory
    after_flags = st.session_state.flags

    stats_delta = {stat: after_stats[stat] - before_stats.get(stat, 0) for stat in STAT_KEYS}
    items_gained = [item for item in after_inventory if item not in before_inventory]
    items_lost = [item for item in before_inventory if item not in after_inventory]
    flags_set: List[tuple[str, Any]] = []
    for flag_name in effects.get("set_flags", {}):
        if _is_public_flag(flag_name):
            flags_set.append((flag_name, after_flags.get(flag_name)))
    return {
        "label": label,
        "stats_delta": stats_delta,
        "items_gained": items_gained,
        "items_lost": items_lost,
        "flags_set": flags_set,
    }


def format_outcome_summary(summary: Dict[str, Any]) -> str:
    """Build a compact summary string for logging."""
    if not summary:
        return "No immediate changes."
    pieces: List[str] = []
    for stat in STAT_KEYS:
        delta = summary.get("stats_delta", {}).get(stat, 0)
        if delta:
            sign = "+" if delta > 0 else ""
            pieces.append(f"{stat.upper()} {sign}{delta}")
    items_gained = summary.get("items_gained", [])
    items_lost = summary.get("items_lost", [])
    flags_set = summary.get("flags_set", [])
    if items_gained:
        pieces.append(f"Gained: {', '.join(items_gained)}")
    if items_lost:
        pieces.append(f"Lost: {', '.join(items_lost)}")
    if flags_set:
        formatted_flags = ", ".join(f"{name}={value}" for name, value in flags_set)
        pieces.append(f"Flags: {formatted_flags}")
    return "; ".join(pieces) if pieces else "No immediate changes."
