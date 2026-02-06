import unittest

from game.ui import format_requirement_tooltip, should_force_injury_redirect
from game.ui_components.path_map import _escape_svg_text


class UiLogicTests(unittest.TestCase):
    def test_redirects_to_injured_for_non_failure_nodes_at_zero_hp(self):
        self.assertTrue(should_force_injury_redirect("forest_crossroad", 0))
        self.assertTrue(should_force_injury_redirect("forest_crossroad", -2))

    def test_does_not_redirect_inside_failure_nodes(self):
        self.assertFalse(should_force_injury_redirect("failure_injured", 0))
        self.assertFalse(should_force_injury_redirect("failure_traitor", -3))

    def test_does_not_redirect_at_death_node(self):
        self.assertFalse(should_force_injury_redirect("death", 0))

    def test_format_requirement_tooltip_includes_current_values(self):
        requirements = {
            "class": ["Rogue"],
            "min_hp": 5,
            "items": ["Key"],
            "flag_true": ["met_king"],
        }
        tooltip = format_requirement_tooltip(
            requirements,
            stats={"hp": 3, "gold": 0, "strength": 0, "dexterity": 0},
            inventory=[],
            flags={"met_king": False},
            player_class="Warrior",
        )
        self.assertIn("Class: Rogue (you: Warrior)", tooltip)
        self.assertIn("HP >= 5 (you: 3)", tooltip)
        self.assertIn("Needs item: Key (you: missing)", tooltip)
        self.assertIn("Flag met_king=True (you: False)", tooltip)

    def test_format_requirement_tooltip_handles_any_of(self):
        requirements = {
            "any_of": [
                {"min_gold": 5},
                {"items": ["Amulet"]},
            ]
        }
        tooltip = format_requirement_tooltip(
            requirements,
            stats={"hp": 5, "gold": 2, "strength": 1, "dexterity": 1},
            inventory=["Torch"],
            flags={},
            player_class="Rogue",
        )
        self.assertIn("Any of:", tooltip)
        self.assertIn("Gold >= 5 (you: 2)", tooltip)
        self.assertIn("Needs item: Amulet (you: missing)", tooltip)

    def test_escape_svg_text(self):
        escaped = _escape_svg_text('<warn ">&')
        self.assertEqual(escaped, "&lt;warn &quot;&gt;&amp;")


if __name__ == "__main__":
    unittest.main()
