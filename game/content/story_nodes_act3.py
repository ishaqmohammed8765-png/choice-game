from typing import Any, Dict

STORY_NODES_ACT3: Dict[str, Dict[str, Any]] = {
    "ember_ridge_vigil": {
        "id": "ember_ridge_vigil",
        "title": "Quiet Beat — Ember Ridge Vigil",
        "text": (
            "A hush settles over the ridge as the last light fades. Fires are banked low and even the drummers pause, "
            "giving you a moment to listen to the wind, the breathing of allies, and the ruin's distant hum."
        ),
        "dialogue": [
            {"speaker": "Signal Runner Tams", "line": "Quiet now means fewer mistakes once we move."},
            {"speaker": "Your Instinct", "line": "Let the silence remind you who you're bringing home."},
        ],
        "choices": [
            {
                "label": "Offer a few steadying words to the strike team",
                "effects": {
                    "trait_delta": {"trust": 1},
                    "set_flags": {"ember_ridge_vigil_spoken": True},
                    "log": "Your calm words steel the line without raising another drumbeat.",
                },
                "next": "war_council_hub",
            },
            {
                "label": "Walk the ridge alone and focus on the plan ahead",
                "effects": {
                    "trait_delta": {"reputation": 1},
                    "set_flags": {"ember_ridge_vigil_walked": True},
                    "log": "You trace the ridge in silence, committing every route and risk to memory.",
                },
                "next": "war_council_hub",
            },
        ],
    },
    "hidden_route_assault": {
        "id": "hidden_route_assault",
        "title": "Hidden Route Counterstrike",
        "text": (
            "The service tunnel forks beneath the ruin into a powder store and a prisoner corridor. "
            "You can either gut the raiders' reserves, or escort captives to the breach and risk losing momentum."
        ),
        "dialogue": [
            {"speaker": "Scout's Markings", "line": "Blue chalk means stores. White chalk means survivors."},
            {"speaker": "Your Instinct", "line": "Either path changes the siege, but not in the same way."},
        ],
        "requirements": {"flag_true": ["knows_hidden_route"]},
        "choices": [
            {
                "label": "Ruin the powder cache before the alarm spreads",
                "effects": {
                    "hp": -1,
                    "trait_delta": {"reputation": 1, "alignment": -1},
                    "set_flags": {"ruin_supply_line_cut": True, "opened_cleanly": True},
                    "seen_events": ["hidden_cache_destroyed"],
                    "log": "You flood the cache with lamp oil and sparks, collapsing the raiders' munitions tunnel.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Escort captives through the service culvert",
                "effects": {
                    "trait_delta": {"trust": 2, "alignment": 1},
                    "set_flags": {"rescued_prisoners": True, "mercy_reputation": True},
                    "seen_events": ["captives_escorted"],
                    "log": "You lead captives out first; grateful families spread word of your mercy.",
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
                    "log": "You juggle sabotage and evacuation at once, barely outrunning the blast wave.",
                },
                "next": "ruin_gate",
            },
        ],
    },
    "lonely_approach": {
        "id": "lonely_approach",
        "title": "No-Banner Approach",
        "text": (
            "Without allied cover, the ruin's outer trenches are thicker with patrols than expected. "
            "A horn call sweeps the hillside and you must pick one hard gamble before the encirclement closes."
        ),
        "dialogue": [
            {"speaker": "Raider Spotter", "line": "Single runner on the north ridge! Cut them off!"},
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
                    "log": "You smash through shields and barbed stakes, reaching the gate bloodied but unbroken.",
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
                    "log": "You crawl through black water and emerge inside the ruin perimeter unseen.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Fake surrender, then bolt when they open the cage",
                "effects": {
                    "trait_delta": {"alignment": -1},
                    "log": "The ploy nearly works, but a branded jailer recognizes your face.",
                },
                "next": "failure_captured",
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
                            "log": "Ruin sentries mistake you for sanctioned enforcers and open the outer lock.",
                            "set_flags": {"opened_cleanly": True},
                        },
                    },
                    {
                        "requirements": {"items": ["Bronze Seal"]},
                        "effects": {"log": "The bronze seal clicks into place and the door parts silently."},
                    },
                    {
                        "requirements": {"items": ["Lockpicks"]},
                        "effects": {
                            "log": "Your lockpicks whisper through tumblers untouched for centuries.",
                            "set_flags": {"opened_cleanly": True},
                        },
                    },
                ],
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
                "next": "ember_ridge_quiet",
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
                "next": "ember_ridge_quiet",
            },
            {
                "label": "Bind Kest with rope and move on",
                "requirements": {"items": ["Rope"]},
                "effects": {
                    "set_flags": {"bound_kest": True, "morality": "merciful"},
                    "log": "You bind Kest securely, leaving him alive but helpless.",
                },
                "next": "ember_ridge_quiet",
            },
        ],
    },
    "ember_ridge_quiet": {
        "id": "ember_ridge_quiet",
        "title": "Quiet Beat — Breathing Stone",
        "text": (
            "Before the core door, the battle noise fades into dripping water and distant bells. For one measured minute, "
            "you can center yourself, listen to your allies, or surge forward before fear catches up."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "This breath will shape your strike more than your blade."},
            {"speaker": "Distant Voices", "line": "We're with you... choose how you carry us in there."},
        ],
        "choices": [
            {
                "label": "Steady your breathing and assess the chamber seams",
                "effects": {
                    "hp": 1,
                    "trait_delta": {"trust": 1},
                    "seen_events": ["quiet_beat_centered"],
                    "log": "You slow your pulse and enter with clearer focus.",
                },
                "next": "final_confrontation",
            },
            {
                "label": "Share a final plan with your nearby allies",
                "effects": {
                    "trait_delta": {"trust": 1, "reputation": 1},
                    "set_flags": {"final_plan_shared": True},
                    "seen_events": ["quiet_beat_allied_plan"],
                    "log": "A few quiet words align everyone around one decisive push.",
                },
                "next": "final_confrontation",
            },
            {
                "label": "Kick the core door and seize momentum now",
                "effects": {
                    "trait_delta": {"reputation": 1, "alignment": -1},
                    "set_flags": {"charged_finale": True},
                    "log": "You abandon hesitation and crash into the chamber at full speed.",
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
            {"speaker": "Captain Serin", "line": "If any old enemies still breathe, they'll throw in with the Warden now."},
        ],
        "choices": [
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
                            "log": "You brace the collapsing arch with raw strength, then land the decisive blow.",
                        },
                        "next": "ending_best_warrior",
                    },
                    {
                        "requirements": {"class": ["Rogue"], "min_dexterity": 5, "items": ["Lockpicks"]},
                        "effects": {
                            "hp": -1,
                            "set_flags": {"warden_defeated": True, "ending_quality": "best", "rogue_best_ending": True},
                            "log": "You ghost through the ward lattice and cut the Emblem conduit before it can surge.",
                        },
                        "next": "ending_best_rogue",
                    },
                    {
                        "requirements": {"class": ["Archer"], "min_dexterity": 5, "items": ["Signal Arrows"]},
                        "effects": {
                            "hp": -1,
                            "set_flags": {"warden_defeated": True, "ending_quality": "best", "archer_best_ending": True},
                            "log": "Your impossible shot severs the vent lattice and collapses the Emblem surge before detonation.",
                        },
                        "next": "ending_best_archer",
                    },
                ],
                "next": "ending_best_warrior",
            },
            {
                "label": "Overpower the Warden in direct combat (Strength 6)",
                "requirements": {"min_strength": 6},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "You shatter the Warden's guard with unstoppable force.",
                },
                "next": "ending_good",
            },
            {
                "label": "Strike from shadows at the device core (Dexterity 6)",
                "requirements": {"min_dexterity": 6},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "You collapse the device core, but debris crushes part of the chamber.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Review contingency plans and ally-dependent finishers",
                "effects": {"log": "You shift position and assess prepared contingencies from earlier missions."},
                "next": "final_confrontation_tactics",
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
    "final_confrontation_tactics": {
        "id": "final_confrontation_tactics",
        "title": "Final Confrontation - Contingency Plans",
        "text": (
            "You exploit chaos in the chamber to choose from backup plans earned through earlier mercy, brutality, "
            "and unfinished rival fronts."
        ),
        "dialogue": [
            {"speaker": "Your Instinct", "line": "Every unfinished debt just arrived at the same battlefield."}
        ],
        "choices": [
            {
                "label": "Exploit the opening from your mercy (requires spared Kest)",
                "requirements": {"flag_true": ["spared_bandit"], "min_dexterity": 4},
                "effects": {
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "Using Kest's warning, you disable the device core and win cleanly.",
                },
                "next": "ending_good",
            },
            {
                "label": "Use the hidden-route sabotage to destabilize the chamber",
                "requirements": {"flag_true": ["tunnel_collapsed"], "min_strength": 4},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Your earlier demolition fractures the chamber floor, ending the device in chaos.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Interrogate Kest's old crew code (Lockpicks + ruthless)",
                "requirements": {"items": ["Lockpicks"], "flag_true": ["cruel_reputation"], "min_dexterity": 4},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Your ruthless reputation lets you force a confession and break the warding code.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Protect trapped villagers first (requires merciful outlook)",
                "requirements": {"flag_true": ["mercy_reputation"], "min_strength": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "You shield the captives, then turn their gratitude into momentum against the Warden.",
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
                "effects": {"log": "You pull back toward the central duel and commit to a direct finishing move."},
                "next": "final_confrontation",
            },
        ],
    },
    "final_confrontation_fallbacks": {
        "id": "final_confrontation_fallbacks",
        "title": "Final Confrontation - Volatile Fallbacks",
        "text": (
            "The chamber destabilizes as old enemies and improvised tools become your last-resort finishers."
        ),
        "choices": [
            {
                "label": "Use the drowned knight's bell-hammer to crack the Warden guard",
                "requirements": {"flag_true": ["tidebound_knight_defeated"], "min_strength": 4},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "good"},
                    "log": "One crushing blow from the recovered bell-hammer caves in the Warden's shield rig.",
                },
                "next": "ending_good",
            },
            {
                "label": "The Tidebound Knight you left alive crashes into the chamber",
                "requirements": {"flag_true": ["branch_causeway_completed"], "flag_false": ["tidebound_knight_defeated"], "min_strength": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed", "skipped_causeway_boss_returned": True},
                    "log": "The drowned guardian answers the Warden's bell call. You survive a two-front duel, but the chamber collapses around you.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Turn Vorga's seized firebombs against the Emblem pylons",
                "requirements": {"flag_true": ["pyre_alchemist_defeated"], "min_dexterity": 4},
                "effects": {
                    "hp": -2,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "Your captured firebombs collapse two pylons, ending the channeling rite in violent ruin.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Vorga returns with fresh firebombs after you left the mill unfinished",
                "requirements": {"flag_true": ["branch_mill_completed"], "flag_false": ["pyre_alchemist_defeated"], "min_dexterity": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed", "skipped_mill_boss_returned": True},
                    "log": "Pyre-Alchemist Vorga storms in with replacement bombs and forces a brutal running fight before you can reach the Emblem.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Raise the Ancient Shield and endure the device backlash",
                "requirements": {"items": ["Ancient Shield"], "min_strength": 4},
                "effects": {
                    "hp": -3,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "The shield saves you as you push through the backlash and fell the Warden.",
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
    "ending_good": {
        "id": "ending_good",
        "title": "Ending — Dawn Over Oakrest",
        "text": (
            "The device is stopped before activation, and the Dawn Emblem returns to the village archive under dawnlight. "
            "If your path was merciful, Oakrest hails you as a guardian of both lives and honor; "
            "if ruthless, they praise your strength but fear what you may become. Campfires across the valley retell "
            "the choices you made in the forest, and every ally weighs those decisions against the quiet that follows."
        ),
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Oakrest sees the sunrise because you stood when others broke."},
            {"speaker": "Signal Runner Tams", "line": "For once I'm carrying harvest counts instead of casualty lists."},
        ],
        "choices": [],
    },
    "ending_best_warrior": {
        "id": "ending_best_warrior",
        "title": "Best Ending — Iron Dawn of Oakrest",
        "text": (
            "Your warrior's stand saves both the Dawn Emblem and the trapped villagers. Word spreads that you held "
            "a collapsing ruin with your bare strength, and Oakrest names you Shield of the Valley. Children trace "
            "chalk outlines of your stance on the training yard, daring each other to stand just as firm."
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
            "night as a flawless victory, and Oakrest entrusts you with its hidden defenses. Whisper networks keep "
            "your name off the lips of raiders, but etched into every locked vault door."
        ),
        "dialogue": [
            {"speaker": "Captain Serin", "line": "No trumpet, no glory march—just perfect work. That's legend enough."},
        ],
        "choices": [],
    },
    "ending_best_archer": {
        "id": "ending_best_archer",
        "title": "Best Ending — Skyfire Dawn of Oakrest",
        "text": (
            "Your final arrow strikes true through storming heat and falling stone, collapsing the Emblem surge without "
            "shattering the chamber. Oakrest's watchtowers adopt your signal code, and every border village sleeps easier "
            "under your marked sky-lanterns. The belltower keeps your arrow notches carved into its railing as a promise "
            "that Oakrest will always look up first."
        ),
        "dialogue": [
            {"speaker": "Signal Runner Tams", "line": "I watched that shot arc through fire. We'll be telling it for generations."},
        ],
        "choices": [],
    },
    "ending_mixed": {
        "id": "ending_mixed",
        "title": "Ending — Victory at a Cost",
        "text": (
            "The Warden falls, but the ruin partially collapses and nearby farms are lost in the aftermath. "
            "Oakrest survives, though your name is spoken with equal gratitude and regret. Dawnwarden medics and Ashfang "
            "labor crews rebuild side by side, but every repaired wall carries the memory of what was sacrificed. "
            "Peace returns, cautious and conditional, wrapped around the grief of what could not be saved."
        ),
        "dialogue": [
            {"speaker": "Villager", "line": "We lived... but the valley won't forget the price."},
            {"speaker": "Signal Runner Tams", "line": "Half my reports are aid requests now. At least there are people left to ask."},
        ],
        "choices": [],
    },
    "ending_bad": {
        "id": "ending_bad",
        "title": "Ending — Nightfall Over Oakrest",
        "text": (
            "Your final gamble fails. The device surges to full power and the forest burns with unnatural fire. "
            "Oakrest is abandoned by sunrise, and your tale becomes a warning. Fractured factions scatter into exile, "
            "arguing whether mercy or brutality doomed the valley first. The ruined watchtower remains as a blackened "
            "marker: the place the valley lost its dawn."
        ),
        "dialogue": [
            {"speaker": "Elder Mara", "line": "Remember this night, so we never choose it again."},
            {"speaker": "Signal Runner Tams", "line": "No routes left to run, commander. Just ash and refugees."},
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
                "label": "Push through the pain and return to the assault route",
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
