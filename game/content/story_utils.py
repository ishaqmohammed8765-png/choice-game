from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

from game.content.constants import MAX_CHOICES_PER_NODE


def simplify_story_nodes(
    story_nodes: Dict[str, Dict[str, Any]],
) -> tuple[Dict[str, Dict[str, Any]], List[str]]:
    """Return a simplified copy of the story graph plus a human-readable report.

    This function is intentionally pure: it never mutates the input mapping.
    """
    report: List[str] = []
    simplified_nodes: Dict[str, Dict[str, Any]] = copy.deepcopy(story_nodes)

    def freeze(value: Any) -> Any:
        if isinstance(value, dict):
            return tuple((key, freeze(value[key])) for key in sorted(value))
        if isinstance(value, list):
            return tuple(freeze(item) for item in value)
        return value

    def is_low_impact(choice: Dict[str, Any]) -> bool:
        effects = choice.get("effects", {})
        return set(effects.keys()) <= {"log"} and not choice.get("conditional_effects")

    for node_id, node in simplified_nodes.items():
        choices = list(node.get("choices", []))
        auto_choices: List[Dict[str, Any]] = []
        keep: List[Dict[str, Any]] = []

        for choice in choices:
            if choice.get("auto_apply"):
                auto_choice = dict(choice)
                auto_choice.pop("auto_apply", None)
                auto_choices.append(auto_choice)
                report.append(f"{node_id}: auto-applied '{choice.get('label', 'unnamed choice')}'")
                continue
            keep.append(choice)

        if auto_choices:
            node["auto_choices"] = auto_choices

        deduped: List[Dict[str, Any]] = []
        seen: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
        for choice in keep:
            key = (
                choice.get("next"),
                freeze(choice.get("requirements", {})),
                freeze(choice.get("effects", {})),
                freeze(choice.get("conditional_effects", [])),
            )
            if key in seen:
                report.append(f"{node_id}: removed duplicate '{choice.get('label', 'unnamed choice')}'")
                continue
            seen[key] = choice
            deduped.append(choice)

        if len(deduped) > MAX_CHOICES_PER_NODE:
            destination_counts: Dict[str | None, int] = {}
            for choice in deduped:
                destination_counts[choice.get("next")] = destination_counts.get(choice.get("next"), 0) + 1
            for destination, count in destination_counts.items():
                if count > 1:
                    report.append(f"{node_id}: {count} choices lead to '{destination}' (groupable destination)")

            low_impact = [choice for choice in deduped if is_low_impact(choice)]
            while len(deduped) > MAX_CHOICES_PER_NODE and low_impact:
                removed = low_impact.pop(0)
                deduped.remove(removed)
                report.append(f"{node_id}: pruned low-impact '{removed.get('label', 'unnamed choice')}'")

        node["choices"] = deduped

    return simplified_nodes, report

