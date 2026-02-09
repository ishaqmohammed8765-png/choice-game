import copy
import json
import os
from pathlib import Path
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
    "show_path_map": False,
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


_META_PROGRESS_PATH = Path(__file__).resolve().parents[1] / ".oakrest_meta_state.json"


def _get_default(key: str) -> Any:
    """Return the default value for a state field, calling factory lambdas for mutable types."""
    value = _DEFAULT_STATE_FIELDS[key]
    return value() if callable(value) else value


def _coerce_string_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        values = list(raw.keys())
    elif isinstance(raw, (list, tuple, set)):
        values = list(raw)
    elif isinstance(raw, str):
        values = [raw]
    else:
        return []
    normalized: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in normalized:
            continue
        normalized.append(text)
    return normalized


def normalize_meta_state(meta_state: Dict[str, Any] | None) -> Dict[str, list[str]]:
    if not isinstance(meta_state, dict):
        return {"unlocked_items": [], "removed_nodes": []}

    # Accept legacy payload keys so older saves still carry progression.
    unlocked = (
        meta_state.get("unlocked_items")
        if "unlocked_items" in meta_state
        else meta_state.get("legacy_items", meta_state.get("meta_items", []))
    )
    removed = (
        meta_state.get("removed_nodes")
        if "removed_nodes" in meta_state
        else meta_state.get("removed_meta_nodes", meta_state.get("removed_locations", []))
    )
    return {
        "unlocked_items": _coerce_string_list(unlocked),
        "removed_nodes": _coerce_string_list(removed),
    }


def _meta_persistence_enabled() -> bool:
    return "PYTEST_CURRENT_TEST" not in os.environ


def _merge_meta_state(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, list[str]]:
    existing_norm = normalize_meta_state(existing)
    incoming_norm = normalize_meta_state(incoming)
    return {
        "unlocked_items": list(
            dict.fromkeys(existing_norm["unlocked_items"] + incoming_norm["unlocked_items"])
        ),
        "removed_nodes": list(
            dict.fromkeys(existing_norm["removed_nodes"] + incoming_norm["removed_nodes"])
        ),
    }


def _load_persistent_meta_state() -> Dict[str, list[str]]:
    if not _meta_persistence_enabled():
        return normalize_meta_state(None)
    if not _META_PROGRESS_PATH.exists():
        return normalize_meta_state(None)
    try:
        payload = json.loads(_META_PROGRESS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return normalize_meta_state(None)
    return normalize_meta_state(payload)


def persist_meta_state(meta_state: Dict[str, Any]) -> None:
    """Persist cross-run legacy progression to disk."""
    normalized = normalize_meta_state(meta_state)
    st.session_state.meta_state = normalized
    if not _meta_persistence_enabled():
        return
    try:
        _META_PROGRESS_PATH.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    except OSError:
        return


def reset_game_state() -> None:
    """Reset all session state values to begin a fresh run."""
    persisted_meta = _load_persistent_meta_state()
    session_meta = st.session_state.get("meta_state", _get_default("meta_state"))
    meta_state = _merge_meta_state(persisted_meta, session_meta)
    for key in _DEFAULT_STATE_FIELDS:
        setattr(st.session_state, key, _get_default(key))
    st.session_state.meta_state = meta_state
    persist_meta_state(meta_state)

def start_game(player_class: str) -> None:
    """Initialize game state from class template and enter first node."""
    template = CLASS_TEMPLATES[player_class]
    persisted_meta = _load_persistent_meta_state()
    session_meta = st.session_state.get("meta_state", {"unlocked_items": [], "removed_nodes": []})
    meta_state = _merge_meta_state(persisted_meta, session_meta)
    st.session_state.meta_state = meta_state
    persist_meta_state(meta_state)
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
    st.session_state.show_path_map = False
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
    if isinstance(snapshot.get("visited_edges"), list):
        for edge in snapshot["visited_edges"]:
            if not isinstance(edge, dict):
                errors.append("Visited edges entries must be objects.")
                break
            if "from" not in edge or "to" not in edge:
                errors.append("Visited edges entries must include 'from' and 'to'.")
                break
            if not isinstance(edge["from"], str) or not isinstance(edge["to"], str):
                errors.append("Visited edge endpoints must be strings.")
                break

    if "history" in snapshot and not isinstance(snapshot["history"], list):
        errors.append("History payload must be a list.")

    if "pending_choice_confirmation" in snapshot:
        pending = snapshot["pending_choice_confirmation"]
        if pending is not None and not isinstance(pending, dict):
            errors.append("Pending choice confirmation must be an object or null.")
        elif isinstance(pending, dict):
            if "node" in pending and not isinstance(pending["node"], str):
                errors.append("Pending choice confirmation node must be a string.")
            if "choice_index" in pending and not isinstance(pending["choice_index"], int):
                errors.append("Pending choice confirmation choice_index must be an integer.")
            if "label" in pending and not isinstance(pending["label"], str):
                errors.append("Pending choice confirmation label must be a string.")
            if "warnings" in pending and not isinstance(pending["warnings"], list):
                errors.append("Pending choice confirmation warnings must be a list.")

    if "auto_event_summary" in snapshot and not isinstance(snapshot["auto_event_summary"], list):
        errors.append("Auto event summary payload must be a list.")

    if "last_outcome_summary" in snapshot:
        summary = snapshot["last_outcome_summary"]
        if summary is not None and not isinstance(summary, dict):
            errors.append("Last outcome summary payload must be an object or null.")

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
        st.session_state.meta_state = _merge_meta_state(existing_meta, incoming_meta)
        persist_meta_state(st.session_state.meta_state)

def ensure_session_state() -> None:
    """Initialize session state keys on first load."""
    if "player_class" not in st.session_state:
        reset_game_state()
    for key in _DEFAULT_STATE_FIELDS:
        if key not in st.session_state:
            setattr(st.session_state, key, _get_default(key))
    st.session_state.meta_state = _merge_meta_state(
        st.session_state.get("meta_state", _get_default("meta_state")),
        _load_persistent_meta_state(),
    )
