from typing import Any, Dict

STORY_NODES_ACT2: Dict[str, Dict[str, Any]] = {
    "scout_report": {
        "id": "scout_report",
        "title": "Scout's Warning",
        "text": (
            "The rescued scout gasps out details about Caldus's operation. The ruin is not just occupied — "
            "Caldus is channeling the Ember Core through a channeling array. His old mentor Sir Edrin guards "
            "the causeway approach, corrupted by the Core's overflow. Vorga, his alchemist, forges "
            "incendiary weapons at a mill nearby. The scout offers a bronze seal taken from a dead loyalist."
        ),
        "dialogue": [
            {"speaker": "Rescued Scout", "line": "Caldus talks to the Core like it's alive. He says the old kingdom's power resonates through it."},
            {"speaker": "Rescued Scout", "line": "Take this seal. It opens doors his loyalists use. Older than fear, and twice as stubborn."},
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
                    "log": "You take the bronze seal; old markings glow faintly, resonating with the Core's distant pulse.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Ask the scout for a hidden approach to Caldus's ruin",
                "requirements": {"flag_true": ["rescued_scout"]},
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "seen_events": ["learned_hidden_route"],
                    "set_flags": {"knows_hidden_route": True},
                    "log": "The scout marks an old service tunnel that predates Caldus's occupation.",
                },
                "next": "hidden_tunnel",
            },
            {
                "label": "Refuse and hurry to the ruin",
                "effects": {
                    "trait_delta": {"reputation": -1},
                    "log": "You refuse the token and press onward. Speed over preparation.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "hidden_tunnel": {
        "id": "hidden_tunnel",
        "title": "Forgotten Service Tunnel",
        "text": (
            "The scout's map leads you into a collapsed maintenance tunnel beneath Caldus's ruin. "
            "Fresh boot prints and ember residue tell you Caldus's loyalists use this route too. "
            "You can sabotage the signal braziers to blind his sentries, but the collapse will trap "
            "anyone still inside."
        ),
        "dialogue": [
            {"speaker": "Echoing Voices", "line": "Someone's still down here... or the tunnel remembers them."},
            {"speaker": "Your Instinct", "line": "Caldus uses this tunnel. Collapsing it costs him a route — and costs anyone trapped below their life."},
        ],
        "requirements": {"flag_true": ["knows_hidden_route"]},
        "choices": [
            {
                "label": "Collapse the tunnel to deny Caldus reinforcements (irreversible)",
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
        "title": "Flooded Causeway — Sir Edrin's Domain",
        "text": (
            "Half-sunken statues line a cracked causeway while cold water swirls around your knees. "
            "Sir Edrin, Caldus's former mentor and the captain who trained him, was the first person "
            "Caldus tested the Ember Core on. The experiment went wrong — Edrin survived but was "
            "transformed, bound to the causeway by the Core's containment power, neither alive nor dead."
        ),
        "dialogue": [
            {"speaker": "Broken Causeway Bell", "line": "Dong... dong... each toll comes from beneath the water, keeping Edrin tethered."},
            {"speaker": "Your Instinct", "line": "Caldus did this to his own teacher. Understanding Edrin means understanding what the Core does to people."},
        ],
        "choices": [
            {
                "label": "Wade forward with shielded footing (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"ember_tide": 1},
                    "set_flags": {"causeway_reached": True},
                    "log": "You muscle through the current and reach the upper terrace, but the detour costs the valley time.",
                },
                "next": "causeway_depths",
            },
            {
                "label": "Anchor rope lines between statues",
                "requirements": {"items": ["Rope"]},
                "effects": {
                    "trait_delta": {"ember_tide": 1},
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
            "Below the altar, a rusted floodgate seals a vault of old containment engines — the same "
            "kind Caldus repurposed for his channeling array. You can reactivate the pumps to drain the "
            "road and expose a safer assault lane, but Edrin's chain-bound form stirs in the dark water."
        ),
        "dialogue": [
            {"speaker": "Ancient Inscription", "line": "When waters rise, the guardian wakes. When the Core burns, the guardian weeps."},
            {"speaker": "Your Instinct", "line": "Edrin was Caldus's first victim. Whatever is chained down there was once a good man."},
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
            "Water drains in slow spirals, revealing the causeway's carved reliefs — scenes of the "
            "old kingdom's fall that Caldus is trying to reverse. The chamber stills, the echo of the "
            "floodgate hanging like a held breath before Edrin's corrupted form rises."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "Edrin didn't choose this. Caldus made him into a weapon. Remember that when you face him."},
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
                "label": "Steady your grip and confront Edrin",
                "effects": {
                    "trait_delta": {"reputation": 1},
                    "seen_events": ["causeway_quiet_steadied"],
                    "log": "You breathe once, slow and deep, before stepping into the rising water.",
                },
                "next": "tidebound_knight",
            },
            {
                "label": "Withdraw before Edrin rises",
                "effects": {"log": "You back away from the vault, leaving Caldus's first victim unchallenged."},
                "next": "war_council_hub",
            },
        ],
    },
    "tidebound_knight": {
        "id": "tidebound_knight",
        "title": "Mini-Boss: Sir Edrin, the Tidebound Knight",
        "text": (
            "A barnacled knight rises from the reservoir in chained plate, dragging a bell-hammer. "
            "Once Caldus's mentor and the finest captain in the Ironwardens, Sir Edrin was the Core's "
            "first test subject. The corruption fused him to the causeway's containment stones. He fights "
            "not from malice but from the compulsion Caldus burned into him. Defeating Edrin opens a "
            "protected assault route to the ruin."
        ),
        "dialogue": [
            {"speaker": "Sir Edrin", "line": "Caldus... release me... I cannot stop... the Core commands..."},
            {"speaker": "Your Instinct", "line": "This is what the Ember Core does. This is what Caldus will do to Oakrest."},
        ],
        "choices": [
            {
                "label": "Shatter Edrin's guard with brute force (Strength 5)",
                "requirements": {"min_strength": 5},
                "effects": {
                    "hp": -2,
                    "trait_delta": {"reputation": 2},
                    "set_flags": {"tidebound_knight_defeated": True, "opened_cleanly": True},
                    "log": "You crack the barnacle armor apart. Edrin collapses and the floodwater drains into old channels.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Use the opened floodgate chain to pin and finish Edrin",
                "requirements": {"flag_true": ["floodgate_open"]},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"tidebound_knight_defeated": True, "ruin_supply_line_cut": True},
                    "log": "You trap the knight in its own chain rig and sever Caldus's water approach.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Retreat with injuries and abandon the flooded route",
                "effects": {"hp": -2, "log": "You escape the vault battered, leaving Edrin — and Caldus's causeway — intact."},
                "next": "war_council_hub",
            },
        ],
    },
    "charred_mill_approach": {
        "id": "charred_mill_approach",
        "title": "Charred Mill Trail — Vorga's Foundry",
        "text": (
            "The old grain mill still turns despite having no river, its wheel driven by ember gusts "
            "channeled from the Ember Core. Vorga, Caldus's apprentice alchemist, has converted it "
            "into a bomb forge. She shares Caldus's vision of a cleansing fire but lacks his restraint — "
            "if he has any left. The firebombs she makes here will burn Oakrest to cinders."
        ),
        "dialogue": [
            {"speaker": "Scorched Villager", "line": "That mill made the bombs that burned my field. Vorga laughed while we ran."},
            {"speaker": "Your Instinct", "line": "Vorga is Caldus's weapons maker. Shut her down and half his firepower dies."},
        ],
        "choices": [
            {
                "label": "Climb the rafters and scout from above (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "trait_delta": {"ember_tide": 1},
                    "set_flags": {"mill_scouted": True},
                    "log": "From the rafters you chart patrol patterns and a weak point in the blast kiln.",
                },
                "next": "smokeforge_floor",
            },
            {
                "label": "Kick in the side gate and storm the yard",
                "effects": {
                    "hp": -1,
                    "trait_delta": {"ember_tide": 1},
                    "set_flags": {"mill_scouted": False},
                    "log": "You smash through the side gate, drawing every sentry's attention.",
                },
                "next": "smokeforge_floor",
            },
            {
                "label": "Withdraw and return to the war council",
                "effects": {"log": "You leave Vorga's forge intact and regroup."},
                "next": "war_council_hub",
            },
        ],
    },
    "smokeforge_floor": {
        "id": "smokeforge_floor",
        "title": "Smokeforge Interior",
        "text": (
            "Bomb racks line the floor beside a roaring kiln fed by ember energy from the ruin. "
            "Vorga's latest batch can level a village block. You can sabotage the powder stores "
            "before confronting her, or push straight into the foundry where she chants over volatile resin."
        ),
        "dialogue": [
            {"speaker": "Ashfang Prisoner", "line": "Vorga said Caldus promised her a new order. She believes every word."},
            {"speaker": "Your Instinct", "line": "These bombs are meant for Oakrest. Every rack you destroy is a street that survives."},
        ],
        "choices": [
            {
                "label": "Sabotage the bomb racks before the duel",
                "effects": {
                    "set_flags": {"bomb_racks_sabotaged": True},
                    "trait_delta": {"reputation": 1},
                    "log": "You soak the fuses and snap detonators, crippling Caldus's firebomb supply.",
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
            "Vorga hurls flask-bombs while furnace vents spew white fire. She is Caldus's true believer — "
            "convinced that burning the valley will fertilize a new golden age. Unlike Caldus, who has "
            "the cold logic of a loyalist, Vorga fights with the passion of a fanatic. Defeating her "
            "cripples Caldus's incendiary stockpile."
        ),
        "dialogue": [
            {"speaker": "Vorga", "line": "Caldus showed me the old kingdom's power in the Core's fire. It was beautiful. You'll see it too — when Oakrest burns."},
            {"speaker": "Your Instinct", "line": "She's not evil. She's convinced. That makes her more dangerous."},
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
                    "log": "Your sabotage blanks her bomb barrage. One precise strike ends the fight.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Escape the foundry before it erupts",
                "effects": {
                    "hp": -2,
                    "log": "You surge through burning beams and escape, but Vorga survives to arm more of Caldus's raiders.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "war_council_hub": {
        "id": "war_council_hub",
        "title": "War Council at Ember Ridge",
        "text": (
            "Trails from every skirmish converge at Ember Ridge, where scouts trade reports before the "
            "final push against Caldus. The orange glow above the ruin is visible now, pulsing like a "
            "heartbeat. Allies and rivals judge you by what you've done — spared lives, won respect, "
            "or ruled through fear. Your next move decides who stands with you at Caldus's gate."
        ),
        "dialogue": [
            {"speaker": "Signal Runner Tams", "line": "The Ember Tide keeps rising. Caldus is almost ready. Say the word and I move people now."},
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
                "label": "Council references the causeway victory over Sir Edrin",
                "requirements": {"flag_true": ["tidebound_knight_defeated"]},
                "effects": {"log": "Scouts remind the council that you defeated Caldus's own corrupted mentor at the causeway."},
            },
            {
                "label": "Council recalls the foundry sabotage against Vorga",
                "requirements": {"flag_true": ["pyre_alchemist_defeated"]},
                "effects": {"log": "Elder Mara notes that Vorga's defeat blunted Caldus's firebomb supply."},
            },
            {
                "label": "Council notes Kest's intelligence on Caldus's defenses",
                "requirements": {"flag_true": ["kest_informant"]},
                "effects": {
                    "set_flags": {"kest_intel_available": True},
                    "log": "Kest's detailed account of Caldus's inner defenses circulates among the commanders.",
                },
            },
        ],
        "choices": [
            {
                "label": "Return to the forest crossroads and resolve more threats",
                "group": "Recon & Reassessment",
                "requirements": {"flag_false": ["returned_for_more_branches"]},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"trust": 1, "ember_tide": 2},
                    "set_flags": {"returned_for_more_branches": True},
                    "log": "You delay the assault. Every hour costs blood along Oakrest's outer farms, but preparation has its own value.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Delay again despite mounting losses",
                "group": "Recon & Reassessment",
                "requirements": {"flag_true": ["returned_for_more_branches"]},
                "effects": {
                    "hp": -2,
                    "trait_delta": {"trust": -1, "reputation": -1, "ember_tide": 3},
                    "set_flags": {"repeated_delay": True},
                    "log": "Tams reports burned wagons and missing scouts as you postpone the assault a second time. Caldus's channeling accelerates.",
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
                    "log": "Serin says your mercy bought real allies; Rangers volunteer for the hardest breach lanes against Caldus.",
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
                    "log": "Fear replaces strategy as you force the council into a headlong assault against Caldus.",
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
                "label": "Lead an allied breach (Ironwarden or Ashfang veterans)",
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
                            "log": "Serin's rangers secure the perimeter. They want Caldus alive — the Ironwardens demand justice.",
                        },
                    },
                    {
                        "requirements": {"flag_true": ["ashfang_allied"]},
                        "effects": {
                            "hp": -1,
                            "trait_delta": {"reputation": 2, "alignment": -1},
                            "set_flags": {"cruel_reputation": True, "hub_plan": "ashfang_push"},
                            "log": "Ashfang drums break enemy nerve. Drogath wants Caldus dead, not captured.",
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
                    "log": "You trust the scout's map and steer the strike team underground toward Caldus.",
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
                    "log": "Freed prisoners light decoy fires, drawing Caldus's sentries off your intended route.",
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
                    ],
                },
                "conditional_effects": [
                    {
                        "requirements": {"flag_true": ["tidebound_knight_defeated"]},
                        "effects": {
                            "set_flags": {"hub_plan": "causeway_route", "opened_cleanly": True},
                            "trait_delta": {"trust": 1, "reputation": 1},
                            "log": "With Edrin defeated, scouts surge down the drained causeway to flank Caldus.",
                        },
                    },
                    {
                        "requirements": {"flag_true": ["ruin_supply_line_cut"], "min_strength": 4},
                        "effects": {
                            "set_flags": {"hub_plan": "supply_denial"},
                            "trait_delta": {"reputation": 1},
                            "log": "With Caldus's supply lines cut, enemy resistance at the gate falters.",
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
                    "log": "You reject every banner and slip toward Caldus's ruin before anyone can stop you.",
                },
                "next": "lonely_approach",
            },
        ],
    },
    "ember_reliquary": {
        "id": "ember_reliquary",
        "title": "Ember Reliquary",
        "text": (
            "Below Ember Ridge, a reliquary chamber hums with old containment lines — the same energy "
            "Caldus corrupted for his channeling array. The Bronze Seal presses into a socket, and the Echo "
            "Locket vibrates in your palm as if the ruin itself remembers you."
        ),
        "dialogue": [
            {"speaker": "Ancient Script", "line": "Legacy is a door that only opens twice."},
            {"speaker": "Your Instinct", "line": "Take what the ridge hid, and carry its weight forward against Caldus."},
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
                "effects": {"log": "You let the containment lines dim and return to the war council."},
                "next": "war_council_hub",
            },
        ],
    },
}
