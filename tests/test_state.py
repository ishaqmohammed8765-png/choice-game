import unittest

from game.state import ensure_session_state, load_snapshot, reset_game_state, snapshot_state, start_game
from game.streamlit_compat import st


class StateTests(unittest.TestCase):
    def setUp(self):
        ensure_session_state()
        reset_game_state()

    def test_start_game_initializes_expected_keys(self):
        start_game("Rogue")
        self.assertEqual(st.session_state.player_class, "Rogue")
        self.assertEqual(st.session_state.current_node, "village_square")
        self.assertIn("Lockpicks", st.session_state.inventory)


    def test_reset_initializes_toggle_and_factions(self):
        self.assertIn("oakrest", st.session_state.factions)
        self.assertFalse(st.session_state.show_locked_choices)
        self.assertFalse(st.session_state.spoiler_debug_mode)

    def test_snapshot_roundtrip(self):
        start_game("Warrior")
        st.session_state.stats["gold"] += 3
        snap = snapshot_state()

        st.session_state.stats["gold"] = 0
        load_snapshot(snap)
        self.assertEqual(st.session_state.stats["gold"], snap["stats"]["gold"])


if __name__ == "__main__":
    unittest.main()
