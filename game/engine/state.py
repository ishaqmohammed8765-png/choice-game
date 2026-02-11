from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from game.state import normalize_meta_state


@dataclass(slots=True)
class GameState:
    """Pure representation of game state for engine-level checks."""

    player_class: str | None
    stats: Dict[str, int]
    inventory: List[str]
    flags: Dict[str, Any]
    traits: Dict[str, int]
    meta_state: Dict[str, List[str]]


def state_from_session(session: Mapping[str, Any]) -> GameState:
    """Build a GameState snapshot from a session-like object."""
    meta_state = normalize_meta_state(session.get("meta_state"))
    return GameState(
        player_class=session.get("player_class"),
        stats=dict(session.get("stats", {})),
        inventory=list(session.get("inventory", [])),
        flags=dict(session.get("flags", {})),
        traits=dict(session.get("traits", {})),
        meta_state={
            "unlocked_items": list(meta_state.get("unlocked_items", [])),
            "removed_nodes": list(meta_state.get("removed_nodes", [])),
        },
    )
