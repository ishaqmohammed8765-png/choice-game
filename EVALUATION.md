# Oakrest: Deterministic Adventure — Detailed Code Evaluation

## 1. Project Overview

**Type:** Interactive text-adventure / narrative game engine
**Language:** Python 3.11
**Framework:** Streamlit (web UI)
**Lines of code:** ~3,500 across 22 source files
**Content scale:** 39 story nodes, ~130 choices, 6+ endings, 3 playable classes

The game is a deterministic, choice-driven fantasy narrative where player class, stats, items, flags, and faction standings shape available paths. No randomness exists anywhere in the mechanics.

---

## 2. Architecture Assessment

### 2.1 Module Structure

```
app.py                     Entry point + Streamlit page config + theme
game/
  logic.py                 Core mechanics: requirements, effects, transitions
  state.py                 Session state lifecycle, snapshots, save/load
  validation.py            Strict story content validation
  streamlit_compat.py      Stub layer for test-time Streamlit absence
  ui.py                    Backward-compat re-export facade
  data.py                  Backward-compat re-export facade
  content/
    constants.py           Stat/trait/faction keys, thresholds
    classes.py             Class templates (Warrior, Rogue, Archer)
    story.py               Aggregator + simplification trigger
    story_utils.py         Auto-apply, dedup, pruning pipeline
    story_nodes_intro.py   Class-specific openings
    story_nodes_act1.py    Act 1 nodes
    story_nodes_act2.py    Act 2 nodes
    story_nodes_act3.py    Act 3 nodes
  ui_components/
    node_view.py           Story rendering + choice interaction
    sidebar.py             Player HUD + save/load + undo
    path_map.py            SVG graph visualization
    epilogue.py            Flag-driven aftermath text
    log_view.py            Recent event log display
tests/
  test_logic.py            9 tests covering core mechanics
  test_state.py            5 tests covering state lifecycle
  test_ui_logic.py         5 tests covering UI helper logic
scripts/
  balance_report.py        Per-class viability analysis
```

**Verdict:** The separation of concerns is strong. Content, logic, state, validation, and UI are cleanly isolated. The backward-compatibility layers (`data.py`, `ui.py`) are a reasonable approach to a recent refactor from monolithic files into the `content/` and `ui_components/` packages.

### 2.2 Dependency Graph

```
app.py -> game.logic, game.state, game.ui
game.logic -> game.data (content), game.state, game.validation
game.state -> game.data (content), game.streamlit_compat
game.validation -> game.content (direct)
game.ui_components/* -> game.data, game.logic, game.streamlit_compat
game.content.story -> game.content.story_utils (simplification at import time)
```

No circular dependencies exist. The `streamlit_compat` module is a leaf with no game imports, which is correct for a compatibility shim.

### 2.3 Architecture Strengths

1. **Pure data-driven content.** Story nodes are plain Python dicts with a consistent schema. No behavior logic leaks into content definitions.
2. **Deterministic by construction.** There is zero use of `random`, `time`, or external input in the game engine. Every outcome is derived from explicit requirements + effects.
3. **Testable without Streamlit.** The `streamlit_compat.py` stub allows the entire logic layer to be tested without installing Streamlit (`_FallbackStreamlit` + `_SessionState`).
4. **Graceful degradation.** Missing nodes route to `failure_captured`, not crashes. Invalid state routes to `death`. Every error path is recoverable.
5. **Content validated at import time.** `validate_story_nodes()` runs on app startup, catching broken links, unknown keys, and impossible requirements before the player sees them.

### 2.4 Architecture Weaknesses

1. **Module-level side effects.** `game/content/story.py:16` calls `simplify_story_nodes(STORY_NODES)` at import time, mutating the global dict. This means importing the module has side effects, which can cause subtle bugs if import order changes or if modules are re-imported in tests.
2. **Global mutable state via `CHOICE_SIMPLIFICATION_REPORT`.** This list in `constants.py` is a module-level mutable singleton. It accumulates across the process lifetime and is never cleared, which would cause issues in long-running test suites or if the app were ever reloaded.
3. **Session state as implicit global.** All game state lives in `st.session_state`, accessed via module-level imports. This works for Streamlit's execution model but makes the code harder to unit test in isolation since every test must set up the full session state.

