import unittest

from game.logic import (
    apply_effects,
    check_requirements,
    get_available_choices,
    resolve_choice_outcome,
    transition_to,
    validate_story_nodes,
)
from game.state import ensure_session_state, reset_game_state
from game.streamlit_compat import st


class LogicTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.current_node = "village_square"
        st.session_state.stats = {"hp": 10, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = ["Rusty Sword"]
        st.session_state.flags = {"class": "Warrior"}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []

    def test_check_requirements_success(self):
        ok, reason = check_requirements({"min_strength": 3, "class": ["Warrior"]})
        self.assertTrue(ok)
        self.assertEqual(reason, "")

    def test_check_requirements_failure(self):
        ok, reason = check_requirements({"min_dexterity": 3})
        self.assertFalse(ok)
        self.assertIn("dexterity", reason.lower())

    def test_check_requirements_any_of(self):
        ok, _ = check_requirements({"any_of": [{"min_strength": 99}, {"min_gold": 5}]})
        self.assertTrue(ok)

    def test_apply_effects_updates_state(self):
        apply_effects(
            {
                "hp": -2,
                "gold": 1,
                "add_items": ["Torch"],
                "set_flags": {"met_scout": True},
                "trait_delta": {"trust": 1},
                "seen_events": ["scout_meeting"],
                "log": "Test event",
            }
        )
        self.assertEqual(st.session_state.stats["hp"], 8)
        self.assertEqual(st.session_state.stats["gold"], 9)
        self.assertIn("Torch", st.session_state.inventory)
        self.assertTrue(st.session_state.flags["met_scout"])
        self.assertEqual(st.session_state.traits["trust"], 1)
        self.assertIn("scout_meeting", st.session_state.seen_events)
        self.assertIn("Test event", st.session_state.event_log)


    def test_apply_effects_updates_factions(self):
        apply_effects({"faction_delta": {"oakrest": 2, "bandits": -1}})
        self.assertEqual(st.session_state.factions["oakrest"], 2)
        self.assertEqual(st.session_state.factions["bandits"], -1)

    def test_get_available_choices_filters_invalid(self):
        node = {
            "choices": [
                {"label": "valid", "requirements": {"min_strength": 4}},
                {"label": "invalid", "requirements": {"min_gold": 99}},
            ]
        }
        available = get_available_choices(node)
        self.assertEqual([c["label"] for c in available], ["valid"])

    def test_resolve_choice_outcome_uses_conditional_next(self):
        choice = {
            "label": "Conditional jump",
            "next": "ending_good",
            "conditional_effects": [
                {"requirements": {"min_strength": 4}, "effects": {"hp": -1}, "next": "ending_bad"}
            ],
        }
        effects, next_node = resolve_choice_outcome(choice)
        self.assertEqual(next_node, "ending_bad")
        self.assertEqual(effects["hp"], -1)

    def test_validate_story_nodes_has_no_warnings(self):
        warnings = validate_story_nodes()
        self.assertEqual([], warnings)

    def test_transition_to_unknown_node_redirects(self):
        transition_to("missing_node")
        self.assertEqual(st.session_state.current_node, "failure_captured")


if __name__ == "__main__":
    unittest.main()
