# Plan: F29 editorial pass, M1 to M4 (Issue #86)

Source: Issue #86, docs/roadmap.md F29 and F30, docs/authoring.md "Lesson format 2",
plan 57 (audit template) and plan 83.

One Issue for all four lessons, in the order M1, M2, M3, M4. Every
computation of the old lessons is kept; displayed results stay the same.

## Audit (before the rewrite)
M1 (format 2 since F28)
- Unsupported: "dropped terms add up to an error of size dt" (the count of steps
  is stated, not multiplied out); the sum behind x_n (n(n-1)/2) is not shown;
  assumption 5 "many orders of magnitude" is typed, not computed.
- Terse: "digit for digit"; the lag is not tied to the claim's evidence as a
  number in the prose.
M2
- Unmotivated: the exponential solution "as substitution confirms" (no
  substitution); position integral stated; "five per cent / less than one per
  cent" typed; Reynolds number < 1 for linear drag stated without source.
- Unsupported: instability limits 1 and 2 tau stated in prose of assumption 6 before
  derivation; the "same reason" claim for the spring (Euler feeds energy) is
  deferred without the algebra.
- Hand-typed numbers in prose, alt text (2 s, 0.5 factor, 1 ms, ...). Console
  blocks: seven. Captions descriptive. No limits, self-check, claim labels,
  figure status.
M3
- Unsupported: Reynolds range 1000 to 100 000 and the drag crisis; the
  interpolation bound (1/8) |y''| dt^2; the unstable step m/(c|v|) "about two
  seconds"; the "why the best angle is lower" explanation (the argument is
  hand-waving); Richardson formula stated.
- Hand-typed numbers and console blocks as in M2.
M4
- Unsupported: "the same algebra shows each step turns the point by
  arctan(omega dt)" (not shown); "about six steps per period, the energy
  doubles at every step" (omega dt = 1 gives factor 2, but 2 pi/1 = six steps);
  "10^-16 per step"; "about forty thousand steps" typed.
- Hand-typed numbers, console blocks, descriptive captions, no limits,
  self-check, claim labels, figure status.

## Guide gap
Recorded in the handoff note if any is found.

## Recorded by Claude, 2026-10-11

- The audit above was posted on Issue #86.
- The worktree was brought up to date with main, which repairs the M6 self-check label (pull request #96) that made site-checks fail here.
- Still for the owner: open the register entry `drag-coefficient-regimes`; it was read through a summary only.
