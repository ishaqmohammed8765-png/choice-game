from typing import Any, Dict

STAT_KEYS = ("hp", "gold", "strength", "dexterity")
TRAIT_KEYS = ("trust", "reputation", "alignment")
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
    "Archer": {
        "hp": 12,
        "gold": 9,
        "strength": 3,
        "dexterity": 3,
        "inventory": ["Shortbow", "Quiver of Arrows"],
    },
}


STORY_NODES: Dict[str, Dict[str, Any]] = {
    "village_square": {
        "id": "village_square",
        "title": "Oakrest Village Square",
        "text": (
            "The bell of Oakrest tolls at dusk. Smoke from the outer farms hangs over the square while frightened "
            "families gather beneath boarded windows. Villagers whisper of raiders, a cursed ruin in the forest, "
            "and a missing relic known as the Dawn Emblem. Elder Mara asks you to track the threat before nightfall."
        ),
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Oakrest has one night left before panic turns to bloodshed."},
            {"speaker": "Blacksmith Tor", "line": "If the roads fall, we fall with them. Bring us sunrise."},
        ],
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
            "A retired scout sells practical tools near a safe firepit. Rain ticks against canvas while weary "
            "travelers trade rumors about missing patrols. You can buy gear or patch your wounds before entering deeper wilderness."
        ),
        "dialogue": [
            {"speaker": "Trader Venn", "line": "Pay now, complain later. The forest collects debts in bone."},
            {"speaker": "Tired Ranger", "line": "We lost two scouts at the ruin gate. Keep a light ready."},
        ],
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
            "Pines crowd around a fork in the path. Fresh cart tracks and bloodied cloth mark recent fighting. "
            "To the left: a narrow ravine crossing. To the right: a campfire glow where bandits argue over spoils. "
            "Ahead, war drums echo from the Ashfang warband while silver lanterns of the Rangers flicker between trees."
        ),
        "dialogue": [
            {"speaker": "Unknown Voice", "line": "Pick wrong, and the forest picks your grave."},
        ],
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
            "shield-bearer Nima argue about whether to assault the ruin now or save trapped villagers first. "
            "Every minute of debate is measured against distant screams from the valley road."
        ),
        "dialogue": [
            {"speaker": "Captain Serin", "line": "Choose quickly. We either save the living or stop the fire at its source."},
            {"speaker": "Archivist Pell", "line": "The Emblem is not a relic now; it is a lit fuse."},
        ],
        "choices": [
            {
                "label": "Swear temporary alliance with Captain Serin",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1, "alignment": 1},
                    "set_flags": {"dawnwarden_allied": True, "mercy_reputation": True},
                    "add_items": ["Warden Token"],
                    "log": "Serin clasps your forearm and grants a Warden Token recognized by local patrols.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Ask Archivist Pell for enemy intelligence",
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"knows_enemy_roster": True},
                    "seen_events": ["learned_enemy_roster"],
                    "log": "Pell briefs you on raider ranks: Ember Troopers, Bonebreakers, and the Emblem Warden.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Challenge Nima in a spar to earn respect (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "trait_delta": {"reputation": 2},
                    "set_flags": {"earned_dawnwarden_respect": True},
                    "log": "After a brutal spar, Nima salutes you and marks a safer approach to the gate.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "ashfang_hunt": {
        "id": "ashfang_hunt",
        "title": "Ashfang Hunting Grounds",
        "text": (
            "Warchief Drogath leads the Ashfangs with scout Yara and beast-handler Korr. They stalk a raider "
            "convoy guarded by ember-hounds and masked zealots. The warband invites you to prove yourself before moonrise."
        ),
        "dialogue": [
            {"speaker": "Warchief Drogath", "line": "In our lands, words are wind. Deeds are law."},
            {"speaker": "Scout Yara", "line": "Show me clean hands in a dirty war, outsider."},
        ],
        "choices": [
            {
                "label": "Join the ambush and crush the convoy (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "hp": -1,
                    "gold": 4,
                    "trait_delta": {"trust": -1, "reputation": 2, "alignment": -1},
                    "set_flags": {"ashfang_allied": True, "cruel_reputation": True},
                    "seen_events": ["ashfang_convoy_slain"],
                    "log": "You and Drogath tear through raiders and scatter ember-hounds into the dark.",
                },
                "next": "war_council_hub",
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
                "next": "war_council_hub",
            },
            {
                "label": "Refuse bloodshed and guide prisoners to safety",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1, "alignment": 2},
                    "set_flags": {"rescued_prisoners": True, "mercy_reputation": True},
                    "log": "You escort shaken prisoners away while the warband fights on without you.",
                },
                "next": "war_council_hub",
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
        "dialogue": [
            {"speaker": "Your Instinct", "line": "Move now. The bridge won't offer a second warning."},
            {"speaker": "Wind Over Stone", "line": "One mistake, and the ravine keeps what it takes."},
        ],
        "choices": [
            {
                "label": "Leap and cling to the far ledge (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "trait_delta": {"reputation": 1},
                    "set_flags": {"ravine_crossed_clean": True},
                    "log": "You catch the ledge with iron grip and pull yourself up.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Take the fall and climb out",
                "effects": {
                    "hp": -3,
                    "trait_delta": {"trust": -1},
                    "set_flags": {"ravine_injured": True},
                    "log": "You hit the ravine floor hard before scrambling back up.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "bandit_camp": {
        "id": "bandit_camp",
        "title": "Bandit Camp",
        "text": (
            "Three bandits surround a bound scout from Oakrest. Their leader, Kest, kicks a broken lantern into the mud "
            "and offers a bargain: leave the scout and walk away with coin, or interfere and spill blood."
        ),
        "dialogue": [
            {"speaker": "Kest", "line": "This one dies either way. Only question is whether you get paid."},
            {"speaker": "Bound Scout", "line": "Don't buy his lie. The ruin is ready to burn Oakrest."},
        ],
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
                "next": "war_council_hub",
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
        "dialogue": [
            {"speaker": "Rescued Scout", "line": "They've rigged the core chamber. If you hear bells, run."},
            {"speaker": "Rescued Scout", "line": "Take this seal. It's older than fear, and twice as stubborn."},
        ],
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
                "next": "war_council_hub",
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
                "effects": {
                    "trait_delta": {"reputation": -1},
                    "log": "You refuse the token and press onward.",
                },
                "next": "war_council_hub",
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
        "dialogue": [
            {"speaker": "Echoing Voices", "line": "Someone's still down here... or the tunnel remembers them."},
            {"speaker": "Your Instinct", "line": "This choice wins time, but it might cost lives."},
        ],
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
                "next": "war_council_hub",
            },
            {
                "label": "Leave the supports intact and continue quietly",
                "effects": {
                    "trait_delta": {"trust": 1, "alignment": 1},
                    "seen_events": ["tunnel_spared"],
                    "log": "You preserve the passage, choosing caution over collateral damage.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "war_council_hub": {
        "id": "war_council_hub",
        "title": "War Council at Ember Ridge",
        "text": (
            "Trails from every skirmish converge at Ember Ridge, where scouts trade reports before the final push. "
            "Allies and rivals judge you by what you've done: spared lives, won respect, or ruled through fear. "
            "Your next move decides who stands with you at the ruin gate."
        ),
        "dialogue": [
            {"speaker": "Signal Runner", "line": "Everyone's waiting on your call. Pick a plan and own the cost."},
            {"speaker": "Your Instinct", "line": "This is the hinge point. Past choices are now present weapons."},
        ],
        "choices": [
            {
                "label": "Coordinate a lawful breach with Dawnwarden support",
                "requirements": {"flag_true": ["dawnwarden_allied"]},
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"opened_cleanly": True, "hub_plan": "dawnwarden_breach"},
                    "log": "Serin's rangers secure the perimeter and hand you a clear line to the gate.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Lead an intimidation push with Ashfang veterans",
                "requirements": {"flag_true": ["ashfang_allied"]},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"reputation": 2, "alignment": -1},
                    "set_flags": {"cruel_reputation": True, "hub_plan": "ashfang_push"},
                    "log": "Ashfang drums break enemy nerve, but the assault leaves casualties in its wake.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Use scout intelligence to approach through the hidden tunnel",
                "requirements": {"flag_true": ["knows_hidden_route"]},
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"hub_plan": "hidden_route"},
                    "log": "You trust the scout's map and steer the strike team underground.",
                },
                "next": "hidden_tunnel",
            },
            {
                "label": "Rally survivors you rescued to create a diversion",
                "requirements": {"flag_true": ["rescued_prisoners"]},
                "effects": {
                    "trait_delta": {"trust": 1, "alignment": 1},
                    "set_flags": {"mercy_reputation": True, "hub_plan": "survivor_diversion"},
                    "log": "Freed prisoners light decoy fires, drawing raiders off your intended route.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Advance alone before reinforcements arrive",
                "effects": {
                    "trait_delta": {"reputation": -1},
                    "set_flags": {"hub_plan": "solo_push"},
                    "log": "You reject every banner and move on the ruin with only your own judgment.",
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
        "dialogue": [
            {"speaker": "Ruin Lookout", "line": "Last warning, traveler. This door eats heroes."},
            {"speaker": "Your Instinct", "line": "Every path in is a promise you'll have to keep."},
        ],
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
        "dialogue": [
            {"speaker": "Ancient Inscription", "line": "Only the careful walk twice these halls."},
            {"speaker": "Distant Raider", "line": "Check the gallery again! Someone's inside!"},
        ],
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
        "dialogue": [
            {"speaker": "Kest", "line": "I sold lies, not villages. Don't let me die for their fire."},
            {"speaker": "Your Instinct", "line": "Mercy can save a soul, or sharpen a knife in your back."},
        ],
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
            "In the heart of the ruin, the armored Warden channels power into the Dawn Emblem. Cracks of molten light "
            "spread across the chamber ceiling as the relic begins to overload. You must stop the device before Oakrest burns."
        ),
        "dialogue": [
            {"speaker": "Ruin Warden", "line": "Witness the old kingdom's dawn reborn in fire."},
            {"speaker": "You", "line": "No more villages burn because of you. It ends here."},
        ],
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
                "instant_death": True,
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
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Oakrest sees the sunrise because you stood when others broke."},
        ],
        "choices": [],
    },
    "ending_best_warrior": {
        "id": "ending_best_warrior",
        "title": "Best Ending — Iron Dawn of Oakrest",
        "text": (
            "Your warrior's stand saves both the Dawn Emblem and the trapped villagers. Word spreads that you held "
            "a collapsing ruin with your bare strength, and Oakrest names you Shield of the Valley."
        ),
        "dialogue": [
            {"speaker": "Blacksmith Tor", "line": "I've never seen stone obey a person, until tonight."},
        ],
        "choices": [],
    },
    "ending_best_rogue": {
        "id": "ending_best_rogue",
        "title": "Best Ending — Silent Dawn of Oakrest",
        "text": (
            "Your rogue precision prevents the surge before anyone else even sees the danger. The Rangers record the "
            "night as a flawless victory, and Oakrest entrusts you with its hidden defenses."
        ),
        "dialogue": [
            {"speaker": "Captain Serin", "line": "No trumpet, no glory march—just perfect work. That's legend enough."},
        ],
        "choices": [],
    },
    "ending_mixed": {
        "id": "ending_mixed",
        "title": "Ending — Victory at a Cost",
        "text": (
            "The Warden falls, but the ruin partially collapses and nearby farms are lost in the aftermath. "
            "Oakrest survives, though your name is spoken with equal gratitude and regret."
        ),
        "dialogue": [
            {"speaker": "Villager", "line": "We lived... but the valley won't forget the price."},
        ],
        "choices": [],
    },
    "ending_bad": {
        "id": "ending_bad",
        "title": "Ending — Nightfall Over Oakrest",
        "text": (
            "Your final gamble fails. The device surges to full power and the forest burns with unnatural fire. "
            "Oakrest is abandoned by sunrise, and your tale becomes a warning."
        ),
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Remember this night, so we never choose it again."},
        ],
        "choices": [],
    },
    "failure_injured": {
        "id": "failure_injured",
        "title": "Setback — Broken but Breathing",
        "text": (
            "You wake in a healer's lean-to, battered and stitched. You lost momentum, but Oakrest still needs you. "
            "Choose how you re-enter the conflict."
        ),
        "dialogue": [
            {"speaker": "Healer Brin", "line": "Pain means you're still in the fight. Decide fast."},
        ],
        "choices": [
            {
                "label": "Recover slowly and return to the village supply line",
                "effects": {
                    "hp": 4,
                    "set_flags": {"recovered_from_injury": True},
                    "log": "Days pass in recovery. You return with fewer scars than rage.",
                },
                "next": "camp_shop",
            },
            {
                "label": "Push through the pain and rejoin the assault route",
                "effects": {
                    "hp": 2,
                    "trait_delta": {"reputation": 1},
                    "log": "You grit your teeth, bind your wounds, and march back toward the ruin.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "failure_captured": {
        "id": "failure_captured",
        "title": "Setback — Captured Alive",
        "text": (
            "Raiders drag you into a holding pit beneath the ruin. A loose grate and distracted guard offer "
            "dangerous chances to break free."
        ),
        "dialogue": [
            {"speaker": "Guard", "line": "Don't bother screaming. Stone doesn't care."},
            {"speaker": "Prisoner", "line": "If you're planning something, make it count."},
        ],
        "choices": [
            {
                "label": "Bribe a guard with hidden coin",
                "requirements": {"min_gold": 3},
                "effects": {
                    "gold": -3,
                    "set_flags": {"escaped_capture": True},
                    "log": "A guard pockets your coin and leaves the latch unfastened.",
                },
                "next": "inner_hall",
            },
            {
                "label": "Force the grate and climb out",
                "requirements": {"min_strength": 3},
                "effects": {
                    "hp": -1,
                    "set_flags": {"escaped_capture": True},
                    "log": "You rip the rusted grate loose and climb out bloodied but free.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Feign loyalty to buy time",
                "instant_death": True,
                "effects": {
                    "set_flags": {"marked_suspect": True},
                    "trait_delta": {"alignment": -1},
                    "log": "Your deception is exposed, and the pit execution is immediate.",
                },
                "next": "core_approach",
            },
        ],
    },
    "failure_traitor": {
        "id": "failure_traitor",
        "title": "Setback — Branded a Traitor",
        "text": (
            "Rumors paint you as a double-agent. Allies hesitate, gates close, and every decision now carries social risk."
        ),
        "dialogue": [
            {"speaker": "Whispering Crowd", "line": "Hero? Traitor? Depends who survived your choices."},
        ],
        "choices": [
            {
                "label": "Seek Captain Serin and prove your intent",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1},
                    "set_flags": {"traitor_brand_cleared": True, "mercy_reputation": True},
                    "log": "You expose forged reports and Serin restores your standing.",
                },
                "next": "dawnwarden_outpost",
            },
            {
                "label": "Work alone through hidden routes",
                "effects": {
                    "trait_delta": {"trust": -1, "reputation": 1},
                    "set_flags": {"traitor_brand_hardened": True, "knows_hidden_route": True},
                    "log": "You stop waiting for forgiveness and carve your own path forward.",
                },
                "next": "hidden_tunnel",
            },
        ],
    },
    "failure_resource_loss": {
        "id": "failure_resource_loss",
        "title": "Setback — Supplies Lost",
        "text": (
            "A failed push costs you supplies and support. You can regroup for stability or gamble on a faster return."
        ),
        "dialogue": [
            {"speaker": "Trader Venn", "line": "You can borrow from me once. After that, the forest collects."},
        ],
        "choices": [
            {
                "label": "Regroup at the roadside camp",
                "effects": {
                    "gold": -2,
                    "hp": 2,
                    "log": "You rebuild your kit from scraps and favors at the campfire.",
                },
                "next": "camp_shop",
            },
            {
                "label": "Call in old favors from the Ashfang scouts",
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"met_ashfang": True},
                    "log": "Ashfang outriders throw you a line and point you back to the hunt.",
                },
                "next": "ashfang_hunt",
            },
        ],
    },
    "death": {
        "id": "death",
        "title": "You Have Fallen",
        "text": (
            "Your wounds are too severe. The quest ends here, and the fate of Oakrest passes to another soul."
        ),
        "dialogue": [
            {"speaker": "Final Thought", "line": "If dawn comes, let it find Oakrest standing."},
        ],
        "choices": [],
    },
}


# -----------------------------
# State and game logic helpers
# -----------------------------
