"""TypedDict schemas for story content structures.

These types define the expected shape of story nodes, choices, effects,
and requirements. They serve as documentation and enable IDE type checking.
"""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class Requirements(TypedDict, total=False):
    """Gating conditions a player must meet to access a choice."""

    class_: List[str]  # mapped from 'class' key at runtime
    any_of: List[Requirements]
    min_hp: int
    min_gold: int
    min_strength: int
    min_dexterity: int
    items: List[str]
    missing_items: List[str]
    flag_true: List[str]
    flag_false: List[str]
    meta_items: List[str]
    meta_missing_items: List[str]
    meta_nodes_present: List[str]


class Effects(TypedDict, total=False):
    """Deterministic outcome applied when a choice is selected."""

    hp: int
    gold: int
    strength: int
    dexterity: int
    add_items: List[str]
    remove_items: List[str]
    set_flags: Dict[str, Any]
    trait_delta: Dict[str, int]
    faction_delta: Dict[str, int]
    seen_events: List[str]
    log: str
    unlock_meta_items: List[str]
    remove_meta_nodes: List[str]


class ConditionalEffect(TypedDict, total=False):
    """A variant outcome applied when its requirements are met."""

    requirements: Requirements
    effects: Effects
    next: str


class Choice(TypedDict, total=False):
    """A single player choice within a story node."""

    label: str
    next: str
    group: str
    requirements: Requirements
    effects: Effects
    conditional_effects: List[ConditionalEffect]
    irreversible: bool
    instant_death: bool
    auto_apply: bool


class DialogueLine(TypedDict):
    """A single line of NPC dialogue."""

    speaker: str
    line: str


class StoryNode(TypedDict, total=False):
    """A single node in the story graph."""

    id: str
    title: str
    text: str
    dialogue: List[DialogueLine]
    choices: List[Choice]
    auto_choices: List[Choice]
    requirements: Requirements


class PlayerStats(TypedDict):
    """Mutable player stat block."""

    hp: int
    gold: int
    strength: int
    dexterity: int


class ClassTemplate(TypedDict):
    """Starting template for a player class."""

    hp: int
    gold: int
    strength: int
    dexterity: int
    inventory: List[str]


class Snapshot(TypedDict, total=False):
    """Full game state snapshot for save/load and undo."""

    player_class: str
    current_node: str
    stats: PlayerStats
    inventory: List[str]
    flags: Dict[str, Any]
    traits: Dict[str, int]
    factions: Dict[str, int]
    seen_events: List[str]
    decision_history: List[Dict[str, str]]
    event_log: List[str]
    history: List[Snapshot]
    visited_nodes: List[str]
    visited_edges: List[Dict[str, str]]
    pending_choice_confirmation: Dict[str, Any] | None
