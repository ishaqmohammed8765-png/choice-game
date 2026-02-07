from typing import Any, Dict

STORY_NODES_INTRO: Dict[str, Dict[str, Any]] = {
    "intro_warrior": {
        "id": "intro_warrior",
        "title": "Warrior Opening — Iron at the Gate",
        "text": (
            "You arrive at Oakrest as dusk falls, the palisade groaning under desperate hands. "
            "A bloodstained proclamation nailed to the gate bears the seal of Warden Caldus, "
            "a former Dawnwarden captain who vanished three winters ago. His message is clear: "
            "surrender the Dawn Emblem or watch the valley burn. Blacksmith Tor recognizes your "
            "old regiment insignia and shoves a shield into your hands."
        ),
        "dialogue": [
            {"speaker": "Blacksmith Tor", "line": "You served under Caldus's banner once. Now he's burning what we built. Show the militia how a warrior stands."},
            {"speaker": "Your Instinct", "line": "Caldus taught formation discipline. Time to turn his own lessons against him."},
        ],
        "choices": [
            {
                "label": "Drill the militia into shield ranks using Caldus's old formations",
                "effects": {
                    "trait_delta": {"reputation": 2},
                    "set_flags": {"class_intro_done": True, "militia_drilled": True, "warrior_oath_taken": True},
                    "seen_events": ["warrior_militia_drill"],
                    "log": "You drill Caldus's own shield formations into the militia, turning his tactics against him.",
                },
                "next": "village_square",
            },
            {
                "label": "Walk the palisade and swear to hold the breach yourself",
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
            "Oakrest's alleys choke with smoke and rumor. You slip through the shadowed routes, "
            "recognizing coded marks scratched into doorframes — marks you once scratched for "
            "Caldus's network before he turned. His agents were your contacts. His smuggling "
            "lanes were your highways. Now those same routes funnel raiders into the village."
        ),
        "dialogue": [
            {"speaker": "Signal Runner Tams", "line": "You ran messages for Caldus before he went dark. You know his playbook better than anyone alive."},
            {"speaker": "Your Instinct", "line": "Every alley Caldus mapped is a knife pointed at Oakrest. Time to turn the blade."},
        ],
        "choices": [
            {
                "label": "Erase Caldus's coded marks and map new escape routes",
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"class_intro_done": True, "shadow_routes_marked": True, "rogue_oath_taken": True},
                    "seen_events": ["rogue_shadow_routes"],
                    "log": "You scrub Caldus's old codes and replace them with escape routes only Oakrest will know.",
                },
                "next": "village_square",
            },
            {
                "label": "Seed false information through Caldus's old whisper network",
                "effects": {
                    "trait_delta": {"trust": 2},
                    "set_flags": {"class_intro_done": True, "shadow_routes_marked": False, "rogue_oath_taken": True},
                    "seen_events": ["rogue_whispered_calm"],
                    "log": "You poison Caldus's intelligence network with false troop counts and phantom barricades.",
                },
                "next": "village_square",
            },
        ],
    },
    "intro_archer": {
        "id": "intro_archer",
        "title": "Archer Opening — Signal Above the Square",
        "text": (
            "From the belltower you see what others only fear: smoke columns marking Caldus's "
            "advance from three directions. You served in his scout corps before he deserted. "
            "You know his signal patterns, his approach vectors, his preference for fire over "
            "steel. The same eyes that once watched for him now watch against him."
        ),
        "dialogue": [
            {"speaker": "Lookout Fen", "line": "You read Caldus's smoke signals once. Now read them for us, before the arrows start flying."},
            {"speaker": "Your Instinct", "line": "Caldus signals with fire. Answer with precision."},
        ],
        "choices": [
            {
                "label": "Take the belltower and decode Caldus's smoke signals for the defense",
                "effects": {
                    "add_items": ["Signal Arrows"],
                    "trait_delta": {"trust": 2},
                    "set_flags": {"class_intro_done": True, "archer_watch_established": True, "archer_oath_taken": True},
                    "seen_events": ["archer_watch_established"],
                    "log": "You decode Caldus's smoke patterns and relay his movements to Oakrest's defenders.",
                },
                "next": "village_square",
            },
            {
                "label": "Chart Caldus's approach vectors and find gaps in his advance",
                "effects": {
                    "trait_delta": {"reputation": 1, "alignment": 1},
                    "set_flags": {"class_intro_done": True, "archer_watch_established": False, "archer_oath_taken": True},
                    "seen_events": ["archer_smoke_routes"],
                    "log": "You map every smoke plume and identify weaknesses in Caldus's encirclement.",
                },
                "next": "village_square",
            },
        ],
    },
}