---

## 3. Core Engine Analysis (`logic.py` — 308 lines)

### 3.1 Requirement Checking (`check_requirements`)

- Handles: class restrictions, min stats (hp/gold/strength/dexterity), required items, missing items, flag true/false, and `any_of` composite requirements.
- Recursive `any_of` handling is correct — each sub-requirement is checked independently.
- Returns `(bool, str)` tuple with a human-readable failure reason, used downstream for tooltips.

**Issue — incomplete `any_of` reason reporting.** When all `any_of` options fail, the reason returned is a generic "Requires one of multiple conditions" instead of listing which specific conditions failed. This reduces debuggability and player understanding.

### 3.2 Choice Resolution (`resolve_choice_outcome`)

- Iterates `conditional_effects` in order, applying the first matching variant.
- Uses `merge_effects` to combine base effects with conditional effects additively for stats and accumulatively for items/flags/traits.
- The `break` on line 141 ensures only the first matching conditional is applied. This is correct for deterministic resolution but could be surprising if a content author expects multiple conditionals to stack.

**Observation:** `merge_effects` uses set operations `{*merged["add_items"], *incoming["add_items"]}` for item deduplication (line 155). This loses ordering. Not a bug for gameplay, but means item display order in effects may not match content definition order.

### 3.3 Effect Application (`apply_effects`)

- Correctly applies stats, items, flags, traits, factions, and seen events.
- `apply_morality_flags()` syncs legacy `mercy_reputation`/`cruel_reputation` booleans with the canonical `morality` flag. This dual-tracking is a maintenance burden but works correctly.

**Issue — no stat floor enforcement.** HP can go negative (line 199: `stats[stat] += effects[stat]`). While `transition_to` checks for `hp <= 0` and routes to death, the raw stat value can be arbitrarily negative. Gold can also go negative if effects aren't carefully authored. There is no clamping.

### 3.4 State Transitions (`transition_to`, `execute_choice`)

- `transition_to` checks HP death, missing node fallback, then sets `current_node`.
- `execute_choice` correctly snapshots state before applying changes, enabling undo.
- `_resolve_transition_node` and `_record_visit` track the visit graph for the path map.

**Issue — redundant death check.** `execute_choice` calls `_resolve_transition_node` (which checks `hp <= 0`) and then also calls `transition_to` (which checks `hp <= 0` again). The `instant_death` early return on line 46-48 sets `current_node = "death"` and returns, but `_record_visit` on line 40 was already called with the resolved node. If `instant_death` is true, the visit is recorded to "death" before the early return, which is correct but slightly confusing control flow.

**Issue — `execute_choice` line 50 calls `transition_to(resolved_next)` but uses the original `resolved_next` from `resolve_choice_outcome`, not the `actual_next` from `_resolve_transition_node`.** If the node is missing, `_record_visit` records a visit to the fallback node, but `transition_to` independently resolves the missing node again. The two fallback resolutions could theoretically diverge (one uses `failure_captured`, the other uses whatever `transition_to` decides).

### 3.5 Auto-Choices (`apply_node_auto_choices`)

- Uses `f"auto_choice::{node_id}::{idx}"` as a flag marker to prevent re-application. This is a clean approach.
- Effects are resolved and applied immediately on node entry.
- The pattern of storing "has this auto-choice fired" as a game flag pollutes the flag namespace with system markers (e.g., `auto_choice::war_council_hub::0`).

---

## 4. State Management Analysis (`state.py` — 180 lines)

### 4.1 Snapshot System

- `snapshot_state()` uses `copy.deepcopy` on every mutable field. This is correct and prevents aliasing bugs.
- `load_snapshot()` restores all fields with `.get()` fallbacks for backward compatibility with older save formats.
- `validate_snapshot()` checks required keys, valid class, valid node, stat/trait/faction structure, and list/dict types. This is thorough.

