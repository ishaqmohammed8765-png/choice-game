from __future__ import annotations

from typing import Any, Dict, List

from game.engine.state import GameState


# Stat/trait requirement specs: (requirement_key, value_key, label)
# "min" checks: current < required  →  fail
# "max" checks: current > required  →  fail
_MIN_REQUIREMENT_CHECKS: List[tuple[str, str, str]] = [
    ("min_hp", "hp", "HP"),
    ("min_gold", "gold", "gold"),
    ("min_strength", "strength", "strength"),
    ("min_dexterity", "dexterity", "dexterity"),
]

_TRAIT_RANGE_CHECKS: List[tuple[str, str, str, str]] = [
    # (requirement_key, trait_key, label, direction)
    ("min_reputation", "reputation", "reputation", "min"),
    ("max_reputation", "reputation", "reputation", "max"),
    ("min_ember_tide", "ember_tide", "ember tide", "min"),
    ("max_ember_tide", "ember_tide", "ember tide", "max"),
]

_SUMMARY_STAT_SPECS: List[tuple[str, str, str]] = [
    ("min_hp", "HP", ""),
    ("min_gold", "Gold", ""),
    ("min_strength", "Strength", ""),
    ("min_dexterity", "Dexterity", ""),
    ("min_reputation", "Reputation", ">="),
    ("max_reputation", "Reputation", "<="),
    ("min_ember_tide", "Ember Tide", ">="),
    ("max_ember_tide", "Ember Tide", "<="),
]


def check_requirements(requirements: Dict[str, Any] | None, state: GameState) -> tuple[bool, str]:
    """Validate requirements against an immutable game-state snapshot."""
    if not requirements:
        return True, ""

    if "any_of" in requirements:
        failed_details: List[str] = []
        for index, option in enumerate(requirements["any_of"], start=1):
            ok, reason = check_requirements(option, state)
            if ok:
                return True, ""
            summary = _summarize_requirements(option)
            # Prefer the most specific reason we have; fall back to summary.
            detail = reason or summary or "unspecified condition"
            if summary and reason and reason != summary:
                detail = f"{summary} ({reason})"
            failed_details.append(f"{index}) {detail}")
        return False, "Requires one of: " + " | ".join(failed_details)

    stats = state.stats
    inventory = state.inventory
    flags = state.flags
    traits = state.traits
    pclass = state.player_class
    unlocked_meta_items = state.meta_state.get("unlocked_items", [])
    removed_meta_nodes = state.meta_state.get("removed_nodes", [])

    if "class" in requirements and pclass not in requirements["class"]:
        return False, f"Requires class: {', '.join(requirements['class'])}"

    for req_key, stat_key, label in _MIN_REQUIREMENT_CHECKS:
        if req_key in requirements and stats.get(stat_key, 0) < requirements[req_key]:
            return False, f"Requires {label} >= {requirements[req_key]}"

    for req_key, trait_key, label, direction in _TRAIT_RANGE_CHECKS:
        if req_key not in requirements:
            continue
        current = traits.get(trait_key, 0)
        threshold = requirements[req_key]
        if direction == "min" and current < threshold:
            return False, f"Requires {label} >= {threshold}"
        if direction == "max" and current > threshold:
            return False, f"Requires {label} <= {threshold}"

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


def _summarize_requirements(requirements: Dict[str, Any] | None) -> str:
    if not requirements:
        return ""

    if "any_of" in requirements:
        return " or ".join(
            summary for summary in (_summarize_requirements(option) for option in requirements["any_of"]) if summary
        )

    parts: List[str] = []
    if "class" in requirements:
        parts.append(f"Class {', '.join(requirements['class'])}")

    for key, label, op in _SUMMARY_STAT_SPECS:
        if key in requirements:
            sep = f" {op} " if op else " "
            parts.append(f"{label}{sep}{requirements[key]}")

    for item in requirements.get("items", []):
        parts.append(item)
    for item in requirements.get("missing_items", []):
        parts.append(f"Without {item}")

    for flag in requirements.get("flag_true", []):
        parts.append(_humanize_flag(flag))
    for flag in requirements.get("flag_false", []):
        parts.append(f"Not {_humanize_flag(flag)}")

    for item in requirements.get("meta_items", []):
        parts.append(f"{item} (legacy)")
    for item in requirements.get("meta_missing_items", []):
        parts.append(f"No {item} (legacy)")
    for node_id in requirements.get("meta_nodes_present", []):
        parts.append(f"Legacy site {node_id}")

    return " and ".join(parts)


def _humanize_flag(flag: str) -> str:
    return flag.replace("_", " ").strip().title()
