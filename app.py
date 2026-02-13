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
    """Apply rich visual styling with polished animations for a fantasy game HUD."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

        :root {
            --hud-bg: #080d1a;
            --hud-panel: #0e1628;
            --hud-panel-glass: rgba(12, 20, 40, 0.75);
            --hud-border: #1e2d4a;
            --hud-border-light: #2a3f66;
            --hud-text: #dbe7ff;
            --hud-muted: #7b8fad;
            --hud-accent: #f0c850;
            --hud-gold: #d4a843;
            --hud-gold-glow: rgba(212, 168, 67, 0.25);
            --hud-danger: #e85454;
            --hud-success: #34d399;
            --glass-bg: linear-gradient(135deg, rgba(14, 22, 40, 0.85), rgba(8, 13, 26, 0.92));
            --glass-border: rgba(42, 63, 102, 0.6);
        }

        /* ===== KEYFRAME ANIMATIONS ===== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 8px rgba(212, 168, 67, 0.15); }
            50% { box-shadow: 0 0 20px rgba(212, 168, 67, 0.3); }
        }
        @keyframes subtleBreathe {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-8px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes borderGlow {
            0%, 100% { border-color: var(--hud-border); }
            50% { border-color: var(--hud-border-light); }
        }

        /* ===== BASE ===== */
        .stApp {
            background:
                radial-gradient(ellipse 1100px 600px at 5% 0%, rgba(20, 40, 80, 0.4), transparent 55%),
                radial-gradient(ellipse 800px 500px at 95% 100%, rgba(100, 55, 15, 0.18), transparent 50%),
                radial-gradient(ellipse 600px 400px at 50% 50%, rgba(15, 20, 40, 0.3), transparent 70%),
                linear-gradient(180deg, #040710 0%, #070c1a 40%, #0a1020 70%, #080d18 100%);
            color: var(--hud-text);
            font-family: 'Crimson Text', Georgia, serif;
        }

        /* ===== TYPOGRAPHY ===== */
        h1, h2, h3, h4 {
            font-family: 'Cinzel', 'Times New Roman', serif !important;
            color: #e8d5b0 !important;
            letter-spacing: 0.05em;
            text-shadow: 0 2px 6px rgba(0,0,0,0.6), 0 0 20px rgba(212,168,67,0.08);
        }
        h1 { color: var(--hud-accent) !important; }

        /* ===== METRICS ===== */
        div[data-testid="stMetricValue"] {
            color: var(--hud-accent) !important;
            font-family: 'Cinzel', serif !important;
            font-weight: 700;
            text-shadow: 0 0 12px var(--hud-gold-glow);
        }
        div[data-testid="stMetricLabel"] {
            font-family: 'Cinzel', serif !important;
            color: var(--hud-muted) !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.75rem !important;
        }

        /* ===== BUTTONS ===== */
        div.stButton > button {
            border-radius: 8px !important;
            border: 1px solid var(--hud-border) !important;
            background: var(--glass-bg) !important;
            color: #c8d8f0 !important;
            font-family: 'Crimson Text', Georgia, serif !important;
            font-size: 1.05rem !important;
            padding: 0.65rem 1.1rem !important;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }
        div.stButton > button::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, transparent 50%);
            pointer-events: none;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, rgba(25, 40, 70, 0.9), rgba(18, 30, 55, 0.95)) !important;
            border-color: #4a7cc9 !important;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15), 0 0 1px rgba(59, 130, 246, 0.3), inset 0 1px 0 rgba(255,255,255,0.05) !important;
            color: #e8f0ff !important;
            transform: translateY(-2px);
        }
        div.stButton > button:active {
            transform: translateY(0px) !important;
            transition-duration: 0.1s !important;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6b2510 0%, #3d1508 50%, #4a1a0a 100%) !important;
            border: 1px solid rgba(251, 146, 60, 0.5) !important;
            color: #fef3c7 !important;
            box-shadow: 0 2px 12px rgba(180, 80, 20, 0.15), inset 0 1px 0 rgba(255,200,100,0.08) !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #862f15 0%, #5c2511 50%, #6b3015 100%) !important;
            border-color: rgba(253, 186, 116, 0.7) !important;
            box-shadow: 0 4px 24px rgba(249, 115, 22, 0.25), 0 0 2px rgba(249, 115, 22, 0.4), inset 0 1px 0 rgba(255,200,100,0.1) !important;
            transform: translateY(-2px);
        }

        /* ===== EXPANDERS ===== */
        div[data-testid="stExpander"] {
            border: 1px solid var(--hud-border) !important;
            background: var(--hud-panel-glass) !important;
            border-radius: 10px !important;
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            transition: border-color 0.3s ease !important;
        }
        div[data-testid="stExpander"]:hover {
            border-color: var(--hud-border-light) !important;
        }
        div[data-testid="stExpander"] summary {
            font-family: 'Cinzel', serif !important;
            color: var(--hud-gold) !important;
            letter-spacing: 0.03em;
        }

        /* ===== CONTAINERS ===== */
        div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] > div[data-testid="stContainer"] {
            border-color: var(--hud-border) !important;
            border-radius: 10px !important;
        }

        /* ===== RADIO ===== */
        div[data-testid="stRadio"] > div {
            gap: 0.5rem !important;
        }
        div[data-testid="stRadio"] label {
            font-family: 'Cinzel', serif !important;
            letter-spacing: 0.03em;
        }

        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0c0a14 0%, #070610 100%) !important;
            border-right: 1px solid var(--hud-border) !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: var(--hud-gold) !important;
        }

        /* ===== TEXTAREA ===== */
        textarea {
            background: rgba(8, 14, 28, 0.9) !important;
            border-color: var(--hud-border) !important;
            color: #d0dcf0 !important;
            font-family: monospace !important;
            border-radius: 8px !important;
        }

        /* ===== FORM ELEMENTS ===== */
        div[data-testid="stCheckbox"] label span {
            font-family: 'Crimson Text', Georgia, serif !important;
        }
        div[data-testid="stToggle"] label span {
            font-family: 'Crimson Text', Georgia, serif !important;
        }

        /* ===== ALERTS ===== */
        div[data-testid="stAlert"] {
            border-radius: 8px !important;
            font-family: 'Crimson Text', Georgia, serif !important;
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
        }

        /* ===== DIVIDERS ===== */
        hr {
            border-color: var(--hud-border) !important;
            opacity: 0.6;
        }

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(42, 63, 102, 0.5);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(62, 88, 130, 0.7);
        }

        /* ===== HORIZONTAL BLOCK ===== */
        div[data-testid="stHorizontalBlock"] {
            align-items: start;
        }

        /* ===== TABS ===== */
        button[data-baseweb="tab"] {
            background: var(--hud-panel-glass) !important;
            border: 1px solid var(--hud-border) !important;
            border-radius: 10px !important;
            color: var(--hud-muted) !important;
            font-family: 'Cinzel', serif !important;
            letter-spacing: 0.03em;
            font-size: 0.82rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
        }
        button[data-baseweb="tab"]:hover {
            border-color: var(--hud-border-light) !important;
            color: #b8c8e0 !important;
            background: rgba(20, 32, 56, 0.8) !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            border-color: rgba(96, 165, 250, 0.5) !important;
            color: #e5efff !important;
            background: linear-gradient(135deg, rgba(30, 50, 85, 0.7), rgba(15, 25, 50, 0.85)) !important;
            box-shadow: 0 2px 12px rgba(96, 165, 250, 0.1) !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        /* ===== PROGRESS BAR ===== */
        div[data-testid="stProgress"] > div {
            border-radius: 6px !important;
            overflow: hidden;
        }

        /* ===== GLOBAL CONTENT ANIMATION ===== */
        [data-testid="stMainBlockContainer"] > div {
            animation: fadeIn 0.4s ease-out;
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
            max-width: 1140px !important;
            padding-top: 0.6rem !important;
            padding-bottom: 0.6rem !important;
            height: calc(100vh - 1.2rem) !important;
            overflow: auto !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0.5rem !important;
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
                max-width: 100% !important;
                height: auto !important;
                overflow: visible !important;
                padding-top: 0.5rem !important;
                padding-bottom: 1rem !important;
                gap: 0.6rem !important;
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
            padding: 1.8rem 2rem;
            border: 1px solid rgba(212, 168, 67, 0.2);
            border-radius: 12px;
            background:
                linear-gradient(135deg, rgba(25, 18, 8, 0.9) 0%, rgba(15, 12, 6, 0.75) 50%, rgba(25, 18, 8, 0.9) 100%);
            margin-bottom: 1.2rem;
            position: relative;
            overflow: hidden;
            box-shadow:
                0 8px 32px rgba(0,0,0,0.5),
                0 2px 8px rgba(0,0,0,0.3),
                inset 0 1px 0 rgba(212, 168, 67, 0.1);
            animation: fadeInUp 0.6s ease-out;
            text-align: center;
        ">
            <!-- Top shimmer line -->
            <div style="
                position: absolute; top: 0; left: 0; right: 0; height: 1px;
                background: linear-gradient(90deg, transparent 10%, rgba(212, 168, 67, 0.4) 50%, transparent 90%);
            "></div>
            <!-- Corner accents -->
            <div style="
                position: absolute; top: -1px; left: -1px; width: 24px; height: 24px;
                border-top: 2px solid rgba(212, 168, 67, 0.3);
                border-left: 2px solid rgba(212, 168, 67, 0.3);
                border-radius: 12px 0 0 0;
            "></div>
            <div style="
                position: absolute; top: -1px; right: -1px; width: 24px; height: 24px;
                border-top: 2px solid rgba(212, 168, 67, 0.3);
                border-right: 2px solid rgba(212, 168, 67, 0.3);
                border-radius: 0 12px 0 0;
            "></div>
            <div style="
                position: absolute; bottom: -1px; left: -1px; width: 24px; height: 24px;
                border-bottom: 2px solid rgba(212, 168, 67, 0.15);
                border-left: 2px solid rgba(212, 168, 67, 0.15);
                border-radius: 0 0 0 12px;
            "></div>
            <div style="
                position: absolute; bottom: -1px; right: -1px; width: 24px; height: 24px;
                border-bottom: 2px solid rgba(212, 168, 67, 0.15);
                border-right: 2px solid rgba(212, 168, 67, 0.15);
                border-radius: 0 0 12px 0;
            "></div>
            <!-- Ornamental divider above title -->
            <div style="
                margin: 0 auto 0.8rem auto;
                width: 60px;
                height: 2px;
                background: linear-gradient(90deg, transparent, rgba(212, 168, 67, 0.5), transparent);
            "></div>
            <h2 style="
                margin: 0;
                font-family: 'Cinzel', serif;
                font-size: 1.8rem;
                color: #f0c850 !important;
                text-shadow: 0 0 30px rgba(240, 200, 80, 0.2), 0 2px 8px rgba(0,0,0,0.6);
                letter-spacing: 0.08em;
                line-height: 1.3;
            ">Oakrest</h2>
            <p style="
                margin: 0.15rem 0 0 0;
                color: rgba(212, 168, 67, 0.6);
                font-family: 'Cinzel', serif;
                font-size: 0.72rem;
                letter-spacing: 0.25em;
                text-transform: uppercase;
            ">Deterministic Adventure</p>
            <!-- Ornamental divider below subtitle -->
            <div style="
                margin: 0.8rem auto 0 auto;
                width: 120px;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(212, 168, 67, 0.3), transparent);
            "></div>
            <p style="
                margin: 0.7rem 0 0 0;
                color: #6b5a40;
                font-family: 'Crimson Text', Georgia, serif;
                font-size: 1.05rem;
                font-style: italic;
                letter-spacing: 0.03em;
            ">No dice. No randomness. Every choice carries weight.</p>
            <!-- Bottom shimmer line -->
            <div style="
                position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
                background: linear-gradient(90deg, transparent 10%, rgba(212, 168, 67, 0.15) 50%, transparent 90%);
            "></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_class_selection() -> None:
    """Render a fantasy-themed class selection screen with pixel art class icons."""
    st.markdown(
        """
        <div style="text-align: center; margin: 1.5rem 0 2.5rem 0; animation: fadeInUp 0.5s ease-out;">
            <h1 style="
                font-family: 'Cinzel', serif;
                color: #f0c850 !important;
                font-size: 2.2rem;
                margin-bottom: 0.4rem;
                text-shadow: 0 0 40px rgba(240, 200, 80, 0.15), 0 2px 8px rgba(0,0,0,0.5);
                letter-spacing: 0.08em;
            ">Choose Your Path</h1>
            <div style="
                margin: 0.3rem auto;
                width: 80px;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(212, 168, 67, 0.4), transparent);
            "></div>
            <p style="
                color: #7a6a50;
                font-family: 'Crimson Text', Georgia, serif;
                font-size: 1.15rem;
                font-style: italic;
                margin-top: 0.5rem;
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
                padding: 0.7rem 1.2rem;
                border: 1px solid rgba(212, 168, 67, 0.25);
                border-radius: 10px;
                background: linear-gradient(135deg, rgba(25, 18, 8, 0.7), rgba(15, 10, 5, 0.5));
                margin-bottom: 1.2rem;
                text-align: center;
                animation: fadeIn 0.6s ease-out 0.2s both;
            ">
                <p style="
                    margin: 0;
                    color: #d4a843;
                    font-family: 'Cinzel', serif;
                    font-size: 0.85rem;
                    letter-spacing: 0.04em;
                ">Legacy items carried forward: <strong>{unlocked_text}</strong></p>
                <p style="
                    margin: 0.25rem 0 0 0;
                    color: #7a6a50;
                    font-family: 'Crimson Text', Georgia, serif;
                    font-size: 0.85rem;
                    font-style: italic;
                ">These relics from past journeys will join your inventory and unlock new paths.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)
    classes = [("Warrior", col1, "0.3s"), ("Rogue", col2, "0.45s"), ("Archer", col3, "0.6s")]
    for class_name, col, delay in classes:
        info = CLASS_INFO[class_name]
        icon_svg = class_icon_svg(class_name, size=56)
        with col:
            st.markdown(
                f"""
                <div style="
                    padding: 1.5rem 1.2rem;
                    border: 1px solid {info['color']}40;
                    border-radius: 12px;
                    background:
                        linear-gradient(180deg, rgba(12, 10, 18, 0.92) 0%, rgba(6, 5, 10, 0.96) 100%);
                    text-align: center;
                    min-height: 280px;
                    box-shadow:
                        0 4px 20px rgba(0,0,0,0.4),
                        0 1px 4px rgba(0,0,0,0.2),
                        inset 0 1px 0 {info['color']}10;
                    position: relative;
                    overflow: hidden;
                    animation: fadeInUp 0.5s ease-out {delay} both;
                ">
                    <!-- Top accent line -->
                    <div style="
                        position: absolute; top: 0; left: 15%; right: 15%; height: 2px;
                        background: linear-gradient(90deg, transparent, {info['color']}50, transparent);
                        border-radius: 0 0 2px 2px;
                    "></div>
                    <!-- Icon container with glow -->
                    <div style="
                        margin: 0.3rem auto 0.8rem auto;
                        width: 72px;
                        height: 72px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 50%;
                        background: radial-gradient(circle, {info['color']}10 0%, transparent 70%);
                        box-shadow: 0 0 30px {info['color']}15;
                    ">
                        {icon_svg}
                    </div>
                    <h3 style="
                        font-family: 'Cinzel', serif;
                        color: {info['accent']} !important;
                        margin: 0 0 0.6rem 0;
                        font-size: 1.3rem;
                        letter-spacing: 0.06em;
                        text-shadow: 0 0 20px {info['color']}30;
                    ">{class_name}</h3>
                    <p style="
                        color: #8b90a0;
                        font-size: 0.9rem;
                        font-family: 'Crimson Text', Georgia, serif;
                        line-height: 1.6;
                        margin-bottom: 0.8rem;
                    ">{info['desc']}</p>
                    <!-- Stat divider -->
                    <div style="
                        margin: 0 auto 0.5rem auto;
                        width: 40px;
                        height: 1px;
                        background: linear-gradient(90deg, transparent, {info['color']}30, transparent);
                    "></div>
                    <p style="
                        color: {info['accent']};
                        font-family: 'Cinzel', serif;
                        font-size: 0.72rem;
                        letter-spacing: 0.08em;
                        opacity: 0.75;
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
    col_story, col_hud = st.columns([1.9, 1.1], gap="large")
    with col_story:
        render_node()
    with col_hud:
        render_side_panel()


if __name__ == "__main__":
    main()
