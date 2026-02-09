from typing import Any, Dict

STORY_NODES_ACT1: Dict[str, Dict[str, Any]] = {
    "village_square": {
        "id": "village_square",
        "title": "Oakrest Village Square",
        "text": (
            "The bell of Oakrest tolls at dusk. Smoke from the outer farms hangs over the square while "
            "frightened families shelter beneath boarded windows. Caldus's proclamation is nailed to every "
            "door: 'The old kingdom rises at dawn. Stand aside or burn with the old world.' Elder Mara presses "
            "a purse of emergency coin into your hand and begs you to prepare before the night closes in. "
            "Every hour spent here is an hour Caldus uses to charge the Ember Core."
        ),
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Caldus was our protector once. Now he believes burning us will bring back a kingdom that died centuries ago."},
            {"speaker": "Blacksmith Tor", "line": "His raiders hit the grain stores at midnight. We have until then to be ready."},
            {"speaker": "Signal Runner Tams", "line": "Every patrol report carries that same Warden seal. He's not hiding anymore."},
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
                "label": "Run scout footwork drills behind the training ground (+1 Dexterity, 4 gold)",
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
                "effects": {"log": "You leave Oakrest and follow the shadowed road into the forest. The Ember Tide rises behind you."},
                "next": "forest_crossroad",
            },
        ],
    },
    "camp_shop": {
        "id": "camp_shop",
        "title": "Roadside Trader & Rest Fire",
        "text": (
            "A retired scout tends a firepit beneath oilcloth, selling tools salvaged from Caldus's abandoned "
            "supply caches. Weary travelers swap grim stories about missing patrols and the orange glow "
            "spreading above the treeline. Every purchase here feels like rationing before a siege."
        ),
        "dialogue": [
            {"speaker": "Trader Venn", "line": "Half this gear was Caldus's before he went mad. Ironic you need it to stop him."},
            {"speaker": "Tired Ranger", "line": "We lost two scouts at the ruin gate. Caldus's loyalists don't take prisoners anymore."},
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
            "Pines crowd around a fork in the path. Fresh cart tracks and bloodied cloth mark Caldus's "
            "supply lines. To the left: a ravine where his early experiments cracked the earth. To the "
            "right: a campfire glow where his deserters argue over stolen spoils. Ahead, the war drums "
            "of Drogath's Ashfang warband compete with the coded lantern flashes of Serin's Ironwardens, "
            "the very order Caldus betrayed."
        ),
        "dialogue": [
            {"speaker": "Scout Iven", "line": "Every trail here was carved by Caldus's operations. Choose which thread you pull."},
            {"speaker": "Signal Runner Tams", "line": "Caldus isn't raiding for gold. He's channeling the Ember Core at the ruin. Every hour, the glow gets brighter."},
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
                            "trait_delta": {"ember_tide": 1},
                            "log": "Your raw force carries you across the groaning beams, but the detour costs precious time.",
                            "set_flags": {"branch_ravine_completed": True},
                        },
                    },
                    {
                        "requirements": {"items": ["Rope"], "flag_false": ["branch_ravine_completed"]},
                        "effects": {
                            "trait_delta": {"ember_tide": 1},
                            "log": "You anchor your rope and swing across the ravine safely, though the ember glow brightens while you climb.",
                            "set_flags": {"used_rope_crossing": True, "branch_ravine_completed": True},
                        },
                    },
                ],
                "next": "ravine_crossing",
            },
            {
                "label": "Approach Caldus's deserters at the bandit camp",
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
                            "trait_delta": {"reputation": 1, "trust": 1, "ember_tide": 1},
                            "set_flags": {"branch_bandit_completed": True, "false_tracks_set": True},
                            "seen_events": ["rogue_false_tracks"],
                            "log": "Your decoys split the camp patrols before you slip in to confront Kest.",
                        },
                    },
                    {
                        "requirements": {"min_dexterity": 4, "flag_false": ["branch_bandit_completed"]},
                        "effects": {
                            "dexterity": 1,
                            "trait_delta": {"ember_tide": 1},
                            "log": "You melt into the brush and approach unheard.",
                            "set_flags": {"branch_bandit_completed": True},
                        },
                    },
                    {
                        "requirements": {"min_strength": 3, "flag_false": ["branch_bandit_completed"]},
                        "effects": {
                            "trait_delta": {"ember_tide": 1},
                            "log": "Branches crack under your boots as you confront the deserters openly.",
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
                "label": "Commit your gathered allies and march on the ruin",
                "requirements": {"flag_true": ["any_branch_completed"]},
                "effects": {
                    "set_flags": {"midgame_commitment_made": True},
                    "log": "You call your banners and move toward the ruin. Every step forward is a step the Ember Tide cannot reclaim.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "forest_crossroad_fronts": {
        "id": "forest_crossroad_fronts",
        "title": "Forest Crossroad - Faction Fronts",
        "text": (
            "You shift away from the central fork and watch the valley fronts unfold. To one side, "
            "Serin's Ironwarden lanterns flash coded warnings — the same order Caldus abandoned when "
            "he stole the Emblem. To the other, Drogath's Ashfang war drums beat a rhythm of raw power."
        ),
        "dialogue": [
            {"speaker": "Scout Iven", "line": "Serin wants Caldus brought to justice. Drogath wants him crushed. Pick your instrument."},
        ],
        "choices": [
            {
                "label": "Follow the ranger lanterns to Serin's outpost",
                "requirements": {"flag_false": ["branch_dawnwarden_completed"]},
                "effects": {
                    "set_flags": {"met_dawnwardens": True, "branch_dawnwarden_completed": True},
                    "trait_delta": {"ember_tide": 1},
                    "log": "You follow coded lantern flashes to the concealed camp of the wardens Caldus betrayed.",
                },
                "next": "dawnwarden_outpost",
            },
            {
                "label": "Archer route: send a signal arrow to the ranger lantern line",
                "requirements": {"class": ["Archer"], "flag_false": ["branch_dawnwarden_completed"]},
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1, "ember_tide": 1},
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
                    "trait_delta": {"ember_tide": 1},
                    "log": "You shadow the drumming trail toward Drogath's hunting column.",
                },
                "next": "ashfang_hunt",
            },
            {
                "label": "Warrior route: answer the war drums with a shield challenge",
                "requirements": {"class": ["Warrior"], "min_strength": 4, "flag_false": ["branch_ashfang_completed"]},
                "effects": {
                    "trait_delta": {"reputation": 2, "ember_tide": 1},
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
            "You unfold a rain-stained field map marked with ranger shorthand. Secondary fronts and "
            "tactical errands branch from the crossroads. Each promises leverage against Caldus, but "
            "each costs time the valley may not have."
        ),
        "dialogue": [
            {"speaker": "Scout Iven", "line": "These side routes look optional until the final battle proves they weren't. But Caldus doesn't wait."},
            {"speaker": "Quartermaster Note", "line": "Supplies, routes, and local favors decide sieges before steel does."},
        ],
        "choices": [
            {
                "label": "Investigate the flooded causeway — Sir Edrin's domain",
                "requirements": {"flag_false": ["branch_causeway_completed"]},
                "effects": {
                    "set_flags": {"branch_causeway_completed": True},
                    "log": "You cut through marsh fog toward a drowned causeway where Caldus's old mentor still keeps vigil.",
                },
                "next": "flooded_causeway_approach",
            },
            {
                "label": "Take the ash-choked mill trail — Vorga's forge",
                "requirements": {"flag_false": ["branch_mill_completed"]},
                "effects": {
                    "set_flags": {"branch_mill_completed": True},
                    "log": "You follow scorched wheel ruts toward Vorga's foundry, where Caldus's firebombs are made.",
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
                "label": "Follow the whispering chimes to a hidden hollow",
                "requirements": {"min_dexterity": 3, "meta_nodes_present": ["echo_shrine"]},
                "effects": {"log": "You trace the chimes through the brush toward a forgotten hollow."},
                "next": "echo_shrine",
            },
            {
                "label": "Warrior duty: fortify the barricade line against Caldus's raiders",
                "requirements": {"class": ["Warrior"], "flag_false": ["warrior_mid_arc_done"]},
                "effects": {
                    "set_flags": {"warrior_mid_arc_done": True},
                    "log": "You step off-road to harden a weak barricade before Caldus's next wave hits.",
                },
                "next": "warrior_barricade",
            },
            {
                "label": "Rogue duty: infiltrate a safehouse in Caldus's supply chain",
                "requirements": {"class": ["Rogue"], "flag_false": ["rogue_mid_arc_done"]},
                "effects": {
                    "set_flags": {"rogue_mid_arc_done": True},
                    "log": "You follow coded marks toward a safehouse embedded in Caldus's logistics network.",
                },
                "next": "rogue_safehouse",
            },
            {
                "label": "Archer duty: secure a ridgewatch overlooking Caldus's approach",
                "requirements": {"class": ["Archer"], "flag_false": ["archer_mid_arc_done"]},
                "effects": {
                    "set_flags": {"archer_mid_arc_done": True},
                    "log": "You climb toward a windswept ridge that commands Caldus's supply route.",
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
        "title": "Echo Hollow",
        "text": (
            "A mossy hollow sits between leaning pines. Wind chimes ring without a breeze, and a carved "
            "locket rests on a stone dais as if it has been waiting for your return."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "This is not a gift. It's a promise that the forest remembers you."},
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
                "label": "Leave the hollow untouched and step back",
                "effects": {"log": "You leave the hollow intact, the chimes fading behind you."},
                "next": "forest_crossroad_operations",
            },
        ],
    },
    "warrior_barricade": {
        "id": "warrior_barricade",
        "title": "Broken Barricade",
        "text": (
            "A ranger line is moments from collapse under pressure from Caldus's ember troopers. "
            "Serin's lieutenant recognizes you and begs for help. The barricade guards the only "
            "civilian corridor left — if it falls, families die on the road."
        ),
        "dialogue": [
            {"speaker": "Serin's Lieutenant", "line": "Hold here and we keep civilians alive until dawn. Caldus's troopers don't stop."},
            {"speaker": "Your Instinct", "line": "This line breaks or holds on your back. Choose how to carry it."},
        ],
        "choices": [
            {
                "label": "Hold the line by brute force, absorbing every hit",
                "effects": {
                    "hp": -2,
                    "trait_delta": {"reputation": 2, "ember_tide": 1},
                    "faction_delta": {"ironwardens": 2, "oakrest": 1},
                    "set_flags": {"warrior_line_held": True, "warrior_barricade_method": "force"},
                    "log": "Your shield discipline steadies the defenders and buys the valley precious hours.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Rally the rangers into a disciplined fallback, trading ground for lives",
                "effects": {
                    "hp": -1,
                    "trait_delta": {"trust": 2, "alignment": 1, "ember_tide": 1},
                    "faction_delta": {"ironwardens": 1, "oakrest": 2},
                    "set_flags": {"warrior_line_held": True, "warrior_barricade_method": "fallback"},
                    "log": "You give ground slowly, saving every defender as you retreat to a stronger position.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Charge the ember troopers alone to break their morale (Strength 5)",
                "requirements": {"min_strength": 5},
                "effects": {
                    "hp": -3,
                    "strength": 1,
                    "trait_delta": {"reputation": 3, "alignment": -1, "ember_tide": 1},
                    "faction_delta": {"ironwardens": 1, "ashfang": 1},
                    "set_flags": {"warrior_line_held": True, "warrior_barricade_method": "charge"},
                    "seen_events": ["warrior_barricade_charge"],
                    "log": "You crash into the trooper line alone, scattering them with a display of terrifying strength.",
                },
                "next": "forest_crossroad",
            },
        ],
    },
    "rogue_safehouse": {
        "id": "rogue_safehouse",
        "title": "Smuggler Safehouse",
        "text": (
            "Behind a false wall, a hub in Caldus's supply chain stores maps, coded letters, and "
            "a ledger naming both his agents and their marks. A captured runner whimpers in the corner. "
            "The intelligence here could shatter Caldus's logistics — or be sold for personal gain."
        ),
        "dialogue": [
            {"speaker": "Captured Runner", "line": "Every name in that ledger changes who survives this week. Caldus pays well for silence."},
            {"speaker": "Your Instinct", "line": "This network was yours once. Now decide what to do with its bones."},
        ],
        "choices": [
            {
                "label": "Steal the ledger and leak it to Oakrest's defenders",
                "effects": {
                    "trait_delta": {"trust": 1, "alignment": 1, "ember_tide": 1},
                    "faction_delta": {"oakrest": 2, "bandits": -2},
                    "set_flags": {"rogue_intel_leaked": True, "rogue_safehouse_method": "leaked"},
                    "seen_events": ["rogue_safehouse_breach"],
                    "log": "You lift the ledger and pass names to Oakrest sentries before dawn. Caldus loses eyes and ears.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Burn the safehouse and destroy Caldus's supply records",
                "effects": {
                    "trait_delta": {"reputation": 2, "alignment": -1, "ember_tide": 1},
                    "faction_delta": {"bandits": -1},
                    "set_flags": {"rogue_safehouse_burned": True, "rogue_safehouse_method": "burned"},
                    "seen_events": ["rogue_safehouse_burned"],
                    "log": "Flames consume the ledger and the safehouse both. Nobody reads those names again — including you.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Copy the critical pages and leave the safehouse intact as a trap",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "dexterity": 1,
                    "trait_delta": {"trust": 2, "reputation": 1, "ember_tide": 1},
                    "faction_delta": {"oakrest": 1},
                    "set_flags": {"rogue_intel_leaked": True, "rogue_safehouse_trapped": True, "rogue_safehouse_method": "trapped"},
                    "seen_events": ["rogue_safehouse_trapped"],
                    "log": "You copy the critical intelligence and rig the safehouse. Caldus's next courier walks into an ambush.",
                },
                "next": "forest_crossroad",
            },
        ],
    },
    "archer_ridgewatch": {
        "id": "archer_ridgewatch",
        "title": "Ridgewatch Nest",
        "text": (
            "From the ridge, you can see Caldus's supply wagons crawling toward the ruin. "
            "Lookout Fen is already here, wounded and running out of signal arrows. "
            "Together you could coordinate the entire valley defense — or strike Caldus's "
            "logistics directly with a few well-placed shots."
        ),
        "dialogue": [
            {"speaker": "Lookout Fen", "line": "I've been marking their wagons for days. One coordinated volley could cripple his supply line."},
            {"speaker": "Your Instinct", "line": "The ridge sees everything. The question is what you choose to do with the view."},
        ],
        "choices": [
            {
                "label": "Mark safe lanes and hostile routes for allied patrols",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1, "ember_tide": 1},
                    "faction_delta": {"ironwardens": 1, "oakrest": 1},
                    "set_flags": {"archer_routes_marked": True, "archer_ridge_method": "signals"},
                    "seen_events": ["archer_ridge_signals"],
                    "log": "Your signal work prevents an ambush and keeps both civilians and scouts moving safely.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Target Caldus's supply wagons with precision shots (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "dexterity": 1,
                    "trait_delta": {"reputation": 2, "ember_tide": 1},
                    "set_flags": {"archer_routes_marked": True, "archer_ridge_method": "strike", "ruin_supply_line_cut": True},
                    "seen_events": ["archer_supply_strike"],
                    "log": "Three arrows, three burning wagons. Caldus's supply line to the ruin frays overnight.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Coordinate a combined signal-and-strike operation with Fen",
                "requirements": {"min_dexterity": 4, "items": ["Signal Arrows"]},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"trust": 1, "reputation": 2, "ember_tide": 1},
                    "faction_delta": {"ironwardens": 2, "oakrest": 1},
                    "set_flags": {"archer_routes_marked": True, "archer_ridge_method": "combined", "ruin_supply_line_cut": True},
                    "seen_events": ["archer_ridge_signals", "archer_supply_strike"],
                    "log": "You and Fen orchestrate a devastating combination of intelligence and firepower across the valley.",
                },
                "next": "forest_crossroad",
            },
        ],
    },
    "dawnwarden_outpost": {
        "id": "dawnwarden_outpost",
        "title": "Ranger Outpost",
        "text": (
            "Captain Serin pins maps by dagger point, her jaw tight with fury. Caldus was her commander "
            "before he stole the Ember Core and vanished. She built the Ironwardens to bring him to "
            "justice. Archivist Pell knows the Emblem's history, and shield-bearer Nima wants a plan "
            "that doesn't end in speeches. Every minute of debate is measured against Caldus's channeling."
        ),
        "dialogue": [
            {"speaker": "Captain Serin", "line": "Caldus trained half my Rangers. He knows our signals, our routes, our weaknesses. But I know his pride."},
            {"speaker": "Archivist Pell", "line": "The Ember Core was a containment seal, not a weapon. Caldus is forcing it to burn what it was meant to protect."},
            {"speaker": "Shield-Bearer Nima", "line": "Give me a plan with spine, not poetry. Caldus won't wait for us to finish arguing."},
        ],
        "choices": [
            {
                "label": "Swear alliance with Serin to bring Caldus to justice",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1, "alignment": 1},
                    "set_flags": {"dawnwarden_allied": True, "mercy_reputation": True},
                    "add_items": ["Warden Token"],
                    "log": "Serin clasps your forearm and grants a Warden Token. She wants Caldus alive to answer for his betrayal.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Ask Pell for intelligence on Caldus's defenses",
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"knows_enemy_roster": True},
                    "seen_events": ["learned_enemy_roster"],
                    "log": "Pell briefs you on Caldus's inner circle: Vorga the alchemist, Sir Edrin the corrupted knight, and the ember loyalists.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Challenge Nima in a spar to earn the wardens' respect (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "trait_delta": {"reputation": 2},
                    "set_flags": {"earned_dawnwarden_respect": True},
                    "log": "After a brutal spar, Nima salutes you and marks a safer approach to Caldus's gate.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "ashfang_hunt": {
        "id": "ashfang_hunt",
        "title": "Ashfang Hunting Grounds",
        "text": (
            "Warchief Drogath leads the Ashfangs through bramble valleys, tracking a raider convoy. "
            "He despises Caldus — not for the betrayal, but for the weakness of hiding behind a relic "
            "instead of fighting with steel. Scout Yara and beast-handler Korr test every outsider "
            "who enters the hunting grounds."
        ),
        "dialogue": [
            {"speaker": "Warchief Drogath", "line": "Caldus hides behind old magic instead of facing his enemies. I'll teach him what real fire looks like."},
            {"speaker": "Scout Yara", "line": "Show me clean hands in a dirty war, outsider. Caldus's deserters said the same before we buried them."},
            {"speaker": "Beast-Handler Korr", "line": "My hounds remember fear. Feed them confidence or feed them meat."},
        ],
        "choices": [
            {
                "label": "Join the ambush and crush Caldus's convoy (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "hp": -1,
                    "gold": 4,
                    "trait_delta": {"trust": -1, "reputation": 2, "alignment": -1},
                    "set_flags": {"ashfang_allied": True, "cruel_reputation": True},
                    "seen_events": ["ashfang_convoy_slain"],
                    "log": "You and Drogath tear through Caldus's supply escort. Fast, brutal, and effective.",
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
                    "log": "Yara yields and gifts you an Ashfang Charm. Drogath nods — speed earns respect too.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Refuse bloodshed and guide convoy prisoners to safety",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1, "alignment": 2},
                    "set_flags": {"rescued_prisoners": True, "mercy_reputation": True},
                    "log": "You escort shaken prisoners away while the warband fights on. Mercy costs speed but earns loyalty.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "ravine_crossing": {
        "id": "ravine_crossing",
        "title": "Ravine Crossing",
        "text": (
            "The ravine was carved by Caldus's first experiment with the Ember Core — a practice "
            "channeling that split the earth and killed two of his own followers. Halfway across, "
            "rotten planks snap beneath your feet. The ember-scarred stone hums faintly below."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "Caldus cracked this ground open. The Emblem's power is real — and growing."},
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
                    "log": "You hit the ember-scarred ravine floor hard before scrambling back up.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "bandit_camp": {
        "id": "bandit_camp",
        "title": "Bandit Camp — Caldus's Deserters",
        "text": (
            "Three of Caldus's former soldiers surround a bound Oakrest scout. Their leader, Kest, "
            "was Caldus's chief scout before he saw what the Ember Core did to Sir Edrin and lost "
            "his nerve. He deserted, taking a handful of troops with him. Now he survives by raiding "
            "the people he once swore to protect."
        ),
        "dialogue": [
            {"speaker": "Kest", "line": "I ran because I saw what the Emblem does to people. Caldus doesn't care anymore — he's not even human near that thing."},
            {"speaker": "Bound Scout", "line": "Don't buy his pity. These raiders burned the eastern mill."},
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
                    "log": "You defeat the deserters brutally and free the scout. Kest's intel dies with him.",
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
                    "log": "You free the scout without a fight. Kest flees, but his fear of Caldus tells you everything.",
                },
                "next": "scout_report",
            },
            {
                "label": "Convince Kest to turn informant against Caldus",
                "requirements": {"flag_true": ["class_intro_done"]},
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1, "alignment": 1},
                    "seen_events": ["kest_turned_informant"],
                    "set_flags": {"rescued_scout": True, "spared_bandit": True, "kest_informant": True, "mercy_reputation": True, "morality": "merciful"},
                    "log": "Kest agrees to share what he knows about Caldus's defenses in exchange for a chance at redemption.",
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
                    "log": "You pocket the bribe and leave the scout to fate. Quick, cold, and efficient.",
                },
                "next": "war_council_hub",
            },
        ],
    },
}
