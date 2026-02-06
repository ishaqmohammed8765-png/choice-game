from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import CHOICE_SIMPLIFICATION_REPORT, MAX_CHOICES_PER_NODE, STORY_NODES
from game.logic import (
    apply_node_auto_choices,
    check_requirements,
    execute_choice,
    get_available_choices,
    get_choice_warnings,
    transition_to,
    transition_to_failure,
)
from game.ui_components.epilogue import get_epilogue_aftermath_lines


def should_force_injury_redirect(node_id: str, hp: int) -> bool:
    """Return whether the current state should auto-redirect into the injured setback."""
    return hp <= 0 and not node_id.startswith("failure_") and node_id != "death"


def _render_pending_confirmation(node_id: str, available_choices: List[Dict[str, Any]]) -> None:
    pending = st.session_state.pending_choice_confirmation
    if not pending or pending.get("node") != node_id:
        return

    with st.container(border=True):
        st.warning(f"Confirm choice: **{pending['label']}**")
        for warning in pending.get("warnings", []):
            st.write(f"- ⚠️ {warning}")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("Confirm risky choice", type="primary", key=f"confirm_{node_id}", use_container_width=True):
                choice_index = pending["choice_index"]
                if 0 <= choice_index < len(available_choices):
                    selected = available_choices[choice_index]
                    execute_choice(node_id, selected["label"], selected)
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key=f"cancel_{node_id}", use_container_width=True):
                st.session_state.pending_choice_confirmation = None
                st.rerun()


def _render_locked_choices(choices: List[Dict[str, Any]]) -> None:
    locked_choices: List[tuple[Dict[str, Any], str]] = []
    for choice in choices:
        ok, reason = check_requirements(choice.get("requirements"))
        if not ok:
            locked_choices.append((choice, reason))

    if locked_choices:
        with st.expander("Locked paths", expanded=False):
            for choice, reason in locked_choices:
                st.write(f"- **{choice['label']}** — _{reason}_")


def render_node() -> None:
    """Render current node, narrative, choices, and edge-case handling."""
    node_id = st.session_state.current_node
    if node_id not in STORY_NODES:
        st.error(f"Missing node '{node_id}'.")
        transition_to("death")
        st.rerun()
        return

    node = STORY_NODES[node_id]

    node_ok, node_reason = check_requirements(node.get("requirements"))
    if not node_ok:
        st.error(f"You cannot access this path: {node_reason}")
        transition_to_failure("traitor")
        st.rerun()
        return

    if apply_node_auto_choices(node_id, node):
        st.rerun()
        return

    st.markdown(f"### 🧭 {node['title']}")
    with st.container(border=True):
        st.write(node["text"])

    dialogue = node.get("dialogue", [])
    if dialogue:
        with st.container(border=True):
            st.caption("Dialogue")
            for line in dialogue:
                speaker = line.get("speaker", "Unknown")
                quote = line.get("line", "")
                st.markdown(f"**{speaker}:** _\"{quote}\"_")

    if should_force_injury_redirect(node_id, st.session_state.stats["hp"]):
        transition_to_failure("injured")
        st.rerun()
        return

    choices = node.get("choices", [])
    available_choices = get_available_choices(node)
    if len(available_choices) > MAX_CHOICES_PER_NODE:
        st.warning(
            f"Choice overflow: {node_id} shows {len(available_choices)} options (max {MAX_CHOICES_PER_NODE}). Displaying first {MAX_CHOICES_PER_NODE}."
        )
        if CHOICE_SIMPLIFICATION_REPORT:
            with st.expander("Choice simplification report", expanded=False):
                for entry in CHOICE_SIMPLIFICATION_REPORT:
                    st.write(f"- {entry}")
        available_choices = available_choices[:MAX_CHOICES_PER_NODE]

    if not choices:
        st.success("The story has reached an ending. Restart to explore another path.")
        if node_id.startswith("ending_"):
            aftermath = get_epilogue_aftermath_lines()
            if aftermath:
                with st.container(border=True):
                    st.subheader("Epilogue Aftermath")
                    for detail in aftermath:
                        st.write(f"- {detail}")
        return

    st.subheader("🎮 What do you do?")
    st.toggle("Show locked choices", key="show_locked_choices", help="Toggle off to hide paths you cannot currently take.")

    _render_pending_confirmation(node_id, available_choices)

    for idx, choice in enumerate(available_choices):
        label = choice["label"]
        warnings = get_choice_warnings(choice)
        display_label = f"⚠️ {label}" if warnings else label
        if st.button(display_label, key=f"choice_{node_id}_{idx}", use_container_width=True):
            if warnings:
                st.session_state.pending_choice_confirmation = {
                    "node": node_id,
                    "choice_index": idx,
                    "label": label,
                    "warnings": warnings,
                }
            else:
                execute_choice(node_id, label, choice)
            st.rerun()

    if st.session_state.show_locked_choices:
        _render_locked_choices(choices)

    if not available_choices:
        st.warning("No valid choices remain based on your current stats, items, and flags.")
        if st.button("Take a setback and adapt", type="primary"):
            transition_to_failure("resource_loss")
            st.rerun()
