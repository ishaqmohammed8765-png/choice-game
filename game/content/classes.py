from typing import Any, Dict

CLASS_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "Warrior": {
        "hp": 14,
        "gold": 8,
        "strength": 4,
        "dexterity": 2,
        "inventory": ["Rusty Sword"],
    },
    "Rogue": {
        "hp": 10,
        "gold": 10,
        "strength": 2,
        "dexterity": 4,
        "inventory": ["Dagger", "Lockpicks"],
    },
    "Archer": {
        "hp": 12,
        "gold": 9,
        "strength": 3,
        "dexterity": 3,
        "inventory": ["Shortbow", "Quiver of Arrows"],
    },
}
