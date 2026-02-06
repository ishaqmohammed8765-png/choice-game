import copy
import json
from typing import Any, Dict, List

import streamlit as st


TRAIT_KEYS = ["trust", "reputation", "alignment"]
HIGH_COST_HP_LOSS = 3
HIGH_COST_GOLD_LOSS = 5


# -----------------------------
# Data model: classes and story
# -----------------------------
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
}


STORY_NODES: Dict[str, Dict[str, Any]] = {
    "village_square": {
        "id": "village_square",
        "title": "Oakrest Village Square",
        "text": (
            "The bell of Oakrest tolls at dusk. Villagers whisper of raiders, a cursed ruin in the forest, "
            "and a missing relic known as the Dawn Emblem. Elder Mara asks you to track the threat before nightfall."
        ),
        "choices": [
            {
                "label": "Buy a rope from the quartermaster (3 gold)",
                "requirements": {"min_gold": 3, "missing_items": ["Rope"]},
                "effects": {
                    "gold": -3,
                    "add_items": ["Rope"],
                    "set_flags": {"has_rope": True},
                    "log": "You buy a sturdy rope and tie it to your pack.",
                },
                "next": "village_square",
            },
            {
                "label": "Visit the herbalist for a tonic (+2 HP, 2 gold)",
                "requirements": {"min_gold": 2, "flag_false": ["bought_tonic"]},
                "effects": {
                    "gold": -2,
                    "hp": 2,
                    "set_flags": {"bought_tonic": True},
                    "log": "A bitter tonic steadies your breath and closes old cuts.",
                },
                "next": "village_square",
            },
            {
                "label": "Visit the roadside trader and rest stop",
                "effects": {"log": "You head to a lantern-lit camp where a trader tends supplies."},
                "next": "camp_shop",
            },
            {
                "label": "Take the forest road toward the old watchtower",
                "effects": {"log": "You leave Oakrest and follow the shadowed road into the forest."},
                "next": "forest_crossroad",
            },
        ],
    },
    "camp_shop": {
        "id": "camp_shop",
        "title": "Roadside Trader & Rest Fire",
        "text": (
            "A retired scout sells practical tools near a safe firepit. You can buy gear or patch your wounds "
            "before entering deeper wilderness."
        ),
        "choices": [
            {
                "label": "Buy rope (3 gold)",
                "requirements": {"min_gold": 3, "missing_items": ["Rope"]},
                "effects": {"gold": -3, "add_items": ["Rope"], "log": "You purchase a sturdy climbing rope."},
                "next": "camp_shop",
            },
            {
                "label": "Buy lockpicks (4 gold)",
                "requirements": {"min_gold": 4, "missing_items": ["Lockpicks"]},
                "effects": {
                    "gold": -4,
                    "add_items": ["Lockpicks"],
                    "log": "You buy a finely balanced lockpick set.",
                },
                "next": "camp_shop",
            },
            {
                "label": "Buy torch (2 gold)",
                "requirements": {"min_gold": 2, "missing_items": ["Torch"]},
                "effects": {"gold": -2, "add_items": ["Torch"], "log": "You light a resin torch for dark passages."},
                "next": "camp_shop",
            },
            {
                "label": "Rest by the fire (+4 HP, 3 gold)",
                "requirements": {"min_gold": 3},
                "effects": {"gold": -3, "hp": 4, "log": "Warm stew and rest restore your strength."},
                "next": "camp_shop",
            },
            {
                "label": "Leave the camp for the forest crossroad",
                "effects": {"log": "You shoulder your gear and continue toward the ruin."},
                "next": "forest_crossroad",
            },
        ],
    },
    "forest_crossroad": {
        "id": "forest_crossroad",
        "title": "Forest Crossroad",
        "text": (
            "Pines crowd around a fork in the path. To the left: a narrow ravine crossing. "
            "To the right: a campfire glow where bandits argue over spoils. Ahead, war drums echo from "
            "the Ashfang warband while silver lanterns of the Rangers flicker between trees."
        ),
        "choices": [
            {
                "label": "Cross the ravine by hauling yourself on old beams (Strength 3)",
                "requirements": {"min_strength": 3},
                "effects": {"log": "Your raw force carries you across the groaning beams."},
                "next": "ravine_crossing",
            },
            {
                "label": "Cross the ravine using your rope",
                "requirements": {"items": ["Rope"]},
                "effects": {
                    "log": "You anchor your rope and swing across the ravine safely.",
                    "set_flags": {"used_rope_crossing": True},
                },
                "next": "ravine_crossing",
            },
            {
                "label": "Sneak toward the bandit camp (Dexterity 3)",
                "requirements": {"min_dexterity": 3},
                "effects": {"log": "You melt into the brush and approach unheard."},
                "next": "bandit_camp",
            },
            {
                "label": "March openly to the bandit camp",
                "effects": {"log": "Branches crack under your boots as you confront the raiders openly."},
                "next": "bandit_camp",
            },
            {
                "label": "Follow the ranger lanterns to their hidden outpost",
                "effects": {
                    "set_flags": {"met_dawnwardens": True},
                    "log": "You leave the road and follow coded lantern flashes to a concealed ranger camp.",
                },
                "next": "dawnwarden_outpost",
            },
            {
                "label": "Track the Ashfang war drums into the bramble valley",
                "effects": {
                    "set_flags": {"met_ashfang": True},
                    "log": "You shadow the drumming trail toward an Ashfang hunting column.",
                },
                "next": "ashfang_hunt",
            },
        ],
    },
    "dawnwarden_outpost": {
        "id": "dawnwarden_outpost",
        "title": "Ranger Outpost",
        "text": (
            "Captain Serin of the Rangers studies maps pinned by dagger points. Archivist Pell and "
            "shield-bearer Nima argue about whether to assault the ruin now or save trapped villagers first."
        ),
        "choices": [
            {
                "label": "Swear temporary alliance with Captain Serin",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1, "alignment": 1},
                    "set_flags": {"dawnwarden_allied": True, "mercy_reputation": True},
                    "add_items": ["Warden Token"],
                    "log": "Serin clasps your forearm and grants a Warden Token recognized by local patrols.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Ask Archivist Pell for enemy intelligence",
                "effects": {
                    "set_flags": {"knows_enemy_roster": True},
                    "seen_events": ["learned_enemy_roster"],
                    "log": "Pell briefs you on raider ranks: Ember Troopers, Bonebreakers, and the Emblem Warden.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Challenge Nima in a spar to earn respect (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "trait_delta": {"reputation": 2},
                    "set_flags": {"earned_dawnwarden_respect": True},
                    "log": "After a brutal spar, Nima salutes you and marks a safer approach to the gate.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "ashfang_hunt": {
        "id": "ashfang_hunt",
        "title": "Ashfang Hunting Grounds",
        "text": (
            "Warchief Drogath leads the Ashfangs with scout Yara and beast-handler Korr. They stalk a raider "
            "convoy guarded by ember-hounds and masked zealots. The warband invites you to prove yourself."
        ),
        "choices": [
            {
                "label": "Join the ambush and crush the convoy (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "hp": -1,
                    "gold": 4,
                    "trait_delta": {"reputation": 2, "alignment": -1},
                    "set_flags": {"ashfang_allied": True, "cruel_reputation": True},
                    "seen_events": ["ashfang_convoy_slain"],
                    "log": "You and Drogath tear through raiders and scatter ember-hounds into the dark.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Duel scout Yara in silence and win by finesse (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"ashfang_respect": True},
                    "add_items": ["Ashfang Charm"],
                    "log": "Yara yields and gifts you an Ashfang Charm that frightens lesser convoy beasts.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Refuse bloodshed and guide prisoners to safety",
                "effects": {
                    "trait_delta": {"trust": 1, "alignment": 2},
                    "set_flags": {"rescued_prisoners": True, "mercy_reputation": True},
                    "log": "You escort shaken prisoners away while the warband fights on without you.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "ravine_crossing": {
        "id": "ravine_crossing",
        "title": "Ravine Crossing",
        "text": (
            "Halfway across, rotten planks snap. You can muscle through the final jump, "
            "or slip and lose precious strength to the rocks below."
        ),
        "choices": [
            {
                "label": "Leap and cling to the far ledge (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {"log": "You catch the ledge with iron grip and pull yourself up."},
                "next": "ruin_gate",
            },
            {
                "label": "Take the fall and climb out",
                "effects": {"hp": -3, "log": "You hit the ravine floor hard before scrambling back up."},
                "next": "ruin_gate",
            },
        ],
    },
    "bandit_camp": {
        "id": "bandit_camp",
        "title": "Bandit Camp",
        "text": (
            "Three bandits surround a bound scout from Oakrest. Their leader, Kest, offers a bargain: "
            "leave the scout and walk away with coin, or interfere and spill blood."
        ),
        "choices": [
            {
                "label": "Break their line in open combat (Strength 3)",
                "requirements": {"min_strength": 3},
                "effects": {
                    "hp": -2,
                    "gold": 4,
                    "trait_delta": {"trust": 1, "reputation": -1, "alignment": -2},
                    "seen_events": ["bandits_slain"],
                    "set_flags": {"rescued_scout": True, "spared_bandit": False, "cruel_reputation": True, "morality": "ruthless"},
                    "log": "You defeat the bandits brutally and free the scout.",
                },
                "next": "scout_report",
            },
            {
                "label": "Cut the scout free while hidden (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 2, "alignment": 2},
                    "seen_events": ["scout_saved_silently"],
                    "set_flags": {"rescued_scout": True, "spared_bandit": True, "mercy_reputation": True, "morality": "merciful"},
                    "log": "You free the scout without a fight; the bandits flee into darkness.",
                },
                "next": "scout_report",
            },
            {
                "label": "Accept Kest's bribe and walk away (+6 gold)",
                "effects": {
                    "gold": 6,
                    "trait_delta": {"trust": -3, "reputation": -2, "alignment": -3},
                    "seen_events": ["scout_abandoned"],
                    "set_flags": {"abandoned_scout": True, "cruel_reputation": True, "morality": "ruthless"},
                    "log": "You pocket the bribe and leave the scout to fate.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "scout_report": {
        "id": "scout_report",
        "title": "Scout's Warning",
        "text": (
            "The rescued scout gasps that raiders have occupied the ancient ruin and are arming an incendiary device. "
            "He offers a bronze ruin seal that can open hidden doors."
        ),
        "requirements": {"flag_true": ["rescued_scout"]},
        "choices": [
            {
                "label": "Accept the bronze seal",
                "requirements": {"missing_items": ["Bronze Seal"]},
                "effects": {
                    "add_items": ["Bronze Seal"],
                    "trait_delta": {"trust": 1},
                    "seen_events": ["accepted_seal"],
                    "set_flags": {"has_seal": True},
                    "log": "You take the bronze seal; old markings glow faintly.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Ask the scout for a hidden approach to the raiders",
                "requirements": {"flag_true": ["rescued_scout"]},
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "seen_events": ["learned_hidden_route"],
                    "set_flags": {"knows_hidden_route": True},
                    "log": "The scout marks an old service tunnel only Oakrest wardens remember.",
                },
                "next": "hidden_tunnel",
            },
            {
                "label": "Refuse and hurry to the ruin",
                "effects": {"log": "You refuse the token and press onward."},
                "next": "ruin_gate",
            },
        ],
    },
    "hidden_tunnel": {
        "id": "hidden_tunnel",
        "title": "Forgotten Service Tunnel",
        "text": (
            "The scout's map leads you into a collapsed maintenance tunnel beneath the ruin. "
            "You can sabotage the signal braziers now, but doing so will trap anyone still inside."
        ),
        "requirements": {"flag_true": ["knows_hidden_route"]},
        "choices": [
            {
                "label": "Collapse the tunnel supports to deny raider reinforcements (irreversible)",
                "effects": {
                    "trait_delta": {"trust": -1, "reputation": 2, "alignment": -1},
                    "seen_events": ["tunnel_collapsed"],
                    "set_flags": {"tunnel_collapsed": True, "irreversible_choice_made": True},
                    "log": "Stone crashes behind you. The route is sealed forever, along with anyone still below.",
                },
                "irreversible": True,
                "next": "ruin_gate",
            },
            {
                "label": "Leave the supports intact and continue quietly",
                "effects": {
                    "trait_delta": {"trust": 1, "alignment": 1},
                    "seen_events": ["tunnel_spared"],
                    "log": "You preserve the passage, choosing caution over collateral damage.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "ruin_gate": {
        "id": "ruin_gate",
        "title": "Ancient Ruin Gate",
        "text": (
            "Cracked stone doors loom beneath ivy and carved suns. A collapsed side breach leads downward, "
            "while the main gate bears a lock made for old emblems."
        ),
        "choices": [
            {
                "label": "Force open the main gate (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {"log": "With a roar, you wrench the gate enough to squeeze through."},
                "next": "inner_hall",
            },
            {
                "label": "Pick the ancient lock (Rogue only)",
                "requirements": {"items": ["Lockpicks"]},
                "effects": {
                    "log": "Your lockpicks whisper through tumblers untouched for centuries.",
                    "set_flags": {"opened_cleanly": True},
                },
                "next": "inner_hall",
            },
            {
                "label": "Use the bronze seal to open the warded door",
                "requirements": {"items": ["Bronze Seal"]},
                "effects": {"log": "The bronze seal clicks into place and the door parts silently."},
                "next": "inner_hall",
            },
            {
                "label": "Crawl through the collapsed breach (-2 HP)",
                "effects": {"hp": -2, "log": "Jagged stones tear at you as you squeeze through."},
                "next": "inner_hall",
            },
            {
                "label": "Call for surrender and safe passage (merciful path)",
                "requirements": {"flag_true": ["mercy_reputation"]},
                "effects": {"log": "Your reputation for mercy persuades a frightened lookout to unbar a side door."},
                "next": "inner_hall",
            },
            {
                "label": "Threaten the lookouts into opening a side gate (ruthless path)",
                "requirements": {"flag_true": ["cruel_reputation"]},
                "effects": {"hp": -1, "log": "They obey, but one lookout stabs you before fleeing."},
                "next": "inner_hall",
            },
            {
                "label": "Present the Warden Token and demand lawful entry",
                "requirements": {"items": ["Warden Token"]},
                "effects": {
                    "log": "Ruin sentries mistake you for sanctioned enforcers and open the outer lock.",
                    "set_flags": {"opened_cleanly": True},
                },
                "next": "inner_hall",
            },
        ],
    },
    "inner_hall": {
        "id": "inner_hall",
        "title": "Inner Hall of Echoes",
        "text": (
            "Torchlight reveals two routes: a trapped gallery leading to the core chamber, "
            "and an armory vault sealed behind rusted bars."
        ),
        "choices": [
            {
                "label": "Disarm and pass the trap gallery (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "set_flags": {"trap_disarmed": True},
                    "log": "You spot pressure plates and bypass every trigger.",
                },
                "next": "core_approach",
            },
            {
                "label": "Charge through the trap gallery (-4 HP)",
                "effects": {"hp": -4, "log": "Darts and blades rake you, but you push through."},
                "next": "core_approach",
            },
            {
                "label": "Pry open the armory bars (Strength 3)",
                "requirements": {"min_strength": 3, "flag_false": ["armory_looted"]},
                "effects": {
                    "add_items": ["Ancient Shield"],
                    "set_flags": {"armory_looted": True},
                    "log": "You bend the bars and recover an Ancient Shield.",
                },
                "next": "inner_hall",
            },
            {
                "label": "Use a torch to spot hidden markings and a safer route",
                "requirements": {"items": ["Torch"], "flag_false": ["torch_route_found"]},
                "effects": {
                    "set_flags": {"torch_route_found": True},
                    "log": "Torchlight reveals chalk marks pointing to a concealed side passage.",
                },
                "next": "core_approach",
            },
            {
                "label": "Use the Ashfang Charm to scatter ember-hounds",
                "requirements": {"items": ["Ashfang Charm"]},
                "effects": {
                    "set_flags": {"hounds_scattered": True},
                    "log": "The charm's scent terrifies ember-hounds guarding the corridor, clearing your path.",
                },
                "next": "core_approach",
            },
        ],
    },
    "core_approach": {
        "id": "core_approach",
        "title": "Antechamber of Conflict",
        "text": (
            "At the chamber's threshold kneels Kest, wounded and desperate. He claims the raider crew betrayed everyone "
            "and begs for mercy. Your choice here may define your fate."
        ),
        "choices": [
            {
                "label": "Spare Kest and take his warning",
                "effects": {
                    "set_flags": {"spared_bandit": True, "morality": "merciful"},
                    "log": "You spare Kest. He reveals a weakness in the Warden's guard.",
                },
                "next": "final_confrontation",
            },
            {
                "label": "Execute Kest",
                "effects": {
                    "trait_delta": {"trust": -2, "alignment": -2},
                    "seen_events": ["kest_executed"],
                    "set_flags": {"spared_bandit": False, "morality": "ruthless"},
                    "log": "You execute Kest and step over his body into the chamber.",
                },
                "irreversible": True,
                "next": "final_confrontation",
            },
            {
                "label": "Bind Kest with rope and move on",
                "requirements": {"items": ["Rope"]},
                "effects": {
                    "set_flags": {"bound_kest": True, "morality": "merciful"},
                    "log": "You bind Kest securely, leaving him alive but helpless.",
                },
                "next": "final_confrontation",
            },
        ],
    },
    "final_confrontation": {
        "id": "final_confrontation",
        "title": "Final Confrontation: The Ruin Warden",
        "text": (
            "In the heart of the ruin, the armored Warden channels power into the Dawn Emblem. "
            "You must stop the device before Oakrest burns."
        ),
        "choices": [
            {
                "label": "Warrior finale: hold the collapsing arch and strike the Warden down",
                "requirements": {"class": ["Warrior"], "min_strength": 4},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "best", "warrior_best_ending": True},
                    "log": "You brace the collapsing arch with raw strength, then land the decisive blow.",
                },
                "next": "ending_best_warrior",
            },
            {
                "label": "Rogue finale: slip through the ward lattice and sever the Emblem feed",
                "requirements": {"class": ["Rogue"], "min_dexterity": 4, "items": ["Lockpicks"]},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "best", "rogue_best_ending": True},
                    "log": "You ghost through the ward lattice and cut the Emblem conduit before it can surge.",
                },
                "next": "ending_best_rogue",
            },
            {
                "label": "Overpower the Warden in direct combat (Strength 5)",
                "requirements": {"min_strength": 5},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "You shatter the Warden's guard with unstoppable force.",
                },
                "next": "ending_good",
            },
            {
                "label": "Exploit the opening from your mercy (requires spared Kest)",
                "requirements": {"flag_true": ["spared_bandit"]},
                "effects": {
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "Using Kest's warning, you disable the device core and win cleanly.",
                },
                "next": "ending_good",
            },
            {
                "label": "Use the hidden-route sabotage to destabilize the chamber",
                "requirements": {"flag_true": ["tunnel_collapsed"]},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Your earlier demolition fractures the chamber floor, ending the device in chaos.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Interrogate Kest's old crew code (Lockpicks + ruthless)",
                "requirements": {"items": ["Lockpicks"], "flag_true": ["cruel_reputation"]},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Your ruthless reputation lets you force a confession and break the warding code.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Protect trapped villagers first (requires merciful outlook)",
                "requirements": {"flag_true": ["mercy_reputation"]},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "You shield the captives, then turn their gratitude into momentum against the Warden.",
                },
                "next": "ending_good",
            },
            {
                "label": "Strike from shadows at the device core (Dexterity 5)",
                "requirements": {"min_dexterity": 5},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "You collapse the device core, but debris crushes part of the chamber.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Raise the Ancient Shield and endure the device backlash",
                "requirements": {"items": ["Ancient Shield"]},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "The shield saves you as you push through the backlash and fell the Warden.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Desperate assault without an advantage",
                "effects": {
                    "hp": -8,
                    "set_flags": {"warden_defeated": False, "ending_quality": "bad"},
                    "log": "You rush in blindly and suffer a devastating counterstrike.",
                },
                "next": "ending_bad",
            },
        ],
    },
    "ending_good": {
        "id": "ending_good",
        "title": "Ending — Dawn Over Oakrest",
        "text": (
            "The device is stopped before activation. The Dawn Emblem is returned to the village archive. "
            "If your path was merciful, Oakrest hails you as a guardian of both lives and honor; "
            "if ruthless, they praise your strength but fear what you may become."
        ),
        "choices": [],
    },
    "ending_best_warrior": {
        "id": "ending_best_warrior",
        "title": "Best Ending — Iron Dawn of Oakrest",
        "text": (
            "Your warrior's stand saves both the Dawn Emblem and the trapped villagers. Word spreads that you held "
            "a collapsing ruin with your bare strength, and Oakrest names you Shield of the Valley."
        ),
        "choices": [],
    },
    "ending_best_rogue": {
        "id": "ending_best_rogue",
        "title": "Best Ending — Silent Dawn of Oakrest",
        "text": (
            "Your rogue precision prevents the surge before anyone else even sees the danger. The Rangers record the "
            "night as a flawless victory, and Oakrest entrusts you with its hidden defenses."
        ),
        "choices": [],
    },
    "ending_mixed": {
        "id": "ending_mixed",
        "title": "Ending — Victory at a Cost",
        "text": (
            "The Warden falls, but the ruin partially collapses and nearby farms are lost in the aftermath. "
            "Oakrest survives, though your name is spoken with equal gratitude and regret."
        ),
        "choices": [],
    },
    "ending_bad": {
        "id": "ending_bad",
        "title": "Ending — Nightfall Over Oakrest",
        "text": (
            "Your final gamble fails. The device surges to full power and the forest burns with unnatural fire. "
            "Oakrest is abandoned by sunrise, and your tale becomes a warning."
        ),
        "choices": [],
    },
    "death": {
        "id": "death",
        "title": "You Have Fallen",
        "text": (
            "Your wounds are too severe. The quest ends here, and the fate of Oakrest passes to another soul."
        ),
        "choices": [],
    },
}


# -----------------------------
# State and game logic helpers
# -----------------------------
def reset_game_state() -> None:
    """Reset all session state values to begin a fresh run."""
    st.session_state.player_class = None
    st.session_state.current_node = None
    st.session_state.stats = {"hp": 0, "gold": 0, "strength": 0, "dexterity": 0}
    st.session_state.inventory = []
    st.session_state.flags = {}
    st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
    st.session_state.seen_events = []
    st.session_state.decision_history = []
    st.session_state.last_choice_feedback = []
    st.session_state.event_log = []
    st.session_state.history = []
    st.session_state.save_blob = ""
    st.session_state.pending_choice_confirmation = None


def start_game(player_class: str) -> None:
    """Initialize game state from class template and enter first node."""
    template = CLASS_TEMPLATES[player_class]
    st.session_state.player_class = player_class
    st.session_state.current_node = "village_square"
    st.session_state.stats = {
        "hp": template["hp"],
        "gold": template["gold"],
        "strength": template["strength"],
        "dexterity": template["dexterity"],
    }
    st.session_state.inventory = copy.deepcopy(template["inventory"])
    st.session_state.flags = {"class": player_class}
    st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
    st.session_state.seen_events = []
    st.session_state.decision_history = []
    st.session_state.last_choice_feedback = []
    st.session_state.event_log = [f"You begin your journey as a {player_class}."]
    st.session_state.history = []
    st.session_state.pending_choice_confirmation = None


def add_log(message: str) -> None:
    """Append a narrative event to the player log."""
    if message:
        st.session_state.event_log.append(message)


def snapshot_state() -> Dict[str, Any]:
    """Capture game state for backtracking and save export."""
    return {
        "player_class": st.session_state.player_class,
        "current_node": st.session_state.current_node,
        "stats": copy.deepcopy(st.session_state.stats),
        "inventory": copy.deepcopy(st.session_state.inventory),
        "flags": copy.deepcopy(st.session_state.flags),
        "traits": copy.deepcopy(st.session_state.traits),
        "seen_events": copy.deepcopy(st.session_state.seen_events),
        "decision_history": copy.deepcopy(st.session_state.decision_history),
        "last_choice_feedback": copy.deepcopy(st.session_state.last_choice_feedback),
        "event_log": copy.deepcopy(st.session_state.event_log),
        "pending_choice_confirmation": copy.deepcopy(st.session_state.pending_choice_confirmation),
    }


def load_snapshot(snapshot: Dict[str, Any]) -> None:
    """Restore game state from a validated snapshot."""
    st.session_state.player_class = snapshot["player_class"]
    st.session_state.current_node = snapshot["current_node"]
    st.session_state.stats = snapshot["stats"]
    st.session_state.inventory = snapshot["inventory"]
    st.session_state.flags = snapshot["flags"]
    st.session_state.traits = snapshot.get("traits", {"trust": 0, "reputation": 0, "alignment": 0})
    st.session_state.seen_events = snapshot.get("seen_events", [])
    st.session_state.decision_history = snapshot.get("decision_history", [])
    st.session_state.last_choice_feedback = snapshot.get("last_choice_feedback", [])
    st.session_state.event_log = snapshot["event_log"]
    st.session_state.pending_choice_confirmation = snapshot.get("pending_choice_confirmation")


def execute_choice(node_id: str, label: str, choice: Dict[str, Any]) -> None:
    """Apply a selected choice and transition to its next node."""
    st.session_state.pending_choice_confirmation = None
    st.session_state.history.append(snapshot_state())
    st.session_state.decision_history.append({"node": node_id, "choice": label})
    apply_effects(choice.get("effects"))
    if choice.get("irreversible"):
        st.session_state.history = []
        add_log("This decision is irreversible. You cannot undo beyond this point.")
    transition_to(choice["next"])


def get_choice_warnings(choice: Dict[str, Any]) -> List[str]:
    """Return warning messages for irreversible or high-cost choices."""
    warnings: List[str] = []
    effects = choice.get("effects", {})

    if choice.get("irreversible"):
        warnings.append("Irreversible choice: this clears undo history once confirmed.")
    if effects.get("hp", 0) <= -HIGH_COST_HP_LOSS:
        warnings.append(f"High HP cost: {effects['hp']} HP")
    if effects.get("gold", 0) <= -HIGH_COST_GOLD_LOSS:
        warnings.append(f"High gold cost: {effects['gold']} gold")

    return warnings


def apply_morality_flags(flags: Dict[str, Any]) -> None:
    """Keep legacy reputation flags in sync with canonical morality value."""
    morality = flags.get("morality")
    if morality == "merciful":
        flags["mercy_reputation"] = True
        flags["cruel_reputation"] = False
    elif morality == "ruthless":
        flags["mercy_reputation"] = False
        flags["cruel_reputation"] = True


def check_requirements(requirements: Dict[str, Any] | None) -> tuple[bool, str]:
    """Validate requirements against current player state."""
    if not requirements:
        return True, ""

    stats = st.session_state.stats
    inventory = st.session_state.inventory
    flags = st.session_state.flags
    pclass = st.session_state.player_class

    if "class" in requirements and pclass not in requirements["class"]:
        return False, f"Requires class: {', '.join(requirements['class'])}"

    if "min_hp" in requirements and stats["hp"] < requirements["min_hp"]:
        return False, f"Requires HP >= {requirements['min_hp']}"
    if "min_gold" in requirements and stats["gold"] < requirements["min_gold"]:
        return False, f"Requires gold >= {requirements['min_gold']}"
    if "min_strength" in requirements and stats["strength"] < requirements["min_strength"]:
        return False, f"Requires strength >= {requirements['min_strength']}"
    if "min_dexterity" in requirements and stats["dexterity"] < requirements["min_dexterity"]:
        return False, f"Requires dexterity >= {requirements['min_dexterity']}"

    for item in requirements.get("items", []):
        if item not in inventory:
            return False, f"Missing item: {item}"

    for item in requirements.get("missing_items", []):
        if item in inventory:
            return False, f"Already have item: {item}"

    for flag in requirements.get("flag_true", []):
        if not flags.get(flag, False):
            return False, f"Requires flag: {flag}=True"

    for flag in requirements.get("flag_false", []):
        if flags.get(flag, False):
            return False, f"Requires flag: {flag}=False"

    return True, ""


def apply_effects(effects: Dict[str, Any] | None) -> None:
    """Apply deterministic choice outcomes to player state."""
    if not effects:
        return

    stats = st.session_state.stats
    inventory = st.session_state.inventory
    flags = st.session_state.flags
    traits = st.session_state.traits
    feedback: List[str] = []

    for stat in ["hp", "gold", "strength", "dexterity"]:
        if stat in effects:
            stats[stat] += effects[stat]

    for item in effects.get("add_items", []):
        if item not in inventory:
            inventory.append(item)

    for item in effects.get("remove_items", []):
        if item in inventory:
            inventory.remove(item)

    for key, value in effects.get("set_flags", {}).items():
        flags[key] = value
        feedback.append(f"World state changed: {key} → {value}")

    for trait, delta in effects.get("trait_delta", {}).items():
        if trait in traits:
            traits[trait] += delta
            sign = "+" if delta >= 0 else ""
            feedback.append(f"Trait shift: {trait} {sign}{delta}")

    for event in effects.get("seen_events", []):
        if event not in st.session_state.seen_events:
            st.session_state.seen_events.append(event)
            feedback.append(f"Key event recorded: {event}")

    apply_morality_flags(flags)

    if effects.get("log"):
        add_log(effects["log"])

    st.session_state.last_choice_feedback = feedback


def transition_to(next_node_id: str) -> None:
    """Move to the next node, handling missing IDs and death checks."""
    if st.session_state.stats["hp"] <= 0:
        st.session_state.current_node = "death"
        add_log("Your HP dropped to 0. You collapse before the quest can be completed.")
        return

    if next_node_id not in STORY_NODES:
        st.session_state.current_node = "death"
        add_log(f"Broken path: node '{next_node_id}' was missing. Your story ends abruptly.")
        return

    st.session_state.current_node = next_node_id


def validate_story_nodes() -> List[str]:
    """Run lightweight static validation over story graph links."""
    warnings: List[str] = []
    for node_id, node in STORY_NODES.items():
        if node.get("id") != node_id:
            warnings.append(f"Node key '{node_id}' does not match its id field '{node.get('id')}'.")

        for choice in node.get("choices", []):
            next_id = choice.get("next")
            if next_id not in STORY_NODES:
                warnings.append(
                    f"Choice '{choice.get('label', 'unnamed')}' in node '{node_id}' points to missing node '{next_id}'."
                )
    return warnings


def get_available_choices(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return choices that pass requirements for display and interaction."""
    valid_choices = []
    for choice in node.get("choices", []):
        is_valid, _ = check_requirements(choice.get("requirements"))
        if is_valid:
            valid_choices.append(choice)
    return valid_choices


def render_sidebar() -> None:
    """Render persistent player information in the sidebar."""
    with st.sidebar:
        st.header("Adventurer")
        st.write(f"**Class:** {st.session_state.player_class}")

        st.subheader("Stats")
        st.write(f"HP: {st.session_state.stats['hp']}")
        st.write(f"Gold: {st.session_state.stats['gold']}")
        st.write(f"Strength: {st.session_state.stats['strength']}")
        st.write(f"Dexterity: {st.session_state.stats['dexterity']}")

        st.subheader("Inventory")
        if st.session_state.inventory:
            for item in st.session_state.inventory:
                st.write(f"- {item}")
        else:
            st.write("(empty)")

        st.subheader("Flags")
        if st.session_state.flags:
            for key, value in sorted(st.session_state.flags.items()):
                st.write(f"- {key}: {value}")
        else:
            st.write("(none)")

        st.subheader("Traits")
        for trait in TRAIT_KEYS:
            st.write(f"{trait.title()}: {st.session_state.traits[trait]}")

        st.subheader("Key Events Seen")
        if st.session_state.seen_events:
            for event in st.session_state.seen_events[-6:]:
                st.write(f"- {event}")
        else:
            st.write("(none)")

        st.divider()
        if st.button("⬅️ Back (undo last choice)", use_container_width=True, disabled=not st.session_state.history):
            previous = st.session_state.history.pop()
            load_snapshot(previous)
            add_log("You retrace your steps and reconsider your decision.")
            st.rerun()

        with st.expander("Save / Load", expanded=False):
            if st.button("Export current state", use_container_width=True):
                st.session_state.save_blob = json.dumps(snapshot_state(), indent=2)

            save_text = st.text_area(
                "State JSON",
                value=st.session_state.save_blob,
                height=180,
                key="save_load_text",
            )
            if st.button("Import state", use_container_width=True):
                try:
                    payload = json.loads(save_text)
                    required_keys = {
                        "player_class",
                        "current_node",
                        "stats",
                        "inventory",
                        "flags",
                        "event_log",
                        "traits",
                        "seen_events",
                        "decision_history",
                        "last_choice_feedback",
                    }
                    if not required_keys.issubset(payload.keys()):
                        st.error("Invalid save: missing required keys.")
                    elif payload["current_node"] not in STORY_NODES:
                        st.error("Invalid save: current node does not exist.")
                    else:
                        load_snapshot(payload)
                        apply_morality_flags(st.session_state.flags)
                        st.success("State imported successfully.")
                        st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON. Please paste a valid exported state.")

        st.divider()
        if st.button("Restart Game", use_container_width=True):
            reset_game_state()
            st.rerun()


def render_node() -> None:
    """Render current node, narrative, choices, and edge-case handling."""
    node_id = st.session_state.current_node
    if node_id not in STORY_NODES:
        st.error(f"Missing node '{node_id}'.")
        transition_to("death")
        st.rerun()
        return

    node = STORY_NODES[node_id]

    # Gate access to nodes that have node-level requirements.
    node_ok, node_reason = check_requirements(node.get("requirements"))
    if not node_ok:
        st.error(f"You cannot access this path: {node_reason}")
        transition_to("death")
        st.rerun()
        return

    st.title(node["title"])
    st.write(node["text"])

    if st.session_state.last_choice_feedback:
        with st.container(border=True):
            st.caption("Consequence feedback")
            for line in st.session_state.last_choice_feedback:
                st.write(f"• {line}")

    # Death can happen from previous choice effects.
    if st.session_state.stats["hp"] <= 0:
        transition_to("death")
        st.rerun()
        return

    choices = node.get("choices", [])
    available_choices = get_available_choices(node)

    if not choices:
        st.success("The story has reached an ending. Restart to explore another path.")
        return

    st.subheader("What do you do?")
    pending = st.session_state.pending_choice_confirmation

    if pending and pending.get("node") == node_id:
        with st.container(border=True):
            st.warning(f"Confirm choice: **{pending['label']}**")
            for warning in pending.get("warnings", []):
                st.write(f"- ⚠️ {warning}")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("Confirm risky choice", type="primary", key=f"confirm_{node_id}", use_container_width=True):
                    choice_index = pending["choice_index"]
                    if 0 <= choice_index < len(available_choices):
                        selected = available_choices[choice_index]
                        execute_choice(node_id, selected["label"], selected)
                    st.rerun()
            with col_cancel:
                if st.button("Cancel", key=f"cancel_{node_id}", use_container_width=True):
                    st.session_state.pending_choice_confirmation = None
                    st.rerun()

    for idx, choice in enumerate(available_choices):
        label = choice["label"]
        warnings = get_choice_warnings(choice)
        display_label = f"⚠️ {label}" if warnings else label
        if st.button(display_label, key=f"choice_{node_id}_{idx}", use_container_width=True):
            if warnings:
                st.session_state.pending_choice_confirmation = {
                    "node": node_id,
                    "choice_index": idx,
                    "label": label,
                    "warnings": warnings,
                }
            else:
                execute_choice(node_id, label, choice)
            st.rerun()

    if not available_choices:
        st.warning("No valid choices remain based on your current stats, items, and flags.")
        if st.button("Accept your fate", type="primary"):
            transition_to("death")
            st.rerun()


def render_log() -> None:
    """Show the most recent narrative events."""
    with st.expander("Recent Event Log (last 10)", expanded=False):
        recent = st.session_state.event_log[-10:]
        if not recent:
            st.write("No events yet.")
        else:
            for entry in recent:
                st.write(f"- {entry}")


def format_requirements(requirements: Dict[str, Any] | None) -> str:
    """Convert requirements dict into readable bullet-style text."""
    if not requirements:
        return "None"

    details: List[str] = []
    if "class" in requirements:
        details.append(f"Class: {', '.join(requirements['class'])}")
    if "min_hp" in requirements:
        details.append(f"HP >= {requirements['min_hp']}")
    if "min_gold" in requirements:
        details.append(f"Gold >= {requirements['min_gold']}")
    if "min_strength" in requirements:
        details.append(f"Strength >= {requirements['min_strength']}")
    if "min_dexterity" in requirements:
        details.append(f"Dexterity >= {requirements['min_dexterity']}")
    if requirements.get("items"):
        details.append(f"Needs items: {', '.join(requirements['items'])}")
    if requirements.get("missing_items"):
        details.append(f"Must not have: {', '.join(requirements['missing_items'])}")
    if requirements.get("flag_true"):
        details.append(f"Flags true: {', '.join(requirements['flag_true'])}")
    if requirements.get("flag_false"):
        details.append(f"Flags false: {', '.join(requirements['flag_false'])}")

    return " | ".join(details) if details else "None"


def format_outcomes(effects: Dict[str, Any] | None) -> str:
    """Convert effects dict into readable outcome summary."""
    if not effects:
        return "No direct effect"

    details: List[str] = []
    for stat in ["hp", "gold", "strength", "dexterity"]:
        if stat in effects:
            value = effects[stat]
            sign = "+" if value >= 0 else ""
            details.append(f"{stat.upper()} {sign}{value}")

    if effects.get("add_items"):
        details.append(f"Add items: {', '.join(effects['add_items'])}")
    if effects.get("remove_items"):
        details.append(f"Remove items: {', '.join(effects['remove_items'])}")
    if effects.get("set_flags"):
        flag_updates = ", ".join([f"{k}={v}" for k, v in effects["set_flags"].items()])
        details.append(f"Set flags: {flag_updates}")
    if effects.get("log"):
        details.append(f"Narrative: {effects['log']}")

    return " | ".join(details) if details else "No direct effect"


def render_choice_outcomes_tab() -> None:
    """Render a separate tab that lists every node choice and its outcomes."""
    st.subheader("All Choices & Outcomes")
    st.caption("A full reference of every choice path, requirements, and deterministic outcomes.")

    for node_id, node in STORY_NODES.items():
        choices = node.get("choices", [])
        if not choices:
            continue

        with st.expander(f"{node['title']} ({node_id})", expanded=False):
            for idx, choice in enumerate(choices, start=1):
                st.markdown(f"**{idx}. {choice['label']}**")
                st.write(f"- **Requirements:** {format_requirements(choice.get('requirements'))}")
                st.write(f"- **Outcome:** {format_outcomes(choice.get('effects'))}")
                st.write(f"- **Next node:** `{choice['next']}`")
                st.write("---")


def ensure_session_state() -> None:
    """Initialize session state keys on first load."""
    if "player_class" not in st.session_state:
        reset_game_state()
    if "history" not in st.session_state:
        st.session_state.history = []
    if "save_blob" not in st.session_state:
        st.session_state.save_blob = ""
    if "traits" not in st.session_state:
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
    if "seen_events" not in st.session_state:
        st.session_state.seen_events = []
    if "decision_history" not in st.session_state:
        st.session_state.decision_history = []
    if "last_choice_feedback" not in st.session_state:
        st.session_state.last_choice_feedback = []
    if "pending_choice_confirmation" not in st.session_state:
        st.session_state.pending_choice_confirmation = None


# -----------------------------
# App entry point
# -----------------------------
def main() -> None:
    st.set_page_config(page_title="Oakrest: Deterministic Adventure", page_icon="🛡️", layout="centered")
    ensure_session_state()
    for warning in validate_story_nodes():
        st.warning(f"Story validator: {warning}")

    st.caption("A deterministic D&D-style choice adventure. No dice, only decisions.")

    if st.session_state.player_class is None:
        st.title("Oakrest: Choose Your Class")
        st.write(
            "Oakrest needs a hero. Your class changes available paths and solutions throughout the story."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Warrior", use_container_width=True, type="primary"):
                start_game("Warrior")
                st.rerun()
        with col2:
            if st.button("Rogue", use_container_width=True, type="primary"):
                start_game("Rogue")
                st.rerun()

        st.markdown("**Warrior:** higher HP and Strength, excels at brute-force paths.")
        st.markdown("**Rogue:** higher Dexterity and stealth options, excels at subtle paths.")
        return

    render_sidebar()

    tab_story, tab_choices = st.tabs(["Story", "Choices & Outcomes"])
    with tab_story:
        render_node()
        render_log()
    with tab_choices:
        render_choice_outcomes_tab()


if __name__ == "__main__":
    main()


# -----------------------------
# README (quick start)
# -----------------------------
# 1) pip install streamlit
# 2) streamlit run app.py