**Issue — `validate_snapshot` doesn't check `history`, `visited_nodes`, or `visited_edges`.** These are present in snapshots (captured by `snapshot_state`) but not validated on load. A malformed save could have invalid types for these fields.

**Issue — `snapshot_state` captures `pending_choice_confirmation` but `validate_snapshot` doesn't check it.** A crafted save payload could inject arbitrary data into `pending_choice_confirmation`.

### 4.2 Session Initialization

- `ensure_session_state` initializes missing keys with defaults. This is correct for Streamlit's rerun model where session state persists across reruns.
- `reset_game_state` zeroes everything. `start_game` copies from class templates.
- `start_game` correctly uses `copy.deepcopy` on the inventory template (line 45) to prevent shared references.

### 4.3 Undo System

- The undo stack in `st.session_state.history` stores full snapshots. This is memory-intensive but simple and correct.
- `irreversible` choices clear the entire history (logic.py line 42), which is a good design constraint.
- No maximum stack depth is enforced. In a long playthrough, the history list could grow large.

---

## 5. Validation System Analysis (`validation.py` — 274 lines)

### 5.1 Coverage

The validator checks:
- Node ID consistency (key vs. `id` field)
- Broken `next` links in choices and conditional effects
- Unknown requirement keys
- Unknown effect keys
- Unknown class names in requirements
- Items that are never granted but required/removed
- Flags that are never set but checked
- Unknown trait and faction keys in deltas
- Unreachable stat requirements (stat never achievable for any valid class)
- Class lockout detection (nodes where a class has zero viable choices)
- Empty class requirements lists
- Intro nodes excluded from lockout checks

**Strength:** This is an unusually thorough validator for a project of this scale. The class-lockout detection and unreachable-stat checks go well beyond typical link integrity validation.

### 5.2 Issues

**Issue — `_possible_stat_caps` returns the same `max_gains` dict for every class (line 78-80).** The function sums all possible stat gains globally but then assigns the same gain dict to every class key. This means the max-stat calculation assumes every class can collect every stat gain in the game, which is incorrect since some choices are class-gated. The function name suggests per-class calculation, but the implementation ignores class requirements on stat-granting choices.

**Issue — `_max_stats_for_class` (line 83-88) compounds the above error by adding these inflated gains to each class's base stats.** The result is that stat reachability checks are overly permissive — they may fail to flag requirements that are actually unreachable for a specific class.

**Observation:** The validator does not check for cycles in the story graph (infinite loops). While the game has natural escape valves (HP drain, flag-gating), a content error could create an unintended loop with no exit.

---

## 6. UI Layer Analysis

### 6.1 Node Rendering (`node_view.py` — 151 lines)

- Handles: missing nodes, node-level requirements, auto-choices, dialogue, HP redirect, choice overflow, endings with epilogue, locked choices, pending confirmation, and empty-choice fallback.
- The `should_force_injury_redirect` function correctly exempts failure nodes and the death node from HP redirect loops.
- Choice overflow raises `RuntimeError` with a hard crash. In production, this would kill the Streamlit app. A softer handling (truncation + warning) might be preferable.

**Issue — rendering order.** Auto-choices are applied (line 77) before the HP redirect check (line 94). If an auto-choice reduces HP to 0, the redirect happens after the auto-choice effects are applied. This is correct but means the player never sees the auto-choice feedback before being redirected.

### 6.2 Sidebar (`sidebar.py` — 80 lines)

- Clean stat display with Streamlit metrics.
- Undo pops the last snapshot and reloads it. Simple and correct.
- Save/load uses JSON serialization with validation.

**Security consideration:** The save/load system accepts arbitrary JSON from a text area (line 22-23). While `validate_snapshot` checks structure, it doesn't sanitize string values. Malicious save data could inject very long strings or special characters that affect rendering. This is low-risk in a single-player context but worth noting.

