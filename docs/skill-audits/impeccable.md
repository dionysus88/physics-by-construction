# Audit: Impeccable

Audited 2026-10-18 for F122 (Issue #215). Owner decision (2026-10-18, on the
Issue): the adapter recommended below, with no scripts, launcher, binary,
hooks, or live mode. In carrying it out, `reference/hooks.md` was left out as
well: it is the playbook that installs the hook into the runners'
configuration, and it names hook files of other runners as if they were
files of the project.

## 1. Upstream

- Repository: <https://github.com/pbakaus/impeccable> (Paul Bakaus).
- The distributed skill is `pbakaus/impeccable/plugin/skills/impeccable/`,
  generated from `pbakaus/impeccable/skill/` (`SKILL.src.md`) by the
  project's build; the generated copy is the one an agent reads and the one
  audited. Skill version 4.6.0 (front matter), engine launcher 0.1.15.
- Pinned commit: `08d5b470495d242ca0470f4aeae1956c3a074f83` (2026-10-17), the
  head of `main` when cloned. The skill directory's own last change is
  `b7cac88a2e614e977cc6bcc89564d4af64323016` (2026-10-16).
- The repository also carries a Rust engine (`crates/`, `Cargo.toml`), a CLI,
  browser and editor extensions, and plugin manifests for several runners;
  none of that is part of what an agent reads, and none of it is audited.

## 2. Files

57 files, directory digest
`0d82b2c282b8c0d3df0f3123ae33d396073879a9c73f054052a64f22ee5adfc9`:

- `SKILL.md` (87 lines, 12 KB): setup, design principles, modes, a table of
  24 commands each with its reference file.
- `reference/` (45 Markdown files, 516 KB): one playbook per command
  (shape, critique, audit, polish, typeset, layout, colorize, animate,
  adapt, harden, clarify, optimize, …), `craft-floor.md` (the quality floor
  and bans), `new-work.md`, `operate.md`, native iOS and Android references,
  and `reference/degraded/`, four subagent briefs used when subagents are
  unavailable.
- `scripts/` (11 files, 1.7 MB): the launcher `impeccable` (POSIX shell) and
  `impeccable.cmd` (Windows), `VERSION`, `command-metadata.json`,
  the font index `font-index.json` and `font-index-failures.json` in `data/`
  of the skill's `scripts/`,
  `live-browser.js` (548 KB, bundled), `live-browser-dom.js`,
  `live-browser-ignores.js`, `live-browser-session.js`, and
  `modern-screenshot.umd.js` (a third-party screenshot library, minified).

The repository's `plugin/` also declares four subagents (`plugin/agents/`)
and three hooks (`plugin/hooks/hooks.json`), installed with the plugin.

Section 9 lists every file with its disposition.

## 3. Scripts

- **The launcher** (`scripts/impeccable`), which `SKILL.md` "Setup" step 1
  tells the agent to run once per session (`impeccable context`), and which
  33 of the 46 reference files call with other verbs. It execs a native
  binary, in this order: `$IMPECCABLE_BIN`; `scripts/bin/<os>-<arch>/impeccable`
  next to it (absent in the repository); a version-pinned cache in
  `~/.impeccable/bin/<version>/`; `~/.impeccable/bin/impeccable`; or
  `impeccable` on `PATH`. When none is found it **downloads the binary** from
  `https://github.com/pbakaus/impeccable/releases/download/` (overridable by
  `$IMPECCABLE_DOWNLOAD_BASE`) with `curl` or `wget` into `~/.impeccable`,
  verifies it against a `.sha256` sidecar fetched from the same place, and
  executes it. The checksum comes from the same origin as the binary, so it
  guards against a broken download, not against a changed release. The
  binary's behaviour is not visible in the skill.
- **The hooks** of the plugin run the same launcher with `hook` at session
  start, after every Edit or Write, and at stop (timeout 30 s): a design
  detector that runs on every edit of every project where the plugin is
  enabled.
- **The live mode** (`live`, `generate`, `live-setup.md`) starts a local
  server on port 8400, injects a script into the project's pages, and may
  patch the project's Content Security Policy configuration; the
  `live-browser*.js` files are what it injects.
- **Other verbs** write to the project: `init` writes `PRODUCT.md`,
  `document` writes `DESIGN.md` and a sidecar, the launcher keeps state in
  `.impeccable/` of the project, `pin` creates slash commands, and
  `doctor.md` recommends `npx impeccable update`.

## 4. Licence

