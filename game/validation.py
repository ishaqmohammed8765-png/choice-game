from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set

from game.content import CLASS_TEMPLATES, FACTION_KEYS, STAT_KEYS, STORY_NODES, TRAIT_KEYS

ALLOWED_REQUIREMENT_KEYS = {
    "class",
    "any_of",
    "min_hp",
    "min_gold",
    "min_strength",
    "min_dexterity",
    "min_reputation",
    "max_reputation",
    "min_ember_tide",
    "max_ember_tide",
    "items",
    "missing_items",
    "flag_true",
    "flag_false",
    "meta_items",
    "meta_missing_items",
    "meta_nodes_present",
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
    "unlock_meta_items",
    "remove_meta_nodes",
}

SYSTEM_FLAG_KEYS = {"class", "any_branch_completed"}
INTRO_NODE_PREFIX = "intro_"


def _iter_all_choices(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(node.get("choices", [])) + list(node.get("auto_choices", []))


def _collect_story_metadata() -> tuple[set[str], set[str]]:
    """Collect known flags and obtainable items."""
    known_flags = set(SYSTEM_FLAG_KEYS)
    obtainable_items: set[str] = set()

    for template in CLASS_TEMPLATES.values():
        for item in template.get("inventory", []):
            obtainable_items.add(item)

    for node in STORY_NODES.values():
        for choice in _iter_all_choices(node):
            effects = choice.get("effects", {})
            obtainable_items.update(effects.get("add_items", []))
            if effects.get("set_flags"):
                known_flags.update(effects["set_flags"].keys())

            for variant in choice.get("conditional_effects", []):
                variant_effects = variant.get("effects", {})
                obtainable_items.update(variant_effects.get("add_items", []))
                if variant_effects.get("set_flags"):
                    known_flags.update(variant_effects["set_flags"].keys())

    return known_flags, obtainable_items


def _possible_stat_caps() -> dict[str, dict[str, int]]:
    """Compute per-class maximum possible stat gains, respecting class-gated choices."""
    known_classes = set(CLASS_TEMPLATES.keys())
    max_gains: dict[str, dict[str, int]] = {
        cls: {stat: 0 for stat in STAT_KEYS} for cls in known_classes
    }
    for node in STORY_NODES.values():
        for choice in _iter_all_choices(node):
            req_classes = choice.get("requirements", {}).get("class")
            eligible = set(req_classes) & known_classes if req_classes else known_classes
            effects = choice.get("effects", {})
            for stat in STAT_KEYS:
                if stat in effects and effects[stat] > 0:
                    for cls in eligible:
                        max_gains[cls][stat] += effects[stat]
            for variant in choice.get("conditional_effects", []):
                variant_req_classes = variant.get("requirements", {}).get("class")
                variant_eligible = set(variant_req_classes) & eligible if variant_req_classes else eligible
                variant_effects = variant.get("effects", {})
                for stat in STAT_KEYS:
                    if stat in variant_effects and variant_effects[stat] > 0:
                        for cls in variant_eligible:
                            max_gains[cls][stat] += variant_effects[stat]
    return max_gains


def _max_stats_for_class() -> dict[str, dict[str, int]]:
    gains = _possible_stat_caps()
    caps: dict[str, dict[str, int]] = {}
    for class_name, template in CLASS_TEMPLATES.items():
        caps[class_name] = {stat: template[stat] + gains[class_name][stat] for stat in STAT_KEYS}
    return caps


def _node_is_terminal(node_id: str, node: Dict[str, Any]) -> bool:
    if node_id in {"death"}:
        return True
    if node_id.startswith("ending_") or node_id.startswith("failure_"):
        return True
    return not node.get("choices") and not node.get("auto_choices")


def _choice_possible_for_class(
    choice: Dict[str, Any],
    class_name: str,
    obtainable_items: Set[str],
    max_stats: Dict[str, int],
) -> bool:
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


def _any_choice_possible_for_class(
    node: Dict[str, Any],
    class_name: str,
    obtainable_items: Set[str],
    max_stats: Dict[str, int],
) -> bool:
    for choice in _iter_all_choices(node):
        if _choice_possible_for_class(choice, class_name, obtainable_items, max_stats):
            return True
    return False


def validate_story_nodes() -> List[str]:
    """Run strict validation over story structure, links, and choice schemas."""
    warnings: List[str] = []
    known_flags, obtainable_items = _collect_story_metadata()
    known_classes = set(CLASS_TEMPLATES.keys())
    max_stats = _max_stats_for_class()

    for node_id, node in STORY_NODES.items():
        if node.get("id") != node_id:
            warnings.append(f"Node key '{node_id}' does not match its id field '{node.get('id')}'.")

        if not _node_is_terminal(node_id, node):
            if not _iter_all_choices(node):
                warnings.append(f"Node '{node_id}' has no choices and is not marked as terminal.")

        for idx, choice in enumerate(_iter_all_choices(node), start=1):
            label = choice.get("label", f"unnamed-{idx}")
            next_id = choice.get("next")
            if next_id not in STORY_NODES:
                warnings.append(f"Choice '{label}' in node '{node_id}' points to missing node '{next_id}'.")

            requirements = choice.get("requirements", {})
            if "class" in requirements:
                unknown_classes = sorted(set(requirements["class"]) - known_classes)
                if unknown_classes:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' has unknown classes: {', '.join(unknown_classes)}."
                    )
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

            for item in requirements.get("items", []):
                if item not in obtainable_items:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' requires item '{item}' that is never granted."
                    )
            for item in effects.get("remove_items", []):
                if item not in obtainable_items:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' removes item '{item}' that is never granted."
                    )
            for item in requirements.get("missing_items", []):
                if item not in obtainable_items:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' checks missing item '{item}' that is never granted."
                    )

            for flag in requirements.get("flag_true", []):
                if flag not in known_flags:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' requires flag '{flag}' that is never set."
                    )
            for flag in requirements.get("flag_false", []):
                if flag not in known_flags:
                    warnings.append(
                        f"Choice '{label}' in node '{node_id}' checks flag '{flag}' that is never set."
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

            for stat_key in ("min_hp", "min_gold", "min_strength", "min_dexterity"):
                if stat_key in requirements:
                    required_value = requirements[stat_key]
                    required_classes: Iterable[str] = requirements.get("class", known_classes)
                    if all(required_value > max_stats[class_name][stat_key.replace("min_", "")] for class_name in required_classes):
                        warnings.append(
                            f"Choice '{label}' in node '{node_id}' requires {stat_key}={required_value}, which is unreachable for all valid classes."
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

        if node_id.startswith(INTRO_NODE_PREFIX):
            continue

        if _iter_all_choices(node):
            for class_name in known_classes:
                if not _any_choice_possible_for_class(node, class_name, obtainable_items, max_stats[class_name]):
                    warnings.append(
                        f"Node '{node_id}' appears to lock out the {class_name} class with its current requirements."
                    )

    # Graph cycle detection: find strongly connected components (SCCs) with
    # no exit edge — these are true dead-end loops the player cannot escape.
    # Hub loops (village ↔ camp) are intentional and have exits, so they pass.
    all_edges: dict[str, set[str]] = {}
    for nid, node in STORY_NODES.items():
        targets: set[str] = set()
        for choice in _iter_all_choices(node):
            next_id = choice.get("next")
            if next_id and next_id in STORY_NODES:
                targets.add(next_id)
        all_edges[nid] = targets

    # Tarjan's SCC algorithm (iterative to avoid deep recursion).
    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    index_map: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    sccs: list[set[str]] = []

    def _strongconnect(v: str) -> None:
        index_map[v] = lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        for w in all_edges.get(v, set()):
            if w not in index_map:
                _strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], index_map[w])

        if lowlink[v] == index_map[v]:
            scc: set[str] = set()
            while True:
                w = stack.pop()
                on_stack.discard(w)
                scc.add(w)
                if w == v:
                    break
            if len(scc) > 1:
                sccs.append(scc)

    import sys
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, len(STORY_NODES) * 3))
    try:
        for nid in STORY_NODES:
            if nid not in index_map:
                _strongconnect(nid)
    finally:
        sys.setrecursionlimit(old_limit)

    for scc in sccs:
        has_exit = False
        for nid in scc:
            for target in all_edges.get(nid, set()):
                if target not in scc:
                    has_exit = True
                    break
            if has_exit:
                break
        if not has_exit:
            for nid in sorted(scc):
                if not _node_is_terminal(nid, STORY_NODES[nid]):
                    warnings.append(
                        f"Node '{nid}' is in a cycle with no exit (potential inescapable loop)."
                    )

    return warnings
