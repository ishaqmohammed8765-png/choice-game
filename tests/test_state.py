import unittest

from game.state import (
    ensure_session_state,
    load_snapshot,
    reset_game_state,
    snapshot_state,
    start_game,
    validate_snapshot,
)
from game.streamlit_compat import st


class StateTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()

    def test_start_game_initializes_expected_keys(self):
        start_game("Rogue")
        self.assertEqual(st.session_state.player_class, "Rogue")
        self.assertEqual(st.session_state.current_node, "intro_rogue")
        self.assertIn("Lockpicks", st.session_state.inventory)


    def test_reset_initializes_toggle_and_factions(self):
        self.assertIn("oakrest", st.session_state.factions)
        self.assertFalse(st.session_state.show_locked_choices)

    def test_snapshot_roundtrip(self):
        start_game("Warrior")
        st.session_state.stats["gold"] += 3
        snap = snapshot_state()

        st.session_state.stats["gold"] = 0
        load_snapshot(snap)
        self.assertEqual(st.session_state.stats["gold"], snap["stats"]["gold"])

    def test_validate_snapshot_accepts_roundtrip_payload(self):
        start_game("Archer")
        snap = snapshot_state()
        ok, errors = validate_snapshot(snap)
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_validate_snapshot_rejects_missing_data(self):
        ok, errors = validate_snapshot({"player_class": "Warrior"})
        self.assertFalse(ok)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
