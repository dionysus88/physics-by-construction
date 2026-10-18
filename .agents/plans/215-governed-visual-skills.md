# Plan: F122, governed visual agent skills (Issue #215)

Implements ADR 019 (decisions 1 to 5; decision 6, the pilots, is F123 to
F129). Source: Issue #215 (the authority on what is delivered) and the
owner's decision of 2026-10-18 on it; ADR 006, ADR 010, ADR 012 decision 2,
ADR 017 decision 7, ADR 018 decision 6; invariant I32 of
`docs/architecture.md`. Risk: High (the owner approves the diff before
merge, criterion 7).

Visual deliverables and skills: none; this feature produces no visual
artifact, it produces the skills and the contract.

Skills: none (no visual deliverable)

## Current state (inspected at e4c2727)

- `.agents/skills/` does not exist; no plan, prompt, or check names a skill.
  The audit of the three candidates is in `docs/skill-audits/` (written
  first, owner instruction 2026-10-18), and the owner approved each outcome
  on the Issue the same day: Frontend Design vendored as is; Impeccable as a
  project-owned `SKILL.md` in front of its unmodified `reference/` files;
  Diagram Design as a thin adapter in project words.
- The workflow starts its roles with `agent_run` of `scripts/lib/agent.sh`
  in three profiles. From `.agents/agents.conf` and the callers: the
  planning roles (project-grill, project-planner) run `claude` write; the
  implementer and the triage implementer `claude` write or unattended; the
  triage `claude` read-only; the planning reviewer and the reviewer `codex`
  read-only. `--agent` allows the other provider for any role, so all six
  provider and profile pairs are possible.
- `scripts/`, `AGENTS.md`, `.agents/prompts`, `docs/development.md`,
  `docs/evaluation.md`, and `docs/project-map.md` are template-owned
  (`.agents/template.conf`); `scripts/sync-template.sh` merges a project
  change to such a file with the template's, so a change survives a sync,
  and the plan records it below for carrying to the template.
- `./scripts/check-docs.sh` (docs-references) checks backticked `.md`
  paths in every tracked Markdown file: a document outside `.agents/skills/`
  that names a skill file literally would fail with the directory absent
  (criterion 6), so those documents name the directory, or a skill file with
  the placeholder `<name>`.
- `scripts/verify.conf` is a file of the check identity: changing it makes
  the targeted run report that CI will run everything, so the last
  verification of this feature is the full `./scripts/verify.sh`.

## Decisions of this plan

1. **Layout.** `.agents/skills/<name>/SKILL.md` with its supporting files
   and `PROVENANCE.yaml`; the README of `.agents/skills/` is the set and the
   policy. Names: `frontend-design`, `impeccable`, `diagram-design`,
   `pbc-scientific-visualization`.
2. **Provenance record** (`PROVENANCE.yaml`), fields: `name`, `kind`
   (`vendored`, `adapter`, `project`), `upstream` (repository URL and path;
   `project` for the project-owned skill), `revision` (the upstream commit,
   40 hex; `none` for `project`), `licence`, `redistribution`, `audit` (the
   record under `docs/skill-audits/`; not for `project`), `assessment`
   (scripts and what they would execute, dependencies, what was removed or
   adapted), `source_material` (adapters: what of the upstream they carry or
   reference), `reviewed` (date), `update_policy`, `digest`.
3. **Digest**: SHA-256 of the lines `<sha256 of the file>  ./<path>`, one
   per file of the skill directory except `PROVENANCE.yaml`, sorted by path,
   each ending in a newline: what
   `find . -type f ! -name PROVENANCE.yaml -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 | shasum -a 256`
   prints in the directory, the form the audit used.
4. **How a plan names skills**: a line `Skills: <name>[@<revision>], ...`
   per visual deliverable, or `Skills: none (<reason>)`. A revision is a
   prefix of at least seven hex digits of the recorded `revision` or
   `digest`.
