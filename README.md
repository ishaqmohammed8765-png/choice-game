# choice-game

A deterministic, choice-driven fantasy adventure built with Streamlit.

## Quick start

1. `python -m pip install -r requirements.txt`
2. `streamlit run app.py`

## Development setup

1. `python -m pip install -r requirements-dev.txt`
2. `python -m pytest -q`

## Current architecture

- `game/content/`: story nodes, class templates, content constants.
- `game/logic.py`: requirement checks, effects, transitions, auto-events.
- `game/state.py`: session lifecycle, snapshots, save/load, undo.
- `game/validation.py`: strict content validation for links, keys, and reachability.
- `game/ui_components/`: modular UI (node view, map, sidebar, sprites, epilogues, logs).

## Gameplay design notes

- Early class identity: openings and class-gated routes should feel distinct.
- Midgame pacing: include quieter beats between major confrontations.
- Ending clarity: tie epilogue aftermath to flags, traits, and faction outcomes.
- Consequences: choices should echo forward, not just change the next line.

## Tooling

- `scripts/balance_report.py`: quick class viability and resource-pressure report.
  - Run with: `python scripts/balance_report.py`
- Story simplification pass:
  - auto-applies marked low-impact beats,
  - removes exact duplicate choices,
  - groups or prunes noisy low-impact options when needed.
