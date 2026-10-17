# Planning change: the scientific atelier, curriculum-grounded physics atlas, and visual agent skills

Date: 2026-10-17
Project: Physics by Construction
Type: product/design requirement change, submitted to the existing planning workflow
Status: change request; not an applied roadmap revision or authorization to activate proposed ADR 017 decisions
Reviewed baseline: `main` at `0aedaac0d4d97c13d8d9611bdc029847ffbcb40b`

## 1. Owner's chosen direction

Adopt visual proposal 1: a scientific atelier with the quality of a carefully designed scientific publication and optional interactive experiments. Warm paper-white backgrounds, nearly black text, cobalt blue and vermilion accents, elegant serif headings, readable body typography, precise monospaced annotations, thin rules and generous whitespace.

The owner selected this direction after considering five alternatives. The later physics-map concept is the direction for the atlas. Mockups are visual references, not authoritative curriculum data or scientifically validated figures.

Remove the proposed homepage section **“From a question to a working model”**. Do not replace it with a renamed three-step teaching formula. The homepage introduction, course structure and actual projects should communicate the approach.

## 2. Why a planning change

This changes more than colours: the homepage hierarchy, site navigation, course-map interaction, shared page templates and presentation of published versus planned material change. It also introduces governed visual agent skills so future visual work follows the chosen design and scientific standards rather than relying on ad hoc prompting. Reconcile the approved requirements, architecture and roadmap through the existing change cycle rather than implementing one oversized styling issue.

Use the existing planning workflow with `--grill` because requirements change. This document requests planning and review; it does not itself amend accepted ADRs. Allocate final feature IDs during reconciliation; do not reuse existing or retired IDs, and do not reopen delivered F25, F26, F44 or F64 as though they had never shipped.

## 3. Technical direction

Keep the existing Quarto site, `.qmd` lessons, Python generators, native MathML, GitHub Pages deployment and scientific verification pipeline. Implement the visual system with scoped CSS and shared templates/includes. Implement the atlas as build-generated semantic HTML plus SVG, enhanced by small dependency-free JavaScript modules.

Inspect the actual path generator and rendering pipeline before choosing file boundaries. Relevant existing surfaces include `site/index.qmd`, `site/path/index.qmd`, `site/_quarto.yml`, `site/assets/site.css`, `src/pbc/authoring`, `site/curriculum.yaml`, lesson front matter and the existing widgets.

No framework, Node bundler, new backend, authentication or hosting migration is needed for this scope. The earlier suggestion of Astro was exploratory; ADR 001's Quarto choice remains the implementation baseline. Keep equations as native MathML rather than adding KaTeX.

Prefer SVG for the map: it supports precise typography, links and scalable scientific drawings. Canvas may serve the optional animated experiment, with a static equivalent and accessible controls. Do not make a generated raster image the navigation surface.

## 4. Page architecture

### Home

1. Shared header with a small project mark, concise primary navigation and a clear start link.
2. Opening: “Build a world. See if it obeys physics.” with a double-pendulum figure and, when implemented and validated, optional controls and animation.
3. Part A and Part B introduction derived from the real course structure, with links into the atlas/index.
4. Capstone highlights grounded in current delivery state.
5. A short invitation to begin with the course.
6. Footer with attribution, source, licences and useful secondary navigation.

Do not include the rejected working-model section, fake metrics, testimonials or inferred learner progress. Autoplay is not necessary. An experiment starts paused or respects reduced-motion preferences and has play, pause and reset controls, units and sensible parameter limits.

### Course atlas at the existing path address

1. Breadcrumb, title and short explanation.
2. Switch between a physics map and the existing course index; search/filter integration where it adds value.
3. A large illustrated concept map limited to the approved curriculum.
4. A selected-concept panel containing a short explanation and canonical lesson links.
5. The complete accessible course/module/lesson index, retaining useful metadata and existing learner features.
6. Capstone links or explicitly labelled planned projects.
7. Shared footer.

Keep `/path/` and existing anchors/bookmarks valid. “The atlas” may be the display label; it does not require an address change. On mobile use a readable region selector, focused map view and ordinary list; do not shrink a desktop map until its labels become unreadable.

### Remaining templates