### 6.3 Path Map (`path_map.py` — 257 lines)

- Generates an SVG spider diagram centered on the current node.
- Uses `_escape_tooltip` to prevent XSS in SVG content. This correctly escapes `&`, `<`, `>`, and `"`.
- Locked choices show requirement tooltips; visited nodes/edges use distinct styling.

**Issue — SVG injection via `unsafe_allow_html=True`.** While tooltips are escaped, the SVG is constructed by string interpolation with node titles and choice labels that come from content data (line 130-131). If content data contained `<script>` tags or SVG event handlers, they would be injected. Since content is developer-authored (not user-input), this is low-risk but violates defense-in-depth. The `_escape_tooltip` function should be applied to all interpolated content strings, not just tooltips.

### 6.4 Epilogue (`epilogue.py` — 91 lines)

- Builds aftermath text from ~30 flag/trait/faction checks.
- Returns at most 9 lines (line 90: `return lines[:9]`), preventing UI overflow.
- Checks cover class-specific flags, morality paths, alliance outcomes, mini-boss results, and trait thresholds.

**Observation:** The 9-line cap is arbitrary. A player who completed many side objectives may miss aftermath details. Consider making this configurable or expandable.

### 6.5 Log View (`log_view.py` — 13 lines)

- Displays the last 10 events in a collapsible expander.
- Minimal and correct. Could benefit from showing timestamps or node context.

---

## 7. Content System Analysis

### 7.1 Story Structure

The story follows a three-act structure:

- **Intro (3 nodes):** Class-specific openings that set initial flags and traits.
- **Act 1 (10 nodes):** Village hub, camp shop, forest crossroad with faction/operation branches.
- **Act 2 (12 nodes):** Mini-bosses (Tidebound Knight, Pyre-Alchemist), war council, hidden routes.
- **Act 3 (14 nodes):** Vigil quiet beat, final confrontation with 3 sub-pages of tactical options, 6 endings, 4 failure/recovery nodes, death.

### 7.2 Choice Simplification Pipeline (`story_utils.py`)

The pipeline runs at import time and modifies `STORY_NODES` in-place:

1. **Auto-apply extraction:** Choices marked `auto_apply: true` are moved from `choices` to `auto_choices`.
2. **Deduplication:** Choices with identical `(next, requirements, effects, conditional_effects)` are removed.
3. **Low-impact pruning:** If choices exceed `MAX_CHOICES_PER_NODE` (6), log-only choices without conditional effects are removed first.

**Issue — `freeze` function for dedup keys (line 11-15) uses `sorted(value)` on dict keys.** This means deduplication treats `{"a": 1, "b": 2}` and `{"b": 2, "a": 1}` as identical, which is correct. However, lists are compared by element order, so `["a", "b"]` and `["b", "a"]` are considered different. This could miss some duplicates where item order differs.

### 7.3 Class Balance (from balance report)

| Metric | Warrior | Rogue | Archer |
|--------|---------|-------|--------|
| Base HP | 14 | 10 | 12 |
| Base Gold | 8 | 10 | 9 |
| Base STR | 4 | 2 | 3 |
| Base DEX | 2 | 4 | 3 |
| Max HP (estimated) | 30 | 26 | 28 |
| Max Gold (estimated) | 26 | 28 | 27 |
| Viable choices | 127 | 126 | 127 |
| Locked nodes | 0 | 0 | 0 |

Balance is remarkably even. All three classes have access to all 39 choice-bearing nodes and roughly equal viable choice counts. The Warrior trades dexterity-gated paths for strength-gated ones, and vice versa for the Rogue, while the Archer sits in the middle.

### 7.4 Content Quality

- **Node text** is well-written with consistent tone (gritty fantasy, concise prose).
- **Dialogue** adds character voice without being excessive (2-3 lines per node).
- **Flag naming** is consistent and descriptive (`branch_ravine_completed`, `mercy_reputation`, `pyre_alchemist_defeated`).
- **Conditional effects** are used effectively for class-variant experiences at the same choice point.

