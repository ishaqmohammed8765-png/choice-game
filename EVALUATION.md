# Oakrest Code & Game Evaluation

## Scope
This review evaluates both:
- **Code quality and maintainability** (architecture, reliability, testability)
- **Game design quality** (branching, consequence design, replay value, UX)

## What I checked
- Read core app and module files (`app.py`, `game/state.py`, `game/logic.py`, `game/ui.py`, `game/data.py`).
- Ran a static structure analysis script over `STORY_NODES`.
- Attempted to install/run Streamlit for runtime validation (blocked by environment network/proxy constraints).

## Overall assessment

### Codebase
**Rating: 8/10 (solid structure, minor maintainability risks)**

#### Strengths
1. **Clean module separation**
   - `state.py` handles lifecycle and snapshots.
   - `logic.py` handles requirements/effects/transitions.
   - `ui.py` handles rendering and interaction flow.
   - `data.py` cleanly centralizes narrative/content.

2. **Good deterministic mechanics**
   - Requirements and effects are explicit dictionaries.

3. **Resilience choices are thoughtful**
   - Missing links and invalid access can route into fallback failure arcs instead of hard crashes.
   - Choice warning/confirmation for irreversible/high-cost options reduces accidental run-ending clicks.

#### Risks / issues
1. **Single giant content file (`game/data.py`)**
   - Story content is extensive and monolithic, which will become difficult to review and diff as it grows.
   - Recommend splitting into chapter/arc files or external JSON/YAML with schema validation.

2. **Validation currently lightweight**
   - Existing validation focuses on ID/link integrity.
   - Recommend adding stricter validation for requirement/effect key correctness, unknown flags/items, and unintended dead-ends.

3. **Sparse automated test coverage**
   - No unit/integration test suite is present.
   - Add tests for:
     - requirements gating behavior,
     - effect application bounds,
     - transition fallback behavior,
     - import/save schema handling.


### Game design
**Rating: 7.5/10 (strong deterministic branching base, room for pacing polish)**

#### Strengths
1. **Meaningful replay loop by class + flags + items**
   - Multiple class templates and gated options encourage replay.
2. **Consequence-forward design**
   - Uses flags, trait deltas, and seen events to carry impact forward.
3. **Recoverable failure arcs**
   - Failure nodes preserve momentum better than abrupt dead-ends.
4. **Clear decision feedback**
   - Warnings, logs, and state visibility help players understand consequences.

#### Opportunities
1. **Improve thematic differentiation per class in early game**
   - Early branch flavor can be made more asymmetrical so each class identity emerges faster.
2. **Pacing and tension curve**
   - Midgame could benefit from one or two “quiet beats” before major confrontations to increase dramatic contrast.
3. **Ending clarity and epilogue richness**
   - Endings could expose more post-choice aftermath details tied to key trait/flag outcomes.

## Static content health snapshot
From static graph analysis:
- **32 nodes**
- **99 choices**
- **6 ending nodes**
- **No broken `next` links detected in choice graph**

Notes:
- Some nodes (e.g., failure/death variants) are intentionally reached through runtime transition logic (`instant_death`/fallbacks) rather than plain static edges.

## Priority recommendations (ordered)
1. Add **test suite** for `logic.py` + save/load schema handling.
2. Add **strict content validator** (unknown keys/flags/items, impossible requirements, class-lock audits).
3. Split `game/data.py` into smaller domain files (or schema-backed content files).
5. Add a basic **balance dashboard script** (per-class path viability, resource pressure by route).

## Verdict
This is a **good foundation** for a deterministic narrative game: architecture is clean and game systems are coherent. The biggest step up now is investing in **validation + tests + content modularization** to safely scale story complexity.
