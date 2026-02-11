from html import escape

from game.streamlit_compat import st

from game.data import init_story_nodes
from game.logic import validate_story_nodes
from game.state import ensure_session_state, normalize_meta_state, start_game
from game.ui import render_node, render_side_panel
from game.ui_components.sprites import class_icon_svg


CLASS_INFO = {
    "Warrior": {
        "desc": (
            "A stalwart defender with unmatched fortitude. Higher HP and Strength let you "
            "force through obstacles and endure punishment others cannot."
        ),
        "stats": "HP 14 | Gold 8 | STR 4 | DEX 2",
        "color": "#b91c1c",
        "accent": "#fca5a5",
    },
    "Rogue": {
        "desc": (
            "A cunning shadow who thrives on guile. Higher Dexterity and starting Lockpicks "
            "open paths closed to brute strength."
        ),
        "stats": "HP 10 | Gold 10 | STR 2 | DEX 4",
        "color": "#6d28d9",
        "accent": "#c4b5fd",
    },
    "Archer": {
        "desc": (
            "A keen-eyed tactician with balanced capabilities. Adaptable Strength and "
            "Dexterity let you flex between combat styles as the story demands."
        ),
        "stats": "HP 12 | Gold 9 | STR 3 | DEX 3",
        "color": "#047857",
        "accent": "#6ee7b7",
    },
}


