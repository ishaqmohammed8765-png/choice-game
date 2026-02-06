from __future__ import annotations

from typing import Any, Dict, List

from game.content.constants import CHOICE_SIMPLIFICATION_REPORT, MAX_CHOICES_PER_NODE


def simplify_story_nodes(story_nodes: Dict[str, Dict[str, Any]]) -> None:
    """Simplify choices by staging auto-applied outcomes and pruning duplicates."""

    def freeze(value: Any) -> Any:
        if isinstance(value, dict):
            return tuple((key, freeze(value[key])) for key in sorted(value))
        if isinstance(value, list):
            return tuple(freeze(item) for item in value)
        return value

    def is_low_impact(choice: Dict[str, Any]) -> bool:
        effects = choice.get("effects", {})
        return set(effects.keys()) <= {"log"} and not choice.get("conditional_effects")

    for node_id, node in story_nodes.items():
        choices = list(node.get("choices", []))
        auto_choices: List[Dict[str, Any]] = []
        simplified: List[Dict[str, Any]] = []

        for choice in choices:
            if choice.get("auto_apply"):
                auto_choice = dict(choice)
                auto_choice.pop("auto_apply", None)
                auto_choices.append(auto_choice)
                CHOICE_SIMPLIFICATION_REPORT.append(
                    f"{node_id}: auto-applied '{choice.get('label', 'unnamed choice')}'"
                )
                continue
            simplified.append(choice)

        if auto_choices:
            node["auto_choices"] = auto_choices

        deduped: List[Dict[str, Any]] = []
        seen: Dict[Any, Dict[str, Any]] = {}
        for choice in simplified:
            key = (
                choice.get("next"),
                freeze(choice.get("requirements", {})),
                freeze(choice.get("effects", {})),
                freeze(choice.get("conditional_effects", [])),
            )
            if key in seen:
                CHOICE_SIMPLIFICATION_REPORT.append(
                    f"{node_id}: removed duplicate '{choice.get('label', 'unnamed choice')}'"
                )
                continue
            seen[key] = choice
            deduped.append(choice)

        if len(deduped) > MAX_CHOICES_PER_NODE:
            low_impact = [choice for choice in deduped if is_low_impact(choice)]
            while len(deduped) > MAX_CHOICES_PER_NODE and low_impact:
                removed = low_impact.pop(0)
                deduped.remove(removed)
                CHOICE_SIMPLIFICATION_REPORT.append(
                    f"{node_id}: pruned low-impact '{removed.get('label', 'unnamed choice')}'"
                )

        node["choices"] = deduped
