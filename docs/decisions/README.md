# Architecture Decision Records

Create ADRs only for significant architectural decisions.

Naming convention:

`NNN-short-description.md`

Examples:

- `001-rendering-approach.md`
- `002-authentication-strategy.md`
- `003-database-choice.md`

Suggested format:

```md
# ADR NNN: Decision title

## Status
Accepted

## Context
Why does this decision need to be made?

## Decision
What did we decide?

## Alternatives considered
What alternatives were considered?

## Consequences
What are the positive and negative consequences?
```
Do not create ADRs for trivial implementation details.

## Index

| ADR | Decision |
|---|---|
| [001](001-quarto-static-site-with-build-time-execution.md) | Quarto as the site generator, with build-time execution and MathML equations |
| [002](002-regenerate-artifacts-and-display-by-reference.md) | Regenerate all lesson artifacts on every build and display code by reference |
| [003](003-single-verification-entry-point-and-ci-budget.md) | One verification entry point, one verified artifact, and a fixed CI time budget |
| [004](004-agent-lessons-verified-by-replay.md) | Agent lessons run behind a provider interface with a tool allowlist and are verified by replay |
| [005](005-workflow-self-tests-run-locally-on-workflow-changes.md) | Workflow self-tests have their own file and run locally only when a workflow file changed; amends ADR 003 |
| [006](006-content-drafting-runs-on-the-maintainers-machine.md) | Agent-assisted content drafting runs on the maintainer's machine; CI holds no LLM key |
| [007](007-real-datasets-as-declared-inputs.md) | Real datasets are declared inputs behind a feasibility gate, with small committed samples under a cap and no portal access in builds; extends ADR 002 |
| [008](008-courses-and-methods-over-stable-strands.md) | Courses by subject and cross-cutting methods as metadata facets over the existing strands, whose identifiers and addresses stay |
| [009](009-external-references-outside-verification.md) | Curated external references come from a register with selection evidence; link validity is a maintenance check outside verification |
| [010](010-coding-agent-exercises-on-the-learners-machine.md) | Coding-agent exercises run only on the learner's machine under a sandbox profile; the site verifies the code, never the agent |
| [011](011-lean-exercise-stubs-outside-the-checked-library.md) | Lean exercise stubs live in `lean/Exercises/`, outside the checked library; their solutions are library modules and a check pairs them |
| [012](012-parallel-verification-jobs-behind-one-required-check.md) | Verification runs in parallel CI jobs that each run groups of the same checks, behind one required check that passes only when every job succeeded; supersedes decision 2 of ADR 003 and of ADR 005 |
| [013](013-eight-courses-and-the-reference-curriculum.md) | The eight physics courses are strands with fixed identifiers, the reference curriculum is declared data that lessons fill by slot, the method paths are a facet of the slot, and the prerequisite graph is validated as a graph while previous and next stay a reading route; supersedes decision 4 of ADR 008 |
| [014](014-verification-proportional-to-the-change.md) | A pull request executes and checks the lessons whose input digest changed against the verified result of `main`, which is restored and never committed; a page's navigation and commit are regenerated on every build and a check is reused only from a base the same check produced; `main` verifies everything, in same-machine shards that one assembly turns into the one built site, so that a full run fits the job timeout at 110 lessons; amends ADR 002 and ADR 012 and is the record ADR 003 decision 6 and ADR 012 decision 8 require |
