# Physics by Construction — Final Curriculum & Learning Path Planning Change

**Date:** 2026-10-10  
**Revision:** 3 — 115-lesson core (four applied-simulation additions to revision 2)  
**Type:** Planning change request (`start-planning.sh --change --grill`)  
**Status:** Proposed; not approved, implemented, or merged  
**Project:** [taspinar/physics-by-construction](https://github.com/taspinar/physics-by-construction)  
**Related existing change:** `docs/changes/physics-next-phase.md`  
**Purpose:** Adopt the revised 115-lesson curriculum, including an authentic progression into numerical engineering (FDM → FEM, phased-array modelling, conservative shallow-water simulation), two newly chosen applied capstones (AI-accelerator thermal modelling and historical tsunami propagation), the previously selected A4 phased-array capstone, genuine experimental data, physics/AI research paths, and an accessible Learning Path redesign.

> **Instructions to the planning agent:** Treat this as a human-authored curriculum decision and planning input, **not** a request to implement the remaining curriculum in one PR. Run a proper planning change. Reconcile all IDs, published lessons, completed features, active GitHub Issues and accepted ADRs against the *current* `origin/main` before writing changes. The lesson IDs in this document are **curriculum labels**, not reserved repository lesson IDs or new F-numbers. Do not silently rename published lessons, reuse retired feature IDs, change their URLs, or recreate delivered work. Report any contradictions for human approval.

## 1. Executive decision

Physics by Construction (PBC) shall have **two complementary parts**:

- **Part A — Computational & Experimental Physics:** Eight subject-focused physics courses. Teach the actual physics through clear explanations, executable Python models, numerical simulations, independent checks, and **real experimental/observational data integrated into each mature course**. No LLM is needed to complete these courses.
- **Part B — Physics + LLMs & AI Agents:** Four cross-cutting learning paths about scientific reasoning, law discovery, agent benchmarks, and autonomous physics research. Reuse the physical models and measured datasets from Part A. Agents remain bounded, local/learner-operated where appropriate, independently checked, and optional to use the site.
- **Existing Lean lesson:** Retain the published Lean/formal-verification lesson and previously approved Lean features. Do **not** add a separate Mathematics curriculum. Physics-specific formal proofs remain available where useful, without conflating a proof of a mathematical model with evidence about physical measurements or Python implementation correctness.

**Target reference curriculum:** **115 lesson slots** = **81 in Part A** + **33 in Part B** + **1 existing Lean lesson**. Revision 2 defined 111 slots (77 + 33 + 1) after adding **five fundamental/numerical physics lessons** (M17, T9, W9, FL9, AST10), **two AI/agent lessons** (AI8, D13) and seven targeted enhancements (D6, D9, AI6, EV1, EV2, R5, Q5/Q8). **Revision 3 adds four Part A slots**: **T10** (finite elements and meshing), **T11** (AI accelerator thermal engineering capstone), **EM9** (adaptive phased-array beam steering capstone, selected in the prior discussion), and **FL10** (historical 2025 Kamchatka tsunami propagation capstone). No new Part B slots or separate mathematics curriculum. The historical conceptual baseline counts **11 already published slots** (8 Mechanics, 1 agent-based gas, 1 LLM experiment, 1 Lean), giving **104 future slots at that historical baseline**. This is a *planning baseline*, not a claim that only 11 lessons are live when the planner runs. Recently delivered F17/F45/F46/F55 or other features may already have published additional lessons. **Reconcile the actual inventory and report delivered/new totals explicitly**; never duplicate existing work merely to match these numbers. Keep 115 as the reference curriculum structure unless a real conflict requires a documented human decision.

| Component | Tracks/courses | Reference lesson slots | Experimental-data labs |
|---|---:|---:|---:|
| Part A | 8 physics courses | 81 | 16 designated labs (two per course) |
| Part B | 4 research/method paths | 33 | Uses data from A rather than duplicating datasets |
| Existing Lean foundation | Existing formal-verification strand | 1 | Not a new math course |
| **Total core curriculum** | | **115** | **16** |

**Out of core scope (future optional expansions):** Nuclear & Particle Physics (4 slots), Plasma Physics (3 slots), Geophysics & Climate Physics (4 slots) = 11 extra, for a possible **126-slot** long-term extension. Physics-Informed ML is **excluded from this curriculum change**; do not introduce a track or create feature issues for it. No independent math, general AI engineering, or generic ML curriculum.

### Revision 2 — agreed additions and exclusions

This revision supersedes the **104-slot count** in the previous draft, not previously published/approved repository decisions. New lessons: **M17, T9, W9, FL9, AST10, AI8, D13**. Existing lesson upgrades: **D6, D9, AI6, EV1, EV2, R5 and Q5/Q8** (the Q5/Q8 pairing is one thematic enhancement across two established slots). No new physics labs, microphone/sensor measurements, instrument-control agents or Physics-Informed ML are requested. No roadmap Fxx IDs are assigned in this document; the planner must allocate them after live reconciliation.

### Revision 3 — selected numerical-engineering additions and capstones

This revision **adds four Part A slots to the revision-2 baseline**: **T10**, **T11**, **EM9**, **FL10**. The user has now selected **AI Accelerator Thermal Modelling** (A2) and **Tsunami Propagation** (A5); the previously expressed **Adaptive Phased-Array Beam Steering** preference (A4) is also integrated. **A7's existing exoplanet lessons remain unchanged**: a JWST atmosphere-retrieval capstone was discussed but not explicitly selected as part of this revision. **EV battery thermal runaway and Formula 1 aerodynamics** are deferred inspiration only, **not** required or separately scheduled capstones. Do not introduce capstones into A1, A3, A6 or A8; keep their valuable fundamental, numerical and measured-data lessons intact.

Core educational aim: progress from governing equations and numerical verification to a **bounded professional workflow** (physical requirements → model → discretization/geometry where appropriate → solve → mesh/time-step or parameter verification → uncertainty/limitations → qualified design/scientific decision). Do **not** demand CAD/meshing in domains where it is unnecessary; the A4 array-factor model is an analytical/numerical electromagnetic system, and A5 uses geospatial meshes/grids rather than conventional CAD. Do not equate a colorful plot, solver convergence or a digital-twin label with physical validation.

**Counts:** A2 **10 → 12**; A4 **8 → 9**; A5 **9 → 10**. All other courses unchanged. Part A **77 → 81**; total **111 → 115**. The original **16 designated measured-data labs remain exactly 16**. An approved historical-observation comparison within FL10 is a capstone validation component, **not** a seventeenth designated lab. All candidate external observational datasets still require F50 approval.

## 2. Non-negotiable continuity and planning safeguards

1. Respect `docs/PROJECT_REQUIREMENTS.md`, `docs/architecture.md`, existing accepted ADRs, and the previously approved `physics-next-phase` change, except where this request explicitly asks the planning/Grill process to amend them. **Use `--grill` if these are new/changed product requirements.** Do not assume the previous F15 one-course rule can support eight courses unchanged.
2. Keep all prior Fxx IDs stable; **never reassign retired IDs** (including F24/F48). Leave delivered feature blocks as history. A scope adjustment to an already-issued/merged feature needs a new dependent feature. Assign new Fxx identifiers only in planning, using the next available IDs.
3. Keep every existing published URL, lesson identifier, old strand identifier and internal link working. Current `mechanics`, `agents-llm`, `agents-abm`, and `lean` strands remain valid. New subject courses need approved stable identifiers and placement rules; no silent URL migrations.
4. Preserve the *three facets* described by ADR 008: **physics course** (subject), **methods** (cross-cutting technique), **strand** (URL/order). One lesson has one primary course and may have multiple methods. Part B is a *method/learning-path view*, **not** a physics course or a duplicate set of lesson pages.
5. Explicitly propose a superseding/new ADR for any required change to ADR 008's course creation, strand and navigation restrictions. F15 currently establishes **one** additional course: reconcile or supersede its restriction through approved planning, not a feature-time workaround. Do not edit a delivered F15 issue to manufacture eight courses.
6. Keep `F50` (dataset registry/feasibility decisions) and `F51` (reusable experimental-analysis methods) as shared infrastructure. Preserve the already planned `F52` optical diffraction, `F53` PIV, `F54` microwave S-parameters, `F60` LIGO/GW150914 and `F55` agent-assisted measured-data work. Do not create clones or claim dataset approvals that have not actually been granted.
7. Distinguish **simulated**, **measured**, **calibrated**, **processed**, and **conceptual** figures. Explain uncertainty, assumptions, validation, error modes, and scientific limitations. Model fit alone never proves a physical law; an LLM explanation is never its own verification.
8. Keep the existing English-language, static Quarto/GitHub Pages architecture, open licensing, no registration or analytics, learner-owned local LLM API keys, fully accessible content without JavaScript, deterministic builds and scientific content checks. Do not use this change to migrate the website, edit company ownership, change legal attribution, or introduce a runtime LLM backend.
9. A verified lesson is substantive physics education: physical question; intuition, assumptions, essential derivation and units; runnable code; science-first figures; numerical/experimental verification; uncertainty/limits; exercises, self-check, source register and reproduction instructions. Avoid mass-produced shallow stubs.
10. Planning should record **delivery dependencies and independent feature slices**. No rule that each curriculum slot must equal one feature, and no one-feature-per-repository pattern. Shared simulation environments, dataset readers, benchmark harnesses and diagrams should be reused.
11. **No hardware-focused expansion:** Do **not** create lessons for building sensor experiments, collecting acoustic recordings, remotely controlling laboratory instruments or operating autonomous physical laboratories. The existing 16 real-data labs work with authentic, properly licensed **already-collected data**. W9 is a numerical/conceptual acoustics lesson, not a microphone lab. AI8 works with approved existing video clips or reproducible simulated clips; no webcam, device-control backend or student upload service.

## 3. Content and navigation model

**Primary site navigation:** Physics Courses (Part A) and Physics + AI (Part B). Also offer cross-cutting filters/views by **Simulation**, **Experimental Data**, **Agent-Based Modelling**, **LLM Agents**, and **Formal Verification**, derived from existing lesson metadata. A lesson should appear as *one canonical page* with cross-links, not multiple independent copies.

**Every mature Part A course** should normally include (a) fundamental numerical models, (b) scientifically meaningful experiments or parameter exploration, and (c) **at least two real-data labs as the long-term curricular target**. Real-data publication is gated by F50; courses may launch with simulations first. No fabricated data, synthetic data presented as measured, or unlicensed samples to satisfy a quota.

**Part B** must progressively distinguish: solving a known physics problem; running a tool-assisted experiment; identifying parameters in a known model; discovering an unknown functional form; active selection of experiments; inference with hidden variables; scientific explanation and falsification; robust generalisation; agent benchmarking; independent report verification. Use physics simulations and actual data from A.

**Legacy lessons:** Map existing Mechanics M1–M8 into A1 without moving URLs. Keep the existing F11 gas lesson under its original `agents-abm` URL and expose it as **T0** in A2 once the Thermodynamics course exists (course metadata and cross-links only, if permitted by a reviewed migration). Keep the F09 LLM projectile experiment under its original `agents-llm` URL and expose it as **AI0**. Keep the F08 Lean lesson under its original `lean` URL as **L1**. Any actually delivered F17/F46/etc. content should be mapped rather than rebuilt.

## 4. Full Part A curriculum — 81 slots

**Curriculum-label convention:** M, T, W, EM, FL, Q, AST and MAT below are *pedagogical labels*. The planner must assign/retain valid repository lesson IDs and courses/strands according to the approved architecture. References to Fxx show continuity with approved features; they are not requests to reopen or overwrite finished Issues.

### A1. Classical Mechanics — 17 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| M1 | Kinematics as a Program | State, time step, explicit Euler, analytic comparison and error convergence. | **Published** (F02) |
| M2 | Newton's Laws | Forces, coupled first-order equations, falling with linear drag. | **Published** (F04) |
| M3 | Projectile Motion with Drag | Quadratic resistance, numerical trajectories, limiting cases and launch range. | **Published** (F04) |
| M4 | Harmonic Oscillator | Oscillator dynamics, exact solution, phase space, explicit Euler energy error. | **Published** (F05) |
| M5 | Numerical Integrators | Explicit/symplectic Euler, Verlet, RK4; stability, order, cost and energy behavior. | **Published** (F05); preserve editorial work F28/F30 |
| M6 | Energy Conservation | Work, energy, numerical drift and nonlinear pendulum. | **Published** (F06) |
| M7 | Momentum and Collisions | Pair forces, centre of mass, elastic collisions. | **Published** (F06) |
| M8 | Kepler Orbits | Central forces, conserved energy/angular momentum, long-time error. | **Published** (F06) |
| M9 | Double Pendulum and Chaos | Coupled dynamics, sensitive initial conditions, Lyapunov analysis. | New |
| M10 | Lagrangian Mechanics | Derive and simulate constrained/coupled mechanical equations. | New |
| M11 | Hamiltonian Mechanics | Phase space, symplectic structure, geometric integration. | New |
| M12 | Resonance and Driven Oscillators | Damping, resonance curves, forcing and validation. | New |
| M13 | Many-Body Gravitation | N-body orbits and long-term numerical stability; compare REBOUND. | New |
| M14 | Nonlinear Dynamics and Bifurcations | Attractors, bifurcations and failure of linear approximations. | New |
| M17 | **Rotational Motion, Torque and Angular Momentum** | Rigid-body rotational dynamics, inertia tensors at an introductory level, torques and conserved angular momentum; simulate gyroscopic precession as a worked example, with checks for units, energy and angular-momentum limits. | **New in revision 2**; link to M10/M11 and D13 |
| M15 | **Experimental: Real Pendulum / Accelerometer Data** | Fit dynamics to real motion data, calibration, noise, residuals and uncertainty. | New; F50/F51 gate |
| M16 | **Experimental: GW150914 Gravitational-Wave Strain** | Process authentic LIGO strain, compare a stated leading-order chirp model, quantify limits. | **F60**, do not duplicate |

M16's **primary home remains Mechanics** (historical bridge from M8), and Astrophysics links to it. Keep the measured/processed distinction explicit for GW150914.

### A2. Thermodynamics & Statistical Physics — 12 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| T0 | Gas from Simple Agents | Emergent gas behavior from simple local particle rules; ABM method remains visible. | **Published F11**, preserve `agents-abm` URL |
| T1 | Random Walks and Diffusion | Microscopic randomness to macroscopic diffusion laws. | New |
| T2 | Kinetic Theory of Gases | Particle collision dynamics and Maxwell–Boltzmann distributions. | New |
| T3 | Entropy and Thermodynamic Equilibrium | Macroscopic entropy from ensembles, scope/limitations. | New |
| T4 | Ising Model and Phase Transitions | Temperature, magnetisation, critical behavior and finite size. | New |
| T5 | Molecular Dynamics | Interparticle potentials, thermodynamic observables and drift checks. | New |
| T6 | Heat Conduction and Diffusion | Bridge from lumped cooling ODEs to 1D/2D spatial heat PDEs; finite differences, conductive/convective boundary conditions, stability, grid/time-step convergence and units. Provides the transparent numerical baseline for T10/T11. | New; **enhanced in revision 3**, no extra slot |
| T9 | **Heat Engines and Thermodynamic Cycles** | Simulate idealized Carnot and comparison cycles, calculate heat/work/efficiency from p–V paths, and check first/second-law constraints and model assumptions. | **New in revision 2** |
| T10 | **From Finite Differences to Finite Elements and Meshes** | Start from T6's 2D heat equation: explain weak-form intuition and piecewise-linear finite elements; generate/inspect a small triangular mesh, assemble and solve a sparse linear system, apply explicit boundary conditions, and compare against a finite-difference or analytical/manufactured reference. Include mesh-quality/refinement checks, energy/heat-flux balance and units. Python/NumPy/SciPy in required path; Gmsh and FEniCSx as optional reference tools, not mandatory CI dependencies. | **New in revision 3**; T6 prerequisite; shared computational method, **not a new mathematics course** |
| T11 | **Applied Capstone: Thermal Engineering of an AI Accelerator** | Design a **hypothetical** multi-hotspot accelerator package or cold-plate proxy. Define heat loads, geometry/material conductivities, contact/convective boundary assumptions and thermal constraints; compute transient/steady temperature fields; compare cooling/material/layout scenarios; optimize maximum temperature subject to stated mass/size/heat-removal constraints; perform mesh/time-step and sensitivity studies with an independent baseline, and report a defensible trade-off. Label it a **digital-twin-style teaching prototype**, **not** a calibrated twin or validated model of a proprietary GPU. No vendor-specific secret data or forced full 3D CFD. | **New in revision 3**; T6 → T10 → T11 (T7 optional real-data cross-link; F50 gating for any measured comparison) |
| T7 | **Experimental: Heat Transfer Measurements** | Thermal conductivity/relaxation from real temperature measurements. | New; F50/F51 gate |
| T8 | **Experimental: Brownian Motion Tracking** | Infer diffusion coefficients from real tracked-particle trajectories. | New; F50/F51 gate |

### A3. Waves & Optics — 9 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| W1 | The Wave Equation | Finite-difference wave propagation, boundaries, convergence. | New |
| W2 | Interference and Resonance | Superposition, standing waves, modes and dispersion. | New |
| W3 | Refraction and Snell's Law | Propagation and interface effects with verified Snell relation. | New |
| W4 | Polarization and Malus's Law | Polarisation states, transmitted intensity and practical limits. | New |
| W5 | Diffraction and Imaging | Model Fraunhofer diffraction and instrument limits. | New |
| W6 | Inverse Optics | Infer unknown optical parameters from intensity data. | New |
| W9 | **Sound Waves, Resonance and Doppler Effect** | Numerical sound propagation, standing-wave modes, resonance and frequency shifts from moving sources/observers, with analytic limiting-case checks; **no audio-recording or sensor-data acquisition requirement**. | **New in revision 2**; connect to W1/W2 |
| W7 | **Experimental: Real Optical Diffraction Images** | Process measured fringe images, fit physical model, residuals/uncertainty. | **F52**, do not duplicate |
| W8 | **Experimental: Wave Flume Measurements** | Compare real tank waves with simulated wave propagation/dispersion. | New; F50 review |

### A4. Electromagnetism — 9 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| EM1 | Coulomb's Law and Electric Fields | Vector fields, superposition and potential. | New |
| EM2 | Lorentz Force and Charged Particles | Charged-particle motion in specified E/B fields. | New |
| EM3 | Faraday's Law and Induction | Time-dependent flux and induced electromotive force. | New |
| EM4 | Maxwell's Equations and FDTD | Build a transparent finite-difference electromagnetic wave solver. | New |
| EM5 | RLC Circuits and Resonance | Transient and frequency-domain circuit behavior. | New |
| EM6 | Waveguides and Electromagnetic Resonances | Modes, boundary conditions, transmission; bridge from waves and superposition to basic antenna radiation/element patterns as preparation for EM9, with limits of idealized models. | New; **enhanced in revision 3**, no extra slot |
| EM7 | **Experimental: Microwave S-Parameters** | Real VNA/Touchstone data, calibration, reflection/transmission, residuals. | **F54**, do not duplicate |
| EM8 | **Experimental: Real RLC Circuit Measurements** | Fit measured impedance/time responses with uncertainty. | New; F50/F51 gate |
| EM9 | **Applied Capstone: Adaptive Phased-Array Beam Steering** | Construct and independently check a finite-array complex field/array-factor model; electronically steer a beam to a moving receiver and place a null toward an interferer when feasible. Vary element spacing, amplitude/phase control, quantization, frequency, noise and element patterns; visualize main lobe, sidelobes, grating lobes and steering/null trade-offs; compare against analytical limits and report when the ideal array model fails. Optional full-wave element-reference comparison; **not** an assertion of a fabricated/validated 6G metasurface or a requirement for heavy EM meshing. | **New in revision 3**; EM4/EM6 plus W2 interference; EM7 optional for real RF/measurement context |

### A5. Fluid Dynamics — 10 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| FL1 | Advection and Diffusion | Schemes, boundary conditions, stability and artificial diffusion. | New |
| FL2 | Navier–Stokes Fundamentals | A contained two-dimensional incompressible-flow solver. | New |
| FL3 | Vortex Formation and Flow Around Obstacles | Vorticity, shedding and Reynolds-regime caveats. | New |
| FL4 | Shock Waves and Burgers' Equation | Nonlinear steepening, shocks and numerical dissipation. | New |
| FL5 | Shallow-Water Equations | Derive depth-averaged mass/momentum balance, water height/velocity transport and wave speed; implement/compare a small conservative numerical scheme with still-water and dam-break checks, depth positivity, boundary conditions and conservation. For the capstone sequence, teach after FL9. | New; **enhanced in revision 3**, no extra slot |
| FL6 | Particle-Based Fluid Simulation | Grid versus particle modeling with limitations. | New |
| FL9 | **Finite-Volume Methods and Conservation Laws** | Implement transparent conservative numerical fluxes for 1D Burgers or shallow-water equations; examine CFL limits, shock capturing, mass/momentum budgets, convergence and comparison with a non-conservative discretization. | **New in revision 2**; build on FL1/FL4; position **before the finite-volume implementation in FL5**, then FL10; connect to D13 |
| FL7 | **Experimental: Particle Image Velocimetry** | Real velocity fields, vortex identification and model comparison. | **F53**, do not duplicate |
| FL8 | **Experimental: Real Turbulence / Flow Measurements** | Turbulence statistics, uncertainty and limited model regimes. | New; F50/F51 gate |
| FL10 | **Applied Capstone: Reconstructing the 2025 Kamchatka Tsunami** | Build a **teaching-scale, non-operational** 2D tsunami propagation model from the shallow-water equations and conservative finite volumes; start with flat-bottom analytical/benchmark cases, then regional, source-documented ocean bathymetry and a transparent **simplified/assumed** initial sea-surface displacement. Explain open boundaries, CFL/time-step and grid convergence, mass budgets, wet/dry limitations, dispersion/Coriolis/spherical-geometry approximations and source uncertainty. Visualize wave height/travel times. If and only if F50 approves source/licence/provenance and permitted subset, compare **historical** simulated signals and qualified arrival-time/waveform results against authentic July 2025 Kamchatka DART observations; otherwise publish a clearly simulated/benchmark-only version until approval. Not for tsunami warning, inundation or quantitative hazard forecasting. | **New in revision 3**; FL1 → FL4 → FL9 → FL5 → FL10; F50/F51 before publishing real observation comparisons; no additional designated lab |

### A6. Quantum Physics — 8 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| Q1 | Schrödinger Equation | Numerical evolution of a one-dimensional wavepacket. | New |
| Q2 | Quantum Tunneling | Barrier transmission, reflection and energy dependence. | New |
| Q3 | Quantum Harmonic Oscillator | Eigenstates, energies and numerical convergence. | New |
| Q4 | Spin and Stern–Gerlach Measurements | Spin states, probabilities, and modeled apparatus assumptions. | New |
| Q5 | Quantum Entanglement | Correlations, measurement and interpretation limits; introduce Bell/CHSH inequalities and distinguish quantum predictions from local-hidden-variable bounds. | **Enhanced in revision 2**, no new slot |
| Q6 | Open Quantum Systems and Decoherence | Density matrices, decoherence and master equations. | New |
| Q7 | **Experimental: Atomic Spectroscopy** | Real spectral lines, calibration and simple line/level models. | New; F50/F51 gate |
| Q8 | **Experimental: Quantum Measurement Statistics** | Analyse genuine documented quantum measurement data, including Bell-test counts **if** a rights-cleared, methodologically suitable dataset is approved; calculate uncertainties, detector/selection caveats and a qualified statistical interpretation. | **Enhanced in revision 2**; F50 dataset suitability must be proven |

### A7. Astrophysics, Cosmology & Relativity — 10 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| AST1 | Three-Body Problem | Nonlinear gravitational dynamics, stability and initial conditions. | New |
| AST2 | Modified Gravity | Deliberately modified central-force laws, orbit diagnostics. | New |
| AST3 | Gravitational Lensing | Simplified ray/deflection models and mass inference limits. | New |
| AST10 | **Special Relativity and Spacetime** | Lorentz transformations, invariant interval, time dilation and length contraction; introduce relativistic energy/momentum and collision checks without creating a separate eighth addition. Verify low-velocity limits and reference-frame consistency. | **New in revision 2**; conceptual prerequisite for AST4 |
| AST4 | Relativistic Orbits | Post-Newtonian orbital precession with stated approximation. | New |
| AST5 | Cosmic Expansion and Redshift | Toy cosmological models and observable relations. | New |
| AST6 | Gravitational-Wave Chirp Simulation | Approximate binary inspiral waveform from a transparent model. | New; cross-link to M16/F60 |
| AST7 | Exoplanet Transit Simulation | Flux curves, geometry and transit-duration effects. | New |
| AST8 | **Experimental: Real Exoplanet Light Curves** | Real photometry, cleaning, fitting and uncertainties. | New; F50/F51 gate |
| AST9 | **Experimental: Galaxy Rotation Curves** | Real rotation curves, mass-model assumptions and caveats. | New; F50/F51 gate |

Do not publish M16/F60 again as an AST data lesson; use cross-links.

### A8. Condensed Matter & Materials Physics — 6 lessons

| Slot | Lesson | Core learning/verification objective | Provenance |
|---|---|---|---|
| MAT1 | Crystal Lattices and Phonons | Lattice dynamics and dispersion. | New |
| MAT2 | Electronic Band Structure | A transparent tight-binding model. | New |
| MAT3 | Elasticity and Deformation | Stress, strain, boundaries and a simple mechanical model. | New |
| MAT4 | Defects and Material Properties | Defect effects, diffusion and model limits. | New |
| MAT5 | **Experimental: X-Ray Diffraction Data** | Measured peaks, lattice spacing and uncertainty. | New; F50/F51 gate |
| MAT6 | **Experimental: Stress–Strain Measurements** | Real material response, elastic regime and hysteresis/uncertainty. | New; F50/F51 gate |

**Part A check:** 17 + 12 + 9 + 9 + 10 + 8 + 10 + 6 = **81** lessons, of which **16** are designated real-data labs. Existing ABM/T0 is counted once. Revision-2 added labels M17, T9, W9, FL9 and AST10; revision-3 appended T10, T11, EM9 and FL10 without renumbering the old slots. Displayed teaching order may place a newer label before an older label: **T6 → T10 → T11**, **EM4/EM6 → EM9** and **FL1 → FL4 → FL9 → FL5 → FL10**. Do not rename or reassign previously published IDs, URLs or completed feature IDs.

### 4.1 Selected applied capstones — shared learning contract (revision 3)

Only **A2/T11, A4/EM9 and A5/FL10** are newly designated engineering/scientific capstones by this revision; **T10 is a reusable FEM bridge**, not a capstone. None requires creating a new Part A course or new Part B lesson. No capstones are mandated for A1, A3, A6, A8, or newly mandated for A7. Keep optional ideas (battery thermal runaway, Formula 1 aerodynamics, JWST atmospheric retrieval) **outside the feature backlog** absent a separate planning decision.

| Capstone | Professional research/engineering question | Required verifiable deliverable | Limitation/credibility boundary |
|---|---|---|---|
| **T11 AI-accelerator thermal engineering** | Given synthetic/hypothetical multi-hotspot heat loads and package/cooling constraints, which material/geometry/cooling configuration manages peak temperature best? | 2D temperature-field figures, energy/flux checks, FEM versus simpler verified reference, mesh/sensitivity plot, trade-off table and justified recommendation | **Not** a measured/calibrated twin of real vendor hardware; no claimed real GPU operating temperatures without measured validation |
| **EM9 adaptive phased-array beam steering** | How do finite-array phase/amplitude controls form, steer and suppress electromagnetic radiation patterns? | Interactive or deterministic beam-pattern sequence, analytical steering checks, main-lobe/sidelobe/null/error measurements, failed-case discussion | Array-factor model ≠ full-wave antenna or programmable metasurface design; no implied fabricated 6G device |
| **FL10 2025 Kamchatka tsunami propagation** | How do conservation-law shallow-water models predict propagation, and where do their predictions differ from historical measurements? | Reproducible wave animation, conservative numerical diagnostics, benchmark tests and (after F50 approval) qualified DART comparison with residuals/uncertainties | Not an operational tsunami forecast; simplified earthquake source/coastline/ocean physics must be explicit; measured comparisons are gated |

Capstones are **science-first**, not marketing demonstrations: show the governing equation and assumptions; justify numerical method; document parameter values and provenance; demonstrate refinement/verification and failure modes; report performance metrics or a decision; explain which aspects are physically validated versus simply checked numerically. Produce **static deterministic preview figures** from verified scripts for Quarto, with optional interactive enhancements that degrade gracefully without JavaScript. Use small/regionally cropped meshes and bounded tests in normal CI; keep optional heavy solver or data-retrieval workflows outside routine pull-request checks. Preserve the existing **16** designated authentic-data labs and their approval gates.

## 5. Full Part B curriculum — 33 slots

These are scientific **method paths**, not four new physics-subject courses. They must retain one primary physics course per lesson, reuse the verified simulation/data environments from Part A, and keep the legacy `agents-llm` strand URLs. Where a physical context spans multiple subjects, select a justified primary course and make cross-links rather than duplicating a lesson. New method-specific strands, if needed, require an approved architecture decision.

### B1. Physics Reasoning & Scientific Agents — 9 lessons

| Slot | Lesson | Purpose and acceptance focus | Provenance |
|---|---|---|---|
| AI0 | LLM Agent Designs a Projectile Experiment | Local bounded agent works with the known projectile simulation; verified tool replay. | **Published F09**, no duplicate |
| AI1 | Agent-Assisted Physics Simulation Development | Agent implements a simulation to specification; independently checked code, units, assumptions. | **F45**; reconcile completion |
| AI2 | Scientific Code Verification and Debugging | Detect incorrect solvers, units, assumptions, test errors; validation rubric. | **F46**; reconcile completion |
| AI3 | Counterexample Hunting | Agent actively tries to falsify a numerical or physical claim. | **F16** |
| AI4 | Multi-Agent Scientific Review | Independent researcher/reviewer/critic roles, disagreements and audits. | **F18** |
| AI5 | Agent-Assisted Real Experimental Physics | Bounded agent investigates approved, genuine dataset from Part A. | **F55** |
| AI6 | Multimodal Physics Reasoning | Interpret diagrams, plots, field images and measured pictures; test object properties, spatial relations, and image-based counterfactual predictions against known physical constraints. This remains a **still-image** lesson distinct from AI8's time-dependent video. | **Enhanced in revision 2**; PhysBench-inspired evaluation |
| AI7 | Interpretable Physics Explanations and Constraints | Distinguish prediction from explanation; units, physical consistency and uncertainty. | New |
| AI8 | **Physical Reasoning from Video** | Compare (1) multimodal LLM direct observations, (2) conventional computer-vision tracking and derived velocity/acceleration, and (3) agent-assisted physics simulation/prediction for short **approved or generated** motion clips (e.g. bounce/pendulum/collisions). Assess trajectories, predictions, false causal claims, uncertainty and frame/sample-rate limitations using independent ground truth. | **New in revision 2**; build on AI6, Mechanics and EV1 |

### B2. Scientific Law Discovery — 13 lessons

| Slot | Lesson | Distinct scientific competency | Reference / continuity |
|---|---|---|---|
| D1 | Black-Box Physics: Discovering Force Laws | Discover unknown dynamics with controlled simulator probes. | NewtonBench-inspired |
| D2 | Physics Without Prior Knowledge | Systematic full/partial/no domain-prior comparisons. | PhysGym-inspired |
| D3 | Discovering Modified Physical Laws | Unlearn familiar laws and identify deliberately modified ones. | NewtonBench-inspired |
| D4 | Discovering Gravity from Experiments | Infer unknown gravitational force relation and test transfer. | GravityBench-inspired |
| D5 | DiscoverPhysics: Unknown Physical Worlds | Unknown forces, couplings, and predictive tests in controlled N-body worlds. | DiscoverPhysics-inspired |
| D6 | Inverse Physics: Parameter Discovery and Uncertainty | Estimate unknown parameters in a *known* model; explicitly test structural/practical identifiability, ambiguous solutions and parameter correlations, and quantify uncertainty on held-out observations. | **F23**, enhanced in revision 2; do not reopen a completed feature |
| D7 | Symbolic Regression for Physical Laws | Recover interpretable functional forms with non-LLM baselines. | PySR, AI-Feynman |
| D8 | Discovering Differential Equations | Infer dynamical equations from trajectories, numerical derivatives and noisy data. | PySINDy |
| D9 | Active Experimental Design | Agent chooses information-rich **simulated** experiments with an explicit budget; compare information-gain strategies and discriminate competing hypotheses against simpler baselines. No physical instrument control. | **F20**, LLM-AutoSciLab; enhanced in revision 2 |
| D10 | Scientific Discovery Under Measurement Noise | Noise, calibration, uncertainty, outliers and failure analysis. | NewtonBench, SR-Scientist |
| D11 | Hidden Forces and Unobserved Variables | Hypotheses with latent effects, observational ambiguity and disambiguating experiments. | DiscoverPhysics |
| D12 | Generalization to Unseen Physical Systems | Challenge laws on held-out settings, force models and conditions. | NewtonBench, PhysGym |
| D13 | **Discovering Conservation Laws and Physical Invariants** | Infer candidate conserved functions from trajectories in unknown systems; validate them across held-out initial conditions, separate true invariants from integration drift or coincidental correlations, and explain simple symmetry/conservation connections without assuming full equation recovery. Include a non-LLM numerical discovery baseline. | **New in revision 2**; connect to M11/M17/FL9 and D7/D8 |

Do not simply embed external benchmark assets without confirming their licences and scientific assumptions. Implement original contained teaching tasks inspired by these projects; optionally connect benchmarks later where compatible.

### B3. Physics Agent Benchmarking — 5 lessons

| Slot | Lesson | Distinct evaluation question | Reference |
|---|---|---|---|
| EV1 | Physics Reasoning Benchmarks | Can models reason about independently checked physics problems, visual/physical-tool affordances and counterfactual predictions? Separate tool-use reasoning from simply calling a software API. | PHYBench, PHYSICS-Verified, PhysToolBench; **enhanced in revision 2** |
| EV2 | Interactive Discovery Benchmarks | Can agents discover laws through controlled **simulated** experiments at full/partial/no-prior-knowledge levels under consistent protocols, budgets and held-out evaluation? | NewtonBench, PhysGym, DiscoverPhysics; **enhanced in revision 2** |
| EV3 | Agent vs Non-Agent Baselines | Does agentic tool use outperform a plain LLM, random selection or symbolic fitting? | Existing baselines + PySR/PySINDy |
| EV4 | Robustness, Cost and Sample Efficiency | Performance versus noise, experiment/tool-call budget, seeds, cost and model choice. | Reproducible evaluation harness |
| EV5 | Scientific Failure Analysis | Categorize wrong laws, leakage, numerical mistakes, hallucinations and overfit. | Independent audit/reproducible case studies |

Define dataset splits, held-out worlds, leakage prevention, versioned prompts/models, trace retention rules, determinism/replay and statistical uncertainty. Record model costs and invocation counts without live API calls in CI. Avoid claiming model comparisons are meaningful if environment or budgets differ.

### B4. Autonomous Scientific Research — 6 lessons

| Slot | Lesson | Purpose | Provenance |
|---|---|---|---|
| R1 | Automated Physics Analysis Pipelines | Parameter sweeps, numerical/experimental analysis and reproducible reports. | **F47**, reuse F51 |
| R2 | Scientific Evidence Maps | Link claims to figures, code, actual measurements and limitations. | **F19** |
| R3 | Scientific Literature and Reproducible Evidence | Curated source claims, methods, citation/provenance, reproduction feasibility. | New; extend reference register, no generic RAG product |
| R4 | Reproducing a Physics Paper with Multiple Agents | Independent agent team reproduces an open, licensed study and documents discrepancies. | **F49** |
| R5 | Agent-Driven Materials Discovery | Agents coordinate bounded, reproducible material-property simulations, compare candidate materials against explicit multi-objective physical constraints and discuss uncertainty/validation rather than treating an LLM preference as evidence. | AtomAgents / matsim-agents-inspired; **enhanced in revision 2** |
| R6 | Autonomous Physics Research Challenge | From unknown system to hypotheses, experiments, falsification and audited report. | New final capstone |

**Part B check:** 9 + 13 + 5 + 6 = **33** lessons; AI0/F09 counted once. AI8 is a distinct video-dynamics lesson; AI6 remains still-image reasoning. D13 discovers invariants instead of duplicating D7 functional-form discovery or D8 equation discovery.

## 6. Existing Lean lesson and formal verification boundaries

- **L1 — Proving What the Simulation Showed:** Preserve the published F08 lesson on a kinematic identity and explicit-Euler oscillator energy growth. This is the **one existing Lean slot counted in the 115-slot reference curriculum**.
- Preserve approved subsequent work such as F17, F21, F22 and F56, and map any already published additional Lean content to the real inventory. These are **not** requests to add a new Math course. If the updated lesson inventory makes the actual total exceed 115, report and resolve rather than deleting or hiding delivered Lean lessons.
- Where formal methods add physics insight, cross-link model properties and theorem assumptions. Never suggest Lean establishes the fidelity of the measurement or the correctness of the generated Python solver.

## 7. Shared architecture and scientifically safe reuse

Plan reusable **physics environments** (known/unknown model settings, controls, observations, units, resets, hidden-truth separation), simulation APIs, experimental-data interfaces, and independent evaluation rather than each lesson building a disconnected framework.

### 7.1 Computational physics core

- Reuse `src/pbc/` numerical models, integrators, plotting, unit/invariant checks, convergence tests, and lesson generation.
- Introduce new specialized libraries only when they improve teaching and verification and do not force a disproportionate heavyweight build. Candidate references: REBOUND for orbits, QuTiP for quantum, FEniCS/PhiFlow for fluids, and Clawpack/Dedalus as optional numerical-method comparators for conservative fluxes/spectral approaches; use independent reference outputs or optional local packages where appropriate.
- Every simulation has a documented domain of validity and an independent baseline or invariant where possible. Physical equations stay readable and teachable, not hidden in a large imported engine.
- For **T6/T10/T11**, teach **finite differences → small triangular finite elements → thermal-engineering application**. Prefer NumPy/SciPy for required deterministic code, mesh/solver reference artifacts with provenance, and **optional** local Gmsh/FEniCSx rather than a new mandatory heavyweight CI dependency. Verify temperature/heat-flux balances, known solutions, mesh/time-step convergence, boundary-condition sensitivity and units.
- For **EM9**, keep the complex finite-array model independently checkable against analytical steering/null/symmetry limiting cases; label idealized element responses, sidelobe artefacts and omitted mutual coupling. Heavy antenna-element/full-wave solvers are optional comparators, not required infrastructure.
- For FL9, expose discrete fluxes and conservation budgets directly; test stability and the appropriate CFL regime, shocks and boundary effects, and explain why numerical conservation is not identical to exact physical modeling. Reuse the resulting implementation/methods in FL5 and FL10, avoiding a second shadow CFD stack.
- For **FL10**, keep a small deterministic benchmark suite (still water, linear-wave propagation, appropriate conservation and positivity checks, boundary sensitivity) separate from optional heavier historical-data reruns. Do not claim agreement with actual 2025 observations before F50 approval, quality review and scientifically defensible comparison.
- For D13, keep the withheld physical ground truth separate from discovery agents; test candidate invariants on untouched trajectories and multiple integration settings to detect false positives.

### 7.2 Experimental data and uncertainty core

- Reuse F50 cards and go/defer/reject decisions. **A candidate dataset is not accepted because it appears in this curriculum**. All new real-data labs need a documented go decision before implementation/publication.
- Reuse F51 for readers, calibration, provenance, uncertainties, residuals, plotting, data subsets, sample rights and reproducibility.
- Required real-data loop: source/instrument and licence → authentic observations → cleaning/calibration/disclosed preprocessing → explicit physical model → side-by-side measured-vs-model plots, including uncertainty/residuals → limitations and a qualified claim.
- Do not commit restricted or excessive source data. Use small validated samples or verified documented download procedures; keep builds offline/reproducible.
- The 16 labs analyse **existing authenticated measurements**. Do not add requirements for smartphone sensors, microphones, classroom data collection or physical laboratories.
- **FL10 historical Kamchatka comparison** may use third-party authentic DART station records and bathymetry **only after** F50 records source, licence/redistribution conditions, quality/metadata, permissions, checksums and a tractable reproducible sample. A historical measurement comparison embedded in a capstone is **not automatically counted as a new designated experimental-data lab**. Clearly separate measured waveforms, processed time series, model-generated curves and assumed earthquake initial conditions; make uncertainty and limitations prominent.

### 7.3 AI/agent scientific evaluation core

- Separate an agent's **hypothesis and explanations** from the *actual simulator truth*, independent evaluation and measured evidence. The agent must not see withheld law/evaluation answers.
- Use allowlisted, bounded tools; no generated code execution in the existing runtime agent harness. Keep optional **learner-operated coding-agent exercises** distinct from the bounded on-site experiment harness, per existing ADR.
- Benchmarks need non-agent baselines, independent hold-outs, multiple seeds where required, budgets, clear scoring and visible failures, reproducible frozen traces, and no build-time/runtime dependence on hosted models or secrets.
- Prefer symbolic discovery (PySR/PySINDy or appropriately implemented baselines) where a lesson benefits, without turning PBC into a general Math + LLM platform or a neural ML framework.
- Keep resource-intensive benchmark runs outside standard PR critical-path CI. PRs must still verify deterministic reference/replay artifacts, coverage for touched shared libraries and publication integrity. Periodic/manual heavier benchmarks may enrich results but cannot be misrepresented as part of every green merge.
- **Video reasoning (AI8):** use licensed/created short clips and deterministic offline motion tracks for CI; compare the direct multimodal-LLM response, classical computer vision and physics-model/agent outputs under matched clips. Clearly distinguish generated from recorded visuals, control for ground-truth leakage, and report prediction errors, confidence and limitations. No live video feed, browser upload, hosted video processing, hidden user recordings or required build-time model calls.

## 8. Learning Path page redesign — required independent feature

**Existing page:** `https://taspinar.github.io/physics-by-construction/path/`  
**Existing foundations:** F03, F26 prerequisite graph, F27 cards/difficulty, F37 lesson metadata/course navigation, F44 visual system. The new work must be a **distinct follow-on feature** (new next available F-number allocated by the planner), rather than reopening delivered F26/F27/F37/F44 or bundling redesign into a random lesson.

### 8.1 Problem and desired experience

The current page exposes too much descriptive metadata at once and repeats long lesson cards across different views. It is insufficiently visual and will deteriorate as the catalog approaches 100+ lessons. The page should look like a modern, calm, scientific publication/laboratory rather than a wall of autogenerated technical documentation or a gamified course marketplace.

### 8.2 Required behavior and visual structure

1. **Course-first overview**: An attractive, scan-friendly overview of the eight Part A subject courses, each with concise text, topic-specific science artwork or verified mini-figure, lesson count and a clear entry point. Never advertise a planned lesson as already published; use actual catalog state for counts and available links.
2. **Collapsible subject sections**: Use native accessible HTML `<details>/<summary>` (or demonstrably equivalent semantic progressive disclosure) for the course's lesson list. Closed by default except possibly a relevant/current course; avoid requiring JavaScript to reach any lesson.
3. **Compact lesson cards**: Default view shows title, one-sentence physical question/description, difficulty, and **small representative verified thumbnail**, plus unobtrusive metadata chips for Simulation, Experimental Data and AI extensions where available.
4. **Expandable details**: More detailed outcomes, prerequisites, 'what you build', related/AI/experimental extensions, **applied-capstone classification for T11/EM9/FL10**, and reproduce links appear on expansion, rather than crowding the default overview. If using nested disclosures, ensure keyboard and screen-reader behavior is correct and complexity justified.
5. **Physics previews from verified sources**: Prefer thumbnails derived from the actual generated and verified figures of the corresponding lesson (orbital trajectory, oscillator phase curve, laser diffraction, measured-versus-model plot, velocity field, wavepacket). Generate deterministically from existing code; allow a documented fallback illustrative SVG generated by the repository. **Do not add hand-copied, decorative, stock or unverifiable images**; no external image dependency or CDN.
6. **Two complementary access paths**: Physics Courses (Part A) as default; Methods/Physics + AI (Part B) as a secondary cross-course view/filter. The same lesson has one canonical page, with metadata-driven links rather than duplicated long cards. ABM and Lean remain discoverable as methods.
7. **Filter/search enhancements**: Where beneficial, accessible filters for course, method, difficulty and publication state. JavaScript enhancements are optional; without JS all lessons and their prerequisites must still be reachable. Coordinate with self-hosted search (F41), not a new external service.
8. **Prerequisite graph**: Preserve the F26 generated SVG, linked nodes and textual accessible alternative; put it under an optional **'View dependency map'** disclosure instead of displaying a huge global graph prominently. Consider course-scoped subsets for large future curricula, generated from the same metadata.
9. **Responsive layout**: Small phones, tablets and desktop; appropriate thumbnail crop, long titles, tables and focus states. Meet WCAG 2.1 AA, contrast, keyboard controls, semantic names/roles, reduced motion and alt/figure descriptions. Preserve site design system (F44).
10. **Performance and stability**: No heavy frontend framework, no external runtime dependencies, no gratuitous animation, no unbounded DOM growth. Preserve the established payload/performance measurement method and budgets; optimize instead of silently inflating them. No broken Quarto relative links, anchors, previous/next behavior or search indexing.

### 8.3 Source-of-truth and implementation scope

- Derive course cards, methods, lesson cards, prerequisites, outcomes, difficulty and related links from **existing validated front matter** (F37) and repository-generated figures. Do not create a second manually maintained catalog.
- Extend `src/pbc/authoring/path.py` / corresponding templates, `site/path/index.qmd`, the established CSS and tests as needed. Introduce an optional verified thumbnail reference in lesson metadata **only if** required; plan its schema, validation and fallback.
- Existing published `mechanics`, `agents-llm`, `agents-abm`, `lean` URL paths and lesson IDs remain valid. New courses receive stable route rules under the course architecture change.
- In-course order, related edges and prerequisites remain scientifically meaningful even where a lesson is featured in both Part A and the method-oriented Part B view.
- Display T11, EM9 and FL10 as the **culminating application within their own physics courses** (and mark planned/unpublished accurately); make their verified generated figures primary previews and disclose the required precursor lessons. Do **not** add a ninth course, create duplicate pages or make all other physics courses adopt a capstone requirement.

### 8.4 Learning Path acceptance criteria

- With JavaScript disabled, a first-time visitor can choose a course, expand it, locate every published lesson, inspect prerequisites and follow canonical links.
- A learner can switch to the method-oriented AI path without encountering duplicate independent lesson content or missing lessons.
- The generated course/lesson counts match exactly the actual published catalog; planned lessons are visibly distinguished or omitted and not misrepresented as published.
- Existing links, saved bookmarks, graph node URLs and external references remain valid.
- Every thumbnail has proven source or a visibly conceptual fallback, appropriate alt text, no manual figure duplication, and deterministic generation.
- Keyboard/screen-reader/mobile checks pass, including course/lesson disclosures and the graph's nonvisual alternative.
- Static build, deterministic rebuild, payload budgets, internal links, prerequisite validation and search-index tests pass.
- Visually review at least one introductory course, a complex course, a measured-data lesson, an agent lesson, long titles and the small-screen layout before merging.

### 8.5 Suggested visual hierarchy

1. Page intro: “Choose a physics course” + short explanation of Construct → Measure → Discover.
2. Eight compact course panels with miniatures and publication progress (real counts).
3. Expanded course: readable small lesson rows/cards with one preview and key metadata; more detail on demand.
4. Secondary method navigation for AI discovery, experimental-data labs, ABM, and Lean.
5. Optional dependency-map disclosure at the bottom.

Keep the existing Learning Path redesign HTML concept from earlier discussions as *visual inspiration*, not as source-of-truth or a requirement to copy its static data. The generated Quarto page must remain authoritative.

## 9. Curriculum architecture migration and prior-feature mapping

Before generating new Issues, produce a **reconciliation report** with:

1. Every published lesson: repository path, actual `id`, `strand`, `course`, methods, Fxx and matching curriculum slot (if any).
2. Every existing roadmap feature relevant to curriculum: F01–F60 (and any new IDs already added), completed/open/in progress, Issue and PR state, and whether it already delivers content. The roadmap itself has some historical status statements; confirm actual source rather than assuming they remain fresh.
3. A single mapping for existing F15, F26, F27, F37, F43, F45, F46, F50–F56, F60, F16–F23, F47/F49 and F17/F21/F22, with no duplicated feature scope.
4. Proposed ADR(s) to allow **all eight subject courses** and new stable course/strand identifiers while keeping existing URLs, with a transparent transition from ADR 008. If a previous accepted decision conflicts, record and request approval; do not reinterpret silently.
5. How F15's original one-course decision will be handled without rewriting a feature whose Issue exists, and how already-published cross-method lessons (ABM and LLM) will be exposed in the new course views.
6. a count reconciliation: current published vs target 115 slots, count of truly new slots, and any extra approved Lean/content lessons not covered by the historical baseline.

**Important:** Adding eight physics courses is a real curricular decision, not simply assigning a measured lab to Mechanics to bypass course gating. Avoid dummy mechanics framings for diffraction, RF, or fluids.

## 10. Delivery plan and proposed feature slicing

The planner should create a *dependency-ordered* backlog, not giant simultaneous Issues or a single 115-lesson feature. Create Issues just in time, each independently demonstrable and verifiable, with fixed Fxx IDs assigned in the roadmap.

| Work package (descriptive placeholder only) | Deliverable | Depends on / existing reuse | Priority |
|---|---|---|---|
| Curriculum & course architecture | Requirements alignment, approved ADR, eight course registrations, stable navigation migration | F15/F37, ADR 008 | **P0** |
| Learning Path UX redesign | Course-first accordion, compact cards, verified previews, method view, accessible graph | F26/F27/F37/F44 + course architecture | **P0**; implement before bulk lessons |
| Shared figure/preview infrastructure | Deterministic thumbnails and metadata validation, no hand-maintained assets | Existing verified figures, F43 | P0/P1 |
| Experimental-data backbone | Finish/sustain F50 decisions, F51 reproducible analysis; no unapproved dataset use | F50, F51 | P0/P1 |
| Law-discovery sandbox & evaluation protocol | Black-box environments, held-out physics, reproducible baselines, replay and scores | Existing agent harness F09/F16, physics models | P1 |
| First discovery lessons | D1, D2, D3, D7 and initial EV2 comparison | Discovery sandbox + method path | P1 |
| Fundamental-physics additions | M17 rotational motion, T9 thermodynamic cycles, W9 acoustics, AST10 special relativity | Existing subject models; AST10 before AST4; M17 informs D13 | **P1** |
| Conservative numerical methods | FL9 finite-volume fluxes, CFL/stability and conserved quantities | FL1/FL4, then applied in FL5/FL10; independent reference solutions; future D13 | **P1** |
| FEM and engineering mesh foundation | T10 transition from T6 FDM heat solver to triangular FEM, sparse systems, mesh convergence and boundary conditions; optional Gmsh/FEniCSx reference | T6; NumPy/SciPy; existing science/figure infrastructure | **P1**, before T11 |
| A2 applied thermal capstone | T11 AI-accelerator thermal modelling: hypothetical package, hotspots, credible assumptions, verification, optimization and clear non-calibrated-twin labelling | T6 + T10; optional approved T7 data | **P1/P2**, after T10 |
| A4 selected phased-array capstone | EM9 phase/amplitude array-factor solver, adaptive steering/interference suppression, verifiable beam patterns and limitations | EM4/EM6 + W2; EM7 optional measurement context | **P1/P2** |
| A5 selected tsunami capstone | FL10 2025 Kamchatka scenario, conservative 2D propagation, verified bathymetry, plots and **F50-gated** authentic DART comparison | FL1 → FL4 → FL9 → FL5, F50/F51 for observed data | **P2**, after core FV/shallow water |
| Conservation-law discovery | D13 model-agnostic invariant search, baselines and held-out checks | D7/D8 + appropriate A1/A5 models; hidden truth | **P1** |
| First measured-data labs | F60, then accepted F52/F53/F54 when subject courses exist | F50/F51 + matching subject course | P1 |
| Expand subject courses | Mechanics advanced, Thermodynamics, Optics, EM, Fluid, Quantum, Astro, Materials | Course architecture, reused solvers | P1–P3 |
| Remaining discovery & benchmarking | D4–D13 (including the separately prioritised D13) and EV1–EV5, independent comparisons with physics benchmarks | Discovery sandbox, shared physics | P2 |
| Scientific agent/automation lessons | AI1–AI8 (including video reasoning) and R1–R5, reuse approved existing Fxx | AI6 + motion data/physics models for AI8; existing F45/F46/F55/F47/F49 etc. | P2 |
| Part B research capstone | R6 with controls, honest limitations and evidence trail; distinct from subject capstones T11/EM9/FL10 | B paths + sufficient A environments | P3 |

**Recommended phases (overlap allowed):**

- **Wave 0 — Governance & UX:** requirements/architecture reconciliation, lesson inventory, ADR, course structure, new Learning Path UX. Do not wait for 100 lessons to redesign navigation.
- **Wave 1 — Discovery foundation + authentic first lab:** black-box physics and benchmark infrastructure, D1/D2/D7, EV baseline, F50/F51 and approved first measured lab.
- **Wave 2 — Core subject expansion:** advanced mechanics (including rotational motion), thermodynamic cycles, waves/acoustics, **T6→T10 FDM/FEM foundation**, conservative FL1→FL4→FL9→FL5 fluid methods, A4 electromagnetic foundations, EM9 phased-array capstone when prerequisites are ready, and associated gated measured-data labs.
- **Wave 3 — Applied capstones and advanced physics:** **T11 AI-accelerator thermal capstone after T10**, **FL10 2025 Kamchatka tsunami after FL5** (historical DART comparison only after F50 approval); remaining scientific discovery (including invariant discovery), video-dynamics reasoning, agent benchmarking, Quantum, Astrophysics (including special relativity), Materials; measured labs added only when feasible.
- **Wave 4 — Research capstone + quality consolidation:** multi-agent reproduction/discovery, reproducibility audits, educational accessibility and curriculum coverage check.

Features may run in parallel when independent, but no feature can replace human dataset decisions, protected architectural approval or scientific review. Implementing the curriculum must not create an ever-growing full heavy benchmark run in each ordinary PR; design CI and verification budgets proactively.

## 11. Required quality / Definition of Done for every new lesson

Every lesson added under this change must:

1. Be physically correct at its stated level: clear research question, assumptions, derivation essentials, units and domain of validity.
2. Use runnable, pinned code or an approved verified form, and reproducible figures generated by the build; pass scientific numerical checks and relevant analytical/independent baselines.
3. Interpret what plots show, not just produce plots. Label provenance of every figure, including simulated vs measured and any processing.
4. Explain numerical, epistemic and empirical limitations honestly; support important claims with the correct evidence type. Agent model outputs alone are not proof.
5. Integrate with current front-matter source of truth: unique canonical ID, course, methods, difficulty, validated prerequisites, outcomes, related lessons and metadata for generated path.
6. Provide relevant exercises/self-check, accessible labels, alt text, figures with units and a tested “Reproduce this” path; cite curated references via the reference register (not hand-copied URLs).
7. Include focused tests appropriate to modified code, physics edge cases and scientific assertions. Avoid unnecessary duplicate expensive tests; shared library changes trigger affected regression checks.
8. Pass applicable CI/verification, independent scientific review and publication/link/payload checks. Avoid live LLM/API calls as required CI.
9. For actual data: use a **go-approved** F50 dataset with verified licence/provenance/checksum, documented preprocessing/uncertainty, small cleared sample or permitted download, and an honest measured-versus-model comparison.
10. For AI/agent work: provide bounded permissions, experiment/tool budget, source and version details, frozen replay, held-out verification, baseline comparison, and recorded failure conditions. No undisclosed model answer leakage.
11. For **T10/T11/EM9/FL10** specifically: demonstrate a physically meaningful progression from existing foundations with checked prerequisites; compare with an analytical, manufactured, independent or trusted numerical reference; show error/refinement and genuine failure modes. Capstone outputs must be genuinely generated by verified physics code and support a qualified trade-off or inference, **not** merely an impressive animation. Heavy CAD/FEM/full-wave/geophysical tools remain optional and tests must respect ordinary CI budgets.
12. For **T11**, do not claim a digital twin of a specific AI chip without vendor-authorized measurements and calibration; for **EM9**, distinguish ideal array factor from realized hardware; for **FL10**, do not publish operational hazard claims or an unapproved measured-data comparison. Establish dataset approvals before integrating remote samples into published builds.

**Curriculum completion** means that the actual lesson inventory reconciles to the approved final set with genuine published content, not placeholder cards; eight subject courses are navigable; measured labs are scientific and rights-compliant; four B paths have valid lessons; the seven revision-2 additions and four revision-3 numerical/applied additions are integrated and non-duplicative; published pages remain reproducible and accessible; and no old published resource is broken.

## 12. Explicit decisions and review questions for Project Grill / planner

These statements express the intended human decisions. Ask the user only if a real conflict or missing authority prevents safe adoption:

1. **Approved intent:** Adopt eight Part A physics-subject courses and four Part B research/method paths, with the revised reference **81 + 33 + 1 = 115** structure (nine Part A additions since the 104-slot baseline, including T10/T11/EM9/FL10, and two Part B additions). If an existing requirement says only one future course may exist, propose the minimum appropriate change to the requirements and a superseding course architecture ADR.
2. **Approved intent:** Every Part A subject eventually has **two** genuine real-data labs as a *curriculum target*, not an obligation to publish unapproved/poor datasets. F50 feasibility remains decisive.
3. **Approved intent:** Physics-Informed ML and Math as standalone subjects are excluded. Maintain existing Lean and physics-linked proof commitments.
4. **Approved intent:** Keep the site static, free, open-source and English-language; no hosted agents, accounts, analytics or hidden uploads. Do not change creator/JIDAI/copyright copy as part of this request.
5. **Planning decision required:** How to stage F15 and the eight-course expansion while respecting delivered work, accepted ADR 008 and stable identifiers/URLs. Provide a specific ADR proposal with migration/test strategy.
6. **Planning decision required:** Confirm exact current delivered lesson count and avoid duplicating late-delivered agent/Lean features. If this changes the 115 total, present a clear reconciliation rather than silently modifying published history.
7. **Planning decision required:** Establish a controlled way to show upcoming planned lessons without claiming they are live, preferably not with heavyweight placeholder lesson pages.
8. **Planning decision required:** The Learning Path redesign is an independent first-class roadmap feature, early enough to precede bulk curriculum creation, not an informal CSS tweak inside an unrelated feature.
9. **Approved intent (revision 3):** Add a foundational FEM bridge **T10** plus exactly these newly designated A2/A4/A5 applied capstones: **T11 AI Accelerator Thermal Engineering**, **EM9 Adaptive Phased-Array Beam Steering** (already selected in the preceding discussion) and **FL10 Historical 2025 Kamchatka Tsunami Propagation**. The two latest confirmed capstone choices are T11 and FL10. Do not silently convert previously discussed options into additional requirements.
10. **Planning decision required:** Confirm how the capstones are sliced into small deliverable features and how F50 will gate the historical tsunami observation data; do not require F50 to ship FL10's self-contained benchmark/simulation core. No mandatory heavyweight commercial or HPC solvers in CI.
11. **Defer:** Battery thermal runaway and Formula 1 aerodynamics (interesting optional extensions only); JWST atmospheric retrieval (discussed but not selected here); all other automatic subject capstones; nuclear/particle, plasma and geophysics/climate specialisations (11 optional slots); Physics-Informed ML. Do not generate implementation Issues for these deferred ideas as part of this change.

## 13. Planning-cycle acceptance criteria (NOT implementation acceptance)

The planning change is ready for human approval only when:

- Approved requirements, roadmap, architecture and any superseding ADRs are mutually consistent and preserve the original project mission and non-goals.
- The curriculum's **81 Part A + 33 Part B + existing Lean** slots are enumerated and counted, with delivered content mapped to them and discrepancies disclosed.
- All previous Fxx features retain IDs/history; completed/open features are not overwritten or recreated.
- New features have practical Goal, Dependencies, Acceptance criteria, Risk and scope boundaries, but are **not** all created as GitHub Issues or implemented in planning.
- F50/F51 reusable experimental foundations and old F52/F53/F54/F60/F55/F23/F20/F45/F46/F49/etc. are linked to the appropriate slots.
- The course/strand architecture supports eight physics subjects, preserves existing published links, and distinguishes primary course from cross-cutting method.
- One explicit independent Learning Path redesign feature covers accordions, verified thumbnails, compact cards, methods view, preserved graph, responsive design, accessibility and no-JS operation.
- All **seven revision-2 additions** (M17, T9, W9, FL9, AST10, AI8, D13) and **four revision-3 additions** (T10, T11, EM9, FL10) are explicit, individually testable curriculum slots; dependencies, validation and ID stability are respected.
- Seven **existing lesson enhancements** are recorded without duplicating slots: D6 identifiability; D9 hypothesis-discriminating information gain; AI6 still-image physical affordances/counterfactuals; EV1 physical-tool understanding; EV2 controlled prior-knowledge comparisons; R5 physical multi-objective constraints; and the linked Q5/Q8 Bell-inequality/eligible-data enhancement.
- Explicitly exclude new sensor-building, acoustic-recording and physical-lab-control lessons; retain all 16 existing-data labs and their F50 decisions.
- The **T6→T10→T11**, **EM4/EM6(+W2)→EM9**, and **FL1→FL4→FL9→FL5→FL10** learning sequences are preserved in the roadmap, and the A2/A4/A5 capstones are visible in the course-first Learning Path with one canonical URL each.
- Capstone plans include bounded simulations, independently checked physics, numerical refinement/limitations, and a justified decision/inference. The T11 digital-twin terminology and FL10 hazard-forecasting limitations are explicit, and historical DART data may be published **only** with F50 approval.
- No unselected A1/A3/A6/A8/A7 capstone, EV thermal-runaway lesson, F1 full-car CFD, or other hidden requirement is created.
- Phased dependencies and scientific/CI/performance risks are visible and actionable.
- `review-planning.sh` has passed after revision, and the human reviews/approves the final planning change before the planning PR is merged.

## 14. References for planning and scientific architecture

**Current project sources (inspect live `origin/main` rather than assuming this snapshot):**

- [Physics by Construction repository](https://github.com/taspinar/physics-by-construction)
- [Existing roadmap](https://github.com/taspinar/physics-by-construction/blob/main/docs/roadmap.md)
- [Existing architecture](https://github.com/taspinar/physics-by-construction/blob/main/docs/architecture.md)
- [Approved requirements](https://github.com/taspinar/physics-by-construction/blob/main/docs/PROJECT_REQUIREMENTS.md)
- [Previously approved `physics-next-phase` change](https://github.com/taspinar/physics-by-construction/blob/main/docs/changes/physics-next-phase.md)
- [Learning Path page](https://taspinar.github.io/physics-by-construction/path/)
- [Agentic Coding Template planning change workflow](https://github.com/taspinar/agentic-coding-template/blob/main/docs/development.md)

**Examples to study, not dependencies mandated for every lesson:**

- Law discovery / physics agents: [NewtonBench](https://github.com/HKUST-KnowComp/NewtonBench), [PhysGym](https://github.com/principia-ai/PhysGym), [DiscoverPhysics](https://github.com/SampsonML/DiscoverPhysics), [GravityBench](https://github.com/NolanKoblischke/GravityBench), [LLM-AutoSciLab](https://github.com/scientific-discovery/LLM-AutoSciLab).
- Symbolic discovery *as physics tools*: [PySR](https://github.com/astroautomata/PySR), [PySINDy](https://github.com/dynamicslab/pysindy), [AI-Feynman](https://github.com/SJ001/AI-Feynman).
- Scientific/agent coding and experiments: [AI-Scientist](https://github.com/SakanaAI/AI-Scientist), [AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory), [ScienceAgentBench](https://github.com/OSU-NLP-Group/ScienceAgentBench).
- Physics reference software: [REBOUND](https://github.com/hannorein/rebound), [QuTiP](https://github.com/qutip/qutip), [PhiFlow](https://github.com/tum-pbs/phiflow), [FEniCSx](https://github.com/FEniCS/dolfinx), [Clawpack](https://github.com/clawpack/clawpack), [Dedalus](https://github.com/DedalusProject/dedalus), [Gmsh](https://gmsh.info/).
- Historical tsunami candidate sources (F50 **must** verify rights, provenance, processing, station/time-window suitability before use): [NOAA DART programme](https://www.ndbc.noaa.gov/dart.shtml), [NOAA ETOPO global relief model](https://www.ncei.noaa.gov/products/etopo-global-relief-model), and reference solvers such as [GeoClaw](https://www.clawpack.org/geoclaw.html). Links are **candidates for investigation**, not automatically approved datasets or implied validation.
- A4 beam-steering capstone should begin from a derivable finite-array model, not from a 6G marketing claim or unreviewed antenna hardware datasheets.
- Image/video and physical-tool benchmarking ideas: [PhysBench](https://github.com/physical-superintelligence-lab/PhysBench), [PhysToolBench](https://github.com/PhysToolBench/PhysToolBench). References are inspiration, not a requirement to install new heavy dependencies or use third-party benchmark videos without licence checks.
- Materials agent research: [AtomAgents](https://github.com/lamm-mit/AtomAgents).

## 15. Verification that scales with the curriculum

### Why this is part of the curriculum plan

The curriculum grows from 20 lessons to about 110. Verification cost grows
with it, because every lesson is executed three times in each CI run:

| Step | What it does | Cost per lesson (measured 2026-10-12, 20 lessons) |
|---|---|---|
| Site build | Executes every lesson page | about 10 s |
| Determinism check | Builds the whole site a second time | about 10 s |
| Reproduction test | Runs the commands shown on the page in a fresh clone and compares the result byte for byte | about 21 s |
| Checks per page | Accessibility scan, no-JavaScript reading, screen widths | about 5 s |

That is about 45 s per lesson. F58 runs the checks in parallel jobs and
brings a pull request to about 12 minutes with 20 lessons. It does not
change the cost per lesson. Extrapolated to 110 lessons, the site build alone
takes about 19 minutes, and a pull request is back at 25 to 30 minutes
however many jobs run side by side.

### Requirement

The time a pull request waits for verification depends on what the pull
request changes, not on the size of the curriculum.

- A pull request that changes one lesson executes and checks that lesson,
  plus every lesson that depends on what it changed.
- A pull request that changes shared code, the locked environment, the site
  configuration, or a toolchain executes and checks every lesson.
- Every push to `main` executes and checks every lesson, so nothing is
  published that was not fully verified.
- The budget of 12 minutes for a typical pull request holds at 110 lessons.

### What has to be decided (new ADR)

Today every run proves that every lesson executes. That is an explicit
decision of the project (ADR 002, ADR 003). Reusing the result of an
unchanged lesson changes it, so it needs a decision record that settles:

1. **What "unchanged" means.** The inputs of a lesson: its source, the
   modules of `src/pbc` it imports, its dataset samples, the lock file, the
   Lean toolchain and manifest, the site configuration and shared templates.
   A lesson is unchanged only when none of these changed.
2. **Where the earlier result comes from.** For example the site that was
   built and verified for the commit on `main` that the pull request is
   based on.
3. **What stays unconditional.** At least: the full run on `main`, and a
   full run whenever the inputs cannot be determined with certainty. The
   rule fails safe: in doubt, everything runs.
4. **How the three executions per lesson reduce to fewer.** The reproduction
   test proves two things, that the commands on the page regenerate the page
   and that this takes at most 30 seconds. The time can be measured during
   the build. Whether the reproduction then still runs for every lesson on
   every pull request is part of this decision.

### Constraints

- No check is dropped. A check runs less often only where the decision
  record says so, and always on `main`.
- No check exists only in the CI workflow: the selection is made by
  `./scripts/verify.sh`, so a local run and CI select the same lessons.
- A local `./scripts/verify.sh` without options still verifies everything.
- The published site is still the site that was verified.

### Order

After F58 (it needs the parallel jobs and the single built site), and before
the first block of new lessons. Until it lands, each new lesson adds about
45 seconds of runner time to every pull request.

### Smaller points that can go with it

- The determinism check builds the whole site a second time on every pull
  request. It can follow the same selection as the build.
- The self-tests of the development workflow (about 3 minutes) run on every
  CI run, also when no workflow file changed. Locally they already run only
  when one did.

---

## Usage

Save this file anywhere readable on your computer, then from a **clean main checkout** of `physics-by-construction` run:

```bash
./scripts/start-planning.sh physics-final-curriculum \
  --change /absolute/path/to/pbc-final-curriculum-planning-change-2026-10-10.md \
  --grill
```

**Why `--grill`:** This is a product-level expansion of the approved curriculum and likely affects the prior one-extra-course requirement and the course/strand architecture, not just a new single roadmap feature. Project Grill should explicitly check whether existing requirements already authorize it and request approval only for necessary changes. Then independently review/revise planning and run `finish-planning.sh` following the repository workflow. No feature implementation or automatic merge is authorized by this document alone.
