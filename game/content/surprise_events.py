from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class SurpriseEvent(TypedDict):
    id: str
    label: str
    min_reputation: int | None
    max_reputation: int | None
    effects: Dict[str, Any]


SURPRISE_EVENTS: List[SurpriseEvent] = [
    {
        "id": "rep_rising",
        "label": "Word spreads",
        "min_reputation": 3,
        "max_reputation": None,
        "effects": {
            "log": "Word of your deeds reaches the outposts, and scouts nod with newfound respect.",
            "trait_delta": {"trust": 1},
        },
    },
    {
        "id": "rep_renowned",
        "label": "Renown opens doors",
        "min_reputation": 6,
        "max_reputation": None,
        "effects": {
            "log": "Merchants extend credit on the strength of your reputation.",
            "gold": 2,
        },
    },
    {
        "id": "rep_soured",
        "label": "Rumors turn",
        "min_reputation": None,
        "max_reputation": -3,
        "effects": {
            "log": "Harsh rumors follow you, and even allies keep their distance.",
            "trait_delta": {"trust": -1},
        },
    },
    {
        "id": "rep_bounty",
        "label": "Bounty posted",
        "min_reputation": None,
        "max_reputation": -6,
        "effects": {
            "log": "A bounty notice bearing your description appears at the next crossing.",
            "set_flags": {"bounty_notice": True},
        },
    },
]
