# Roadmap

Project direction for Physics by Construction, derived from the approved
`docs/PROJECT_REQUIREMENTS.md` (approved 2026-10-06, re-approved on
2026-10-09 with the change request `docs/changes/physics-next-phase.md`
and on 2026-10-12 with the change request
`docs/changes/final-curriculum.md`) and consistent with
`docs/architecture.md` and ADRs 001 to 014.

Keep this high-level. GitHub Issues are the actionable backlog and the source
of truth for a feature once its Issue exists. Each feature below has a stable
ID; `./scripts/create-feature-issue.sh <ID>` copies its block into an Issue.
Detailed implementation plans are written just in time under `.agents/plans/`
when a feature becomes active, not here.

This roadmap does not choose which feature is active. It records dependencies;
the human picks the next feature among those whose dependencies are done.
Review the later-phase features against the current architecture before
starting them.

## State at the change cycle `physics-next-phase`

Checked on 2026-10-09 at the base commit `2f011ea` of the planning branch
`planning/physics-next-phase`:

- **F01 to F12 are delivered, F10 pending the human release steps.** Their
  pull requests are merged and the site publishes eleven lessons in four
  strands. The Issues of F01 to F09, F11, and F12 (#3, #7, #12, #15, #18,
  #21, #23, #25, #24, #30, #31) are closed. F10's Issue #29 was closed on
  GitHub on 2026-10-09, as read when this revision was written, although
  `docs/release-readiness.md` expects it to stay open until the release tag
  exists; no release tag and no GitHub release existed on that date, so
  F10's criterion 7 (a release tag for the MVP) is still open. The remaining
  items are the human steps recorded in `docs/release-readiness.md`: the tag
  (`mvp-v1.0.0` on the merge commit), the release note, and the follow-up
  Issues for the two accessibility observations and the style differences.
  Those steps are not roadmap features; the features that depend on F10
  need its delivered site and audit, not the tag. Two deferred review
  findings are open as Issues #8 and #34.
- **F13, F14, and F15 have no Issue.** Their blocks below are unchanged by
  the change cycle; the next-phase features that touch the same ground (F28
  self-checks, F38 hints, F26 and F27 on the path page, F15's course topic)
  name them as neighbours instead of widening them.
- **The MVP blocks F01 to F12 are records**, kept as they were approved and
  delivered. A feature that changes what one of them delivered is a new
  feature below that names it as a dependency.

**Feature IDs of the change cycle.** The change request discussed candidates
F16 to F56. Where a candidate became a feature, it keeps its candidate number
as its final ID, so that the discussion history stays traceable. The numbers
of candidates that were merged into another feature or deferred (F24, F48)
are retired and are never assigned to anything else. Features the change
cycle adds without a candidate number take the next unused IDs from F57
onward. The section "Candidate mapping" records every candidate's outcome.

## State at the change cycle `final-curriculum`

Checked on 2026-10-12 at the base commit `0580b3a` of the planning branch
`planning/final-curriculum`, against the repository, `gh issue list
--state all`, and `gh pr list --state all`. This is the reconciliation
report that section 9 of `docs/changes/final-curriculum.md` asks for; the
files are the truth, this section is their summary at that commit.

### Published lessons and their slots

Twenty-two lessons are published, all with `course: mechanics`, in the
four strands. The slot labels are the curriculum labels of the change
request (ADR 013); eighteen lessons fill a slot (seventeen take their
`slot` in F62, the gas lesson T0 in F70 together with its course) and four
are Lean lessons beyond the one Lean slot of the baseline.

| Lesson directory under `site/lessons/` | `id` | Strand, order | Methods | Feature | Slot |
|---|---|---|---|---|---|
| `mechanics/01-kinematics-as-a-program` | `kinematics` | mechanics 1 | simulation | F02 | M1 |
| `mechanics/02-newtons-laws` | `newtons-laws` | mechanics 2 | simulation | F04 | M2 |
| `mechanics/03-projectile-motion-with-drag` | `projectile-with-drag` | mechanics 3 | simulation | F04 | M3 |
| `mechanics/04-harmonic-oscillator` | `harmonic-oscillator` | mechanics 4 | simulation | F05 | M4 |
| `mechanics/05-numerical-integrators` | `numerical-integrators` | mechanics 5 | simulation | F05 (editorial F30) | M5 |
| `mechanics/06-energy-conservation` | `energy-conservation` | mechanics 6 | simulation | F06 | M6 |
| `mechanics/07-momentum-and-collisions` | `momentum-and-collisions` | mechanics 7 | simulation | F06 | M7 |
| `mechanics/08-kepler-orbit` | `kepler-orbit` | mechanics 8 | simulation | F06 | M8 |
| `mechanics/09-verifying-scientific-code` | `verifying-scientific-code` | mechanics 9 | simulation | F46 | AI2 (physics reasoning path; a mechanics lesson, no agent) |
| `mechanics/10-automated-analysis-pipelines` | `automated-analysis-pipelines` | mechanics 10 | simulation, measured-data | F47 | R1 (autonomous research path) |
| `mechanics/11-gravitational-wave-strain` | `gravitational-wave-strain` | mechanics 11 | measured-data, simulation | F60 | M16 (designated lab; primary home mechanics) |
| `mechanics/12-inverse-physics-parameter-discovery` | `inverse-physics` | mechanics 12 | simulation, measured-data | F23 | D6 (law discovery path) |
| `agents-llm/01-an-agent-runs-an-experiment` | `agent-experiment` | agents-llm 1 | simulation, llm-agents | F09 | AI0 |
| `agents-llm/02-a-counterexample-hunter` | `counterexample-hunter` | agents-llm 2 | simulation, llm-agents | F16 | AI3 |
| `agents-llm/03-three-reviewers` | `scientific-review` | agents-llm 3 | simulation, llm-agents | F18 | AI4 |
| `agents-llm/04-an-experimental-design-agent` | `experimental-design-agent` | agents-llm 4 | simulation, llm-agents | F20 | D9 (law discovery path) |
| `agents-abm/01-particles-in-a-box` | `particles-in-a-box` | agents-abm 1 | simulation, abm | F11 | T0; no `slot` until F70 sets `slot: T0` and `course: thermodynamics` together (ADR 013 decision 6); address unchanged |
| `lean/01-proving-what-the-simulation-showed` | `proving-what-the-simulation-showed` | lean 1 | lean | F08 | L1 |
| `lean/02-momentum-in-a-collision-proved` | `collision-momentum-proved` | lean 2 | lean | F17 | none: beyond the baseline |
| `lean/03-what-symplectic-euler-conserves` | `symplectic-euler-conserved-energy` | lean 3 | lean | F17 | none: beyond the baseline |
| `lean/04-lean-exercises-on-your-machine` | `lean-exercises-on-your-machine` | lean 4 | lean | F21 | none: beyond the baseline |
| `lean/05-the-chirp-law-proved` | `chirp-law-proved` | lean 5 | lean | F56 | none: beyond the baseline |

Three lessons (`counterexample-hunter`, `scientific-review`,
`experimental-design-agent`) declare no `format`; the format-2 default
flip of F28 is still pending for them and is not a concern of this change.

### Count reconciliation

| Count | Value |
|---|---|
| Reference curriculum (requirements decision 23) | 115 slots: 81 Part A, 33 Part B, 1 Lean |
| Published lessons at `0580b3a` | 22 |
| Published lessons that fill a slot | 18: M1 to M8, M16, T0, AI0, AI2, AI3, AI4, D6, D9, R1, L1; 17 carry `slot` from F62, T0 from F70 with its course |
| Published lessons beyond the baseline | 4 Lean lessons (F17, F21, F56); kept, mapped, never deleted or hidden |
| Slots to fill | 97, of which 6 belong to features that exist without an Issue (AI1 F45, AI5 F55, R4 F49, W7 F52, FL7 F53, EM7 F54) and 91 to the new features of Phase 4 |
| Lessons when the reference curriculum is complete | 119: 115 slots plus the 4 Lean lessons beyond the baseline, plus any further Lean lesson of F22 |
| Designated measured-data labs | 16 (M15, M16, T7, T8, W7, W8, EM7, EM8, FL7, FL8, Q7, Q8, AST8, AST9, MAT5, MAT6); 1 published (M16), 3 with existing features (W7, FL7, EM7), 12 new features |
| Datasets with a go decision | 3 (GW150914 strain, used; Aalborg wave flume, for W8; NPL S-parameters, for EM7) |

115 stays the reference structure (requirements decision 23). The
historical baseline of the change request (11 published, 104 future)
counted one Lean lesson and no agent, pipeline, lab, or inverse-physics
lesson; the actual inventory is reported above and no published lesson is
rebuilt to match a count.

### Features of the previous phases: state and role in the final curriculum

Every feature F01 to F60 keeps its block as approved; the blocks are
history. "Delivered" means the Issue is closed and the pull request
merged. The slot column is the mapping that section 9, point 3, of the
change request asks for; no feature's scope is duplicated.

| Feature, Issue | State at `0580b3a` | Role in the final curriculum |
|---|---|---|
| F01 to F09, #3 to #25 | Delivered | The site, the lesson format, M1 to M8, L1, AI0. |
| F10, #29 | Delivered; release tag still a human step | None. |
| F11, #30 | Delivered | T0 of the thermodynamics course, re-homed by front matter in F70, which sets `course` and `slot` together (ADR 013 decision 6); no slot before F70. |
| F12, #31 | Delivered | The content workflow every lesson feature uses. |
| F13, #89; F14, #94 | Delivered | Progress marks and recommendations that F64 keeps on the redesigned path. |
| F15, no Issue | Not started; **dropped by `final-curriculum`** (ADR 013 decision 7) | Its goal is delivered by F62 and the first lesson feature of each course (F70, F71, F72, F73, F89, F91, F94); its ID is never reused. |
| F16, #87 | Delivered | AI3. |
| F17, #61 | Delivered | Two Lean lessons beyond the baseline (L2, L3). |
| F18, #88 | Delivered | AI4; its reviewers are reused by F110 and F111. |
| F19, #111 | Delivered | The evidence map page; the R2 lesson that teaches it is F109. |
| F20, #128 | Delivered | D9, with the revision-2 enhancement (hypothesis-discriminating information gain) already in its design and judging; no new feature. |
| F21, #90 | Delivered | A Lean lesson beyond the baseline (L4). |
| F22, no Issue | Not started; unchanged | A Lean strand lesson outside the 115 slots; kept as approved. |
| F23, #120 | Delivered | D6, with the revision-2 enhancement (identifiability, parameter correlations, held-out uncertainty) delivered by its fitting helpers and page; no new feature. |
| F25 to F44, Issues #41 to #60, #83 to #86, #99 to #112, and #121 | Delivered | The visual system, metadata, graph, cards, format 2, search, diagrams, and components that F62 to F64 build on without reopening. |
| F45, no Issue | Not started; unchanged | AI1; coordinates with M12 of F68 on the resonance reference solution. |
| F46, #62 | Delivered | AI2 (a mechanics lesson without an agent, in the physics reasoning path). |
| F47, #123 | Delivered | R1. |
| F49, no Issue | Not started; unchanged | R4. |
| F50, #51 | Delivered | The gate every new lab and F88's comparison pass; its process is reused, the Issue is not reopened. |
| F51, #102 (follow-up #115) | Delivered | The shared analysis core of every lab. |
| F52, no Issue | Not started; unchanged | W7; its course is `waves`, created by F71 (reconciled note in its block). |
| F53, no Issue | Not started; unchanged | FL7; its course is `fluids`, created by F73. |
| F54, no Issue | Not started; unchanged | EM7; its course is `electromagnetism`, created by F72; its dataset has a go decision. |
| F55, no Issue | Not started; unchanged | AI5. |
| F56, #129 | Delivered | A Lean lesson beyond the baseline (L5). |
| F57, #49; F59, #101 | Delivered | Identity and the instructor pack; unchanged. |
| F58, #130 (follow-up #138 open) | Delivered | The parallel jobs F61 builds on. |
| F60, #122 | Delivered | M16. |

Retired IDs F24 and F48 stay retired. The seven enhancements of existing
slots named in revision 2 are recorded under "Slot mapping" below: two
are delivered (D6 by F23, D9 by F20), and five belong to the features that
create their slots (AI6 in F96, EV1 in F100, EV2 in F81, R5 in F110, and
the linked Q5/Q8 pair in F90 and F103); none adds a slot.

### Architecture decisions of this change cycle

- **ADR 013** allows all eight courses with fixed identifiers, makes every
  course a strand with the same identifier created by its first lesson
  feature, declares the reference curriculum as data that lessons fill by
  `slot`, derives the four method paths from the slot, validates the
  prerequisite graph as a graph while previous and next stay the reading
  route (a prerequisite may live in a later strand), and reconciles F15
  as dropped. It supersedes decision 4 of ADR 008 and amends its decisions
  1, 3, and 5; every published address, identifier, and link stays.
- **ADR 014** makes a pull request verify what it changed against the
  verified result of `main`, which is restored and never committed, with
  `main` verifying everything; the navigation and the commit a page shows
  are regenerated on every build, and a check is reused only from a base
  the same check implementation produced; a lesson whose inputs cannot be
  followed, a changed shared input, or changed checks make the run a full
  run, and a full run executes the lessons in same-machine lesson shards
  that one assembly turns into the one built site, so that every job fits
  the timeout at 110 lessons. It amends ADR 002 and ADR 012 and is the
  record that ADR 003 decision 6 and ADR 012 decision 8 require. F61
  delivers the selection, with F62, before the first lesson feature of
  this phase; F113 delivers the lesson shards before the lesson count
  passes the lesson-shard size.

No accepted ADR conflicts with the re-approved requirements; ADR 008's
single-additional-course rule is the one decision the requirements asked
to supersede, and ADR 013 does it.

## Overview

Phases: Phase 1 is the MVP; Phase 2 is the work the requirements placed
after the MVP; Phase 3 is the change cycle `physics-next-phase`, ordered in
waves R0 to R5 by dependency; Phase 4 is the change cycle
`final-curriculum`, ordered in waves C0 to C4 (see "Execution order"). A
wave is a suggested grouping, not a gate: a feature may start when its
dependencies are done. The gates of Phase 4 (F61 and F62 before every
lesson feature of the phase, F64 before the lesson features of waves C2 to
C4) are dependencies, listed in the table and in each block.

| ID | Feature | Phase | Depends on | Risk |
|---|---|---|---|---|
| F01 | Published site skeleton with the full verification pipeline | 1, delivered | none | High |
| F02 | Lesson format and the first mechanics lesson | 1, delivered | F01 | Medium |
| F03 | Learning path | 1, delivered | F02 | Medium |
| F04 | Mechanics lessons: Newton's laws and projectile motion with drag | 1, delivered | F02 | Medium |
| F05 | Mechanics lessons: the harmonic oscillator and numerical integrators | 1, delivered | F04 | Medium |
| F06 | Mechanics lessons: energy, momentum, and a capstone orbit | 1, delivered | F03, F05 | Medium |
| F07 | Interactive visualizations | 1, delivered | F05 | Medium |
| F08 | Formal proofs strand: first Lean lesson | 1, delivered | F03, F05 | Medium |
| F09 | LLM agents strand: first agent-driven experiment lesson | 1, delivered | F03, F04 | High |
| F10 | MVP release readiness and launch | 1, delivered (release tag pending) | F01 to F09 | Medium |
| F11 | Agent-based modelling strand: first lesson | 2, delivered | F03, F06 | Medium |
| F12 | Content proposal workflow through GitHub Issues | 2, delivered | F10 | High |
| F13 | Self-check quizzes and browser-local progress | 2 | F03, F07, F10 | Medium |
| F14 | Adaptive recommendations | 2 | F13 | Medium |
| F15 | Second course on the three-pillar path | 2, dropped by `final-curriculum` (ADR 013) | F10 | Medium |
| F58 | Parallel verification jobs behind one required check | 3, R0 | F10 | High |
| F44 | Visual design and accessibility system | 3, R1 | F10 | Medium |
| F57 | Open-source identity, attribution, and citation | 3, R1 | F10, F12 | Medium |
| F25 | Homepage narrative: Construct, Investigate, Verify | 3, R1 | F57 | Low |
| F37 | Lesson metadata and course navigation | 3, R1 | F10, F12 | Medium |
| F26 | Generated prerequisite graph | 3, R1 | F37 | Medium |
| F27 | Learning path cards and the difficulty scale | 3, R1 | F37, F44 | Low |
| F35 | Code explanation: annotated excerpts | 3, R1 | F10 | Low |
| F36 | Numeric results as semantic tables | 3, R1 | F10 | Low |
| F28 | Lesson format 2, the reference register, and the M1 pilot | 3, R1 | F37, F44, F35, F36 | Medium |
| F30 | Editorial pass M5 to M8, with M5 as the research-backed pilot | 3, R1 | F28 | Medium |
| F29 | Editorial pass M1 to M4 | 3, R1 | F28, F30 (the M5 pilot reviewed) | Medium |
| F39 | Unified local setup, run recipes, and the link maintenance check | 3, R1 | F10 | Low |
| F50 | Experimental dataset registry and feasibility gate | 3, R3 (may start beside R1) | F10 | Medium |
| F42 | Before you begin, and the glossary | 3, R2 | F37, F28 | Low |
| F38 | Progressive hints in exercises | 3, R2 | F28 | Low |
| F40 | Reproducibility UX | 3, R2 | F28 | Low |
| F41 | Self-hosted search | 3, R2 | F37 | Medium |
| F31 | Agent and Lean editorial pass | 3, R2 | F28, F30 | Medium |
| F32 | Mechanics diagrams M1 to M4 | 3, R2 | F29 | Low |
| F33 | Mechanics diagrams M5 to M8 | 3, R2 | F30 | Low |
| F34 | Agent and Lean diagrams | 3, R2 | F31 | Low |
| F45 | Agent-assisted simulation development | 3, R2 | F10 | High |
| F46 | Scientific code verification and debugging | 3, R2 | F10 | Medium |
| F16 | Counterexample hunter | 3, R2 | F09, F46, F28 | Medium |
| F17 | Further Lean mechanics proofs | 3, R2 | F08, F28 | Medium |
| F59 | Instructor pack for one published lesson | 3, R2 | F57, F30 | Low |
| F51 | Experimental methods and visualization foundations | 3, R3 | F50 (a go decision), F28 | Medium |
| F60 | Gravitational-wave strain lab: from Kepler's orbit to a chirp | 3, R3 | F51, F06 | Medium |
| F43 | Science-first visualization components | 3, R3 | F07, F51 | Medium |
| F54 | Microwave S-parameter lab | 3, R4 | F51, a course for the lab (F72 since `final-curriculum`; see the block) | Medium |
| F53 | Flow measurement lab with PIV fields | 3, R4 | F51, F43, a course for the lab (F73 since `final-curriculum`; see the block) | Medium |
| F52 | Optical diffraction lab | 3, R4 | F51, F43, a course for the lab (F71 since `final-curriculum`; see the block) | Medium |
| F55 | Agent-assisted experimental physics | 3, R4 | F45, one of F60 or F54 | Medium |
| F23 | Inverse physics: parameter discovery with uncertainty | 3, R4 | F51, one of F60 or F54 | Medium |
| F47 | Automated analysis pipelines | 3, R4 | F51 | Medium |
| F18 | Multi-agent scientific review | 3, R4 | F09, F46 | Medium |
| F19 | Scientific evidence map | 3, R4 | F28, F29, F30, F31, F37 | Low |
| F56 | Lean proofs for the models of measured-data labs | 3, R4 | F17, F54 | Medium |
| F20 | Autonomous experimental design | 3, R5 | F16, F23 | Medium |
| F21 | Interactive Lean exercises | 3, R5 | F17 | Medium |
| F22 | Agent-assisted theorem proving | 3, R5 | F21, F45 | High |
| F49 | Research capstone: reproduce an open physics paper with a multi-agent team | 3, R5 | F18, F45, F46, F47 | High |

Retired candidate numbers: F24 (optional local tutor, deferred) and F48
(paper reproduction, absorbed into F49). See "Candidate mapping".

Phase 4, the change cycle `final-curriculum` (2026-10-12). The slots are
the curriculum labels of `docs/changes/final-curriculum.md`; the full
mapping is under "Slot mapping".

| ID | Feature | Wave | Slots | Depends on | Risk |
|---|---|---|---|---|---|
| F61 | Verification proportional to the change | C0 | none | F58 | High |
| F113 | Bounded full verification: same-machine lesson shards of the build | C0 | none | F61, F58 | High |
| F62 | Eight courses and the reference curriculum | C0 | none (migrates 17 published lessons; T0 by F70) | F03, F37, F26, F27, F25 | Medium |
| F63 | Verified lesson previews | C0 | none | F62, F28, F44 | Medium |
| F64 | Learning Path redesign: course-first, compact, accessible | C0 | none | F62, F63, F26, F27, F37, F41, F44, F13, F14 | Medium |
| F65 | Physics environments and the discovery evaluation protocol | C1 | none | F09, F16, F20, F23, F46 | Medium |
| F66 | Law discovery lessons: black-box force laws | C1 | D1, D2, D3 | F61, F62, F113 by the lesson-shard rule, F65 | Medium |
| F67 | Symbolic regression and equation discovery | C1 | D7, D8 | F61, F62, F113 by the lesson-shard rule, F65, F23 | Medium |
| F68 | Advanced mechanics: chaos, Lagrangian and Hamiltonian mechanics, resonance | C1 | M9, M10, M11, M12 | F61, F62, F113 by the lesson-shard rule, F05, F06 | Medium |
| F69 | Mechanics: many-body gravitation, nonlinear dynamics, rotational motion | C1 | M13, M14, M17 | F61, F62, F113 by the lesson-shard rule, F68, F06 | Medium |
| F70 | Thermodynamics: random walks, kinetic theory, entropy | C1 | T1, T2, T3 (and T0 re-homed) | F61, F62, F113 by the lesson-shard rule, F11, F06 | Medium |
| F71 | Waves and optics: the wave equation, interference, sound | C1 | W1, W2, W9 | F61, F62, F113 by the lesson-shard rule, F05 | Medium |
| F72 | Electromagnetism: fields, charged particles, induction | C1 | EM1, EM2, EM3 | F61, F62, F113 by the lesson-shard rule, F06 | Medium |
| F73 | Fluid dynamics: advection, Burgers, finite volumes, shallow water | C1 | FL1, FL4, FL9, FL5 | F61, F62, F113 by the lesson-shard rule, F05, F06 | Medium |
| F74 | Wave flume lab | C1 | W8 | F61, F62, F113 by the lesson-shard rule, F71, F51, F43 | Medium |
| F75 | Thermodynamics: Ising model, molecular dynamics, heat engines | C2 | T4, T5, T9 | F61, F62, F64, F113, F70 | Medium |
| F76 | Heat conduction and the finite-element bridge | C2 | T6, T10 | F61, F62, F64, F113, F70 | Medium |
| F77 | Optics: refraction, polarisation, diffraction, inverse optics | C2 | W3, W4, W5, W6 | F61, F62, F64, F113, F71 | Medium |
| F78 | Electromagnetism: Maxwell's equations and FDTD, RLC circuits, waveguides | C2 | EM4, EM5, EM6 | F61, F62, F64, F113, F72, F71 | Medium |
| F79 | Fluid dynamics: Navier-Stokes, vortex shedding, particle-based fluids | C2 | FL2, FL3, FL6 | F61, F62, F64, F113, F73 | Medium |
| F80 | Applied capstone: adaptive phased-array beam steering | C2 | EM9 | F61, F62, F64, F113, F78, F71 | Medium |
| F81 | Interactive discovery benchmarks and non-agent baselines | C2 | EV2, EV3 | F61, F62, F64, F113, F65, F66, F67 | Medium |
| F82 | Discovering conservation laws and invariants | C2 | D13 | F61, F62, F64, F113, F65, F67, F69 | Medium |
| F83 | Pendulum and accelerometer data lab | C2 | M15 | F61, F62, F64, F113, F51, F68 | Medium |
| F84 | Heat transfer measurements lab | C2 | T7 | F61, F62, F64, F113, F76, F51 | Medium |
| F85 | Brownian motion tracking lab | C2 | T8 | F61, F62, F64, F113, F70, F51 | Medium |
| F86 | RLC circuit measurements lab | C2 | EM8 | F61, F62, F64, F113, F78, F51 | Medium |
| F87 | Applied capstone: thermal engineering of a hypothetical AI accelerator | C3 | T11 | F61, F62, F64, F113, F76 | Medium |
| F88 | Applied capstone: reconstructing the 2025 Kamchatka tsunami | C3 | FL10 | F61, F62, F64, F113, F73, F51 | High |
| F89 | Quantum physics: the Schrödinger equation, tunnelling, the harmonic oscillator | C3 | Q1, Q2, Q3 | F61, F62, F64, F113, F05, F71 | Medium |
| F90 | Quantum physics: spin, entanglement and Bell inequalities, open systems | C3 | Q4, Q5, Q6 | F61, F62, F64, F113, F89 | Medium |
| F91 | Astrophysics: the three-body problem, modified gravity, lensing | C3 | AST1, AST2, AST3 | F61, F62, F64, F113, F69 | Medium |
| F92 | Relativity and cosmology: special relativity, relativistic orbits, cosmic expansion | C3 | AST10, AST4, AST5 | F61, F62, F64, F113, F91 | Medium |
| F93 | Gravitational-wave chirp and exoplanet transit simulations | C3 | AST6, AST7 | F61, F62, F64, F113, F91, F60 | Medium |
| F94 | Materials physics: crystal lattices and phonons, electronic band structure | C3 | MAT1, MAT2 | F61, F62, F64, F113, F71, F89 | Medium |
| F95 | Materials physics: elasticity and deformation, defects | C3 | MAT3, MAT4 | F61, F62, F64, F113, F94, F76 | Medium |
| F96 | Multimodal physics reasoning and interpretable explanations | C3 | AI6, AI7 | F61, F62, F64, F113, F09, F46, F65 | Medium |
| F97 | Physical reasoning from video | C3 | AI8 | F61, F62, F64, F113, F96, F06 | Medium |
| F98 | Discovery under noise, hidden variables, and generalisation | C3 | D10, D11, D12 | F61, F62, F64, F113, F66, F81 | Medium |
| F99 | Discovering gravity and unknown physical worlds | C3 | D4, D5 | F61, F62, F64, F113, F66, F69, F91 | Medium |
| F100 | Physics reasoning benchmarks | C3 | EV1 | F61, F62, F64, F113, F96, F65 | Medium |
| F101 | Robustness, cost, and scientific failure analysis | C3 | EV4, EV5 | F61, F62, F64, F113, F81, F98 | Medium |
| F102 | Atomic spectroscopy lab | C3 | Q7 | F61, F62, F64, F113, F89, F51 | Medium |
| F103 | Quantum measurement statistics lab | C3 | Q8 | F61, F62, F64, F113, F90, F51 | Medium |
| F104 | Exoplanet light curves lab | C3 | AST8 | F61, F62, F64, F113, F93, F51 | Medium |
| F105 | Galaxy rotation curves lab | C3 | AST9 | F61, F62, F64, F113, F91, F51 | Medium |
| F106 | X-ray diffraction data lab | C3 | MAT5 | F61, F62, F64, F113, F94, F51 | Medium |
| F107 | Stress-strain measurements lab | C3 | MAT6 | F61, F62, F64, F113, F95, F51 | Medium |
| F108 | Turbulence and flow measurements lab | C3 | FL8 | F61, F62, F64, F113, F79, F53, F51 | Medium |
| F109 | Evidence maps and reproducible literature evidence | C4 | R2, R3 | F61, F62, F64, F113, F19, F39, F28 | Medium |
| F110 | Agent-driven materials discovery | C4 | R5 | F61, F62, F64, F113, F95, F18, F20 | Medium |
| F111 | Autonomous physics research challenge | C4 | R6 | F61, F62, F64, F113, F49, F101, F98, F65 | High |
| F112 | Curriculum completion audit | C4 | none | every scheduled lesson feature, F64 | Low |

The features of the previous phase without an Issue keep their IDs and
blocks and fill these slots when their dependencies are met: F45 (AI1),
F55 (AI5), F49 (R4), F52 (W7, after F71), F53 (FL7, after F73), F54 (EM7,
after F72); F22 stays a Lean strand feature outside the slots. Each of
them publishes a lesson in this phase and therefore starts after F61 and
F62, and after F113 under the full-run gate, like every lesson feature of
the phase (the gates under "Phase 4"); their blocks are not rewritten, the
gate is this rule. F15 is dropped.

Risk levels follow `.agents/policies/autonomy.md`. Every feature that adds a
lesson is at least Medium, because physics and proof content needs independent
review, not only passing checks. Features that change CI, repository
settings, legal text, or let an agent write code are High.

## Product structure

From the requirements (decision 15) and ADR 008. The site has three facets,
all derived from lesson front matter; there is no second list.

| Facet | Content | Today | Next phase |
|---|---|---|---|
| **Physics courses** (by subject) | Mechanics. Later candidates: waves and optics (bridged by the wave-flume and optics datasets), Lagrangian and Hamiltonian mechanics, statistical physics, electromagnetism, fluid dynamics. | One course, implicit | `course` in every lesson (F37); a second course only through F15 with the human's explicit choice. F15 yields one course. A measured-data lab whose subject F15 does not choose waits for a later course feature, which takes the next unused ID when the human asks for it; the only other route is a `mechanics` framing its Issue justifies under ADR 008 decision 3. **Since `final-curriculum` (ADR 013):** the eight courses `mechanics`, `thermodynamics`, `waves`, `electromagnetism`, `fluids`, `quantum`, `astrophysics`, `materials` with fixed identifiers, each a strand with the same identifier created by its first lesson feature (F70, F71, F72, F73, F89, F91, F94); the reference curriculum in the curriculum file, filled by `slot` (F62); F15 dropped; a lab's home is its subject's course, and the `mechanics` framing of a lab of another subject is no longer a route. |
| **Methods** (cross-cutting, not subjects) | Simulation, LLM agents in the harness, agent-based modelling, formal verification in Lean, measured data, coding agents on the learner's machine. | Four strands in one linear path | `methods` tags, one method path per method on the learning-path page, related-lesson links (F37); no method becomes a course. |
| **Strands** (URL groups and ordering) | `mechanics`, `agents-llm`, `agents-abm`, `lean`. | Unchanged | Unchanged identifiers and addresses; display titles may be refined (for example "AI-assisted research" for `agents-llm`). A measured-data lab of the mechanics course takes the next order in the `mechanics` strand; a lesson about a method lives in that method's strand. No lesson is placed by a method tag alone (ADR 008 decision 4). **Since `final-curriculum` (ADR 013):** one strand per course in curriculum order, then the three method strands; the lessons of the four method paths live in `agents-llm`. |
| **Method paths** (since `final-curriculum`, ADR 013) | Physics reasoning and scientific agents (AI0 to AI8), scientific law discovery (D1 to D13), physics agent benchmarking (EV1 to EV5), autonomous scientific research (R1 to R6). | Not shown; six published lessons belong to them | A facet of the slot: a secondary view of the path page over the same canonical pages (F62, F64); never a course, a strand, or a page of its own. |

Rules that follow: a lab belongs to one primary course and links to its
agent, measured-data, and Lean extensions instead of being duplicated; no
lesson asserts that every experiment has an LLM or Lean counterpart; the
dataset survey (Appendix A of the change request) adds no course and no
strand; a web gallery of verified experiments (F43, F51) is a presentation,
not a strand.

## MVP lesson list

The requirements leave the exact lesson list to planning. The MVP has ten
lessons: eight in the mechanics strand, one LLM agent lesson, and one Lean
lesson. Changing this list is a roadmap change.

| # | Strand | Lesson | Feature |
|---|---|---|---|
| M1 | mechanics | Kinematics as a program: state, time step, explicit Euler, comparison with the closed form, error convergence | F02 |
| M2 | mechanics | Newton's laws as a first-order system: force models, a generic stepper, falling with linear drag against its analytic solution | F04 |
| M3 | mechanics | Projectile motion with quadratic drag: no closed form, validation by limiting cases and convergence, range against launch angle | F04 |
| M4 | mechanics | The harmonic oscillator: exact solution, phase space, what explicit Euler does to its energy | F05 |
| M5 | mechanics | Numerical integrators: explicit Euler, symplectic Euler, velocity Verlet, Runge-Kutta 4; order, stability, cost | F05 |
| M6 | mechanics | Energy conservation: work and energy, energy drift as a diagnostic, the pendulum at large amplitude | F06 |
| M7 | mechanics | Momentum conservation and collisions: pairwise forces, centre of mass, elastic collisions | F06 |
| M8 | mechanics | Capstone, the Kepler orbit: a two-body central force, conserved energy and angular momentum, long-time behaviour | F06 |
| A1 | agents-llm | An LLM agent designs and runs an experiment on the projectile-with-drag simulation | F09 |
| L1 | lean | Proving what the simulation showed: a kinematic identity and the energy growth of explicit Euler on the harmonic oscillator | F08 |

The agent-based modelling lesson was not in the MVP list; F11 delivered it
as the first follow-up, and the first release includes it (eleven lessons).

## MVP requirements coverage

| MVP requirement | Delivered by |
|---|---|
| Mechanics course of 6 to 10 lessons with numerical simulations | F02, F04, F05, F06 |
| At least one LLM agent lesson, run locally with the learner's key | F09 |
| Agent-based modelling lesson, or an explicit roadmap slot | F11 |
| At least one Lean 4 and Mathlib lesson, CI running `lake build` | F01 (pipeline), F08 (lesson) |
| Every lesson has explanation, assumptions, worked examples, reproducible code, exercises or interactives | F02 (format and checks), F07 (interactives), every lesson feature |
| Static site on GitHub Pages rebuilt from `main` by CI | F01 |
| CI executes all Python and builds all proofs; failing lessons cannot merge | F01 |
| Documented authoring workflow: lesson template, local verification command | F02 |
| Public repository with MIT and CC BY 4.0 licences | F01 |
| Visible learning path with ordering, difficulty, prerequisites | F03 |
| WCAG 2.1 AA, responsive, works without JavaScript | F01 (automated checks), F10 (manual audit) |

## Phase 1 — MVP

### F01 — Published site skeleton with the full verification pipeline

**Goal.** Put a real, if nearly empty, site on GitHub Pages and gate every
pull request with one verification command that already exercises Python,
Lean with Mathlib, and the site build. Every later feature only adds content
and checks to this pipeline.

**User-visible outcome.** A visitor to the GitHub Pages URL sees a home page
that explains the project and its three pillars, states the licences, and
links to the repository. A contributor sees one required status check on every
pull request.

**In scope.**

- Python project: `pyproject.toml`, `uv.lock`, `.python-version`, the `pbc`
  package skeleton, Ruff, pytest, and at least one real unit test.
- Lean project in `lean/` with pinned toolchain and Mathlib, and one small
  theorem that imports Mathlib, so the cache path and build time are proven.
- Quarto project in `site/` with home and about/licence pages, MathML
  equations with a self-hosted math font, an accessible highlighting theme,
  and only self-hosted assets.
- Checks added to `scripts/verify.conf`: lint and format, unit tests, Lean
  build that fails on `sorry` and project axioms, site build, built-site
  checks (no other-origin resources, no cookies, image alt text and
  dimensions, internal links, readable without JavaScript, automated WCAG 2.1
  A/AA scan), and the determinism check.
- The supported-machine contract of the architecture: a documented one-time
  setup in `docs/development.md` that provides Git, uv, elan, jq, the
  Playwright browser build pinned through `uv.lock`, and on Linux that
  browser's system libraries. Setup is the only step that may need
  administrator rights; `./scripts/verify.sh` stays unprivileged and installs
  no system packages.
- Preflight checks for that contract: a check listed first in
  `scripts/verify.conf` and `scripts/doctor.sh` both report every missing
  prerequisite, including a browser build that is absent or cannot start,
  with a fix hint.
- CI workflow: actions pinned by commit SHA, read-only default permissions,
  the same setup as a local machine, caches, job timeout, site artifact on
  every run, deploy job from `main` that publishes the verified artifact.
- Licences: `LICENSE` (MIT, code) and `LICENSE-CONTENT` (CC BY 4.0, lesson
  text and figures), stated in the README and the site footer.
- Repository hygiene: project README, CONTRIBUTING with contribution licence
  terms and the template section removed, CODEOWNERS placeholder replaced,
  `.env.example` and `.gitignore` updated, Dependabot configuration for
  Python and Actions, `docs/development.md`, `docs/deployment.md`, and
  `docs/operations.md` updated.
- A checklist of settings only the human can apply, applied with their
  approval: enable Pages with GitHub Actions as source, add the `verify`
  required check to the `main` ruleset, confirm Dependabot alerts, secret
  scanning, and push protection.

**Out of scope.** The lesson format, lessons, the learning path, widgets, Lean
display on pages, agent code, a custom domain.

**Dependencies.** None.

**Acceptance criteria.**

1. On a clean macOS and a clean Linux machine that has completed only the
   documented one-time setup (Git, uv, elan, jq, the Playwright browser
   build, and on Linux its system libraries), `./scripts/verify.sh` passes
   without administrator rights and leaves the built site in a documented,
   git-ignored directory. A test shows that verification and
   `./scripts/doctor.sh` fail with a fix hint when a prerequisite is missing,
   at least for jq and for the browser build.
2. The CI workflow runs checks only through `./scripts/verify.sh`. Each new
   check has a test showing it fails on a violating input: a failing Python
   test, a Lean file that does not compile, a Lean file containing `sorry`, a
   page that loads a resource from another origin, an image without alt text.
3. A push to `main` publishes the artifact built by the verify job of that
   commit; the deploy job contains no build step. The home page is reachable
   at the GitHub Pages URL.
4. Workflows declare `contents: read` by default; only the deploy job has
   `pages: write` and `id-token: write`; every action is pinned by commit
   SHA; no secret is referenced; triggers are `pull_request` and `push` to
   `main` only.
5. `verify` is a required status check on `main`, and a pull request with a
   failing check cannot be merged.
6. The built site requests nothing from another origin and sets no cookie.
7. The home page is fully readable with JavaScript disabled, renders a sample
   equation as MathML, is usable at phone width without horizontal scrolling
   of the page, and has zero violations in the automated WCAG 2.1 A/AA scan.
8. Two builds of the same commit on the same platform produce byte-identical
   output.
9. The site works when served from the repository sub-path of the default
   Pages URL, and the base URL is one configuration value.
10. A warm-cache pull request run finishes within 12 minutes and Mathlib is
    not compiled from source. Measured times per check are recorded in the
    pull request.
11. Licence files exist; the README and site footer state MIT for code and
    CC BY 4.0 for content. No template placeholder text remains in the
    README, CONTRIBUTING, CODEOWNERS, or `.env.example`.
12. A page with sample equations, code, and a figure renders correctly in the
    current Chromium, Firefox, and WebKit engines, recorded in the pull
    request.

**Risk.** High. The feature changes CI permissions, deployment, and
repository settings, which need explicit human approval at each step.
Technical risks: Mathlib build products against GitHub's cache quota; Quarto
outputs that embed build-time values and break determinism; the Quarto binary
download at install time; accessibility defects in the default theme.

**Detailed implementation plan expected.** Yes.

### F02 — Lesson format and the first mechanics lesson

**Goal.** Define what a lesson is, enforce it with checks, document how to
write one, and prove it with the first published lesson.

**User-visible outcome.** A learner can read lesson M1, "Kinematics as a
program", with explanation, explicit assumptions, worked examples, executed
code and figures, exercises with solutions, and a "Reproduce this" section
whose commands regenerate the lesson's results from a clone. An author can
create a new lesson from a template and a guide.

**In scope.**

- Lesson directory convention, front matter schema, and required sections,
  as outlined in the architecture's lesson model.
- The verified display forms for Python: executed cells and by-reference
  excerpts from `src/pbc`, with the "not verified" marker and its visible
  label.
- Figure conventions: produced by executed cells, alt text, explicit
  dimensions, deterministic rendering.
- Exercise and solution pattern that works without JavaScript.
- "Reproduce this" section naming exact files, commands, and the built
  commit.
- Lesson source checks: schema, required sections, unmarked non-executed
  code, committed generated artifacts. The last check rejects tracked
  figures, outputs, execution caches, and rendered pages. Its one exemption
  is the replay fixture location of a lesson directory, whose path convention
  this feature fixes (ADR 002); nothing else may be committed there.
- Authoring guide in `docs/` and a lesson template, including the rule for
  attributing third-party material under the content licence.
- Lesson M1 and the `pbc.mechanics` code and unit tests it needs.

**Out of scope.** The learning path page and navigation between lessons (F03),
Lean and agent display forms (F08, F09), widgets (F07), further lessons.

**Dependencies.** F01.

**Acceptance criteria.**

1. Lesson M1 is published and contains every required section.
2. Each lesson source check has a test showing it fails on a violating
   lesson: missing metadata field, missing required section, non-executed
   Python block without the "not verified" marker, figure without alt text,
   committed generated figure. A test also shows that a file at the replay
   fixture location passes the committed-artifact check.
3. A by-reference excerpt on the built page is textually identical to the
   source in `src/pbc` at the built commit, shown by a test.
4. Running the commands in M1's "Reproduce this" section on macOS and on
   Linux reproduces every number on the page at the displayed precision.
5. Every numerical claim in M1 is the output of an executed cell, and M1's
   numerical method is validated against the closed-form solution in a unit
   test with an explicit tolerance.
6. The lesson page is fully readable with JavaScript disabled, shows
   equations as MathML, passes the automated accessibility scan, and executes
   within 30 seconds.
7. Material marked "not verified" renders a visible label on the page.
8. The authoring guide lets a second lesson be created from the template
   without reading existing lesson sources; the reviewer confirms this by
   following it.

**Risk.** Medium. The format is expensive to change once several lessons use
it. The by-reference helper and the "not verified" check carry the site's
integrity guarantee, so they need direct tests.

**Detailed implementation plan expected.** Yes.

### F03 — Learning path

**Goal.** Make the ordered learning path visible everywhere, so a learner
always knows where they are and what comes next.

**User-visible outcome.** A learning path page lists strands in order and,
within each, lessons with their order, difficulty, and prerequisites. Every
lesson shows its strand, position, difficulty, linked prerequisites, and
previous and next links.

**In scope.**

- One difficulty scale defined in one place and explained on the path page.
- Path page, lesson header, and previous and next links, all generated from
  lesson front matter.
- Validation of the path: unique lesson IDs, prerequisites exist, no cycles,
  prerequisites come earlier in the path, no gaps or duplicates in order.
- A strand appears only when it has a published lesson.
- Navigation that works without JavaScript and on phone, tablet, and desktop
  widths.

**Out of scope.** Progress tracking, recommendations, and any stored learner
state (F13, F14). Site search.

**Dependencies.** F02.

**Acceptance criteria.**

1. The path page and every lesson header are generated from front matter;
   adding a lesson requires no edit to any hand-maintained list.
2. Each path validation rule has a test showing the build fails on a
   violation: duplicate ID, unknown prerequisite, cycle, prerequisite later
   in the path.
3. From the home page, a learner reaches every published lesson, and from
   any lesson its previous lesson, next lesson, and prerequisites, with
   JavaScript disabled.
4. The path page and a lesson page are usable at phone, tablet, and desktop
   widths without horizontal scrolling of the page, shown by a built-site
   check.
5. The path page passes the automated accessibility scan.

**Risk.** Medium. Quarto has no built-in validation of custom metadata, so
the generation and validation code is project-owned.

**Detailed implementation plan expected.** Yes.

### F04 — Mechanics lessons: Newton's laws and projectile motion with drag

**Goal.** Move from kinematics to dynamics: forces as functions, a generic
stepping interface, and a problem without a closed-form solution.

**User-visible outcome.** Lessons M2 and M3 are published in the mechanics
strand.

**In scope.**

- Lesson M2 and lesson M3 as listed in the MVP lesson list, each in the F02
  format.
- The `pbc.mechanics` code they need, including the stepping interface later
  lessons and the agent lesson reuse, with unit tests.

**Out of scope.** Integrators beyond what M2 and M3 need (F05). Changes to the
lesson format or checks, unless a defect is found; such changes get their own
Issue.

**Dependencies.** F02.

**Acceptance criteria.**

1. M2 and M3 are published, pass all lesson and built-site checks, and each
   executes within 30 seconds.
2. M2's simulation is validated in a unit test against the analytic solution
   for linear drag, with an explicit tolerance.
3. M3's simulation is validated in unit tests by its drag-free limit and by
   convergence under time-step refinement.
4. Each lesson states its modelling assumptions and what breaks when they do
   not hold.
5. Each lesson has at least two exercises with on-page solutions, and the
   solutions' numerical answers come from executed code.
6. The simulation functions M3 uses are importable from `pbc` with documented
   parameters and units.

**Risk.** Medium. Physics and numerical correctness need independent review;
passing checks do not prove a lesson teaches the right thing.

**Detailed implementation plan expected.** Yes, short: lesson outline, code
interface, validation strategy.

### F05 — Mechanics lessons: the harmonic oscillator and numerical integrators

**Goal.** Teach how the choice of integrator changes what a simulation can be
trusted for, using the harmonic oscillator as the test system.

**User-visible outcome.** Lessons M4 and M5 are published in the mechanics
strand.

**In scope.**

- Lesson M4 and lesson M5 as listed in the MVP lesson list.
- Explicit Euler, symplectic Euler, velocity Verlet, and Runge-Kutta 4 in
  `pbc.mechanics` behind the F04 stepping interface, with unit tests.

**Out of scope.** Adaptive step-size methods beyond a pointer to further
reading. The formal proof of the Euler energy result (F08). The interactive
comparison (F07).

**Dependencies.** F04.

**Acceptance criteria.**

1. M4 and M5 are published, pass all lesson and built-site checks, and each
   executes within 30 seconds.
2. Unit tests verify the empirical order of accuracy of each integrator on
   the harmonic oscillator.
3. M4 shows, from executed code, that explicit Euler's energy grows by the
   same factor every step, and states that factor; this is the claim F08
   proves.
4. M5 compares the four integrators on accuracy, energy behaviour, and cost,
   with every figure and number produced by executed code.
5. Each lesson states its assumptions and has at least two exercises with
   on-page solutions.

**Risk.** Medium. Same content risk as F04. The integrator interface is
reused by F06, F07, F08, and F09, so a poor interface is costly later.

**Detailed implementation plan expected.** Yes, short.

### F06 — Mechanics lessons: energy, momentum, and a capstone orbit

**Goal.** Complete the mechanics course with the conservation laws as
diagnostics and a capstone that uses everything before it.

**User-visible outcome.** Lessons M6, M7, and M8 are published; the mechanics
strand is complete at eight lessons.

**In scope.**

- Lessons M6, M7, and M8 as listed in the MVP lesson list.
- The `pbc.mechanics` code they need (pendulum, pairwise forces and
  collisions, two-body central force), with unit tests.

**Out of scope.** Many-particle simulations and emergent behaviour (F11).
Lagrangian or Hamiltonian formalism (a candidate for F15).

**Dependencies.** F03, F05. F03 provides the learning path that criterion 5
checks.

**Acceptance criteria.**

1. M6, M7, and M8 are published, pass all lesson and built-site checks, and
   each executes within 30 seconds.
2. Unit tests verify momentum conservation to round-off for pairwise forces,
   and energy and angular momentum behaviour for the orbit under a symplectic
   integrator within a stated bound.
3. M8 reuses code from earlier lessons through `pbc`, not by copying it.
4. Each lesson states its assumptions and has at least two exercises with
   on-page solutions.
5. The learning path shows eight mechanics lessons in order with consistent
   prerequisites.

**Risk.** Medium. Same content risk as F04. Three lessons make this the
largest content feature; if review shows it is too large, split M8 into its
own Issue without changing this roadmap's lesson list.

**Detailed implementation plan expected.** Yes, short.

### F07 — Interactive visualizations

**Goal.** Establish how optional JavaScript widgets are built, tested, and
degraded, and ship the first one where it adds understanding.

**User-visible outcome.** In a mechanics lesson (default: the integrator
comparison in M5), a learner changes parameters such as the time step and the
integrator and sees the trajectory and energy respond. Without JavaScript, the
same place shows a static figure and an explanation.

**In scope.**

- Widget convention: a dependency-free, self-hosted ES module that enhances a
  static figure already in the page.
- Data for widgets computed by executed Python cells at build time and
  embedded in the page; or, where the widget computes in the browser, a test
  comparing its results with `pbc` reference values.
- Keyboard operability, visible focus, text alternative, and respect for
  reduced-motion preferences.
- Built-site tests for the widget and for its fallback.
- One widget in one published lesson, and a section on widgets in the
  authoring guide.

**Out of scope.** In-browser Python. Any JavaScript package manager or
bundler. Widgets that store state (F13). A widget in every lesson.

**Dependencies.** F05.

**Acceptance criteria.**

1. With JavaScript disabled, the lesson shows a static figure and text in
   place of the widget, and no content is lost.
2. With JavaScript enabled, the widget responds to its controls, is fully
   operable by keyboard, and passes the automated accessibility scan.
3. The widget loads no code or data from another origin and writes nothing to
   cookies or browser storage, shown by a built-site check.
4. Values the widget displays agree with `pbc` reference values within a
   stated tolerance, shown by a test.
5. The page has no layout shift when the widget loads, shown by reserved
   dimensions in the markup.
6. The build remains deterministic and within the CI budget.

**Risk.** Medium. Physics duplicated in JavaScript can drift from the tested
Python; criterion 4 exists for that. The requirements ask for interactives
only "where useful", so this is the MVP feature with the least requirement
pressure: if the human wants a smaller MVP, it can move after F10 without
affecting other features.

**Detailed implementation plan expected.** Yes.

### F08 — Formal proofs strand: first Lean lesson

**Goal.** Open the third pillar: a physics result from the mechanics course,
stated and proved in Lean 4 with Mathlib, shown on the site and checked by CI.

**User-visible outcome.** Lesson L1 is published in the formal proofs strand.
A learner reads the statement and proof with syntax highlighting, sees that CI
compiled it, and can open it in the repository or in the Lean web editor.

**In scope.**

- Lean display form: excerpts included by reference from files in `lean/`,
  with a vendored Lean syntax definition for highlighting.
- Links from the lesson to the repository file at the built commit and to
  the Lean web editor loading that file, labelled as possibly running a
  different Mathlib version.
- Visible CI evidence on the page: the commit and the toolchain and Mathlib
  versions the proof was compiled with.
- Lesson L1: the kinematic identity for constant acceleration, and the
  per-step energy growth of explicit Euler on the harmonic oscillator that M4
  demonstrates numerically.
- Authoring guide section on Lean lessons, including the rule that physical
  assumptions are hypotheses, not axioms, and that proofs are about models,
  not about the Python code.

**Out of scope.** Proofs about the Python implementation. Hover or type
information on the page. Proofs involving derivatives or differential
equations, unless the plan shows they fit; they are candidates for later
lessons.

**Dependencies.** F03, F05.

**Acceptance criteria.**

1. L1 is published in the `lean` strand and passes all lesson and built-site
   checks.
2. Every Lean excerpt on the page is textually identical to its source in
   `lean/` at the built commit, shown by a test.
3. `lake build` compiles every theorem L1 displays; a `sorry` or a
   project-declared axiom in any Lean file fails verification, shown by a
   test.
4. Each theorem's physical assumptions appear as explicit hypotheses and are
   explained in the lesson's assumptions section.
5. Lean code is highlighted at build time and readable with JavaScript
   disabled, with colour contrast that passes the automated scan.
6. The repository link points at the built commit, and the web editor link
   opens the proof; the page states which is authoritative.
7. The lesson connects each theorem to the numerical observation it proves
   and says what the proof does not cover.
8. Verification stays within the CI budget.

**Risk.** Medium. The vendored syntax definition may highlight imperfectly.
The public web editor's Mathlib version can drift from the pinned one. Proof
effort is hard to estimate; the chosen theorems are algebraic to keep it low.

**Detailed implementation plan expected.** Yes.

### F09 — LLM agents strand: first agent-driven experiment lesson

**Goal.** Open the second pillar: an LLM agent that designs and runs an
experiment on a mechanics simulation, runnable by the learner with their own
key and verified in CI without any key.

**User-visible outcome.** Lesson A1 is published in the LLM agents strand. A
learner reads how the agent is built, sees a recorded run whose tool results
were recomputed by CI, and runs the agent locally with their own API key
against the projectile-with-drag simulation.

**In scope.**

- The agent harness in `pbc.agents` as decided in ADR 004: model client
  interface, tool allowlist with validated and bounded arguments, run loop
  with a step limit, transcript.
- A replay client and one live client for the default provider, with the
  provider SDK as an optional dependency.
- Agent display form: the replay run rendered on the page, recorded model
  messages labelled as recorded.
- A1's replay fixture, committed under the rule of ADR 002: recorded model
  messages and expected tool results, no credentials, at the fixture location
  F02 defined, so the committed-artifact check accepts it. The page shows the
  recomputed tool results, never the recorded ones.
- Key handling: environment variable only, documented in the lesson and in
  `.env.example` by name; nothing printed, logged, or written to transcripts.
- Lesson A1, including a plain statement of what the agent may and may not
  do, and what a learner should expect to differ in a live run.
- Authoring guide section on agent lessons and on re-recording a transcript.

**Out of scope.** Agents that write or execute code, use a shell, or access
the network. Multi-agent systems. Calling an LLM from the site or from CI.
Agent-based modelling (F11).

**Dependencies.** F03, F04. Before implementation, the human decides the
default LLM provider (unresolved question 1 of the requirements) and the
decision is recorded in the feature plan.

**Acceptance criteria.**

1. A1 is published in the `agents-llm` strand and passes all lesson and
   built-site checks.
2. Verification runs A1 with the replay client, with no network access and no
   credential, and recomputes every tool result. A test shows that a changed
   simulation result beyond tolerance fails the replay with a message that
   says how to re-record.
3. A tool call outside the allowlist, or with arguments outside their bounds,
   is rejected without being executed, shown by tests.
4. The harness has no code path that evaluates model output as code, runs a
   shell command, or opens a network connection other than the live client's
   provider request, confirmed by review and by tests of the tool dispatch.
5. A test shows that a key set in the environment appears in no log line,
   printed output, exception message, or transcript.
6. No workflow references an LLM secret, and the built site contains no
   request to an LLM provider.
7. Switching provider requires implementing one client and changing one
   configuration value; the lesson shows where.
8. The maintainer has run A1 live once with their own key and recorded the
   committed replay fixture from that run; it sits at the declared fixture
   location, contains no credential, and passes the committed-artifact check.
   The page labels the model and date.
9. The lesson instructs learners to keep keys in local environment variables
   and never in code, notebooks, or committed files.

**Risk.** High. The feature handles credentials and executes model-directed
actions. It needs security-focused independent review and explicit human
approval of the allowlist boundary. Other risks: provider API changes; replay
that is too brittle when simulation code changes.

**Detailed implementation plan expected.** Yes.

### F10 — MVP release readiness and launch

**Goal.** Confirm the first release meets the requirements a reader cannot
verify from CI alone, settle the remaining launch decision, and declare the
MVP released.

**User-visible outcome.** The site presents a complete first release: ten
lessons across three strands, a coherent learning path, and clear pages on how
to reproduce, how to contribute, and the licences.

**In scope.**

- Manual WCAG 2.1 AA audit of the site chrome and one lesson of each strand
  (keyboard, screen reader, zoom and reflow, contrast), with defects fixed or
  filed.
- Reading pass over all lessons for consistent structure, terminology,
  prerequisites, and difficulty levels.
- A cold-start reproduction on macOS and Linux following only the public
  documentation.
- The custom domain decision (unresolved question 3 of the requirements),
  taken by the human, and applied if chosen.
- Contribution information for outside readers: how to report an error, the
  licence terms for contributions, and that the content proposal workflow is
  planned (F12).
- A release tag and a release note.

**Out of scope.** New lessons or new site capabilities. The content proposal
workflow itself (F12). Announcing or marketing the site.

**Dependencies.** F01, F02, F03, F04, F05, F06, F08, F09, and F07 unless the
human has moved it after the MVP.

**Acceptance criteria.**

1. Every row of this roadmap's MVP requirements coverage table is checked
   against the published site and recorded as met in the pull request.
2. The manual accessibility audit is recorded; no known WCAG 2.1 A or AA
   failure remains open without a linked Issue and the human's acceptance.
3. A reviewer who did not write the lessons reproduces one lesson of each
   strand from a clean clone on macOS and on Linux using only the public
   documentation.
4. The custom domain decision is recorded; if a domain is chosen, the site is
   served over HTTPS from it and all internal links still resolve.
5. Every lesson's assumptions, prerequisites, and difficulty are present and
   consistent with the learning path.
6. Measured CI times for the complete MVP are within the budget in the
   architecture, or the over-budget response of ADR 003 has been applied.
7. The repository has a release tag for the MVP.

**Risk.** Medium. The audit can uncover theme-level accessibility defects
that are expensive to fix late; running the automated scan from F01 onward
limits this. A custom domain changes DNS and Pages settings and needs the
human.

**Detailed implementation plan expected.** No. A checklist in the Issue is
enough; defects found become their own Issues.

## Phase 2 — After the MVP

These features are in scope for the project and out of scope for the MVP.
Their descriptions are deliberately coarser. Revalidate each against the
architecture and the requirements before creating its Issue.

### F11 — Agent-based modelling strand: first lesson

**Goal.** Open the agent-based modelling strand: many simple interacting
agents, no LLM, and behaviour that emerges from local rules.

**User-visible outcome.** The first lesson of the `agents-abm` strand is
published, and the strand appears in the learning path.

**In scope.**

- One lesson that builds a multi-agent simulation on the mechanics course,
  default topic: many colliding particles in a box, from pairwise collisions
  to pressure and the velocity distribution.
- The `pbc` code it needs, with unit tests, and seeded randomness so the
  build stays deterministic.

**Out of scope.** LLM agents. A general agent-based modelling framework or a
third-party one, unless the plan justifies it. Statistical mechanics beyond
what the lesson needs.

**Dependencies.** F03, F06. The requirements name this lesson the first
follow-up after the MVP.

**Acceptance criteria.**

1. The lesson is published in the `agents-abm` strand in the F02 format and
   passes all lesson and built-site checks within the per-lesson budget.
2. All randomness is seeded and two builds are byte-identical.
3. Unit tests check at least one emergent quantity against its theoretical
   value within a stated statistical tolerance.
4. The lesson states its modelling assumptions and how agent-based modelling
   differs from the LLM agents strand.

**Risk.** Medium. Many-particle simulations can exceed the 30 second lesson
budget; the problem size must be chosen for it.

**Detailed implementation plan expected.** Yes, short.

### F12 — Content proposal workflow through GitHub Issues

**Goal.** Let outside contributors and agents propose new content, have it
assessed, and have it drafted and merged through reviewed pull requests.

**User-visible outcome.** A contributor opens a lesson proposal Issue from a
form, receives an assessment against published criteria, and an accepted
proposal becomes a drafted lesson in a pull request that passes the same
verification as any lesson.

**In scope.**

- Issue form for lesson proposals and published assessment criteria (fit to
  the learning path, prerequisites, verifiability by code or proof, scope).
- A documented path from accepted proposal to drafted lesson, reusing the
  repository's existing Issue, plan, implement, and review scripts where they
  fit.
- Agent-assisted drafting, with the decision on where the agent runs and
  whether CI may hold an LLM key (unresolved question 2 of the requirements)
  taken by the human during planning. The requirements recommend the
  maintainer's machine first.
- Contribution licence terms applied to proposals and drafts.

**Out of scope.** Automatic merging. Any change that gives fork pull requests
secrets or write permissions. Public discussion features beyond Issues.

**Dependencies.** F10.

**Acceptance criteria.**

1. A proposal can be opened from an Issue form and is assessed against
   written criteria, with the outcome recorded on the Issue.
2. An accepted proposal reaches `main` only through a reviewed pull request
   that passes `verify`.
3. The human's decision on LLM credentials in CI is recorded. If CI holds a
   key, a new ADR records the threat model and workflows on fork pull
   requests still receive no secrets; if not, no workflow references an LLM
   secret.
4. Agent-drafted content is identified as such in its pull request.
5. The workflow is documented for contributors and for the maintainer.

**Risk.** High if a credential is introduced into CI, otherwise Medium.
Workflows triggered by Issues or by fork pull requests are a common source of
secret exposure and need security-focused review.

**Detailed implementation plan expected.** Yes.

### F13 — Self-check quizzes and browser-local progress

**Goal.** Give learners machine-readable self-checks and a record of their
progress that never leaves their browser.

**User-visible outcome.** Lessons offer self-check questions with immediate
feedback. The learning path shows which lessons the learner has completed. A
control clears all stored state.

**In scope.**

- A self-check question format authored in lessons, with answers and
  feedback, that degrades to the existing exercise-with-solution pattern
  without JavaScript.
- Progress and self-check results stored in browser local storage under a
  versioned, site-specific key, keyed by stable lesson IDs.
- A visible explanation of what is stored and a clear-data control.
- A machine-readable export of the learning path in the built site for
  client-side use.

**Out of scope.** Accounts, sync, export to any server, grading or
certification, recommendations (F14).

**Dependencies.** F03, F07, F10.

**Acceptance criteria.**

1. Completing a self-check updates the learner's progress, which persists
   across page loads in the same browser and is removed by the clear-data
   control.
2. A built-site test shows that no network request carries learner state and
   that no cookie is set.
3. With JavaScript disabled, every self-check is still usable as an exercise
   with a visible solution.
4. A change to the stored data format migrates or safely discards old data,
   shown by a test.
5. Self-check and progress controls are operable by keyboard and pass the
   automated accessibility scan.

**Risk.** Medium. This is the first feature that stores anything in the
browser, so the privacy invariant needs a direct test.

**Detailed implementation plan expected.** Yes.

### F14 — Adaptive recommendations

**Goal.** Recommend the next lesson or extra exercises from the learner's
local self-check results.

**User-visible outcome.** The learning path and lesson pages suggest what to
do next, with the reason for each suggestion, computed entirely in the
browser.

**In scope.**

- Recommendation rules that use only the path's prerequisite graph and the
  locally stored results.
- An explanation of each recommendation and a way to ignore it.

**Out of scope.** Any server-side or LLM-based recommendation. Learner
modelling beyond the stored self-check results. Analytics.

**Dependencies.** F13.

**Acceptance criteria.**

1. Given a fixed stored state, recommendations are deterministic and covered
   by tests of the rules.
2. Each recommendation states why it was made.
3. A built-site test shows that computing recommendations makes no network
   request.
4. Without stored state or without JavaScript, the site shows the plain
   learning path with no error.

**Risk.** Medium. The value of the feature depends on recommendation quality,
which tests cannot establish; plan a review with real use.

**Detailed implementation plan expected.** Yes.

### F15 — Second course on the three-pillar path

**Dropped by the change cycle `final-curriculum` (2026-10-12; ADR 013
decision 7).** F15 was never started and has no Issue. Its goal, a course
beyond mechanics, is delivered by F62 (the eight courses and the reference
curriculum) and by the first lesson feature of each course (F70, F71, F72,
F73, F89, F91, F94), each with the human's approval of the lesson list in
its Issue, as this block asked. Its rule that a course contains an agent
lesson and a Lean lesson is not carried: the method paths are a view over
the courses, and proofs are added where they add physics insight. The ID
F15 is never reused. The block below is kept as approved, as history.

**Goal.** Grow beyond mechanics with a second course that again spans
simulation, agents, and proof.

**User-visible outcome.** A second course appears in the learning path, with
its own ordered lessons and prerequisites on the mechanics course.

**In scope.**

- The human chooses the course topic and approves its lesson list in the
  Issue (candidates: oscillations and waves, Lagrangian and Hamiltonian
  mechanics, statistical physics).
- Lessons in the existing format, including at least one agent lesson and one
  Lean lesson.
- Any extension of the learning path model needed to show more than one
  course.

**Out of scope.** Changes to the pipeline or lesson format beyond what a
second course strictly needs. A language other than English.

**Dependencies.** F10. F12 is not required, but the course may be the first
user of that workflow if it exists.

**Acceptance criteria.**

1. The approved lesson list is recorded in the Issue before drafting starts.
2. Every lesson of the course passes the same checks as the mechanics course,
   and total verification stays within the CI budget or the over-budget
   response of ADR 003 has been applied.
3. The learning path shows both courses with correct prerequisites.
4. The course contains at least one agent lesson and one Lean lesson.

**Risk.** Medium. Execution time grows with every lesson; this course is the
most likely point at which the single verify job must be split.

**Detailed implementation plan expected.** Yes, starting with a course
outline; the course will likely be delivered as several Issues.

## Phase 3 — Next phase (change cycle `physics-next-phase`)

Every feature in this phase comes from `docs/changes/physics-next-phase.md`
(2026-10-09); each block names its candidate or section there. The wave R0
and the wave R1 are specified in detail, because they are the first wave of
the change request. Waves R2 to R5 are deliberately coarser: revalidate each
feature against the architecture, the requirements, and the delivered
features before creating its Issue, and expect a feature plan to refine it.

What every feature of this phase inherits, without repeating it in each
block: the invariants of `docs/architecture.md` (static site, no other-origin
resource, readable without JavaScript, WCAG 2.1 AA, deterministic builds,
verified display forms, no credential anywhere in CI); the lesson format and
checks of `docs/authoring.md`; the CI budget of ADR 003; and the editorial
standard of the requirements ("UX expectations"): self-contained
progressive-depth lessons, purposeful researched external references,
scientifically faithful figures, typed claims.

### Wave R0 — Keep the pipeline within budget

### F58 — Parallel verification jobs behind one required check

**Source.** `docs/release-readiness.md` (F10, "CI time against the budget")
and ADR 003, decision 6; change request Section 14, point 7 (verification
strategy). No candidate number.

**Problem.** With eleven lessons the `verify` job takes about 15 minutes
with warm caches against a 12 minute budget (measured 2026-10-08, runs
37857338092 and 37859587548). The first response of ADR 003 was applied in
F10 and saved about a minute and a half. Every feature of this phase adds
pages, and every page adds execution and checking time, so the second
response is due. The roadmap recommends it before them without making it a
dependency of any feature: the per-check budgets and the over-budget
response of ADR 003 decision 6 stay the guard while the overrun lasts.

**Goal.** Apply the second response of ADR 003: run named subsets of the
same `verify.conf` checks in parallel CI jobs behind one aggregate required
status check, without changing what is checked or how a laptop verifies.

**User-visible outcome.** A contributor still sees one required check,
`verify`, on every pull request; it finishes within the budget. Locally,
`./scripts/verify.sh` is unchanged.

**In scope.**

- A subset mechanism in `scripts/verify.sh` (for example `--only <group>`),
  with groups declared in `scripts/verify.conf` by a tag on each check, so
  that every check stays declared in one file and no check is declared in
  workflow YAML. A check without a tag belongs to a default group, so a new
  check is never silently skipped.
- The workflow: one job per group in parallel, each with the setup and
  caches it needs, and one aggregate job named `verify` that fails when any
  group fails, is skipped, or is cancelled. The deploy job depends on the
  aggregate job and still publishes the artifact the site-building group
  uploaded.
- The determinism check and the built-site checks consume the site that the
  build group produced, either in the same job or through a job artifact,
  without rebuilding in a way that could differ from what is published.
- A test in `tests/integration/test_ci_workflow.py` that the union of the
  groups the workflow runs is every check of `verify.conf` and of
  `verify-workflow.conf`, that the aggregate job is the only job named
  `verify`, and that no job has write permissions except deploy.
- An ADR that amends decision 2 of ADR 003 and decision 2 of ADR 005 (the
  single verify job that is the one required status check) with the group
  design, written in this feature as ADR 005 and ADR 006 were, and the matching update of
  the CI section of `docs/architecture.md` and of `docs/deployment.md`.
- The required status check of the `main` ruleset keeps its name `verify`,
  so no ruleset change is needed; if GitHub requires one, it is a human step
  recorded in the pull request.

**Out of scope.** Dropping, filtering, or scheduling a check (not available
without a new ADR). Changing any check's content. Self-hosted runners.

**Dependencies.** F10. ADR 003 decision 6 authorises the split.

**Acceptance criteria.**

1. A warm-cache pull request run finishes within 12 minutes wall clock,
   measured on three consecutive pull requests and recorded in the pull
   request and in `docs/release-readiness.md`'s table.
2. Every check of `verify.conf` and `verify-workflow.conf` runs in exactly
   one group; a test fails when a check is in no group or in two.
3. `./scripts/verify.sh` without arguments runs every product check locally
   as before; `--only <group>` runs one group; a test covers both.
4. A failing check in any group fails the aggregate `verify` check, shown by
   a test on a violating input per group, and a pull request with a failing
   group cannot be merged.
5. The deploy job publishes the artifact built by the build group of the
   same commit; no job builds the site twice for publication.
6. Workflow permissions stay `contents: read` by default, with write scopes
   only in the deploy job; every action is pinned by SHA.
7. The ADR amending ADR 003 and ADR 005 is accepted with the merge, and the
   status of both names it.

**Risk.** High. The feature changes the CI workflow structure, the required
status check, and the deploy chain, which need explicit human approval and
security-focused review. Technical risk: cache restores multiplied by the
number of jobs; a group that needs Mathlib and the browser both.

**Detailed implementation plan expected.** Yes.

### Wave R1 — Clarity, usability, identity, and the editorial pilots

Order within the wave, by dependency: F44 and F57 and F37 and F35 and F36
and F39 are independent of each other and may run in parallel worktrees;
F25 after F57; F26 and F27 after F37; F28 after F37, F44, F35, F36; F30
after F28; F29 after the M5 pilot of F30 has been reviewed.

### F44 — Visual design and accessibility system

**Source.** Candidate F44; Section 8.3 (component rules); Section 10.2
(footer attribution slot); Section 14 (design constraints).

**Problem.** The site runs on Quarto's default theme with one short
stylesheet. The lesson constructs the next phase adds (claim labels, figure
status, "Go deeper" blocks, self-checks, hint steps, cards, a footer
attribution line) have no visual language, and the manual audit of F10 left
two observations open: no skip link, and a low-contrast focus ring on the
navigation.

**Goal.** One coherent, accessible visual system for the site chrome and the
lesson components, defined as CSS tokens and a small set of component
styles, so that later features add components without inventing styles.

**User-visible outcome.** The site reads consistently on phone, tablet, and
desktop: clear heading hierarchy, readable figures at every width, a skip
link, visible focus everywhere, accessible colours, and a discreet footer
line that F57 fills. Nothing a reader relies on changes meaning.

**In scope.**

- Design tokens in `site/assets/site.css`: type scale, spacing, colour
  palette with contrast-checked pairs for text, links, labels, and the five
  figure-status and four claim-type labels, and the colour-blind-safe
  sequence Matplotlib figures use, exposed to lesson code through one
  `pbc.authoring` constant so figures and CSS agree.
- Component styles: lesson header, "What you'll learn", assumptions list,
  claim labels, figure status and caption, semantic result tables (F36),
  annotated excerpts (F35), "Go deeper" block, self-check and hint details,
  path cards (F27), the prerequisite graph container (F26), the footer
  attribution slot (F57).
- A skip link and a focus style for the navigation that passes the
  contrast of WCAG 2.2's focus appearance criterion, closing the two
  observations of F10's audit.
- The page payload budget check of the architecture (initial payload
  1.5 MB), added to `tests/e2e` with the measured sizes of every page
  recorded in the pull request.
- A section in `docs/authoring.md` on the components and the tokens.

**Out of scope.** A JavaScript build toolchain, a third-party CSS framework,
a theme switch, decorative imagery, any branding graphic, any marketing
surface. Content changes to lessons (the editorial passes).

**Dependencies.** F10.

**Acceptance criteria.**

1. Every page passes the automated WCAG 2.1 A/AA scan, and the skip link and
   navigation focus pass the scripted keyboard pass of F10's audit on the
   same scope, recorded in the pull request.
2. Every colour pair used for text and labels has a contrast ratio of at
   least 4.5:1 (3:1 for large text and controls), shown by a unit test over
   the token definitions.
3. The eleven lesson pages, the path page, and the chrome pages are usable
   at 320, 768, and 1280 CSS px without two-way scrolling, and figures scale
   to the viewport, shown by the built-site checks.
4. A sample page that uses every component renders correctly in the current
   Chromium, Firefox, and WebKit engines, recorded with screenshots in the
   pull request.
5. The initial payload of every page is at most 1.5 MB, shown by the new
   built-site check, with the sizes recorded.
6. Physics content stays central: no page gains an element that is not
   content, navigation, licence, or attribution; the built-site check for
   other-origin resources and cookies still passes.
7. The build stays deterministic and within the CI budget.

**Risk.** Medium. Theme-level changes touch every page; the accessibility
scan and the three-engine check limit regressions.

**Detailed implementation plan expected.** Yes, short: tokens, component
list, and the check.

### F57 — Open-source identity, attribution, and citation

**Source.** Section 10 of the change request (unnumbered proposal); Section
3G; requirements decisions 20 and 21; unresolved questions 5 and 7.

**Decision on placement (Section 3G).** One small independently testable
feature, not deliverables scattered over F25, F44, and F12: the acceptance
checks (a) to (h) of Section 10.5 span the home page, footer, About, README,
`CITATION.cff`, and the Issue forms, and they are testable together. F25
and F44 consume the canonical text this feature defines; F12's Issue form
pattern is reused, not rebuilt. The JIDAI website page and the organization
profile are outside this repository (see "Candidate mapping").

**Decisions recorded before any copy is written** (from the requirements):

- Creator: Ahmet Taspinar, TU Delft Applied Physics alumnus, founder of
  JIDAI. Canonical description: "Physics by Construction is a free,
  open-source educational initiative by JIDAI, created by Ahmet Taspinar."
  One sentence, carried verbatim on the home page, the About page, the
  README, and in `CITATION.cff`. The footer carries a shortened attribution
  line derived from the same source, the sentence without its subject ("An
  open-source educational initiative by JIDAI, created by Ahmet Taspinar");
  no surface types either text by hand.
- Rights: the copyright line "Ahmet Taspinar and the Physics by Construction
  contributors" stays; JIDAI is the initiative's company, not a copyright
  holder, funder, or university partner; MIT for code and CC BY 4.0 for
  content are unchanged; no legal notice changes in this feature.
- Repository and address: `github.com/taspinar/physics-by-construction` and
  the Pages URL stay; the `jidai-nl` organization exists with the creator as
  owner, may link to the repository from its profile (a human action outside
  this repository), and no transfer follows.
- Citation: `CITATION.cff` names the actual authors and the project URL and
  repository, with the licence fields; no DOI until a release policy exists.
- Community: nothing requires an account, contact with JIDAI, tracking, or a
  corporate link; no marketing surface.

**Goal.** Make the creator and the JIDAI association discoverable, truthful,
and discreet, give the project citation metadata, and give contributors two
more entry points, without touching ownership, licences, or addresses.

**User-visible outcome.** An ordinary visitor understands the project from
the home page and finds one low-key link to the creator and JIDAI context;
the About page explains the creator, what JIDAI is, why the project is open
source, how to cite, and how to contribute; the footer carries one concise
line; the README has the same description; a researcher can cite the
project from `CITATION.cff`; a contributor can open a scientific correction
or a dataset suggestion from a form.

**In scope.**

- The canonical description and attribution text in one place
  (`site/_quarto.yml` metadata or a `pbc.authoring` constant) and rendered
  from there on the home page (F25 places it), the footer, the About page,
  and the README; the instructor packs (F59) and `CITATION.cff` reuse it.
- Footer line: the shortened attribution line derived from the canonical
  sentence, with one link to `https://jidai.nl`;
  readable without JavaScript and at phone width; not repeated in lessons.
- About page sections: creator and background; what JIDAI is and what it
  does for the project, distinguishing creator and maintainer from rights
  holder; why open source and editorial independence; how to cite (the
  `CITATION.cff` text); how to contribute; the existing licence and
  third-party material sections unchanged.
- `CITATION.cff` validated against the CFF schema by a test, with the
  authors, the project and repository URLs, `license: MIT` for the code and
  the content licence stated in the message, and the version left to the
  release tag once it exists.
- README: the description, the creator and JIDAI line, the homepage, the
  contribution entry points, and where the licences are; the physics
  overview stays first.
- Two Issue forms reusing the F12 pattern: `scientific-correction.yml`
  (page, the statement, the correction, the source and its licence, the
  evidence) and `dataset-suggestion.yml` (source URL or DOI, creator,
  licence, measurement type, size, what a lesson could learn from it);
  `CONTRIBUTING.md` and the Contribute page name them. A scientific
  submission requires a source, a licence, and independent review, which
  the forms say.
- A built-site check that the canonical sentence appears on the home page
  and the About page, that the footer carries the derived line, that no
  other page repeats the footer line in its content, that the home page's
  content outside the footer carries exactly one attribution link and it
  leads to the About page, and that the site still loads nothing from
  another origin.
- An "Identity and attribution" section in `docs/authoring.md` stating the
  rules above for every future page.

**Out of scope.** Changing copyright holders, licences, repository owner,
or Pages URL. A JIDAI.nl page. The organization profile. Logos, banners,
badges beyond a plain text line in the README, splash screens, forms that
collect contact details, any analytics. University names or logos.

**Dependencies.** F10; F12, whose Issue-form set, `CONTRIBUTING.md`, and
Contribute page this feature extends. The human approves the final wording
of the footer, About, README, and `CITATION.cff` on the pull request before
merge.

**Acceptance criteria.**

1. (a) From the home page, a visitor reaches the About page's creator and
   JIDAI section in one click, and that is the only attribution link in the
   home page's content, excluding the site footer, whose derived line
   carries the `https://jidai.nl` link on every page.
2. (b) Every statement about authorship, ownership, licences, JIDAI's role,
   and published versus planned content on the home, About, README, and
   `CITATION.cff` matches the decisions above; the human confirms it on the
   pull request.
3. (c) The canonical sentence is identical on the home page, the About page,
   the README, and in `CITATION.cff`, and the footer line is the shortened
   attribution derived from the same source, shown by a test that reads all
   five surfaces and compares them with the one source.
4. (d) The Contribute page and `CONTRIBUTING.md` describe how to correct,
   propose, and suggest a dataset without contacting JIDAI, and the five
   Issue forms (the existing bug, feature, and lesson-proposal forms and the
   two new ones) open with their required fields, shown by a schema test.
5. (e) No new account, analytics, lead form, mailing list, or outbound
   request; the other-origin and cookie checks pass.
6. (f) `LICENSE`, `LICENSE-CONTENT`, the repository address, and
   `website.site-url` are byte-identical to before the feature.
7. (g) The footer and About page pass the accessibility scan, the keyboard
   pass, the no-JavaScript check, and the width checks.
8. (h) All eleven lesson pages are unchanged by the feature, shown by a
   before-and-after comparison of the built pages recorded in the pull
   request. The comparison excludes the footer element and normalises the
   built commit, which every lesson page embeds and which differs between
   any two commits (the SHA in the excerpt links, in the Lean evidence box,
   and in "Reproduce this"); after that normalisation the pages are
   byte-identical. The same-commit determinism check is unchanged and still
   passes.
9. `CITATION.cff` validates and contains no DOI field.

**Risk.** Medium. Public copy about a company and a person must be accurate
and discreet; the human approves the wording. No technical risk.

**Detailed implementation plan expected.** No. The Issue holds the copy for
approval; a checklist is enough.

### F25 — Homepage narrative: Construct, Investigate, Verify

**Source.** Candidate F25; Section 1 (mission); Section 10.2 (homepage
row); Section 14, slice 1.

**Problem.** The home page presents three pillars, "Simulate, Experiment
with agents, Prove", and the requirements now state three activities,
Construct, Investigate, Verify, with real measurements as first-class
content that does not exist yet. The page must say so honestly.

**Goal.** A home page that states the mission in the approved terms, shows
what is published and what is planned without overstating either, and
leads to the learning path, the methods, and the About page.

**User-visible outcome.** A visitor learns in one screen what the site
teaches and how (Construct, Investigate, Verify), sees the eleven published
lessons and the mechanics course as published, sees the measured-data labs
and further courses as planned, with no date promised, and finds the
attribution line F57 defined.

**In scope.**

- The narrative: mission, the three activities with one concrete example
  each that exists on the site today (a simulation, an agent run, a proof),
  and a plain "what is published, what is planned" section generated from
  the lesson metadata and a short hand-maintained list of planned items
  that names this roadmap's IDs.
- The "One result, three ways" example kept or replaced by one that spans
  the three activities.
- The F57 attribution placement.
- Links to the path page by course and by method (F37, if delivered; else
  the current path page).

**Out of scope.** Any marketing tone, hero imagery, testimonials, claims of
adoption, counters, or news. Changes to lessons.

**Dependencies.** F57 (the canonical description). F37 is not required;
the page links to what exists.

**Acceptance criteria.**

1. The page names Construct, Investigate, and Verify and links each to one
   published example, shown by a built-site test of the links.
2. The counts and names of published lessons on the page come from the
   lesson metadata, not from typed numbers, shown by a test that changes the
   lessons and rebuilds.
3. Every planned item on the page names a roadmap ID and is labelled
   planned; no planned item is linked as if it existed.
4. The page is readable without JavaScript, passes the accessibility scan,
   and fits phone width.
5. A reviewer who did not write the page confirms that every sentence about
   the site is true of the published site at that commit, recorded on the
   pull request.

**Risk.** Low.

**Detailed implementation plan expected.** No.

### F37 — Lesson metadata and course navigation

**Source.** Candidate F37; Section 1 (curriculum and navigation); Section
12 (F26 + F27 + F37 one source of truth); ADR 008.

**Decision on slicing (Section 12).** The shared source of truth, the
metadata extension and the path page by course and method, is this feature;
the prerequisite graph (F26) and the cards (F27) are separate consumers of
it, each deliverable and reviewable on its own.

**Problem.** The learning path is one linear list of four strands. The
requirements organise content as courses by subject with methods
cross-cutting, and ask that a lab belong to one primary course and link to
its extensions. There is no field for a course, a method, an outcome, or a
related lesson, and the path page cannot show them.

**Goal.** Extend the lesson metadata with `course`, `methods`, `outcomes`,
and `related`, keep the strands as URL groups and ordering, and generate
the learning path page by course with one path per method, all from front
matter.

**User-visible outcome.** The learning path page lists the mechanics course
with its eight core lessons and its agent, agent-based-modelling, and proof
extensions, then one section per method listing the lessons that use it. A
lesson header names its course, its methods, its position, its outcomes
("What you'll learn"), its prerequisites, its related lessons, and previous
and next. Every existing URL still works.

**In scope.**

- `COURSES` and `METHODS` vocabularies in `pbc.authoring.path`, next to
  `STRANDS` and `DIFFICULTIES`; the four new front-matter fields with
  validation (course exists, at least one method, two to five outcomes,
  related lessons exist and are not already among this lesson's
  prerequisites); the rule that a course appears only when it has a lesson.
- Migration of all eleven lessons: `course: mechanics` for every lesson,
  methods and outcomes written from each lesson's current description and
  text, related links one-directional from the prerequisite side: M3 → A1
  (`agent-experiment`), M7 → the gas lesson (`particles-in-a-box`), M1 → L1
  and M4 → L1 (`proving-what-the-simulation-showed`). The extension lesson
  keeps the mechanics lesson among its prerequisites and does not list it
  as related, so every pair passes the validation above. The migration
  changes front matter only.
- The path page by course and by method; the lesson header; a Quarto
  sidebar that lists the current course's lessons and works without
  JavaScript at every width, or no sidebar if the no-JavaScript check cannot
  be met.
- An explanation on the path page of what previous and next mean (the one
  linear order) against what the course order and the prerequisites mean.
- `docs/authoring.md` and the lesson template updated; the content proposal
  form's strand dropdown gains a course field; `docs/content-proposals.md`
  criteria name the course.

**Out of scope.** The graph (F26), the cards (F27), search (F41), a second
course (F15), changing any strand identifier or address, changing any
lesson body.

**Dependencies.** F10; F12, whose lesson-proposal form and
`docs/content-proposals.md` criteria this feature changes.

**Acceptance criteria.**

1. All eleven lessons carry the four new fields, and a test shows the build
   fails on a lesson that lacks `course`, has no method, has an outcome
   count outside two to five, names a related lesson that does not exist,
   or names one of its own prerequisites as related.
2. The path page shows every lesson under its course and under each of its
   methods, generated from front matter, shown by a built-site test that
   compares the page with the metadata.
3. Every lesson URL that existed before the feature resolves to the same
   lesson, shown by a test over the list of previous addresses.
4. From the home page, with JavaScript disabled, a reader reaches every
   lesson through the course list and through each method path.
5. The header of every lesson shows course, methods, outcomes, prerequisites
   with links, related lessons, previous and next, consistent with the front
   matter, shown by the existing header test extended.
6. The path page and a lesson page are usable at phone, tablet, and desktop
   widths, and pass the accessibility scan.
7. Lesson source bodies (everything below the front matter) are
   byte-identical to before, shown by the diff of the pull request.

**Risk.** Medium. The migration touches every lesson's front matter and the
header every page renders; the tests of F03 catch drift. The sidebar is the
one piece of Quarto chrome that may need JavaScript; the fallback is to
omit it.

**Detailed implementation plan expected.** Yes, short: schema, vocabularies,
migration table, page layout.

### F26 — Generated prerequisite graph

**Source.** Candidate F26; Section 14, slice 3.

**Problem.** Prerequisites are visible only lesson by lesson; a reader
cannot see the shape of the path, which lessons are required before which,
and where the extensions branch off.

**Goal.** A clickable prerequisite graph on the learning path page,
generated from front matter, accessible, with a text fallback.

**User-visible outcome.** The path page shows a directed graph of lessons
grouped by course, with arrows from prerequisite to dependant and a distinct
style for related (recommended, not required) links; each node links to its
lesson; without JavaScript the same SVG is present with a text list of
edges; on a phone the page offers the linear list first.

**In scope.**

- A layout computed at build time in Python (a layered layout of the
  prerequisite DAG, deterministic), rendered as inline SVG with a `<title>`
  and a `<desc>` that `aria-labelledby` names, and a visually hidden
  ordered list of the edges in text ("M4 requires M2") as the accessible
  alternative. The SVG does not carry `role="img"`: that role has
  presentational children, which would remove the node links from the
  accessibility tree and fail the `nested-interactive` rule of the scan;
  `role="group"` is used only where a grouping is needed.
- Arrow direction and the required-versus-recommended distinction explained
  in a legend next to the graph; colours not the only distinction.
- Keyboard focus on every node link; focus order follows path order.
- A width-aware layout: at phone width the graph scrolls inside its own box
  (as wide equations do) and the linear list stays primary.
- A test that the graph's edges equal the prerequisite and related
  relations of the front matter, and that the SVG is byte-stable.

**Out of scope.** A graph library loaded in the browser; animation;
progress overlays (F13, F14); a graph per lesson page.

**Dependencies.** F37. F44 is not a dependency: F26 ships with a minimal
style for the graph container, and F44 replaces it with the component style
when it lands.

**Acceptance criteria.**

1. The edges of the rendered graph equal the prerequisite and related
   relations of the metadata, shown by a test.
2. Every node is a link to its lesson, reachable by keyboard, with visible
   focus; the SVG is labelled by its title and description through
   `aria-labelledby`, carries no `role="img"`, and has the text list of
   edges; the accessibility scan passes.
3. With JavaScript disabled, the graph and the text alternative are present
   and nothing is lost.
4. The page has no two-way scrolling at 320 CSS px; the graph scrolls inside
   its box.
5. Two builds produce a byte-identical SVG.

**Risk.** Medium. Layout quality for a growing graph; the layered layout
must stay readable when courses and labs are added, which the feature tests
with a synthetic thirty-lesson path.

**Detailed implementation plan expected.** Yes, short.

### F27 — Learning path cards and the difficulty scale

**Source.** Candidate F27; Section 14, slice 4.

**Problem.** The path page lists each lesson as a paragraph of prose:
description, level, prerequisites. Outcomes are not stated, the level
labels are explained only at the top, and a reader cannot scan the course.

**Goal.** Compact, scannable lesson cards on the path page from the F37
metadata, and a difficulty legend that explains each level where it is
used.

**User-visible outcome.** Each lesson on the path page is a card: title,
one-sentence description, two to five outcomes, course and methods, level
with its definition on hover and in text, prerequisites as links, and the
related lessons. Cards reflow to one column on a phone.

**In scope.**

- The card component (F44 styles) rendered by the path page generator from
  front matter; the difficulty legend rendered from `DIFFICULTIES` with a
  level badge on each card that links to the legend.
- Plain headings and lists inside cards so that screen readers get the same
  structure as the linear list did.
- No text is typed by hand into a card; a test compares the cards with the
  metadata.

**Out of scope.** Progress state on cards (F13), recommendations (F14),
images on cards, cards elsewhere than the path page.

**Dependencies.** F37, F44.

**Acceptance criteria.**

1. The cards show title, description, outcomes, course, methods, level,
   prerequisites, and related lessons from the front matter, shown by a
   test over every lesson.
2. The level of every card links to the legend, and the legend text equals
   `DIFFICULTIES`.
3. The path page passes the accessibility scan, reads correctly without
   JavaScript, and reflows to one column at 320 CSS px without two-way
   scrolling.
4. The page's initial payload stays within the F44 budget.

**Risk.** Low.

**Detailed implementation plan expected.** No.

### F35 — Code explanation: annotated excerpts

**Source.** Candidate F35; Section 11.4 (F35 row).

**Problem.** Lessons show code by reference, which keeps it honest, but
several lessons show four or more excerpts under one introductory sentence
(M6 lines 224 to 260, M7 lines 240 to 280, M8 lines 240 to 277 of their
sources), and no excerpt can point at the line where the physics happens:
the update order, the unit conversion, the state variable.

**Goal.** Let a lesson show the lines of an excerpt that matter, annotate
them, and hide helpers, while the check that an excerpt equals its source
still holds.

**User-visible outcome.** An excerpt can highlight named lines with a short
margin note ("the new velocity moves the particle"), show only a named
region of a function, and state inputs, outputs, and units in a small table
above it; the full source stays one click away at the built commit.

**In scope.**

- `excerpt(..., lines=..., notes={...}, region=...)` in
  `pbc.authoring.excerpt`, rendered as a code block with marked lines and
  notes that are plain text in the page (readable without styles and by
  assistive technology), plus an optional interface table from the
  function's signature and docstring.
- The excerpt check extended: a region or a line range is still compared
  with the source file; a note cannot contain a number that the build did
  not compute.
- The authoring rule: explain why each shown step implements the physics,
  the update order, the state variables, the units, and the error modes;
  hide helpers that are not the point; link API documentation only through
  the reference register and only when it teaches more than the lesson
  explains.
- Applied to one lesson as the example (M2's stepper), leaving the others
  to the editorial passes.

**Out of scope.** Rewriting lesson prose (F29, F30, F31). Any client-side
code viewer.

**Dependencies.** F10.

**Acceptance criteria.**

1. An annotated excerpt on the built page is textually identical to its
   source region at the built commit, shown by the extended test.
2. Notes and interface tables render without JavaScript and pass the
   accessibility scan; marked lines are distinguished by more than colour.
3. A test shows the check fails when a region does not exist or when an
   excerpt's notes drift from the source after the source changes.
4. M2 uses the new form for its stepper and its page reproduces
   byte-identically through "Reproduce this".

**Risk.** Low.

**Detailed implementation plan expected.** No.

### F36 — Numeric results as semantic tables

**Source.** Candidate F36; Section 11.4 (F36 row); requirements "UX
expectations" (numeric outputs as tables with units and interpretation).

**Problem.** Every numeric result on the site is a fixed-width `print()`
block: more than forty printed tables across the eleven lessons (for
example M1 source lines 207, 275, and 322, M5 lines 333 and 409, M6 line
413, M8 line 348). Units sit in header strings, screen readers get a
preformatted block, and narrow screens scroll sideways.

**Goal.** A helper that turns arrays into a semantic table with a caption,
column units, and chosen precision, and an interpretation sentence pattern,
so that results are readable, accessible, and still computed by the build.

**User-visible outcome.** Results appear as real tables with header cells,
units in the headers, right-aligned numbers at a stated precision, a
caption that says what the table shows, and a sentence after it that says
what the reader should conclude.

**In scope.**

- `pbc.authoring.table(rows, columns=[(name, unit, format)], caption=...)`
  rendering Markdown or HTML tables from a cell, with `scope` on header
  cells, numbers formatted at a stated precision, and a wide table that
  scrolls inside its own box like a wide equation.
- The authoring rule that a result table has units, a caption, and an
  interpretation; the check function that flags a cell whose output is a
  multi-line fixed-width block of numbers, delivered with a unit test and
  enabled for no lesson yet, because the `format` field arrives with F28;
  F28 enables it for format-2 lessons and owns the lesson-level test.
- Applied to one lesson as the example (M1's four tables), leaving the
  others to the editorial passes.

**Out of scope.** Interactive sorting; rewriting other lessons.

**Dependencies.** F10.

**Acceptance criteria.**

1. Tables on M1 have header cells with units, a caption, and a stated
   precision, and the numbers equal the previous printed ones at that
   precision, shown in the pull request.
2. The tables pass the accessibility scan and cause no two-way scrolling at
   320 CSS px.
3. A unit test shows the check function flags a violating cell (a console
   block of numbers) and accepts a `table()` cell; enabling it for format-2
   lessons and the lesson-level test belong to F28.
4. M1 reproduces byte-identically through "Reproduce this".

**Risk.** Low.

**Detailed implementation plan expected.** No.

### F28 — Lesson format 2, the reference register, and the M1 pilot

**Source.** Candidate F28; Section 11 (11.1 layered design, 11.2 selection
protocol, 11.4 F28 row, 11.5 pilot); Section 14, slice 5; ADR 009.

**Problem.** The audit of the published lessons on 2026-10-09 (see "Lesson
editorial decision" below) found: no typed claims, no figure status, no
limits section except in the Lean lesson, no self-check distinct from the
exercises, no curated external reference anywhere, captions that describe
but do not interpret, and hand-typed approximate numbers in prose. M1 is a
good lesson, which is why it is the pilot: the format must add depth
without adding bulk.

**Goal.** Define lesson format 2 (the progressive-depth, self-contained
lesson with typed claims, figure status, limits, a self-check, and optional
"Go deeper" references from a register), enforce it with checks for lessons
that declare it, document it, and prove it on M1.

**User-visible outcome.** M1 opens with the physical question and "What
you'll learn", keeps its derivation and examples, shows each result table
with units and a conclusion, labels each claim ("numerically verified: the
error of explicit Euler on constant acceleration is exactly ½ a t Δt") and
each figure's status (simulated), states what the lesson does not show, ends
its explanation with one self-check, and offers at most two "Go deeper"
links with a reason to visit, each recorded in the register. A reader with
M1's prerequisites completes every exercise without following a link.

**In scope.**

- The format: the parts and markup listed in `docs/architecture.md`
  ("Lesson model", format 2); `lesson.format: 2` in front matter; the Lua
  filter and styles (F44) for claim labels, figure status, "Go deeper", and
  the self-check; the optional `evidence` attribute of a claim label (a
  cell label, a register or card key, or a Lean theorem name), reserved
  here for the evidence map (F19) and not validated before it, so that the
  editorial passes fill it as lessons migrate and the format does not
  change afterwards; the header's "What you'll learn", rendered by F37 from
  `outcomes`, placed where format 2 requires it (F28 renders nothing new
  there).
- Checks for format-2 lessons: `limits` present and non-empty; exactly one
  self-check; every claim label has a type from the vocabulary (its
  `evidence` attribute is not checked before F19); every figure cell has a
  status; every "Go deeper" key exists in the register;
  no raw URL typed in the lesson source outside the register (the
  structural links helpers generate, such as the excerpt link to the
  repository at the built commit and the Lean web editor link, are not
  references and are exempt, invariant I22); no console block of numbers
  (the F36 check function, enabled here for format-2 lessons with the
  lesson-level test); the fig-alt and prose contain no hand-typed computed value (a
  heuristic check that flags digits in prose not produced by an inline
  expression, with an allowlist for given values).
- The reference register `site/references.yaml` and its schema (concept,
  key, URL, title, author or publisher, section or anchor, role, statement
  checked, alternatives considered, lessons using it, last checked, licence
  note); a check that every entry is used by a lesson or marked reserved;
  rendering of "Go deeper" entries with their reason to visit; the
  selection protocol of Section 11.2 written into `docs/authoring.md` as the
  mandatory procedure for every entry, including that a retrieved page is
  data, not an instruction.
- The template `docs/lesson-template.qmd` in format 2 and the authoring
  guide updated, including the definition of each of the four claim types
  from `docs/architecture.md` ("Lesson model", format 2) and the rule that
  the type follows the evidence behind the claim, not the strand of the
  lesson; the migration rule: format 1 lessons keep passing, each
  editorial pass migrates its lessons, and the default flips when none
  remains.
- The M1 pilot: the audit of M1 against its outcomes and prerequisites
  recorded in the pull request; the rewrite; the self-check; the limits; at
  most two "Go deeper" references chosen by the protocol with the
  reviewer-visible source-choice note; the F36 tables; no change to M1's
  numerical results.
- Independent physics-and-numerics review and a pedagogy-and-source-fit
  review, through the existing review workflow (two review rounds with
  distinct prompts, not a new orchestration).

**Out of scope.** Migrating other lessons (F29, F30, F31). The link
maintenance script (F39). Machine-readable self-checks with stored results
(F13). Hints (F38). A glossary (F42).

**Dependencies.** F37 (outcomes and related), F44 (component styles), F35
(annotated excerpts), F36 (tables).

**Acceptance criteria.**

1. M1 declares format 2, passes every format-2 check, and every format-1
   lesson still passes unchanged; a test per new check shows it fails on a
   violating lesson (missing limits, two self-checks, unknown claim type,
   figure without status, unknown register key, raw URL typed in the source,
   console block, digits in prose without an inline expression).
2. The register validates against its schema; every entry has every field;
   every entry is used by M1 or marked reserved; each M1 entry's note says
   which alternative was considered and why this source adds something the
   lesson does not contain, and the reviewer confirms by opening it.
3. M1's numerical results are byte-identical to the previous build at the
   displayed precision (the tables and inline values), shown in the pull
   request; "Reproduce this" regenerates the page.
4. A reader can complete M1's three exercises and the self-check without
   following any external link, confirmed by the pedagogy reviewer, who
   also confirms that every major concept has its physical question, core
   explanation, worked example, interpretation, and limits.
5. Both independent reviews are recorded on the Issue with no Critical or
   Major finding open.
6. The page passes the accessibility scan, reads without JavaScript (labels
   and "Go deeper" are plain text), and fits phone width; its initial
   payload is within the F44 budget.
7. The authoring guide lets an author migrate a lesson to format 2 without
   reading M1's source; the independent reviewer confirms this by migrating
   a small scratch lesson, or an uncommitted copy of one format-1 lesson,
   using only the guide and the template, and records it on the pull
   request. Any gap the F30 M5 reviewer later finds in the guide is an F30
   finding, not a reopening of F28.

**Risk.** Medium. The format is expensive to change once lessons migrate;
the heuristic check for hand-typed numbers can produce false positives and
needs an allowlist. Content risk: more structure can make a lesson longer
without making it clearer; criterion 4 and the two reviews guard it.

**Detailed implementation plan expected.** Yes.

### F30 — Editorial pass M5 to M8, with M5 as the research-backed pilot

**Source.** Candidate F30; Section 3H; Section 11.3 (the M5 example sources);
Section 11.5 (first pilot: M5).

**Decision on the pilots (Section 3H, 11.5).** The template pilot is M1
(F28), because the template must exist before any pass. The research-backed
editorial pilot is M5, the first lesson of this feature, reviewed on its own
before M6 to M8 start; M1 is then the first lesson of F29, so both
difficulty levels are piloted before bulk editing. No new numbered feature
is invented for the pilot.

**Problem.** M5 (847 lines) is the lesson with the most method distinctions
to get right and the one lesson with a "Further reading" paragraph, which
names two books without URLs, sections, or reasons. Its symplectic Euler
updates the velocity first (as the lesson and `integrators.py` state), its
Verlet is velocity Verlet with a predicted velocity in the second
acceleration call, and its Runge-Kutta 4 is the classical fixed-step method;
any external source must match these exactly, and SciPy's adaptive RK45 is
not the same stepper. M6 to M8 state several results without derivation
(M6's series for the period, M8's orbital elements) and type numbers by
hand (M8 has no inline expression at all).

**Goal.** Migrate M5, then M6, M7, and M8 to format 2 under the editorial
standard: explain what is unmotivated, distinguish the methods accurately,
interpret every figure, replace hand-typed numbers with computed ones, and
add only the external references that demonstrably add insight.

**User-visible outcome.** Four lessons in format 2. M5's reader finds, for
each of the four methods, the physical question, the update rule with the
exact ordering, the derivation of order and energy behaviour, the
interpretation of each figure, a "Go deeper" link only where a source adds
a derivation or intuition the lesson does not contain, and a self-check on
the limits of each method.

**In scope.**

- Per lesson, in this order: M5 alone first; then M6, M7, M8 as one or
  three Issues at the human's choice. Each: an audit of gaps with examples
  before rewriting, recorded on the Issue (unmotivated equations, missing
  assumptions, unsupported assertions, terse explanations, hand-typed
  numbers, descriptive captions); the rewrite in format 2, with the
  `evidence` attribute filled on each claim label (F28); references
  researched by the protocol of F28 with at least two sources compared per
  concept where practical, and the source-choice note; no change to the
  numerical implementation to accommodate a source.
- For M5: the candidate sources of Section 11.3 are inputs to the research,
  not pre-approved links; each is re-opened and compared with alternatives;
  the velocity-first symplectic Euler ordering, the velocity Verlet variant,
  and classical RK4 versus adaptive RK45 are verified against each chosen
  source; the two books stay only if a public section or a library record
  gives the reader a reason and a way to find them.
- Independent physics-and-numerics review and pedagogy-and-source-fit
  review per lesson, through the existing review workflow; M5's reviews
  gate M6 to M8. A gap in the F28 authoring guide that M5's migration
  exposes is recorded as an F30 finding and fixed in the guide here.
- Figures keep their generating code; captions become interpretive; the
  F36 tables replace console blocks; F35 excerpts annotate the update
  order.

**Out of scope.** New figures or diagrams (F33). Changing numerical results
unless a scientific correction is justified and approved on the Issue. M1
to M4 (F29). Hints (F38).

**Dependencies.** F28.

**Acceptance criteria.**

1. M5, then M6, M7, and M8 declare format 2 and pass every format-2 check;
   the audit of each lesson is recorded on its Issue before the rewrite.
2. Every number in prose, captions, and alt text of the four lessons comes
   from an executed expression, with the given values of exercises as the
   only allowed exception, shown by the F28 check.
3. Every external reference of the four lessons is in the register with its
   full selection evidence, and the physics reviewer confirms that each
   target matches the lesson's exact method variant (for M5: the
   velocity-first symplectic Euler, velocity Verlet, classical RK4; no
   source presented as RK4 that describes RK45).
4. The numerical results of the four lessons are unchanged at displayed
   precision, or an approved scientific correction is recorded on the Issue
   with its reason.
5. A reader can complete each lesson's principal exercise without
   following a link; the self-check of each lesson tests the method's
   limits, not a fact; both reviewers confirm per lesson.
6. M5's reviews are complete with no Critical or Major finding open before
   M6's Issue is created.
7. Each page passes the accessibility scan, the no-JavaScript check, the
   width checks, and the payload budget, and executes within 30 seconds.

**Risk.** Medium. Content and source correctness need independent review;
M5 is the lesson most exposed to a wrong external source.

**Detailed implementation plan expected.** Yes, short, for M5: the audit
template and the research log format; M6 to M8 follow it.

### F29 — Editorial pass M1 to M4

**Source.** Candidate F29; Section 11.5 (second pilot: M1).

**Problem.** M2 and M3 state the exponential solution, the Reynolds-number
regime, the drag-free range, and the interpolation bound without a
justification sentence or a source (M2 lines 62 to 64, 143 to 155; M3
lines 74 to 76, 134 to 140, 170); M4 asserts "the same algebra shows" for
its per-step rotation without showing it; M2 to M4 type approximate numbers
by hand in prose; captions describe rather than interpret; no lesson
offers a deeper path.

**Goal.** Migrate M1 (already in format 2 from F28, now with the editorial
pass proper), M2, M3, and M4 under the standard, lesson by lesson, with M1
first as the beginner-level pilot.

**User-visible outcome.** Four introductory and intermediate lessons in
format 2 with every equation motivated or derived to the declared
prerequisite level, interpretive captions, computed numbers, a self-check,
and at most a few researched "Go deeper" links.

**In scope.** As F30, for M1 (the editorial pass on the F28 pilot: gaps,
references, review), M2, M3, M4; one or four Issues at the human's choice;
the same reviews.

**Out of scope.** As F30. Diagrams (F32).

**Dependencies.** F28; F30's M5 pilot reviewed, so that the lessons learned
from the intermediate pilot apply.

**Acceptance criteria.** Criteria 1 to 5 and 7 of F30 applied to M1 to M4,
with criterion 3 checking the drag regimes and the exponential solution
sources against the lesson's exact statements.

**Risk.** Medium.

**Detailed implementation plan expected.** No; F30's audit template and
research log apply.

### F39 — Unified local setup, run recipes, and the link maintenance check

**Source.** Candidate F39; Section 11.4 (F39 / CI reproducibility row);
Section 14, slice 6; ADR 009.

**Problem.** `docs/development.md` and the Reproduce page cover the build
toolchain, and every lesson lists its commands, but there is no single
learner-facing guide that separates reproducing a lesson from extending it,
no setup for the optional agent runtimes (the live client, a coding agent
of the learner's choice) and for Lean work beyond the build, no
troubleshooting, and no way to check the external links the register will
hold.

**Goal.** One setup guide with tested commands per supported system, split
into the required build toolchain and the optional learner workflows, a
"reproduce versus extend" recipe per lesson type, troubleshooting, and the
on-demand link maintenance check.

**User-visible outcome.** A learner finds one page that says what to
install for reading and reproducing (nothing beyond the supported-machine
contract), what to add for running an agent live, for a coding-agent
exercise, and for editing Lean locally, and what to do when a step fails.
The maintainer can run `./scripts/check-links.sh` and get a report of every
register link that no longer resolves to its section.

**In scope.**

- `site/setup.qmd` (or a rewritten Reproduce page) with: the required
  setup, verified on macOS and Linux from a fresh install; optional setups
  (live LLM client with the key in the environment, a coding agent under
  the sandbox profile of ADR 010, Lean editing with the pinned toolchain);
  per lesson type the "reproduce" commands (what "Reproduce this" lists)
  and the "extend" commands (edit, test, preview); a troubleshooting table
  of the failures the preflight and doctor scripts report and the first
  cold-start attempt of F10 met (unreachable Lean release host, Mathlib
  clone prompt, missing browser libraries).
- A test that every command on the page that the build can run is run in
  CI (the commands of the required setup are those of `ci.yml` and are
  checked for equality), and that the optional commands are in
  `.not-verified` blocks.
- `scripts/check-links.sh`: reads the register, opens every URL with a
  timeout, checks that the page is reachable and, when an anchor is given,
  that it exists, and prints a report with the last-checked date to update;
  it is not in `verify.conf` and has no CI job (ADR 009); a test in
  `tests/integration`, run by the existing `check-tests` entry of
  `verify.conf`, runs it against a local fixture server (ADR 005 decision
  4: a test of a project script belongs with the product checks, not with
  the workflow self-tests). As a new file under `scripts/`, it is named in
  `docs/project-map.md` (the `docs-scripts` check requires it) and is
  guarded by `scripts/verify-workflow.conf` until it is excluded there
  after confirming that no workflow self-test reads it (ADR 005 decision
  4); the first local run before that exclusion runs the workflow
  self-tests.
- The maintenance rule in `docs/authoring.md`: run the link check before an
  editorial pass and at least once a quarter; a rotten link is re-researched,
  never replaced by a title match.

**Out of scope.** Installing anything in CI that verification does not
need. A scheduled workflow (would add a trigger; needs its own review).
Windows support.

**Dependencies.** F10.

**Acceptance criteria.**

1. A reviewer who did not write the page completes the required setup and
   reproduces one lesson of each strand on a clean macOS and a clean Linux
   machine following only the page, recorded on the pull request; the
   Linux run that F10 could not complete is completed or its blocker
   recorded.
2. The required commands on the page equal the commands of `ci.yml` and of
   the Reproduce page, shown by a test.
3. Every optional command is marked "not verified" and names the account or
   credential it needs and where the key goes (environment variable).
4. `./scripts/check-links.sh` reports a dead link and a missing anchor on
   a local fixture, shown by a test, and is absent from `verify.conf`.
5. The page passes the accessibility scan, reads without JavaScript, and
   fits phone width.

**Risk.** Low.

**Detailed implementation plan expected.** No.

### F50 — Experimental dataset registry and feasibility gate

**Source.** Candidate F50; Section 8 (survey, 8.1 shortlist, 8.2 spike, 8.4
gates, 8.5 deferment); Appendix A; Section 14, slice 7; ADR 007.

**Decision on the spike (Section 8.2).** The feasibility spike is the first
deliverable of this feature, not a separate numbered feature. It may start
beside wave R1, because it changes no page and touches no lesson; its go,
defer, or reject decisions gate F51 and every lab.

**Problem.** The requirements make real measurements first-class content
and require a feasibility gate before any lesson commitment; the repository
has no dataset, card, sample, reader, or rights record. The survey of 25
sources is a shortlist of editorial estimates, not validated labs.

**Goal.** Establish the dataset registry, the card schema, the rights and
artifact-type vocabulary, the sample location and caps, the learner-side
download script, and the checks; then run the feasibility spike on three
deliberately different candidates and record a go, defer, or reject
decision for each, with the evidence.

**User-visible outcome.** Nothing on the site yet. In the repository: one
card per surveyed dataset (25 from Appendix A, including negative
findings), a dossier per spiked dataset with a reference figure generated
from actual data by source-controlled code, a decision table, and the
checks that every later lab inherits.

**In scope.**

- `data/registry/<dataset>.yaml` schema: source DOI or URL, creator,
  licence or permission status with the four rights questions (local
  download, redistribution of subsets, publication of figures and
  derivatives, modification and attribution), version and access date,
  measurement type per artifact (`raw-measured`, `processed-measured`,
  `calibrated-observation`, `modelled-reference`, `synthetic-test`),
  calibration details, schema, units, cadence, coordinate conventions,
  masks and missing values, documented uncertainty, size, format and the
  reader it needs, checksum where available, estimated local runtime and
  memory, estimated page payload, decision (`go`, `defer`, `reject`,
  `survey-only`) with reasons and date.
- `data/samples/<dataset>/` as the declared committed location with the
  caps of the architecture (2 MB per file, 8 MB per dataset, 32 MB in all),
  a card for every sample, a checksum check, a rights check that permits
  committed samples only under CC0, CC BY, or an equivalent recorded
  permission, and a parsing test per sample asserting field names, shapes,
  units, masks, and cadence. Committed in this feature only for the
  datasets with a go decision and only what the dossier's figure needs.
- `scripts/fetch-data.sh <dataset>`: learner-side download of the full
  dataset by the card's URL, version, and checksum, with the host's rate
  limits respected; never called by the build or CI; a test that the build
  passes with data portals and external web hosts blocked (criterion 2). As
  a new file under `scripts/`, it is named in `docs/project-map.md` (the
  `docs-scripts` check requires it) and
  is guarded by `scripts/verify-workflow.conf` until it is excluded there
  after confirming that no workflow self-test reads it (ADR 005 decision 4);
  its test belongs with the product checks.
- The feasibility spike on three candidates of different kinds, recommended
  first pass: GW150914 strain (time series; GWOSC, CC BY 4.0 as read on the
  record page on 2026-10-09, about 1 MB per detector for 32 s at 4096 Hz),
  the Aalborg submerged-bar wave flume (measured-versus-modelled; Zenodo
  15049542, CC BY 4.0, 78.6 MB archive, md5 recorded), and the NPL on-wafer
  S-parameters (complex RF measurement; Zenodo 22658069, CC BY 4.0, 3.1 MB
  zip of Touchstone files). Each: retrieve a real minimal sample; inspect
  the actual files; label every artifact; produce the reference
  visualization from source-controlled code, with a physical consistency
  check where applicable (for the strain, the published chirp and the
  acknowledgement text GWOSC requires; for the flume, the measured and the
  CFD series separated; for the S-parameters, passivity and the calibration
  context); establish the rights of derived figures; estimate runtime,
  memory, CI needs, and web payload; and write the dossier
  `docs/datasets/<dataset>.md` with the decision.
- The minimal locked readers the three spike samples need, added as
  ordinary locked dependencies with their licences recorded: an HDF5
  reader for the strain, unless the plain-text strain product GWOSC also
  publishes avoids the dependency, and a Touchstone reader; the flume
  archive is extracted and read with what the locked environment already
  provides where that suffices. F51 generalises these readers into
  `pbc.data`.
- Cards for the remaining 22 Appendix A sources as `survey-only`, with what
  is known and the gate each would have to pass, including the optical
  diffraction record (Zenodo 19436924, whose record page shows a CC BY 4.0
  licence field next to a copyright line, both recorded on the card as
  read, because the change request flags redistribution as unclear; RAR
  archives of 46 MB and more) and the cylinder-wake PIV (Zenodo 20765567,
  CC BY 4.0, one 1.1 GB MAT file of processed fields at 20 Hz with masked
  zeros).
- The decision table and the recommendation for the first lab, recorded in
  `docs/datasets/README.md` and summarised in this roadmap by the human when
  F51 is created.
- `docs/authoring.md` section "Measured data": the gate, the card, the
  sample rule, the figure status, the typed claims, the no-LLM path.

**Out of scope.** Readers and analysis beyond what the three reference
figures need; F51 generalises the minimal readers of this feature into
`pbc.data`. Any lesson page. Committing anything restricted or
above the caps. Contacting a portal from the build.

**Dependencies.** F10. ADR 007.

**Acceptance criteria.**

1. The card schema validates every card; a test shows the dataset check
   fails on a sample without a card, a sample above a cap, a checksum
   mismatch, a sample whose card's rights do not permit redistribution, and
   a sample without a parsing test.
2. The build and every check pass with no access to data portals, external
   web pages, or model APIs (invariant I20), shown by a test that runs
   `./scripts/verify.sh` with those hosts blocked, or with all egress
   blocked after the toolchain, package, and Mathlib caches are warm, or by
   an equivalent guard in the data readers. Fetching the pinned toolchains,
   packages, and the Mathlib cache is an install-time dependency (ADR 003
   decision 4; architecture, "Toolchains and pinning") and is not what the
   test blocks.
3. Three dossiers exist, each with: the actual file inspected (named with
   version and checksum), the artifact labels, the reference figure
   generated by a script in the repository from the committed or downloaded
   data, the rights answers with the source of each answer, the size and
   runtime estimates, and a go, defer, or reject decision with reasons.
4. The 22 remaining cards exist with `survey-only` and name the gate each
   would have to pass; no score from the survey spreadsheet is copied as a
   fact.
5. Every committed sample is under the caps, rights-cleared on its card,
   and parsed by a test; the total of `data/samples/` is reported in the
   pull request.
6. A reviewer who did not write the spike regenerates each reference figure
   from the committed sample or the documented download and confirms the
   figure's status label and caption.
7. The recommendation for the first lab is recorded with its reasons and
   its fallback.

**Risk.** Medium. Rights and format surprises (RAR, MAT, HDF5 readers;
acknowledgement texts), host rate limits, and the temptation to let a
beautiful figure decide: criterion 3 ties every decision to evidence.

**Detailed implementation plan expected.** Yes: the card schema, the three
spike plans, the figure scripts.

### Wave R2 — Finish the editorial standard, trustworthy scientific coding

### F42 — Before you begin, and the glossary

**Source.** Candidate F42; Section 11.4 (F37 and F42 row).

**Goal.** A site-wide glossary of the assumed vocabulary (mathematics,
Python, numerical methods, physics, Lean) with concise on-site definitions
and internal cross-links, and a "Before you begin" block on every lesson
generated from its outside prerequisites, linking each to its glossary entry.

**In scope.** `site/glossary.qmd` with entries in a small YAML or Markdown
structure that lessons reference by key; the header cell rendering "Before
you begin" from `prerequisites.outside` with glossary links; a check that
every outside prerequisite maps to an entry; external introductions only
through the reference register and only where they add real depth; the
authoring rule to prefer an internal link where the explanation exists.

**Out of scope.** Re-teaching prerequisites; a search index (F41).

**Dependencies.** F37, F28.

**Acceptance criteria.** Every outside prerequisite of every lesson resolves
to a glossary entry (test); the glossary page and the block read without
JavaScript, pass the accessibility scan, and fit phone width; each entry is
one to three sentences with a cross-link to the lesson that uses it.

**Risk.** Low. **Detailed implementation plan expected.** No.

### F38 — Progressive hints in exercises

**Source.** Candidate F38; Section 11.4 (F38, F13, F14 row); Section 12
(F38 + F13/F14).

**Goal.** Exercises can carry one to three hints, each a closed `details`
element before the solution, so that a reader can take one step at a time
without seeing the answer; no stored state, no quiz engine.

**In scope.** A `.hint` div inside `.exercise`, rendered by the lesson
filter as nested `details` that open without JavaScript; the lesson check
that hints come before the solution and contain no computed number that
the solution's cells did not produce; the authoring rule that "Go deeper"
references and hints are distinct and that a hint never leaks the answer;
applied to the exercises of M1 and M5 as examples.

**Out of scope.** Recording whether a hint was opened (F13); any
recommendation (F14).

**Dependencies.** F28.

**Acceptance criteria.** Hints render as nested details without JavaScript
and pass the accessibility scan; a test shows the check fails on a hint
after the solution; F13's later self-check format can wrap the same
markup, confirmed by a note on the Issue.

**Risk.** Low. **Detailed implementation plan expected.** No.

### F40 — Reproducibility UX

**Source.** Candidate F40; Section 12 (F28 + F35 + F36 + F40 + F42).

**Goal.** Keep the exact source revision and the verification evidence on
every page while making the hashes and commands unobtrusive: a short
"Reproduce this" summary with the commit and one command, and the full
listing (files, tests, Lean record, commands) in a closed `details`.

**In scope.** `reproduce_this()` renders the summary and the details; the
built-site check that the commands still regenerate the page is unchanged;
the Lean evidence box gets the same treatment; a "copy" affordance only if
it needs no JavaScript to read.

**Dependencies.** F28.

**Acceptance criteria.** Every lesson's reproduction test still passes; the
commit, the files, and the commands are present in the page text without
JavaScript; the section is shorter on first view and complete when opened.

**Risk.** Low. **Detailed implementation plan expected.** No.

### F41 — Self-hosted search

**Source.** Candidate F41.

**Goal.** Site search over lessons, glossary, and pages from an index built
at build time and served from the site's own origin, with the learning path
and the glossary as the navigational fallback without JavaScript.

**In scope.** Quarto's built-in search enabled with its local index and its
bundled script only (no Algolia, no other origin), or a project-owned index
if Quarto's cannot meet the origin and payload checks; a built-site check
that search makes no request to another origin and sets nothing in storage;
the search control hidden without JavaScript and the path page linked in
its place.

**Dependencies.** F37.

**Acceptance criteria.** With JavaScript, a query finds a lesson by a term
in its body; the other-origin, cookie, and storage checks pass; without
JavaScript the page shows the fallback and no broken control; the index
counts within the page payload budget; the accessibility scan passes.

**Risk.** Medium: Quarto's search integration and the no-JavaScript chrome
need care; the fallback is to not ship it.

**Detailed implementation plan expected.** No.

### F31 — Agent and Lean editorial pass

**Source.** Candidate F31; Section 11.4 (F29 to F31 row).

**Goal.** Migrate A1, the agent-based-modelling lesson, and L1 to format 2
under the standard: explain tool bounds, replay trust, theorem hypotheses,
what an LLM claim is and how it is tested, and empirical versus numerical
versus formal evidence; curate authoritative API and formal-method
references through the register after reading them; keep every proof and
explanation self-contained.

**In scope.** As F30, per lesson, with the agent lesson's physical question
(the angle of the longest throw) moved before the technique; A1's raw
dictionary outputs (source lines 443 to 447) as tables; L1's residual claim
(line 270) derived in place; typed claims on every result (the agent's
conclusion from its simulated runs as `numerically-verified` only where
the build recomputes it, never `experimentally-supported`, because no
measurement is involved; the theorems as `formal-theorem` with scope).

**Dependencies.** F28, F30.

**Acceptance criteria.** Criteria 1 to 5 and 7 of F30 for the three lessons;
in addition, L1's "What the proofs do not cover" stays and every theorem's
claim label states its scope; A1's live-run commands stay "not verified".

**Risk.** Medium. **Detailed implementation plan expected.** No.

### F32 — Mechanics diagrams M1 to M4

**Source.** Candidate F32; Section 11.4 (F32 to F34 row).

**Goal.** Conceptual diagrams drawn by code, labelled `conceptual`, where a
picture carries a physical insight the prose cannot: the state and the
update as a transition, force arrows on the falling particle, drag against
velocity, the trajectory with and without drag, the oscillator's phase
plane and energy ellipse.

**In scope.** `pbc.authoring.diagrams` helpers (arrows, labelled states,
simple geometry) over Matplotlib, deterministic, with the F44 palette; each
diagram in an executed cell with alt text and a caption that states the
insight; no image files; third-party diagrams cited and linked, never
rehosted.

**Dependencies.** F29.

**Acceptance criteria.** Each diagram is produced by the build, labelled
`conceptual`, has alt text that conveys the insight, and is byte-stable;
the pedagogy reviewer confirms each diagram answers a question the prose
raised; the pages stay within the payload and time budgets.

**Risk.** Low. **Detailed implementation plan expected.** No.

### F33 — Mechanics diagrams M5 to M8

**Source.** Candidate F33.

**Goal.** As F32 for the integrator comparison (the update orderings side
by side), energy bands versus drift, the collision geometry and the centre
of mass, and the Kepler orbit's phase drift and conserved vectors.

**Dependencies.** F30. **Acceptance criteria.** As F32. **Risk.** Low.
**Detailed implementation plan expected.** No.

### F34 — Agent and Lean diagrams

**Source.** Candidate F34.

**Goal.** As F32 for the agent tool flow (model, harness, allowlist,
simulation), replay verification (recorded messages, recomputed results),
and the theorem pipeline (statement, hypotheses, Lean, CI record, page),
each with its precise scope stated.

**Dependencies.** F31. **Acceptance criteria.** As F32. **Risk.** Low.
**Detailed implementation plan expected.** No.

### F45 — Agent-assisted simulation development

**Reconciled by the change cycle `final-curriculum` (2026-10-12).** F45
fills slot AI1 of the physics reasoning path and is unchanged; it has no
Issue. Its default exercise, a damped driven oscillator with resonance, is
also the subject of lesson M12 (F68): whichever lands first owns the
verified reference solution in `src/pbc`, and the other reuses it (see
F68).

**Source.** Candidate F45 (merged with the shared workflow of F55); Section
12 (F45 + F55); requirements use case 9; ADR 010, accepted with this
planning.

**Decision (Section 12).** One agent-assisted scientific coding workflow,
defined here and reused by F55 for experimental problems and by F22 for
proofs. Lessons stay separate from the shared workflow.

**Goal.** Teach a learner to drive a coding agent of their choice, on their
own machine with their own account, from an approved physical
specification to a tested Python simulation, and to verify the agent's
code, assumptions, and units; and define the reusable workflow and sandbox
profile every later coding-agent exercise follows.

**In scope.** The workflow document: specification format (physics,
assumptions, interface, units, tests the result must pass), the sandbox
profile (a scratch checkout, an allowlist of commands such as running the
tests and the formatter, no network beyond the agent's provider, a budget
in steps, time, and cost, review of every diff before running it), and the
review rubric (assumptions, units, update order, tests, failure modes). The
first lesson, in the `agents-llm` strand with method `coding-agents`: one
mechanics problem the course has not solved (default: a damped driven
oscillator with resonance), the specification, the verified reference
solution and tests in `src/pbc`, the rubric, and an example transcript
marked "not verified" with the agent and date. A test that no workflow
file, script, or check invokes a coding agent. The authoring guide section
"Coding-agent exercises".

**Out of scope.** Running any agent in CI or the build; replaying
agent-written code; a specific vendor as a requirement; experimental data
(F55); Lean (F22).

**Dependencies.** F10.

**Acceptance criteria.** The reference solution passes its tests and the
page executes within budget; the page states the sandbox profile and the
rubric in full; the transcript is labelled "not verified" with model and
date; a test shows CI and the build contain no coding-agent invocation and
no credential; a learner following the page with any coding agent reaches
a state where the provided tests decide, confirmed by the maintainer's own
run recorded on the Issue; the security-focused review approves the
sandbox profile.

**Risk.** High: the exercise invites a learner to run agent-written code;
the profile, the budget, and the review rule are the safeguards, and the
site never runs any of it.

**Detailed implementation plan expected.** Yes.

### F46 — Scientific code verification and debugging

**Source.** Candidate F46 (shares a validation contract with F18); Section
12 (F46 + F18).

**Goal.** A lesson on how scientific code is shown to be right: independent
physics tests (limits, conservation, convergence), deliberately faulty
reference implementations the reader must catch, negative tests that must
fail, and an objective evaluation of a piece of code against a contract;
and the written validation contract (what a verifier checks, in what order,
with what evidence) that F18's review agents and F45's rubric reuse.

**In scope.** `pbc.verification` helpers (order estimation, invariant
checks, convergence tables) with tests; a gallery of faulty steppers in
`src/pbc` marked as such; the lesson in the `mechanics` strand with method
`simulation`, at the next order there (ADR 008 decision 3), with the
previous-and-next prose of M8 checked after the insertion; the contract
document.

**Dependencies.** F10.

**Acceptance criteria.** Each faulty implementation is caught by a named
test on the page, and a correct one passes the same tests; the contract is
referenced by name in the lesson and reusable by F18; the usual lesson and
page checks.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F16 — Counterexample hunter

**Source.** Candidate F16.

**Goal.** A bounded agent in the ADR 004 harness that tests a falsifiable
physics claim through allowlisted simulations and reports either a
verified counterexample or an inconclusive outcome; every experiment is
logged and replayed in CI.

**In scope.** An allowlist over the integrators and models of the course
with bounded parameters; the claim format (a statement, a predicate the
harness evaluates on simulation output, a budget); a lesson in the
`agents-llm` strand with two claims, one false (a counterexample exists
within the budget) and one the agent cannot settle; the replay fixture;
the verdict typed `numerically-verified` only for the recomputed
counterexample, never for the agent's prose.

**Out of scope.** Code-writing agents; multi-agent debate (F18).

**Dependencies.** F09, F46 (the contract names what counts as a
counterexample), F28 (the typed claim the verdict carries).

**Acceptance criteria.** The counterexample is recomputed by the build and
the page shows the recomputed values; the inconclusive case is labelled so;
the ADR 004 boundary tests cover the new allowlist; replay passes without
credentials.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F17 — Further Lean mechanics proofs

**Source.** Candidate F17 (also the source material for F56 and F22).

**Goal.** Two or more focused Lean lessons tied to mechanics lessons:
momentum conservation of the pairwise collision rule of M7, and a property
of an integrator on the oscillator (the modified energy conserved by
symplectic Euler, or the per-step rotation), with pinned checks,
hypotheses as assumptions, and the limits stated.

**In scope.** Modules under `lean/PhysicsByConstruction/Mechanics/`; lessons
in the `lean` strand with `course: mechanics`, each listing the mechanics
lesson it proves something about (M5 or M7) among its `prerequisites`, as
L1 lists M1 and M4; M5 and M7 gain the new lesson under `related`, because
related links are one-directional from the prerequisite side and a lesson
may not list a prerequisite as related (F37); each theorem's claim typed
`formal-theorem` with its scope; the Lean build time kept within budget.

**Dependencies.** F08, F28 (the typed claims and their scope).

**Acceptance criteria.** As F08's criteria 1 to 8 for each lesson; the
connection to the numerical observation it proves and what it does not
cover are stated; the `lean-build` time is recorded.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F59 — Instructor pack for one published lesson

**Source.** Section 9 of the change request (unnumbered proposal);
requirements use case 11; Section 10.2 (For Educators row).

**Decision (Section 9).** One small feature rather than a deliverable of an
existing one: no pedagogy feature produces educator material, and the pack
is independently testable. It reuses the F37 outcomes, the F57 citation
text, and the F12 Issue path for feedback; it adds no authoring platform.

**Goal.** One reusable teaching pack for a lesson that has passed its
editorial pass (default: M5), with a lecturer guide, learning objectives,
prerequisites, approximate time, a student assignment, a rubric, a
reference solution verified by the build, accessibility notes, a no-AI
pathway, accurate citation and reuse terms, and a neutral way to suggest
improvements.

**In scope.** `docs/instructor-packs/<lesson>.md` generated in part from
the lesson's metadata (outcomes, prerequisites, difficulty) so it cannot
drift; the assignment's reference solution as executed cells in a
non-published page or in tests; a "For educators" page on the site that
lists packs, states the licence and the citation, and links to the Issue
forms; no form, no contact requirement, no claims of adoption.

**Dependencies.** F57, F30 (M5 in format 2).

**Acceptance criteria.** The pack's objectives and prerequisites equal the
lesson's metadata (test); the reference solution is verified by the build;
the citation text equals `CITATION.cff`; an educator who did not write the
lesson follows the pack and reports what was missing, recorded on the
Issue; the page passes the usual checks.

**Risk.** Low. **Detailed implementation plan expected.** No.

### Wave R3 — From measurements to models

### F51 — Experimental methods and visualization foundations

**Source.** Candidate F51 (merged with the analysis core of F47); Section
8.3; Section 8.4; Section 12 (F47 + F51).

**Decision (Section 12).** One reusable data-analysis and uncertainty core
lives here; F47 is a lesson that uses it for sweeps and reports.

**Goal.** The shared `pbc.data` package every measured-data lab uses:
readers for the formats the go decisions need (HDF5, Touchstone, CSV; MAT
or FITS only if a lab with a go decision needs them), generalised from the
minimal readers F50 locked for its spike samples, calibration and mask
handling, noise and uncertainty propagation, residuals, curve fitting with
identifiability diagnostics, and science-first plotting helpers
(measured-versus-model panels with residuals, signed colour scales, time
series with uncertainty bands, status labels), with cross-lab test fixtures
from the committed samples.

**In scope.** The package with unit tests on the committed samples; the
figure conventions of the requirements enforced by helpers (status label,
axis units, legend, residual panel, no false colour presented as natural,
no smoothing presented as raw); a page-side pattern for the measured-data
lab (format 2 plus the data card rendered on the page, the artifact labels,
the download instructions, the no-LLM path); a built-site check that a
figure from a measured sample carries `measured`, `calibrated`, or
`processed`, never `simulated`.

**Out of scope.** Any lab page (F60, F54, F53, F52); browser components
(F43); agents (F55).

**Dependencies.** F50 with at least one go decision; F28 (the format-2
page pattern, claim labels, and figure status the lab pattern and the
built-site check use), which carries to every lab built on this package.

**Acceptance criteria.** Each reader parses its committed sample and
asserts fields, shapes, units, masks, and cadence; the fitting helper
recovers known parameters of a synthetic test within stated tolerance and
reports uncertainty; a reference figure for each go dataset is regenerated
by the helpers and matches the dossier's; the no-network test of F50 still
passes; the new dependencies are locked and their licences recorded.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F60 — Gravitational-wave strain lab: from Kepler's orbit to a chirp

**Source.** Section 8.1 (LIGO GW150914 row: "later a stand-alone
gravitation/signals lab if scope allows"); Section 13, R3 ("a
planner-approved waves/signals lab"); the planner's recommendation under
"Experimental data choice". No candidate number; new ID.

**Goal.** The first measured-data lab of the mechanics course, conditional
on F50's go decision for GW150914: from the calibrated strain of the two
detectors to the chirp, and from the two-body orbit of M8 to the
Newtonian-order estimate of the chirp mass from the frequency and its rate
of change, compared with the published value, with every processing step
(bandpass, whitening, time-frequency resolution) disclosed and every claim
typed.

**In scope.** A lesson at the next order in the `mechanics` strand (ADR 008
decision 3; F46 may have taken an order before it), with `course:
mechanics`, methods `measured-data` and `simulation`, M8 among its
`prerequisites`, M8's front matter gaining the lab under `related` (links
are one-directional from the prerequisite side, F37), and the
previous-and-next prose of M8 and of the lesson before it checked after the
insertion; the committed 32 s sample
of each detector at 4096 Hz with its card and the GWOSC acknowledgement;
measured-versus-model panels (whitened strain against the Newtonian chirp
model and residuals); the spectrogram with an explained colour scale and a
static keyframe; a typed claim set: `observational` (the signal is present
in both detectors), `experimentally-supported` (the chirp-mass estimate,
an inference from the measured strain through the stated Newtonian model
with its uncertainty), and an explicit statement of what the Newtonian
model does not capture; the no-LLM path; the plain-language conclusion.

**Out of scope.** General relativity beyond the stated order-of-magnitude
model; matched filtering against a template bank; any claim of detection
significance beyond the published one, which is cited `observational`.

**Dependencies.** F51, F06. F50's go decision for the dataset.

**Acceptance criteria.** All the gates of Section 8.4 of the change
request: the sample parses with asserted fields; the reference figure is
regenerated from the committed sample with pinned settings; rights and the
acknowledgement are recorded and shown; every figure is labelled; the
measured strain stays distinct from the filtered signal and the model;
download and reproduction are versioned and tested; a no-LLM path exists;
the page is within the time and payload budgets, readable without
JavaScript, and accessible; the physical assumptions, the error metric,
and the interpretation are stated; an independent physics review confirms
the model statement and the claim types.

**Risk.** Medium: signal processing can mislead (a whitened signal is not
a measurement); the status labels and the review guard it.

**Detailed implementation plan expected.** Yes.

### F43 — Science-first visualization components

**Source.** Candidate F43; Section 8.3 (reusable visualization system).

**Goal.** At most four reusable browser components, built on the F07 widget
convention, that present verified data derived from executed cells: a field
viewer (scalar map with vector overlay and time slider over sparse verified
frames), an image-versus-model comparator (synchronized panes and
difference map on shared scales), a signal explorer (trace, filtered
signal, time-frequency view, model overlay), and a waveform comparator
(measured against simulated profiles with error metrics). A 3D viewer only
if a lab with settled rights and size needs it.

**In scope.** One component per lab that needs it, no component without a
lab; the on-demand data budget of the architecture (3 MB per page, own
origin, after a user action) with the built-site check; static keyframes
and captions in the page; keyboard and mobile operation; export of the
displayed values as text; the rule that a component never alters a claimed
observed value (a test that displayed values equal the embedded data).

**Out of scope.** A separate engine per lab; animation that cannot stop
under reduced motion; computing physics in the browser.

**Dependencies.** F07, F51; delivered component by component with F60,
F53, F52, F54 as each needs one.

**Acceptance criteria.** As F07's criteria for each component, plus the
on-demand budget check, the observed-value test, and a keyframe for every
animation.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, per
component.

### Wave R4 — Evidence and advanced labs

### F54 — Microwave S-parameter lab

**Reconciled by the change cycle `final-curriculum` (2026-10-12).** The
lab's course is `electromagnetism`, created by F72 (ADR 013); the references to
F15 below are history, F15 is dropped, and the `mechanics` framing is no
longer a route. The feature is otherwise unchanged and has no Issue; it
starts when F72 and its other dependencies are delivered.

**Source.** Candidate F54; Section 8.1 (NPL row, "strong low-friction
candidate").

**Goal.** From calibrated vector-network-analyser Touchstone `.s2p` files
to complex transmission and reflection, the Smith chart, and a fitted
transmission-line or lumped model, with the calibration assumptions,
passivity and energy context, and uncertainty quantified; power and
amplitude definitions distinguished; an optional focused Lean theorem on
the model (F56).

**Dependencies.** F51; F50's go decision; a course that exists. Every
lesson belongs to exactly one primary course and no lesson is placed by a
method tag (ADR 008 decisions 3 and 4, invariant I18), so this lab is
published only in an electromagnetism or waves-and-optics course. F15
yields one course of the human's choosing: if the human chooses one of
these subjects for F15, that course is the lab's home; otherwise the lab
waits for a later course feature, which takes the next unused ID when the
human asks for it. The only other route is the `mechanics` course if the
lab's Issue justifies that framing under ADR 008 decision 3, which the
planner does not expect because RF transmission is not the physics of the
mechanics course. The F50 dossier is evidence for the F15 choice.

**Acceptance criteria.** The gates of Section 8.4 as in F60.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F53 — Flow measurement lab with PIV fields

**Reconciled by the change cycle `final-curriculum` (2026-10-12).** The
lab's course is `fluids`, created by F73 (ADR 013); the references to
F15 below are history, F15 is dropped, and the `mechanics` framing is no
longer a route. The feature is otherwise unchanged and has no Issue; it
starts when F73 and its other dependencies are delivered.

**Source.** Candidate F53; Section 8.1 (cylinder-wake and Rostock rows).

**Goal.** From processed PIV velocity fields to vorticity, streamlines, and
the vortex-shedding frequency and Strouhal number, with the field viewer of
F43; raw frames distinguished from PIV-derived fields; masked regions and
cadence handled explicitly; a compact local subset designed from the 1.1 GB
file, or the small Sheffield or OpenPIV example, either usable only after
its `survey-only` card and a feasibility spike with a go decision under F50
(its provenance check).

**Dependencies.** F51, F43; F50's go decision; a course that exists: a
fluid-dynamics course if the human chooses that subject for F15 (F15
yields one course), otherwise a later course feature that takes the next
unused ID when the human asks for it, or the `mechanics` course if the
lab's Issue justifies that framing under ADR 008 decision 3 (vortex
shedding as the fluid mechanics of the course), the one lab for which that
framing is plausible. No placement by method tag (ADR 008 decision 4).

**Acceptance criteria.** The gates of Section 8.4; the committed subset
under the caps; the animation with a keyframe within the on-demand budget.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F52 — Optical diffraction lab

**Reconciled by the change cycle `final-curriculum` (2026-10-12).** The
lab's course is `waves`, created by F71 (ADR 013); the references to
F15 below are history, F15 is dropped, and the `mechanics` framing is no
longer a route. The feature is otherwise unchanged and has no Issue; it
starts when F71 and its other dependencies are delivered.

**Source.** Candidate F52; Section 8.1 (Fraunhofer row).

**Goal.** From a measured far-field diffraction photograph to the Fourier
optics model, side-by-side measured and simulated intensity with residuals,
uncertainty, and inference of the grating geometry, with the comparator of
F43. The record page (Zenodo 19436924) shows a CC BY 4.0 licence field next
to a copyright line and the change request flags redistribution as unclear;
the gate decides, and still verifies the terms of the photographs, the RAR
extraction in a locked environment, and the sample size.

**Dependencies.** F51, F43; F50's go decision; a course that exists: the
waves-and-optics course if the human chooses it for F15 (F15 yields one
course), otherwise a later course feature that takes the next unused ID
when the human asks for it. No placement by method tag (ADR 008 decision
4); a `mechanics` framing under ADR 008 decision 3 is not plausible for
diffraction, so this lab has no home until a waves-and-optics course
exists.

**Acceptance criteria.** The gates of Section 8.4.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F55 — Agent-assisted experimental physics

**Source.** Candidate F55 (lesson only; the workflow is F45's); Section 12
(F45 + F55).

**Goal.** One lesson that applies the F45 workflow to a measured dataset
with a go decision: inspect, specify, implement the analysis in Python with
a coding agent, visualize, validate independently against the F51
reference, and report; no second workflow and no shell access beyond the
F45 profile.

**Dependencies.** F45; one of F60 or F54.

**Acceptance criteria.** As F45's criteria on the chosen dataset; the
agent's result is compared with the verified reference analysis and the
difference reported.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F23 — Inverse physics: parameter discovery with uncertainty

**Source.** Candidate F23; Section 12 (F20 + F23).

**Goal.** Fit model parameters to measured or synthetic observations,
quantify residuals, uncertainty, and identifiability, and show when a fit
is not evidence; an optional bounded agent in the harness proposes fits.

**Dependencies.** F51; one of F60 or F54 for the measured case.

**Acceptance criteria.** The fitting helpers recover synthetic parameters
within tolerance and report a non-identifiable case as such; the measured
case states its uncertainty; claims typed; the usual lesson checks.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F47 — Automated analysis pipelines

**Source.** Candidate F47 (lesson; its core merged into F51).

**Goal.** A lesson that builds a reusable analysis and report workflow on
`pbc.data`: parameter sweeps, statistics, uncertainty, figures, and a
reproducible report generated by the build, shown on one simulated and one
measured problem.

**Dependencies.** F51.

**Acceptance criteria.** The report is regenerated by the build and
compared with a committed expectation at displayed precision; the usual
checks.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F18 — Multi-agent scientific review

**Source.** Candidate F18 (shares the contract of F46); Section 12.

**Goal.** Independent review agents in the ADR 004 harness, one for
physical assumptions, one for the numerical implementation, one for the
evidence, each with bounded local tools over `src/pbc` and the F46
contract; visible disagreement and resolution; reproducible transcripts
replayed in CI; a lesson that reviews a piece of lesson code and a faulty
variant.

**Dependencies.** F09, F46.

**Acceptance criteria.** Each reviewer's tool results are recomputed by the
build; the faulty variant is flagged by at least one reviewer through a
recomputed check, not through prose; the ADR 004 boundary holds; no new
orchestration framework beyond the harness loop run three times.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F19 — Scientific evidence map

**Source.** Candidate F19.

**Goal.** A static, accessible page that lists every typed claim of the
site with its scope and links it to its evidence: the executed cell, the
sample and card, the replayed agent run, or the Lean theorem; generated
from the claim markup of format 2 through the `evidence` attribute that
F28 reserves and the editorial passes fill, so this feature adds only the
page and the check, not a format change.

**Dependencies.** F28, F29, F30, F31 (every lesson in format 2), F37.

**Acceptance criteria.** Every claim on the site appears once with its type,
scope, lesson, and evidence link (test); the page reads without JavaScript
and passes the accessibility scan; a claim without an `evidence` attribute,
or whose attribute names no existing cell, register or card key, or Lean
theorem, fails the build.

**Risk.** Low. **Detailed implementation plan expected.** No.

### F56 — Lean proofs for the models of measured-data labs

**Source.** Candidate F56; Section 12 (F17 + F56 + F22).

**Goal.** Prove selected exact properties of the mathematical models or
numerical schemes a lab uses (for example passivity or energy relations of
the transmission-line model of F54, or a property of the fitting scheme),
never of the data or the Python; delivered as lessons in the `lean` strand
with `course` set to the lab's course and the lab among their
`prerequisites`; the lab's front matter gains the proof lesson under
`related` (links are one-directional from the prerequisite side, F37).

**Dependencies.** F17, F54 (or the first lab whose model has a provable
property).

**Acceptance criteria.** As F08 and F17; the page states that the theorem
proves nothing about the measurement.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### Wave R5 — Research capstones

### F20 — Autonomous experimental design

**Source.** Candidate F20; Section 12 (F20 + F23).

**Goal.** An agent in the harness chooses measurements and parameters under
a budget to discriminate between competing models, estimates uncertainty,
and has its conclusions independently assessed; built on the F16 loop and
the F23 fitting helpers.

**Dependencies.** F16, F23.

**Acceptance criteria.** The chosen design is recomputed and scored by the
build; the agent's conclusion is typed only as the recomputed evidence
supports; replay passes.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F21 — Interactive Lean exercises

**Source.** Candidate F21.

**Goal.** Learners complete pinned Lean exercises locally; the site shows
the statements, hints, and checked solutions without in-browser Lean.

**Note for planning.** Exercise stubs contain `sorry`, which invariant I12
forbids in `lean/`. The feature plan must propose, as a new ADR, a declared
exercise location outside the checked library (for example a second Lake
package `lean-exercises/`) whose solutions live in the checked library, with
a check that every stub has a solution that builds without `sorry`; the
site shows stubs "not verified" and solutions by reference.

**Dependencies.** F17.

**Acceptance criteria.** Every stub has a checked solution; the hints
render as details without JavaScript; the exercise package builds within
the Lean budget; the ADR is accepted.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F22 — Agent-assisted theorem proving

**Source.** Candidate F22; Section 12 (F17 + F56 + F22); ADR 010.

**Goal.** A local, constrained workflow under the F45 profile: conjecture,
counterexample search with F16's loop, Lean formalization by a coding
agent, proof checking with `lake build`, and human semantic review, starting
from the known reference proofs of F17 and F21.

**Dependencies.** F21, F45.

**Acceptance criteria.** Any proof shown on the site is compiled by CI like
every proof; the agent's transcript is "not verified"; the page states
what a compiled proof does and does not establish; the security review
approves the profile for Lean.

**Risk.** High (agent-written code on the learner's machine).
**Detailed implementation plan expected.** Yes.

### F49 — Research capstone: reproduce an open physics paper with a multi-agent team

**Source.** Candidates F48 and F49, merged (Section 12: "a single capstone
may be preferable").

**Goal.** One capstone project: reproduce a focused open-access paper (DOI,
parameter provenance, fit and figure comparison, a residual discrepancy
report) with a planner, a coder, an analyst, and independent reviewers
built from F45, F46, F47, and F18; human review required; no new
orchestration framework.

**Dependencies.** F18, F45, F46, F47.

**Acceptance criteria.** The reproduced figures are regenerated by the
build from documented inputs under the dataset rules; discrepancies are
reported as such, typed, and not explained away; the reviewers' recomputed
checks are shown; the paper's licence and the data rights are recorded.

**Risk.** High (scope). **Detailed implementation plan expected.** Yes,
likely several Issues.

## Phase 4 — Final curriculum (change cycle `final-curriculum`)

Every feature in this phase comes from `docs/changes/final-curriculum.md`
(revision 3, 2026-10-10) and the requirements re-approved with it on
2026-10-12 (decisions 23 to 31); each block names the slots of the
reference curriculum it fills and the section of the change request it
comes from. The wave C0 and the discovery foundation F65 are specified in
detail, because they are the first wave and everything else depends on
them. Waves C1 to C4 are deliberately coarser: revalidate each feature
against the architecture, the requirements, the curriculum file, and the
delivered features before creating its Issue, and expect a feature plan to
refine it. The human approves each course's concrete lesson list in the
Issues before drafting (requirements, unresolved question 6).

What every feature of this phase inherits, without repeating it in each
block:

- **The gates** (requirements decisions 29 and 30). Every feature that
  publishes a lesson in this phase depends on F61 (verification
  proportional to the change) and F62 (the courses, the curriculum file,
  and the `slot` field its lessons must carry), whether or not its block
  names them: no lesson of this phase is drafted, and no Issue for one is
  created, before both are delivered. Every lesson feature of waves C2,
  C3, and C4, which is the bulk of the new lessons, additionally depends
  on F64 (the Learning Path redesign). The dependency tables and the
  blocks repeat these gates so that `create-feature-issue.sh` sees them;
  this rule is the source when a block is terser. There is no exception
  for cost: departing from a gate is a change to the requirements, not a
  scheduling choice.
- **The full-run gate** (ADR 014 decisions 7 and 11). Every job of a full
  run must fit the job timeout, and until F113 is delivered a full run is
  the one `build` job of ADR 012, which fits the budget up to the
  lesson-shard size of 32 lessons. A lesson feature of wave C1 depends on F113 unless
  the lesson count it brings the site to is at most 32 (twenty-two today,
  so room for about ten lessons, in the order the human creates the
  Issues); every lesson feature of waves C2 to C4 depends on F113 as it
  depends on F64. The dependency table marks the wave C1 features "F113
  by the lesson-shard rule" and names F113 outright from wave C2 on; F61
  records the measured count at which the one job leaves the budget, and
  if that count is below 32 no lesson feature starts before F113.
- **The invariants and the lesson model** of `docs/architecture.md`,
  including the reference curriculum and the slot (ADR 013), the
  verification selection (ADR 014), and the format-2 lesson checks of
  `docs/authoring.md`.
- **The definition of done of a lesson** (change request, section 11;
  requirements decision 31): substantive physics at its stated level with
  the physical question, assumptions, essential derivation, units, and
  domain of validity; runnable pinned code and figures the build
  regenerates; interpreted figures with provenance labels; honest numerical,
  epistemic, and empirical limitations; typed claims with evidence; unique
  identifier, course, slot, methods, difficulty, validated prerequisites,
  outcomes, and related links; exercises, a self-check, accessible labels,
  and a tested "Reproduce this" path; references from the register; focused
  tests for the code it adds; applicable checks passing within the budgets;
  and an independent scientific review before merge. No live LLM or API
  call is a required check.
- **A feature may deliver exactly one slot.** There is no rule that a slot
  is a feature, and none that it is not (requirements, later phases and
  decision 31; change request, section 2, point 10). Until 2026-10-13 the
  sentence of the later phases read "no feature equals one slot", against
  decision 31; the project owner corrected it on that day to the wording of
  decision 31. The features of this roadmap that deliver one slot stand.
- **The placement rule**: a lesson of a course's physics lives in the
  course's strand at the next free order, with `course` and `slot` set; a
  lesson whose subject is a method lives in `agents-llm` (the method paths),
  `agents-abm`, or `lean`, with the primary course of the physics it uses.
  The first lesson feature of a course creates its strand directory and its
  package under `src/pbc` (ADR 013). Related links are one-directional from
  the prerequisite side (F37).
- **The lab rule** (requirements decisions 18 and 27; ADR 007): a
  measured-data lab feature starts with the feasibility spike of its
  candidate dataset under the F50 process (card, inspected file, artifact
  labels, reference figure from source-controlled code, rights, sizes,
  dossier) and waits for the human's go decision; on defer or reject the
  feature records the decision on its card and dossier and stops, or
  proposes another candidate in a new spike. A lab then meets the gates of
  section 8.4 of `docs/changes/physics-next-phase.md` as F60 did: sample
  under the caps with a parsing test, regenerated reference figure, rights
  and attribution shown, every figure labelled, measurements distinct from
  processed signals and models, versioned and tested download, a no-LLM
  path, the page within the time and payload budgets, the physical
  assumptions, error metric, and interpretation stated, and an independent
  physics review of the claim types. No dataset is accepted because the
  curriculum names it; only GW150914 strain, the Aalborg wave flume, and
  the NPL S-parameters have a go decision today.
- **The capstone rule** (change request, section 4.1; requirements
  decision 26, non-goals, and "Content integrity"; architecture, "Applied
  capstone and numerical-engineering lesson"): a verified progression from
  the precursor lessons; a bounded workflow from physical requirements to a
  qualified decision; comparison with an analytical, manufactured,
  independent, or trusted numerical reference; refinement and genuine
  failure modes; the credibility boundary stated and typed; the required
  path on the pinned stack within the page budget; heavy tools optional,
  with their outputs as declared `modelled-reference` inputs.
- **The agent rule** (requirements decision 25; ADR 004; architecture,
  "Law-discovery environment and agent benchmark"): bounded allowlisted
  tools, a budget, versioned model and prompt, a frozen replay the build
  recomputes, the hidden truth never reachable, non-agent baselines,
  hold-outs, seeds where needed, visible failures, and heavy runs outside
  `verify.conf`.
- **No hardware** (requirements decision 28): no lesson builds a sensor
  experiment, records audio, collects classroom or smartphone data, or
  controls an instrument; the acoustics lesson is numerical, and the
  video-reasoning lesson uses generated or rights-cleared existing clips.

Risk levels follow `.agents/policies/autonomy.md`: every lesson feature is
at least Medium (independent scientific review); a feature that changes CI,
workflow permissions, or the required check is High.

### Wave C0 — Governance, verification, and the learning path

Order within the wave, by dependency: F61 and F62 are independent of each
other and may run in parallel worktrees; F113 after F61; F63 after F62;
F64 after F63. F61 and F62 precede the first lesson feature of this phase
(requirements decision 30; the gates under "Phase 4"): until F61 lands,
every new lesson would add about 45 seconds of runner time to every pull
request, and until F62 lands a lesson cannot carry a validated `slot`.
F113 precedes every lesson feature that would take the lesson count past
32 (the full-run gate), and F64 precedes the lesson features of waves C2
to C4 (requirements decision 29).

### F61 — Verification proportional to the change

**Source.** Change request section 15; requirements decision 30 and
"Runtime and deployment constraints"; ADR 012 decisions 8 and 9; ADR 014,
proposed with this planning and accepted when it is approved.

**Problem.** Every pull request executes every lesson three times and
checks every page. With twenty-two lessons a run takes 18 to 25 minutes
against a budget of 12; at 110 lessons the site build alone would take
about 19 minutes. The verification cost must depend on what a pull
request changes, not on the size of the curriculum, without dropping a
check, without a check that exists only in CI, and with the published site
still the site that was verified in full.

**Goal.** Implement ADR 014: a pull request executes and checks the
lessons whose input digest changed against the verified result of the
latest successful run on `main`, and every page whose bytes differ from
it; what a page shows of its context (navigation, slot, the commit it
names) is produced by every build and never taken from the base; a check
is reused only from a base the same check implementation produced;
`main` verifies everything and publishes the base; the selection lives in
`./scripts/verify.sh`.

**User-visible outcome.** A contributor who changes one lesson sees the
`verify` check finish within 12 minutes; a contributor who changes shared
code, the checks themselves, or a lesson whose inputs cannot be followed
sees a full run, as before. Locally, `./scripts/verify.sh` without
options is unchanged; with the base option it runs the same selection CI
runs. Nothing on the published site changes.

**In scope.**

- The input digest of a lesson (ADR 014 decision 1) as one function in the
  authoring package, with a test that each kind of input (lesson source,
  fixture, an imported `src/pbc` module and a module it imports, a sample
  and its card, a displayed Lean module, the toolchain and manifest, the
  Python pins, each shared site file, `src/pbc/authoring`) changes the
  digest, and that a lesson with a dynamic import, a composed path, a
  non-Python cell, or a read outside the known locations has no digest.
  The digests of every lesson are written beside the built site.
- The base option of `./scripts/verify.sh`: it names a directory that
  holds the base (site checksums, executed results, digests); the script
  computes the selection once and writes it where the checks read it; a
  run without the option runs everything; `--only` and the base combine as
  CI needs; the record of a run with a base names the base.
- The site build with a base: the executed results of the base are
  restored, the entries of every changed lesson are removed, Quarto
  executes the changed lessons and renders every page; the time of each
  executed lesson is measured and compared with the 30-second budget. The
  default build writes the store, which `.gitignore` lists and the
  committed-artifact check rejects. The determinism check starts its second
  build from the same restored state. The reproduction check and the
  per-page checks read the selection: the reproduction runs for changed
  lessons; the per-page checks run for the pages whose bytes differ from
  the base, found by comparing the built site with the base's checksums
  after the build commit is normalised in both.
- The context of a page regenerated on every build (ADR 014 decision 9):
  the header (`lesson_header`: previous and next, prerequisites, related
  lessons, course, slot, path position) and the provenance helpers
  (`reproduce_this`, the excerpt and Lean helpers, which embed
  `build_commit()`) stop being replayed from the store. The feature picks
  the mechanism (the helpers move out of the executed cells into a build
  step such as a filter or a post-render over marked regions, or the
  store is written without the outputs of those cells and they run on
  every build) and changes the lesson template and the authoring helpers
  once; lesson bodies stay as they are. The store entries of the pages
  that are not lessons (home, path, evidence map, glossary, about) are
  never restored.
- The identity of the checks (ADR 014 decision 10): one digest over
  `scripts/verify.sh`, `scripts/verify.conf`, `scripts/build-site.sh`,
  `scripts/check-determinism.sh`, `tests/e2e`, `tests/support`,
  `tests/integration`, `tests/e2e/shards.json`, `pyproject.toml`,
  `uv.lock`, and the browser tooling the runner preparation installs,
  written into the base beside the lesson digests. When the current
  tree's identity differs from the base's, nothing of the base is
  restored: the run executes every lesson, checks every page, and
  reproduces every lesson against its own results, and its record says
  why; no reproduction ever compares bytes with a result of the base
  (ADR 012 decision 4). A split per check group is allowed only with a
  test that shows each group's inputs are complete.
- The workflow: a `main` run uploads the base (executed results and
  digests beside the site artifact of ADR 012) after `verify` passed; a
  `pull_request` run retrieves the latest base read-only (a read permission
  on the artifacts of earlier runs, or the cache of the default branch,
  whichever needs the smaller permission and is tested) and accepts it
  only by its provenance (ADR 014 decision 2): the run that produced it
  is a `push` run on `refs/heads/main` whose aggregate `verify` check
  concluded with success, established from that run's recorded event,
  branch, and conclusion, never from the artifact's name, its recency,
  or its contents; a pull request run, including one from a fork,
  uploads the built site for review and must not be able to supply a
  base. The contents of a base are data: the workflow and the script
  execute nothing from it and read nothing in it as configuration. The
  run then verifies that the accepted base is complete and of the
  current format and passes it to the script, or runs without it. If
  the feature chooses the cache of the default branch, its plan records
  why the cache's scoping gives the same guarantee (an entry is written
  only by a `main` run after `verify` passed, a pull request run reads
  the default branch's entries and can never write one that a later
  pull request reads, and a fork pull request writes nothing) and a test
  shows it. A run on `main` never receives a base; a test of the
  workflow file shows it.
- Tests in `tests/integration`: the selection names exactly the lessons
  whose digest differs; a lesson without a digest selects every lesson; a
  changed shared input of ADR 014 decision 4 selects every lesson, one
  test per input; a changed module of `src/pbc` selects every lesson that
  imports it directly or through another module, and every lesson when
  its importers cannot be followed; a missing, truncated, or older-format
  base selects every lesson; an artifact of a pull request run and an
  artifact of a `main` run whose `verify` did not succeed are each
  rejected as a base and the run executes every lesson, one test per
  rejected case, with the provenance read from the producing run's
  event, branch, and conclusion and not from the artifact's name or
  upload time; a failing changed lesson fails the run; a page that
  differs from the base is checked and a byte-identical page is not; the
  workflow passes a base only on pull requests and keeps `contents: read`
  with the one added read scope.
- Tests of the regenerated context, on a run with a base built from a
  fixture site: inserting a lesson between two unchanged ones updates
  their previous and next links and the path page; retitling an unchanged
  lesson updates every unchanged page that links to it (previous, next,
  prerequisites, related); adding a prerequisite or a related link to a
  changed lesson updates the unchanged page it points at where that page
  shows it; the "Reproduce this" section and every code and Lean excerpt
  of an unchanged page name the commit of the run, never the commit of
  the base, and the page the reader gets is the page that was checked.
- Tests of the check identity: a change to each input of the identity (a
  test file of `tests/e2e`, a module of `tests/support`, the verification
  script, its configuration, `tests/e2e/shards.json`, the build or
  determinism script, `uv.lock`) makes the run a full run in which every
  lesson is executed, every page checked, and every lesson reproduced
  against this run's results, with nothing restored from the base; an
  unchanged identity reuses the checks as decision 3 says; a base without
  an identity runs everything.
- The measurement: three consecutive pull requests that change one
  lesson, their wall clock and the render time per page without execution,
  recorded in the pull request and in `docs/release-readiness.md`; the
  projection to 110 lessons from the measured per-page render cost. The
  render is measured on a build that executes no scientific cell and
  runs the context cells of ADR 014 decision 9 if the feature keeps them
  as executed cells, which is the build the assembly of F113 makes, so
  the figure carries over to it. The full run on `main` as well: the
  time of the `build` job with warm and with cold caches and its cost
  per lesson on the slowest runner of those runs, projected to 110
  lessons, and the lesson count at which that one job leaves the
  full-run budget of ADR 014 decision 7 (35 minutes with cold caches),
  which is the count the full-run gate of this phase uses until F113
  lands.
- `docs/architecture.md` ("Inside one verification run", "CI pipeline and
  time budget"), `docs/deployment.md`, and `docs/development.md` updated;
  the acceptance of ADR 014 recorded in its status with the merge.

**Out of scope.** Selecting the Lean build (requirements, unresolved
question 8), the integration tests, or the workflow self-tests; a
schedule; a path filter in the workflow file; changing what any check
checks; self-hosted runners; the job timeout, which stays 45 minutes, and
the lesson shards and assembly of a full run (ADR 014 decisions 7 and 11;
F113).

**Dependencies.** F58 (the parallel jobs, the single built site, and the
checksums the comparison with the base reuses).

**Acceptance criteria.**

1. Three consecutive warm-cache pull requests that each change one lesson
   finish within 12 minutes wall clock; the times, the number of lessons,
   the per-page render cost without execution, and the projection to 110
   lessons are recorded in `docs/release-readiness.md`.
2. A pull request that changes one lesson executes that lesson in the
   build and in the second build, reproduces it, and checks its page and
   every page whose bytes differ from the base, and nothing else of the
   lesson checks; shown by the run's record and by a test.
   The pages of that run show the navigation of the pull request's tree
   and name its commit: the tests of the regenerated context (lesson
   insertion, retitling, prerequisite and related links, commit
   provenance) pass, and the attached site artifact of the pull request
   is inspected for the previous, next, and "Reproduce this" of one
   unchanged page.
3. A pull request that changes a shared input of ADR 014 decision 4
   (`uv.lock`, `pyproject.toml`, `.python-version`, a file of
   `src/pbc/authoring`, `site/_quarto.yml`, a template, filter, asset, or
   shared site file, the glossary, the reference register, the curriculum
   file, the Lean toolchain or manifest) executes every lesson; one that
   changes a module of `src/pbc` executes every lesson that imports it
   directly or through another module, and every lesson when the
   module's importers cannot be followed; shown by a test per input kind.
4. A run on `main` executes and checks every lesson and publishes the base
   only after `verify` passed; a test of the workflow file shows no base
   reaches a `main` run, that a pull request run accepts a base only from
   a `push` run on `refs/heads/main` whose `verify` succeeded, and no job
   gained write permissions.
5. A run in which any lesson's inputs cannot be followed, a run whose
   base is missing or of another format, and a run offered an artifact
   of a pull request run or of a `main` run whose `verify` did not
   succeed (rejected by its provenance) execute every lesson; a test per
   case. A pull request that changes a test of the built site,
   a support module, the verification script or its configuration,
   `tests/e2e/shards.json`, the build or determinism script, or `uv.lock`
   is a full run: it executes every lesson, checks every page, and
   reproduces every lesson against its own results with the current
   checks, restoring nothing from the base; a test per input of the
   identity shows it and shows that no reproduction compared bytes with a
   result of the base, and the record of such a run says why it ran in
   full.
6. `./scripts/verify.sh` without options runs every check as before; with
   the base option it selects as CI does; a test covers both, and a local
   run of the selection on a laptop matches the selection CI made for the
   same base.
7. No check left `scripts/verify.conf`, every group still runs in exactly
   one job, and the published site of `main` is the fully verified one
   (the tests of F58 still pass).
8. ADR 014 is accepted with the merge; ADR 002, ADR 003, and ADR 012 name
   it in their status.
9. The full run on `main` is measured (the `build` job with warm and with
   cold caches, its cost per lesson taken on the slowest runner of those
   runs) and projected to 110 lessons; the projection and the lesson
   count at which the one job leaves the
   35-minute budget of ADR 014 decision 7 are recorded in
   `docs/release-readiness.md`. That count is at least the lesson-shard
   size of 32 lessons (ADR 014 decision 11), which the measured cost
   confirms or lowers and never raises; if it is lower, F113 reduces the
   lesson-shard size accordingly and no lesson feature starts before F113.

**Risk.** High. The feature changes the CI workflow, a workflow
permission, and the merge gate's meaning on pull requests, which need
explicit human approval and security-focused review; the digest is a new
guarantee whose completeness the tests must demonstrate; the render cost
of unchanged pages may dominate at 110 lessons, which criterion 1 measures
and reports rather than hides.

**Detailed implementation plan expected.** Yes.

### F113 — Bounded full verification: same-machine lesson shards of the build

**Source.** ADR 014 decisions 7 and 11; ADR 012 decisions 2, 3, 4, 6, and
9; requirements, "Runtime and deployment constraints" (every push to
`main` executes and checks every lesson; the site is served from a
verified build of `main`; the planner sets a concrete budget); change
request section 15 (the cost per lesson).

**Problem.** The `build` job of ADR 012 holds the three executions of
every lesson (the build, the second build for determinism, the
reproduction in a fresh clone), which compare bytes and have to run on one
machine. It took 20 min 27 s with cold caches at twenty-two lessons; at
about 41 seconds per lesson it leaves the full-run budget of 35 minutes
at about 40 lessons and needs about 80 at 110, against a timeout of 45.
F61 makes a pull request pay for what it changed, but a run on `main`
and a full-run pull request still execute every lesson, and a run on
`main` that times out publishes nothing.

**Goal.** Implement ADR 014 decision 11: a full run executes the lessons
in same-machine lesson shards of at most 32 lessons, each making its
comparisons of bytes on its own machine, and one assembly renders the one
built site from their results, so that every job of a full run fits the
timeout at 110 lessons without a tolerance, a dropped check, or a raised
timeout. A lesson shard is a share of the lessons that the script derives
from their count; it is not the division of the built-site tests in
`tests/e2e/shards.json` (F58, ADR 012), which this feature leaves as it
is. "Shard" alone in this block means a lesson shard.

**User-visible outcome.** A push to `main`, and a pull request that is a
full run, finish within the job timeout at any size of the curriculum up
to 110 lessons; a contributor still sees one required check, `verify`;
the published site is still one site verified in full. Locally,
`./scripts/verify.sh` without options is unchanged.

**In scope.**

- The lesson-shard and assembly modes of `./scripts/verify.sh`:
  `--shard k/N` runs the group `build` on the k-th lesson shard, which the
  script assigns from the lesson list in a stable order with at most `S`
  lessons per shard, `S = 32` declared in `scripts/verify.conf` and `N`
  the ceiling of the lesson count over `S`, never read from a file; the
  assembly mode names the parts to assemble. Both are partial runs like
  `--only` and verify nothing by themselves; a run without options
  executes everything in one build on one machine, as today.
- The shard run: the Lean build in full; the execution of the share and
  its second execution for determinism; the render of the share's pages;
  the reproduction of each lesson of the share in a fresh clone against
  the pages and figure files this shard rendered; the publication of the
  part (the share's entries of the store, its rendered pages and figure
  files) with the checksum of every file, as a job artifact.
- The assembly: retrieve the parts; require that every file is the
  recorded one and that the parts cover every lesson exactly once; render
  every page from the union of the parts (and, on a pull request, the
  base for the unchanged lessons) without executing a scientific cell of
  any lesson, with the context of ADR 014 decision 9 from the current
  tree (if F61 kept the header and provenance helpers as executed cells,
  the assembly runs those context cells and nothing else of a lesson);
  the assembly's runner prepares what those context cells read, in
  particular the Lean build record the Lean excerpt helper checks
  (architecture, "Formal proof lesson"), restored from a shard's part
  and required equal across every part, or recreated by the Lean build,
  which is cheap with Mathlib's cache, the plan stating which; the
  assembly's cost is then the render cost F61 measured on a build of
  the same shape; render a second
  time and compare the bytes on the same machine; require that each
  lesson page equals the page its shard rendered and reproduced; upload
  the one site with its checksums (ADR 012 decision 6); on `main`,
  publish the base of F61 from the assembled results.
- The workflow: `build` becomes a matrix of lesson shards and `assemble`
  a job after them; the `e2e` jobs download the assembled site and keep
  their division of `tests/e2e/shards.json`; `deploy` is unchanged. The
  number of lesson shards is derived from the lesson count by the
  script, and the workflow's lesson-shard count equals that derivation (`N` the
  ceiling of the lesson count over `S`, ADR 014 decision 11), never more
  and never fewer: either a job computes the matrix from the script's
  output, or the matrix is static and is bumped exactly when the lesson
  count crosses a multiple of `S`, and the test asserts equality between
  the workflow's shards and the script's, so that an over-covering matrix
  fails as an under-covering one does (an idle shard still prepares a
  runner, and the requirement is a bounded full run, not a padded one);
  the feature chooses the simpler one that needs no permission and tests
  it.
- Tests in `tests/integration`: the lesson shards cover every lesson
  exactly once and none exceeds `S`; the workflow's lesson shards equal
  the script's; a
  failing shard fails `verify`; a missing, extra, or altered part fails
  the assembly; a lesson page that differs from its shard's fails the
  assembly; no shard uploads a Pages artifact; the tests marked
  `same_machine` run on the machine that computed the bytes they compare
  with (ADR 012 decision 4, extended); a local run without options is
  unchanged in meaning; workflow permissions stay `contents: read` with
  write scopes only in `deploy`.
- The measurement: one full run on `main` with warm caches and one with
  cold caches (as F58 measured), the time of every shard and of the
  assembly, the cost per lesson on the slowest runner of those runs,
  recorded in the pull request and in `docs/release-readiness.md`, with
  the projection to 110 lessons (four shards) against the 35-minute
  budget of ADR 014 decision 7, and the shard size `S = 32` confirmed or
  lowered from that cost. And, by the protocol of F61 criterion 1, three
  consecutive warm-cache pull requests that each change one lesson on
  the sharded workflow: their wall clock, the assembly's time, and the
  projection to 110 lessons, recorded in `docs/release-readiness.md`,
  because the assembly is a second step on the longest path of every
  pull request and the 12-minute budget of requirements decision 30 must
  be established on the workflow shape that persists.
- `docs/architecture.md` ("CI pipeline and time budget", "Inside one
  verification run"), `docs/deployment.md`, and `docs/development.md`
  updated; the status of ADR 012 and ADR 014 records the delivery.

**Out of scope.** Changing what any check checks; selecting the Lean
build (requirements, unresolved question 8); a tolerance in any
comparison of bytes; raising the job timeout, which is the fallback of ADR
014 decision 11 and needs a revision of that record; self-hosted runners;
changing the pull request budget (F61 sets it; criterion 5 re-measures
it on the sharded workflow).

**Dependencies.** F61 (the store, the selection, the regenerated context,
and the base, which the shards and the assembly reuse), F58.

**Acceptance criteria.**

1. A full run on `main` at the lesson count of its day, with warm caches
   and with cold caches, finishes with every job within 35 minutes; the
   times per shard and for the assembly, the cost per lesson on the
   slowest runner of those runs, and the projection to 110 lessons with
   every job within 35 minutes are
   recorded in `docs/release-readiness.md`; that cost confirms the shard
   size of 32 lessons or the feature lowers it (ADR 014 decision 7).
2. The published site is one site rendered by the assembly; every lesson
   page of it is byte-identical to the page its shard reproduced; the
   `e2e` jobs check that site and `deploy` publishes it; a test shows
   that no shard uploads a Pages artifact.
3. The lesson shards cover every lesson exactly once, none exceeds 32
   lessons, their number is derived from the lesson count and read from
   no file, and the workflow's lesson shards equal the script's; a test
   per property.
4. A failing shard, a missing or altered part, and a lesson page that
   differs from its shard's each fail `verify`; a test per case.
5. A pull request with a base runs the same jobs; a shard with nothing
   to execute finishes in its fixed cost; three consecutive warm-cache
   pull requests that each change one lesson, measured as F61 criterion
   1 measures them, finish within 12 minutes wall clock on the sharded
   workflow, with their times, the assembly's time, and the projection
   to 110 lessons recorded in `docs/release-readiness.md`.
6. `./scripts/verify.sh` without options runs every check in one process
   on one machine as before; `--shard` and the assembly verify nothing by
   themselves; a test covers both.
7. Every group runs in exactly one job or one shard matrix; the tests
   marked `same_machine` run on the machine of the bytes they compare
   with; permissions are unchanged (the tests of F58 and F61 still pass).
8. The status of ADR 012 and ADR 014 records the delivery.

**Risk.** High. The feature changes the CI workflow and the deploy chain,
which need explicit human approval and security-focused review.
Technical risk: the assembly's render of a page from a shard's results
must equal the shard's render of it on another machine; the store holds
the executed outputs and the figure files as bytes, so the render should
not depend on the machine, and criterion 2 proves it on the hosted
runners. If it does not hold, the feature records the evidence and stops,
and the fallback of ADR 014 decision 11 is decided by the human as a
revision of that record.

**Detailed implementation plan expected.** Yes.

### F62 — Eight courses and the reference curriculum

**Source.** Change request sections 2, 3, 9, and 12 (decisions 5 to 7);
requirements decisions 23 to 25 and unresolved question 6; ADR 013,
proposed with this planning and accepted when it is approved.

**Problem.** The site has one course and no record of the reference
curriculum: no stable identifiers for the other seven courses, no place
for a planned lesson that is not a placeholder page, no way to show the
four method paths, and a hand-kept planned list on the home page that
names a delivered feature and a dropped one.

**Goal.** Implement ADR 013: the eight course identifiers and the strand
order; the curriculum file with the 115 slots, the four method paths, and
every slot's home and kind; the `slot` front-matter field with its checks;
the migration of the twenty-two published lessons; the path page and the
home page reading the planned structure from the file and every published
fact from front matter.

**User-visible outcome.** The learning path page lists the mechanics
course with its published lessons and, visibly distinguished, its planned
slots; names the seven courses that have no lesson yet in one sentence;
shows the four method paths as a secondary view with their published
lessons in path order and their planned slots; keeps every method view and
every link. The home page's planned list names the courses and paths of
the reference curriculum with their real published counts. A lesson header
shows the lesson's slot and, for a method-path lesson, its position in its
path. Every existing URL still works.

**In scope.**

- `COURSES` with the eight identifiers and titles of ADR 013 decision 1;
  `STRANDS` in the order of decision 2 (courses first, then the three
  method strands), with the display title of `agents-llm` refined to name
  physics and AI; a course still appears as a course only when it has a
  lesson.
- The curriculum file (site/curriculum.yaml), read and validated by
  `pbc.authoring.path`: the eight courses, the four paths, and the 115
  slots of the requirements' decision 23 with label, working title, home,
  position in the path where applicable, and kind; a schema check that
  rejects an unknown course or path, a duplicate label, a slot without a
  home, a slot with both a course and a path, and any field that belongs
  to front matter.
- The `slot` field: optional, unique, naming an existing label; the lesson
  source check fails on an unknown label, on two lessons with one slot,
  and on a lesson whose `course` is not the home of a slot homed in a
  course (a slot of a method path may be filled by a lesson of any
  course); the seventeen published lessons that fill a slot of their own
  course or of a path migrate (M1 to M8, M16, AI0, AI2, AI3, AI4, D6, D9,
  R1, L1 as listed under "State at the change cycle `final-curriculum`");
  the gas lesson gets no slot in F62 and keeps `course: mechanics`: F70
  sets `slot: T0` and `course: thermodynamics` together (ADR 013 decision
  6), and until then T0 is an unfilled planned slot of a course that has
  no lesson, named in the one sentence and shown nowhere else; the four
  Lean lessons beyond the baseline get no slot; front matter only, bodies
  byte-identical.
- The path page: planned slots per course and per path from the file,
  visibly distinguished, with label and working title only, no link and
  no count; the four paths as a view after the courses and before the
  method views; the planned courses named in one sentence; the test that
  compares the page with the front matter and the file.
- The home page: `PLANNED` of `pbc.authoring.home` replaced by the
  courses and paths of the file with their published counts; the test of
  the home page updated to read the file instead of the roadmap table.
- `path.json` (F13) and the lesson header carry the slot and the path
  position; `docs/authoring.md` and the lesson template state the slot
  rule and the placement rule of ADR 013; the content-proposal form's
  course list gains the eight courses.
- The prerequisite rule of ADR 013 decision 8 in the lesson source check
  (`pbc.authoring.path.problems`): a prerequisite must exist, the graph
  must have no cycle, and a prerequisite in the same strand must come
  earlier in that strand; a prerequisite in another strand may come later
  in the linear order. The course view and the path view of the path page
  order lessons by the order in which the curriculum file lists their
  slots, lessons without a slot after them in linear order; previous and
  next, the graph layout, and every address stay as they are. The path
  page's explanation of previous and next (F37) says that a prerequisite
  may live in a later strand and that the dependency map gives the order
  of ideas. Tests on fixture lessons: a `thermodynamics` lesson that
  requires the gas lesson of `agents-abm` (the T0 to T2 progression)
  passes and the course view lists T0 first; a `mechanics` lesson that
  requires a `lean` lesson passes; a prerequisite later in the same strand
  fails; a cycle across strands fails; the twenty-two published lessons
  still pass unchanged.

**Out of scope.** Any new lesson or strand directory (the first lesson
feature of each course creates it); the redesign of the path page's
layout (F64) and the thumbnails (F63); changing any address, identifier,
or lesson body.

**Dependencies.** F03 (F62 replaces the "prerequisite later in the path"
check of F03 criterion 2 by the graph rule of ADR 013 decision 8), F37
(the metadata and the path page it extends), F26 and F27 (consumers that
must keep working), F25 (the home page's planned list).

**Acceptance criteria.**

1. The curriculum file holds exactly 81 Part A slots in the eight courses
   (17, 12, 9, 9, 10, 8, 10, 6), 33 Part B slots in the four paths (9, 13,
   5, 6), and the one Lean slot; 16 slots are labs and 3 are capstones;
   a test counts them, so that a change of the file is a reviewed change
   of the curriculum and this roadmap's "Slot mapping" is updated with it.
2. The seventeen published lessons that fill a slot of their course or of
   a path carry their slot; the gas lesson (T0, set by F70) and the four
   Lean lessons beyond the baseline carry none; a test shows the build
   fails on an unknown label, on a duplicated slot, and on a lesson whose
   course is not the home of the course slot it names; lesson bodies are
   byte-identical to before, shown by the diff of the pull request.
3. The path page shows every published lesson under its course and, for
   a method-path lesson, under its path at its position; every unfilled
   slot of a course that has a lesson, and of every path, appears as
   planned with no link; a course that has no lesson is named in the one
   sentence and shows no slot (so T0 is listed only from F70); a planned
   slot is never counted in a published count; shown by a test over the
   file and the front matter.
4. Every lesson URL that existed before the feature resolves to the same
   lesson, and previous and next follow the strand order of ADR 013
   (unchanged until a second course strand exists), shown by the test over
   the list of previous addresses.
   The prerequisite check accepts a prerequisite in a later strand and
   rejects a later prerequisite in the same strand and a cycle, shown by
   the fixture tests of ADR 013 decision 8 (the T0 to T2 progression and
   a cross-strand dependency), and the course view orders by the slot
   order of the curriculum file.
5. The home page's planned list is derived from the file, names no
   delivered feature, and its test reads the file.
6. From the home page, with JavaScript disabled, a reader reaches every
   lesson through the course list and through each path; the page passes
   the accessibility scan and reflows at 320 CSS px.
7. ADR 013 is accepted with the merge; ADR 008 names it in its status;
   F15 is recorded as dropped.

**Risk.** Medium. The migration touches the front matter of every lesson
and the header every page renders; the F03 and F37 tests catch drift. The
file is a new validated input that the human approves line by line.

**Detailed implementation plan expected.** Yes, short: the file schema,
the migration table, the page sections.

### F63 — Verified lesson previews

**Source.** Change request section 8.2 (items 3 and 5), 8.3, and section
10 ("Shared figure/preview infrastructure"); requirements "UX expectations"
(thumbnails) and non-goals (no decorative, stock, hand-copied, or external
images); decision 29.

**Goal.** A deterministic small preview for every published lesson,
derived from the lesson's own verified figure by the same executed cell
that produces it, with a repository-generated conceptual SVG as the
documented fallback, so that the learning path can show one verified
thumbnail per lesson without any committed, copied, or external image.

**User-visible outcome.** Nothing until F64 uses it, except that the
preview of every lesson is built, checked, and byte-stable, and the
learning path export names it.

**In scope.** The optional `preview` front-matter field naming a figure
cell label of the lesson. Introducing the field is justified (change
request section 8.3 and requirements decision 29 allow a new field only
when it is needed) because a lesson has several figures and the
representative one (a measured-versus-model panel, a phase curve) is
often not the first, which is frequently a conceptual setup diagram;
deriving the preview from the first figure cell was considered and
rejected for that reason. Declaring it stays optional per lesson, with
the conceptual fallback below for a lesson that names none, so that no
lesson is forced to declare one. The
figure helper writes, beside the full
figure, a small raster or SVG rendering at a fixed size with the same
status label in its alt text; a lesson without `preview` gets the
conceptual fallback drawn by code from its course and methods (no image
file); the built-site check that every lesson has exactly one preview,
that it comes from the named cell or the fallback, that two builds give
byte-identical previews, and that no image on the path page is loaded
from outside the build; `path.json` carries the preview path and its alt
text; the twenty-two published lessons each name a preview cell (a
trajectory, a phase curve, a measured-versus-model panel, a transcript
figure, a proof diagram) chosen in the Issue; `docs/authoring.md`.

**Out of scope.** The path page layout (F64); cropping by hand;
image files of any kind; previews of pages that are not lessons.

**Dependencies.** F62 (the field joins the validated schema), F28 (figure
status), F44 (the visual system's sizes).

**Acceptance criteria.** Every lesson has one preview that a test traces
to its named cell or to the fallback; two builds produce byte-identical
previews; the preview carries alt text with the status; the previews of all
lessons together stay within the initial payload budget of the path page
(measured by the F44 check); the authoring guide states the rule; a lesson
whose `preview` names no figure cell fails the build.

**Risk.** Medium. Matplotlib output at small sizes needs explicit,
deterministic configuration; the F02 determinism settings and the byte
test guard it.

**Detailed implementation plan expected.** Yes, short.

### F64 — Learning Path redesign: course-first, compact, accessible

**Source.** Change request section 8 (8.1 to 8.5) and section 12,
decision 8; requirements "UX expectations" (Learning Path page) and
decision 29.

**Decision on scope (section 8).** One feature, after F62 (the data) and
F63 (the previews), that rebuilds the page from the delivered F26, F27,
F37, F41, F44, F13, and F14 foundations without reopening them. It is
delivered before the bulk of the new lessons, so that the page does not
deteriorate as the catalogue grows.

**Problem.** The page exposes every card in full in every view, repeats
long cards across the course and method views, shows the whole graph
prominently, and will become unreadable at a hundred lessons. It must
look like a calm scientific publication: course-first, compact, with
detail on demand.

**Goal.** The page of the requirements' "UX expectations": course panels
with real counts and verified miniatures; a course's lessons behind native
disclosure, closed by default; compact cards with a thumbnail and chips;
details on expansion; the method paths and the methods as a secondary
view; the graph under an optional disclosure with course-scoped subsets;
optional filters that coordinate with the search; every lesson reachable
without JavaScript; every existing address valid.

**User-visible outcome.** A first-time visitor sees "Choose a physics
course" with the three activities explained, compact course panels, one
per course that has a lesson, with the courses that have none named in
one sentence (the change request asks for eight panels; the
requirements' use case 1 and ADR 013 decision 5 show a course as each
gains a lesson, so a course without one gets no panel for that reason; a
panel with a zero count and a conceptual miniature was considered and
rejected, because the change request forbids advertising planned content
as published and a zero-count panel is a placeholder in another form),
opens a course, scans its lessons as small rows with one preview each,
opens a
lesson's details when wanted, switches to the physics-and-AI paths, the
measured-data labs, agent-based modelling, or Lean as views over the same
lessons, and finds the dependency map at the bottom.

**In scope.**

- The page generator (`pbc.authoring.path`, the templates, `site/path`)
  rendering: the intro; one panel per course with description, published
  count, the F63 preview of its first or representative lesson (chosen by
  a rule in the file, not by hand), and the entry link; `<details>` and
  `<summary>` per course, closed by default, with the current course open
  when the page is reached from a lesson, if that can be done without a
  script; lesson rows in the slot order of the curriculum file (ADR 013
  decision 8) with title, one-sentence physical question,
  difficulty badge, thumbnail, chips for simulation, experimental data,
  and AI extensions, and planned slots as distinguished rows; a nested
  disclosure per lesson with outcomes, prerequisites, what the reader
  builds, related extensions, the capstone classification for T11, EM9,
  and FL10 when they exist, and the reproduce link; the four method paths
  and the method views as secondary sections that list the same lessons
  compactly and link to the canonical pages; the F13 progress marks and
  the F14 recommendations kept.
- The graph (F26) unchanged in content, under a "View dependency map"
  disclosure, with a course-scoped subset per course generated from the
  same metadata and the text alternative kept.
- Optional filters (course, method, difficulty, publication state) as a
  form that works by links without JavaScript and is enhanced with a
  script that stores nothing; coordinated with the search of F41 (the
  index keeps the page's prose).
- Responsive layout at phone, tablet, and desktop widths; focus states;
  reduced motion; the F44 design system; the payload budgets of the
  architecture measured for the new page; no framework; no external
  resource.
- The tests: the page equals the front matter and the curriculum file;
  counts equal the published lessons; every lesson reachable with scripts
  disabled through its course and through each path and method; every
  previous address and graph node address resolves; the accessibility
  scan, the keyboard pass over the disclosures and the graph, and the
  no-two-way-scroll check at 320 CSS px; the payload check; byte-stable
  rebuilds; the search index unchanged in meaning.
- A visual review before merge recorded on the Issue: an introductory
  course, the mechanics course with its planned slots, a measured-data
  lesson, an agent lesson, long titles, and the phone layout.

**Out of scope.** New lessons; changes to lesson pages beyond the header's
link to the path; a second catalogue; images that are not F63 previews;
animation; a frontend framework; changing any address.

**Dependencies.** F62, F63, F26, F27, F37, F41, F44, F13, F14.

**Acceptance criteria.**

1. With JavaScript disabled, a first-time visitor can choose a course,
   expand it, find every published lesson, read its prerequisites, and
   follow its canonical link; shown by a built-site test per course and
   per path.
2. The method-path view and the method views show no duplicate lesson
   content and miss no lesson; a lesson appears once as a canonical page
   and elsewhere as a link; shown by a test.
3. Every course and path count equals the published catalogue; planned
   slots are visibly distinguished and never linked or counted.
4. Every previous address, bookmark, and graph node address resolves;
   shown by the test over the list of previous addresses.
5. Every thumbnail is an F63 preview with alt text; no image loads from
   outside the build.
6. The accessibility scan passes; the disclosures and the graph work by
   keyboard and read correctly with a screen reader in the manual pass
   recorded on the Issue; the page reflows at 320 CSS px without two-way
   scrolling; reduced motion is respected.
7. The page's initial payload is within the architecture's budget, and
   its byte-stable rebuild, link, prerequisite, and search-index tests
   pass.
8. The visual review of criterion 8.4 of the change request is recorded
   on the Issue before merge.

**Risk.** Medium. The page is the site's main navigation; the tests of
F03, F26, F27, F37, F41, and F13 catch regressions, and the no-script
tests are the guard for the disclosures.

**Detailed implementation plan expected.** Yes.

### Wave C1 — Discovery foundation and the first new physics

Order within the wave, by dependency: F65 first among the discovery
features and the only feature of the wave that may start before the
gates, because it publishes no lesson; every lesson feature of the wave
after F61 and F62, and after F113 once the lesson count would pass 32
(the full-run gate: the wave adds twenty-six lessons to twenty-two, so
F113 lands within this wave, after about the first ten); then F66 and
F67; the first lesson features of the
courses (F68, F70, F71, F72, F73) are independent of each other and of
F65 and may run in parallel worktrees; F69 after F68; F74 after F71 and
F51; F52, F53, F54, F45, and F55 of the previous phase as their
dependencies, including the gates, are met (see "State at the change
cycle `final-curriculum`"). This wave is the first block of new lessons;
the waves after it are the bulk that F64 gates.

### F65 — Physics environments and the discovery evaluation protocol

**Source.** Change request sections 5, 7.3, and 10 ("Law-discovery
sandbox & evaluation protocol"); requirements decision 25; ADR 004;
architecture, "Law-discovery environment and agent benchmark".

**Decision on slicing (section 10).** One shared package, `pbc.discovery`,
carries the environments, the baselines, and the protocol; the lessons of
the law-discovery and benchmarking paths are separate features that use
it. No lesson builds its own framework.

**Goal.** A reusable environment abstraction over the models of `src/pbc`
with the hidden truth kept apart from the agent; non-agent baselines; the
evaluation protocol (splits, held-out worlds, budgets, seeds, scoring,
versioned prompts and models, frozen traces, cost records); and the
harness allowlist that exposes an environment's controls and observations
to an agent and nothing else.

**User-visible outcome.** Nothing on the site; in the repository, the
package with its tests and one worked environment (the force laws of the
mechanics course with modifiable parameters and a hidden modified law),
the protocol written in its own document, docs/discovery-protocol.md
(new in this feature, as F46 added `docs/validation-contract.md`; the
feature registers it in `docs/project-map.md`), and the authoring section
"Discovery lessons". The protocol does not go into `docs/evaluation.md`,
which is the review-criteria document of the development workflow, not a
product document.

**In scope.** `Environment` (controls with bounds and units, observations
with noise, a budget, reset, a hidden truth that no public method
returns); environments for the projectile, the oscillator, the central
force, and an N-body world once F69 exists; the harness tools over an
environment (ADR 004) with tests that the allowlist cannot reach the
truth; baselines (random and grid probing, least squares in `pbc.data`,
sparse identification or symbolic regression in pure Python or as a
locked library with its licence recorded); the protocol: held-out
settings, full, partial, and no prior-knowledge conditions, budgets, seeds,
scoring, the replay fixture with model, prompt, and version, cost and call
counts recorded from the run that produced the fixture; the rule that a
full benchmark run lives outside `verify.conf` with a small deterministic
replay on the page.

**Out of scope.** Any lesson page; external benchmark assets (inspiration
only, no embedding before licences and assumptions are checked); code
execution by the agent; a neural or general machine-learning framework.

**Dependencies.** F09, F16, F20 (the harness, the counterexample loop,
and the design agent it generalises), F23 (the fitting helpers), F46 (the
validation contract).

**Acceptance criteria.** A test shows the agent's tools cannot read the
hidden truth of any environment; each baseline recovers a known law or
parameter on a synthetic environment within tolerance and reports failure
on one it cannot; the protocol's scoring is deterministic from a frozen
trace and recomputed by a test; the replay passes without credentials; a
locked discovery library, if any, has its licence and weight recorded;
docs/discovery-protocol.md (which does not exist before this feature)
states the protocol, `docs/project-map.md` lists the document, and the
authoring guide states its use; `docs/evaluation.md` is unchanged.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F66 — Law discovery lessons: black-box force laws (D1, D2, D3)

**Source.** Change request section 5 (B2: D1 to D3) and section 10
("First discovery lessons"). Slots D1, D2, D3 of the scientific law
discovery path; lessons in `agents-llm` with `course: mechanics`.

**Goal.** Three lessons on the F65 environments: discovering an unknown
force law with controlled probes (D1); the same discovery with full,
partial, and no prior knowledge compared under one protocol (D2); and
unlearning a familiar law to identify a deliberately modified one (D3);
each with a non-agent baseline, held-out tests, a frozen replay, and a
typed verdict only where the build recomputes it.

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F65.

**Acceptance criteria.** The lesson rule; the agent rule; the three
conditions of D2 scored on the same held-out settings; the modified law of
D3 recovered by the baseline and reported for the agent as it is; the
replay recomputed by the build.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F67 — Symbolic regression and equation discovery (D7, D8)

**Source.** Change request section 5 (B2: D7, D8). Slots D7 and D8;
lessons in `agents-llm` with `course: mechanics`, methods `simulation`
(and `llm-agents` only where an agent is used).

**Goal.** Interpretable functional forms recovered from simulated data
with non-LLM tools (D7), and dynamical equations inferred from
trajectories with numerical derivatives and noise (D8), on the course's
models, with the identifiability and noise limits stated; the baselines
every later discovery lesson compares with.

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F65, F23.

**Acceptance criteria.** The lesson rule; a known law and a known equation
recovered within tolerance from clean data and the failure under noise
shown and explained; any locked library's licence recorded; no claim that
a recovered form is the physical law beyond what held-out data supports.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F68 — Advanced mechanics: chaos, Lagrangian and Hamiltonian mechanics, resonance (M9 to M12)

**Source.** Change request section 4 (A1: M9, M10, M11, M12). Slots M9 to
M12 in the `mechanics` strand.

**Goal.** Four lessons: the double pendulum and sensitivity to initial
conditions with a Lyapunov estimate (M9); constrained and coupled systems
from a Lagrangian, simulated and checked (M10); phase space, symplectic
structure, and geometric integration (M11); damping, driving, resonance
curves, and their validation (M12).

**Note on F45.** F45's default coding-agent exercise is a damped driven
oscillator with resonance. Whichever lands first owns the verified
reference solution in `src/pbc`; the other reuses it; M12 is the course
lesson that teaches the physics and F45 the exercise that builds it.

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F05, F06; coordination with F45 as noted.

**Acceptance criteria.** The lesson rule; M9's Lyapunov estimate checked
against the sign expected in regular and chaotic regimes; M10's equations
checked against the Newtonian form for a case with a closed form; M11's
symplectic integrator checked for the conserved modified energy of M5 and
L3, with L3 among M11's prerequisites although it lives in the later
`lean` strand (ADR 013 decision 8); M12's resonance curve checked against
the analytic amplitude.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F69 — Mechanics: many-body gravitation, nonlinear dynamics, rotational motion (M13, M14, M17)

**Source.** Change request section 4 (A1: M13, M14, M17; M17 new in
revision 2). Slots M13, M14, M17 in the `mechanics` strand.

**Goal.** N-body orbits and long-term stability with an optional REBOUND
comparison as a declared reference artifact (M13); attractors,
bifurcations, and where linearisation fails (M14); rigid-body rotation,
inertia tensors at an introductory level, torque, angular momentum, and
gyroscopic precession as the worked example, with unit, energy, and
angular-momentum checks (M17, linked to M10, M11, and later D13).

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F68, F06.

**Acceptance criteria.** The lesson rule; M13's energy and angular-momentum
drift reported per integrator and compared with the reference artifact
where one is declared; M14's bifurcation diagram checked against a known
threshold; M17's precession rate checked against the analytic limit.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F70 — Thermodynamics and statistical physics: random walks, kinetic theory, entropy (T1, T2, T3)

**Source.** Change request section 4 (A2: T1, T2, T3) and section 3
(legacy T0). Slots T1 to T3; the first lesson feature of the
`thermodynamics` course: it creates the strand directory and
`pbc.thermodynamics`, and re-homes the gas lesson of F11 as `course:
thermodynamics`, `slot: T0` under its `agents-abm` address, setting the
two fields in one change (the lesson carries no slot before F70; ADR 013
decision 6).

**Goal.** From microscopic randomness to diffusion laws (T1); particle
collisions and the Maxwell-Boltzmann distribution, reusing the F11 gas
model (T2); entropy from ensembles with its scope and limits (T3).

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F11, F06.

**Acceptance criteria.** The lesson rule; the course appears on the path
with its four lessons (T0 to T3, T0 first by the slot order of the
curriculum file) and its eight planned slots; T0's address and identifier
unchanged and its header naming the new course; T2 lists T0 as a
prerequisite although T0 comes later in the linear order (ADR 013
decision 8); T1's
diffusion coefficient checked against the random-walk prediction; T2's
distribution checked against the analytic form at the simulated
temperature; T3's entropy checked in a case with a closed form.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F71 — Waves and optics: the wave equation, interference, sound (W1, W2, W9)

**Source.** Change request section 4 (A3: W1, W2, W9; W9 new in revision
2, numerical, no recording). Slots W1, W2, W9; the first lesson feature of
the `waves` course (strand directory, `pbc.waves`).

**Goal.** Finite-difference wave propagation with boundaries and
convergence (W1); superposition, standing waves, modes, and dispersion
(W2); numerical sound propagation, resonance, and the Doppler shift with
analytic limiting cases, with no audio or sensor requirement (W9).

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F05.

**Acceptance criteria.** The lesson rule; W1's convergence order measured
and the CFL limit shown; W2's mode frequencies checked against the
analytic values; W9's Doppler shift checked against the formula for a
moving source and a moving observer.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F72 — Electromagnetism: fields, charged particles, induction (EM1, EM2, EM3)

**Source.** Change request section 4 (A4: EM1, EM2, EM3). Slots EM1 to
EM3; the first lesson feature of the `electromagnetism` course (strand
directory, `pbc.electromagnetism`); gives F54 its home.

**Goal.** Vector fields, superposition, and potential (EM1);
charged-particle motion in given fields (EM2); time-dependent flux and the
induced electromotive force (EM3).

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F06.

**Acceptance criteria.** The lesson rule; EM1's field checked against the
closed form for a dipole; EM2's cyclotron frequency checked; EM3's induced
voltage checked against the flux derivative.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F73 — Fluid dynamics: advection, Burgers, finite volumes, shallow water (FL1, FL4, FL9, FL5)

**Source.** Change request section 4 (A5: FL1, FL4, FL9, FL5; FL9 new in
revision 2; FL5 enhanced in revision 3), section 7.1 (FL9, FL5), and
section 10 ("Conservative numerical methods"). Slots FL1, FL4, FL9, FL5 in
the teaching order FL1, FL4, FL9, FL5; the first lesson feature of the
`fluids` course (strand directory, `pbc.fluids` with the conservative
fluxes that FL5 and FL10 reuse); gives F53 its home.

**Goal.** Schemes, boundary conditions, stability, and artificial
diffusion (FL1); nonlinear steepening, shocks, and numerical dissipation
(FL4); transparent conservative fluxes with CFL limits, shock capturing,
mass and momentum budgets, convergence, and a comparison with a
non-conservative discretisation (FL9); the depth-averaged balance, a small
conservative scheme with still-water and dam-break checks, depth
positivity, boundaries, and conservation (FL5).

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F05, F06.

**Acceptance criteria.** The lesson rule; FL1's numerical diffusion
measured against the modified equation; FL4's shock speed checked against
the Rankine-Hugoniot condition; FL9's budgets conserved to round-off and
the non-conservative scheme's error shown; FL5's still water preserved and
the dam-break front checked against the exact solution; one flux
implementation shared by FL9 and FL5.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F74 — Wave flume lab (W8)

**Source.** Change request section 4 (A3: W8); the Aalborg submerged-bar
dataset with a go decision from F50 (`docs/datasets/aalborg-submerged-bar.md`).
Slot W8, a measured-data lab of the `waves` course.

**Goal.** Measured tank waves over a submerged bar compared with the
simulated propagation and dispersion of W1 and W2, with the measured and
the modelled-reference artifacts of the card kept distinct, the waveform
comparator of F43, residuals, and a qualified claim.

**Dependencies.** F61, F62 (the gates of this phase), F113 by the lesson-shard rule of the full-run gate, F71, F51, F43; the go decision exists, so no new spike
unless the committed sample needs widening within the caps.

**Acceptance criteria.** The lab rule; the measured series never labelled
`simulated` and the CFD series of the card labelled by its artifact; the
model's dispersion compared with the measured gauges with uncertainty.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### Wave C2 — Core subject expansion and numerical engineering

Order within the wave: every lesson feature of this wave after F64 (the
gates under "Phase 4"); F75 and F76 after F70; F77 after F71; F78 after
F72 and F71; F79 after F73; F80 after F78; F81 after F66 and F67; F82
after F67 and F69; the labs F83 to F86 after their course lessons and
F51, each through its gate.

### F75 — Thermodynamics: Ising model, molecular dynamics, heat engines (T4, T5, T9)

**Source.** Change request section 4 (A2: T4, T5, T9; T9 new in revision
2). Slots T4, T5, T9 in the `thermodynamics` strand.

**Goal.** Magnetisation, critical behaviour, and finite-size effects (T4);
interparticle potentials, thermodynamic observables, and drift checks
(T5); idealised Carnot and comparison cycles with heat, work, and
efficiency from p-V paths and the first and second laws checked (T9).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F70.

**Acceptance criteria.** The lesson rule; T4's critical temperature
estimated and compared with the exact two-dimensional value with
finite-size caveats; T5's energy conservation and equipartition checked;
T9's efficiency checked against the Carnot bound.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F76 — Heat conduction and the finite-element bridge (T6, T10)

**Source.** Change request section 4 (A2: T6 enhanced in revision 3; T10
new in revision 3), section 7.1 (T6/T10/T11), and section 10 ("FEM and
engineering mesh foundation"); requirements decision 26 and non-goals (no
heavyweight solver as a mandatory dependency). Slots T6 and T10 in the
`thermodynamics` strand; adds `pbc.fem`, the small triangular
finite-element solver that T11 and MAT3 reuse.

**Goal.** From lumped cooling to the one- and two-dimensional heat
equation with finite differences, conductive and convective boundaries,
stability, grid and time-step convergence, and units (T6); then weak-form
intuition, piecewise-linear elements on a small triangular mesh generated
and inspected in the lesson, assembly and solution of a sparse system with
SciPy, explicit boundary conditions, comparison with the finite-difference
solution and a manufactured solution, mesh-quality and refinement checks,
and energy and heat-flux balances (T10). Gmsh and FEniCSx are optional
reference tools whose output, if used, is a declared `modelled-reference`
input; they are not dependencies.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F70.

**Acceptance criteria.** The lesson rule; T6's stability limit and
convergence order measured; T10's error against the manufactured solution
decreasing at the expected rate under refinement, its flux balance closed
to a stated tolerance, its page within the 30-second budget on the pinned
stack, and any optional-tool artifact carrying a card; a test that
`pbc.fem` has no import outside the locked environment.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F77 — Optics: refraction, polarisation, diffraction, inverse optics (W3, W4, W5, W6)

**Source.** Change request section 4 (A3: W3 to W6). Slots W3 to W6 in
the `waves` strand; W5 prepares F52's home.

**Goal.** Propagation across an interface with Snell's law verified (W3);
polarisation states, Malus's law, and practical limits (W4); Fraunhofer
diffraction and instrument limits (W5); inferring optical parameters from
intensity data, on simulated data until F52 provides measured images (W6).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F71.

**Acceptance criteria.** The lesson rule; W3's refracted angle, W4's
transmitted intensity, and W5's fringe spacing checked against the closed
forms; W6's recovered parameters within tolerance on synthetic data with
the identifiability limit shown.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F78 — Electromagnetism: Maxwell's equations and FDTD, RLC circuits, waveguides and antenna basics (EM4, EM5, EM6)

**Source.** Change request section 4 (A4: EM4, EM5, EM6 enhanced in
revision 3). Slots EM4 to EM6 in the `electromagnetism` strand.

**Goal.** A transparent finite-difference time-domain solver for
electromagnetic waves (EM4); transient and frequency-domain circuit
behaviour (EM5); modes, boundary conditions, and transmission in
waveguides, with the bridge from superposition to element radiation
patterns that EM9 needs and the limits of the idealised models (EM6).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F72, F71 (W1's finite differences and W2's
superposition).

**Acceptance criteria.** The lesson rule; EM4's wave speed and reflection
checked and its stability limit shown; EM5's resonance checked against the
analytic response; EM6's cut-off frequencies checked and the element
pattern compared with the analytic dipole pattern.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F79 — Fluid dynamics: Navier-Stokes, vortex shedding, particle-based fluids (FL2, FL3, FL6)

**Source.** Change request section 4 (A5: FL2, FL3, FL6). Slots FL2, FL3,
FL6 in the `fluids` strand; FL3 prepares F53's physics.

**Goal.** A contained two-dimensional incompressible solver (FL2);
vorticity, shedding, and the Reynolds-regime caveats (FL3); grid versus
particle modelling and its limits (FL6).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F73.

**Acceptance criteria.** The lesson rule; FL2 checked against a
lid-driven-cavity reference at low Reynolds number declared as a
`modelled-reference` input or against a manufactured solution; FL3's
Strouhal number compared with the published range with the regime stated;
FL6's conservation checked.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F80 — Applied capstone: adaptive phased-array beam steering (EM9)

**Source.** Change request section 4 (A4: EM9), section 4.1, section 7.1
(EM9), and section 10 ("A4 selected phased-array capstone"); requirements
decision 26 and non-goals. Slot EM9, the applied capstone of the
`electromagnetism` course.

**Goal.** A finite-array complex field and array-factor model checked
against analytical steering, null, and symmetry limits; electronic
steering toward a moving receiver and a null toward an interferer where
feasible; the effect of element spacing, amplitude and phase control,
quantisation, frequency, noise, and element patterns on the main lobe,
sidelobes, and grating lobes; the trade-offs and the cases where the ideal
model fails; the page states that an array-factor model is not a full-wave
antenna or metasurface design and implies no fabricated device.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F78, F71 (W2); F54 optional for measured RF context.

**Acceptance criteria.** The capstone rule; the steering angle, the null
depth, and the grating-lobe onset checked against the analytic
expressions; the quantisation and noise degradation measured; an
optional full-wave element reference, if used, declared as a
`modelled-reference` input; deterministic preview figures from the verified
sequence, and any interactive enhancement degrading to them.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F81 — Interactive discovery benchmarks and non-agent baselines (EV2, EV3)

**Source.** Change request section 5 (B3: EV2 enhanced in revision 2,
EV3). Slots EV2 and EV3 of the agent benchmarking path; lessons in
`agents-llm` with `course: mechanics`.

**Goal.** Whether agents discover laws through simulated experiments at
full, partial, and no prior knowledge under one protocol with budgets and
held-out evaluation (EV2); whether agentic tool use outperforms a plain
model, random selection, or symbolic fitting (EV3); with the protocol of
F65 and the lessons of F66 and F67 as the subjects.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F65, F66, F67.

**Acceptance criteria.** The agent rule; the scores recomputed from frozen
traces; the baselines on the same environments and budgets; the page
states when a comparison is not meaningful because budgets or
environments differ; no live call in CI.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F82 — Discovering conservation laws and invariants (D13)

**Source.** Change request section 5 (B2: D13, new in revision 2) and
section 7.1 (D13). Slot D13 of the law discovery path; lesson in
`agents-llm` with `course: mechanics`.

**Goal.** Candidate conserved functions inferred from trajectories of
unknown systems, validated across held-out initial conditions and
integration settings, true invariants separated from integration drift and
coincidental correlations, with a non-LLM numerical baseline and the
symmetry-conservation connection explained without assuming equation
recovery; on the mechanics models of M11 and M17 and, where F73 exists,
the fluxes of FL9.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F65, F67, F69.

**Acceptance criteria.** The lesson and agent rules; the baseline finds
the known invariants of a test system and rejects a drift artefact; the
agent's candidates are tested on untouched trajectories by the build; the
withheld truth is unreachable.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F83 — Pendulum and accelerometer data lab (M15)

**Source.** Change request section 4 (A1: M15). Slot M15, a measured-data
lab of the `mechanics` course; no candidate card exists.

**Goal.** Fit the dynamics of M4, M6, and M12 to genuine already-collected
motion data (a published pendulum or accelerometer record with rights for
redistribution), with calibration, noise, residuals, and uncertainty.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F51, F68; a new candidate card and spike with a go
decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F84 — Heat transfer measurements lab (T7)

**Source.** Change request section 4 (A2: T7). Slot T7, a measured-data
lab of the `thermodynamics` course; no candidate card exists.

**Goal.** Thermal conductivity or relaxation inferred from real temperature
records against the models of T6, with uncertainty; an optional cross-link
for T11's parameters.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F76, F51; a new candidate card and spike with a go
decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F85 — Brownian motion tracking lab (T8)

**Source.** Change request section 4 (A2: T8). Slot T8, a measured-data
lab of the `thermodynamics` course; no candidate card exists.

**Goal.** Diffusion coefficients inferred from genuine tracked-particle
trajectories against T1, with the tracking disclosed as processing.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F70, F51; a new candidate card and spike with a go
decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F86 — RLC circuit measurements lab (EM8)

**Source.** Change request section 4 (A4: EM8). Slot EM8, a measured-data
lab of the `electromagnetism` course; no candidate card exists.

**Goal.** Measured impedance or time responses of a real circuit fitted
with the EM5 model, with uncertainty.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F78, F51; a new candidate card and spike with a go
decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### Wave C3 — Applied capstones, advanced physics, and the agent paths

Order within the wave: every lesson feature of this wave after F64 (the
gates under "Phase 4"); F87 after F76; F88 after F73 and F51; F89 to F95
by their dependencies, in parallel worktrees where independent; F96 after
F65; F100 after F96 and F65; F97 after F96; F98 after F66 and F81; F99 after F66, F69,
and F91; F101 after F81 and F98; the labs F102 to F108 after their course lessons, each through its
gate.

### F87 — Applied capstone: thermal engineering of a hypothetical AI accelerator (T11)

**Source.** Change request section 4 (A2: T11), section 4.1, section 7.1,
and section 10 ("A2 applied thermal capstone"); requirements decision 26
and non-goals. Slot T11, the applied capstone of the `thermodynamics`
course.

**Goal.** A hypothetical multi-hotspot package or cold-plate proxy: heat
loads, geometry and material conductivities, contact and convective
boundary assumptions, and thermal constraints stated; transient and
steady temperature fields with `pbc.fem`; cooling, material, and layout
scenarios compared; the maximum temperature optimised under stated mass,
size, and heat-removal constraints; mesh, time-step, and sensitivity
studies against the T6 finite-difference baseline; a trade-off table and
a justified recommendation; labelled a digital-twin-style teaching
prototype, not a calibrated twin or a model of a proprietary device, with
no vendor data and no full three-dimensional CFD.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F76; F84 optional for a measured cross-link.

**Acceptance criteria.** The capstone rule; the energy and flux balances
closed to a stated tolerance; the finite-element and finite-difference
solutions agreeing under refinement; the sensitivity plot and the
trade-off table generated by the build; the credibility label as a typed
claim on the page; the page within the budget with a small mesh.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F88 — Applied capstone: reconstructing the 2025 Kamchatka tsunami (FL10)

**Source.** Change request section 4 (A5: FL10), section 4.1, section 7.1
(FL10), section 7.2 (the gated comparison), section 10 ("A5 selected
tsunami capstone"), section 12 (decision 10), and section 14 (candidate
sources); requirements decision 26, "Data and persistence" (measured-data
target), and non-goals. Slot FL10, the applied capstone of the `fluids`
course.

**Decision on slicing (section 12, decision 10).** Two deliverables in
one feature, separable into two Issues: the simulation and benchmark core,
which depends on no dataset approval and is published as clearly
simulated; and the historical comparison, which starts with the F50 spike
of the DART records and the bathymetry (rights, provenance, processing,
station and time-window suitability, a tractable sample) and is published
only on a go decision. The second never blocks the first.

**Goal.** A teaching-scale, non-operational two-dimensional propagation
model from the shallow-water equations and the conservative fluxes of
FL9 and FL5: flat-bottom analytical and benchmark cases, then regional,
source-documented bathymetry on a cropped grid and a transparent assumed
initial sea-surface displacement; open boundaries, CFL and grid
convergence, mass budgets, wet-dry limits, dispersion, Coriolis, and
spherical-geometry approximations, and the source uncertainty explained;
wave-height and travel-time figures; after the gate, qualified arrival-time
and waveform comparisons with authentic July 2025 DART records with
residuals and uncertainties; the page states it is not for warning,
inundation, or hazard forecasting.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F73, F51; F50's process for the DART and bathymetry
candidates (new cards).

**Acceptance criteria.** The capstone rule; the benchmark suite (still
water, linear-wave propagation, conservation, positivity, boundary
sensitivity) deterministic and within the page budget on the cropped grid;
the bathymetry's source and licence on its card; until the gate grants it,
no measured comparison and no claim of agreement with observations; after
it, the lab rule applies to the comparison, which is a validation
component and not a seventeenth lab; heavier reruns outside `verify.conf`.

**Risk.** High. Scope, data rights, and the temptation to present a
striking animation as validation; the two-deliverable slicing, the gate,
and the review guard it.

**Detailed implementation plan expected.** Yes, likely two Issues.

### F89 — Quantum physics: the Schrödinger equation, tunnelling, the harmonic oscillator (Q1, Q2, Q3)

**Source.** Change request section 4 (A6: Q1, Q2, Q3). Slots Q1 to Q3;
the first lesson feature of the `quantum` course (strand directory,
`pbc.quantum`); QuTiP is an optional comparator only.

**Goal.** Numerical evolution of a one-dimensional wavepacket (Q1);
barrier transmission and reflection against energy (Q2); eigenstates,
energies, and numerical convergence (Q3).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F05, F71 (W1's finite differences).

**Acceptance criteria.** The lesson rule; norm conservation and the
free-particle dispersion checked (Q1); the transmission coefficient
checked against the closed form (Q2); the eigenvalues converging to the
analytic spectrum (Q3).

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F90 — Quantum physics: spin, entanglement and Bell inequalities, open systems (Q4, Q5, Q6)

**Source.** Change request section 4 (A6: Q4, Q5 enhanced in revision 2,
Q6). Slots Q4 to Q6 in the `quantum` strand; Q5's Bell and CHSH content
is the first half of the linked Q5/Q8 enhancement.

**Goal.** Spin states, probabilities, and the modelled Stern-Gerlach
apparatus (Q4); correlations, measurement, the Bell and CHSH inequalities,
and the distinction between the quantum prediction and the
local-hidden-variable bound (Q5); density matrices, decoherence, and
master equations (Q6).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F89.

**Acceptance criteria.** The lesson rule; Q5's CHSH value computed from
the simulated correlations and compared with both bounds; Q6's trace and
positivity preserved by the integrator.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F91 — Astrophysics: the three-body problem, modified gravity, lensing (AST1, AST2, AST3)

**Source.** Change request section 4 (A7: AST1, AST2, AST3). Slots AST1
to AST3; the first lesson feature of the `astrophysics` course (strand
directory, `pbc.astrophysics`, reusing the N-body code of F69).

**Goal.** Nonlinear gravitational dynamics, stability, and initial
conditions (AST1); deliberately modified central-force laws with orbit
diagnostics (AST2); simplified deflection and lensing models with the
limits of mass inference (AST3).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F69.

**Acceptance criteria.** The lesson rule; AST1's conserved quantities
tracked and a known periodic solution reproduced; AST2's precession
checked against the perturbative prediction; AST3's deflection angle
checked against the weak-field formula.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F92 — Relativity and cosmology: special relativity, relativistic orbits, cosmic expansion (AST10, AST4, AST5)

**Source.** Change request section 4 (A7: AST10 new in revision 2, AST4,
AST5). Slots AST10, AST4, AST5 in the `astrophysics` strand, in that
teaching order.

**Goal.** Lorentz transformations, the invariant interval, time dilation,
length contraction, relativistic energy and momentum with collision checks
and the low-velocity limit (AST10); post-Newtonian orbital precession with
its approximation stated (AST4); toy cosmological models and observable
relations (AST5).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F91.

**Acceptance criteria.** The lesson rule; AST10's invariants preserved
and the Newtonian limit recovered; AST4's precession checked against the
first-order formula; AST5's distance-redshift relation checked against
the analytic case.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F93 — Gravitational-wave chirp and exoplanet transit simulations (AST6, AST7)

**Source.** Change request section 4 (A7: AST6, AST7). Slots AST6 and
AST7 in the `astrophysics` strand; AST6 cross-links M16 (F60) and L5
(F56), which are not republished.

**Goal.** An approximate binary-inspiral waveform from a transparent
model, linked to the measured strain of M16 without repeating it (AST6);
transit flux curves, geometry, and duration effects (AST7), the simulated
counterpart of AST8.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F91, F60.

**Acceptance criteria.** The lesson rule; AST6's chirp law checked
against the closed form of `pbc.mechanics.chirp` and the page linking
M16 instead of showing the measured strain again; AST7's transit depth
and duration checked against the analytic geometry.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F94 — Materials physics: crystal lattices and phonons, electronic band structure (MAT1, MAT2)

**Source.** Change request section 4 (A8: MAT1, MAT2). Slots MAT1 and
MAT2; the first lesson feature of the `materials` course (strand
directory, `pbc.materials`).

**Goal.** Lattice dynamics and dispersion (MAT1); a transparent
tight-binding model (MAT2).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F71 (W2's modes), F89 (Q3's eigenproblems).

**Acceptance criteria.** The lesson rule; MAT1's dispersion checked
against the one-dimensional chain's closed form; MAT2's band structure
checked against the analytic tight-binding bands.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F95 — Materials physics: elasticity and deformation, defects (MAT3, MAT4)

**Source.** Change request section 4 (A8: MAT3, MAT4). Slots MAT3 and
MAT4 in the `materials` strand; MAT3 may reuse `pbc.fem`.

**Goal.** Stress, strain, boundaries, and a simple mechanical model (MAT3);
defect effects, diffusion, and the limits of the model (MAT4).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F94, F76 (optional reuse of the finite-element solver).

**Acceptance criteria.** The lesson rule; MAT3's solution checked against
the closed form of a loaded bar; MAT4's diffusion checked against T1.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F96 — Multimodal physics reasoning and interpretable explanations (AI6, AI7)

**Source.** Change request section 5 (B1: AI6 enhanced in revision 2,
AI7) and section 7.3. Slots AI6 and AI7 of the physics reasoning path;
lessons in `agents-llm` with `course: mechanics`.

**Goal.** Interpreting diagrams, plots, field images, and measured
pictures from the site's own verified figures; testing object properties,
spatial relations, and image-based counterfactual predictions against
known constraints, as still images (AI6); distinguishing prediction from
explanation, with units, physical consistency, and uncertainty as the
tests of an explanation (AI7).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F09, F46; F65 for the evaluation protocol.

**Acceptance criteria.** The lesson and agent rules; every image is a
verified figure of the site or a declared sample with rights; the model's
answers are scored against constraints the build recomputes; the page
distinguishes the model's explanation from the verified result.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F97 — Physical reasoning from video (AI8)

**Source.** Change request section 5 (B1: AI8, new in revision 2) and
section 7.3 ("Video reasoning"); requirements decision 28 and non-goals.
Slot AI8 of the physics reasoning path; lesson in `agents-llm` with
`course: mechanics`.

**Goal.** For short motion clips the repository generates from verified
simulations (a bounce, a pendulum, a collision), or approved existing clips
with recorded rights, compare the direct multimodal-model observation,
conventional tracking with derived velocity and acceleration, and
agent-assisted simulation and prediction against the independent ground
truth; report trajectory and prediction errors, false causal claims,
confidence, and the limits of frame and sample rates. No webcam, upload,
hosted processing, or build-time model call.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F96, F06; a rights record for any clip that is not
generated.

**Acceptance criteria.** The lesson and agent rules; generated clips
labelled as generated and reproduced by the build; the tracking's offline
output deterministic and compared with the ground truth by a test; clips
within the on-demand payload budget and loaded only after a user action;
no clip of a person.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F98 — Discovery under noise, hidden variables, and generalisation (D10, D11, D12)

**Source.** Change request section 5 (B2: D10, D11, D12). Slots D10 to
D12 of the law discovery path; lessons in `agents-llm` with `course:
mechanics`.

**Goal.** Noise, calibration, outliers, and failure analysis in discovery
(D10); hypotheses with latent effects, observational ambiguity, and
disambiguating experiments (D11); laws challenged on held-out settings,
force models, and conditions (D12).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F66, F81.

**Acceptance criteria.** The lesson and agent rules; the held-out worlds
of D12 never probed by the agent, shown by the trace; the baselines'
degradation under noise measured (D10).

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F99 — Discovering gravity and unknown physical worlds (D4, D5)

**Source.** Change request section 5 (B2: D4, D5). Slots D4 and D5 of the
law discovery path; lessons in `agents-llm` with `course: mechanics`
(D4) and `course: astrophysics` (D5, on the N-body worlds).

**Goal.** Inferring an unknown gravitational relation and testing its
transfer (D4); unknown forces and couplings in controlled N-body worlds
with predictive tests (D5), as original contained tasks inspired by the
published benchmarks, not their assets.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F66, F69, F91.

**Acceptance criteria.** The lesson and agent rules; the transfer test of
D4 on a world the agent never probed; the N-body truth of D5 unreachable
and the agent's predictions scored by the build.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F100 — Physics reasoning benchmarks (EV1)

**Source.** Change request section 5 (B3: EV1 enhanced in revision 2).
Slot EV1 of the agent benchmarking path; lesson in `agents-llm` with
`course: mechanics`.

**Goal.** Whether models reason about independently checked physics
problems, visual and tool affordances, and counterfactual predictions,
with tool-use reasoning separated from calling a software interface; on
problems from the site's own lessons with recomputed answers.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F96, F65.

**Acceptance criteria.** The agent rule; every problem's answer recomputed
by the build; the affordance and counterfactual items use verified figures;
the score and its uncertainty over seeds shown with the failures.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F101 — Robustness, cost, and scientific failure analysis (EV4, EV5)

**Source.** Change request section 5 (B3: EV4, EV5). Slots EV4 and EV5 of
the agent benchmarking path; lessons in `agents-llm` with `course:
mechanics`.

**Goal.** Performance against noise, budget, seeds, cost, and model choice
from recorded runs (EV4); categorised failures (wrong laws, leakage,
numerical mistakes, hallucinations, overfitting) as reproducible case
studies with independent audits (EV5).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F81, F98.

**Acceptance criteria.** The agent rule; costs and call counts recorded
from the runs that produced the fixtures and never measured in CI; each
failure case reproduced from a frozen trace with the recomputed check
that exposes it.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F102 — Atomic spectroscopy lab (Q7)

**Source.** Change request section 4 (A6: Q7). Slot Q7, a measured-data
lab of the `quantum` course; the NIST infrared spectra card is a
`survey-only` candidate.

**Goal.** Real spectral lines, calibration, and simple line and level
models with uncertainty.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F89, F51; a spike with a go decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F103 — Quantum measurement statistics lab (Q8)

**Source.** Change request section 4 (A6: Q8 enhanced in revision 2),
the second half of the linked Q5/Q8 enhancement. Slot Q8, a measured-data
lab of the `quantum` course; the Sandia gate-set tomography card is a
`survey-only` candidate, and a Bell-test count dataset is used only if a
rights-cleared, methodologically suitable one passes the gate.

**Goal.** Genuine documented quantum measurement data with uncertainties,
detector and selection caveats, and a qualified statistical
interpretation; Bell-test counts against the Q5 bounds if and only if the
gate approves a suitable dataset.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F90, F51; a spike with a go decision.

**Acceptance criteria.** The lab rule; the page states which loophole or
selection the data does not close.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F104 — Exoplanet light curves lab (AST8)

**Source.** Change request section 4 (A7: AST8). Slot AST8, a
measured-data lab of the `astrophysics` course; the TESS light-curve card
is a `survey-only` candidate.

**Goal.** Real photometry, cleaning, the AST7 model fitted, and the
uncertainties of the inferred geometry.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F93, F51; a spike with a go decision; a FITS reader
only if the go decision needs it.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F105 — Galaxy rotation curves lab (AST9)

**Source.** Change request section 4 (A7: AST9). Slot AST9, a
measured-data lab of the `astrophysics` course; no candidate card exists.

**Goal.** Real rotation curves against mass models, with the assumptions
and caveats of the inference stated.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F91, F51; a new candidate card and spike with a go
decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F106 — X-ray diffraction data lab (MAT5)

**Source.** Change request section 4 (A8: MAT5). Slot MAT5, a
measured-data lab of the `materials` course; the electron-diffraction
card is a related `survey-only` candidate and a new X-ray card may be
needed.

**Goal.** Measured peaks, lattice spacing, and uncertainty against MAT1.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F94, F51; a spike with a go decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F107 — Stress-strain measurements lab (MAT6)

**Source.** Change request section 4 (A8: MAT6). Slot MAT6, a
measured-data lab of the `materials` course; no candidate card exists.

**Goal.** Real material response, the elastic regime, hysteresis, and
uncertainty against MAT3.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F95, F51; a new candidate card and spike with a go
decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### F108 — Turbulence and flow measurements lab (FL8)

**Source.** Change request section 4 (A5: FL8). Slot FL8, a measured-data
lab of the `fluids` course; the Rostock, Sheffield, and OpenPIV cards are
`survey-only` candidates distinct from F53's cylinder wake.

**Goal.** Turbulence statistics, uncertainty, and the limited regimes of
the FL2 and FL3 models.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F79, F53, F51; a spike with a go decision.

**Acceptance criteria.** The lab rule.

**Risk.** Medium. **Detailed implementation plan expected.** Yes.

### Wave C4 — Research capstone and consolidation

Order within the wave: every lesson feature of this wave after F64 (the
gates under "Phase 4"); F109 after F19 and F39; F110 after F95, F18, and
F20; F111 last among the lessons, after F49, F101, and F98; F112 last,
after every lesson feature of the phase; it may be run earlier as a
status report that declares no completion (see its block).

### F109 — Evidence maps and reproducible literature evidence (R2, R3)

**Source.** Change request section 5 (B4: R2, R3). Slots R2 and R3 of the
autonomous research path; lessons in `agents-llm` with `course:
mechanics`. F19 delivered the evidence map page, not a lesson; R2 is the
lesson that teaches reading and auditing it.

**Goal.** Linking claims to figures, code, measurements, and limitations
through the evidence map of F19 (R2); curated source claims, methods,
citation and provenance, and reproduction feasibility through the
reference register, with no generic retrieval product (R3).

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F19, F39, F28.

**Acceptance criteria.** The lesson rule; every link rendered from the
register or the evidence map; no live retrieval; an agent that proposes
sources logs them for human review and never writes a citation.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F110 — Agent-driven materials discovery (R5)

**Source.** Change request section 5 (B4: R5 enhanced in revision 2).
Slot R5 of the autonomous research path; lesson in `agents-llm` with
`course: materials`.

**Goal.** Agents coordinating bounded, reproducible material-property
simulations of MAT1 to MAT4, comparing candidates against explicit
multi-objective physical constraints, with uncertainty and validation
discussed and a model's preference never treated as evidence.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F95, F18, F20.

**Acceptance criteria.** The lesson and agent rules; the constraint checks
recomputed by the build; the agent's ranking compared with the recomputed
one.

**Risk.** Medium. **Detailed implementation plan expected.** Yes, short.

### F111 — Autonomous physics research challenge (R6)

**Source.** Change request section 5 (B4: R6) and section 10 ("Part B
research capstone"). Slot R6 of the autonomous research path; lesson in
`agents-llm` with the primary course of the chosen unknown system.

**Goal.** From an unknown system to hypotheses, experiments,
falsification, and an audited report, with controls, honest limitations,
and an evidence trail; distinct from the subject capstones T11, EM9, and
FL10 and from F49's paper reproduction.

**Dependencies.** F61, F62, F64, F113 (the gates of this phase), F49, F101, F98, F65.

**Acceptance criteria.** The lesson and agent rules; the report's claims
typed and each recomputed or marked; the audit by the F18 reviewers shown
with recomputed checks; the hidden truth revealed only after the audit on
the page.

**Risk.** High (scope). **Detailed implementation plan expected.** Yes,
likely several Issues.

### F112 — Curriculum completion audit

**Source.** Change request section 11 ("Curriculum completion") and
section 10 (Wave 4, "quality consolidation"); requirements "Project goal"
(the long-term target).

**Goal.** Establish whether the published inventory reconciles to the
reference curriculum, and say so without rounding. The audit classifies
every one of the 115 slots as one of: filled by a substantive published
lesson (the definition of done of section 11); a designated lab whose
dataset gate recorded defer or reject, with its dossier (requirements
decision 27: a lab is a target that the gate decides); a slot the human
removed from the reference structure by a recorded decision that changed
the curriculum file and the requirements' decision 23 (none exists
today); or outstanding. A slot whose feature was not scheduled, not
started, or not finished is outstanding, never deferred: the audit
reports what is missing and makes no scope decision. Completion
(requirements "Project goal"; change request section 11) is declared
only when no slot is outstanding; otherwise the audit is a status report
that lists the outstanding slots with their features. The audit also
establishes: eight courses navigable; sixteen designated labs, with the
gated ones' outcomes recorded and qualified separately from the core
slots; the four paths with valid lessons; the eleven revision-2 and
revision-3 additions and the seven enhancements present and
non-duplicative; a reproducibility audit of a sample of lessons across
courses from a fresh clone; a screen-reader pass of the path and a lesson
of each course; no published address broken.

**Dependencies.** F64 and every lesson feature of this phase (F66 to
F111, and F45, F49, F52, F53, F54, and F55 of the previous phase, which
fill slots). The audit may be run earlier as a status report; such a run
declares no completion.

**Acceptance criteria.** The audit recorded in `docs/release-readiness.md`
with the slot table of this roadmap updated; a test that every slot of
the curriculum file is classified as filled, gated (with the dossier that
records the gate's decision), removed by a recorded decision, or
outstanding, that the four classes add up to 115, and that "complete" is
written only when the outstanding class is empty; the gated labs listed
apart from the core slots with their dossiers; the sampled reproductions
byte-identical at displayed precision; the manual passes recorded.

**Risk.** Low. **Detailed implementation plan expected.** No.

## Candidate mapping

Every candidate of the change request and its outcome. "Kept" means a
feature with the candidate's number; "extends" means the work is an
obligation of an existing feature; "absorbed" means another feature
carries it; "deferred" means no feature until a trigger (see "Deferred
research candidates").

| Candidate | Outcome | Final ID | Consolidation decision |
|---|---|---|---|
| F16 Counterexample hunter | Kept | F16 | Inside the ADR 004 harness; depends on the F46 contract for what counts as a counterexample. |
| F17 Additional Lean mechanics proofs | Kept | F17 | Also the source material for F56 and F22. |
| F18 Multi-agent scientific review | Kept | F18 | Shares the validation contract with F46; harness loop run per reviewer, no new framework. |
| F19 Scientific evidence map | Kept | F19 | Generated from the claim markup of F28 (its reserved `evidence` attribute); waits for all lessons in format 2. |
| F20 Autonomous experimental design | Kept | F20 | Built on F16 and F23 rather than separate tools. |
| F21 Interactive Lean exercises | Kept | F21 | Needs an ADR for exercise stubs outside the checked library. |
| F22 Agent-assisted formal theorem proving | Kept | F22 | Under the F45 workflow and ADR 010. |
| F23 Inverse physics / parameter discovery | Kept | F23 | Shares `pbc.data` fitting with F51; teaches a different question than F20. |
| F24 Optional local AI physics tutor | Deferred | retired | Not selected: an expensive optional workflow that must not block the deterministic F13 and F14; trigger below. |
| F25 Homepage narrative | Kept | F25 | Consumes the F57 attribution text; coordinated with F44 styles. |
| F26 Generated prerequisite graph | Kept | F26 | Consumer of the F37 metadata. |
| F27 Learning path cards and difficulty scale | Kept | F27 | Consumer of the F37 metadata and F44 styles. |
| F28 Reusable lesson introduction/template | Kept, widened to format 2 | F28 | Carries the Section 11 standard, the reference register, claim and figure labels, the self-check, and the M1 pilot. |
| F29 Mechanics editorial pass M1 to M4 | Kept | F29 | M1 as the beginner pilot of the standard, after the M5 pilot. |
| F30 Mechanics editorial pass M5 to M8 | Kept | F30 | M5 first as the research-backed pilot, reviewed before M6 to M8. |
| F31 Agent/Lean editorial pass | Kept | F31 | |
| F32 Mechanics diagrams M1 to M4 | Kept | F32 | Diagrams drawn by code, labelled conceptual; no image files. |
| F33 Mechanics diagrams M5 to M8 | Kept | F33 | |
| F34 Agent/Lean diagrams | Kept | F34 | |
| F35 Code explanation and snippets | Kept, as tooling | F35 | Annotated excerpts; the prose work is in the editorial passes. |
| F36 Numeric tables/output | Kept, as tooling | F36 | The table helper; applied by the editorial passes. |
| F37 Course navigation | Kept, widened | F37 | Owns the metadata extension (course, methods, outcomes, related) as the single source of truth for F26 and F27. |
| F38 Progressive hints and solutions | Kept | F38 | Markup only, no quiz or progress; F13 may wrap it. |
| F39 Unified local setup and run recipes | Kept, plus link check | F39 | Also carries `scripts/check-links.sh` (Section 11.4, F39 row). |
| F40 Reproducibility UX | Kept | F40 | |
| F41 Self-hosted search | Kept | F41 | |
| F42 Before you begin and glossary | Kept | F42 | |
| F43 More interactive physics widgets | Kept, as science-first components | F43 | At most four components, one per lab that needs it (Section 8.3). |
| F44 Visual design and accessibility system | Kept | F44 | Includes the footer slot for F57 and the payload check. |
| F45 Agent-assisted simulation development | Kept, plus the shared workflow | F45 | The one coding-agent workflow (Section 12: F45 + F55). |
| F46 Scientific code verification and debugging | Kept | F46 | Owns the validation contract F18 and F45 reuse. |
| F47 Automated scientific analysis pipelines | Kept, as a lesson | F47 | Its analysis core is F51's (Section 12: F47 + F51). |
| F48 Reproduce an open physics paper | Absorbed | retired, into F49 | One capstone whose subject is a paper reproduction (Section 12: F48 + F49). |
| F49 Multi-agent computational research capstone | Kept, merged with F48 | F49 | |
| F50 Experimental dataset registry + feasibility | Kept, includes the spike of Section 8.2 | F50 | The spike is its first deliverable, not a new feature. |
| F51 Experimental methods and visualization foundations | Kept, merged with F47's core | F51 | |
| F52 Optical diffraction lab | Kept, conditional | F52 | The record page shows a CC BY 4.0 licence field next to a copyright line; the change request flags redistribution as unclear; the gate decides. Needs a waves-and-optics course (F15 if the human chooses it, else a later course feature). |
| F53 Flow measurements / PIV lab | Kept, conditional | F53 | Needs a compact subset and a course that exists (F15 if the human chooses fluid dynamics, a later course feature, or a `mechanics` framing its Issue justifies under ADR 008). |
| F54 Electromagnetic wave measurement lab | Kept | F54 | The compact fallback first lab if F60 is deferred, once F15 or a later course feature has given it a course; no placement by method tag (ADR 008). |
| F55 Agent-assisted experimental physics | Kept, as a lesson | F55 | Uses the F45 workflow; no second workflow. |
| F56 Experimental model formal verification | Kept | F56 | Lessons in the `lean` strand tied to a lab; no new strand. |
| Section 8.2 feasibility spike | Extends | F50 | |
| Section 8.3 visualization system | Extends | F43, F51, F44 | |
| Section 8.5 long-term dataset candidates | Deferred | none | Cards as `survey-only` in F50; triggers below. |
| Section 9 Instructor packs | New feature | F59 | Independently testable; reuses F28, F57, F12. |
| Section 10 JIDAI identity and community (repository surfaces) | New feature | F57 | One small feature; F25 and F44 consume its text. |
| Section 10 JIDAI.nl portfolio page | Not selected | none | A company-site task outside this repository. |
| Section 10 `jidai-nl` organization profile link | Not selected | none | A human action on GitHub outside this repository; no transfer. |
| Section 10 repository transfer or subdomain | Not selected | none | A separate migration decision; excluded by the requirements. |
| Section 11 research-backed editorial standard | Extends | F28, F29, F30, F31, F35, F36, F42, F39; ADR 009 | No new numbered feature for the standard (Section 3H). |
| Section 11.4 F12 research stage | Extends | F12 (delivered) by F28's protocol | The protocol in `docs/authoring.md` applies to agent-drafted content; no workflow change. |
| Section 13 R0 "finish active work" | Done | F10, F11, F12 delivered | Remaining human steps in `docs/release-readiness.md`. |
| CI budget overrun (release readiness) | New feature | F58 | The second response of ADR 003. |
| Gravitational-wave lab (Section 8.1, 13) | New feature | F60 | The planner's recommended first lab, conditional on F50. |

## Slot mapping (change cycle `final-curriculum`)

Every slot of the reference curriculum (requirements decision 23) with the
lesson that fills it or the feature that will. "Published" names a lesson
`id`. A lab is published only after its dataset's go decision; a capstone's
historical comparison (FL10) is gated separately and is not a lab. The
teaching order inside a course may differ from the label order, as the
change request states (T6, T10, T11; EM4 and EM6 to EM9; FL1, FL4, FL9,
FL5, FL10; AST10 before AST4).

### Part A, 81 slots

| Course | Slot | Working title | Kind | Status, feature |
|---|---|---|---|---|
| mechanics | M1 | Kinematics as a program | lesson | Published, `kinematics` (F02) |
| mechanics | M2 | Newton's laws | lesson | Published, `newtons-laws` (F04) |
| mechanics | M3 | Projectile motion with drag | lesson | Published, `projectile-with-drag` (F04) |
| mechanics | M4 | Harmonic oscillator | lesson | Published, `harmonic-oscillator` (F05) |
| mechanics | M5 | Numerical integrators | lesson | Published, `numerical-integrators` (F05, F30) |
| mechanics | M6 | Energy conservation | lesson | Published, `energy-conservation` (F06) |
| mechanics | M7 | Momentum and collisions | lesson | Published, `momentum-and-collisions` (F06) |
| mechanics | M8 | Kepler orbits | lesson | Published, `kepler-orbit` (F06) |
| mechanics | M9 | Double pendulum and chaos | lesson | F68 |
| mechanics | M10 | Lagrangian mechanics | lesson | F68 |
| mechanics | M11 | Hamiltonian mechanics | lesson | F68 |
| mechanics | M12 | Resonance and driven oscillators | lesson | F68 (coordinated with F45) |
| mechanics | M13 | Many-body gravitation | lesson | F69 |
| mechanics | M14 | Nonlinear dynamics and bifurcations | lesson | F69 |
| mechanics | M17 | Rotational motion, torque, and angular momentum | lesson, revision 2 | F69 |
| mechanics | M15 | Experimental: real pendulum or accelerometer data | lab | F83, gated |
| mechanics | M16 | Experimental: GW150914 gravitational-wave strain | lab | Published, `gravitational-wave-strain` (F60) |
| thermodynamics | T0 | Gas from simple agents | lesson | Published, `particles-in-a-box` (F11); `course` and `slot` set together by F70, no slot before |
| thermodynamics | T1 | Random walks and diffusion | lesson | F70 |
| thermodynamics | T2 | Kinetic theory of gases | lesson | F70 |
| thermodynamics | T3 | Entropy and thermodynamic equilibrium | lesson | F70 |
| thermodynamics | T4 | Ising model and phase transitions | lesson | F75 |
| thermodynamics | T5 | Molecular dynamics | lesson | F75 |
| thermodynamics | T6 | Heat conduction and diffusion | lesson, enhanced in revision 3 | F76 |
| thermodynamics | T9 | Heat engines and thermodynamic cycles | lesson, revision 2 | F75 |
| thermodynamics | T10 | From finite differences to finite elements and meshes | lesson, revision 3 | F76 |
| thermodynamics | T11 | Applied capstone: thermal engineering of an AI accelerator | capstone, revision 3 | F87 |
| thermodynamics | T7 | Experimental: heat transfer measurements | lab | F84, gated |
| thermodynamics | T8 | Experimental: Brownian motion tracking | lab | F85, gated |
| waves | W1 | The wave equation | lesson | F71 |
| waves | W2 | Interference and resonance | lesson | F71 |
| waves | W3 | Refraction and Snell's law | lesson | F77 |
| waves | W4 | Polarisation and Malus's law | lesson | F77 |
| waves | W5 | Diffraction and imaging | lesson | F77 |
| waves | W6 | Inverse optics | lesson | F77 |
| waves | W9 | Sound waves, resonance, and the Doppler effect | lesson, revision 2 | F71 |
| waves | W7 | Experimental: real optical diffraction images | lab | F52, gated (unchanged feature; home `waves`) |
| waves | W8 | Experimental: wave flume measurements | lab | F74 (go decision exists) |
| electromagnetism | EM1 | Coulomb's law and electric fields | lesson | F72 |
| electromagnetism | EM2 | Lorentz force and charged particles | lesson | F72 |
| electromagnetism | EM3 | Faraday's law and induction | lesson | F72 |
| electromagnetism | EM4 | Maxwell's equations and FDTD | lesson | F78 |
| electromagnetism | EM5 | RLC circuits and resonance | lesson | F78 |
| electromagnetism | EM6 | Waveguides and electromagnetic resonances | lesson, enhanced in revision 3 | F78 |
| electromagnetism | EM7 | Experimental: microwave S-parameters | lab | F54 (go decision exists; unchanged feature; home `electromagnetism`) |
| electromagnetism | EM8 | Experimental: real RLC circuit measurements | lab | F86, gated |
| electromagnetism | EM9 | Applied capstone: adaptive phased-array beam steering | capstone, revision 3 | F80 |
| fluids | FL1 | Advection and diffusion | lesson | F73 |
| fluids | FL2 | Navier-Stokes fundamentals | lesson | F79 |
| fluids | FL3 | Vortex formation and flow around obstacles | lesson | F79 |
| fluids | FL4 | Shock waves and Burgers' equation | lesson | F73 |
| fluids | FL5 | Shallow-water equations | lesson, enhanced in revision 3 | F73 |
| fluids | FL6 | Particle-based fluid simulation | lesson | F79 |
| fluids | FL9 | Finite-volume methods and conservation laws | lesson, revision 2 | F73 |
| fluids | FL7 | Experimental: particle image velocimetry | lab | F53, gated (unchanged feature; home `fluids`) |
| fluids | FL8 | Experimental: real turbulence or flow measurements | lab | F108, gated |
| fluids | FL10 | Applied capstone: reconstructing the 2025 Kamchatka tsunami | capstone, revision 3 | F88 (comparison gated) |
| quantum | Q1 | Schrödinger equation | lesson | F89 |
| quantum | Q2 | Quantum tunnelling | lesson | F89 |
| quantum | Q3 | Quantum harmonic oscillator | lesson | F89 |
| quantum | Q4 | Spin and Stern-Gerlach measurements | lesson | F90 |
| quantum | Q5 | Quantum entanglement, Bell and CHSH | lesson, enhanced in revision 2 | F90 |
| quantum | Q6 | Open quantum systems and decoherence | lesson | F90 |
| quantum | Q7 | Experimental: atomic spectroscopy | lab | F102, gated |
| quantum | Q8 | Experimental: quantum measurement statistics | lab, enhanced in revision 2 | F103, gated |
| astrophysics | AST1 | Three-body problem | lesson | F91 |
| astrophysics | AST2 | Modified gravity | lesson | F91 |
| astrophysics | AST3 | Gravitational lensing | lesson | F91 |
| astrophysics | AST10 | Special relativity and spacetime | lesson, revision 2 | F92 |
| astrophysics | AST4 | Relativistic orbits | lesson | F92 |
| astrophysics | AST5 | Cosmic expansion and redshift | lesson | F92 |
| astrophysics | AST6 | Gravitational-wave chirp simulation | lesson | F93 (cross-links M16, L5) |
| astrophysics | AST7 | Exoplanet transit simulation | lesson | F93 |
| astrophysics | AST8 | Experimental: real exoplanet light curves | lab | F104, gated |
| astrophysics | AST9 | Experimental: galaxy rotation curves | lab | F105, gated |
| materials | MAT1 | Crystal lattices and phonons | lesson | F94 |
| materials | MAT2 | Electronic band structure | lesson | F94 |
| materials | MAT3 | Elasticity and deformation | lesson | F95 |
| materials | MAT4 | Defects and material properties | lesson | F95 |
| materials | MAT5 | Experimental: X-ray diffraction data | lab | F106, gated |
| materials | MAT6 | Experimental: stress-strain measurements | lab | F107, gated |

Count: 17 + 12 + 9 + 9 + 10 + 8 + 10 + 6 = 81, of which 16 labs and 3
capstones.

### Part B, 33 slots

| Path | Slot | Working title | Status, feature |
|---|---|---|---|
| physics reasoning and scientific agents | AI0 | LLM agent designs a projectile experiment | Published, `agent-experiment` (F09) |
| physics reasoning and scientific agents | AI1 | Agent-assisted physics simulation development | F45 (unchanged feature) |
| physics reasoning and scientific agents | AI2 | Scientific code verification and debugging | Published, `verifying-scientific-code` (F46) |
| physics reasoning and scientific agents | AI3 | Counterexample hunting | Published, `counterexample-hunter` (F16) |
| physics reasoning and scientific agents | AI4 | Multi-agent scientific review | Published, `scientific-review` (F18) |
| physics reasoning and scientific agents | AI5 | Agent-assisted real experimental physics | F55 (unchanged feature) |
| physics reasoning and scientific agents | AI6 | Multimodal physics reasoning (still images; enhanced in revision 2) | F96 |
| physics reasoning and scientific agents | AI7 | Interpretable physics explanations and constraints | F96 |
| physics reasoning and scientific agents | AI8 | Physical reasoning from video (revision 2) | F97 |
| scientific law discovery | D1 | Black-box physics: discovering force laws | F66 |
| scientific law discovery | D2 | Physics without prior knowledge | F66 |
| scientific law discovery | D3 | Discovering modified physical laws | F66 |
| scientific law discovery | D4 | Discovering gravity from experiments | F99 |
| scientific law discovery | D5 | Unknown physical worlds | F99 |
| scientific law discovery | D6 | Inverse physics: parameter discovery and uncertainty (enhanced in revision 2) | Published, `inverse-physics` (F23) |
| scientific law discovery | D7 | Symbolic regression for physical laws | F67 |
| scientific law discovery | D8 | Discovering differential equations | F67 |
| scientific law discovery | D9 | Active experimental design (enhanced in revision 2) | Published, `experimental-design-agent` (F20) |
| scientific law discovery | D10 | Scientific discovery under measurement noise | F98 |
| scientific law discovery | D11 | Hidden forces and unobserved variables | F98 |
| scientific law discovery | D12 | Generalisation to unseen physical systems | F98 |
| scientific law discovery | D13 | Discovering conservation laws and physical invariants (revision 2) | F82 |
| physics agent benchmarking | EV1 | Physics reasoning benchmarks (enhanced in revision 2) | F100 |
| physics agent benchmarking | EV2 | Interactive discovery benchmarks (enhanced in revision 2) | F81 |
| physics agent benchmarking | EV3 | Agent versus non-agent baselines | F81 |
| physics agent benchmarking | EV4 | Robustness, cost, and sample efficiency | F101 |
| physics agent benchmarking | EV5 | Scientific failure analysis | F101 |
| autonomous scientific research | R1 | Automated physics analysis pipelines | Published, `automated-analysis-pipelines` (F47) |
| autonomous scientific research | R2 | Scientific evidence maps | F109 (the page is F19, delivered) |
| autonomous scientific research | R3 | Scientific literature and reproducible evidence | F109 |
| autonomous scientific research | R4 | Reproducing a physics paper with multiple agents | F49 (unchanged feature) |
| autonomous scientific research | R5 | Agent-driven materials discovery (enhanced in revision 2) | F110 |
| autonomous scientific research | R6 | Autonomous physics research challenge | F111 |

Count: 9 + 13 + 5 + 6 = 33.

### The Lean slot and the lessons beyond the baseline

| Slot | Working title | Status |
|---|---|---|
| L1 | Proving what the simulation showed | Published, `proving-what-the-simulation-showed` (F08) |
| none | Momentum in a collision, proved | Published, `collision-momentum-proved` (F17) |
| none | What symplectic Euler conserves | Published, `symplectic-euler-conserved-energy` (F17) |
| none | Lean exercises on your machine | Published, `lean-exercises-on-your-machine` (F21) |
| none | The chirp law, proved | Published, `chirp-law-proved` (F56) |
| none | Agent-assisted theorem proving | F22 (unchanged feature) |

Total: 81 + 33 + 1 = 115 slots; 119 lessons and more when complete, the
Lean lessons beyond the baseline included and never hidden.

### Enhancements of existing slots (revision 2), no new slot

| Enhancement | Where it is delivered |
|---|---|
| D6 identifiability, parameter correlations, held-out uncertainty | Delivered by F23 (`pbc.data.fit` and `pbc.data.inverse`) |
| D9 hypothesis-discriminating information gain under a budget, simulated only | Delivered by F20 (`pbc.agents.design`) |
| AI6 still-image affordances and counterfactuals | F96 |
| EV1 physical-tool understanding separated from software interfaces | F100 |
| EV2 full, partial, and no prior-knowledge comparisons under one protocol | F81, on F65's protocol |
| R5 physical multi-objective constraints | F110 |
| Q5 Bell and CHSH inequalities, with Q8 using eligible data only if the gate approves it | F90 (Q5) and F103 (Q8) |

## Experimental data choice

Planner's recommendation for the first measured-data lab, to be confirmed
or overturned by the evidence of the F50 spike:

1. **First lab: GW150914 strain (F60), as a mechanics-course extension of
   M8.** Reasons: the data is small (about 1 MB per detector for 32 s at
   4096 Hz), calibrated, CC BY 4.0 with a stated acknowledgement, in HDF5
   and plain text (readers that lock as ordinary Python dependencies); the
   physics connects to the published course through the two-body orbit of
   M8 and a Newtonian-order chirp model, so it belongs to a course that
   exists instead of waiting for a second course; the measurement-to-model
   loop is complete (measured strain, disclosed filtering, model, residuals,
   a typed claim); the visual is immediately understandable. Risk to
   verify in the spike: the processing steps must be explained so that a
   whitened signal is never presented as the measurement, and the model's
   scope must be stated honestly.
2. **Fallback: NPL S-parameters (F54), after F15.** (Since
   `final-curriculum`: F15 is dropped and F54's course is `electromagnetism`,
   created by F72; the rest of this item is history.) The most compact and
   technically robust dataset (3.1 MB, Touchstone, CC BY 4.0), but it needs
   RF background the course does not teach and has no published course to
   belong to, and ADR 008 allows no lesson without a primary course. It
   becomes the first lab only if F60 is deferred or rejected by the spike
   and F15 has chosen an electromagnetism or waves-and-optics course for it;
   the fallback path therefore runs through F15 before F54, and the F50
   dossiers are the evidence for that choice.
3. **Bridge for F15: the Aalborg wave flume.** (Since `final-curriculum`:
   F15 is dropped; the flume is W8 of the `waves` course created by F71, and
   F52's home is the same course; the rest of this item is history.) The strongest
   measured-versus-modelled set (CC BY 4.0, measured and CFD series), but
   78.6 MB and a waves subject; it is the natural first lab of a waves and
   optics course if the human chooses that topic for F15, and the spike's
   dossier is the evidence for that choice. Once F15 chooses waves, the
   flume is the bridge: its course is the home F54 publishes in, and the
   fallback of item 2 no longer waits.
4. **Not first:** optical diffraction (RAR archives, 46 MB and more,
   photographs), cylinder-wake PIV (1.1 GB MAT), and every Section 8.5
   candidate, for size, format, or course reasons recorded in their cards.

Permissions, sample-file evidence, plotting approach, visual accessibility,
and the size and CI budgets are the spike's deliverables (F50 acceptance
criteria 3 and 5), not assumptions of this roadmap.

## Lesson editorial decision

The Section 11 standard is adopted as written into the requirements and
the architecture (format 2), with ADR 009 for the references. The audit of
the eleven published lessons on 2026-10-09, from their sources at `2f011ea`,
found these evidence-backed improvements, which the pilots and passes
address:

- **No external reference anywhere.** No lesson body contains a URL; M5's
  "Further reading" names two books without a section, a URL, or a reason.
  The standard asks for curated depth paths at the relevant concept, with a
  reason, from the register.
- **Console tables everywhere.** More than forty fixed-width `print()`
  tables carry the numeric results; none is a semantic table with header
  cells (F36).
- **Descriptive captions.** Every figure has a caption and alt text, but
  the interpretation sits in the prose after it, and captions do not
  state the figure's status (F28 figure status, interpretive captions).
- **Hand-typed numbers.** M8 has no inline expression and types every
  number in prose; M2, M3, M4, M6, M7, and A1 type approximate values
  ("about one per cent", "about forty thousand steps") and some alt texts
  carry digits (M6 line 376, M8 line 458, A1 line 339) (F28 check).
- **Unmotivated statements.** The exponential drag solution and the
  Reynolds regimes in M2, the drag law and interpolation bound in M3, the
  "same algebra shows" rotation in M4, the period series and the symplectic
  bound in M6, the elastic-collision formulas in M7, the orbital elements
  and Kepler's equation in M8, the virial correction and the Rayleigh
  distribution in the gas lesson, the residual claim in L1 (editorial
  passes).
- **Limits.** Only L1 has a dedicated "What the proofs do not cover"
  section; M6 and the gas lesson have a subsection; the others state limits
  only inside the assumptions (format 2 `limits`).
- **Openings.** Most lessons open with a physical question or a link to an
  earlier result; A1 and the gas lesson open with the technique (F31).
- **Code sections.** M6, M7, and M8 show four or more excerpts under one
  sentence; no excerpt points at the physically important line (F35).
- **Method distinctions are correct today.** M5 states and implements
  velocity-first symplectic Euler, velocity Verlet with a predicted
  velocity, and classical fixed-step Runge-Kutta 4, and nothing uses
  SciPy's adaptive solver; the passes must keep it so when sources are
  added.

Candidate sources for M5 (Section 11.3) enter the F30 research as inputs
with documented fitness to check, not as links to insert: each is reopened,
compared with at least one alternative, and recorded in the register only
if it adds a derivation, intuition, or figure the lesson lacks and matches
the exact variant the lesson implements.

## Deferred research candidates

Not features. Each has a trigger for revisiting; until then no Issue.

| Candidate | Why deferred | Trigger to revisit |
|---|---|---|
| F24 Optional local AI physics tutor | Optional, expensive, and must not block the deterministic F13 and F14; the requirements forbid a hosted tutor | F13 and F14 delivered and a learner need recorded in Issues that hints (F38) and recommendations (F14) do not meet |
| CERN CMS event displays (Section 8.1) | A showcase, not a course commitment; CC0 on record | A particle-physics course chosen for F15 or a later course, and F43's 3D viewer justified by it |
| Solar, stellar, and exoplanet observations (SDO, Gaia, TESS) | Observational labs with calibration and selection effects beyond mechanics | A course that needs them; F51 readers for FITS justified by a go decision |
| Rostock PIV + fluorescence | Phase-averaged data; advanced fluid visualization | F53 delivered and a demand for a second fluid lab |
| ALMA DSHARP, ALMA HL Tau, Euclid Q1 | Large files, specialist calibration | An astrophysics course under F15 |
| Electron diffraction, UKAEA MAST, superconducting-qubit tomography, IR interferograms, NIST IR spectra, LenslessPiCam, Haidinger rings, shock-tube schlieren | Size, specialism, rights, or provenance questions recorded in their `survey-only` cards | A course or lab that needs them and a feasibility spike with a go decision |
| JIDAI.nl portfolio page | Outside this repository | A company-site task, tracked there |
| `jidai-nl` organization profile link, repository transfer, project subdomain | Outside this repository; transfer excluded by the requirements | A separate migration decision with its own review |
| A scheduled link-check workflow | Would add a workflow trigger | Link rot found faster than quarterly manual runs catch it, and a review of the trigger |

Deferred by the change cycle `final-curriculum` (2026-10-12), with no
feature and no Issue (change request sections 1, 4.1, and 12, decision 11;
requirements non-goals):

| Candidate | Why deferred | Trigger to revisit |
|---|---|---|
| Nuclear and particle physics (4 slots), plasma physics (3), geophysics and climate physics (4): the 126-slot extension | Outside the core curriculum by the requirements | A separate planning decision after the reference curriculum is substantially published |
| Battery thermal runaway, Formula 1 aerodynamics | Inspiration for T11 and FL2/FL3 only; not selected | A separate planning decision; never an implicit capstone |
| JWST atmospheric retrieval for A7 | Discussed, not selected; A7's exoplanet lessons stay as enumerated | A separate planning decision |
| Any capstone for A1, A3, A6, A7, or A8 | The requirements limit capstones to T11, EM9, and FL10 | A requirements change |
| Physics-informed machine learning, a mathematics curriculum, a generic AI or machine-learning curriculum | Excluded by the requirements | A requirements change |
| Embedding external benchmark assets (NewtonBench, PhysGym, DiscoverPhysics, GravityBench, PhysBench, PhysToolBench, ...) | Inspiration for original contained tasks; licences and assumptions unchecked | A licence and assumption review recorded on a card, lesson by lesson |
| Selecting the Lean build with ADR 014 | Requirements, unresolved question 8 | The human's decision with or after F61 |

## Execution order and first-wave release plan

By dependency, not by number. A wave is a grouping for planning; the human
picks the next feature among those whose dependencies are done.

| Wave | Order within the wave | Outcome |
|---|---|---|
| R0 | F58 | CI within budget, recommended before pages are added but not a gate for R1 (the per-check budgets and ADR 003 decision 6 stay the guard); the release of the MVP tagged by the human (`docs/release-readiness.md`) |
| R1 | F44, F57, F37, F35, F36, F39 in parallel worktrees; then F25 (after F57), F26 and F27 (after F37); then F28 (M1 template pilot); then F30's M5 pilot; then F29 (M1 editorial), F30 (M6 to M8), F29 (M2 to M4) | A clear, honest, identified site with the editorial standard proven on both pilots and the mechanics course migrated; a release "clarity" tagged after it |
| R1, beside | F50 spike (no page) | The go, defer, or reject decisions and the first-lab confirmation |
| R2 | F42, F38, F40, F41, F31, F32, F33, F34, F59; F46, F45, F16, F17 | All lessons in format 2 with diagrams, hints, glossary, search, one instructor pack; trustworthy scientific coding with one counterexample lesson and further proofs |
| R3 | F51, then F60 (or F54 as the fallback, after F15 has chosen its course; since `final-curriculum`, F15 is dropped and F54 waits for F72), F43's first component | The first measured-data lab published after its gate |
| R4 | F54, F53, F52 as their courses exist (F15 gives at most one of them a course; the others wait for a later course feature, or for F53 a justified `mechanics` framing; since `final-curriculum`, F15 is dropped and the courses are F72, F73, and F71, with no `mechanics` framing); F55, F23, F47, F18, F19, F56 | Evidence and advanced labs |
| R5 | F20, F21, F22, F49 | Research capstones |

Phase 4, by dependency; the first wave stays reviewable because every
feature in it is a tooling change with tests (F61, F113, F62, F63) or one
page with accuracy checks (F64). No lesson of the phase is drafted before
F61 and F62 have landed, no lesson that takes the count past 32 before
F113 has, and no lesson of waves C2 to C4 before F64 and F113 have (the
gates under "Phase 4"); there is no cost exception.

| Wave | Order within the wave | Outcome |
|---|---|---|
| C0 | F61 and F62 in parallel worktrees; F113 after F61; then F63; then F64 | Verification proportional to a change within 12 minutes; a full run that fits the timeout at 110 lessons; eight courses, the reference curriculum, and the slots; verified previews; the course-first Learning Path, before the bulk of the lessons |
| C1 | F65 (may start during C0); after F61 and F62, and after F113 once the lesson count would pass 32: F66 and F67; F68, F70, F71, F72, F73 in parallel worktrees; F69 after F68; F74 after F71; F52, F53, F54, F45, F55 as their dependencies are met | The discovery foundation and its first lessons; the first lessons of thermodynamics, waves, electromagnetism, and fluids; advanced mechanics; the second measured-data lab (W8, go decision in hand) and the already planned labs as their courses exist |
| C2 | After F64 and F113: F75, F76 after F70; F77 after F71; F78 after F72; F79 after F73; F80 after F78; F81, F82 after the discovery lessons; F83 to F86 through their gates | Core subject expansion, the finite-difference to finite-element bridge, conservative fluid methods, the phased-array capstone, the first benchmarks, invariant discovery, and gated labs |
| C3 | After F64 and F113: F87 after F76; F88 after F73; F89 to F95 by dependency; F96, F97, F98, F99, F100, F101; F102 to F108 through their gates | The thermal and tsunami capstones (the tsunami comparison only after its gate), quantum, astrophysics with relativity, materials, the remaining reasoning, discovery, and benchmarking lessons, and gated labs |
| C4 | After F64 and F113: F109, F110, F111; F49 and F22 as their dependencies are met; F112 after every lesson feature of the phase | The research capstone, the last path lessons, and the completion audit, which declares completion only when no core slot is outstanding |

Features F13 (#89) and F14 (#94) are delivered with their approved scope;
F64 keeps their progress marks and recommendations on the redesigned path.
F15 is dropped by `final-curriculum` (ADR 013 decision 7) and is never
scheduled: the courses of the labs F54, F53, and F52 are created by F72,
F73, and F71, and each lab starts when its course feature and its other
dependencies are delivered (the Phase 4 waves above). F12's workflow is
unchanged; the reference protocol of F28 applies to agent-drafted content
through `docs/authoring.md`.

The first wave stays reviewable because every feature in it is one of:
a tooling change with tests (F58, F35, F36, F37, F44, F39), a page with
accuracy checks (F25, F57, F26, F27), or one lesson at a time with two
independent reviews (F28, F30, F29). No feature in R1 implements a lab,
sends outreach, or creates content for the JIDAI website.

## Verification strategy for the next phase

What each new kind of artifact is checked by, extending `docs/architecture.md`
("Inside one verification run"). Every check is an entry in
`scripts/verify.conf`, runs identically locally and in CI, and fails on a
violating input shown by a test; the one deliberate exception is named.

| Artifact | Check | Feature |
|---|---|---|
| Lesson metadata (course, methods, outcomes, related, format) | Lesson source check: vocabulary, counts, existence; path page and header generated from it | F37, F28 |
| Format 2 parts: limits, self-check, claim labels, figure status, "Go deeper" keys, tables, computed numbers | Lesson source check for lessons that declare format 2; the default flips when every lesson has migrated | F28 |
| Reference register | Schema; every key used or reserved; no raw URL typed in a lesson source, with the helper-generated structural links of I22 exempt | F28 |
| External link validity | `scripts/check-links.sh`, on demand, never in `verify.conf` and never a merge gate (ADR 009) | F39 |
| Dataset cards and samples | Schema; caps; checksum; rights; a parsing test per sample; the build passes with data portals and external web hosts blocked | F50 |
| Measured-data figures | Status label from the sample's artifact type; measured-versus-model helpers; review | F51 |
| Diagrams | Executed cells, `conceptual` label, byte-stable | F32 to F34 |
| Page payload | Built-site check: initial 3 MB (raised from 1.5 MB by the project owner on 2026-10-10; the F44 block above is the historical record of the 1.5 MB that feature delivered and measured), on demand 3 MB, 5 MB in all; the budget table of `docs/architecture.md` is authoritative | F44, F43 |
| Widgets and components | The F07 checks plus the observed-value test and the keyframe | F43 |
| Coding-agent exercises | A test that no workflow, script, or check invokes an agent; the produced reference code and tests verified like any code (ADR 010) | F45 |
| Harness lessons | Replay without credentials; the ADR 004 boundary tests on every allowlist | F16, F18, F20 |
| Identity text | Built-site check that the canonical text is where it must be and nowhere else; `CITATION.cff` schema | F57 |
| CI structure | Every check in exactly one group; one aggregate required check; permissions | F58 |
| Local execution | `./scripts/verify.sh` unchanged in meaning; the setup page's required commands equal CI's; optional workflows "not verified" | F39 |

Added by the change cycle `final-curriculum`:

| Artifact | Check | Feature |
|---|---|---|
| Lesson input digests and the selection | The digest changes for every input kind and is absent for an unfollowable lesson; the selection equals the changed lessons, or every lesson when a lesson has no digest or a shared input changed; a run on `main` and a run without a base verify everything; the published site is the fully verified one | F61 |
| The base of a pull request run | Published only after `verify` passed; retrieved read-only and accepted only when the run that produced it is a `push` run on `refs/heads/main` whose `verify` concluded with success, established from that run's recorded event, branch, and conclusion and never from the artifact's name or recency; its contents are data, nothing in it executed or read as configuration; complete and of the current format; an artifact of a pull request run or of a failed `main` run is rejected, and a missing or rejected base runs everything | F61 |
| The context of a page on a run with a base | An inserted or retitled lesson, or a changed prerequisite or related link, updates the unchanged pages that show it; every page names the commit of the run; the pages that are not lessons are never restored | F61 |
| The identity of the checks | A change to any input of the identity makes the run a full run that restores nothing from the base; no reproduction compares bytes with a result of the base; a base without an identity runs everything | F61 |
| The lesson shards and the assembly of a full run | The lesson shards (shares of the lessons derived from their count, not the division of `tests/e2e/shards.json`) cover every lesson exactly once within the lesson-shard size and equal the workflow's; every comparison of bytes is on the machine that computed them; the assembled site's lesson pages equal the shards' reproduced pages; a failing shard or an incomplete assembly fails `verify`; every job of a full run within 35 minutes at the measured size and in the projection to 110 lessons | F113 |
| The curriculum file and the `slot` field | Schema; 115 slots in the agreed counts; every slot known; no slot filled twice; a planned slot never linked or counted; the home page's planned list derived from it | F62 |
| The prerequisite graph across strands | A prerequisite in a later strand is accepted (the T0 to T2 progression, a mechanics lesson on a Lean lesson); a later prerequisite in the same strand and a cycle are rejected; the course view orders by the slot order of the curriculum file; every previous address resolves | F62 |
| Lesson previews | Exactly one per lesson, traced to its figure cell or the fallback, byte-stable, with alt text, within the path page's payload | F63 |
| The Learning Path page | Equals front matter and the curriculum file; every lesson reachable without scripts through its course and each path; every previous address and graph node resolves; accessibility, keyboard, payload, and width checks | F64 |
| Discovery environments and benchmark scores | The hidden truth unreachable through the allowlist; scores recomputed from frozen traces; baselines on the same environment and budget; no live call in CI | F65 and every path lesson |
| Capstone and finite-element lessons | The credibility claim and figure labels present; the reference comparison and the refinement figures generated by the build; the required path within the page budget on the pinned stack; an optional tool's artifact carries a card | F76, F80, F87, F88 |
| Generated motion clips | Reproduced by the build, labelled generated, within the on-demand budget, loaded after a user action | F97 |
| Curriculum completion | Every slot classified as filled, gated, removed by a recorded decision, or outstanding, adding up to 115; "complete" only with no outstanding slot; gated labs listed apart with their dossiers; sampled reproductions from a fresh clone; the manual passes recorded | F112 |

Manual gates that stay manual: independent physics and pedagogy reviews per
lesson (through the existing review workflow); the human's approval of
identity copy, of the sandbox profile, of any CI or ruleset change, of
every go decision on a dataset, of each course's lesson list in its
Issues, and of the curriculum file; a screen-reader pass per release.

## Not on the roadmap

The requirements' non-goals stay excluded: accounts and server-side learner
data, any backend, analytics and tracking, in-browser Python and hosted
notebooks, formal verification of the Python code, certification or grading
that leaves the browser, languages other than English, a mobile app, hosted
or runtime LLM calls and any tutor or chat on the site, marketing surfaces
of any kind, outreach campaigns, a repository transfer or a changed Pages
URL, changed copyright or licence holders, bundled large or restricted
datasets, and any claim that a proof establishes a measurement or that
every experiment has an LLM or Lean counterpart. Since the change cycle
`final-curriculum`, also: lessons that build sensor experiments, record
audio, collect classroom or smartphone data, control instruments, or
operate a physical laboratory; a mathematics curriculum, a
physics-informed machine-learning track, or a generic AI or
machine-learning curriculum; the nuclear and particle, plasma, and
geophysics and climate expansions; a capstone presented as a calibrated
digital twin, a fabricated or validated device, or an operational
forecast, and any capstone beyond T11, EM9, and FL10; a heavyweight
solver as a mandatory build or CI dependency; and decorative, stock,
hand-copied, or externally hosted images. Adding any of them is a
requirements change that returns to Project Grill.
