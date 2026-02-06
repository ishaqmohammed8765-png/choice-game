from game.streamlit_compat import st

from game.logic import validate_story_nodes
from game.state import ensure_session_state, start_game
from game.ui import render_log, render_node, render_path_map, render_sidebar


def inject_game_theme() -> None:
    """Apply lightweight visual styling so the app feels closer to a fantasy game HUD."""
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top, #1f2a44 0%, #0f172a 50%, #020617 100%);
            color: #e2e8f0;
        }
        h1, h2, h3 {
            color: #f8fafc !important;
            letter-spacing: 0.02em;
        }
        div[data-testid="stMetricValue"] {
            color: #facc15;
        }
        div.stButton > button {
            border-radius: 10px;
            border: 1px solid #334155;
        }
        div[data-testid="stExpander"] {
            border-color: #334155 !important;
            background: rgba(15, 23, 42, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_game_header() -> None:
    """Display title and subtitle in a game-like top panel."""
    st.markdown(
        """
        <div style="padding: 0.8rem 1rem; border: 1px solid #334155; border-radius: 12px;
                    background: linear-gradient(90deg, rgba(30,41,59,.75), rgba(51,65,85,.45));
                    margin-bottom: 0.75rem;">
            <h2 style="margin:0;">⚔️ Oakrest: Deterministic Adventure</h2>
            <p style="margin:0.25rem 0 0 0; color:#cbd5e1;">No dice. No randomness. Every choice carries weight.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def main() -> None:
    st.set_page_config(page_title="Oakrest: Deterministic Adventure", page_icon="🛡️", layout="centered")
    inject_game_theme()
    ensure_session_state()
    for warning in validate_story_nodes():
        st.warning(f"Story validator: {warning}")

    render_game_header()

    if st.session_state.player_class is None:
        st.title("Oakrest: Choose Your Class")
        st.write(
            "Oakrest needs a hero. Your class changes available paths and solutions throughout the story."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Warrior", use_container_width=True, type="primary"):
                start_game("Warrior")
                st.rerun()
        with col2:
            if st.button("Rogue", use_container_width=True, type="primary"):
                start_game("Rogue")
                st.rerun()
        with col3:
            if st.button("Archer", use_container_width=True, type="primary"):
                start_game("Archer")
                st.rerun()

        st.markdown("**Warrior:** higher HP and Strength, excels at brute-force paths.")
        st.markdown("**Rogue:** higher Dexterity and stealth options, excels at subtle paths.")
        st.markdown("**Archer:** balanced HP with adaptable Strength and Dexterity, excels at flexible tactics.")
        return

    render_sidebar()

    st.markdown("### Adventure Console")
    active_panel = st.radio(
        "View",
        ["Story", "Path Map"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if active_panel == "Story":
        render_node()
        render_log()
    else:
        render_path_map()


if __name__ == "__main__":
    main()
