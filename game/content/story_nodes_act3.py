from typing import Any, Dict

STORY_NODES_ACT3: Dict[str, Dict[str, Any]] = {
    "ember_ridge_vigil": {
        "id": "ember_ridge_vigil",
        "title": "Quiet Beat — Ember Ridge Vigil",
        "text": (
            "A hush settles over the ridge as the last light fades. The orange pulse above Caldus's ruin "
            "beats slower now, like a heart gathering strength. Fires are banked low and even the drummers "
            "pause, giving you a moment to listen to the wind, the breathing of allies, and the distant hum "
            "of the Dawn Emblem consuming everything Caldus feeds it."
        ),
        "dialogue": [
            {"speaker": "Signal Runner Tams", "line": "Quiet now means fewer mistakes once we move. Caldus won't give us a second chance."},
            {"speaker": "Your Instinct", "line": "Let the silence remind you who you're bringing home — and who put them in danger."},
        ],
        "choices": [
            {
                "label": "Offer a few steadying words to the strike team",
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"ember_ridge_vigil_spoken": True},
                    "log": "Your calm words steel the line. Soldiers repeat them to each other as they sharpen blades.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Walk the ridge alone and focus on the plan ahead",
                "effects": {
                    "trait_delta": {"reputation": 1},
                    "set_flags": {"ember_ridge_vigil_walked": True},
                    "log": "You trace the ridge in silence, committing every route and risk to memory before facing Caldus.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "hidden_route_assault": {
        "id": "hidden_route_assault",
        "title": "Hidden Route Counterstrike",
        "text": (
            "The service tunnel forks beneath Caldus's ruin into a powder store and a prisoner corridor. "
            "Caldus's zealots use the left fork to arm the Emblem pylons; the right holds villagers taken "
            "as labor for the ritual. You can gut his reserves or free the captives, but not both quietly."
        ),
        "dialogue": [
            {"speaker": "Scout's Markings", "line": "Blue chalk means Caldus's stores. White chalk means survivors."},
            {"speaker": "Your Instinct", "line": "Either path weakens Caldus, but not in the same way."},
        ],
        "requirements": {"flag_true": ["knows_hidden_route"]},
        "choices": [
            {
                "label": "Ruin Caldus's powder cache before the alarm spreads",
                "effects": {
                    "hp": -1,
                    "trait_delta": {"reputation": 1, "alignment": -1},
                    "set_flags": {"ruin_supply_line_cut": True, "opened_cleanly": True},
                    "seen_events": ["hidden_cache_destroyed"],
                    "log": "You flood Caldus's cache with lamp oil and sparks, collapsing his munitions tunnel.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Escort captives through the service culvert",
                "effects": {
                    "trait_delta": {"trust": 2, "alignment": 1},
                    "set_flags": {"rescued_prisoners": True, "mercy_reputation": True},
                    "seen_events": ["captives_escorted"],
                    "log": "You lead captives out first; grateful families spread word of your mercy against Caldus.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Split your attention and attempt both objectives",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "hp": -2,
                    "trait_delta": {"reputation": 2},
                    "set_flags": {
                        "ruin_supply_line_cut": True,
                        "rescued_prisoners": True,
                        "opened_cleanly": True,
                    },
                    "seen_events": ["captives_escorted", "hidden_cache_destroyed"],
                    "log": "You juggle sabotage and evacuation at once, barely outrunning the blast wave beneath Caldus's ruin.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "lonely_approach": {
        "id": "lonely_approach",
        "title": "No-Banner Approach",
        "text": (
            "Without allied cover, Caldus's outer trenches are thicker with patrols than expected. "
            "Ember-branded sentries sweep the hillside and you must pick one hard gamble before "
            "the encirclement closes around you."
        ),
        "dialogue": [
            {"speaker": "Caldus's Sentry", "line": "Single runner on the north ridge! Cut them off before Caldus's ward triggers!"},
            {"speaker": "Your Instinct", "line": "Going solo was never meant to be safe. Commit or be cornered."},
        ],
        "choices": [
            {
                "label": "Break through the trench line by force (Strength 5)",
                "requirements": {"min_strength": 5},
                "effects": {
                    "hp": -2,
                    "strength": 1,
                    "trait_delta": {"reputation": 1},
                    "set_flags": {"opened_cleanly": False},
                    "log": "You smash through shields and barbed stakes, reaching Caldus's gate bloodied but unbroken.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Vanish through drainage culverts (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "hp": -1,
                    "dexterity": 1,
                    "trait_delta": {"trust": -1, "reputation": 1},
                    "set_flags": {"opened_cleanly": True},
                    "log": "You crawl through black water and emerge inside Caldus's perimeter unseen.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Fake surrender, then bolt when they open the cage",
                "effects": {
                    "trait_delta": {"alignment": -1},
                    "log": "The ploy nearly works, but a branded zealot recognizes your face from Caldus's bounty.",
                },
                "next": "failure_captured",
            },
        ],
    },
    "ruin_gate": {
        "id": "ruin_gate",
        "title": "Caldus's Ruin — The Outer Gate",
        "text": (
            "Cracked stone doors loom beneath ivy and Caldus's burnt sigils. The Dawn Emblem's pulse "
            "is audible here — a low throb that vibrates through the masonry. A collapsed side breach "
            "leads downward, while the main gate bears Caldus's warding lock, forged from old kingdom seals."
        ),
        "dialogue": [
            {"speaker": "Caldus's Voice (amplified)", "line": "I can feel you at my threshold. You are too late to stop the dawn I am building."},
            {"speaker": "Your Instinct", "line": "He knows you're here. Every path in is a promise you'll have to keep."},
        ],
        "choices": [
            {
                "label": "Force open the main gate (Strength 4)",
                "requirements": {"min_strength": 4},
                "effects": {"log": "With a roar, you wrench Caldus's gate enough to squeeze through."},
                "next": "inner_hall",
            },
            {
                "label": "Use tools or credentials to open the gate",
                "requirements": {
                    "any_of": [
                        {"items": ["Lockpicks"]},
                        {"items": ["Bronze Seal"]},
                        {"items": ["Warden Token"]},
                    ]
                },
                "conditional_effects": [
                    {
                        "requirements": {"items": ["Warden Token"]},
                        "effects": {
                            "log": "Caldus's sentries mistake you for sanctioned enforcers and open the outer lock.",
                            "set_flags": {"opened_cleanly": True},
                        },
                    },
                    {
                        "requirements": {"items": ["Bronze Seal"]},
                        "effects": {"log": "The bronze seal — taken from Caldus's own network — clicks into place and the door parts silently."},
                    },
                    {
                        "requirements": {"items": ["Lockpicks"]},
                        "effects": {
                            "log": "Your lockpicks whisper through tumblers Caldus never bothered to change.",
                            "set_flags": {"opened_cleanly": True},
                        },
                    },
                ],
                "next": "inner_hall",
            },
            {
                "label": "Crawl through the collapsed breach (-2 HP)",
                "effects": {"hp": -2, "log": "Jagged stones tear at you as you squeeze beneath Caldus's wards."},
                "next": "inner_hall",
            },
            {
                "label": "Call for surrender and safe passage (merciful path)",
                "requirements": {"flag_true": ["mercy_reputation"]},
                "effects": {"log": "Your reputation for mercy persuades a frightened zealot to unbar a side door. Not all of Caldus's followers believe."},
                "next": "inner_hall",
            },
            {
                "label": "Threaten the lookouts into opening a side gate (ruthless path)",
                "requirements": {"flag_true": ["cruel_reputation"]},
                "effects": {"hp": -1, "log": "They obey out of terror, but one zealot stabs you before fleeing Caldus's ruin."},
                "next": "inner_hall",
            },
        ],
    },
    "inner_hall": {
        "id": "inner_hall",
        "title": "Inner Hall of Echoes",
        "text": (
            "Torchlight reveals two routes through Caldus's occupied ruin: a trapped gallery leading "
            "to his ritual chamber, and an armory vault sealed behind rusted bars. The walls are carved "
            "with scenes of the old kingdom — Caldus has annotated them in charcoal, circling the Dawn "
            "Emblem in every panel."
        ),
        "dialogue": [
            {"speaker": "Ancient Inscription", "line": "Only the careful walk twice these halls."},
            {"speaker": "Caldus's Zealot (distant)", "line": "Check the gallery again! Someone breached the gate!"},
        ],
        "choices": [
            {
                "label": "Disarm and pass the trap gallery (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "set_flags": {"trap_disarmed": True},
                    "log": "You spot pressure plates Caldus wired into the old mechanisms and bypass every trigger.",
                },
                "next": "core_approach",
            },
            {
                "label": "Charge through the trap gallery (-4 HP)",
                "effects": {"hp": -4, "log": "Darts and blades rake you, but you push through Caldus's defenses."},
                "next": "core_approach",
            },
            {
                "label": "Pry open the armory bars (Strength 3)",
                "requirements": {"min_strength": 3, "flag_false": ["armory_looted"]},
                "effects": {
                    "add_items": ["Ancient Shield"],
                    "set_flags": {"armory_looted": True},
                    "log": "You bend the bars and recover an Ancient Shield that predates Caldus's occupation.",
                },
                "next": "inner_hall",
            },
            {
                "label": "Let the Ember Sigil reveal a sealed dawn vault",
                "requirements": {"meta_items": ["Ember Sigil"], "meta_nodes_present": ["dawn_vault"]},
                "effects": {
                    "log": "The sigil's heat exposes a hidden vault door behind Caldus's charcoal notes.",
                },
                "next": "dawn_vault",
            },
            {
                "label": "Use a torch to spot hidden markings and a safer route",
                "requirements": {"items": ["Torch"], "flag_false": ["torch_route_found"]},
                "effects": {
                    "set_flags": {"torch_route_found": True},
                    "log": "Torchlight reveals old chalk marks — pre-dating Caldus — pointing to a concealed side passage.",
                },
                "next": "core_approach",
            },
            {
                "label": "Use the Ashfang Charm to scatter ember-hounds",
                "requirements": {"items": ["Ashfang Charm"]},
                "effects": {
                    "set_flags": {"hounds_scattered": True},
                    "log": "The charm terrifies Caldus's ember-hounds, clearing the corridor.",
                },
                "next": "core_approach",
            },
        ],
    },
    "dawn_vault": {
        "id": "dawn_vault",
        "title": "Vault of the First Dawn",
        "text": (
            "The vault air is warm and still. A crystal reliquary holds a shard of the Dawn Emblem — "
            "the uncorrupted original that Caldus has been trying to replicate. It pulses with light "
            "that does not burn. It feels like it has been waiting for someone who would not misuse it."
        ),
        "dialogue": [
            {"speaker": "Vault Whisper", "line": "Carry the dawn, and the ruin will remember you — not Caldus."},
            {"speaker": "Your Instinct", "line": "This is what the Emblem was before Caldus twisted it. This is the weight of every replay you survived."},
        ],
        "requirements": {"meta_nodes_present": ["dawn_vault"]},
        "choices": [
            {
                "label": "Take the Dawn Relic and seal the vault behind you",
                "requirements": {"meta_missing_items": ["Dawn Relic"]},
                "effects": {
                    "add_items": ["Dawn Relic"],
                    "unlock_meta_items": ["Dawn Relic"],
                    "remove_meta_nodes": ["dawn_vault"],
                    "set_flags": {"dawn_relic_claimed": True},
                    "log": "Light pools around your hands as the relic binds itself to your future journeys — a counterweight to Caldus's corruption.",
                },
                "next": "inner_hall",
            },
            {
                "label": "Close the vault and return to the hall",
                "effects": {"log": "You leave the dawn sealed and step back into Caldus's echoing hall."},
                "next": "inner_hall",
            },
        ],
    },
    "core_approach": {
        "id": "core_approach",
        "title": "Antechamber — Kest's Last Stand",
        "text": (
            "At the threshold of Caldus's ritual chamber kneels Kest, wounded and desperate. Once "
            "Caldus's most trusted scout, Kest deserted when he realized the Dawn Emblem would consume "
            "Oakrest — not restore it. He begs for mercy, offering what he knows about Caldus's defenses."
        ),
        "dialogue": [
            {"speaker": "Kest", "line": "I ran messages for Caldus. I believed in the old kingdom. But he's burning living people to resurrect dead ones."},
            {"speaker": "Kest", "line": "Spare me and I'll tell you where his ward array is weakest. Kill me and walk in blind."},
            {"speaker": "Your Instinct", "line": "Caldus threw this man away. Mercy can save a soul, or sharpen a knife in your back."},
        ],
        "choices": [
            {
                "label": "Spare Kest and take his intelligence on Caldus's defenses",
                "effects": {
                    "set_flags": {"spared_bandit": True, "morality": "merciful", "kest_intel_available": True},
                    "trait_delta": {"trust": 1, "alignment": 1},
                    "log": "Kest reveals the resonance gap in Caldus's ward lattice — a weakness only an insider would know.",
                },
                "next": "ember_ridge_quiet",
            },
            {
                "label": "Execute Kest — Caldus's people deserve no quarter",
                "effects": {
                    "trait_delta": {"trust": -2, "alignment": -2},
                    "seen_events": ["kest_executed"],
                    "set_flags": {"spared_bandit": False, "morality": "ruthless"},
                    "log": "You execute Kest. One fewer variable, but one fewer source of information against Caldus.",
                },
                "irreversible": True,
                "next": "ember_ridge_quiet",
            },
            {
                "label": "Bind Kest with rope and move on",
                "requirements": {"items": ["Rope"]},
                "effects": {
                    "set_flags": {"bound_kest": True, "morality": "merciful"},
                    "trait_delta": {"trust": 1},
                    "log": "You bind Kest securely. He shouts Caldus's ward pattern at your back as you leave.",
                },
                "next": "ember_ridge_quiet",
            },
        ],
    },
    "ember_ridge_quiet": {
        "id": "ember_ridge_quiet",
        "title": "Quiet Beat — The Threshold",
        "text": (
            "Before Caldus's core door, the battle noise fades into dripping water and the Emblem's "
            "deep pulse. For one measured moment, you can center yourself, rally your allies, or "
            "crash through before fear catches up. Beyond this door, Caldus waits."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "This breath will shape your strike more than your blade."},
            {"speaker": "Distant Voices", "line": "We're with you... choose how you carry us in there against Caldus."},
        ],
        "choices": [
            {
                "label": "Steady your breathing and assess the chamber seams",
                "effects": {
                    "hp": 1,
                    "trait_delta": {"trust": 1},
                    "seen_events": ["quiet_beat_centered"],
                    "log": "You slow your pulse and enter with clearer focus, ready for Caldus.",
                },
                "next": "final_confrontation",
            },
            {
                "label": "Share a final plan with your nearby allies",
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"final_plan_shared": True},
                    "seen_events": ["quiet_beat_allied_plan"],
                    "log": "A few quiet words align everyone around one decisive push against Caldus.",
                },
                "next": "final_confrontation",
            },
            {
                "label": "Kick the core door and seize momentum now",
                "effects": {
                    "trait_delta": {"reputation": 1, "alignment": -1},
                    "set_flags": {"charged_finale": True},
                    "log": "You abandon hesitation and crash into Caldus's chamber at full speed.",
                },
                "next": "final_confrontation",
            },
        ],
    },
    "final_confrontation": {
        "id": "final_confrontation",
        "title": "Final Confrontation: Warden Caldus",
        "text": (
            "In the heart of the ruin, Caldus stands before the Dawn Emblem with his arms raised, "
            "channeling molten light through a lattice of old kingdom warding stones. Cracks of fire "
            "spread across the ceiling. He turns to face you — not with rage, but with the absolute "
            "certainty of a man who believes he is saving the world by burning it."
        ),
        "dialogue": [
            {"speaker": "Caldus", "line": "You see destruction. I see rebirth. The old kingdom sleeps inside this fire, and every village I burn is fuel for its return."},
            {"speaker": "Caldus", "line": "Edrin understood, before the Emblem broke him. Vorga understood. Even Kest understood, once. You will too — when Oakrest becomes the pyre."},
            {"speaker": "You", "line": "Oakrest is people, Caldus. Not fuel. It ends here."},
            {"speaker": "Caldus", "line": "Then let the Emblem decide which of us is right."},
        ],
        "choices": [
            {
                "label": "Invoke the Dawn Relic to stabilize the Emblem (legacy path)",
                "requirements": {"items": ["Dawn Relic"]},
                "effects": {
                    "set_flags": {"warden_defeated": True, "ending_quality": "best", "legacy_ending": True},
                    "log": "The relic's uncorrupted light steadies the Emblem, unraveling Caldus's ritual without destroying the chamber.",
                },
                "next": "ending_legacy",
            },
            {
                "label": "Elite class finisher (Warrior, Rogue, or Archer)",
                "requirements": {
                    "any_of": [
                        {"class": ["Warrior"], "min_strength": 5},
                        {"class": ["Rogue"], "min_dexterity": 5, "items": ["Lockpicks"]},
                        {"class": ["Archer"], "min_dexterity": 5, "items": ["Signal Arrows"]},
                    ]
                },
                "conditional_effects": [
                    {
                        "requirements": {"class": ["Warrior"], "min_strength": 5},
                        "effects": {
                            "hp": -2,
                            "set_flags": {"warden_defeated": True, "ending_quality": "best", "warrior_best_ending": True},
                            "log": "You brace the collapsing arch with raw strength, then land the decisive blow on Caldus while he channels the Emblem.",
                        },
                        "next": "ending_best_warrior",
                    },
                    {
                        "requirements": {"class": ["Rogue"], "min_dexterity": 5, "items": ["Lockpicks"]},
                        "effects": {
                            "hp": -1,
                            "set_flags": {"warden_defeated": True, "ending_quality": "best", "rogue_best_ending": True},
                            "log": "You ghost through Caldus's ward lattice and sever the Emblem conduit before the surge can reach Oakrest.",
                        },
                        "next": "ending_best_rogue",
                    },
                    {
                        "requirements": {"class": ["Archer"], "min_dexterity": 5, "items": ["Signal Arrows"]},
                        "effects": {
                            "hp": -1,
                            "set_flags": {"warden_defeated": True, "ending_quality": "best", "archer_best_ending": True},
                            "log": "Your impossible shot severs the vent lattice and collapses Caldus's ritual before the fire reaches Oakrest.",
                        },
                        "next": "ending_best_archer",
                    },
                ],
                "next": "ending_best_warrior",
            },
            {
                "label": "Overpower Caldus in direct combat (Strength 6)",
                "requirements": {"min_strength": 6},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "You shatter Caldus's guard with unstoppable force. He falls, whispering the old kingdom's name.",
                },
                "next": "ending_good",
            },
            {
                "label": "Strike from shadows at the Emblem core (Dexterity 6)",
                "requirements": {"min_dexterity": 6},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "You collapse the Emblem core, but the backlash crushes part of the chamber and Caldus escapes into the rubble.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Review contingency plans and ally-dependent finishers",
                "effects": {"log": "You shift position and assess contingencies earned from earlier missions against Caldus's circle."},
                "next": "final_confrontation_tactics",
            },
            {
                "label": "Desperate assault without an advantage",
                "instant_death": True,
                "effects": {
                    "hp": -8,
                    "set_flags": {"warden_defeated": False, "ending_quality": "bad"},
                    "log": "You rush in blindly. Caldus redirects the Emblem's fire and you are consumed.",
                },
                "next": "ending_bad",
            },
        ],
    },
    "final_confrontation_tactics": {
        "id": "final_confrontation_tactics",
        "title": "Final Confrontation — Contingency Plans",
        "text": (
            "Caldus's ritual falters as you exploit chaos in the chamber. The relationships you built "
            "and the choices you made against his circle — Edrin, Vorga, Kest — now converge into "
            "backup plans that can tip the balance."
        ),
        "dialogue": [
            {"speaker": "Caldus", "line": "You think alliances matter? The old kingdom had allies too. They all burned the same."},
            {"speaker": "Your Instinct", "line": "Every unfinished debt just arrived at the same battlefield. Use them."},
        ],
        "choices": [
            {
                "label": "Exploit Kest's intelligence on Caldus's ward weakness",
                "requirements": {"flag_true": ["spared_bandit"], "min_dexterity": 4},
                "effects": {
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "Using Kest's insider knowledge, you disable the Emblem conduit and Caldus's ritual collapses.",
                },
                "next": "ending_good",
            },
            {
                "label": "Use the hidden-route sabotage to destabilize the chamber",
                "requirements": {"flag_true": ["tunnel_collapsed"], "min_strength": 4},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Your earlier demolition fractures the chamber floor. Caldus falls through burning stone.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Intimidate Caldus's remaining zealots into deserting (ruthless path)",
                "requirements": {"flag_true": ["cruel_reputation"], "min_strength": 4},
                "effects": {
                    "hp": -1,
                    "trait_delta": {"trust": -1},
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Your ruthless reputation shatters the last of Caldus's support. Alone, he cannot maintain the ritual.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Rally freed captives and allies to overwhelm Caldus's defenses (merciful path)",
                "requirements": {"flag_true": ["mercy_reputation"], "min_strength": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "You shield the chamber's survivors, and their gratitude becomes momentum against Caldus.",
                },
                "next": "ending_good",
            },
            {
                "label": "Review volatile fallback plans",
                "effects": {"log": "You pivot toward raw fallback options tied to unresolved bosses and heavy gear."},
                "next": "final_confrontation_fallbacks",
            },
            {
                "label": "Return to your direct assault options",
                "effects": {"log": "You pull back toward the central duel and commit to a direct finishing move against Caldus."},
                "next": "final_confrontation",
            },
        ],
    },
    "final_confrontation_fallbacks": {
        "id": "final_confrontation_fallbacks",
        "title": "Final Confrontation — Volatile Fallbacks",
        "text": (
            "The chamber destabilizes as Caldus's ritual strains the Emblem. Old enemies and "
            "improvised tools become your last-resort finishers — each carrying the consequences "
            "of paths you chose or abandoned."
        ),
        "dialogue": [
            {"speaker": "Caldus", "line": "Break me if you can. The Emblem will finish what I started."},
        ],
        "choices": [
            {
                "label": "Use Edrin's bell-hammer to crack Caldus's ward array",
                "requirements": {"flag_true": ["tidebound_knight_defeated"], "min_strength": 4},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "One crushing blow from Edrin's recovered bell-hammer shatters Caldus's ward lattice.",
                },
                "next": "ending_good",
            },
            {
                "label": "Sir Edrin crashes into the chamber, still bound to Caldus's command",
                "requirements": {"flag_true": ["branch_causeway_completed"], "flag_false": ["tidebound_knight_defeated"], "min_strength": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed", "skipped_causeway_boss_returned": True},
                    "log": "Edrin — Caldus's corrupted mentor — answers the Emblem's call. You survive a two-front duel, but the chamber collapses.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Turn Vorga's seized firebombs against Caldus's Emblem pylons",
                "requirements": {"flag_true": ["pyre_alchemist_defeated"], "min_dexterity": 4},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Vorga's own firebombs collapse two pylons, ending Caldus's ritual in violent ruin.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Vorga returns to reinforce Caldus with fresh firebombs",
                "requirements": {"flag_true": ["branch_mill_completed"], "flag_false": ["pyre_alchemist_defeated"], "min_dexterity": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed", "skipped_mill_boss_returned": True},
                    "log": "Vorga storms in with fresh bombs to defend Caldus. A brutal running fight follows before you can reach the Emblem.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Raise the Ancient Shield and endure the Emblem's backlash",
                "requirements": {"items": ["Ancient Shield"], "min_strength": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "The shield saves you as you push through the Emblem's backlash and fell Caldus.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Return to contingency plans",
                "effects": {"log": "You back away from the worst-case options and reassess cleaner contingencies."},
                "next": "final_confrontation_tactics",
            },
        ],
    },
    # --- ENDINGS ---
    "ending_good": {
        "id": "ending_good",
        "title": "Ending — Dawn Over Oakrest",
        "text": (
            "Caldus falls, and the Dawn Emblem dims to a low ember, its destructive cycle broken. "
            "The ruin sighs as ancient stones settle. Outside, the orange glow fades from the sky and "
            "Oakrest's watchtowers signal the all-clear for the first time in days.\n\n"
            "If your path was merciful, Oakrest hails you as a guardian of both lives and honor — "
            "allies you spared and captives you freed stand beside you at the victory fire. "
            "If your path was ruthless, they praise your strength but fear what you may become — "
            "the silence around your campfire is louder than any cheer.\n\n"
            "Caldus's body is carried from the ruin. Serin insists on a proper burial. Drogath "
            "spits on the grave. The valley retells the choices you made in the forest, and every "
            "ally weighs those decisions against the quiet that follows."
        ),
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Oakrest sees the sunrise because you stood when others broke. We will debate your methods for years — but we are alive to debate."},
            {"speaker": "Signal Runner Tams", "line": "For once I'm carrying harvest counts instead of casualty lists. Caldus is gone."},
        ],
        "choices": [],
    },
    "ending_legacy": {
        "id": "ending_legacy",
        "title": "Ending — Legacy Dawn",
        "text": (
            "The Dawn Relic steadies the Emblem without destroying it, purging Caldus's corruption "
            "from the warding lattice. Caldus staggers backward, watching his life's work unravel — "
            "not in fire, but in calm light. The old kingdom he tried to resurrect speaks through the "
            "relic, and its voice is not the voice of fire. It says: let them live.\n\n"
            "Oakrest inherits a calm sunrise and a relic that answers only to your lineage of choices. "
            "The valley's leaders seal a new oath: no future warden can wield the Emblem without "
            "the trust earned by those who carried it across more than one life."
        ),
        "dialogue": [
            {"speaker": "Caldus (broken)", "line": "The kingdom... it was supposed to return in fire. Why does it forgive them?"},
            {"speaker": "Elder Mara", "line": "You've done what no single journey could. Oakrest will remember every return."},
            {"speaker": "Signal Runner Tams", "line": "It's like the valley knows your footsteps now. Even the Emblem trusts you."},
        ],
        "choices": [],
    },
    "ending_best_warrior": {
        "id": "ending_best_warrior",
        "title": "Best Ending — Iron Dawn of Oakrest",
        "text": (
            "Your warrior's stand saves both the Dawn Emblem and the trapped villagers. You hold "
            "a collapsing arch with raw strength while Caldus's ritual unravels around him. He "
            "reaches for the Emblem one last time, but you are between him and everyone he would burn.\n\n"
            "Caldus trained soldiers to hold lines. You hold one against him.\n\n"
            "Word spreads that you held a collapsing ruin with your bare strength, and Oakrest "
            "names you Shield of the Valley. Children trace chalk outlines of your stance on the "
            "training yard, daring each other to stand just as firm."
        ),
        "dialogue": [
            {"speaker": "Caldus (defeated)", "line": "I trained a hundred soldiers to hold lines. None of them held one against me."},
            {"speaker": "Blacksmith Tor", "line": "I've never seen stone obey a person, until tonight."},
        ],
        "choices": [],
    },
    "ending_best_rogue": {
        "id": "ending_best_rogue",
        "title": "Best Ending — Silent Dawn of Oakrest",
        "text": (
            "Your rogue precision prevents the surge before anyone else sees the danger. You ghost "
            "through Caldus's ward lattice — the same coded network you once ran messages through — "
            "and sever the Emblem conduit with a lockpick where a sword would fail.\n\n"
            "Caldus built a fortress of secrets. You unmade it in silence.\n\n"
            "The Rangers record the night as a flawless victory, and Oakrest entrusts you with "
            "its hidden defenses. Whisper networks keep your name off the lips of raiders, but "
            "etched into every locked vault door."
        ),
        "dialogue": [
            {"speaker": "Caldus (confused)", "line": "How? I warded every— you were inside my network. You knew the codes."},
            {"speaker": "Captain Serin", "line": "No trumpet, no glory march — just perfect work. That's legend enough."},
        ],
        "choices": [],
    },
    "ending_best_archer": {
        "id": "ending_best_archer",
        "title": "Best Ending — Skyfire Dawn of Oakrest",
        "text": (
            "Your final arrow strikes true through storming heat and falling stone, collapsing "
            "Caldus's ritual surge without shattering the chamber. You read the smoke signals one "
            "last time — the same signals you decoded from Caldus's scout corps — and thread your "
            "shot through the only gap in the Emblem's fire.\n\n"
            "Caldus built a pyre that could reach the sky. You shot it down from the ridgeline.\n\n"
            "Oakrest's watchtowers adopt your signal code, and every border village sleeps easier "
            "under your marked sky-lanterns. The belltower keeps your arrow notches carved into "
            "its railing as a promise that Oakrest will always look up first."
        ),
        "dialogue": [
            {"speaker": "Caldus (staring)", "line": "That shot... through the vent lattice... from outside the ward ring. Impossible."},
            {"speaker": "Signal Runner Tams", "line": "I watched that shot arc through fire. We'll be telling it for generations."},
        ],
        "choices": [],
    },
    "ending_mixed": {
        "id": "ending_mixed",
        "title": "Ending — Victory at a Cost",
        "text": (
            "Caldus falls, but the Emblem's backlash tears through the ruin and the surrounding farms. "
            "Oakrest survives, though your name is spoken with equal gratitude and regret. The Ember Tide "
            "scarred the valley before you could stop it — fields that burned will take years to recover.\n\n"
            "Caldus's body is never recovered from the rubble. Some believe he survived. Serin posts "
            "sentries at the ruin for months. Drogath argues it doesn't matter — the ritual is broken.\n\n"
            "Dawnwarden medics and Ashfang labor crews rebuild side by side, but every repaired wall "
            "carries the memory of what was sacrificed. Peace returns, cautious and conditional."
        ),
        "dialogue": [
            {"speaker": "Villager", "line": "We lived... but the valley won't forget the price. Caldus almost won."},
            {"speaker": "Signal Runner Tams", "line": "Half my reports are aid requests now. At least there are people left to ask."},
            {"speaker": "Elder Mara", "line": "You stopped the fire. Not soon enough. But you stopped it."},
        ],
        "choices": [],
    },
    "ending_bad": {
        "id": "ending_bad",
        "title": "Ending — Nightfall Over Oakrest",
        "text": (
            "Your final gamble fails. The Dawn Emblem surges to full power and the forest burns with "
            "unnatural fire — Caldus's vision of rebirth consuming everything in its path. He stands "
            "in the flames, arms raised, laughing and weeping as the old kingdom's phantom streets "
            "shimmer in the heat haze for one terrible moment before collapsing into ash.\n\n"
            "Oakrest is abandoned by sunrise. Caldus dies in the fire he started, but his victory "
            "is complete. Fractured factions scatter into exile, arguing whether mercy or brutality "
            "doomed the valley first. The ruined watchtower remains as a blackened marker: the place "
            "the valley lost its dawn."
        ),
        "dialogue": [
            {"speaker": "Caldus (burning)", "line": "There... do you see it? The old kingdom... it's beautiful... it's..."},
            {"speaker": "Elder Mara", "line": "Remember this night, so we never choose it again."},
            {"speaker": "Signal Runner Tams", "line": "No routes left to run. Just ash and refugees."},
        ],
        "choices": [],
    },
    # --- FAILURE / RECOVERY NODES ---
    "failure_injured": {
        "id": "failure_injured",
        "title": "Setback — Broken but Breathing",
        "text": (
            "You wake in a healer's lean-to, battered and stitched. Caldus's Ember Tide still pulses "
            "in the sky — you lost momentum, but Oakrest still needs you. The ruin is not yet sealed."
        ),
        "dialogue": [
            {"speaker": "Healer Brin", "line": "Pain means you're still in the fight. Caldus won't wait for you to heal — decide fast."},
        ],
        "choices": [
            {
                "label": "Recover slowly and return to the village supply line",
                "effects": {
                    "hp": 4,
                    "trait_delta": {"ember_tide": 1},
                    "set_flags": {"recovered_from_injury": True},
                    "log": "Days pass in recovery. You return with fewer scars than rage, but Caldus's ritual has advanced.",
                },
                "next": "camp_shop",
            },
            {
                "label": "Push through the pain and return to the assault route",
                "effects": {
                    "hp": 2,
                    "trait_delta": {"reputation": 1},
                    "log": "You grit your teeth, bind your wounds, and march back toward Caldus's ruin.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "failure_captured": {
        "id": "failure_captured",
        "title": "Setback — Captured by Caldus's Zealots",
        "text": (
            "Caldus's zealots drag you into a holding pit beneath the ruin. Ember-branded guards "
            "pace above. A loose grate and a distracted sentry offer dangerous chances to break free "
            "before Caldus decides what to do with you."
        ),
        "dialogue": [
            {"speaker": "Zealot Guard", "line": "Caldus says you're either fuel or a convert. Pick one."},
            {"speaker": "Prisoner", "line": "If you're planning something, make it count. They feed the pyre at dawn."},
        ],
        "choices": [
            {
                "label": "Bribe a guard with hidden coin",
                "requirements": {"min_gold": 3},
                "effects": {
                    "gold": -3,
                    "set_flags": {"escaped_capture": True},
                    "log": "A guard pockets your coin and leaves the latch unfastened. Even zealots have a price.",
                },
                "next": "inner_hall",
            },
            {
                "label": "Force the grate and climb out",
                "requirements": {"min_strength": 3},
                "effects": {
                    "hp": -1,
                    "set_flags": {"escaped_capture": True},
                    "log": "You rip the rusted grate loose and climb out bloodied but free of Caldus's pit.",
                },
                "next": "forest_crossroad",
            },
            {
                "label": "Feign loyalty to buy time",
                "instant_death": True,
                "effects": {
                    "set_flags": {"marked_suspect": True},
                    "trait_delta": {"alignment": -1},
                    "log": "Your deception is exposed. Caldus's zealots do not forgive pretenders.",
                },
                "next": "core_approach",
            },
        ],
    },
    "failure_traitor": {
        "id": "failure_traitor",
        "title": "Setback — Branded a Traitor",
        "text": (
            "Caldus's network of informants paints you as a double-agent. Allies hesitate, gates close, "
            "and every decision now carries social risk. You must clear your name or forge ahead alone."
        ),
        "dialogue": [
            {"speaker": "Whispering Crowd", "line": "Hero? Traitor? Even Caldus couldn't tell which you are."},
        ],
        "choices": [
            {
                "label": "Seek Captain Serin and prove your intent",
                "effects": {
                    "trait_delta": {"trust": 2, "reputation": 1},
                    "set_flags": {"traitor_brand_cleared": True, "mercy_reputation": True},
                    "log": "You expose Caldus's forged reports and Serin restores your standing.",
                },
                "next": "dawnwarden_outpost",
            },
            {
                "label": "Work alone through hidden routes",
                "effects": {
                    "trait_delta": {"trust": -1, "reputation": 1},
                    "set_flags": {"traitor_brand_hardened": True, "knows_hidden_route": True},
                    "log": "You stop waiting for forgiveness and carve your own path toward Caldus.",
                },
                "next": "hidden_tunnel",
            },
        ],
    },
    "failure_resource_loss": {
        "id": "failure_resource_loss",
        "title": "Setback — Supplies Lost",
        "text": (
            "A failed push costs you supplies and support. Caldus's sentries stripped your camp while "
            "you fought. You can regroup for stability or gamble on a faster return to the assault."
        ),
        "dialogue": [
            {"speaker": "Trader Venn", "line": "Caldus's riders hit the supply line. You can borrow from me once. After that, the forest collects."},
        ],
        "choices": [
            {
                "label": "Regroup at the roadside camp",
                "effects": {
                    "gold": -2,
                    "hp": 2,
                    "trait_delta": {"ember_tide": 1},
                    "log": "You rebuild your kit from scraps. The delay costs Oakrest time as Caldus's ritual advances.",
                },
                "next": "camp_shop",
            },
            {
                "label": "Call in old favors from the Ashfang scouts",
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"met_ashfang": True},
                    "log": "Ashfang outriders throw you a line and point you back toward Caldus's perimeter.",
                },
                "next": "ashfang_hunt",
            },
        ],
    },
    "death": {
        "id": "death",
        "title": "You Have Fallen",
        "text": (
            "Your wounds are too severe. The quest ends here, and the fate of Oakrest passes to "
            "another soul. Caldus's ritual continues unchallenged. The Ember Tide rises."
        ),
        "dialogue": [
            {"speaker": "Final Thought", "line": "If dawn comes, let it find Oakrest standing — even without me."},
        ],
        "choices": [],
    },
}