- Course/module openings: one relevant scientific illustration, introduction, prerequisites and compact lesson list. Reuse existing course sections where possible; add routes only when they serve a clear purpose and are included in the migration plan.
- Lessons: calm reading column, appropriate line length, table of contents, legible code and MathML, larger figures where useful, current prerequisites and previous/next navigation. Preserve section IDs, claims, calculations, results, references and experiment commands.
- Capstones: a strong project opening and spacious model/results presentation. Dark navy can frame visualizations; instructions remain readable. A new standalone interactive lab is additional functionality and must be separately scoped.
- About and supporting pages: use the same design language while preserving glossary, evidence, setup, contribution, search and licence access.
- Experiment gallery: deferred until enough real browser experiments exist. No empty gallery or links to nonexistent experiments.

## 5. The physics map: content and interaction contract

### Use the real eight-course structure

The concept preview omitted two important course areas. The implementation must include all eight approved Part A courses, not copy the six-region mockup:

1. Classical mechanics.
2. Thermodynamics and statistical physics.
3. Waves and optics.
4. Electromagnetism.
5. Fluid dynamics.
6. Quantum physics.
7. Astrophysics, cosmology, and relativity.
8. Condensed matter and materials physics.

Show the four actual Part B paths: physics reasoning and scientific agents; scientific law discovery; physics agent benchmarking; autonomous scientific research. Part B can be a connected research layer, but it must not obscure these distinctions. Preserve the Lean and method views rather than silently dropping them.

### Source of truth

Generate course/path/slot information from `site/curriculum.yaml` and publication state, titles, prerequisites and canonical URLs from current lesson metadata. Do not maintain a second hand-written lesson catalogue.

Introduce a small validated map-specific manifest only for information not already represented: concept IDs, display placement, concept-to-slot associations and curated conceptual connections. Each course/path/slot/lesson reference must resolve. Concept membership is not inferred solely from lesson titles.

Distinguish explicitly:

- **Conceptual connection:** a scientific relationship, curated with a short rationale.
- **Prerequisite:** an actual directed dependency, generated from the existing prerequisite data; do not invent prerequisites for planned lessons.
- **Capstone membership:** concepts a real project integrates, with links only when published.

Modes may show concepts or prerequisites separately to avoid a dense tangle. Course areas can have subtle boundaries and meaningful small illustrations; avoid arbitrary geography that suggests scientific relationships it cannot support.

### Published versus planned

The map may show the reference curriculum, but planned concepts/slots must be visibly labelled and distinguishable without colour alone. Published counts come from actual lessons. A planned slot is not a lesson link and must not be counted as published. Following a planned concept may reveal its planned description; it must not imply usable lesson content exists.

The chosen thermal and tsunami projects are planned, not delivered at the reviewed baseline. Highlight them as planned and use the actual roadmap descriptions. The thermal project represents a hypothetical accelerator, not measured performance of a named commercial chip. Preserve the existing EM9 phased-array capstone in the index/map; highlighting two projects does not delete the third.

### Accessible interactions

Every published lesson stays reachable without JavaScript. Use native links and disclosures, visible keyboard focus, labelled controls and a semantic textual equivalent to the map. Interactive selection, zoom and filters enhance that structure. Do not add browser storage for map controls; retain existing progress/recommendation behaviour under its existing contract.

## 6. Scientific and editorial boundaries

This is a presentation and navigation change, not a curriculum rewrite. Keep lesson text, scientific code, computed values, units, reference keys and claims intact unless a separate reviewed change explicitly changes them.

Do not impose “Observe / Predict / Build / Explain” on every lesson. F114–F116 already govern the editorial programme and deliberately avoid identical lesson narratives. Coordinate with that work without merging it into this redesign.

Distinguish interface artwork from scientific evidence. Decorative SVG can establish identity, but a diagram presented as a lesson result must follow the existing scientific generation/checking rules. Do not ship the mockups' generated equations, plots or illustrated measurements as verified science.

The homepage pendulum needs a real model, numerical validation and correspondence with the existing mechanics implementation. Avoid duplicating physics in JavaScript without a cross-language reference check. Clearly distinguish an illustrative animation from a validated interactive model until that work is complete.

## 7. Visual agent skills: adoption, enforcement, and scientific guardrails

### Purpose and scope

Adopt a small, maintained set of agent skills to help the existing planning → implementation → independent review workflow produce coherent visual design and reliable scientific illustrations. A skill is guidance and tooling, **not evidence that the resulting physics is correct**. Its use must be traceable and its output reviewed against the existing scientific and accessibility requirements.

Evaluate the following candidates before adoption; names indicate target capabilities, not an instruction to install unreviewed repository code:

