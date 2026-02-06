"""Compatibility layer for legacy imports.

Story content now lives in the game.content package, split into smaller modules.
"""

from game.content import (
    CHOICE_SIMPLIFICATION_REPORT,
    CLASS_TEMPLATES,
    FACTION_KEYS,
    HIGH_COST_GOLD_LOSS,
    HIGH_COST_HP_LOSS,
    MAX_CHOICES_PER_NODE,
    STAT_KEYS,
    STORY_NODES,
    TRAIT_KEYS,
    init_story_nodes,
)

__all__ = [
    "CHOICE_SIMPLIFICATION_REPORT",
    "CLASS_TEMPLATES",
    "FACTION_KEYS",
    "HIGH_COST_GOLD_LOSS",
    "HIGH_COST_HP_LOSS",
    "MAX_CHOICES_PER_NODE",
    "STAT_KEYS",
    "STORY_NODES",
    "TRAIT_KEYS",
    "init_story_nodes",
]
