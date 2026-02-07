import copy
from typing import Any, Dict

from game.streamlit_compat import st

from game.data import CLASS_TEMPLATES, FACTION_KEYS, STAT_KEYS, STORY_NODES, TRAIT_KEYS

INTRO_NODE_BY_CLASS = {
    "Warrior": "intro_warrior",
    "Rogue": "intro_rogue",
    "Archer": "intro_archer",
}

def reset_game_state() -> None:
    """Reset all session state values to begin a fresh run."""
    meta_state = st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})
    st.session_state.player_class = None
    st.session_state.current_node = None
    st.session_state.stats = {"hp": 0, "gold": 0, "strength": 0, "dexterity": 0}
    st.session_state.inventory = []
    st.session_state.flags = {}
    st.session_state.traits = {name: 0 for name in TRAIT_KEYS}
    st.session_state.seen_events = []
    st.session_state.factions = {name: 0 for name in FACTION_KEYS}
    st.session_state.decision_history = []
    st.session_state.last_choice_feedback = []
    st.session_state.last_outcome_summary = None
    st.session_state.auto_event_summary = []
    st.session_state.pending_auto_death = False
    st.session_state.event_log = []
    st.session_state.history = []
    st.session_state.save_blob = ""
    st.session_state.pending_choice_confirmation = None
    st.session_state.show_locked_choices = False
    st.session_state.visited_nodes = []
    st.session_state.visited_edges = []
    st.session_state.meta_state = meta_state

def start_game(player_class: str) -> None:
    """Initialize game state from class template and enter first node."""
    template = CLASS_TEMPLATES[player_class]
    meta_state = st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})
    st.session_state.player_class = player_class
    st.session_state.current_node = INTRO_NODE_BY_CLASS.get(player_class, "village_square")
    st.session_state.stats = {
        "hp": template["hp"],
        "gold": template["gold"],
        "strength": template["strength"],
        "dexterity": template["dexterity"],
    }
    st.session_state.inventory = copy.deepcopy(template["inventory"])
    for item in meta_state.get("unlocked_items", []):
        if item not in st.session_state.inventory:
            st.session_state.inventory.append(item)
    st.session_state.flags = {"class": player_class}
    st.session_state.traits = {name: 0 for name in TRAIT_KEYS}
    st.session_state.seen_events = []
    st.session_state.factions = {name: 0 for name in FACTION_KEYS}
    st.session_state.decision_history = []
    st.session_state.last_choice_feedback = []
    st.session_state.last_outcome_summary = None
    st.session_state.auto_event_summary = []
    st.session_state.pending_auto_death = False
    st.session_state.event_log = [f"You begin your journey as a {player_class}."]
    if meta_state.get("unlocked_items"):
        add_log(f"Legacy items carried forward: {', '.join(meta_state['unlocked_items'])}.")
    st.session_state.history = []
    st.session_state.pending_choice_confirmation = None
    st.session_state.show_locked_choices = False
    st.session_state.visited_nodes = [st.session_state.current_node]
    st.session_state.visited_edges = []


