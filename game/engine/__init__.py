"""Core engine helpers that operate independently of the Streamlit UI."""

from game.engine.requirements import check_requirements
from game.engine.state import GameState, state_from_session
from game.engine.state_machine import (
    Rule,
    StateMachine,
    TransitionContext,
    TransitionResult,
    build_context,
    evaluate_transition,
    get_phase,
    get_state_machine,
)

__all__ = [
    "GameState",
    "Rule",
    "StateMachine",
    "TransitionContext",
    "TransitionResult",
    "build_context",
    "check_requirements",
    "evaluate_transition",
    "get_phase",
    "get_state_machine",
    "state_from_session",
]
