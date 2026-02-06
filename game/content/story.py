from typing import Any, Dict

from game.content.story_nodes_act1 import STORY_NODES_ACT1
from game.content.story_nodes_act2 import STORY_NODES_ACT2
from game.content.story_nodes_act3 import STORY_NODES_ACT3
from game.content.story_nodes_intro import STORY_NODES_INTRO
from game.content.story_utils import simplify_story_nodes

STORY_NODES: Dict[str, Dict[str, Any]] = {
    **STORY_NODES_INTRO,
    **STORY_NODES_ACT1,
    **STORY_NODES_ACT2,
    **STORY_NODES_ACT3,
}

_simplified = False


def init_story_nodes() -> None:
    """Run story simplification once. Safe to call multiple times."""
    global _simplified
    if _simplified:
        return
    simplify_story_nodes(STORY_NODES)
    _simplified = True