---

## 8. Test Suite Analysis

### 8.1 Current Coverage

**19 tests, all passing (0.14s):**

| File | Tests | Coverage Area |
|------|-------|---------------|
| `test_logic.py` | 9 | Requirements, effects, choices, transitions, validation |
| `test_state.py` | 5 | Initialization, reset, snapshot roundtrip, validation |
| `test_ui_logic.py` | 5 | HP redirect logic, requirement tooltips |

### 8.2 Coverage Gaps

The following areas have no test coverage:

1. **`execute_choice` end-to-end.** The full pipeline of snapshot → resolve → apply → transition → record visit is untested.
2. **`merge_effects`.** Additive stat merging, item dedup, and flag override behavior are untested.
3. **`apply_morality_flags`.** The legacy flag sync is untested.
4. **`get_choice_warnings`.** Warning generation for irreversible/high-cost choices is untested.
5. **`apply_node_auto_choices`.** Auto-choice application and the `auto_choice::` flag marker system are untested.
6. **`simplify_story_nodes`.** The dedup, auto-apply extraction, and pruning pipeline is untested.
7. **Save/load integration.** Loading a snapshot and verifying full game state restoration is only partially tested (stat check only, not flags/traits/factions).
8. **Negative gold / negative HP edge cases.** No tests verify behavior when stats go below 0.
9. **Path map SVG generation.** No tests for the visualization logic or tooltip formatting edge cases.
10. **Epilogue generation.** No tests for the flag-driven aftermath text builder.

### 8.3 Test Infrastructure

- Tests use `unittest.TestCase` with a manual `setUp` that initializes session state.
- The `streamlit_compat` fallback works correctly for test isolation.
- `pytest.ini` correctly sets `pythonpath = .` for module resolution.
- No mocking framework is used. Tests operate directly on the fallback session state.

---

## 9. Bugs and Issues Found

### 9.1 Confirmed Bugs

| ID | Severity | Location | Description |
|----|----------|----------|-------------|
| B1 | Medium | `logic.py:50` | `transition_to(resolved_next)` uses the original `resolved_next` rather than `actual_next` from `_resolve_transition_node`. If a node is missing, `_record_visit` records the fallback while `transition_to` independently resolves the fallback, potentially diverging. |
| B2 | Low | `validation.py:64-80` | `_possible_stat_caps` computes global max gains without considering class-gated choices. All classes get the same inflated gain estimate, making stat-reachability checks overly permissive. |
| B3 | Low | `logic.py:199` | No stat floor enforcement. HP and gold can go negative through effects. While downstream logic handles `hp <= 0`, gold has no such safety net and can reach negative values. |

### 9.2 Design Concerns

| ID | Severity | Location | Description |
|----|----------|----------|-------------|
| D1 | Low | `content/story.py:16` | `simplify_story_nodes()` called at import time mutates the global `STORY_NODES` dict as a side effect. |
| D2 | Low | `content/constants.py:9` | `CHOICE_SIMPLIFICATION_REPORT` is a module-level mutable list that grows unboundedly. |
| D3 | Low | `node_view.py:109` | Choice overflow raises `RuntimeError`, crashing the app. A softer fallback would be more resilient. |
| D4 | Low | `path_map.py:130-131` | Node titles and choice labels are interpolated into SVG without escaping. Content-authored only, but violates defense-in-depth. |

---

## 10. Code Quality Metrics

### 10.1 Strengths

- **Type annotations** are used consistently across all function signatures.
- **Docstrings** are present on all public functions.
- **No dead code** — every function is called and every import is used.
- **Consistent naming conventions** — snake_case throughout, clear function names.
- **No external dependencies** beyond Streamlit and pytest.
- **Error messages are user-facing quality** — e.g., `"Missing item: {item}"`, `"Requires HP >= {min_hp}"`.

### 10.2 Weaknesses

