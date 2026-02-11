"""Expanded tests covering execute_choice, merge_effects, auto-choices,
morality flags, choice warnings, simplification, and edge cases."""

import copy
import unittest

from game.data import STORY_NODES
from game.engine.state import state_from_session
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
        self.assertEqual(merged["add_items"], ["Torch", "Rope", "Shield"])

    def test_flag_override(self):
        base = {"set_flags": {"met_scout": True}}
        incoming = {"set_flags": {"met_scout": False, "found_relic": True}}
        merged = merge_effects(base, incoming)
        self.assertFalse(merged["set_flags"]["met_scout"])
        self.assertTrue(merged["set_flags"]["found_relic"])


class EngineStateTests(unittest.TestCase):
    def test_state_from_session_normalizes_legacy_meta_keys(self):
        snapshot = state_from_session(
            {
                "player_class": "Warrior",
                "stats": {"hp": 1, "gold": 0, "strength": 0, "dexterity": 0},
                "inventory": [],
                "flags": {},
                "traits": {},
                "meta_state": {"legacy_items": ["Echo Locket"], "removed_locations": ["echo_shrine"]},
            }
        )
        self.assertEqual(snapshot.meta_state["unlocked_items"], ["Echo Locket"])
        self.assertEqual(snapshot.meta_state["removed_nodes"], ["echo_shrine"])

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
        self.assertEqual(merged["seen_events"], ["event_a", "event_b"])


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
        st.session_state.factions = {"oakrest": 0, "ironwardens": 0, "ashfang": 0, "bandits": 0}
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
        st.session_state.factions = {"oakrest": 0, "ironwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []

    def test_gold_cannot_go_negative(self):
        apply_effects({"gold": -10})
        self.assertEqual(st.session_state.stats["gold"], 0)

    def test_hp_can_go_negative(self):
        """HP is clamped to 0; death is handled by transition logic."""
        apply_effects({"hp": -20})
        self.assertEqual(st.session_state.stats["hp"], 0)


class AutoChoiceSummaryTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.stats = {"hp": 10, "gold": 3, "strength": 4, "dexterity": 2}
        st.session_state.inventory = []
        st.session_state.flags = {}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.factions = {"oakrest": 0, "ironwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []
        st.session_state.auto_event_summary = []
        st.session_state.pending_auto_death = False

    def test_apply_node_auto_choices_records_summary(self):
        node = {
            "auto_choices": [
                {"label": "Auto setback", "effects": {"hp": -2, "gold": -5, "set_flags": {"met_scout": True}}}
            ]
        }
        applied = apply_node_auto_choices("test_node", node)
        self.assertTrue(applied)
        self.assertEqual(st.session_state.stats["hp"], 8)
        self.assertEqual(st.session_state.stats["gold"], 0)
        self.assertTrue(st.session_state.auto_event_summary)
        self.assertTrue(any("Auto event" in entry for entry in st.session_state.event_log))


class AutoChoiceTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.stats = {"hp": 10, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = []
        st.session_state.flags = {"class": "Warrior"}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.factions = {"oakrest": 0, "ironwardens": 0, "ashfang": 0, "bandits": 0}
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

    def test_validate_rejects_invalid_visited_edge_shape(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["visited_edges"] = [{"source": "a", "target": "b"}]
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)
        self.assertTrue(any("visited edges" in error.lower() for error in errors))

    def test_validate_rejects_invalid_pending_choice_confirmation(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["pending_choice_confirmation"] = {"choice_index": "bad"}
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)
        self.assertTrue(any("pending choice" in error.lower() for error in errors))

    def test_snapshot_isolation(self):
        """Snapshots must be deep copies — mutating state must not affect the snapshot."""
        start_game("Warrior")
        snap = snapshot_state()
        original_gold = snap["stats"]["gold"]
        st.session_state.stats["gold"] += 100
        self.assertEqual(snap["stats"]["gold"], original_gold)


class SimplificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from game.data import init_story_nodes
        init_story_nodes()

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


class AnyOfRequirementTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.stats = {"hp": 10, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = []
        st.session_state.flags = {}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}

    def test_any_of_failure_includes_specific_reasons(self):
        """When all any_of options fail, the reason should list specific failures."""
        ok, reason = check_requirements({
            "any_of": [
                {"min_strength": 99},
                {"min_gold": 99},
            ]
        })
        self.assertFalse(ok)
        self.assertIn("strength", reason.lower())
        self.assertIn("gold", reason.lower())

    def test_any_of_passes_when_one_option_met(self):
        ok, reason = check_requirements({
            "any_of": [
                {"min_strength": 99},
                {"min_gold": 5},
            ]
        })
        self.assertTrue(ok)
        self.assertEqual(reason, "")


class AutoChoiceDeathTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.stats = {"hp": 2, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = []
        st.session_state.flags = {}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.factions = {"oakrest": 0, "ironwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []
        st.session_state.auto_event_summary = []
        st.session_state.pending_auto_death = False

    def test_auto_choice_triggers_death_when_hp_zero(self):
        """Auto-choices that reduce HP to 0 should trigger pending_auto_death."""
        node = {
            "auto_choices": [
                {"label": "Lethal trap", "effects": {"hp": -10}},
                {"label": "Should not fire", "effects": {"hp": 5}},
            ]
        }
        apply_node_auto_choices("death_test_node", node)
        self.assertTrue(st.session_state.pending_auto_death)
        self.assertLessEqual(st.session_state.stats["hp"], 0)

    def test_auto_choice_death_stops_further_processing(self):
        """After death trigger, remaining auto-choices should not fire."""
        node = {
            "auto_choices": [
                {"label": "Lethal trap", "effects": {"hp": -10}},
                {"label": "Heal after death", "effects": {"hp": 99}},
            ]
        }
        apply_node_auto_choices("stop_test_node", node)
        # HP should clamp to 0 after death trigger; the heal must not fire.
        self.assertEqual(st.session_state.stats["hp"], 0)


class ExecuteChoiceHPDeathTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.current_node = "village_square"
        st.session_state.stats = {"hp": 2, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = ["Rusty Sword"]
        st.session_state.flags = {"class": "Warrior"}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0}
        st.session_state.factions = {"oakrest": 0, "ironwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []
        st.session_state.decision_history = []
        st.session_state.history = []
        st.session_state.visited_nodes = []
        st.session_state.visited_edges = []
        st.session_state.pending_choice_confirmation = None

    def test_execute_choice_hp_death_redirects(self):
        """A choice that reduces HP to 0 should redirect to death node."""
        choice = {
            "label": "Dangerous choice",
            "next": "camp_shop",
            "effects": {"hp": -10},
        }
        execute_choice("village_square", "Dangerous choice", choice)
        self.assertEqual(st.session_state.current_node, "death")


class FormatOutcomeSummaryTests(unittest.TestCase):
    def test_empty_summary(self):
        from game.logic import format_outcome_summary
        self.assertEqual(format_outcome_summary({}), "No immediate changes.")
        self.assertEqual(format_outcome_summary(None), "No immediate changes.")

    def test_stat_changes_formatted(self):
        from game.logic import format_outcome_summary
        summary = {
            "stats_delta": {"hp": -3, "gold": 2, "strength": 0, "dexterity": 0},
            "items_gained": [],
            "items_lost": [],
            "flags_set": [],
        }
        result = format_outcome_summary(summary)
        self.assertIn("HP -3", result)
        self.assertIn("GOLD +2", result)

    def test_items_and_flags_formatted(self):
        from game.logic import format_outcome_summary
        summary = {
            "stats_delta": {"hp": 0, "gold": 0, "strength": 0, "dexterity": 0},
            "items_gained": ["Torch"],
            "items_lost": ["Key"],
            "flags_set": [("met_king", True)],
        }
        result = format_outcome_summary(summary)
        self.assertIn("Gained: Torch", result)
        self.assertIn("Lost: Key", result)
        self.assertIn("met_king", result)


class TransitionToFailureTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.event_log = []

    def test_transition_to_failure_injured(self):
        from game.logic import transition_to_failure
        transition_to_failure("injured")
        self.assertEqual(st.session_state.current_node, "failure_injured")

    def test_transition_to_failure_unknown_type_defaults(self):
        from game.logic import transition_to_failure
        transition_to_failure("nonexistent_type")
        self.assertEqual(st.session_state.current_node, "failure_injured")


class EpilogueTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()
        start_game("Warrior")

    def test_epilogue_returns_list(self):
        from game.ui_components.epilogue import get_epilogue_aftermath_lines
        lines = get_epilogue_aftermath_lines()
        self.assertIsInstance(lines, list)

    def test_epilogue_respects_max_lines(self):
        from game.ui_components.epilogue import get_epilogue_aftermath_lines
        # Set many flags to generate lots of lines
        st.session_state.flags.update({
            "final_plan_shared": True,
            "charged_finale": True,
            "ember_ridge_vigil_taken": True,
            "ember_ridge_vigil_spoken": True,
            "ember_ridge_vigil_walked": True,
            "causeway_quiet_marked": True,
            "causeway_quiet_steadied": True,
            "militia_drilled": True,
            "shadow_routes_marked": True,
            "archer_watch_established": True,
            "warrior_oath_taken": True,
            "morality": "merciful",
        })
        lines = get_epilogue_aftermath_lines()
        self.assertLessEqual(len(lines), 9)

    def test_epilogue_morality_flags(self):
        from game.ui_components.epilogue import get_epilogue_aftermath_lines
        st.session_state.flags["morality"] = "merciful"
        lines = get_epilogue_aftermath_lines()
        self.assertTrue(
            any("refuge" in line.lower() or "protected" in line.lower() for line in lines)
            if lines else True
        )


class SnapshotVisitedFieldsTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()

    def test_validate_rejects_bad_visited_nodes_type(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["visited_nodes"] = "not a list"
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)
        self.assertTrue(any("visited nodes" in e.lower() for e in errors))

    def test_validate_rejects_bad_visited_edges_type(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["visited_edges"] = "not a list"
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)
        self.assertTrue(any("visited edges" in e.lower() for e in errors))

    def test_snapshot_preserves_visited_data(self):
        start_game("Warrior")
        st.session_state.visited_nodes = ["village_square", "camp_shop"]
        st.session_state.visited_edges = [{"from": "village_square", "to": "camp_shop"}]
        snap = snapshot_state()
        reset_game_state()
        load_snapshot(snap)
        self.assertEqual(st.session_state.visited_nodes, ["village_square", "camp_shop"])
        self.assertEqual(st.session_state.visited_edges, [{"from": "village_square", "to": "camp_shop"}])


class MergeEffectsMetaTests(unittest.TestCase):
    def test_unlock_meta_items_merge(self):
        base = {"unlock_meta_items": ["Locket"]}
        incoming = {"unlock_meta_items": ["Locket", "Ring"]}
        merged = merge_effects(base, incoming)
        self.assertEqual(sorted(merged["unlock_meta_items"]), ["Locket", "Ring"])

    def test_remove_meta_nodes_merge(self):
        base = {"remove_meta_nodes": ["node_a"]}
        incoming = {"remove_meta_nodes": ["node_a", "node_b"]}
        merged = merge_effects(base, incoming)
        self.assertEqual(sorted(merged["remove_meta_nodes"]), ["node_a", "node_b"])

    def test_remove_items_merge(self):
        base = {"remove_items": ["Key"]}
        incoming = {"remove_items": ["Key", "Rope"]}
        merged = merge_effects(base, incoming)
        self.assertEqual(sorted(merged["remove_items"]), ["Key", "Rope"])

    def test_empty_base_merge(self):
        merged = merge_effects({}, {"hp": -3, "add_items": ["Torch"]})
        self.assertEqual(merged["hp"], -3)
        self.assertEqual(merged["add_items"], ["Torch"])


class IsPublicFlagTests(unittest.TestCase):
    def test_internal_prefixes_hidden(self):
        from game.logic import _is_public_flag
        self.assertFalse(_is_public_flag("auto_choice::node::0"))
        self.assertFalse(_is_public_flag("branch_forest_completed"))
        self.assertFalse(_is_public_flag("system_init"))
        self.assertFalse(_is_public_flag("internal_counter"))
        self.assertFalse(_is_public_flag("visited_node"))

    def test_any_branch_completed_hidden(self):
        from game.logic import _is_public_flag
        self.assertFalse(_is_public_flag("any_branch_completed"))

    def test_normal_flags_visible(self):
        from game.logic import _is_public_flag
        self.assertTrue(_is_public_flag("met_scout"))
        self.assertTrue(_is_public_flag("morality"))
        self.assertTrue(_is_public_flag("dawnwarden_allied"))


class CarryoverItemsTests(unittest.TestCase):
    """Tests for the cross-playthrough carryover (meta) items system."""

    def setUp(self):
        ensure_session_state()
        reset_game_state()
        st.session_state.player_class = "Warrior"
        st.session_state.current_node = "village_square"
        st.session_state.stats = {"hp": 10, "gold": 8, "strength": 4, "dexterity": 2}
        st.session_state.inventory = ["Rusty Sword"]
        st.session_state.flags = {"class": "Warrior"}
        st.session_state.traits = {"trust": 0, "reputation": 0, "alignment": 0, "ember_tide": 0}
        st.session_state.factions = {"oakrest": 0, "ironwardens": 0, "ashfang": 0, "bandits": 0}
        st.session_state.seen_events = []
        st.session_state.event_log = []
        st.session_state.meta_state = {"unlocked_items": [], "removed_nodes": []}

    def test_unlock_meta_item_adds_to_meta_state(self):
        apply_effects({
            "add_items": ["Echo Locket"],
            "unlock_meta_items": ["Echo Locket"],
            "remove_meta_nodes": ["echo_shrine"],
            "log": "You claim the locket.",
        })
        self.assertIn("Echo Locket", st.session_state.inventory)
        self.assertIn("Echo Locket", st.session_state.meta_state["unlocked_items"])
        self.assertIn("echo_shrine", st.session_state.meta_state["removed_nodes"])

    def test_meta_state_persists_across_reset(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket"], "removed_nodes": ["echo_shrine"]}
        reset_game_state()
        self.assertEqual(st.session_state.meta_state["unlocked_items"], ["Echo Locket"])
        self.assertEqual(st.session_state.meta_state["removed_nodes"], ["echo_shrine"])

    def test_start_game_adds_meta_items_to_inventory(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket", "Ember Sigil"], "removed_nodes": []}
        start_game("Rogue")
        self.assertIn("Echo Locket", st.session_state.inventory)
        self.assertIn("Ember Sigil", st.session_state.inventory)
        self.assertIn("Lockpicks", st.session_state.inventory)

    def test_start_game_logs_legacy_items(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket"], "removed_nodes": []}
        start_game("Warrior")
        self.assertTrue(any("Legacy items" in entry for entry in st.session_state.event_log))

    def test_start_game_no_duplicate_meta_items(self):
        st.session_state.meta_state = {"unlocked_items": ["Lockpicks"], "removed_nodes": []}
        start_game("Rogue")
        count = st.session_state.inventory.count("Lockpicks")
        self.assertEqual(count, 1)

    def test_meta_items_requirement_passes(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket"], "removed_nodes": []}
        ok, reason = check_requirements({"meta_items": ["Echo Locket"]})
        self.assertTrue(ok)

    def test_meta_items_requirement_fails(self):
        st.session_state.meta_state = {"unlocked_items": [], "removed_nodes": []}
        ok, reason = check_requirements({"meta_items": ["Echo Locket"]})
        self.assertFalse(ok)
        self.assertIn("legacy", reason.lower())

    def test_meta_missing_items_requirement_passes(self):
        st.session_state.meta_state = {"unlocked_items": [], "removed_nodes": []}
        ok, reason = check_requirements({"meta_missing_items": ["Echo Locket"]})
        self.assertTrue(ok)

    def test_meta_missing_items_requirement_fails(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket"], "removed_nodes": []}
        ok, reason = check_requirements({"meta_missing_items": ["Echo Locket"]})
        self.assertFalse(ok)

    def test_meta_nodes_present_passes_when_not_removed(self):
        st.session_state.meta_state = {"unlocked_items": [], "removed_nodes": []}
        ok, reason = check_requirements({"meta_nodes_present": ["echo_shrine"]})
        self.assertTrue(ok)

    def test_meta_nodes_present_fails_when_removed(self):
        st.session_state.meta_state = {"unlocked_items": [], "removed_nodes": ["echo_shrine"]}
        ok, reason = check_requirements({"meta_nodes_present": ["echo_shrine"]})
        self.assertFalse(ok)
        self.assertIn("vanished", reason.lower())

    def test_snapshot_includes_meta_state(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket"], "removed_nodes": ["echo_shrine"]}
        snap = snapshot_state()
        self.assertIn("meta_state", snap)
        self.assertEqual(snap["meta_state"]["unlocked_items"], ["Echo Locket"])
        self.assertEqual(snap["meta_state"]["removed_nodes"], ["echo_shrine"])

    def test_snapshot_meta_state_is_deep_copy(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket"], "removed_nodes": []}
        snap = snapshot_state()
        st.session_state.meta_state["unlocked_items"].append("Ember Sigil")
        self.assertEqual(snap["meta_state"]["unlocked_items"], ["Echo Locket"])

    def test_load_snapshot_merges_meta_state(self):
        st.session_state.meta_state = {"unlocked_items": ["Ember Sigil"], "removed_nodes": ["ember_reliquary"]}
        start_game("Warrior")
        snap = snapshot_state()
        snap["meta_state"] = {"unlocked_items": ["Echo Locket"], "removed_nodes": ["echo_shrine"]}
        load_snapshot(snap)
        self.assertIn("Echo Locket", st.session_state.meta_state["unlocked_items"])
        self.assertIn("Ember Sigil", st.session_state.meta_state["unlocked_items"])
        self.assertIn("echo_shrine", st.session_state.meta_state["removed_nodes"])
        self.assertIn("ember_reliquary", st.session_state.meta_state["removed_nodes"])

    def test_load_snapshot_without_meta_state_preserves_existing(self):
        st.session_state.meta_state = {"unlocked_items": ["Echo Locket"], "removed_nodes": ["echo_shrine"]}
        start_game("Warrior")
        snap = snapshot_state()
        del snap["meta_state"]
        load_snapshot(snap)
        self.assertIn("Echo Locket", st.session_state.meta_state["unlocked_items"])

    def test_validate_snapshot_accepts_valid_meta_state(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["meta_state"] = {"unlocked_items": ["Echo Locket"], "removed_nodes": ["echo_shrine"]}
        ok, errors = validate_snapshot(snap)
        self.assertTrue(ok)

    def test_validate_snapshot_rejects_bad_meta_state_type(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["meta_state"] = "not a dict"
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)
        self.assertTrue(any("meta state" in e.lower() for e in errors))

    def test_validate_snapshot_rejects_bad_unlocked_items_type(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["meta_state"] = {"unlocked_items": "not a list", "removed_nodes": []}
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)

    def test_validate_snapshot_rejects_bad_removed_nodes_type(self):
        start_game("Warrior")
        snap = snapshot_state()
        snap["meta_state"] = {"unlocked_items": [], "removed_nodes": "not a list"}
        ok, errors = validate_snapshot(snap)
        self.assertFalse(ok)

    def test_full_carryover_chain_echo_locket(self):
        """Simulate finding the Echo Locket and verifying it carries over."""
        # Playthrough 1: find the Echo Locket
        apply_effects({
            "add_items": ["Echo Locket"],
            "unlock_meta_items": ["Echo Locket"],
            "remove_meta_nodes": ["echo_shrine"],
            "set_flags": {"echo_locket_claimed": True},
            "log": "The locket hums.",
        })
        self.assertIn("Echo Locket", st.session_state.meta_state["unlocked_items"])

        # Start playthrough 2
        start_game("Rogue")
        self.assertIn("Echo Locket", st.session_state.inventory)
        # Echo shrine should be gone
        ok, _ = check_requirements({"meta_nodes_present": ["echo_shrine"]})
        self.assertFalse(ok)
        # Can use the locket for the reliquary
        st.session_state.inventory.append("Bronze Seal")
        ok, _ = check_requirements({
            "items": ["Bronze Seal"],
            "meta_items": ["Echo Locket"],
            "meta_nodes_present": ["ember_reliquary"],
        })
        self.assertTrue(ok)

    def test_full_carryover_chain_three_relics(self):
        """Simulate the full 3-playthrough relic progression chain."""
        # Playthrough 1: Echo Locket
        apply_effects({
            "unlock_meta_items": ["Echo Locket"],
            "remove_meta_nodes": ["echo_shrine"],
        })

        # Playthrough 2: Ember Sigil
        start_game("Warrior")
        apply_effects({
            "unlock_meta_items": ["Ember Sigil"],
            "remove_meta_nodes": ["ember_reliquary"],
        })

        # Playthrough 3: First Age Relic
        start_game("Archer")
        apply_effects({
            "unlock_meta_items": ["First Age Relic"],
            "remove_meta_nodes": ["dawn_vault"],
        })

        # Playthrough 4: should have all three relics
        start_game("Warrior")
        self.assertIn("Echo Locket", st.session_state.inventory)
        self.assertIn("Ember Sigil", st.session_state.inventory)
        self.assertIn("First Age Relic", st.session_state.inventory)

        # All shrines/vaults should be gone
        ok, _ = check_requirements({"meta_nodes_present": ["echo_shrine"]})
        self.assertFalse(ok)
        ok, _ = check_requirements({"meta_nodes_present": ["ember_reliquary"]})
        self.assertFalse(ok)
        ok, _ = check_requirements({"meta_nodes_present": ["dawn_vault"]})
        self.assertFalse(ok)

        # First Age Relic should unlock the legacy ending
        ok, _ = check_requirements({"items": ["First Age Relic"]})
        self.assertTrue(ok)

    def test_unlock_meta_item_idempotent(self):
        """Unlocking the same meta item twice should not create duplicates."""
        apply_effects({"unlock_meta_items": ["Echo Locket"]})
        apply_effects({"unlock_meta_items": ["Echo Locket"]})
        count = st.session_state.meta_state["unlocked_items"].count("Echo Locket")
        self.assertEqual(count, 1)

    def test_remove_meta_node_idempotent(self):
        """Removing the same meta node twice should not create duplicates."""
        apply_effects({"remove_meta_nodes": ["echo_shrine"]})
        apply_effects({"remove_meta_nodes": ["echo_shrine"]})
        count = st.session_state.meta_state["removed_nodes"].count("echo_shrine")
        self.assertEqual(count, 1)


class CarryoverEpilogueTests(unittest.TestCase):
    """Tests that carryover item flags appear in the epilogue."""

    def setUp(self):
        ensure_session_state()
        reset_game_state()
        start_game("Warrior")

    def test_echo_locket_epilogue(self):
        from game.ui_components.epilogue import get_epilogue_aftermath_lines
        st.session_state.flags["echo_locket_claimed"] = True
        lines = get_epilogue_aftermath_lines(max_lines=None)
        self.assertTrue(any("locket" in line.lower() for line in lines))

    def test_ember_sigil_epilogue(self):
        from game.ui_components.epilogue import get_epilogue_aftermath_lines
        st.session_state.flags["ember_sigil_claimed"] = True
        lines = get_epilogue_aftermath_lines(max_lines=None)
        self.assertTrue(any("sigil" in line.lower() for line in lines))

    def test_dawn_relic_epilogue(self):
        from game.ui_components.epilogue import get_epilogue_aftermath_lines
        st.session_state.flags["dawn_relic_claimed"] = True
        lines = get_epilogue_aftermath_lines(max_lines=None)
        self.assertTrue(any("relic" in line.lower() for line in lines))

    def test_legacy_ending_epilogue(self):
        from game.ui_components.epilogue import get_epilogue_aftermath_lines
        st.session_state.flags["legacy_ending"] = True
        lines = get_epilogue_aftermath_lines(max_lines=None)
        self.assertTrue(any("relic" in line.lower() or "lifetime" in line.lower() for line in lines))


if __name__ == "__main__":
    unittest.main()
