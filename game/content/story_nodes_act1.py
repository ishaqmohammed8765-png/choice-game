from typing import Any, Dict

STORY_NODES_ACT1: Dict[str, Dict[str, Any]] = {
    "village_square": {
        "id": "village_square",
        "title": "Oakrest Village Square",
        "text": (
            "The bell of Oakrest tolls at dusk. Smoke from the outer farms hangs over the square while frightened "
            "families gather beneath boarded windows. Villagers whisper of raiders, a cursed ruin in the forest, "
            "and a missing relic known as the Dawn Emblem. A bloodstained order nailed to the chapel door bears one "
            "signature: Warden Caldus, sworn to 'rekindle dawn through fire.' Elder Mara asks you to track the threat "
            "before nightfall."
        ),
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Oakrest has one night left before panic turns to bloodshed."},
            {"speaker": "Blacksmith Tor", "line": "If the roads fall, we fall with them. Bring us sunrise."},
            {"speaker": "Signal Runner Tams", "line": "Every patrol report carries that same Warden seal now."},
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
                "label": "Train at Tor's forge yard (+1 Strength, 4 gold)",
                "requirements": {"min_gold": 4, "flag_false": ["trained_strength_once"]},
                "effects": {
                    "gold": -4,
                    "strength": 1,
                    "set_flags": {"trained_strength_once": True},
                    "log": "Hours of hammer drills and shield carries leave you stronger for the road ahead.",
                },
                "next": "village_square",
            },
            {
                "label": "Run scout footwork drills behind the chapel (+1 Dexterity, 4 gold)",
                "requirements": {"min_gold": 4, "flag_false": ["trained_dexterity_once"]},
                "effects": {
                    "gold": -4,
                    "dexterity": 1,
                    "set_flags": {"trained_dexterity_once": True},
                    "log": "You practice quick steps and low movement lanes until your reactions sharpen.",
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
                "label": "Spar with a retired legionnaire (+1 Strength, 5 gold)",
                "requirements": {
                    "class": ["Warrior"],
                    "min_gold": 5,
                    "flag_false": ["camp_strength_training_done"],
                },
                "effects": {
                    "gold": -5,
                    "strength": 1,
                    "set_flags": {"camp_strength_training_done": True},
                    "log": "A brutal round of drills hardens your stance and power.",
                },
                "next": "camp_shop",
            },
            {
                "label": "Practice night marksmanship and quick draws (+1 Dexterity, 5 gold)",
                "requirements": {
                    "class": ["Rogue", "Archer"],
                    "min_gold": 5,
                    "flag_false": ["camp_dexterity_training_done"],
                },
                "effects": {
                    "gold": -5,
                    "dexterity": 1,
                    "set_flags": {"camp_dexterity_training_done": True},
                    "log": "Under lantern light, you refine snap reactions and precision.",
                },
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
            {"speaker": "Scout Iven", "line": "Every trail here writes a different ending. Choose what you're willing to own."},
            {"speaker": "Drum-Echo", "line": "Ignore a threat now, and it will remember your name later."},
            {"speaker": "Signal Runner Tams", "line": "Caldus isn't raiding for gold. He's gathering fuel for something bigger at Ember Ridge."},
        ],
        "choices": [
            {
                "label": "Cross the ravine (Strength 4 or Rope)",
                "requirements": {
                    "any_of": [
                        {"min_strength": 4, "flag_false": ["branch_ravine_completed"]},
                        {"items": ["Rope"], "flag_false": ["branch_ravine_completed"]},
                    ]
                },
                "conditional_effects": [
                    {
                        "requirements": {"min_strength": 4, "flag_false": ["branch_ravine_completed"]},
                        "effects": {
                            "strength": 1,
                            "log": "Your raw force carries you across the groaning beams and leaves your arms battle-hardened.",
                            "set_flags": {"branch_ravine_completed": True},
                        },
                    },
                    {
                        "requirements": {"items": ["Rope"], "flag_false": ["branch_ravine_completed"]},
                        "effects": {
                            "log": "You anchor your rope and swing across the ravine safely.",
                            "set_flags": {"used_rope_crossing": True, "branch_ravine_completed": True},
                        },
                    },
                ],
                "next": "ravine_crossing",
            },
            {
                "label": "Approach the bandit camp (sneak, misdirect, or march)",
                "requirements": {
                    "any_of": [
                        {"min_dexterity": 4, "flag_false": ["branch_bandit_completed"]},
                        {"class": ["Rogue"], "flag_false": ["branch_bandit_completed"]},
                        {"min_strength": 3, "flag_false": ["branch_bandit_completed"]},
                    ]
                },
                "conditional_effects": [
                    {
                        "requirements": {"class": ["Rogue"], "flag_false": ["branch_bandit_completed"]},
                        "effects": {
                            "trait_delta": {"reputation": 1, "trust": 1},
                            "set_flags": {"branch_bandit_completed": True, "false_tracks_set": True},
                            "seen_events": ["rogue_false_tracks"],
                            "log": "Your decoys split the camp patrols before you slip in to face Kest.",
                        },
                    },
                    {
                        "requirements": {"min_dexterity": 4, "flag_false": ["branch_bandit_completed"]},
                        "effects": {
                            "dexterity": 1,
                            "log": "You melt into the brush and approach unheard, sharpening your movement control.",
                            "set_flags": {"branch_bandit_completed": True},
                        },
                    },
                    {
                        "requirements": {"min_strength": 3, "flag_false": ["branch_bandit_completed"]},
                        "effects": {
                            "log": "Branches crack under your boots as you confront the raiders openly.",
                            "set_flags": {"branch_bandit_completed": True},
                        },
                    },
                ],
                "next": "bandit_camp",
            },
            {
                "label": "Open your field map for side operations and support missions",
                "effects": {
                    "log": "You kneel at a stump, spread your map, and review side operations before the final push.",
                },
                "next": "forest_crossroad_operations",
            },
            {
                "label": "Survey faction fronts and warband movement",
                "effects": {"log": "You study fresh tracks and distant signal lights before choosing a faction front."},
                "next": "forest_crossroad_fronts",
            },
            {
                "label": "Leave the crossroads and commit your gathered allies to Ember Ridge",
                "requirements": {"flag_true": ["any_branch_completed"]},
                "effects": {
                    "set_flags": {"midgame_commitment_made": True},
                    "log": "After scouting multiple fronts, you call your banners and move to Ember Ridge.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "forest_crossroad_fronts": {
        "id": "forest_crossroad_fronts",
        "title": "Forest Crossroad - Faction Fronts",
        "text": (
            "You shift away from the central fork and watch the valley fronts unfold: ranger lanterns in one direction, "
            "Ashfang war drums in another, and side roads where fresh threats keep emerging."
        ),
        "dialogue": [
            {"speaker": "Scout Iven", "line": "Pick a front and finish it hard. Half-measures become tomorrow's ambush."}
        ],
        "choices": [
            {
                "label": "Follow the ranger lanterns to their hidden outpost",
                "requirements": {"flag_false": ["branch_dawnwarden_completed"]},
                "effects": {
                    "set_flags": {"met_dawnwardens": True, "branch_dawnwarden_completed": True},
                    "log": "You leave the road and follow coded lantern flashes to a concealed ranger camp.",
                },
                "next": "dawnwarden_outpost",
            },
            {
                "label": "Archer route: send a signal arrow to the ranger lantern line",
                "requirements": {"class": ["Archer"], "flag_false": ["branch_dawnwarden_completed"]},
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"branch_dawnwarden_completed": True, "met_dawnwardens": True, "signal_arrow_used": True},
                    "seen_events": ["archer_signal_arrow"],
                    "log": "Your signal arrow lands beside Serin's scouts, earning immediate escort to their outpost.",
                },
                "next": "dawnwarden_outpost",
            },
            {
                "label": "Track the Ashfang war drums into the bramble valley",
                "requirements": {"flag_false": ["branch_ashfang_completed"]},
                "effects": {
                    "set_flags": {"met_ashfang": True, "branch_ashfang_completed": True},
                    "faction_delta": {"ashfang": 1},
                    "log": "You shadow the drumming trail toward an Ashfang hunting column.",
                },
                "next": "ashfang_hunt",
            },
            {
                "label": "Warrior route: answer the war drums with a shield challenge",
                "requirements": {"class": ["Warrior"], "min_strength": 4, "flag_false": ["branch_ashfang_completed"]},
                "effects": {
                    "trait_delta": {"reputation": 2},
                    "faction_delta": {"ashfang": 2},
                    "set_flags": {"branch_ashfang_completed": True, "met_ashfang": True, "ashfang_challenge_answered": True},
                    "seen_events": ["warrior_drum_challenge"],
                    "log": "You meet Drogath's vanguard in open challenge, forcing respect before a word is spoken.",
                },
                "next": "ashfang_hunt",
            },
            {
                "label": "Return to the main crossroads",
                "effects": {"log": "You step back to the central fork and reassess the wider battlefield."},
                "next": "forest_crossroad",
            },
        ],
    },
    "forest_crossroad_operations": {
        "id": "forest_crossroad_operations",
        "title": "Forest Crossroad - Operations Map",
        "text": (
            "You unfold a rain-stained field map marked with ranger shorthand. Secondary fronts and tactical errands "
            "branch from the crossroads, each promising leverage before Ember Ridge."
        ),
        "dialogue": [
            {"speaker": "Scout Iven", "line": "These side routes look optional, until the final battle proves they weren't."},
            {"speaker": "Quartermaster Note", "line": "Supplies, routes, and local favors decide sieges before steel does."},
        ],
        "choices": [
            {
                "label": "Investigate the flooded causeway road",
                "requirements": {"flag_false": ["branch_causeway_completed"]},
                "effects": {
                    "set_flags": {"branch_causeway_completed": True},
                    "log": "You cut through marsh fog toward a drowned causeway where bells still toll underwater.",
                },
                "next": "flooded_causeway_approach",
            },
            {
                "label": "Take the ash-choked mill trail",
                "requirements": {"flag_false": ["branch_mill_completed"]},
                "effects": {
                    "set_flags": {"branch_mill_completed": True},
                    "log": "You follow scorched wheel ruts toward an abandoned mill wrapped in ember smoke.",
                },
                "next": "charred_mill_approach",
            },
            {
                "label": "Scavenge the collapsed scout cache with Rope and Torch",
                "requirements": {"items": ["Rope", "Torch"], "flag_false": ["cache_salvaged"]},
                "effects": {
                    "gold": 4,
                    "trait_delta": {"reputation": 1},
                    "set_flags": {"cache_salvaged": True},
                    "seen_events": ["cache_salvaged_combo"],
                    "log": "Using rope and torch together, you recover a hidden cache that others missed.",
                },
                "next": "forest_crossroad_operations",
            },
            {
                "label": "Follow the whispering chimes to a hidden shrine",
                "requirements": {"min_dexterity": 3, "meta_nodes_present": ["echo_shrine"]},
                "effects": {"log": "You trace the chimes through the brush toward a forgotten shrine."},
                "next": "echo_shrine",
            },
            {
                "label": "Warrior duty: fortify a ranger barricade line",
                "requirements": {"class": ["Warrior"], "flag_false": ["warrior_mid_arc_done"]},
                "effects": {
                    "set_flags": {"warrior_mid_arc_done": True},
                    "log": "You step off-road to harden a weak barricade before nightfall.",
                },
                "next": "warrior_barricade",
            },
            {
                "label": "Rogue duty: investigate a smuggler safehouse",
                "requirements": {"class": ["Rogue"], "flag_false": ["rogue_mid_arc_done"]},
                "effects": {
                    "set_flags": {"rogue_mid_arc_done": True},
                    "log": "You follow coded marks toward a hidden safehouse.",
                },
                "next": "rogue_safehouse",
            },
            {
                "label": "Archer duty: secure a ridgewatch sniper nest",
                "requirements": {"class": ["Archer"], "flag_false": ["archer_mid_arc_done"]},
                "effects": {
                    "set_flags": {"archer_mid_arc_done": True},
                    "log": "You climb toward a windswept ridge to claim a tactical overlook.",
                },
                "next": "archer_ridgewatch",
            },
            {
                "label": "Return to the main crossroads routes",
                "effects": {"log": "You roll up the operations map and step back to the central trails."},
                "next": "forest_crossroad",
            },
        ],
    },
    "echo_shrine": {
        "id": "echo_shrine",
        "title": "Echo Shrine",
        "text": (
            "A mossy shrine sits between leaning pines. Wind chimes ring without a breeze, and a carved locket rests "
            "on the altar as if it has been waiting for your return."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "This is not a gift. It's a promise that the forest remembers you."}
        ],
        "requirements": {"meta_nodes_present": ["echo_shrine"]},
        "choices": [
            {
                "label": "Claim the Echo Locket and let it bind to your story",
                "requirements": {"meta_missing_items": ["Echo Locket"]},
                "effects": {
                    "add_items": ["Echo Locket"],
                    "unlock_meta_items": ["Echo Locket"],
                    "remove_meta_nodes": ["echo_shrine"],
                    "set_flags": {"echo_locket_claimed": True},
                    "log": "The locket hums with every footstep, as if it knows your next journey already.",
                },
                "next": "forest_crossroad_operations",
            },
            {
                "label": "Leave the shrine untouched and step back",
                "effects": {"log": "You leave the shrine intact, the chimes fading behind you."},
                "next": "forest_crossroad_operations",
            },
        ],
    },
    "warrior_barricade": {
        "id": "warrior_barricade",
        "title": "Broken Barricade",
        "text": (
            "A ranger line is moments from collapse under brute pressure. Your presence could hold it or break it."
        ),
        "dialogue": [
            {"speaker": "Serin's Lieutenant", "line": "Hold here and we keep civilians alive until dawn."}
        ],
        "choices": [
            {
                "label": "Hold the line by force",
                "effects": {
                    "hp": -2,
                    "trait_delta": {"reputation": 2},
                    "faction_delta": {"dawnwardens": 2, "oakrest": 1},
                    "set_flags": {"warrior_line_held": True},
                    "log": "Your shield discipline steadies the defenders and buys the valley precious time.",
                },
                "next": "forest_crossroad",
            }
        ],
    },
    "rogue_safehouse": {
        "id": "rogue_safehouse",
        "title": "Smuggler Safehouse",
        "text": (
            "Behind a false wall, smugglers stash maps and coded letters naming both allies and traitors."
        ),
        "dialogue": [
            {"speaker": "Captured Runner", "line": "Every name in that ledger changes who survives this week."}
        ],
        "choices": [
            {
                "label": "Steal intel and leak it to Oakrest",
                "effects": {
                    "trait_delta": {"trust": 1, "alignment": -1},
                    "faction_delta": {"oakrest": 2, "bandits": -2},
                    "set_flags": {"rogue_intel_leaked": True},
                    "seen_events": ["rogue_safehouse_breach"],
                    "log": "You lift the ledger and pass names to Oakrest sentries before dawn.",
                },
                "next": "forest_crossroad",
            }
        ],
    },
    "archer_ridgewatch": {
        "id": "archer_ridgewatch",
        "title": "Ridgewatch Nest",
        "text": (
            "From the ridge, you can relay signals across the valley and redirect patrols before clashes begin."
        ),
        "dialogue": [
            {"speaker": "Lookout Fen", "line": "One arrow in the right place saves ten swords from being drawn."}
        ],
        "choices": [
            {
                "label": "Mark safe lanes and hostile routes",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1},
                    "faction_delta": {"dawnwardens": 1, "oakrest": 1},
                    "set_flags": {"archer_routes_marked": True},
                    "seen_events": ["archer_ridge_signals"],
                    "log": "Your signal work prevents an ambush and keeps both civilians and scouts moving.",
                },
                "next": "forest_crossroad",
            }
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
            {"speaker": "Captain Serin", "line": "My first patrol died buying this map. Don't waste what they paid for."},
            {"speaker": "Archivist Pell", "line": "The Emblem is not a relic now; it is a lit fuse, and I know who lit it."},
            {"speaker": "Shield-Bearer Nima", "line": "Give me a plan with spine, not poetry."},
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
            {"speaker": "Scout Yara", "line": "Show me clean hands in a dirty war, outsider. Mine stopped being clean years ago."},
            {"speaker": "Beast-Handler Korr", "line": "My hounds remember fear. Feed them confidence or feed them meat."},
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
                    "strength": 1,
                    "trait_delta": {"reputation": 1},
                    "set_flags": {"ravine_crossed_clean": True},
                    "log": "You catch the ledge with iron grip, pull yourself up, and feel your power grow.",
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
                    "strength": 1,
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
                    "dexterity": 1,
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
}
