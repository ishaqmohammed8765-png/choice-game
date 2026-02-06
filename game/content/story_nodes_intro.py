from typing import Any, Dict

STORY_NODES_INTRO: Dict[str, Dict[str, Any]] = {
    "intro_warrior": {
        "id": "intro_warrior",
        "title": "Warrior Opening — Iron at the Gate",
        "text": (
            "You arrive at Oakrest to find the palisade creaking under the weight of anxious villagers. "
            "Blacksmith Tor presses a shield into your hands and asks you to turn fear into formation before the night raid."
        ),
        "dialogue": [
            {"speaker": "Blacksmith Tor", "line": "We need a wall, not a mob. Show them how a warrior stands."},
            {"speaker": "Your Instinct", "line": "Make them believe the line will hold, and it will."},
        ],
        "choices": [
            {
                "label": "Drill the militia into shield ranks",
                "effects": {
                    "trait_delta": {"reputation": 2},
                    "set_flags": {"class_intro_done": True, "militia_drilled": True, "warrior_oath_taken": True},
                    "seen_events": ["warrior_militia_drill"],
                    "log": "You drill shield lines and hammer the militia into a wall of iron, defining Oakrest's defense by your discipline.",
                },
                "next": "village_square",
            },
            {
                "label": "Walk the palisade and promise you'll hold the breach",
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"class_intro_done": True, "militia_drilled": False, "warrior_oath_taken": True},
                    "seen_events": ["warrior_oath_palisade"],
                    "log": "You vow to hold the line yourself, and the militia takes courage from your oath.",
                },
                "next": "village_square",
            },
        ],
    },
    "intro_rogue": {
        "id": "intro_rogue",
        "title": "Rogue Opening — Whispers in the Lanes",
        "text": (
            "Oakrest's back alleys are a web of fear and rumor. You slip into the shadowed routes to find the paths "
            "raiders miss and the exits the villagers can trust."
        ),
        "dialogue": [
            {"speaker": "Signal Runner Tams", "line": "We need someone who can move unseen. You have that look."},
            {"speaker": "Your Instinct", "line": "Every alley is a promise: escape, ambush, or betrayal."},
        ],
        "choices": [
            {
                "label": "Map hidden alleys and whisper routes",
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"class_intro_done": True, "shadow_routes_marked": True, "rogue_oath_taken": True},
                    "seen_events": ["rogue_shadow_routes"],
                    "log": "You map escape routes and whisper lanes, turning panic into a rogue's network of quiet control.",
                },
                "next": "village_square",
            },
            {
                "label": "Blend into the crowd and seed calm through rumor",
                "effects": {
                    "trait_delta": {"trust": 2},
                    "set_flags": {"class_intro_done": True, "shadow_routes_marked": False, "rogue_oath_taken": True},
                    "seen_events": ["rogue_whispered_calm"],
                    "log": "You tuck fear behind confident whispers, and the square stops shaking long enough to breathe.",
                },
                "next": "village_square",
            },
        ],
    },
    "intro_archer": {
        "id": "intro_archer",
        "title": "Archer Opening — Signal Above the Square",
        "text": (
            "From the belltower, you can see the smoke trails and hear the frightened bells below. "
            "An archer's view is a promise: early warning, clean shots, and the resolve to act first."
        ),
        "dialogue": [
            {"speaker": "Lookout Fen", "line": "One arrow in the right place saves ten swords from being drawn."},
            {"speaker": "Your Instinct", "line": "Claim the high ground and the village will follow your signal."},
        ],
        "choices": [
            {
                "label": "Take the belltower and call scouting shots",
                "effects": {
                    "add_items": ["Signal Arrows"],
                    "trait_delta": {"trust": 2},
                    "set_flags": {"class_intro_done": True, "archer_watch_established": True, "archer_oath_taken": True},
                    "seen_events": ["archer_watch_established"],
                    "log": "From the belltower, your archer's signals choreograph the square, moving villagers before raiders can strike.",
                },
                "next": "village_square",
            },
            {
                "label": "Chart the smoke trails beyond the farms",
                "effects": {
                    "trait_delta": {"reputation": 1, "alignment": 1},
                    "set_flags": {"class_intro_done": True, "archer_watch_established": False, "archer_oath_taken": True},
                    "seen_events": ["archer_smoke_routes"],
                    "log": "You mark every smoke plume and return with a clear map of the raiders' approach.",
                },
                "next": "village_square",
            },
        ],
    },
}
