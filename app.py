import copy
from typing import Any, Dict, List

import streamlit as st


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
            "and a missing relic known as the Dawn Sigil. Elder Mara asks you to track the threat before nightfall."
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
                "label": "Take the forest road toward the old watchtower",
                "effects": {"log": "You leave Oakrest and follow the shadowed road into the forest."},
                "next": "forest_crossroad",
            },
        ],
    },
    "forest_crossroad": {
        "id": "forest_crossroad",
        "title": "Forest Crossroad",
        "text": (
            "Pines crowd around a fork in the path. To the left: a narrow ravine crossing. "
            "To the right: a campfire glow where bandits argue over spoils."
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
                    "set_flags": {"rescued_scout": True, "spared_bandit": False, "cruel_reputation": True},
                    "log": "You defeat the bandits brutally and free the scout.",
                },
                "next": "scout_report",
            },
            {
                "label": "Cut the scout free while hidden (Dexterity 4)",
                "requirements": {"min_dexterity": 4},
                "effects": {
                    "set_flags": {"rescued_scout": True, "spared_bandit": True, "mercy_reputation": True},
                    "log": "You free the scout without a fight; the bandits flee into darkness.",
                },
                "next": "scout_report",
            },
            {
                "label": "Accept Kest's bribe and walk away (+6 gold)",
                "effects": {
                    "gold": 6,
                    "set_flags": {"abandoned_scout": True, "cruel_reputation": True},
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
            "The rescued scout gasps that cultists have occupied the ancient ruin and prepare a blood ritual. "
            "He offers a bronze ruin seal that can open hidden doors."
        ),
        "requirements": {"flag_true": ["rescued_scout"]},
        "choices": [
            {
                "label": "Accept the bronze seal",
                "requirements": {"missing_items": ["Bronze Seal"]},
                "effects": {
                    "add_items": ["Bronze Seal"],
                    "set_flags": {"has_seal": True},
                    "log": "You take the bronze seal; old runes glow faintly.",
                },
                "next": "ruin_gate",
            },
            {
                "label": "Refuse and hurry to the ruin",
                "effects": {"log": "You refuse the token and press onward."},
                "next": "ruin_gate",
            },
        ],
    },
    "ruin_gate": {
        "id": "ruin_gate",
        "title": "Ancient Ruin Gate",
        "text": (
            "Cracked stone doors loom beneath ivy and carved suns. A collapsed side breach leads downward, "
            "while the main gate bears a lock made for old sigils."
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
                "requirements": {"class": ["Rogue"]},
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
        ],
    },
    "inner_hall": {
        "id": "inner_hall",
        "title": "Inner Hall of Echoes",
        "text": (
            "Torchlight reveals two routes: a trapped gallery leading to the ritual chamber, "
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
                "next": "ritual_approach",
            },
            {
                "label": "Charge through the trap gallery (-4 HP)",
                "effects": {"hp": -4, "log": "Darts and blades rake you, but you push through."},
                "next": "ritual_approach",
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
        ],
    },
    "ritual_approach": {
        "id": "ritual_approach",
        "title": "Antechamber of Judgement",
        "text": (
            "At the chamber's threshold kneels Kest, wounded and desperate. He claims the cult betrayed everyone "
            "and begs for mercy. Your choice here may define your fate."
        ),
        "choices": [
            {
                "label": "Spare Kest and take his warning",
                "effects": {
                    "set_flags": {"spared_bandit": True, "mercy_reputation": True},
                    "log": "You spare Kest. He reveals a weakness in the Warden's guard.",
                },
                "next": "final_confrontation",
            },
            {
                "label": "Execute Kest",
                "effects": {
                    "set_flags": {"spared_bandit": False, "cruel_reputation": True},
                    "log": "You execute Kest and step over his body into the chamber.",
                },
                "next": "final_confrontation",
            },
            {
                "label": "Bind Kest with rope and move on",
                "requirements": {"items": ["Rope"]},
                "effects": {
                    "set_flags": {"bound_kest": True},
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
            "In the heart of the ruin, the armored Warden channels power into the Dawn Sigil. "
            "You must end the ritual before Oakrest burns."
        ),
        "choices": [
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
                    "log": "Using Kest's warning, you disable the ritual focus and win cleanly.",
                },
                "next": "ending_good",
            },
            {
                "label": "Strike from shadows at the ritual focus (Dexterity 5)",
                "requirements": {"min_dexterity": 5},
                "effects": {
                    "hp": -1,
                    "set_flags": {"warden_defeated": True, "ending_quality": "mixed"},
                    "log": "You collapse the ritual focus, but debris crushes part of the chamber.",
                },
                "next": "ending_mixed",
            },
            {
                "label": "Raise the Ancient Shield and endure the ritual backlash",
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
            "The ritual is stopped before completion. The Dawn Sigil is returned to the village shrine, "
            "and Oakrest celebrates you as a measured hero whose choices spared lives and saved the realm."
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
        "title": "Ending — Night Without Dawn",
        "text": (
            "Your final gamble fails. The ritual surges to completion and the forest burns with unnatural fire. "
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
    st.session_state.event_log = []


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
    st.session_state.event_log = [f"You begin your journey as a {player_class}."]


def add_log(message: str) -> None:
    """Append a narrative event to the player log."""
    if message:
        st.session_state.event_log.append(message)


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

    if effects.get("log"):
        add_log(effects["log"])


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

    # Death can happen from previous choice effects.
    if st.session_state.stats["hp"] <= 0:
        transition_to("death")
        st.rerun()
        return

    choices = node.get("choices", [])
    available = get_available_choices(node)

    if not choices:
        st.success("The story has reached an ending. Restart to explore another path.")
        return

    if not available:
        st.warning("No valid choices remain based on your current stats, items, and flags.")
        if st.button("Accept your fate", type="primary"):
            transition_to("death")
            st.rerun()
        return

    st.subheader("What do you do?")
    for idx, choice in enumerate(available):
        label = choice["label"]
        if st.button(label, key=f"choice_{node_id}_{idx}", use_container_width=True):
            apply_effects(choice.get("effects"))
            transition_to(choice["next"])
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


def ensure_session_state() -> None:
    """Initialize session state keys on first load."""
    if "player_class" not in st.session_state:
        reset_game_state()


# -----------------------------
# App entry point
# -----------------------------
def main() -> None:
    st.set_page_config(page_title="Oakrest: Deterministic Adventure", page_icon="🛡️", layout="centered")
    ensure_session_state()

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
    render_node()
    render_log()


if __name__ == "__main__":
    main()


# -----------------------------
# README (quick start)
# -----------------------------
# 1) pip install streamlit
# 2) streamlit run app.py
