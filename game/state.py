import copy
from typing import Any, Dict

import streamlit as st

from game.data import CLASS_TEMPLATES

def reset_game_state() -> None:
    """Reset all session state values to begin a fresh run."""
    st.session_state.player_class = None
    st.session_state.current_node = None
    st.session_state.stats = {"hp": 0, "gold": 0, "strength": 0, "dexterity": 0}
    st.session_state.inventory = []
    st.session_state.flags = {}
    st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
    st.session_state.seen_events = []
    st.session_state.decision_history = []
    st.session_state.last_choice_feedback = []
    st.session_state.event_log = []
    st.session_state.history = []
    st.session_state.save_blob = ""
    st.session_state.pending_choice_confirmation = None

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
    st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
    st.session_state.seen_events = []
    st.session_state.decision_history = []
    st.session_state.last_choice_feedback = []
    st.session_state.event_log = [f"You begin your journey as a {player_class}."]
    st.session_state.history = []
    st.session_state.pending_choice_confirmation = None

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
        "decision_history": copy.deepcopy(st.session_state.decision_history),
        "last_choice_feedback": copy.deepcopy(st.session_state.last_choice_feedback),
        "event_log": copy.deepcopy(st.session_state.event_log),
        "pending_choice_confirmation": copy.deepcopy(st.session_state.pending_choice_confirmation),
    }

def load_snapshot(snapshot: Dict[str, Any]) -> None:
    """Restore game state from a validated snapshot."""
    st.session_state.player_class = snapshot["player_class"]
    st.session_state.current_node = snapshot["current_node"]
    st.session_state.stats = snapshot["stats"]
    st.session_state.inventory = snapshot["inventory"]
    st.session_state.flags = snapshot["flags"]
    st.session_state.traits = snapshot.get("traits", {"trust": 0, "reputation": 0, "alignment": 0})
    st.session_state.seen_events = snapshot.get("seen_events", [])
    st.session_state.decision_history = snapshot.get("decision_history", [])
    st.session_state.last_choice_feedback = snapshot.get("last_choice_feedback", [])
    st.session_state.event_log = snapshot["event_log"]
    st.session_state.pending_choice_confirmation = snapshot.get("pending_choice_confirmation")

def ensure_session_state() -> None:
    """Initialize session state keys on first load."""
    if "player_class" not in st.session_state:
        reset_game_state()
    if "history" not in st.session_state:
        st.session_state.history = []
    if "save_blob" not in st.session_state:
        st.session_state.save_blob = ""
    if "traits" not in st.session_state:
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
    if "seen_events" not in st.session_state:
        st.session_state.seen_events = []
    if "decision_history" not in st.session_state:
        st.session_state.decision_history = []
    if "last_choice_feedback" not in st.session_state:
        st.session_state.last_choice_feedback = []
    if "pending_choice_confirmation" not in st.session_state:
        st.session_state.pending_choice_confirmation = None
