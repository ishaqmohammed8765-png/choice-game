from game.streamlit_compat import st


def render_log(*, max_entries: int = 10) -> None:
    """Render a compact event log panel for recent narrative/system updates."""
    logs = st.session_state.get("event_log", [])
    if not logs:
        return

    with st.expander("Recent Events", expanded=False):
        for entry in logs[-max_entries:]:
            st.write(f"- {entry}")
