"""Expanded tests covering execute_choice, merge_effects, auto-choices,
morality flags, choice warnings, simplification, and edge cases."""

import copy
import unittest

from game.data import STORY_NODES
from game.logic import (
    apply_effects,
    apply_morality_flags,
    apply_node_auto_choices,
    check_requirements,
    execute_choice,
    get_choice_warnings,
    merge_effects,
    resolve_choice_outcome,
    transition_to,
)
from game.state import (
    ensure_session_state,
    load_snapshot,
    reset_game_state,
    snapshot_state,
    start_game,
    validate_snapshot,
)
from game.streamlit_compat import st


class MergeEffectsTests(unittest.TestCase):
    def test_additive_stat_merging(self):
        base = {"hp": -2, "gold": 3}
        incoming = {"hp": -1, "gold": 2}
        merged = merge_effects(base, incoming)
        self.assertEqual(merged["hp"], -3)
        self.assertEqual(merged["gold"], 5)

    def test_item_dedup(self):
        base = {"add_items": ["Torch", "Rope"]}
        incoming = {"add_items": ["Rope", "Shield"]}
        merged = merge_effects(base, incoming)
        self.assertEqual(sorted(merged["add_items"]), ["Rope", "Shield", "Torch"])

    def test_flag_override(self):
        base = {"set_flags": {"met_scout": True}}
        incoming = {"set_flags": {"met_scout": False, "found_relic": True}}
        merged = merge_effects(base, incoming)
        self.assertFalse(merged["set_flags"]["met_scout"])
        self.assertTrue(merged["set_flags"]["found_relic"])

    def test_trait_delta_addition(self):
        base = {"trait_delta": {"trust": 2}}
        incoming = {"trait_delta": {"trust": -1, "reputation": 3}}
        merged = merge_effects(base, incoming)
        self.assertEqual(merged["trait_delta"]["trust"], 1)
        self.assertEqual(merged["trait_delta"]["reputation"], 3)

    def test_faction_delta_addition(self):
        base = {"faction_delta": {"oakrest": 1}}
        incoming = {"faction_delta": {"oakrest": 2, "bandits": -1}}
        merged = merge_effects(base, incoming)
        self.assertEqual(merged["faction_delta"]["oakrest"], 3)
        self.assertEqual(merged["faction_delta"]["bandits"], -1)

    def test_log_override(self):
        base = {"log": "old message"}
        incoming = {"log": "new message"}
        merged = merge_effects(base, incoming)
        self.assertEqual(merged["log"], "new message")

    def test_seen_events_dedup(self):
        base = {"seen_events": ["event_a"]}
        incoming = {"seen_events": ["event_a", "event_b"]}
        merged = merge_effects(base, incoming)
        self.assertEqual(sorted(merged["seen_events"]), ["event_a", "event_b"])


class MoralityFlagsTests(unittest.TestCase):
    def test_merciful_sets_mercy(self):
        flags = {"morality": "merciful"}
        apply_morality_flags(flags)
        self.assertTrue(flags["mercy_reputation"])
        self.assertFalse(flags["cruel_reputation"])

    def test_ruthless_sets_cruel(self):
        flags = {"morality": "ruthless"}
        apply_morality_flags(flags)
        self.assertFalse(flags["mercy_reputation"])
        self.assertTrue(flags["cruel_reputation"])

    def test_no_morality_unchanged(self):
        flags = {"some_other_flag": True}
        apply_morality_flags(flags)
        self.assertNotIn("mercy_reputation", flags)
        self.assertNotIn("cruel_reputation", flags)


class ChoiceWarningsTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.stats = {"hp": 10, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = []
        st.session_state.flags = {}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}

    def test_irreversible_warning(self):
        choice = {"label": "Test", "irreversible": True, "next": "death", "effects": {}}
        warnings = get_choice_warnings(choice)
        self.assertTrue(any("Irreversible" in w for w in warnings))

    def test_instant_death_warning(self):
        choice = {"label": "Test", "instant_death": True, "next": "death", "effects": {}}
        warnings = get_choice_warnings(choice)
        self.assertTrue(any("Lethal" in w or "death" in w.lower() for w in warnings))

    def test_high_hp_cost_warning(self):
        choice = {"label": "Test", "next": "village_square", "effects": {"hp": -5}}
        warnings = get_choice_warnings(choice)
        self.assertTrue(any("HP" in w for w in warnings))

    def test_high_gold_cost_warning(self):
        choice = {"label": "Test", "next": "village_square", "effects": {"gold": -6}}
        warnings = get_choice_warnings(choice)
        self.assertTrue(any("gold" in w.lower() for w in warnings))

    def test_no_warnings_for_safe_choice(self):
        choice = {"label": "Test", "next": "village_square", "effects": {"hp": -1}}
        warnings = get_choice_warnings(choice)
        self.assertEqual(warnings, [])


class ExecuteChoiceTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.current_node = "village_square"
        st.session_state.stats = {"hp": 10, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = ["Rusty Sword"]
        st.session_state.flags = {"class": "Warrior"}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.factions = {"oakrest": 0, "dawnwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []
        st.session_state.decision_history = []
        st.session_state.history = []
        st.session_state.visited_nodes = []
        st.session_state.visited_edges = []
        st.session_state.pending_choice_confirmation = None

    def test_execute_choice_transitions_and_records(self):
        choice = {
            "label": "Go to camp",
            "next": "camp_shop",
            "effects": {"gold": -2},
        }
        execute_choice("village_square", "Go to camp", choice)
        self.assertEqual(st.session_state.current_node, "camp_shop")
        self.assertEqual(st.session_state.stats["gold"], 6)
        self.assertIn("village_square", st.session_state.visited_nodes)
        self.assertIn("camp_shop", st.session_state.visited_nodes)
        self.assertTrue(len(st.session_state.history) > 0)
        self.assertEqual(st.session_state.decision_history[-1]["choice"], "Go to camp")

    def test_execute_choice_instant_death(self):
        choice = {
            "label": "Fatal choice",
            "next": "ending_good",
            "effects": {},
            "instant_death": True,
        }
        execute_choice("village_square", "Fatal choice", choice)
        self.assertEqual(st.session_state.current_node, "death")

    def test_execute_choice_irreversible_clears_history(self):
        st.session_state.history = [{"fake": "snapshot"}]
        choice = {
            "label": "Point of no return",
            "next": "camp_shop",
            "effects": {},
            "irreversible": True,
        }
        execute_choice("village_square", "Point of no return", choice)
        self.assertEqual(st.session_state.history, [])

    def test_execute_choice_missing_node_falls_back(self):
        choice = {
            "label": "Broken link",
            "next": "nonexistent_node",
            "effects": {},
        }
        execute_choice("village_square", "Broken link", choice)
        # Should route to failure_captured or death, not crash
        self.assertIn(st.session_state.current_node, {"failure_captured", "death"})


class GoldClampingTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.stats = {"hp": 10, "gold": 3, "strength": 4, "dexterity": 2}
        st.session_state.inventory = []
        st.session_state.flags = {}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.factions = {"oakrest": 0, "dawnwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []

    def test_gold_cannot_go_negative(self):
        apply_effects({"gold": -10})
        self.assertEqual(st.session_state.stats["gold"], 0)

    def test_hp_can_go_negative(self):
        """HP is allowed to go negative; death is handled by transition logic."""
        apply_effects({"hp": -20})
        self.assertLess(st.session_state.stats["hp"], 0)


class AutoChoiceTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.stats = {"hp": 10, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = []
        st.session_state.flags = {"class": "Warrior"}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.factions = {"oakrest": 0, "dawnwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []

    def test_auto_choice_applies_effects(self):
        node = {
            "auto_choices": [
                {"label": "Auto heal", "next": "village_square", "effects": {"hp": 2}},
            ],
            "choices": [],
        }
        result = apply_node_auto_choices("test_node", node)
        self.assertTrue(result)
        self.assertEqual(st.session_state.stats["hp"], 12)

    def test_auto_choice_fires_only_once(self):
        node = {
            "auto_choices": [
                {"label": "Auto heal", "next": "village_square", "effects": {"hp": 2}},
            ],
            "choices": [],
        }
        apply_node_auto_choices("test_once_node", node)
        hp_after_first = st.session_state.stats["hp"]
        result = apply_node_auto_choices("test_once_node", node)
        self.assertFalse(result)
        self.assertEqual(st.session_state.stats["hp"], hp_after_first)

    def test_auto_choice_respects_requirements(self):
        node = {
            "auto_choices": [
                {
                    "label": "Need gold",
                    "next": "village_square",
                    "effects": {"hp": 5},
                    "requirements": {"min_gold": 999},
                },
            ],
            "choices": [],
        }
        result = apply_node_auto_choices("test_req_node", node)
        self.assertFalse(result)
        self.assertEqual(st.session_state.stats["hp"], 10)


class SnapshotIntegrationTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()

    def test_full_roundtrip_preserves_all_fields(self):
        start_game("Rogue")
        st.session_state.stats["gold"] += 5
        st.session_state.flags["met_king"] = True
        st.session_state.traits["trust"] = 3
        st.session_state.factions["oakrest"] = 2
        st.session_state.inventory.append("Magic Ring")
        st.session_state.seen_events.append("king_audience")

        snap = snapshot_state()

        reset_game_state()
        start_game("Warrior")

        load_snapshot(snap)

        self.assertEqual(st.session_state.player_class, "Rogue")
        self.assertEqual(st.session_state.stats["gold"], 15)
        self.assertTrue(st.session_state.flags["met_king"])
        self.assertEqual(st.session_state.traits["trust"], 3)
        self.assertEqual(st.session_state.factions["oakrest"], 2)
        self.assertIn("Magic Ring", st.session_state.inventory)
        self.assertIn("king_audience", st.session_state.seen_events)

    def test_validate_rejects_bad_stats_type(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["stats"] = "not a dict"
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)
        self.assertTrue(any("stats" in e.lower() for e in errors))

    def test_validate_rejects_invalid_class(self):
        snap = snapshot_state()
        snap["player_class"] = "Mage"
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)

    def test_snapshot_isolation(self):
        """Snapshots must be deep copies — mutating state must not affect the snapshot."""
        start_game("Warrior")
        snap = snapshot_state()
        original_gold = snap["stats"]["gold"]
        st.session_state.stats["gold"] += 100
        self.assertEqual(snap["stats"]["gold"], original_gold)


class SimplificationTests(unittest.TestCase):
    def test_auto_apply_choices_extracted(self):
        """Nodes with auto_apply choices should have them in auto_choices after simplification."""
        for node_id, node in STORY_NODES.items():
            for choice in node.get("choices", []):
                self.assertFalse(
                    choice.get("auto_apply", False),
                    f"Choice in {node_id} still has auto_apply=True after simplification",
                )

    def test_no_exact_duplicate_choices(self):
        """No two choices in the same node should have identical next+requirements+effects."""

        def freeze(value):
            if isinstance(value, dict):
                return tuple((k, freeze(value[k])) for k in sorted(value))
            if isinstance(value, list):
                return tuple(freeze(item) for item in value)
            return value

        for node_id, node in STORY_NODES.items():
            seen_keys = set()
            for choice in node.get("choices", []):
                key = (
                    choice.get("next"),
                    freeze(choice.get("requirements", {})),
                    freeze(choice.get("effects", {})),
                    freeze(choice.get("conditional_effects", [])),
                )
                self.assertNotIn(
                    key, seen_keys,
                    f"Duplicate choice found in {node_id}: {choice.get('label')}",
                )
                seen_keys.add(key)


if __name__ == "__main__":
    unittest.main()
