# Plan: F68 advanced mechanics, M9 to M12 (Issue #168)

Source: Issue #168, docs/roadmap.md F68, docs/authoring.md "Lesson format 2".

## Decisions
- Four format 2 lessons in the `mechanics` strand, orders 13 to 16 (orders 1 to
  12 are taken; the slot, not the order, places them in the course): M9
  `double-pendulum-chaos`, M10 `lagrangian-mechanics`, M11
  `hamiltonian-mechanics`, M12 `resonance`.
- Code in `src/pbc/mechanics/`: `chaos.py` (double pendulum, Benettin Lyapunov
  estimate), `lagrangian.py` (Euler-Lagrange operator by central differences,
  momentum, energy, three Lagrangians), `hamiltonian.py` (Legendre transform,
  Jacobian of a step, phase-space area, modified energies), `resonance.py`
  (driven damped oscillator, analytic amplitude and phase, closed-form motion,
  measured resonance curve). No new dependency (no sympy).
- F45 has not landed: `resonance.py` owns the verified resonance reference
  solution; F45 reuses it.
- No new reference-register entries (they need human review): no go-deeper
  blocks. Outside prerequisites use existing glossary terms.
- M11 lists `symplectic-euler-conserved-energy` (L3) among its prerequisites
  (ADR 013 decision 8).

## Steps
1. chaos.py + tests (Lyapunov sign in regular and chaotic regimes, known
   exponent of a hyperbolic point).
2. lagrangian.py + tests (against the Newtonian form, normal modes, M9
   equations).
3. hamiltonian.py + tests (modified energy of M5 and L3, area, Jacobian).
4. resonance.py + tests (amplitude, phase, peak, closed form).
5. The four lessons.
6. Docs: roadmap status row, architecture mention if needed.
7. verify.sh.