| Candidate skill | Appropriate scope | Selection policy |
|---|---|---|
| Impeccable | Typography, layout, visual hierarchy and interface refinement across the atelier | Required when a feature changes a major user-facing visual surface, once approved and available |
| Anthropic Frontend Design | Shared UI elements, responsive presentation and interactive components within Quarto | Required for relevant frontend changes when approved; do not let it introduce a framework or bundled frontend toolchain |
| Diagram Design | Conceptual physics illustrations and explanatory diagrams | Required when producing or substantially changing a conceptual diagram if approved; check science and semantics independently |
| Manim | Optional mathematical/physics animations where motion genuinely clarifies a concept | Optional, evaluated in a bounded pilot; never required for ordinary lessons or the site build |
| PBC Scientific Visualization (new, project-owned) | Scientific plots, model/data comparisons, numerical experiments, errors, uncertainty, invariants | Required for new or substantially revised scientific figures, with exceptions justified in the feature plan |

Do **not** include FreeCAD or OpenSCAD in this change: parametrically modeled CAD is not an established dependency of the current atlas or lesson programme. Reconsider only if a future feature identifies a specific educational use case.

### Installation, provenance and compatibility

- Audit the exact upstream SKILL.md, any scripts, references, license, security assumptions, pinned revision and dependencies before use. Do not assume a skill is trustworthy or redistributable because it appears in a public directory.
- Use a project-local, versioned location discoverable by the actual Claude Code / agentic-coding-template invocation (for example `.claude/skills/<name>/SKILL.md` **if supported by the installed runner**). Otherwise explicitly resolve the skill path in the feature runner. Do not rely on globally installed skills on the owner's laptop or silent automatic discovery.
- Prefer thin project-owned adapters referencing approved source material when vendoring is prohibited or unsuitable. Pin the dependency and record update/review policy; do not fetch mutable instructions or run third-party installers during CI.
- Ensure feature worktrees have the same approved skill files; record skill name and version/ref in implementation evidence. Missing required skills cause a clear configuration failure or an explicitly approved alternative, not silent omission.
- Keep the existing Quarto, `.qmd`, CSS, SVG, native MathML, Python reproducibility, verified generators and GitHub Pages stack. Skill-generated suggestions must be adapted to those constraints, not used to introduce Astro, React, Node bundles, or remote runtime services.

### Project-owned Scientific Visualization Skill

Write a concise, practical `SKILL.md`, backed by representative good/bad examples and the existing authoring, accessibility and scientific-verification references. Cover:

- Which visual to use: conceptual diagram, analytic/numerical plot, experimental data plot, uncertainty/residual display, animation, or interface illustration.
- Axes, units, scales, legends, symbols, uncertainty bounds, captions, accessible palettes and colour-independent encodings.
- Comparisons of numerical, analytic and experimental results, numerical convergence, conserved quantities, error sources and stability where relevant.
- Reproducible Python generation, authoritative input data, deterministic seeds where appropriate, retained source artifacts and approved provenance.
- Explicit differentiation of decorative conceptual illustration from scientifically validated model or measurement; no invented results, equations or data in final figures.
- Accessible static equivalents for movement, reduced-motion controls, and avoiding unnecessary browser/runtime payload.

This skill supplements—not supersedes—the visual quality gate, authoring rules and scientific contracts already accepted in PBC.

### Agent workflow contract

1. **Planner:** classify each new visual deliverable (page/layout, conceptual diagram, scientific figure, animation, or none); select the applicable approved skills; define the expected artifact, scientific validation method and accessible fallback in the feature plan. Mark non-applicability explicitly when needed, without requiring every skill on every feature.
2. **Implementer:** read the chosen approved skill instructions and apply relevant guidance before implementing the artifact; link output and source in the completion evidence; explain any intentional exception. Merely listing a skill without observable output is not compliance.
3. **Independent reviewer:** assess the actual rendered desktop/mobile interface or generated scientific artifact and its sources. Verify scientific claims against independent computations/tests, accessibility and curriculum/source-of-truth constraints. Check the feature's selected skills were followed or an exception approved; do not accept an unsupported self-report.
4. **Verification:** where feasible add lightweight, targeted checks for missing references, missing artifact sources, accessible alternatives and metadata consistency. Aesthetic merit and scientific interpretation require visual/human review; do not add brittle screenshot pixel checks or full renders to every ordinary lesson change.
5. **Governance:** introduce the workflow contract through `AGENTS.md`, `docs/authoring.md`, relevant planner/implementer/reviewer instructions and feature-plan schema/templates **only where supported and needed**. Do not create an additional mandatory review agent or alter the owner approval hierarchy.