def validate_snapshot(snapshot: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a snapshot payload for save/load safety."""
    errors: list[str] = []
    required_keys = {
        "player_class",
        "current_node",
        "stats",
        "inventory",
        "flags",
        "event_log",
        "traits",
        "seen_events",
        "factions",
        "decision_history",
        "last_choice_feedback",
    }
    missing = required_keys - set(snapshot)
    if missing:
        errors.append(f"Missing required keys: {', '.join(sorted(missing))}.")
        return False, errors

    if snapshot["player_class"] not in CLASS_TEMPLATES:
        errors.append("Unknown player_class in save payload.")
    if snapshot["current_node"] not in STORY_NODES:
        errors.append("Current node does not exist in story.")

    stats = snapshot.get("stats", {})
    if not isinstance(stats, dict) or any(stat not in stats for stat in STAT_KEYS):
        errors.append("Stats payload is missing required stat keys.")

    traits = snapshot.get("traits", {})
    if not isinstance(traits, dict) or any(trait not in traits for trait in TRAIT_KEYS):
        errors.append("Traits payload is missing required trait keys.")

    factions = snapshot.get("factions", {})
    if not isinstance(factions, dict) or any(faction not in factions for faction in FACTION_KEYS):
        errors.append("Factions payload is missing required faction keys.")

    if not isinstance(snapshot.get("inventory"), list):
        errors.append("Inventory payload must be a list.")
    if not isinstance(snapshot.get("flags"), dict):
        errors.append("Flags payload must be an object.")
    if not isinstance(snapshot.get("seen_events"), list):
        errors.append("Seen events payload must be a list.")
    if not isinstance(snapshot.get("decision_history"), list):
        errors.append("Decision history payload must be a list.")
    if not isinstance(snapshot.get("last_choice_feedback"), list):
        errors.append("Choice feedback payload must be a list.")
    if not isinstance(snapshot.get("event_log"), list):
        errors.append("Event log payload must be a list.")

    if "visited_nodes" in snapshot and not isinstance(snapshot["visited_nodes"], list):
        errors.append("Visited nodes payload must be a list.")
    if "visited_edges" in snapshot and not isinstance(snapshot["visited_edges"], list):
        errors.append("Visited edges payload must be a list.")

    if "meta_state" in snapshot:
        meta = snapshot["meta_state"]
        if not isinstance(meta, dict):
            errors.append("Meta state payload must be an object.")
        else:
            if "unlocked_items" in meta and not isinstance(meta["unlocked_items"], list):
                errors.append("Meta state unlocked_items must be a list.")
            if "removed_nodes" in meta and not isinstance(meta["removed_nodes"], list):
                errors.append("Meta state removed_nodes must be a list.")

    return not errors, errors

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
        "factions": copy.deepcopy(st.session_state.factions),
        "decision_history": copy.deepcopy(st.session_state.decision_history),
        "last_choice_feedback": copy.deepcopy(st.session_state.last_choice_feedback),
        "last_outcome_summary": copy.deepcopy(st.session_state.last_outcome_summary),
        "auto_event_summary": copy.deepcopy(st.session_state.auto_event_summary),
        "pending_auto_death": copy.deepcopy(st.session_state.pending_auto_death),
        "event_log": copy.deepcopy(st.session_state.event_log),
        "pending_choice_confirmation": copy.deepcopy(st.session_state.pending_choice_confirmation),
        "visited_nodes": copy.deepcopy(st.session_state.visited_nodes),
        "visited_edges": copy.deepcopy(st.session_state.visited_edges),
        "meta_state": copy.deepcopy(st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})),
    }

def load_snapshot(snapshot: Dict[str, Any]) -> None:
    """Restore game state from a validated snapshot."""
    st.session_state.player_class = snapshot["player_class"]
    st.session_state.current_node = snapshot["current_node"]
    st.session_state.stats = snapshot["stats"]
    st.session_state.inventory = snapshot["inventory"]
    st.session_state.flags = snapshot["flags"]
    st.session_state.traits = snapshot.get("traits", {name: 0 for name in TRAIT_KEYS})
    st.session_state.seen_events = snapshot.get("seen_events", [])
    st.session_state.factions = snapshot.get("factions", {name: 0 for name in FACTION_KEYS})
    st.session_state.decision_history = snapshot.get("decision_history", [])
    st.session_state.last_choice_feedback = snapshot.get("last_choice_feedback", [])
    st.session_state.last_outcome_summary = snapshot.get("last_outcome_summary")
    st.session_state.auto_event_summary = snapshot.get("auto_event_summary", [])
    st.session_state.pending_auto_death = snapshot.get("pending_auto_death", False)
    st.session_state.event_log = snapshot["event_log"]
    st.session_state.pending_choice_confirmation = snapshot.get("pending_choice_confirmation")
    st.session_state.visited_nodes = snapshot.get("visited_nodes", [snapshot["current_node"]])
    st.session_state.visited_edges = snapshot.get("visited_edges", [])
    if "meta_state" in snapshot:
        existing_meta = st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})
        incoming_meta = snapshot["meta_state"]
        merged_items = list(dict.fromkeys(existing_meta.get("unlocked_items", []) + incoming_meta.get("unlocked_items", [])))
        merged_nodes = list(dict.fromkeys(existing_meta.get("removed_nodes", []) + incoming_meta.get("removed_nodes", [])))
        st.session_state.meta_state = {"unlocked_items": merged_items, "removed_nodes": merged_nodes}

def ensure_session_state() -> None:
    """Initialize session state keys on first load."""
    if "player_class" not in st.session_state:
        reset_game_state()
    if "history" not in st.session_state:
        st.session_state.history = []
    if "save_blob" not in st.session_state:
        st.session_state.save_blob = ""
    if "traits" not in st.session_state:
        st.session_state.traits = {name: 0 for name in TRAIT_KEYS}
    if "seen_events" not in st.session_state:
        st.session_state.seen_events = []
    if "factions" not in st.session_state:
        st.session_state.factions = {name: 0 for name in FACTION_KEYS}
    if "decision_history" not in st.session_state:
        st.session_state.decision_history = []
    if "last_choice_feedback" not in st.session_state:
        st.session_state.last_choice_feedback = []
    if "pending_choice_confirmation" not in st.session_state:
        st.session_state.pending_choice_confirmation = None
    if "last_outcome_summary" not in st.session_state:
        st.session_state.last_outcome_summary = None
    if "auto_event_summary" not in st.session_state:
        st.session_state.auto_event_summary = []
    if "pending_auto_death" not in st.session_state:
        st.session_state.pending_auto_death = False
    if "show_locked_choices" not in st.session_state:
        st.session_state.show_locked_choices = False
    if "visited_nodes" not in st.session_state:
        st.session_state.visited_nodes = []
    if "visited_edges" not in st.session_state:
        st.session_state.visited_edges = []
    if "meta_state" not in st.session_state:
        st.session_state.meta_state = {"unlocked_items": [], "removed_nodes": []}
