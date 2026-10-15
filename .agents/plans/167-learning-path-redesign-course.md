# Plan — Issue #167 (F64): Learning Path redesign, course-first, compact, accessible

Rebuilds the page from the delivered F26, F27, F37, F41, F44, F13, F14 foundations; uses the F62 curriculum file and the F63 previews. No address changes, no new lesson.

## Steps

1. **Page generator** (`src/pbc/authoring/path.py`, `PathOverview`): order is courses, method paths, methods, difficulty, order, progress, dependency map. A course is a heading, a panel (description, count of published and planned, preview of the representative lesson, link to the first lesson) and a closed `<details>` with the lessons as rows. The representative lesson is the first lesson in teaching order that names its own `preview`, else the first lesson (rule in the code, `_representative`). Rows and planned slots are merged in the order of the curriculum file (`_ordered`); planned rows have no link and are not counted.
2. **Row**: thumbnail (F63 preview, alt text), title link, question (description), level badge, chips (simulation, experimental data, AI extensions) and a nested `details.lesson-details` with course, slot, methods, level, outcomes, prerequisites, related extensions, the classification of a slot whose kind is not `lesson` (T11, EM9, FL10 when published), and the reproduce link.
3. **Method paths and methods**: `ol.path-links`, one link per lesson to its canonical page; planned slots of a path as planned rows.
4. **Dependency map**: the whole graph under `details#dependency-map`; a course-scoped subset in each course (`PrerequisiteGraph.svg(scope=...)` prefixes every id so none repeats).
5. **Filters**: `nav.path-jump` links to every course, path, and method; `site/learner/path.js` adds a form (course, method, difficulty, publication) that hides rows, opens the course the address points into, and stores nothing. The search index is built from the page at render time, so it does not change.
6. **CSS** (`site/assets/site.css`): panel, compact rows, chips, planned rows; only the F44 tokens, no motion.
7. **Tests**: unit tests (`tests/unit/test_learning_path.py`, `tests/unit/test_curriculum.py`, `tests/unit/test_prerequisite_graph.py`); built-site tests (`tests/e2e/test_learning_path.py`) for each course and path with scripts disabled, the keyboard pass, 320 px, the filters. The payload, accessibility, determinism, link, and previous-address checks of the built site apply to the page unchanged.
8. **Docs**: `docs/architecture.md`, `docs/authoring.md`.

## Not done here

- Opening the current course without a script is not possible with native `<details>`; `path.js` does it with a script.
- The manual screen-reader pass and the visual review of criterion 8 need a browser and a human; they are recorded on the Issue by the human before the merge.
