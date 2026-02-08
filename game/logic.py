from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import FACTION_KEYS, HIGH_COST_GOLD_LOSS, HIGH_COST_HP_LOSS, STAT_KEYS, STORY_NODES, TRAIT_KEYS
from game.content.surprise_events import SURPRISE_EVENTS
from game.engine.requirements import check_requirements as check_requirements_engine
from game.engine.state import state_from_session
from game.engine.state_machine import evaluate_transition, get_phase
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
    """Apply a selected choice and transition to its next node.

    Uses the state machine to evaluate transitions, applying rules for
    HP death, missing nodes, phase-specific logic, and cross-cutting concerns.
    """
    st.session_state.pending_choice_confirmation = None
    st.session_state.history.append(snapshot_state())
    st.session_state.decision_history.append({"node": node_id, "choice": label})
    resolved_effects, resolved_next = resolve_choice_outcome(choice)
    summary = apply_effects(resolved_effects, label=label)
    st.session_state.last_outcome_summary = summary
    if summary:
        add_log(f"Recent changes: {format_outcome_summary(summary)}")

    if choice.get("irreversible"):
        st.session_state.history = []
        add_log("This decision is irreversible. You cannot undo beyond this point.")

    if choice.get("instant_death"):
        _record_visit(node_id, "death")
        st.session_state.current_node = "death"
        add_log("This choice proves fatal. Your journey ends immediately.")
        return

    # Evaluate transition through the state machine
    sm_result = evaluate_transition(node_id, resolved_next, label, st.session_state)

    # Apply any extra effects from state machine rules
    if sm_result.extra_effects:
        apply_effects(sm_result.extra_effects, label="(state machine)", trigger_surprises=False)

    # Determine actual destination
    actual_next = sm_result.redirect_to or resolved_next
    # Fallback safety check
    actual_next = _resolve_transition_node(actual_next)

    _record_visit(node_id, actual_next)

    if sm_result.log_message:
        add_log(sm_result.log_message)
    elif actual_next == "death" and resolved_next != "death":
        add_log("You collapse from your wounds. Your journey ends here.")
    elif actual_next != resolved_next:
        add_log(f"Broken path detected for '{resolved_next}'. You are rerouted to a fallback failure arc.")

    st.session_state.current_node = actual_next
    st.session_state.current_phase = get_phase(actual_next)


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
    return check_requirements_engine(requirements, state_from_session(st.session_state))


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


# Keys in effects that are deduplicated lists when merging
_MERGE_LIST_KEYS = ("add_items", "remove_items", "seen_events", "unlock_meta_items", "remove_meta_nodes")

# Keys in effects that are additive dicts when merging
_MERGE_ADDITIVE_DICT_KEYS = ("trait_delta", "faction_delta")


def merge_effects(base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two effect dicts deterministically, favoring incoming for log text."""
    merged = dict(base)
    for stat in STAT_KEYS:
        if stat in incoming:
            merged[stat] = merged.get(stat, 0) + incoming[stat]

    for key in _MERGE_LIST_KEYS:
        if incoming.get(key):
            merged.setdefault(key, [])
            merged[key] = list({*merged[key], *incoming[key]})

    if incoming.get("set_flags"):
        merged.setdefault("set_flags", {})
        merged["set_flags"].update(incoming["set_flags"])

    for key in _MERGE_ADDITIVE_DICT_KEYS:
        if incoming.get(key):
            merged.setdefault(key, {})
            for name, delta in incoming[key].items():
                merged[key][name] = merged[key].get(name, 0) + delta

    if "log" in incoming:
        merged["log"] = incoming["log"]

    return merged


def apply_effects(
    effects: Dict[str, Any] | None,
    *,
    label: str | None = None,
    trigger_surprises: bool = True,
) -> Dict[str, Any]:
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

    if trigger_surprises:
        if "auto_event_summary" not in st.session_state:
            st.session_state.auto_event_summary = []
        surprise_summaries = _apply_surprise_events()
        if surprise_summaries:
            st.session_state.auto_event_summary.extend(surprise_summaries)

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


def _apply_surprise_events() -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    reputation = st.session_state.traits.get("reputation", 0)
    ember_tide = st.session_state.traits.get("ember_tide", 0)
    for event in SURPRISE_EVENTS:
        if event["id"] in st.session_state.seen_events:
            continue
        min_rep = event.get("min_reputation")
        max_rep = event.get("max_reputation")
        if min_rep is not None and reputation < min_rep:
            continue
        if max_rep is not None and reputation > max_rep:
            continue
        min_et = event.get("min_ember_tide")
        max_et = event.get("max_ember_tide")
        if min_et is not None and ember_tide < min_et:
            continue
        if max_et is not None and ember_tide > max_et:
            continue
        event_effects = dict(event["effects"])
        seen_events = list(event_effects.get("seen_events", []))
        seen_events.append(event["id"])
        event_effects["seen_events"] = seen_events
        summary = apply_effects(event_effects, label=event["label"], trigger_surprises=False)
        if summary:
            summaries.append(summary)
            add_log(f"Surprise event ({event['label']}): {format_outcome_summary(summary)}")
        else:
            add_log(f"Surprise event ({event['label']}): {event_effects.get('log', 'An unexpected turn unfolds.')}")
    return summaries


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


def _resolve_transition_node(next_node_id: str) -> str:
    """Determine the actual destination node, falling back for missing nodes or death."""
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

    stats_delta = {
        stat: delta
        for stat in STAT_KEYS
        if (delta := after_stats[stat] - before_stats.get(stat, 0)) != 0
    }
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
