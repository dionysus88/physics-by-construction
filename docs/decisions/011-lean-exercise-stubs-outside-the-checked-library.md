# ADR 011: Lean exercise stubs live in `lean/Exercises/`, outside the checked library; their solutions are modules of the library

## Status

Proposed with the implementation of F21 (Issue #90); accepted when that pull
request is merged. Narrows invariant I12 to the checked library.

Date: 2026-10-10

## Context

An interactive Lean exercise gives the learner a theorem statement whose proof
is `sorry`, to be completed on their own machine. Invariant I12 says that Lean
proofs contain no `sorry`, and the check of `scripts/check-lean.sh` enforces it
on every module of `lean/PhysicsByConstruction/` (build, then the axiom audit).
A stub therefore cannot be a module of the library. The site must still show
the stub, its hints, and a checked solution, without running Lean in the
browser (the site has no runtime beyond static files; ADR 001), and a stub
must not drift from the solution it pairs with.

## Decision

1. **Stubs are in `lean/Exercises/<Name>.lean`.** The directory lies in the
   existing Lake project, next to but outside the library glob
   (`PhysicsByConstruction.+`), so `lake build` never compiles it into the
   library and the axiom audit, which imports library modules only, never sees
   its `sorry`. A learner opens `lean/` in their editor and runs
   `lake env lean Exercises/<Name>.lean` from there.
2. **Solutions are library modules.** The solution of a stub is
   `lean/PhysicsByConstruction/Exercises/<Name>.lean`: built by `lake build`,
   audited for `sorry` and axioms like every other proof, and displayed with
   `lean_excerpt`.
3. **A pairing check** runs inside `scripts/check-lean.sh`, after the audit
   (`python -m pbc.authoring.exercises`): every stub has a solution module with
   the same name; both state the same theorems with the same statement text
   (comments and layout ignored); the stub still contains `sorry` and the
   solution contains none; a solution without a stub is an error. Each stub
   also compiles, and its only messages are the `sorry` warnings.
4. **The record carries the stubs.** The build record of the check gains an
   `exercises` map from stub to checksum. A page shows a stub
   (`lean_stub`) only when the file is the one the check compiled, and shows it
   inside the "not verified" box with the statement that it proves nothing.
5. **I12 is narrowed**, not dropped: no `sorry`, `admit`, or project axiom in
   the checked library, and in `lean/` outside `Exercises/`. Only files of
   `lean/Exercises/` may contain `sorry`, and only as the proof of a theorem
   whose solution the library holds.
6. **No second Lake package.** One Lake project means one Mathlib checkout and
   one build cache fetch; the exercises add seconds to the Lean budget, not a
   second dependency resolution.

## Alternatives considered

**A second Lake package `lean-exercises/` requiring the first.** Rejected:
its own `lake-manifest.json` and `.lake/packages` mean a second clone of
Mathlib and a second cache fetch in every CI and every learner's setup, a
second set of pins (I10) to keep equal, and no benefit the directory outside
the library glob does not give. It can be adopted later if exercises need
their own dependencies.

**Stubs as the solution files with the proofs removed by a script at build
time.** Rejected: the stub the learner clones must exist in the repository
without a build, and a generated stub is a generated artifact (I6).

**Stubs inside the library, with `sorry` allowed by an allowlist in the audit.**
Rejected: it weakens the one check that guarantees the library has no
unproved theorem, and one mistake in the allowlist hides a real `sorry`.

**Verify the solution against the stub in Lean** (import both and compare the
types). Rejected for now: a stub is not a module that can be imported next to
its solution without name clashes. The text comparison fails on any change
of a statement, and the stub's compilation proves the statement is well-typed.
A statement that is textually equal can differ only through a changed
definition, which the library's own build catches.

## Consequences

Positive:

- The guarantee of I12 for the library is unchanged and still enforced by the
  same audit.
- Every stub has a solution that builds without `sorry`, and the site shows
  exactly the stub the check compiled.
- The learner needs nothing beyond the clone and the pinned toolchain.

Negative, with mitigations:

- A stub can compile and still be unprovable if its statement is false; the
  solution module, which proves the same text, rules that out.
- The statement comparison is textual; a layout-only difference passes and a
  semantic-preserving rewrite fails, which makes authors keep the two files
  alike, as intended.
- A learner can copy the solution from the repository; the page says the
  exercise is for the learner's own practice and marks hints and solution as
  separate steps.
