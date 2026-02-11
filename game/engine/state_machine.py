"""State-machine / rule-driven layer that sits on top of the node graph.

The node graph (STORY_NODES) remains the presentation layer - it defines
narrative text, dialogue, and available choices.  The state machine adds:

1. **Rules**: Declarative conditions that can override or redirect transitions.
2. **State phases**: Game-wide phases (exploration, combat, council, finale)
   that activate different rule sets.
3. **Transition hooks**: Pre/post transition callbacks for cross-cutting concerns
   (HP death, failure routing, surprise events).

The node graph is still authoritative for *what content exists*. The state machine
decides *which node to enter next* and *what side-effects fire* during transitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence


# ---------------------------------------------------------------------------
# Core data types
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Rule:
    """A declarative rule that can redirect or modify transitions.

    Rules are evaluated in priority order (lower number = higher priority).
    The first matching rule wins.
    """

    name: str
    priority: int
    condition: Callable[[TransitionContext], bool]
    action: Callable[[TransitionContext], TransitionResult]


@dataclass(slots=True)
class TransitionContext:
    """Snapshot of everything relevant to a transition decision."""

    from_node: str
    to_node: str
    choice_label: str
    phase: str
    stats: Dict[str, int]
    inventory: List[str]
    flags: Dict[str, Any]
    traits: Dict[str, int]
    factions: Dict[str, int]
    visited_nodes: List[str]
    meta_state: Dict[str, Any]
    player_class: Optional[str] = None


@dataclass(slots=True)
class TransitionResult:
    """The outcome of a rule evaluation."""

    redirect_to: Optional[str] = None
    block: bool = False
    block_reason: str = ""
    extra_effects: Optional[Dict[str, Any]] = None
    log_message: str = ""


# ---------------------------------------------------------------------------
# Phase definitions
# ---------------------------------------------------------------------------

PHASE_NODES: Dict[str, List[str]] = {
    "intro": ["intro_warrior", "intro_rogue", "intro_archer"],
    "exploration": [
        "village_square", "camp_shop", "forest_ravine_a", "forest_ravine_b",
        "bandit_hideout", "bandit_negotiation",
    ],
    "combat": [
        "tidebound_causeway", "pyre_mill", "causeway_approach",
        "tidebound_battle", "pyre_battle",
    ],
    "council": [
        "war_council_hub", "war_council_plan", "war_council_debate",
    ],
    "finale": [
        "ember_ridge_vigil", "ruin_gate_breach", "ruin_gate_assault",
        "ruin_gate_stealth", "ruin_gate_diplomacy",
    ],
    "ending": [
        "ending_best", "ending_good", "ending_compromise",
        "ending_survival", "ending_tragic", "ending_legacy",
    ],
    "failure": [
        "failure_injured", "failure_captured",
        "failure_traitor", "failure_resource_loss", "death",
    ],
}

# Reverse lookup: node_id -> phase
_NODE_PHASE_MAP: Dict[str, str] = {}
for _phase, _nodes in PHASE_NODES.items():
    for _nid in _nodes:
        _NODE_PHASE_MAP[_nid] = _phase


def get_phase(node_id: str) -> str:
    """Return the game phase for a given node, defaulting to 'exploration'."""
    # Keep phase badges resilient even when content adds new node IDs.
    if node_id:
        if node_id.startswith("ending_"):
            return "ending"
        if node_id.startswith("failure_"):
            return "failure"
        if node_id.startswith("intro_"):
            return "intro"
    return _NODE_PHASE_MAP.get(node_id, "exploration")


# ---------------------------------------------------------------------------
# Built-in rules
# ---------------------------------------------------------------------------


def _rule_hp_death(ctx: TransitionContext) -> bool:
    return ctx.stats.get("hp", 0) <= 0


def _action_hp_death(_ctx: TransitionContext) -> TransitionResult:
    return TransitionResult(
        redirect_to="death",
        log_message="You collapse from your wounds. Your journey ends here.",
    )


def _rule_missing_node(ctx: TransitionContext) -> bool:
    from game.data import STORY_NODES
    return ctx.to_node not in STORY_NODES


def _action_missing_node(ctx: TransitionContext) -> TransitionResult:
    from game.data import STORY_NODES
    fallback = "failure_captured" if "failure_captured" in STORY_NODES else "death"
    return TransitionResult(
        redirect_to=fallback,
        log_message=f"Broken path detected for '{ctx.to_node}'. Rerouted to fallback.",
    )


def _rule_failure_loop(ctx: TransitionContext) -> bool:
    """Prevent infinite failure loops by checking if we're already in a failure node."""
    return (
        ctx.from_node.startswith("failure_")
        and ctx.to_node.startswith("failure_")
        and ctx.to_node == ctx.from_node
    )


def _action_failure_loop(_ctx: TransitionContext) -> TransitionResult:
    return TransitionResult(
        redirect_to="death",
        log_message="You cannot recover from this situation.",
    )


def _rule_ember_tide_escalation(ctx: TransitionContext) -> bool:
    """Auto-escalate ember tide effects during finale phase."""
    return ctx.phase == "finale" and ctx.traits.get("ember_tide", 0) >= 7


def _action_ember_tide_escalation(_ctx: TransitionContext) -> TransitionResult:
    return TransitionResult(
        extra_effects={"hp": -1, "log": "The Ember Tide scorches everything around you."},
        log_message="Ember Tide burns at critical levels.",
    )