### Bounded pilots and approval

- **Atelier/Home/Atlas pilot:** use approved Impeccable and Frontend Design guidance on the end-to-end Home + Atlas + one existing lesson preview already required below. Compare real responsive layouts, legibility and accessibility against the selected design direction. The chosen mockups remain references, not data.
- **Conceptual diagram pilot:** apply Diagram Design to one existing mechanics concept and compare with a simpler verified SVG. Establish whether it adds learner value without a new heavyweight dependency.
- **Scientific figure pilot:** apply the project-owned visualization skill to one existing mechanics or numerical-integration plot, preserving verified values and commands; evaluate clarity, uncertainty and reproducibility.
- **Optional animation feasibility pilot:** evaluate Manim on a small numerical-integration or mechanics explanation only if a static figure is inadequate. Measure rendering time, dependency burden, asset size, static fallback and actual instructional value; keep it out of normal CI unless specifically justified.

For each pilot record before/after artifacts, qualitative rubric findings, build/runtime cost, known limitations and owner decision. Do not impose the standards retroactively across all existing lessons or block independent lesson features during the pilot. Expand to future lesson templates only after owner approval and coordination with F114–F116's editorial work.

### Additional acceptance criteria

- Every approved and used third-party skill has a documented upstream source, pinned revision, license decision, dependency/security assessment and maintainable local availability.
- At least one feature plan demonstrates deliberate skill selection, including an explicit reason where optional skills are not applicable.
- Implementer completion evidence and independent review identify what was changed and what rendered or generated artifact was actually evaluated.
- New scientific figures generated during the pilot retain scientific correctness, source data/code, units and accessible interpretation; visualization skill guidance cannot override tests.
- The Home/Atlas pilot visibly reflects the atelier direction but remains a Quarto/semantic HTML/SVG implementation with the published/planned safeguards of this request.
- No unapproved new framework, paid-model/API requirement, CAD engine, runtime dependency or routine CI animation rendering is introduced.
- The skill integration is reviewable in bounded feature slices, with a fallback if a third-party candidate fails quality/licensing/security review.

## 8. Proposed delivery slices

These are planning slices, not assigned feature IDs or one issue per implementation step.

| Slice | Deliverable | Dependencies |
|---|---|---|
| A | Reconcile requirements, current feature status, design specification, source references, map data contract and candidate skill audit | Current main and this change request |
| A2 | Approve/pin project-local visual skills, create the PBC visualization skill and integrate explicit selection/review guidance | A; upstream license/security/compatibility review |
| B | Shared visual foundations, typography, header/footer and a representative lesson template; pilot approved design skills | A, A2 |
| C | Complete homepage, initially using honest static scientific imagery | B |
| D | Curriculum-derived map data, reviewed concepts/connections and accessible static SVG/text atlas; pilot conceptual-diagram guidance where useful | A, A2; existing F62/F63/F64 foundations |
| E | Atlas integration, selection, filters and responsive interaction | B, D |
| F | Roll out shared design across course views, lessons and supporting pages | B and compatibility checks |
| G | Optional validated pendulum interaction and publication-ready polish; animation feasibility only if justified | C and scientific validation |
| H | Scientific figure/diagram skill pilots, independent review and owner decision on future authoring integration | A2; coordinate with F114–F116 |

First make one end-to-end preview containing Home, Atlas and a real existing lesson, using approved visual design skills and documenting the skills selected. Inspect desktop and mobile before broad rollout. Reuse current lesson previews for lesson rows; decorative map artwork is a distinct asset class, not a replacement for F63 previews. Record the prospective amendment to F64's old “only previews/no animation” product restrictions in the new approved requirements rather than ignoring it.

Do not block all lesson authoring on completion of the redesign. Shared template or metadata changes need coordination; independent lesson work can continue when the approved verification capacity and dependencies permit it.

## 9. Acceptance and verification