5. **The check** is `python -m pbc.skills` (`src/pbc/skills.py`), entry
   `skills-config` of `scripts/verify.conf` without a group (as
   `dataset-checks`): no new script under `scripts/`, the tests in
   `tests/unit`, which the targeted run executes. It fails, naming the
   skill, when the README lists a skill without a directory or a directory
   is not listed; a directory has no `SKILL.md`, a `SKILL.md` whose front
   matter names another skill, a symbolic link, or no or an incomplete
   provenance record; the digest does not match; or a plan under
   `.agents/plans/` names a skill that does not exist or at another
   revision. It reads the files as data, never as instructions.
6. **Discovery** is demonstrated per provider and profile with the flags of
   `agent_run`, from this worktree, and recorded in the README of
   `.agents/skills/`; whatever is discovered, the role instructions name the
   files to read by path (`.agents/skills/<name>/SKILL.md` for each skill the
   plan selects).
7. **Boundary test** `tests/unit/test_skills_boundary.py`: no script,
   workflow, check entry, site source, Python source except `pbc.skills`, or
   dependency manifest names `.agents/skills` or a skill installer; exactly
   one check of `verify.conf` runs `pbc.skills`, without a group; and the
   structural checks of the group `default` pass on a scratch copy of the
   tracked files without `.agents/skills/`. The build and every other
   check are demonstrated once by a full `./scripts/verify.sh` with the
   directory removed from the worktree, in which only `skills-config` may
   fail, and recorded in the completion record (too slow for a test).

## Steps

1. The plan (this file). The audit records' owner decision recorded.
2. `.agents/skills/frontend-design/`: `SKILL.md` and `LICENSE.txt` byte for
   byte at `dbd4588f`; provenance.
3. `.agents/skills/impeccable/`: the project-owned `SKILL.md`; `reference/`
   and `reference/degraded/` byte for byte at `08d5b470`; `LICENSE` and
   `NOTICE.md` of the repository; no `scripts/`; provenance.
4. `.agents/skills/diagram-design/`: the adapter `SKILL.md` in project
   words with the MIT notice in `LICENSE`; nothing of the upstream copied;
   provenance.
5. `SKILL.md` of `.agents/skills/pbc-scientific-visualization/` with the topics of
   the Issue and examples traced to the lessons named there; provenance.
6. The README of `.agents/skills/`: the set, the selection policy, plan,
   completion, and review, moving a pin, the discovery matrix.
7. `src/pbc/skills.py`, `skills-config` in `verify.conf`,
   `tests/unit/test_skills_config.py` (a test per failure case and a pass on
   the repository).
8. The contract: `AGENTS.md` (short section), `docs/authoring.md`
   ("Visual deliverables and skills"), one line each in
   `.agents/prompts/planner.md`, `implementer.md`, `reviewer.md`;
   `docs/architecture.md` current state; `docs/development.md` lists the
   check where the checks are described.
9. `tests/unit/test_skills_boundary.py`; the full run without the directory.
10. Discovery demonstration (step 6 records it).
11. Full `./scripts/verify.sh`, last.

## Template-synced files changed

Carry these to the template repository, or keep them through the merge of
`sync-template.sh`: `AGENTS.md`, `.agents/prompts/planner.md`,
`.agents/prompts/implementer.md`, `.agents/prompts/reviewer.md`,
`scripts/verify.conf`, `docs/development.md`. Project-only: `.agents/skills/`, `docs/skill-audits/`,
`src/pbc/skills.py`, the pytest tests (with `skills-config` added to the
list of checks in `tests/integration/test_site_check_division.py`),
`docs/authoring.md`,
`docs/architecture.md`.

## Verification

Unit tests of the check and the boundary; `./scripts/check-docs.sh`; the
full `./scripts/verify.sh` (a check-identity file changed).

## Open questions

None. The user-level Impeccable plugin on the owner's machine is the
owner's matter (Issue comment of 2026-10-18).
