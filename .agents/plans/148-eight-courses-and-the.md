# Plan — Issue #148 (F62): eight courses and the reference curriculum

Implements ADR 013. Short plan: the file schema, the migration, the page sections.

## The curriculum file (`site/curriculum.yaml`)

- `courses` (the eight of `COURSES`, checked equal), `paths` (four: `reasoning`,
  `law-discovery`, `benchmarking`, `autonomous-research`), `slots` (115, one line
  each, in teaching order; generated once from the roadmap's "Slot mapping").
- A slot has `label`, `title`, `kind` and exactly one home: `course`, `path` (with
  `position`, 1.. in file order), or `strand` (only the Lean slot L1, home `lean`).
- `pbc.authoring.path.curriculum_problems` rejects an unknown course or path, a
  duplicate label, a slot without a home or with two, and any front-matter field.

## Code

- `COURSES` (eight), `STRANDS` (courses first, then `agents-llm`, `agents-abm`,
  `lean`), `Lesson.slot`, `Curriculum`, `LearningPath.curriculum`.
- `problems(lessons, curriculum)`: unknown or duplicate slot, a slot of another
  course; prerequisite rule of decision 8 (same strand earlier, cycles anywhere).
- Course and path views in slot order (`in_course`, `in_path`, `taught`);
  `planned_in_course`, `planned_in_path`, `planned_courses`.
- Path page: planned slots (no link, no card, not counted), "Method paths"
  section between courses and methods, one sentence naming courses without a
  lesson, explanation of previous and next updated. Header: Slot row.
  `path.json`: `slot`, `path`, `position`. Home page: planned list derived from
  the file with published counts (`PLANNED` removed).

## Migration

17 published lessons get `slot` in front matter only (M1-M8, M16, AI0, AI2, AI3,
AI4, D6, D9, R1, L1). The gas lesson (F70) and the four Lean lessons beyond the
baseline get none.

## Tests

`tests/unit/test_curriculum.py` (counts, schema, slot rules, prerequisite
fixtures including T0 to T2, page sections, header); updated unit tests of the
path, home, and export; e2e tests of the path page and home page.
