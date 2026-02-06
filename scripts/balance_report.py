from __future__ import annotations

from collections import defaultdict

from game.content import CLASS_TEMPLATES, STAT_KEYS, STORY_NODES
from game.validation import _collect_story_metadata


def _max_stats_for_class() -> dict[str, dict[str, int]]:
    max_gains = {stat: 0 for stat in STAT_KEYS}
    for node in STORY_NODES.values():
        for choice in node.get("choices", []):
            effects = choice.get("effects", {})
            for stat in STAT_KEYS:
                if stat in effects and effects[stat] > 0:
                    max_gains[stat] += effects[stat]
            for variant in choice.get("conditional_effects", []):
                variant_effects = variant.get("effects", {})
                for stat in STAT_KEYS:
                    if stat in variant_effects and variant_effects[stat] > 0:
                        max_gains[stat] += variant_effects[stat]
    return {
        class_name: {stat: template[stat] + max_gains[stat] for stat in STAT_KEYS}
        for class_name, template in CLASS_TEMPLATES.items()
    }


def _choice_possible_for_class(choice: dict, class_name: str, obtainable_items: set[str], max_stats: dict) -> bool:
    requirements = choice.get("requirements", {})
    if "class" in requirements and class_name not in requirements["class"]:
        return False
    if "min_hp" in requirements and requirements["min_hp"] > max_stats["hp"]:
        return False
    if "min_gold" in requirements and requirements["min_gold"] > max_stats["gold"]:
        return False
    if "min_strength" in requirements and requirements["min_strength"] > max_stats["strength"]:
        return False
    if "min_dexterity" in requirements and requirements["min_dexterity"] > max_stats["dexterity"]:
        return False
    for item in requirements.get("items", []):
        if item not in obtainable_items:
            return False
    return True


def main() -> None:
    _, obtainable_items = _collect_story_metadata()
    max_stats = _max_stats_for_class()

    for class_name, template in CLASS_TEMPLATES.items():
        totals = defaultdict(int)
        locked_nodes = []
        high_cost_choices = []
        for node_id, node in STORY_NODES.items():
            choices = node.get("choices", [])
            if not choices:
                continue
            possible_choices = [
                choice
                for choice in choices
                if _choice_possible_for_class(choice, class_name, obtainable_items, max_stats[class_name])
            ]
            if not possible_choices:
                locked_nodes.append(node_id)
            for choice in possible_choices:
                req = choice.get("requirements", {})
                if req.get("min_gold", 0) >= template["gold"] + 2:
                    high_cost_choices.append((node_id, choice.get("label", "(unnamed)")))
            totals["choices"] += len(possible_choices)
            totals["nodes"] += 1

        print("=" * 60)
        print(f"Class: {class_name}")
        print(f"Base stats: {template}")
        print(f"Estimated max stats: {max_stats[class_name]}")
        print(f"Nodes with choices evaluated: {totals['nodes']}")
        print(f"Total viable choices: {totals['choices']}")
        if locked_nodes:
            print("Locked nodes (no viable choices):")
            for node_id in locked_nodes:
                print(f"  - {node_id}")
        if high_cost_choices:
            print("High resource pressure choices (gold-heavy):")
            for node_id, label in high_cost_choices[:10]:
                print(f"  - {node_id}: {label}")
        print()


if __name__ == "__main__":
    main()
