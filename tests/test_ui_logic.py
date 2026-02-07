import math
import unittest

from game.ui import format_requirement_tooltip, should_force_injury_redirect
from game.ui_components.path_map import (
    _build_legend,
    _build_line,
    _build_node_group,
    _escape_svg_text,
    _node_type,
    _render_svg_text,
    _wrap_svg_label,
)


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


class NodeTypeTests(unittest.TestCase):
    def test_death_node(self):
        self.assertEqual(_node_type("death"), "death")

    def test_ending_nodes(self):
        self.assertEqual(_node_type("ending_good"), "ending")
        self.assertEqual(_node_type("ending_bad"), "ending")

    def test_failure_nodes(self):
        self.assertEqual(_node_type("failure_injured"), "failure")
        self.assertEqual(_node_type("failure_captured"), "failure")

    def test_normal_nodes(self):
        self.assertEqual(_node_type("village_square"), "normal")
        self.assertEqual(_node_type("camp_shop"), "normal")


class WrapSvgLabelTests(unittest.TestCase):
    def test_short_text_stays_single_line(self):
        self.assertEqual(_wrap_svg_label("Go north"), ["Go north"])

    def test_long_text_wraps(self):
        lines = _wrap_svg_label("Return to the forest crossroads")
        self.assertTrue(len(lines) > 1)
        for line in lines:
            self.assertLessEqual(len(line), 20)  # reasonable wrap

    def test_empty_text(self):
        self.assertEqual(_wrap_svg_label(""), [""])

    def test_single_word(self):
        self.assertEqual(_wrap_svg_label("Attack"), ["Attack"])

    def test_custom_max_chars(self):
        lines = _wrap_svg_label("Hello World Foo Bar", max_chars=8)
        self.assertTrue(all(len(line) <= 10 for line in lines))


class RenderSvgTextTests(unittest.TestCase):
    def test_empty_lines_returns_empty(self):
        self.assertEqual(_render_svg_text([], x=100, y=100, class_name="test"), "")

    def test_single_line_contains_tspan(self):
        result = _render_svg_text(["Hello"], x=50, y=60, class_name="label")
        self.assertIn("<tspan", result)
        self.assertIn("Hello", result)
        self.assertIn('class="label"', result)

    def test_multi_line_has_multiple_tspans(self):
        result = _render_svg_text(["Line 1", "Line 2"], x=50, y=60, class_name="t")
        self.assertEqual(result.count("<tspan"), 2)

    def test_escapes_special_characters(self):
        result = _render_svg_text(["<test>&"], x=50, y=60, class_name="t")
        self.assertIn("&lt;test&gt;&amp;", result)


class BuildLineTests(unittest.TestCase):
    def test_zero_length_returns_empty(self):
        self.assertEqual(
            _build_line(10, 10, 10, 10, edge_visited=False, is_locked=False), ""
        )

    def test_normal_line_has_arrow_marker(self):
        result = _build_line(0, 0, 100, 0, edge_visited=False, is_locked=False)
        self.assertIn('marker-end="url(#arrow)"', result)
        self.assertIn("path-line", result)
        self.assertNotIn("locked", result)
        self.assertNotIn("visited", result)

    def test_visited_line_uses_visited_marker(self):
        result = _build_line(0, 0, 100, 0, edge_visited=True, is_locked=False)
        self.assertIn('url(#arrow-visited)', result)
        self.assertIn("visited", result)

    def test_locked_line_uses_locked_marker(self):
        result = _build_line(0, 0, 100, 0, edge_visited=False, is_locked=True)
        self.assertIn('url(#arrow-locked)', result)
        self.assertIn("locked", result)

    def test_line_shortened_by_node_radius(self):
        result = _build_line(0, 0, 100, 0, edge_visited=False, is_locked=False, node_radius=20)
        # x2 should be 100 - 20 = 80
        self.assertIn('x2="80.0"', result)

    def test_secondary_line_has_class(self):
        result = _build_line(0, 0, 100, 0, edge_visited=False, is_locked=False, is_secondary=True)
        self.assertIn("secondary", result)


class BuildNodeGroupTests(unittest.TestCase):
    def test_normal_unlocked_node(self):
        result = _build_node_group(
            100, 100,
            label_lines=["Go here"],
            tooltip_text="Destination: Village",
            is_locked=False,
            is_visited=False,
        )
        self.assertIn("choice-node", result)
        self.assertIn("<circle", result)
        self.assertIn("Go here", result)
        self.assertIn("Destination: Village", result)
        self.assertNotIn("locked", result)

    def test_locked_node_has_locked_class(self):
        result = _build_node_group(
            100, 100,
            label_lines=["Locked"],
            tooltip_text="Locked: needs key",
            is_locked=True,
            is_visited=False,
        )
        self.assertIn("locked", result)

    def test_death_node_has_icon(self):
        result = _build_node_group(
            100, 100,
            label_lines=["Die"],
            tooltip_text="",
            is_locked=False,
            is_visited=False,
            node_type="death",
        )
        self.assertIn("node-death", result)
        self.assertIn("&#9760;", result)  # skull icon

    def test_ending_node_has_icon(self):
        result = _build_node_group(
            100, 100,
            label_lines=["Win"],
            tooltip_text="",
            is_locked=False,
            is_visited=False,
            node_type="ending",
        )
        self.assertIn("node-ending", result)
        self.assertIn("&#9733;", result)  # star icon

    def test_failure_node_has_icon(self):
        result = _build_node_group(
            100, 100,
            label_lines=["Fail"],
            tooltip_text="",
            is_locked=False,
            is_visited=False,
            node_type="failure",
        )
        self.assertIn("node-failure", result)
        self.assertIn("&#9888;", result)  # warning icon

    def test_visited_normal_node_uses_blue_stroke(self):
        result = _build_node_group(
            100, 100,
            label_lines=["Visited"],
            tooltip_text="",
            is_locked=False,
            is_visited=True,
            node_type="normal",
        )
        self.assertIn("#38bdf8", result)  # blue stroke
        self.assertIn("visited", result)

    def test_empty_tooltip_omits_title(self):
        result = _build_node_group(
            100, 100,
            label_lines=["Test"],
            tooltip_text="",
            is_locked=False,
            is_visited=False,
        )
        self.assertNotIn("<title>", result)


class BuildLegendTests(unittest.TestCase):
    def test_legend_contains_labels(self):
        result = _build_legend(10, 400)
        self.assertIn("Available", result)
        self.assertIn("Visited", result)
        self.assertIn("Locked", result)
        self.assertIn("Ending", result)
        self.assertIn("Death", result)
        self.assertIn("Setback", result)

    def test_legend_has_line_elements(self):
        result = _build_legend(10, 400)
        self.assertIn("<line", result)
        self.assertIn("stroke-dasharray", result)  # for locked line


if __name__ == "__main__":
    unittest.main()
