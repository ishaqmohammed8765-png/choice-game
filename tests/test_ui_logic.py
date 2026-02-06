import unittest

from game.ui import should_force_injury_redirect


class UiLogicTests(unittest.TestCase):
    def test_redirects_to_injured_for_non_failure_nodes_at_zero_hp(self):
        self.assertTrue(should_force_injury_redirect("forest_crossroad", 0))
        self.assertTrue(should_force_injury_redirect("forest_crossroad", -2))

    def test_does_not_redirect_inside_failure_nodes(self):
        self.assertFalse(should_force_injury_redirect("failure_injured", 0))
        self.assertFalse(should_force_injury_redirect("failure_traitor", -3))

    def test_does_not_redirect_at_death_node(self):
        self.assertFalse(should_force_injury_redirect("death", 0))


if __name__ == "__main__":
    unittest.main()
