from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import CHOICE_SIMPLIFICATION_REPORT, MAX_CHOICES_PER_NODE, STORY_NODES
from game.logic import (
    apply_node_auto_choices,
    check_requirements,
    execute_choice,
    format_outcome_summary,
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


def _render_outcome_summary() -> None:
    summary = st.session_state.last_outcome_summary
    if not summary:
        return
    stats_delta = summary.get("stats_delta", {})
    items_gained = summary.get("items_gained", [])
    items_lost = summary.get("items_lost", [])
    flags_set = summary.get("flags_set", [])

    with st.container(border=True):
        st.caption("Outcome Summary")
        stat_definitions = [
            ("HP", "hp"),
            ("Gold", "gold"),
            ("STR", "strength"),
            ("DEX", "dexterity"),
        ]
        changed_stats = [(label, key) for label, key in stat_definitions if key in stats_delta]
        if changed_stats:
            columns = st.columns(len(changed_stats))
            for col, (label, key) in zip(columns, changed_stats):
                value = max(0, st.session_state.stats[key]) if key == "hp" else st.session_state.stats[key]
                col.metric(label, value, _format_delta(stats_delta.get(key, 0)))
        else:
            st.caption("No stat changes.")

        if items_gained or items_lost or flags_set:
            if items_gained:
                st.write(f"**Items gained:** {', '.join(items_gained)}")
            if items_lost:
                st.write(f"**Items lost:** {', '.join(items_lost)}")
            if flags_set:
                flag_text = ", ".join(f"{name} → {value}" for name, value in flags_set)
                st.write(f"**Flags set:** {flag_text}")
        else:
            st.caption("No inventory or flag changes.")
    st.session_state.last_outcome_summary = None


def _render_auto_events() -> None:
    summaries = st.session_state.auto_event_summary
    if not summaries:
        return
    with st.container(border=True):
        st.caption("Auto events")
        for summary in summaries:
            label = summary.get("label") or "Auto event"
            st.write(f"- **{label}** — {format_outcome_summary(summary)}")
    st.session_state.auto_event_summary = []


def _render_pending_auto_death() -> bool:
    if not st.session_state.pending_auto_death:
        return False
    st.error("An event occurs...")
    _render_auto_events()
    if st.button("Continue", type="primary", use_container_width=True):
        st.session_state.pending_auto_death = False
        transition_to("death")
        st.rerun()
    return True


def _format_delta(value: int) -> str:
    if value == 0:
        return "0"
    sign = "+" if value > 0 else ""
    return f"{sign}{value}"


def _is_low_impact(choice: Dict[str, Any]) -> bool:
    effects = choice.get("effects", {})
    return set(effects.keys()) <= {"log"} and not choice.get("conditional_effects")


def _group_choices(
    indexed_choices: List[tuple[int, Dict[str, Any]]],
    *,
    group_by_destination: bool,
) -> List[Dict[str, Any]]:
    groups: List[Dict[str, Any]] = []
    seen: Dict[str, Dict[str, Any]] = {}
    for index, choice in indexed_choices:
        group_label = choice.get("group")
        destination = choice.get("next")
        if group_label:
            key = f"group::{group_label}"
        elif group_by_destination:
            key = f"dest::{destination}"
        else:
            key = f"choice::{index}"

        if key not in seen:
            display_label = group_label
            if not display_label and group_by_destination:
                next_title = STORY_NODES.get(destination, {}).get("title", destination or "Unknown")
                display_label = f"More options → {next_title}"
            groups.append(
                {
                    "key": key,
                    "label": display_label,
                    "destination": destination,
                    "choices": [],
                }
            )
            seen[key] = groups[-1]
        seen[key]["choices"].append((index, choice))
    return groups


def _render_choice_button(node_id: str, index: int, choice: Dict[str, Any], *, key_prefix: str = "choice") -> None:
    label = choice["label"]
    warnings = get_choice_warnings(choice)
    display_label = f"⚠️ {label}" if warnings else label
    if st.button(display_label, key=f"{key_prefix}_{node_id}_{index}", use_container_width=True):
        if warnings:
            st.session_state.pending_choice_confirmation = {
                "node": node_id,
                "choice_index": index,
                "label": label,
                "warnings": warnings,
            }
        else:
            execute_choice(node_id, label, choice)
        st.rerun()


def _render_grouped_choices(
    node_id: str,
    indexed_choices: List[tuple[int, Dict[str, Any]]],
    *,
    overflow: bool,
) -> None:
    has_explicit_groups = any(choice.get("group") for _, choice in indexed_choices)
    if not overflow and not has_explicit_groups:
        for index, choice in indexed_choices:
            _render_choice_button(node_id, index, choice)
        return

    groups = _group_choices(indexed_choices, group_by_destination=overflow)
    if not overflow:
        for group in groups:
            if len(group["choices"]) == 1 and not group["label"]:
                index, choice = group["choices"][0]
                _render_choice_button(node_id, index, choice)
            else:
                label = group["label"] or "Grouped options"
                with st.expander(label, expanded=False):
                    for index, choice in group["choices"]:
                        _render_choice_button(node_id, index, choice, key_prefix=f"group_{group['key']}")
        return

    more_groups: List[Dict[str, Any]] = []
    primary_groups: List[Dict[str, Any]] = []
    for group in groups:
        if all(_is_low_impact(choice) for _, choice in group["choices"]):
            more_groups.append(group)
        else:
            primary_groups.append(group)

    if len(primary_groups) > MAX_CHOICES_PER_NODE - 1:
        overflow_groups = primary_groups[MAX_CHOICES_PER_NODE - 1 :]
        primary_groups = primary_groups[: MAX_CHOICES_PER_NODE - 1]
        more_groups = overflow_groups + more_groups

    for group in primary_groups:
        if len(group["choices"]) == 1 and not group["label"]:
            index, choice = group["choices"][0]
            _render_choice_button(node_id, index, choice)
        else:
            label = group["label"] or "Grouped options"
            with st.expander(label, expanded=False):
                for index, choice in group["choices"]:
                    _render_choice_button(node_id, index, choice, key_prefix=f"group_{group['key']}")

    if more_groups:
        with st.expander("More options", expanded=False):
            for group in more_groups:
                label = group["label"] or "Additional options"
                st.caption(label)
                for index, choice in group["choices"]:
                    _render_choice_button(node_id, index, choice, key_prefix=f"more_{group['key']}")


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

    if _render_pending_auto_death():
        return

    apply_node_auto_choices(node_id, node)
    if _render_pending_auto_death():
        return

    st.markdown(f"### 🧭 {node['title']}")
    _render_outcome_summary()
    _render_auto_events()
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
    overflow = len(available_choices) > MAX_CHOICES_PER_NODE
    if overflow:
        st.warning("This scene has many options; some are grouped.")
        with st.expander("Developer diagnostics", expanded=False):
            st.write(
                f"Node '{node_id}' has {len(available_choices)} available choices (cap: {MAX_CHOICES_PER_NODE})."
            )
            st.write("Consider grouping by destination or assigning explicit choice groups in content.")
            if CHOICE_SIMPLIFICATION_REPORT:
                st.divider()
                st.caption("Choice simplification report")
                for entry in CHOICE_SIMPLIFICATION_REPORT:
                    st.write(f"- {entry}")

    if not choices:
        st.success("The story has reached an ending. Restart to explore another path.")
        if node_id.startswith("ending_"):
            show_full_epilogue = st.toggle(
                "Show full epilogue",
                key="show_full_epilogue",
                help="Expand the epilogue with extra reminders of your earlier choices.",
            )
            aftermath = get_epilogue_aftermath_lines(max_lines=None if show_full_epilogue else 9)
            if aftermath:
                with st.container(border=True):
                    st.subheader("Epilogue Aftermath")
                    for detail in aftermath:
                        st.write(f"- {detail}")
        return

    st.subheader("🎮 What do you do?")
    st.toggle("Show locked choices", key="show_locked_choices", help="Toggle off to hide paths you cannot currently take.")

    _render_pending_confirmation(node_id, available_choices)
    indexed_choices = list(enumerate(available_choices))
    _render_grouped_choices(node_id, indexed_choices, overflow=overflow)

    if st.session_state.show_locked_choices:
        _render_locked_choices(choices)

    if not available_choices:
        st.warning("No valid choices remain based on your current stats, items, and flags.")
        if st.button("Take a setback and adapt", type="primary"):
            transition_to_failure("resource_loss")
            st.rerun()
