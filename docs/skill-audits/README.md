# Audit of the candidate visual skills (F122)

The audit that ADR 019 decision 2 and the requirements' unresolved question 13
make the condition of using a third-party skill. One record per candidate;
the owner approves each outcome on Issue #215 before anything is vendored,
adapted, or dropped. The owner approved the recommendations on 2026-10-18
(the comment on the Issue); the result is in `.agents/skills/`. Nothing in this directory is a skill: these records are
read by people and by the planner, never followed as instructions.

## How the audit was made (2026-10-18)

Each upstream repository was cloned into a new, empty directory outside the
repository and the worktree, with Git hooks disabled, no submodules, and no
Git LFS download. Only its files were read. No script, package, installer,
hook, or binary of a candidate was executed, imported, or installed; what a
script would execute is recorded from reading it. Every revision is a commit
SHA.

## Record template

Each record has these fields, the fields of F122 "In scope":

1. **Upstream**: the repository, the path of the skill in it, the pinned
   commit, and the date of that commit.
2. **Files**: every file the skill directory carries, by kind, with its size,
   and the SHA-256 of the directory (the digest of the sorted per-file
   SHA-256 list, the form the skills configuration check will verify).
   A record whose skill carries more than its `SKILL.md` and licence ends
   with a section "File inventory" that lists each file, with its size,
   its Git blob, what it is, and whether it is retained or left out.
3. **Scripts**: every script and what it would execute: interpreter,
   imports, network access, files written, binaries started.
4. **Licence**: the licence of the skill and of bundled third-party content,
   and the redistribution decision.
5. **Dependencies and security assumptions**: what the skill expects to be
   installed or reachable, what it writes, and what it asks the agent to do.
6. **Compatibility**: with the Quarto, `.qmd`, CSS, SVG, native MathML,
   Python, and GitHub Pages stack, and with both runners (Claude Code for the
   writing roles, Codex read-only for the reviewing roles).
7. **Removed or adapted**: what would be left out or changed, and why.
8. **Recommended outcome**: vendored at the pinned revision, a thin
   project-owned adapter, or dropped, with the reason. The owner decides.

## Decision table

| Candidate | Upstream at the pinned commit | Licence | Scripts | Recommended outcome | Owner decision |
|---|---|---|---|---|---|
| [Anthropic Frontend Design](frontend-design.md) | `anthropics/skills` `dbd4588f` | Apache-2.0 | none | Vendor as is (two files) | Vendor as is (2026-10-18) |
| [Impeccable](impeccable.md) | `pbakaus/impeccable` `08d5b470` | Apache-2.0 | launcher that downloads and runs a native binary; 550 KB of browser JavaScript | Adapter: a project-owned `SKILL.md` in front of the vendored prose references, no script | Adapter; `reference/hooks.md` also left out (2026-10-18) |
| [Diagram Design](diagram-design.md) | `cathrynlavery/diagram-design` `550fd66e` | MIT (bundled icons MIT, CC0) | six Python scripts, one needs Playwright | Adapter that carries the general diagram principles in project words, or drop | Thin adapter (2026-10-18) |

Manim is not audited (question 15: not scheduled); FreeCAD and OpenSCAD are
not candidates.

## Found on the owner's machine

Impeccable 4.5.0 is installed and enabled as a user-level Claude Code
plugin (`~/.claude/settings.json`, `~/.claude/plugins/cache/impeccable`), and
an engine binary 0.1.11 has been downloaded to `~/.impeccable/bin/`. At the
audited revision the plugin declares hooks that run that binary at the start
of every session, after every Edit or Write, and at every stop (see
[impeccable.md](impeccable.md), "Scripts"); an enabled user-level plugin
applies in every project the owner opens, this one and its feature worktrees
included. The installed 4.5.0 was not audited. ADR 019 rejects a globally
installed skill; whether to disable the plugin is the owner's decision and
outside this repository.