def _rule_low_reputation_council(ctx: TransitionContext) -> bool:
    """Block council access if reputation is too low."""
    return (
        ctx.phase == "council"
        and ctx.to_node == "war_council_hub"
        and ctx.traits.get("reputation", 0) <= -3
    )


def _action_low_reputation_council(_ctx: TransitionContext) -> TransitionResult:
    return TransitionResult(
        redirect_to="failure_traitor",
        log_message="Your reputation precedes you. The council refuses entry.",
    )


# The default rule set, evaluated in priority order
DEFAULT_RULES: List[Rule] = [
    Rule("hp_death", priority=0, condition=_rule_hp_death, action=_action_hp_death),
    Rule("missing_node", priority=1, condition=_rule_missing_node, action=_action_missing_node),
    Rule("failure_loop", priority=2, condition=_rule_failure_loop, action=_action_failure_loop),
    Rule("ember_escalation", priority=10, condition=_rule_ember_tide_escalation, action=_action_ember_tide_escalation),
    Rule("low_rep_council", priority=10, condition=_rule_low_reputation_council, action=_action_low_reputation_council),
]


# ---------------------------------------------------------------------------
# State Machine
# ---------------------------------------------------------------------------


@dataclass
class StateMachine:
    """Hybrid state machine that wraps the node graph with rule evaluation.

    Usage:
        sm = StateMachine()
        result = sm.evaluate_transition(context)
        # result tells you the actual destination and any side effects
    """

    rules: List[Rule] = field(default_factory=lambda: list(DEFAULT_RULES))
    _phase_rules: Dict[str, List[Rule]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rules.sort(key=lambda r: r.priority)

    def add_rule(self, rule: Rule) -> None:
        """Register a new rule, maintaining priority order."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)

    def add_phase_rule(self, phase: str, rule: Rule) -> None:
        """Register a rule that only applies during a specific phase."""
        self._phase_rules.setdefault(phase, []).append(rule)
        self._phase_rules[phase].sort(key=lambda r: r.priority)

    def evaluate_transition(self, ctx: TransitionContext) -> TransitionResult:
        """Evaluate all applicable rules and return the combined result.

        Rules are checked in priority order. The first rule that matches
        and produces a redirect wins for destination. Extra effects from
        all matching rules are merged.
        """
        final = TransitionResult()
        all_rules = list(self.rules)

        # Add phase-specific rules
        phase_rules = self._phase_rules.get(ctx.phase, [])
        if phase_rules:
            all_rules = sorted(all_rules + phase_rules, key=lambda r: r.priority)

        for rule in all_rules:
            if not rule.condition(ctx):
                continue

            result = rule.action(ctx)

            # First redirect wins
            if result.redirect_to and not final.redirect_to:
                final.redirect_to = result.redirect_to

            if result.block and not final.block:
                final.block = True
                final.block_reason = result.block_reason

            # Merge extra effects
            if result.extra_effects:
                if final.extra_effects is None:
                    final.extra_effects = {}
                for key, val in result.extra_effects.items():
                    if isinstance(val, (int, float)) and key in final.extra_effects:
                        final.extra_effects[key] = final.extra_effects[key] + val
                    else:
                        final.extra_effects[key] = val

            if result.log_message:
                if final.log_message:
                    final.log_message += " " + result.log_message
                else:
                    final.log_message = result.log_message

        return final

    def get_valid_transitions(
        self,
        from_node: str,
        choices: Sequence[Dict[str, Any]],
        session_state: Any,
    ) -> List[Dict[str, Any]]:
        """Filter choices through the state machine, returning only valid ones.

        Each returned choice is annotated with a '_sm_result' key containing
        the TransitionResult, so the UI can show redirect info if needed.
        """
        valid = []
        for choice in choices:
            next_node = choice.get("next", "")
            ctx = build_context(from_node, next_node, choice.get("label", ""), session_state)

            result = self.evaluate_transition(ctx)
            if result.block:
                continue

            annotated = dict(choice)
            annotated["_sm_result"] = result
            valid.append(annotated)

        return valid


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Singleton instance
_MACHINE: Optional[StateMachine] = None


def get_state_machine() -> StateMachine:
    """Return the singleton StateMachine instance."""
    global _MACHINE
    if _MACHINE is None:
        _MACHINE = StateMachine()
    return _MACHINE


def build_context(
    from_node: str,
    to_node: str,
    choice_label: str,
    session_state: Any,
) -> TransitionContext:
    """Build a TransitionContext from the current session state."""
    return TransitionContext(
        from_node=from_node,
        to_node=to_node,
        choice_label=choice_label,
        phase=get_phase(from_node),
        stats=dict(getattr(session_state, "stats", {}) or {}),
        inventory=list(getattr(session_state, "inventory", []) or []),
        flags=dict(getattr(session_state, "flags", {}) or {}),
        traits=dict(getattr(session_state, "traits", {}) or {}),
        factions=dict(getattr(session_state, "factions", {}) or {}),
        visited_nodes=list(getattr(session_state, "visited_nodes", []) or []),
        meta_state=dict(getattr(session_state, "meta_state", {}) or {}),
        player_class=getattr(session_state, "player_class", None),
    )


def evaluate_transition(
    from_node: str,
    to_node: str,
    choice_label: str,
    session_state: Any,
) -> TransitionResult:
    """Convenience wrapper: evaluate a transition through the singleton machine."""
    ctx = build_context(from_node, to_node, choice_label, session_state)
    return get_state_machine().evaluate_transition(ctx)