def inject_game_theme() -> None:
    """Apply lightweight visual styling so the app feels closer to a fantasy game HUD."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

        :root {
            --hud-bg: #0b1220;
            --hud-panel: #111a2e;
            --hud-border: #2b3449;
            --hud-text: #dbe7ff;
            --hud-muted: #8ea0bf;
            --hud-accent: #facc15;
            --hud-danger: #ef4444;
        }

        .stApp {
            background:
                radial-gradient(900px 500px at 0% 0%, rgba(26, 52, 99, 0.38), transparent 60%),
                radial-gradient(700px 420px at 100% 100%, rgba(128, 69, 18, 0.22), transparent 62%),
                linear-gradient(180deg, #05070f 0%, #090f1d 50%, #0b111f 100%);
            color: var(--hud-text);
            font-family: 'Crimson Text', Georgia, serif;
        }

        h1, h2, h3, h4 {
            font-family: 'Cinzel', 'Times New Roman', serif !important;
            color: #e8d5b0 !important;
            letter-spacing: 0.04em;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }
        h1 { color: #facc15 !important; }

        div[data-testid="stMetricValue"] {
            color: #facc15 !important;
            font-family: 'Cinzel', serif !important;
            font-weight: 700;
            text-shadow: 0 0 8px rgba(250, 204, 21, 0.3);
        }
        div[data-testid="stMetricLabel"] {
            font-family: 'Cinzel', serif !important;
            color: #a8a29e !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.75rem !important;
        }

        div.stButton > button {
            border-radius: 6px !important;
            border: 1px solid var(--hud-border) !important;
            background: linear-gradient(180deg, #1a2740 0%, #10192d 100%) !important;
            color: #d6e4ff !important;
            font-family: 'Crimson Text', Georgia, serif !important;
            font-size: 1.05rem !important;
            padding: 0.6rem 1rem !important;
            transition: all 0.25s ease !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
        }
        div.stButton > button:hover {
            background: linear-gradient(180deg, #223656 0%, #15233c 100%) !important;
            border-color: #93c5fd !important;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.2), inset 0 1px 0 rgba(255,255,255,0.05) !important;
            color: #eff6ff !important;
            transform: translateY(-1px);
        }
        div.stButton > button:active {
            transform: translateY(0px) !important;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(180deg, #7c2d12 0%, #4a1c0d 100%) !important;
            border-color: #fb923c !important;
            color: #fef3c7 !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(180deg, #9a3412 0%, #5c2511 100%) !important;
            border-color: #fdba74 !important;
            box-shadow: 0 0 16px rgba(249, 115, 22, 0.25) !important;
        }

        div[data-testid="stExpander"] {
            border-color: var(--hud-border) !important;
            background: rgba(11, 18, 32, 0.72) !important;
            border-radius: 8px !important;
        }
        div[data-testid="stExpander"] summary {
            font-family: 'Cinzel', serif !important;
            color: #c9a54e !important;
        }

        div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] > div[data-testid="stContainer"] {
            border-color: var(--hud-border) !important;
        }

        div[data-testid="stRadio"] > div {
            gap: 0.5rem !important;
        }
        div[data-testid="stRadio"] label {
            font-family: 'Cinzel', serif !important;
            letter-spacing: 0.03em;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #13111a 0%, #0a0910 100%) !important;
            border-right: 1px solid var(--hud-border) !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #c9a54e !important;
        }

        textarea {
            background: #0a1222 !important;
            border-color: var(--hud-border) !important;
            color: #d9e6ff !important;
            font-family: monospace !important;
        }

        div[data-testid="stCheckbox"] label span {
            font-family: 'Crimson Text', Georgia, serif !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 6px !important;
            font-family: 'Crimson Text', Georgia, serif !important;
        }

        hr {
            border-color: var(--hud-border) !important;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0a15;
        }
        ::-webkit-scrollbar-thumb {
            background: #2a2015;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #3a3025;
        }

        /* Toggle switch styling */
        div[data-testid="stToggle"] label span {
            font-family: 'Crimson Text', Georgia, serif !important;
        }

        div[data-testid="stHorizontalBlock"] {
            align-items: start;
        }

        button[data-baseweb="tab"] {
            background: rgba(17, 26, 46, 0.72) !important;
            border: 1px solid var(--hud-border) !important;
            border-radius: 8px !important;
            color: var(--hud-muted) !important;
            font-family: 'Cinzel', serif !important;
            letter-spacing: 0.02em;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            border-color: #60a5fa !important;
            color: #e5efff !important;
            background: linear-gradient(180deg, rgba(36, 59, 99, 0.64), rgba(17, 30, 55, 0.82)) !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_fixed_game_layout() -> None:
    """Use a compact fixed layout on desktop while preserving mobile scroll behavior."""
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main,
        .stApp {
            height: 100vh !important;
            overflow: hidden !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1080px !important;
            padding-top: 0.7rem !important;
            padding-bottom: 0.7rem !important;
            height: calc(100vh - 1.4rem) !important;
            overflow: auto !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0.55rem !important;
        }

        [data-testid="stMainBlockContainer"] > div {
            width: 100%;
        }

        @media (max-width: 900px) {
            [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > .main,
            .stApp {
                height: auto !important;
                overflow: auto !important;
            }

            [data-testid="stMainBlockContainer"] {
                height: auto !important;
                overflow: visible !important;
                padding-top: 0.6rem !important;
                padding-bottom: 0.9rem !important;
                gap: 0.7rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_game_header() -> None:
    """Display title and subtitle in an ornate fantasy top panel."""
    st.markdown(
        """
        <div style="
            padding: 1.2rem 1.5rem;
            border: 1px solid #3a2a15;
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(30,20,10,0.85), rgba(20,15,8,0.7), rgba(30,20,10,0.85));
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(201,165,78,0.1);
        ">
            <div style="
                position: absolute; top: 0; left: 0; right: 0; height: 1px;
                background: linear-gradient(90deg, transparent, #c9a54e40, transparent);
            "></div>
            <h2 style="
                margin: 0;
                font-family: 'Cinzel', serif;
                font-size: 1.6rem;
                color: #facc15 !important;
                text-shadow: 0 0 20px rgba(250, 204, 21, 0.2);
                letter-spacing: 0.06em;
            ">Oakrest: Deterministic Adventure</h2>
            <p style="
                margin: 0.3rem 0 0 0;
                color: #8b7355;
                font-family: 'Crimson Text', Georgia, serif;
                font-size: 1rem;
                font-style: italic;
                letter-spacing: 0.02em;
            ">No dice. No randomness. Every choice carries weight.</p>
            <div style="
                position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
                background: linear-gradient(90deg, transparent, #c9a54e20, transparent);
            "></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_class_selection() -> None:
    """Render a fantasy-themed class selection screen with pixel art class icons."""
    st.markdown(
        """
        <div style="text-align: center; margin: 1rem 0 2rem 0;">
            <h1 style="
                font-family: 'Cinzel', serif;
                color: #facc15 !important;
                font-size: 2rem;
                margin-bottom: 0.3rem;
                text-shadow: 0 0 30px rgba(250, 204, 21, 0.15);
            ">Choose Your Path</h1>
            <p style="
                color: #8b7355;
                font-family: 'Crimson Text', Georgia, serif;
                font-size: 1.15rem;
                font-style: italic;
            ">Oakrest needs a hero. Your class shapes available paths and solutions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    meta_state = normalize_meta_state(st.session_state.get("meta_state"))
    unlocked = meta_state.get("unlocked_items", [])
    if unlocked:
        unlocked_text = ", ".join(escape(str(item), quote=True) for item in unlocked)
        st.markdown(
            f"""
            <div style="
                padding: 0.6rem 1rem;
                border: 1px solid #c9a54e40;
                border-radius: 8px;
                background: linear-gradient(135deg, rgba(30,20,10,0.6), rgba(20,15,8,0.4));
                margin-bottom: 1rem;
                text-align: center;
            ">
                <p style="
                    margin: 0;
                    color: #c9a54e;
                    font-family: 'Cinzel', serif;
                    font-size: 0.85rem;
                    letter-spacing: 0.04em;
                ">Legacy items carried forward: <strong>{unlocked_text}</strong></p>
                <p style="
                    margin: 0.2rem 0 0 0;
                    color: #8b7355;
                    font-family: 'Crimson Text', Georgia, serif;
                    font-size: 0.85rem;
                    font-style: italic;
                ">These relics from past journeys will join your inventory and unlock new paths.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)
    classes = [("Warrior", col1), ("Rogue", col2), ("Archer", col3)]
    for class_name, col in classes:
        info = CLASS_INFO[class_name]
        icon_svg = class_icon_svg(class_name, size=48)
        with col:
            st.markdown(
                f"""
                <div style="
                    padding: 1.2rem 1rem;
                    border: 1px solid {info['color']}50;
                    border-radius: 8px;
                    background: linear-gradient(180deg, rgba(15,12,20,0.9), rgba(8,6,12,0.95));
                    text-align: center;
                    min-height: 260px;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.3), inset 0 1px 0 {info['color']}15;
                    transition: border-color 0.3s ease, box-shadow 0.3s ease;
                ">
                    <div style="margin-bottom: 0.5rem;">
                        {icon_svg}
                    </div>
                    <h3 style="
                        font-family: 'Cinzel', serif;
                        color: {info['accent']} !important;
                        margin: 0 0 0.5rem 0;
                        font-size: 1.25rem;
                    ">{class_name}</h3>
                    <p style="
                        color: #9ca3af;
                        font-size: 0.9rem;
                        font-family: 'Crimson Text', Georgia, serif;
                        line-height: 1.5;
                        margin-bottom: 0.7rem;
                    ">{info['desc']}</p>
                    <p style="
                        color: {info['accent']};
                        font-family: 'Cinzel', serif;
                        font-size: 0.75rem;
                        letter-spacing: 0.06em;
                        opacity: 0.8;
                    ">{info['stats']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Begin as {class_name}",
                use_container_width=True,
                type="primary",
                key=f"class_{class_name}",
            ):
                start_game(class_name)
                st.rerun()


def _render_validation_warnings() -> None:
    if "story_validation_warnings" not in st.session_state:
        st.session_state.story_validation_warnings = validate_story_nodes()

    warnings = st.session_state.story_validation_warnings
    if not warnings:
        return

    with st.expander("Story validation warnings", expanded=False):
        if st.button("Re-run validator", key="refresh_story_validation"):
            st.session_state.story_validation_warnings = validate_story_nodes()
            st.rerun()
        st.warning("Validation found issues with story data. Review before publishing.")
        for warning in warnings:
            st.write(f"- {warning}")


def main() -> None:
    st.set_page_config(page_title="Oakrest: Deterministic Adventure", page_icon="shield", layout="wide")
    inject_game_theme()
    init_story_nodes()
    ensure_session_state()
    _render_validation_warnings()

    if st.session_state.player_class is None:
        render_game_header()
        _render_class_selection()
        return

    inject_fixed_game_layout()
    col_story, col_hud = st.columns([1.85, 1.15], gap="large")
    with col_story:
        render_node()
    with col_hud:
        render_side_panel()


if __name__ == "__main__":
    main()