Apache License 2.0 (`LICENSE` at the repository root; `SKILL.md` front matter
"Apache 2.0"). `NOTICE.md` records that `reference/ios.md` and
`reference/android.md` are distilled from ehmo's `platform-design-skills`
(MIT). Redistribution of the prose with the licence and the notice is
allowed; a modified copy must say that it was modified. The skill credits
Anthropic's frontend-design skill as its origin.

## 5. Dependencies and security assumptions

- Assumes it may download and execute a native binary at run time, and run
  it from hooks on every edit: **contrary to ADR 019 decision 3** (no
  instructions or tooling fetched at run time, nothing installed outside
  the audit) and to the owner's rule for this Issue.
- Assumes a writable home directory, network access, and a dev server it can
  instrument.
- Assumes it may write `PRODUCT.md`, `DESIGN.md`, and `.impeccable/` at the
  project root and edit build configuration (CSP) for the live mode.
- `SKILL.md` has an explicit fallback, "Launcher unavailable": the agent says
  that context loading did not run, reads the existing `PRODUCT.md` and
  `DESIGN.md`, and continues with steps 2 and 3. The design guidance itself
  (the modes, `craft-floor.md`, the command playbooks) is usable without the
  binary.

## 6. Compatibility

- **Stack:** the guidance is CSS and HTML and fits Quarto, SCSS, SVG, and
  GitHub Pages; much of it is aimed at application UI (React, Next.js,
  Svelte, native mobile) and does not apply. The "Read" mode (documentation,
  articles, guides) is the one that matches lesson pages, "Persuade" the
  home page. The live mode assumes a JavaScript dev server and does not fit
  `quarto preview`.
- **Project documents:** `PRODUCT.md` and `DESIGN.md` at the root would
  duplicate the design specification of F123 and `docs/authoring.md`; in
  this project the specification is the design authority.
- **Runners:** the launcher needs a shell and network; the reviewing roles
  run read-only (Codex), so a reviewer cannot run it anyway. The prose reads
  the same in both runners. `SKILL.md` references `${CLAUDE_SKILL_DIR}`, a
  Claude Code variable.

## 7. Removed or adapted

- Removed: all of `scripts/` (the launcher, the browser bundles, the
  screenshot library, the font index); the plugin's hooks and subagent
  manifests (never part of a project copy).
