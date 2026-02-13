from html import escape

from game.streamlit_compat import st


def render_log(*, max_entries: int = 10) -> None:
    """Render a compact event log panel for recent narrative/system updates."""
    logs = st.session_state.get("event_log", [])
    if not logs:
        return

    with st.expander("Recent Events", expanded=False):
        entries_html = []
        for entry in logs[-max_entries:]:
            safe_entry = escape(str(entry), quote=True)
            entries_html.append(
                f'<div style="'
                f'padding:4px 8px 4px 12px;'
                f'margin-bottom:3px;'
                f'border-left:2px solid rgba(42, 63, 102, 0.4);'
                f'border-radius:0 4px 4px 0;'
                f'font-family:\'Crimson Text\',Georgia,serif;'
                f'font-size:0.88rem;'
                f'color:#8b9ab5;'
                f'background:rgba(12, 18, 32, 0.3);'
                f'">{safe_entry}</div>'
            )
        st.markdown("\n".join(entries_html), unsafe_allow_html=True)
