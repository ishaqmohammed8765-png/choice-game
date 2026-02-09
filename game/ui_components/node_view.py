from html import escape
from typing import Any, Dict, List

from game.streamlit_compat import st

from game.data import CHOICE_SIMPLIFICATION_REPORT, MAX_CHOICES_PER_NODE, STORY_NODES
from game.logic import (
    apply_node_auto_choices,
    check_requirements,
    execute_choice,
    format_outcome_summary,
    get_choice_warnings_with_effects,
    get_node_choice_evaluations,
    resolve_choice_outcome,
    transition_to,
    transition_to_failure,
)
from game.ui_components.epilogue import get_epilogue_aftermath_lines
from game.ui_components.log_view import render_log
from game.ui_components.sprites import item_sprite, stat_icon_svg


def should_force_injury_redirect(node_id: str, hp: int) -> bool:
    """Return whether the current state should auto-redirect into the injured setback."""
    return hp <= 0 and not node_id.startswith("failure_") and node_id != "death"


def _escape_html(text: Any) -> str:
    """Escape arbitrary text for safe insertion into HTML blocks."""
    return escape(str(text), quote=True).replace("\n", "<br/>")


def _render_pending_confirmation(node_id: str, available_choices: List[Dict[str, Any]]) -> None:
    pending = st.session_state.pending_choice_confirmation
    if not pending or pending.get("node") != node_id:
        return

    st.markdown(
        """
        <div style="
            padding: 0.8rem 1rem;
            border: 1px solid #b9451c80;
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(185,28,28,0.15), rgba(30,20,10,0.6));
            margin-bottom: 0.5rem;
        ">
            <p style="
                margin: 0 0 0.3rem 0;
                font-family: 'Cinzel', serif;
                color: #fca5a5;
                font-size: 0.9rem;
            ">Confirm risky choice</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.warning(f"Confirm choice: **{pending['label']}**")
        for warning in pending.get("warnings", []):
            st.write(f"- {warning}")
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


def _render_locked_choices(locked_choices: List[tuple[Dict[str, Any], str]]) -> None:
    if locked_choices:
        with st.expander("Locked paths", expanded=False):
            for choice, reason in locked_choices:
                label_text = _escape_html(choice.get("label", "Unknown choice"))
                reason_text = _escape_html(reason)
                st.markdown(
                    f'<div style="padding:4px 8px;margin-bottom:4px;border:1px solid #334155;'
                    f'border-radius:6px;background:rgba(15,15,30,0.4);">'
                    f'<span style="color:#64748b;font-family:\'Crimson Text\',serif;"><strong>{label_text}</strong></span>'
                    f' - <span style="color:#94a3b8;font-style:italic;font-size:0.85rem;">{reason_text}</span></div>',
                    unsafe_allow_html=True,
                )


def _render_outcome_summary() -> None:
    summary = st.session_state.last_outcome_summary
    if not summary:
        return
    stats_delta = summary.get("stats_delta", {})
    items_gained = summary.get("items_gained", [])
    items_lost = summary.get("items_lost", [])

    # Build a compact inline outcome ribbon (no flags shown to reduce clutter)
    parts: List[str] = []
    stat_map = {"hp": "HP", "gold": "Gold", "strength": "STR", "dexterity": "DEX"}
    for stat_key, label in stat_map.items():
        delta = stats_delta.get(stat_key, 0)
        if delta != 0:
            icon = stat_icon_svg(stat_key, size=13)
            color = "#22c55e" if delta > 0 else "#ef4444"
            sign = "+" if delta > 0 else ""
            parts.append(
                f'<span style="display:inline-flex;align-items:center;gap:2px;">'
                f'{icon}<span style="color:{color};font-weight:600;font-size:0.85rem;">{sign}{delta} {label}</span></span>'
            )

    if items_gained:
        for item_name in items_gained:
            sprite = item_sprite(item_name, size=16)
            parts.append(f'<span style="display:inline-flex;align-items:center;gap:2px;">{sprite}<span style="color:#22c55e;font-size:0.85rem;">+{item_name}</span></span>')

    if items_lost:
        for item_name in items_lost:
            sprite = item_sprite(item_name, size=16)
            parts.append(f'<span style="display:inline-flex;align-items:center;gap:2px;">{sprite}<span style="color:#ef4444;text-decoration:line-through;font-size:0.85rem;">{item_name}</span></span>')

    if not parts:
        st.session_state.last_outcome_summary = None
        return

    separator = '<span style="color:#334155;margin:0 6px;">|</span>'
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:6px 10px;'
        f'border-left:3px solid #c9a54e40;background:rgba(15,15,30,0.3);border-radius:0 6px 6px 0;'
        f'margin-bottom:0.5rem;font-family:\'Cinzel\',serif;">'
        f'{separator.join(parts)}</div>',
        unsafe_allow_html=True,
    )
    st.session_state.last_outcome_summary = None


def _render_auto_events() -> None:
    summaries = st.session_state.auto_event_summary
    if not summaries:
        return
    with st.container(border=True):
        st.caption("Auto events")
        for summary in summaries:
            label = summary.get("label") or "Auto event"
            st.write(f"- **{label}** - {format_outcome_summary(summary)}")
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


def _get_choice_cost_preview(effects: Dict[str, Any]) -> str:
    """Build a short cost/reward preview string for a choice."""
    parts: List[str] = []
    stat_labels = {"hp": "HP", "gold": "Gold", "strength": "STR", "dexterity": "DEX"}
    for stat_key, label in stat_labels.items():
        delta = effects.get(stat_key, 0)
        if delta != 0:
            sign = "+" if delta > 0 else ""
            color = "#6ee7b7" if delta > 0 else "#fca5a5"
            parts.append(f'<span style="color:{color};font-size:0.75rem;">{sign}{delta} {label}</span>')
    for item in effects.get("add_items", []):
        parts.append(f'<span style="color:#6ee7b7;font-size:0.75rem;">+{_escape_html(item)}</span>')
    for item in effects.get("remove_items", []):
        parts.append(f'<span style="color:#fca5a5;font-size:0.75rem;">-{_escape_html(item)}</span>')
    return " ".join(parts)


def _render_choice_card(
    node_id: str,
    index: int,
    choice: Dict[str, Any],
    *,
    resolved_effects: Dict[str, Any] | None = None,
    key_prefix: str = "choice",
) -> None:
    """Render a single choice as a styled card with preview info."""
    label = choice["label"]
    safe_label = _escape_html(label)
    effects = resolved_effects
    if effects is None:
        effects, _ = resolve_choice_outcome(choice)
    warnings = get_choice_warnings_with_effects(choice, effects)
    cost_preview = _get_choice_cost_preview(effects)

    warning_icon = ""
    if warnings:
        warning_icon = '<span style="color:#fbbf24;margin-right:4px;">&#9888;</span>'

    # Build the card HTML
    card_html = f"""
    <div style="
        padding: 8px 12px;
        border: 1px solid #2a201580;
        border-left: 3px solid #c9a54e50;
        border-radius: 4px 8px 8px 4px;
        background: linear-gradient(135deg, rgba(20,15,10,0.5), rgba(10,10,20,0.4));
        margin-bottom: 2px;
    ">
        <div style="
            font-family: 'Crimson Text', Georgia, serif;
            color: #e2d5c1;
            font-size: 0.95rem;
            line-height: 1.3;
        ">{warning_icon}{safe_label}</div>
        {f'<div style="margin-top:3px;">{cost_preview}</div>' if cost_preview else ''}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    if st.button("Choose", key=f"{key_prefix}_{node_id}_{index}", use_container_width=True):
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


def _should_group_by_destination(node_id: str, indexed_choices: List[tuple[int, Dict[str, Any]]], *, overflow: bool) -> bool:
    if overflow:
        return True
    if len(indexed_choices) < 5:
        return False
    self_loop_count = sum(1 for _, entry in indexed_choices if entry["choice"].get("next") == node_id)
    return self_loop_count >= 3


def _render_grouped_choices(
    node_id: str,
    indexed_choices: List[tuple[int, Dict[str, Any]]],
    *,
    overflow: bool,
) -> None:
    has_explicit_groups = any(entry["choice"].get("group") for _, entry in indexed_choices)
    group_by_destination = _should_group_by_destination(node_id, indexed_choices, overflow=overflow)

    if not group_by_destination and not has_explicit_groups:
        # Render choices as styled cards in a clean list
        for index, entry in indexed_choices:
            _render_choice_card(
                node_id,
                index,
                entry["choice"],
                resolved_effects=entry.get("resolved_effects"),
            )
        return

    groups = _group_choices(
        indexed_choices,
        group_by_destination=group_by_destination,
        current_node_id=node_id,
    )
    if not overflow:
        for group in groups:
            if len(group["choices"]) == 1 and not group["label"]:
                index, entry = group["choices"][0]
                _render_choice_card(
                    node_id,
                    index,
                    entry["choice"],
                    resolved_effects=entry.get("resolved_effects"),
                )
            else:
                label = group["label"] or "Grouped options"
                with st.expander(label, expanded=False):
                    for index, entry in group["choices"]:
                        _render_choice_card(
                            node_id,
                            index,
                            entry["choice"],
                            resolved_effects=entry.get("resolved_effects"),
                            key_prefix=f"group_{group['key']}",
                        )
        return

    more_groups: List[Dict[str, Any]] = []
    primary_groups: List[Dict[str, Any]] = []
    for group in groups:
        if all(_is_low_impact(entry["choice"]) for _, entry in group["choices"]):
            more_groups.append(group)
        else:
            primary_groups.append(group)

    if len(primary_groups) > MAX_CHOICES_PER_NODE - 1:
        overflow_groups = primary_groups[MAX_CHOICES_PER_NODE - 1 :]
        primary_groups = primary_groups[: MAX_CHOICES_PER_NODE - 1]
        more_groups = overflow_groups + more_groups

    for group in primary_groups:
        if len(group["choices"]) == 1 and not group["label"]:
            index, entry = group["choices"][0]
            _render_choice_card(
                node_id,
                index,
                entry["choice"],
                resolved_effects=entry.get("resolved_effects"),
            )
        else:
            label = group["label"] or "Grouped options"
            with st.expander(label, expanded=False):
                for index, entry in group["choices"]:
                    _render_choice_card(
                        node_id,
                        index,
                        entry["choice"],
                        resolved_effects=entry.get("resolved_effects"),
                        key_prefix=f"group_{group['key']}",
                    )

    if more_groups:
        with st.expander("More options", expanded=False):
            for group in more_groups:
                label = group["label"] or "Additional options"
                st.caption(label)
                for index, entry in group["choices"]:
                    _render_choice_card(
                        node_id,
                        index,
                        entry["choice"],
                        resolved_effects=entry.get("resolved_effects"),
                        key_prefix=f"more_{group['key']}",
                    )


def _group_choices(
    indexed_choices: List[tuple[int, Dict[str, Any]]],
    *,
    group_by_destination: bool,
    current_node_id: str | None = None,
) -> List[Dict[str, Any]]:
    groups: List[Dict[str, Any]] = []
    seen: Dict[str, Dict[str, Any]] = {}
    for index, entry in indexed_choices:
        choice = entry["choice"]
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
                if destination == current_node_id:
                    display_label = "Preparation options"
                else:
                    next_title = STORY_NODES.get(destination, {}).get("title", destination or "Unknown")
                    display_label = f"More options \u2192 {next_title}"
            groups.append(
                {
                    "key": key,
                    "label": display_label,
                    "destination": destination,
                    "choices": [],
                }
            )
            seen[key] = groups[-1]
        seen[key]["choices"].append((index, entry))
    return groups


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

    # Enhanced node title with decorative styling
    st.markdown(
        f"""
        <div style="
            padding: 0.5rem 0;
            margin-bottom: 0.3rem;
            border-bottom: 1px solid #2a201540;
        ">
            <h3 style="
                font-family: 'Cinzel', serif;
                color: #e8d5b0 !important;
                margin: 0;
                font-size: 1.3rem;
                letter-spacing: 0.04em;
                text-shadow: 0 1px 4px rgba(0,0,0,0.4);
            ">{_escape_html(node['title'])}</h3>
            <span style="
                color: #4a3728;
                font-family: 'Cinzel', serif;
                font-size: 0.65rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            ">{_escape_html(node_id)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_outcome_summary()
    _render_auto_events()
    render_log()

    # Build narrative text with dialogue woven in
    dialogue = node.get("dialogue", [])
    narrative_text = _escape_html(node["text"])
    ending_aftermath = []
    if node_id.startswith("ending_"):
        ending_aftermath = get_epilogue_aftermath_lines(max_lines=None)

    # Build the combined narrative + dialogue HTML
    narrative_html = f"""
    <div style="
        padding: 0.8rem 1rem;
        border: 1px solid #2a2015;
        border-radius: 8px;
        background: linear-gradient(135deg, rgba(20,15,10,0.7), rgba(10,10,20,0.5));
        margin-bottom: 0.6rem;
        line-height: 1.7;
        font-family: 'Crimson Text', Georgia, serif;
        font-size: 1.05rem;
        color: #d4d4dc;
    ">
        <p style="margin:0 0 0.6rem 0;">{narrative_text}</p>
    """

    if dialogue:
        for line in dialogue:
            speaker = _escape_html(line.get("speaker", "Unknown"))
            quote = _escape_html(line.get("line", ""))
            narrative_html += (
                f'<div style="margin:0.5rem 0;padding:4px 0 4px 12px;border-left:2px solid #c9a54e40;">'
                f'<span style="color:#c9a54e;font-family:\'Cinzel\',serif;font-size:0.85rem;font-weight:600;">{speaker}:</span> '
                f'<span style="color:#d4d4dc;font-style:italic;">&ldquo;{quote}&rdquo;</span>'
                f'</div>'
            )

    if ending_aftermath:
        narrative_html += (
            '<div style="margin-top:0.7rem;padding-top:0.5rem;border-top:1px solid #c9a54e30;">'
            '<p style="margin:0 0 0.35rem 0;color:#c9a54e;font-family:\'Cinzel\',serif;font-size:0.9rem;">Aftermath</p>'
        )
        for detail in ending_aftermath:
            safe_detail = _escape_html(detail)
            narrative_html += (
                f'<div style="margin:0.3rem 0;padding-left:12px;border-left:2px solid #c9a54e25;">'
                f'<span style="color:#d4d4dc;">{safe_detail}</span>'
                f'</div>'
            )
        narrative_html += "</div>"

    narrative_html += "</div>"
    st.markdown(narrative_html, unsafe_allow_html=True)

    if should_force_injury_redirect(node_id, st.session_state.stats["hp"]):
        transition_to_failure("injured")
        st.rerun()
        return

    choices = node.get("choices", [])
    evaluations = get_node_choice_evaluations(node_id, node)
    available_entries = [entry for entry in evaluations if entry["is_available"]]
    available_choices = [entry["choice"] for entry in available_entries]
    locked_choices = [
        (entry["choice"], entry["locked_reason"])
        for entry in evaluations
        if not entry["is_available"] and entry["locked_reason"]
    ]
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
        st.markdown(
            """
            <div style="
                padding: 0.8rem 1rem;
                border: 1px solid #c9a54e40;
                border-radius: 8px;
                background: linear-gradient(135deg, rgba(30,20,10,0.6), rgba(20,15,8,0.4));
                text-align: center;
                margin: 1rem 0;
            ">
                <p style="
                    margin: 0;
                    color: #c9a54e;
                    font-family: 'Cinzel', serif;
                    font-size: 1rem;
                    letter-spacing: 0.04em;
                ">The story has reached an ending.</p>
                <p style="
                    margin: 0.3rem 0 0 0;
                    color: #8b7355;
                    font-family: 'Crimson Text', Georgia, serif;
                    font-size: 0.9rem;
                    font-style: italic;
                ">Restart to explore another path.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Choice section with styled header
    st.markdown(
        """
        <div style="
            margin: 0.8rem 0 0.4rem 0;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid #c9a54e20;
        ">
            <h4 style="
                font-family: 'Cinzel', serif;
                color: #c9a54e !important;
                margin: 0;
                font-size: 1rem;
                letter-spacing: 0.05em;
            ">Choose your path</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_pending_confirmation(node_id, available_choices)
    indexed_choices = list(enumerate(available_entries))
    _render_grouped_choices(node_id, indexed_choices, overflow=overflow)

    if st.session_state.show_locked_choices:
        _render_locked_choices(locked_choices)

    if not available_choices:
        st.warning("No valid choices remain based on your current stats, items, and flags.")
        if st.button("Take a setback and adapt", type="primary"):
            transition_to_failure("resource_loss")
            st.rerun()