- Excluded commands: `live`, `generate` (they need the scripts and modify
  the project's pages and CSP), `hooks`, `pin`, `doctor` (they manage the
  binary and the user's runner), and `init` and `document` as writers of
  root `PRODUCT.md` and `DESIGN.md` (the specification of F123 takes their
  place).
- Kept: `reference/*.md` (except `reference/hooks.md`, see above) and
  `reference/degraded/*.md`, unmodified, at the
  pin.

## 8. Recommended outcome

**Adapter.** A project-owned `SKILL.md` in `.agents/skills/impeccable/` that
states what of Impeccable applies here (the modes "Read" and "Persuade",
`craft-floor.md`, and the playbooks shape, critique, audit, polish, typeset,
layout, colorize, animate, adapt, clarify, distill, quieter, harden), names
the design specification and `docs/authoring.md` as the brief, forbids the
launcher, and lists the excluded commands; beside it the unmodified
`reference/` files of the pinned commit with `LICENSE` and `NOTICE.md`, and
the provenance record. The upstream `SKILL.md` is not used as the entry
point, because its first step runs the launcher and an agent would try to
download the binary before falling back.

Alternatives for the owner: vendor the upstream `SKILL.md` and `reference/`
unmodified without `scripts/` and rely on its "Launcher unavailable"
fallback (simpler, but every session starts with a failed command, and an
agent with network access and a home directory could find a cached binary,
as on the owner's machine); or drop Impeccable and rely on Frontend Design
alone, from which Impeccable is derived.

## 9. File inventory

Every file of the skill directory `plugin/skills/impeccable/` at the pinned
commit (57), and the two repository-root files the adapter carries,
enumerated from the pinned tree (read 2026-10-18 with a shallow fetch of the
commit into an empty directory; nothing executed). Paths are relative to the
skill directory, except `LICENSE` and `NOTICE.md` (repository root). "Git
blob" is the first twelve hex digits of the file's Git object id at the pin.
Each retained file was compared with its blob and is byte-identical; the
digest of `PROVENANCE.yaml` covers the copies.

| File | Bytes | Git blob | What it is | Disposition |
|---|---:|---|---|---|
| LICENSE | 10766 | bb3f6d23b1f8 | Apache License 2.0 of the repository root | Retained unmodified as `LICENSE` |
| NOTICE.md | 503 | 0468271c904a | Notice of the MIT source of `ios.md` and `android.md` | Retained unmodified as `NOTICE.md` |
| SKILL.md | 11937 | 64869d953e0f | Upstream entry point: setup (runs the launcher), principles, modes, the command table | Excluded (not copied): replaced by the project's `SKILL.md`; its first step runs the launcher |
| reference/adapt.md | 11313 | cabc0fde5334 | Playbook: adapt a web design to another screen size or context | Retained, applies (named in the project's `SKILL.md`) |
| reference/adapt.native.md | 3910 | 877871aa0314 | Playbook: adapt a native iOS or Android design | Retained unmodified, not used: native platform |
| reference/android.md | 4093 | 1f67a6bb5749 | Native Android platform rules (MIT source, `NOTICE.md`) | Retained unmodified, not used: native platform |
| reference/animate.md | 5236 | 4ae4cc5fcd7a | Playbook: motion | Retained, applies (named in the project's `SKILL.md`) |
| reference/audit.md | 9243 | 896ac8c61cc2 | Playbook: technical quality audit of a web surface | Retained, applies (named in the project's `SKILL.md`) |
| reference/audit.native.md | 8326 | 2f5ac5143c99 | Playbook: technical audit of a native app | Retained unmodified, not used: native platform |
| reference/bolder.md | 3497 | d90e62d0d90f | Playbook: amplify an existing design | Retained unmodified, not used: unless a plan asks for it |
| reference/clarify.md | 4590 | 3047a9d82b9c | Playbook: interface copy | Retained, applies (named in the project's `SKILL.md`) |
| reference/colorize.md | 4537 | dc45f88c5f81 | Playbook: colour | Retained, applies (named in the project's `SKILL.md`) |
| reference/component-review.md | 7954 | 16af0335b57a | Checkpoint of comp-led builds; runs launcher verbs | Retained unmodified, not named by the project's `SKILL.md`; its launcher steps are forbidden there |
| reference/craft-floor.md | 4486 | 64a195eba65a | The quality floor and bans, read before building | Retained, applies (named in the project's `SKILL.md`) |
| reference/craft.md | 555 | dbbc9402c07c | Deprecated alias note for new visual work | Retained unmodified, not named by the project's `SKILL.md` |
| reference/critique.md | 45587 | 2e00cbf02255 | Playbook: design critique (design review plus detector evidence) | Retained, applies (named in the project's `SKILL.md`) |
| reference/degraded/asset-producer.md | 8401 | 216dc91fc18b | Inline brief of the upstream asset-producer subagent | Retained unmodified, not used: subagent brief of the upstream workflow |
| reference/degraded/documenter.md | 3325 | e9dfb799bcec | Inline brief of the upstream documenter subagent | Retained unmodified, not used: subagent brief of the upstream workflow |
| reference/degraded/finish-reviewer.md | 15803 | 06f257d4a97e | Inline brief of the upstream finish-reviewer subagent | Retained unmodified, not used: subagent brief of the upstream workflow |
| reference/degraded/manual-edit-applier.md | 7196 | ef5095b92462 | Inline brief of the upstream live-edit applier subagent | Retained unmodified, not used: subagent brief of the upstream workflow |
| reference/delight.md | 3716 | 798c43a5b735 | Playbook: memorable moments | Retained unmodified, not used: unless a plan asks for it |
| reference/distill.md | 5579 | 6943c965b648 | Playbook: remove complexity | Retained, applies (named in the project's `SKILL.md`) |
| reference/doctor.md | 5549 | d21b8c452a75 | Maintenance: repair drift of Impeccable artifacts, recommends `npx impeccable update` | Retained unmodified, not used: needs the launcher, changes the runner |
| reference/document.md | 27454 | b5e50d5ed1de | Writes `DESIGN.md` at the project root | Retained unmodified, not used: writes `DESIGN.md` |
| reference/extract.md | 3337 | 4c6255cf2430 | Playbook: extract reusable components and tokens | Retained unmodified, not named by the project's `SKILL.md` |
| reference/generate.md | 13110 | c1744f34793f | Fast lane into live mode (variants in the browser) | Retained unmodified, not used: live mode, needs the launcher |
| reference/harden.md | 9305 | 426b2d586a0d | Playbook: edge cases, errors, empty states | Retained, applies (named in the project's `SKILL.md`) |
| reference/hooks.md | 14017 | a65a6bc85cc3 | Installs and manages the design-detector hook in the runners' configuration | Excluded (not copied): installs a hook; nothing kept links to it |
| reference/init.md | 11697 | d1b8f01cad65 | Writes `PRODUCT.md` | Retained unmodified, not used: writes `PRODUCT.md` |
| reference/ios.md | 3812 | c6244dfe3217 | Native iOS platform rules (MIT source, `NOTICE.md`) | Retained unmodified, not used: native platform |
| reference/layout.md | 5154 | 7c13be125c64 | Playbook: spacing, rhythm, hierarchy | Retained, applies (named in the project's `SKILL.md`) |
| reference/live-setup.md | 8179 | 816b34ada4c7 | One-time live-mode configuration under `.impeccable/live/` | Retained unmodified, not used: live mode, needs the launcher |
| reference/live.md | 36449 | ed02659a8398 | Live variant mode: dev-server injection and hot swap | Retained unmodified, not used: live mode, needs the launcher |
| reference/mode-operate.md | 4716 | 833775ba85f0 | Mode rules: Operate | Retained unmodified, not named by the project's `SKILL.md`; the project limits Operate to widget interfaces |
| reference/mode-persuade.md | 3638 | 9c152d67064f | Mode rules: Persuade and Experience | Retained, applies (named in the project's `SKILL.md`); Persuade only |
| reference/mode-read.md | 4396 | b30c4c9139e3 | Mode rules: Read | Retained, applies (named in the project's `SKILL.md`) |
| reference/new-work.md | 62320 | 960b7dcfb12e | Flow for a new surface or visual identity | Retained, applies (named in the project's `SKILL.md`) |
| reference/onboard.md | 7688 | 464ae5516e26 | Playbook: onboarding to first value | Retained unmodified, not named by the project's `SKILL.md` |
| reference/operate.md | 4145 | 524f2c3ae9fa | Operate mode depth and Read notes | Retained, applies (named in the project's `SKILL.md`); widget interfaces only |
| reference/optimize.md | 7594 | 5c55a1642876 | Playbook: performance | Retained unmodified, not named by the project's `SKILL.md` |
| reference/overdrive.md | 9010 | 01a1cb131f7b | Playbook: technically ambitious effects | Retained unmodified, not used: unless a plan asks for it |
| reference/polish.md | 6632 | ea300b399724 | Playbook: final refinement pass | Retained, applies (named in the project's `SKILL.md`) |
| reference/quieter.md | 4951 | bcd4f8a6948f | Playbook: reduce visual intensity | Retained, applies (named in the project's `SKILL.md`) |
| reference/region-map.md | 3340 | 277508938ce9 | Region map of an approved comp; runs launcher verbs | Retained unmodified, not named by the project's `SKILL.md`; its launcher steps are forbidden there |
| reference/routing.md | 3322 | 9ccd9d59e293 | Command menu and routing of a bare invocation | Retained unmodified, not named by the project's `SKILL.md` |
| reference/shape.md | 3547 | 90a74ae81333 | Playbook: discovery interview and design brief | Retained, applies (named in the project's `SKILL.md`) |
| reference/typeset.md | 5249 | 60a5029d7a00 | Playbook: typography | Retained, applies (named in the project's `SKILL.md`) |
| reference/visualize.md | 13911 | 731165e7453f | Direction comps and image-generated assets | Retained unmodified, not named by the project's `SKILL.md` |
| scripts/VERSION | 7 | c34958a4711d | Launcher version (0.1.15) | Excluded (not copied): scripts |
| scripts/command-metadata.json | 8392 | 89891ea4df17 | Command metadata read by the launcher | Excluded (not copied): scripts |
| scripts/data/font-index-failures.json | 2437 | 1aca67220413 | Font index build failures | Excluded (not copied): scripts |
| scripts/data/font-index.json | 1100013 | 9d2029971df2 | Font index used by launcher verbs | Excluded (not copied): scripts |
| scripts/impeccable | 8514 | eb60f8667dd6 | POSIX launcher: finds, or downloads and verifies, then execs the native binary | Excluded (not copied): downloads and executes a binary (ADR 019 decision 3) |
| scripts/impeccable.cmd | 9306 | 789a96f4cc9d | Windows launcher, same behaviour | Excluded (not copied): downloads and executes a binary |
| scripts/live-browser-dom.js | 10623 | 8646944982fc | Live mode: DOM helpers injected into pages | Excluded (not copied): live mode |
| scripts/live-browser-ignores.js | 10346 | 1c8514c7bcd8 | Live mode: ignore rules of the injected script | Excluded (not copied): live mode |
| scripts/live-browser-session.js | 4346 | ad9cdf008fdb | Live mode: session of the injected script | Excluded (not copied): live mode |
| scripts/live-browser.js | 548692 | f706898e45de | Live mode: bundled script injected into pages | Excluded (not copied): live mode |
| scripts/modern-screenshot.umd.js | 29290 | a9c5208f6b14 | Third-party screenshot library, minified | Excluded (not copied): live mode |
