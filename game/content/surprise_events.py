from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class SurpriseEvent(TypedDict):
    id: str
    label: str
    min_reputation: int | None
    max_reputation: int | None
    min_ember_tide: int | None
    max_ember_tide: int | None
    effects: Dict[str, Any]


SURPRISE_EVENTS: List[SurpriseEvent] = [
    # --- Reputation events ---
    {
        "id": "rep_rising",
        "label": "Word spreads",
        "min_reputation": 3,
        "max_reputation": None,
        "min_ember_tide": None,
        "max_ember_tide": None,
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
        "min_ember_tide": None,
        "max_ember_tide": None,
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
        "min_ember_tide": None,
        "max_ember_tide": None,
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
        "min_ember_tide": None,
        "max_ember_tide": None,
        "effects": {
            "log": "A bounty notice bearing your description appears at the next crossing.",
            "set_flags": {"bounty_notice": True},
        },
    },
    # --- Ember Tide events (time pressure from Caldus's ritual) ---
    {
        "id": "ember_tide_rising",
        "label": "Outer farms ignite",
        "min_reputation": None,
        "max_reputation": None,
        "min_ember_tide": 3,
        "max_ember_tide": None,
        "effects": {
            "log": "Orange light blooms on the horizon. Caldus's ritual feeds on every hour you spend away from the ruin.",
            "set_flags": {"ember_tide_rising": True},
        },
    },
    {
        "id": "ember_tide_critical",
        "label": "The sky darkens",
        "min_reputation": None,
        "max_reputation": None,
        "min_ember_tide": 5,
        "max_ember_tide": None,
        "effects": {
            "log": "Ash clouds blot the stars. Scouts report villagers fleeing Oakrest. Caldus is close to completing the ritual.",
            "set_flags": {"ember_tide_critical": True},
            "trait_delta": {"trust": -1},
        },
    },
    {
        "id": "ember_tide_desperate",
        "label": "The Emblem pulses",
        "min_reputation": None,
        "max_reputation": None,
        "min_ember_tide": 7,
        "max_ember_tide": None,
        "effects": {
            "log": "A deep throb rolls through the earth. The Dawn Emblem's corruption is nearly complete.",
            "set_flags": {"ember_tide_desperate": True},
            "trait_delta": {"trust": -1, "reputation": -1},
        },
    },
]