- Home and Atlas match the chosen atelier direction across desktop, tablet and mobile; the owner reviews a concrete rendered preview before final visual acceptance.
- The rejected homepage section is absent.
- All eight courses, four research paths, existing method views and capstones are represented accurately.
- Every published lesson is reachable with and without JavaScript; published counts and links match current metadata. Planned content is clearly differentiated.
- Every map reference resolves, prerequisite edges agree with source metadata, and conceptual edges have an explicit type and rationale.
- Existing routes, anchors, search, progress, recommendations, setup links, experiment commands and attribution/licences continue working.
- Keyboard interaction and screen-reader reading order work; respect reduced motion; retain WCAG 2.1 AA and the existing 320 CSS px reflow requirement.
- Self-host fonts and assets with licences recorded. Stay within existing payload budgets; measure the complete initial page and map enhancement. Heavy optional assets load on demand from the site's origin.
- Preserve scientific determinism and provenance. No check is weakened for a visual match.
- Run verification tiers required by current policy. Shared CSS/templates/assets and check changes may invalidate all reuse and require a full run; do not promise that the redesign qualifies as a targeted-only change.
- Use meaningful data/link/interaction regression checks and visual review, rather than brittle tests that reproduce CSS values.
- Enforce relevant approved skill selection and record rendered/verified outputs; do not mistake skill usage for a correctness guarantee.

## 10. Current state reconciliation, checked 2026-10-17

Repository files are evidence of merged implementation; GitHub issues/PRs are evidence of current tracking and review. Historical state tables in the roadmap describe their dated baseline and are not a live completion ledger.

### Curriculum

At the reviewed main commit, direct enumeration of `site/lessons/**/index.qmd` gives **32 lessons**, of which **28 fill a declared slot**. `site/curriculum.yaml` defines **115 slots: 81 Part A, 33 Part B and one Lean slot**. Thus **87 slots remain unfilled**. Four published Lean lessons sit outside that baseline; filling the reference curriculum would yield 119 published lessons if those four remain and the baseline stays unchanged.

