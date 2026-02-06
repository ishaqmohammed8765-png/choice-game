import streamlit as st

from game.logic import validate_story_nodes
from game.state import ensure_session_state, start_game
from game.ui import render_choice_outcomes_tab, render_log, render_node, render_sidebar

def main() -> None:
    st.set_page_config(page_title="Oakrest: Deterministic Adventure", page_icon="🛡️", layout="centered")
    ensure_session_state()
    for warning in validate_story_nodes():
        st.warning(f"Story validator: {warning}")

    st.caption("A deterministic D&D-style choice adventure. No dice, only decisions.")

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

    tab_story, tab_choices = st.tabs(["Story", "Choices & Outcomes"])
    with tab_story:
        render_node()
        render_log()
    with tab_choices:
        render_choice_outcomes_tab()


if __name__ == "__main__":
    main()
