# Plan: F21 — interactive Lean exercises (Issue #90)

## Design

- **ADR 011** (Proposed): stubs in `lean/Exercises/<Name>.lean`, in the existing
  Lake project but outside the library glob; solutions are library modules
  `PhysicsByConstruction.Exercises.<Name>`. No second Lake package (one Mathlib,
  one cache fetch); the ADR records why. I12 is narrowed to the library.
- **Pairing check** in `scripts/check-lean.sh`, after the axiom audit:
  `python -m pbc.authoring.exercises` requires, per stub, a solution module with
  the same theorems and the same statement text (comments and layout ignored),
  `sorry` in the stub and none in the solution, no solution without a stub.
  Each stub is then compiled; its only messages must be `sorry` warnings.
- **Build record** gains `exercises: {Exercises.<Name>: sha256}`.
- **Display.** `lean_stub(name, anchor)` renders a region of a stub in a
  `.not-verified` box, refusing a stub that changed after the check. The
  solution is shown with the existing `lean_excerpt`. Hints are the existing
  `.hint` divs (closed `details`, no JavaScript).
- **Content.** Lesson `lean/04-lean-exercises-on-your-machine`, format 2, three
  exercises (two of constant acceleration, one impulse/momentum), each with hints.

## Tests

- Unit (`tests/unit/test_lean_exercises.py`): statement extraction, every pairing
  failure, stub display, stale stub refused, repository stubs paired.
- Integration (`tests/integration/test_lean_check.py`): the check passes a paired
  stub and records it; fails without a solution; fails on a stub that does not compile.
- Existing lesson, e2e checks cover the new page (hints, not-verified markers).

## Docs

`docs/architecture.md` (layout, I12), `docs/project-map.md`,
`docs/decisions/011-*` and its index, `docs/authoring.md` (Lean exercises).

## Discoveries while implementing

- All three solutions are `subst` + `field_simp` + `ring`; the stub compiles
  with only `sorry` warnings. The Lean build adds about 3 s per solution module.
