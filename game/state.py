import copy
from typing import Any, Dict

from game.streamlit_compat import st

from game.data import CLASS_TEMPLATES, FACTION_KEYS, STAT_KEYS, STORY_NODES, TRAIT_KEYS

INTRO_NODE_BY_CLASS = {
    "Warrior": "intro_warrior",
    "Rogue": "intro_rogue",
    "Archer": "intro_archer",
}

# Canonical default values for all game-state fields.
# Used by reset, ensure, snapshot, and load to stay in sync.
_DEFAULT_STATE_FIELDS: Dict[str, Any] = {
    "player_class": None,
    "current_node": None,
    "stats": lambda: {"hp": 0, "gold": 0, "strength": 0, "dexterity": 0},
    "inventory": lambda: [],
    "flags": lambda: {},
    "traits": lambda: {name: 0 for name in TRAIT_KEYS},
    "seen_events": lambda: [],
    "factions": lambda: {name: 0 for name in FACTION_KEYS},
    "decision_history": lambda: [],
    "last_choice_feedback": lambda: [],
    "last_outcome_summary": None,
    "auto_event_summary": lambda: [],
    "pending_auto_death": False,
    "event_log": lambda: [],
    "history": lambda: [],
    "save_blob": "",
    "pending_choice_confirmation": None,
    "show_locked_choices": False,
    "visited_nodes": lambda: [],
    "visited_edges": lambda: [],
    "meta_state": lambda: {"unlocked_items": [], "removed_nodes": []},
}

# Fields that are captured in snapshots for save/load and undo.
_SNAPSHOT_FIELDS = (
    "player_class", "current_node", "stats", "inventory", "flags",
    "traits", "seen_events", "factions", "decision_history",
    "last_choice_feedback", "last_outcome_summary", "auto_event_summary",
    "pending_auto_death", "event_log", "pending_choice_confirmation",
    "visited_nodes", "visited_edges", "meta_state",
)


def _get_default(key: str) -> Any:
    """Return the default value for a state field, calling factory lambdas for mutable types."""
    value = _DEFAULT_STATE_FIELDS[key]
    return value() if callable(value) else value


def reset_game_state() -> None:
    """Reset all session state values to begin a fresh run."""
    meta_state = st.session_state.get("meta_state", _get_default("meta_state"))
    for key in _DEFAULT_STATE_FIELDS:
        setattr(st.session_state, key, _get_default(key))
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
        key: copy.deepcopy(
            st.session_state.get(key, _get_default(key))
        )
        for key in _SNAPSHOT_FIELDS
    }

def load_snapshot(snapshot: Dict[str, Any]) -> None:
    """Restore game state from a validated snapshot."""
    for key in _SNAPSHOT_FIELDS:
        if key == "meta_state":
            continue  # meta_state uses merge logic below
        if key == "visited_nodes" and key not in snapshot:
            setattr(st.session_state, key, [snapshot["current_node"]])
            continue
        setattr(st.session_state, key, snapshot.get(key, _get_default(key)))

    if "meta_state" in snapshot:
        existing_meta = st.session_state.get("meta_state", _get_default("meta_state"))
        incoming_meta = snapshot["meta_state"]
        merged_items = list(dict.fromkeys(existing_meta.get("unlocked_items", []) + incoming_meta.get("unlocked_items", [])))
        merged_nodes = list(dict.fromkeys(existing_meta.get("removed_nodes", []) + incoming_meta.get("removed_nodes", [])))
        st.session_state.meta_state = {"unlocked_items": merged_items, "removed_nodes": merged_nodes}

def ensure_session_state() -> None:
    """Initialize session state keys on first load."""
    if "player_class" not in st.session_state:
        reset_game_state()
    for key in _DEFAULT_STATE_FIELDS:
        if key not in st.session_state:
            setattr(st.session_state, key, _get_default(key))