F68, F70 and F71 shipped the recent mechanics, thermodynamics and waves expansions. Open lesson feature issues include F66 (#189), F67 (#190), F72 (#187) and F73 (#188). Many later lesson, lab, benchmark and capstone features remain roadmap items without an issue. An absent open issue does not mean the feature shipped.

### Delivered non-lesson foundations

- F62 curriculum metadata, F63 verified previews, F65 discovery foundation and protocol are present.
- F64's existing course-first Learning Path redesign is delivered; issue #167 is now closed, although the dated roadmap snapshot still describes manual checks as outstanding.
- Existing prerequisite graph, search, progress/recommendations, visual/accessibility system, glossary, evidence map, dataset framework and instructor-pack capability already exist. Extend these rather than rebuilding them independently.
- F118 audit merged in PR #182.
- F119 implementation merged in PR #191; measurement record merged in PR #199; issue #185 is now closed. The historical measurement document itself states that it does not close an issue, so use GitHub for current closure state.
- The three recorded one-lesson PRs took 14:05, 14:52 and 12:27; each changed one lesson but executed two. These satisfy the 20-minute budget and 15-minute target in those runs, not a universal timing guarantee.

### Remaining non-lesson or cross-cutting work

| Work | Current state and implication |
|---|---|
| F114 editorial voice guide, #181 | Guide exists and PR #183 merged, but the issue remains open. Do not describe the entire editorial programme as complete. |
| F115 editorial pilot | Still a roadmap feature; mechanics 01–05 pilot and owner approval remain. |
| F116 authoring/template/review integration | Follows approved F115 pilot; the existing voice guide explicitly remains a draft until this integration. |
| F117 learner experiment entry points, #202 | PR #205 is open; not merged into main at review time. Its title explicitly reserves criteria 7 and 8 for post-merge validation. Follow-ups #203 and #204 are open. |
| F120 incremental-main evidence, #196 | Evidence and owner amendments are recorded on the feature branch/issue. No open F120 PR appeared in the current open-PR list. Main is not incremental. |
| F121 incremental-main implementation | Conditional roadmap work; activation depends on accepted environment-equivalence evidence and high-risk review. |
| F113 full-run sharding, #150 | Paused, not delivered, not yet closed or superseded. Keep it as a fallback decision, not an automatic task to restart. |
| F61, #147 | Selection implementation exists, measurements are recorded, issue remains open; closure must reconcile its remaining evidence/criteria. |
| F112 curriculum completion audit, #151 | Open; can report status but cannot declare curriculum completion with 87 slots missing. |
| Deferred tooling/data issues | #8, #34, #66 and #138 remain open, plus workflow-model selection #165. Assess current applicability and priority instead of treating them as prerequisite blockers for every lesson. |
| New atelier and atlas | Not implemented; this change request adds the design/navigation work. |

### Verification gate: important current qualification

ADR 017 decisions 7 and 8 are accepted and applied through F119. Decisions 1–6 and 9 remain proposed. The owner comment on #196 dated 2026-10-16 supports incremental main in principle but requests stronger enforced environment identity, runner-equivalence evidence, chain limits, provenance, fail-closed full verification and a weekly full audit. F121 preparation is permitted; activation is not yet approved.

ADR 014's recorded interim gate permits the one build job a 60-minute timeout, 50-minute planning budget and capacity up to 45 lessons. Therefore the old roadmap sentence “no lesson starts beyond 32” is superseded by that later decision: lesson work is possible within the gate, subject to actual dependencies. Do not exceed 45 without measured and approved capacity, or a subsequently accepted strategy. F117 adds work to verification, so review its post-merge measurement before consuming the remaining capacity.

## 11. Suggested order alongside the redesign

1. Finish F117's review and required post-merge evidence; retain its follow-ups explicitly.
2. Reconcile F114 tracking and proceed through the F115 pilot and F116 integration.
3. Continue the runner-equivalence evidence and owner decision for F120/F121; keep F113 paused unless explicitly resumed.
4. Audit and integrate approved visual skills first, then implement atelier/atlas in bounded slices with evidence-based visual review, coordinating shared-template changes.
5. Continue eligible lesson features within the measured interim capacity. Reassess before 45 lessons; do not wait until the next lesson would exceed the limit.
6. Use F112 for honest completion reporting and perform final curriculum acceptance only when the slots and checks actually support it.

This is a scheduling recommendation, not a declaration that all infrastructure must finish before any lesson can proceed.

## 12. How to apply this request

Save this file outside the repository or supply its actual downloaded path. From the local PBC repository, use:

```bash
./scripts/start-planning.sh scientific-atelier-atlas \
  --change /absolute/path/to/pbc-atelier-atlas-planning-change.md \
  --grill
```

Replace the placeholder with the real path. The script copies the request into `docs/changes/scientific-atelier-atlas.md` and starts a change cycle. Let that workflow reconcile current main, changed requirements, roadmap features, dependencies and any needed ADR amendment. Do not run a second competing planning cycle over overlapping shared files without reconciliation.

## 13. Evidence links

- [Roadmap at reviewed commit](https://github.com/taspinar/physics-by-construction/blob/0aedaac0d4d97c13d8d9611bdc029847ffbcb40b/docs/roadmap.md)
- [Reference curriculum](https://github.com/taspinar/physics-by-construction/blob/0aedaac0d4d97c13d8d9611bdc029847ffbcb40b/site/curriculum.yaml)
- [Architecture](https://github.com/taspinar/physics-by-construction/blob/0aedaac0d4d97c13d8d9611bdc029847ffbcb40b/docs/architecture.md)
- [ADR 001: Quarto](https://github.com/taspinar/physics-by-construction/blob/main/docs/decisions/001-quarto-static-site-with-build-time-execution.md)
- [ADR 014 and interim gate](https://github.com/taspinar/physics-by-construction/blob/main/docs/decisions/014-verification-proportional-to-the-change.md)
- [ADR 017](https://github.com/taspinar/physics-by-construction/blob/main/docs/decisions/017-incremental-main-from-a-chain-of-verified-bases.md)
- [F64 #167](https://github.com/taspinar/physics-by-construction/issues/167), [F114 #181](https://github.com/taspinar/physics-by-construction/issues/181), [F119 #185](https://github.com/taspinar/physics-by-construction/issues/185)
- [F117 #202](https://github.com/taspinar/physics-by-construction/issues/202), [open PR #205](https://github.com/taspinar/physics-by-construction/pull/205)
- [F120 #196 and owner amendments](https://github.com/taspinar/physics-by-construction/issues/196)
- [F61 #147](https://github.com/taspinar/physics-by-construction/issues/147), [paused F113 #150](https://github.com/taspinar/physics-by-construction/issues/150), [F112 #151](https://github.com/taspinar/physics-by-construction/issues/151)
- [Measured verification results](https://github.com/taspinar/physics-by-construction/blob/0aedaac0d4d97c13d8d9611bdc029847ffbcb40b/docs/release-readiness.md#f119-measurements-after-the-merge)

All status claims are a dated snapshot and must be refreshed by the planner before implementation.
