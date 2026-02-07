from typing import Any, Dict

STORY_NODES_ACT2: Dict[str, Dict[str, Any]] = {
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
    "flooded_causeway_approach": {
        "id": "flooded_causeway_approach",
        "title": "Flooded Causeway",
        "text": (
            "Half-sunken statues line a cracked causeway while cold water swirls around your knees. "
            "Villagers whisper that a tidebound knight has guarded this ruin road for years, drowning scouts and raiders alike."
        ),
        "dialogue": [
            {"speaker": "Broken Causeway Bell", "line": "Dong... dong... each toll comes from beneath the water."},
            {"speaker": "Your Instinct", "line": "This path could save Oakrest's flank, if you can survive what's guarding it."},
        ],
        "choices": [
            {
                "label": "Wade forward with shielded footing (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "hp": -1,
                    "set_flags": {"causeway_reached": True},
                    "log": "You muscle through the current and reach the upper terrace bruised but steady.",
                },
                "next": "causeway_depths",
            },
            {
                "label": "Anchor rope lines between statues",
                "requirements": {"items": ["Rope"]},
                "effects": {
                    "set_flags": {"causeway_reached": True},
                    "log": "Your rope rig keeps you above the undertow as you cross safely.",
                },
                "next": "causeway_depths",
            },
            {
                "label": "Backtrack and report to the war council",
                "effects": {"log": "You retreat from the floodline and return to Ember Ridge."},
                "next": "war_council_hub",
            },
        ],
    },
    "causeway_depths": {
        "id": "causeway_depths",
        "title": "Undervault Chamber",
        "text": (
            "Below the altar, a rusted floodgate seals a vault of old warding engines. You can reactivate the pumps "
            "to drain the road and expose a safer assault lane, but something massive is chained in the dark water."
        ),
        "dialogue": [
            {"speaker": "Ancient Inscription", "line": "When waters rise, the guardian wakes."},
            {"speaker": "Your Instinct", "line": "No more delays. Whatever is chained down there is your real trial."},
        ],
        "choices": [
            {
                "label": "Unlock the floodgate with lockpicks",
                "requirements": {"items": ["Lockpicks"]},
                "effects": {
                    "set_flags": {"floodgate_open": True},
                    "log": "Tumblers grind loose and the floodgate heaves upward.",
                },
                "next": "causeway_quiet",
            },
            {
                "label": "Force the floodgate wheel (Strength 5)",
                "requirements": {"min_strength": 5},
                "effects": {
                    "hp": -1,
                    "set_flags": {"floodgate_open": True},
                    "log": "You wrench the corroded wheel until the chain snaps and the vault roars awake.",
                },
                "next": "causeway_quiet",
            },
            {
                "label": "Fall back before the chamber floods",
                "effects": {"log": "You abandon the vault and withdraw to regroup."},
                "next": "war_council_hub",
            },
        ],
    },
    "causeway_quiet": {
        "id": "causeway_quiet",
        "title": "Quiet Beat — Drowned Silence",
        "text": (
            "Water drains in slow spirals, revealing the causeway's carved reliefs. The chamber stills, the echo of the "
            "floodgate hanging like a held breath before the guardian rises."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "This pause is the last calm the causeway will give you."},
            {"speaker": "Distant Water", "line": "The chains begin to sing beneath the surface."},
        ],
        "choices": [
            {
                "label": "Mark the safer footing for your allies",
                "effects": {
                    "trait_delta": {"trust": 1},
                    "seen_events": ["causeway_quiet_marked"],
                    "log": "You note each dry stone, giving your allies a path through the flood.",
                },
                "next": "tidebound_knight",
            },
            {
                "label": "Steady your grip and confront the guardian",
                "effects": {
                    "trait_delta": {"reputation": 1},
                    "seen_events": ["causeway_quiet_steadied"],
                    "log": "You breathe once, slow and deep, before stepping into the rising water.",
                },
                "next": "tidebound_knight",
            },
            {
                "label": "Withdraw before the knight rises",
                "effects": {"log": "You back away from the vault, leaving the guardian unchallenged."},
                "next": "war_council_hub",
            },
        ],
    },
    "tidebound_knight": {
        "id": "tidebound_knight",
        "title": "Mini-Boss: Tidebound Knight",
        "text": (
            "A barnacled knight rises from the reservoir in chained plate, dragging a bell-hammer the size of a cart axle. "
            "If you defeat it, the drained causeway will give Oakrest a protected route straight to the ruin's outer wall."
        ),
        "dialogue": [
            {"speaker": "Tidebound Knight", "line": "None pass the drowned oath."},
            {"speaker": "Your Instinct", "line": "Break this guardian and the whole battlefield changes."},
        ],
        "choices": [
            {
                "label": "Shatter the knight's guard with brute force (Strength 5)",
                "requirements": {"min_strength": 5},
                "effects": {
                    "hp": -2,
                    "trait_delta": {"reputation": 2},
                    "set_flags": {"tidebound_knight_defeated": True, "opened_cleanly": True},
                    "log": "You crack the barnacle armor apart and the floodwater drains into old channels.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Use the opened floodgate chain to pin and finish it",
                "requirements": {"flag_true": ["floodgate_open"]},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"tidebound_knight_defeated": True, "ruin_supply_line_cut": True},
                    "log": "You trap the knight in its own chain rig and sever the raiders' water approach.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Retreat with injuries and abandon the flooded route",
                "effects": {"hp": -2, "log": "You escape the vault battered, leaving the guardian undefeated."},
                "next": "war_council_hub",
            },
        ],
    },
    "charred_mill_approach": {
        "id": "charred_mill_approach",
        "title": "Charred Mill Trail",
        "text": (
            "The old grain mill still turns despite having no river, its wheel driven by ember gusts from below. "
            "Scouts report a pyre-alchemist has been forging firebombs here for the Warden's troops."
        ),
        "dialogue": [
            {"speaker": "Scorched Villager", "line": "That mill made the bombs that burned my field."},
            {"speaker": "Your Instinct", "line": "If this forge falls, fewer fires reach Oakrest."},
        ],
        "choices": [
            {
                "label": "Climb the rafters and scout from above (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "set_flags": {"mill_scouted": True},
                    "log": "From the rafters you chart patrol patterns and a weak point in the blast kiln.",
                },
                "next": "smokeforge_floor",
            },
            {
                "label": "Kick in the side gate and storm the yard",
                "effects": {
                    "hp": -1,
                    "set_flags": {"mill_scouted": False},
                    "log": "You smash through the side gate, drawing every sentry's attention.",
                },
                "next": "smokeforge_floor",
            },
            {
                "label": "Withdraw and return to Ember Ridge",
                "effects": {"log": "You leave the mill to regroup with allied scouts."},
                "next": "war_council_hub",
            },
        ],
    },
    "smokeforge_floor": {
        "id": "smokeforge_floor",
        "title": "Smokeforge Interior",
        "text": (
            "Bomb racks line the floor beside a roaring kiln. You can sabotage the powder stores now, "
            "or push straight into the foundry where the pyre-alchemist is chanting over volatile resin."
        ),
        "dialogue": [
            {"speaker": "Ashfang Prisoner", "line": "One spark and this whole place jumps to the sky."},
            {"speaker": "Your Instinct", "line": "Make this count. The war won't forgive a sloppy fire."},
        ],
        "choices": [
            {
                "label": "Sabotage the bomb racks before the duel",
                "effects": {
                    "set_flags": {"bomb_racks_sabotaged": True},
                    "trait_delta": {"reputation": 1},
                    "log": "You soak the fuses and snap detonators, reducing the foundry's firepower.",
                },
                "next": "pyre_alchemist",
            },
            {
                "label": "Charge the foundry immediately",
                "effects": {
                    "hp": -1,
                    "set_flags": {"bomb_racks_sabotaged": False},
                    "log": "You rush the furnace gantry before finishing any sabotage.",
                },
                "next": "pyre_alchemist",
            },
        ],
    },
    "pyre_alchemist": {
        "id": "pyre_alchemist",
        "title": "Mini-Boss: Pyre-Alchemist Vorga",
        "text": (
            "Vorga hurls flask-bombs while furnace vents spew white fire. Defeating her will cripple the raiders' "
            "incendiary stockpile and calm the panic spreading through Oakrest's outskirts."
        ),
        "dialogue": [
            {"speaker": "Vorga", "line": "I bottle dawn itself. You cannot outrun sunrise."},
            {"speaker": "Your Instinct", "line": "End this forge and the village breathes easier tonight."},
        ],
        "choices": [
            {
                "label": "Win a close-quarters duel (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "hp": -2,
                    "set_flags": {"pyre_alchemist_defeated": True, "ruin_supply_line_cut": True},
                    "trait_delta": {"reputation": 2},
                    "log": "You force Vorga off the gantry and scatter the last armed bombs into cooling ash.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Trigger your sabotage and finish Vorga in the smoke",
                "requirements": {"flag_true": ["bomb_racks_sabotaged"]},
                "effects": {
                    "hp": -1,
                    "set_flags": {"pyre_alchemist_defeated": True, "opened_cleanly": True},
                    "trait_delta": {"trust": 1, "alignment": 1},
                    "log": "Your sabotage blanks her bomb barrage, and one precise strike ends the fight.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Escape the foundry before it erupts",
                "effects": {
                    "hp": -2,
                    "log": "You surge through burning beams and escape, but Vorga survives to arm more raiders.",
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
            {"speaker": "Signal Runner Tams", "line": "Reports keep stacking, commander. Say the word and I move people now."},
            {"speaker": "Your Instinct", "line": "This ridge is a ledger. Every spared enemy and ignored threat gets collected tonight."},
            {"speaker": "Elder Mara", "line": "How you fought matters as much as whether you win. Oakrest will remember both."},
        ],
        "auto_choices": [
            {
                "label": "Council cites the captives you freed",
                "requirements": {"flag_true": ["rescued_prisoners"]},
                "effects": {"log": "Tams points out the freed prisoners already lighting diversion fires by your order."},
            },
            {
                "label": "Council murmurs about your brutal reputation",
                "requirements": {"max_reputation": -2},
                "effects": {
                    "set_flags": {"council_fearful": True},
                    "log": "Whispers ripple through the ridge; some commanders avert their eyes, fearing what follows your victories.",
                },
            },
            {
                "label": "Council references the causeway victory",
                "requirements": {"flag_true": ["tidebound_knight_defeated"]},
                "effects": {"log": "Scouts remind the council that your causeway win opened a flank the raiders still fear."},
            },
            {
                "label": "Council recalls the foundry sabotage",
                "requirements": {"flag_true": ["pyre_alchemist_defeated"]},
                "effects": {"log": "Elder Mara notes the foundry sabotage that blunted Vorga's firebomb supply."},
            },
        ],
        "choices": [
            {
                "label": "Return to the forest crossroads and resolve more unfinished threats",
                "group": "Recon & Reassessment",
                "requirements": {"flag_false": ["returned_for_more_branches"]},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"trust": 1},
                    "set_flags": {"returned_for_more_branches": True},
                    "log": "You delay the siege and head back out, but every hour costs blood along Oakrest's outer farms.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Delay again despite mounting losses",
                "group": "Recon & Reassessment",
                "requirements": {"flag_true": ["returned_for_more_branches"]},
                "effects": {
                    "hp": -2,
                    "trait_delta": {"trust": -1, "reputation": -1},
                    "set_flags": {"repeated_delay": True},
                    "log": "Tams reports burned wagons and missing scouts as you postpone the assault a second time.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Review assault plans with the council (unlocks assault options)",
                "group": "Council Briefing",
                "requirements": {"flag_false": ["war_council_briefed"]},
                "effects": {
                    "set_flags": {"war_council_briefed": True},
                    "log": "You walk the council through the battlefield intel, narrowing the assault options.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Hear Serin's judgment of your command",
                "group": "Council Briefing",
                "requirements": {"flag_true": ["mercy_reputation"]},
                "auto_apply": True,
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"serin_endorsement": True},
                    "log": "Serin says your mercy bought real allies; Rangers volunteer for the hardest breach lanes.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Hear Drogath's judgment of your command",
                "group": "Council Briefing",
                "requirements": {"flag_true": ["cruel_reputation"]},
                "auto_apply": True,
                "effects": {
                    "trait_delta": {"reputation": 1, "trust": -1},
                    "set_flags": {"drogath_endorsement": True},
                    "log": "Drogath respects your fear tactics, but even allies step back when you enter the firelight.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Hold a quiet vigil before the assault",
                "group": "Council Briefing",
                "requirements": {"flag_false": ["ember_ridge_vigil_taken"]},
                "effects": {
                    "hp": 1,
                    "trait_delta": {"trust": 1},
                    "set_flags": {"ember_ridge_vigil_taken": True},
                    "log": "You take a measured pause at the ridge, letting the silence reset the war council's nerves.",
                },
                "next": "ember_ridge_vigil",
            },
            {
                "label": "Intimidate the council into a reckless push",
                "group": "Council Briefing",
                "requirements": {"flag_true": ["war_council_briefed"], "max_reputation": -2},
                "effects": {
                    "trait_delta": {"trust": -2, "reputation": -1, "alignment": -1},
                    "set_flags": {"hub_plan": "fear_push", "council_cowed": True},
                    "log": "Fear replaces strategy as you force the council into a headlong assault.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Use the Echo Locket and Bronze Seal to unseal a reliquary",
                "group": "Relics & Secrets",
                "requirements": {
                    "items": ["Bronze Seal"],
                    "meta_items": ["Echo Locket"],
                    "meta_nodes_present": ["ember_reliquary"],
                },
                "effects": {
                    "log": "The locket resonates with the seal's markings, revealing a sealed stair beneath the ridge.",
                },
                "next": "ember_reliquary",
            },
            {
                "label": "Lead an allied breach (Dawnwarden or Ashfang veterans)",
                "group": "Assault Plans",
                "requirements": {
                    "flag_true": ["war_council_briefed"],
                    "any_of": [{"flag_true": ["dawnwarden_allied"]}, {"flag_true": ["ashfang_allied"]}],
                },
                "conditional_effects": [
                    {
                        "requirements": {"flag_true": ["dawnwarden_allied"]},
                        "effects": {
                            "trait_delta": {"trust": 1, "reputation": 1},
                            "set_flags": {"opened_cleanly": True, "hub_plan": "dawnwarden_breach"},
                            "log": "Serin's rangers secure the perimeter and hand you a clear line to the gate.",
                        },
                    },
                    {
                        "requirements": {"flag_true": ["ashfang_allied"]},
                        "effects": {
                            "hp": -1,
                            "trait_delta": {"reputation": 2, "alignment": -1},
                            "set_flags": {"cruel_reputation": True, "hub_plan": "ashfang_push"},
                            "log": "Ashfang drums break enemy nerve, but the assault leaves casualties in its wake.",
                        },
                    },
                ],
                "next": "ruin_gate",
            },
            {
                "label": "Use scout intelligence to approach through the hidden tunnel",
                "group": "Assault Plans",
                "requirements": {
                    "flag_true": ["war_council_briefed", "knows_hidden_route"],
                    "min_dexterity": 4,
                },
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"hub_plan": "hidden_route"},
                    "log": "You trust the scout's map and steer the strike team underground for a second strike.",
                },
                "next": "hidden_route_assault",
            },
            {
                "label": "Rally survivors you rescued to create a diversion",
                "group": "Assault Plans",
                "requirements": {"flag_true": ["war_council_briefed", "rescued_prisoners"]},
                "effects": {
                    "trait_delta": {"trust": 1, "alignment": 1},
                    "set_flags": {"mercy_reputation": True, "hub_plan": "survivor_diversion"},
                    "log": "Freed prisoners light decoy fires, drawing raiders off your intended route.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Exploit your battlefield advantage (causeway or supply denial)",
                "group": "Assault Plans",
                "requirements": {
                    "flag_true": ["war_council_briefed"],
                    "any_of": [
                        {"flag_true": ["tidebound_knight_defeated"]},
                        {"flag_true": ["ruin_supply_line_cut"], "min_strength": 4},
                    ]
                },
                "conditional_effects": [
                    {
                        "requirements": {"flag_true": ["tidebound_knight_defeated"]},
                        "effects": {
                            "set_flags": {"hub_plan": "causeway_route", "opened_cleanly": True},
                            "trait_delta": {"trust": 1, "reputation": 1},
                            "log": "Scouts surge down the drained causeway, giving your assault a disciplined flank.",
                        },
                    },
                    {
                        "requirements": {"flag_true": ["ruin_supply_line_cut"], "min_strength": 4},
                        "effects": {
                            "set_flags": {"hub_plan": "supply_denial"},
                            "trait_delta": {"reputation": 1},
                            "log": "With bomb stocks and river routes cut, enemy resistance at the gate falters.",
                        },
                    },
                ],
                "next": "ruin_gate",
            },
            {
                "label": "Advance alone before reinforcements arrive (Strength 4, Dexterity 4)",
                "group": "Assault Plans",
                "requirements": {"flag_true": ["war_council_briefed"], "min_strength": 4, "min_dexterity": 4},
                "effects": {
                    "trait_delta": {"reputation": -1, "trust": -1},
                    "set_flags": {"hub_plan": "solo_push"},
                    "log": "You reject every banner and slip toward the ruin before anyone can stop you.",
                },
                "next": "lonely_approach",
            },
        ],
    },
    "ember_reliquary": {
        "id": "ember_reliquary",
        "title": "Ember Reliquary",
        "text": (
            "Below Ember Ridge, a reliquary chamber hums with old warding lines. The Bronze Seal presses into a socket, "
            "and the Echo Locket vibrates in your palm as if the ruin itself remembers you."
        ),
        "dialogue": [
            {"speaker": "Ancient Script", "line": "Legacy is a door that only opens twice."},
            {"speaker": "Your Instinct", "line": "Take what the ridge hid, and carry its weight forward."},
        ],
        "requirements": {"meta_nodes_present": ["ember_reliquary"]},
        "choices": [
            {
                "label": "Claim the Ember Sigil and bind it to your fate",
                "requirements": {"meta_missing_items": ["Ember Sigil"]},
                "effects": {
                    "add_items": ["Ember Sigil"],
                    "unlock_meta_items": ["Ember Sigil"],
                    "remove_meta_nodes": ["ember_reliquary"],
                    "set_flags": {"ember_sigil_claimed": True},
                    "log": "Heat crawls across your skin as the sigil brands itself into your story.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Back away from the reliquary while it sleeps",
                "effects": {"log": "You let the warding lines dim and return to the war council."},
                "next": "war_council_hub",
            },
        ],
    },
}
