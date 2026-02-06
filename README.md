# choice-game

A deterministic, choice-driven fantasy adventure built with Streamlit.

## Quick start

1. `pip install streamlit`
2. `streamlit run app.py`

## Opportunities

Game design opportunities to consider as you expand content:

- Emphasize **early class differentiation** so each class feels distinct in the opening beats.
- Add a **pacing contrast** in the midgame (one or two quieter beats before major confrontations).
- Expand **ending clarity/epilogues** with aftermath details tied to key flags and traits.

## Recommendations

Priority recommendations to scale safely:

1. Add a **test suite** around `logic.py` and save/load schema handling.
2. Add a **strict content validator** (unknown flags/items, impossible requirements, class-lock audits).
3. Split `game/data.py` into smaller content files or externalize to schema-validated JSON/YAML.
5. Build a **balance dashboard** for per-class path viability and resource pressure.

## Narrative design principles

### Delayed consequences
Delayed consequences are what make players say **"oh damn..."**.

A choice should not only change the next line of dialogue — it should echo into later scenes, changing risk, trust, and what options are still possible.

### 4. Branching narrative paths
Not just different endings:
- Different scenes
- Different characters
- Different information

If everyone sees the same middle, it’s not really branching.

### 5. Irreversible decisions
Some choices must:
- Lock out content
- Kill characters
- Permanently change the world

This creates emotional weight.

### 🎮 Player-facing essentials
### 6. Clear feedback
Players must feel the impact through:
- NPC reactions
- World changes
- Tone shifts
- New options appearing or disappearing

Never say **"this mattered"** — show it.

## Choice simplification (max 6 options)

To prevent overloaded nodes, the story loader runs a simplification pass that:

- Auto-applies marked, low-impact choices (ex: class intro beats, judgment barks).
- Merges exact duplicates.
- Prunes log-only choices that duplicate another option with the same destination.
- Reports all changes in the console report list.

Tune the cap with `MAX_CHOICES_PER_NODE` in `game/data.py`. The UI will gracefully group overflow choices and surface diagnostics instead of crashing.

## Player feedback & overflow handling

- Every choice now shows a compact outcome summary (stat deltas, items, and public flags).
- Auto-applied events surface in a dedicated "Auto events" panel so changes are visible.
- Dense nodes show a warning banner and grouped option expanders when choices exceed the cap.

### Before/after examples

**Village Square (before):**
- 9 options (class intro + multiple prep/buy choices + two departures).

**Village Square (after):**
- Class intro is auto-applied on first visit.
- 6 remaining player-facing choices (prep/buy options plus the two departure paths).

**War Council Hub (before):**
- 11 options (judgment barks, multiple allied breaches, tactical routes).

**War Council Hub (after):**
- Judgment barks are auto-applied.
- Allied breach and tactical advantage options are merged into clear, single entries.
- 6 remaining player-facing choices.