- **No type definitions for content schemas.** Story nodes, choices, effects, and requirements are all `Dict[str, Any]`. TypedDict or dataclass definitions would catch schema errors at development time.
- **Magic strings.** Node IDs like `"death"`, `"failure_captured"`, flag names like `"any_branch_completed"` are scattered as string literals. Constants or enums would reduce typo risk.
- **No logging.** The application uses no Python logging. Debugging content issues in production requires reading Streamlit warnings on-screen.

---

## 11. Game Design Assessment

### 11.1 Narrative Structure: 8/10

- Three-act structure with rising stakes works well.
- Class-specific openings establish identity early.
- Quiet beat nodes (Ember Ridge Vigil, Breathing Stone) provide effective pacing contrast.
- The war council hub serves as a natural convergence point that rewards thorough exploration.
- Mini-bosses (Tidebound Knight, Pyre-Alchemist) add tactical variety to an otherwise choice-heavy flow.

### 11.2 Consequence Design: 9/10

- Flags carry across the entire game: early mercy/cruelty choices shape late-game options.
- The morality system (merciful/ruthless) gates distinct final-confrontation tactics.
- Skipped mini-bosses return as complications in the finale (e.g., "The Tidebound Knight you left alive crashes into the chamber").
- The epilogue system translates 30+ flags into personalized aftermath text.
- Irreversible choices with explicit warnings create meaningful weight.

### 11.3 Replay Value: 8/10

- Three classes with different stat profiles and exclusive choices.
- Faction alignment (Dawnwardens vs. Ashfang) creates distinct alliance paths.
- Morality branching opens different gate paths at the ruin and different finale tactics.
- 6+ distinct endings (best per-class, good, mixed, bad) encourage multiple playthroughs.
- Item-gated paths (Rope, Torch, Lockpicks, Bronze Seal, Warden Token, Ashfang Charm) reward thorough exploration.

### 11.4 Player Experience: 7/10

- The sidebar HUD provides clear state visibility.
- Locked choice display helps players understand what they're missing.
- The path map visualization is a good addition but limited to one-hop view.
- Undo system is well-implemented with irreversible checkpoints.
- The camp shop / village square loop for purchasing items is a clean preparation mechanic.

**Weakness:** The war council hub has up to 10 choices (before simplification), which can feel overwhelming. The choice simplification pipeline mitigates this, but the underlying content complexity at this node is high.

---

## 12. Summary Ratings

| Category | Rating | Notes |
|----------|--------|-------|
| Architecture | 8/10 | Clean separation, testable design, minor side-effect issues |
| Core Engine | 8/10 | Correct deterministic mechanics, minor transition logic inconsistency |
| Validation | 9/10 | Unusually thorough for project scale, minor stat-cap calculation issue |
| UI Layer | 7/10 | Functional and styled, SVG escaping gap, hard crash on overflow |
| Content Quality | 8.5/10 | Well-written, consistent tone, good flag design |
| Test Coverage | 6/10 | 19 passing tests but significant gaps in integration/edge cases |
| Game Design | 8/10 | Strong consequence system, good replay, solid pacing |
| **Overall** | **7.5/10** | A well-built foundation with clear paths for improvement |

---

## 13. Priority Recommendations

1. **Add TypedDict or dataclass schemas** for story nodes, choices, effects, and requirements. This would catch schema errors at development time and improve IDE support.
2. **Expand test coverage** to include `execute_choice`, `merge_effects`, auto-choices, simplification pipeline, and negative-stat edge cases.
3. **Fix the stat-cap calculation** in `validation.py` to account for class-gated choices, providing accurate reachability checks.
4. **Add stat floor clamping** in `apply_effects` (e.g., `max(0, stats[stat])` for gold) to prevent impossible negative values.
5. **Escape content strings in SVG generation** using `_escape_tooltip` on all interpolated values, not just tooltip text.
6. **Move the simplification call** out of import-time into an explicit initialization step.
7. **Add graph cycle detection** to the validator to catch unintended infinite loops in story content.
8. **Consider a multi-hop path map** that shows the broader story graph, not just immediate choices from the current node.
