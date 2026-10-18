---
name: impeccable
description: "Physics by Construction adapter of Impeccable (pbakaus/impeccable at 08d5b470): typography, layout, hierarchy, colour, motion, and refinement guidance for a major user-facing visual surface of the site (the home, the atlas, a lesson page's frame). Prose only; it runs no command. Use when a feature plan selects it."
license: "Project-owned adapter; the files under reference/ are Apache-2.0, see LICENSE and NOTICE.md"
---

# Impeccable, adapted for Physics by Construction

This file is the project's own entry point to Impeccable. The files under
`reference/` are the upstream playbooks, byte for byte at
`pbakaus/impeccable@08d5b470495d242ca0470f4aeae1956c3a074f83` (Apache-2.0,
`LICENSE`; `NOTICE.md` names the MIT source of `ios.md` and `android.md`),
except `reference/hooks.md`, the playbook that installs the upstream hook
into the runners' configuration, which is left out. They are unmodified; this file says how they apply here, and where it
disagrees with them, this file wins. The audit is
`docs/skill-audits/impeccable.md`; the provenance is `PROVENANCE.yaml`.

## Never run anything

The upstream skill is built around a launcher (`scripts/impeccable`) that
downloads and executes a native binary, hooks that run it on every edit, and
a live mode that injects scripts into the project's pages. None of it is
here, and none of it may be used:

- Do not run, download, install, or look for `impeccable`, its launcher, an
  `npx impeccable` command, or a binary in `~/.impeccable`. A reference that
  says to run `"<skill-base-dir>/scripts/impeccable" <verb>` (or
  `impeccable <verb>`) describes a step that does not exist in this
  project: skip it, do by reading and by looking at the render what the
  step was for, and say in your result that the automated detector did not
  run.
- Do not write `PRODUCT.md`, `DESIGN.md`, a design sidecar, or a
  `.impeccable/` directory. Do not start a dev server for a live mode, inject
  a script into a page, or change a Content Security Policy.
- Ignore the user-level Impeccable plugin or skill if your runner also
  offers one: it is not the audited copy, and ADR 019 rules out global
  skills. This file and `reference/` are the only Impeccable guidance of the
  project.

## The brief

Impeccable says "the brief wins". In this project the brief is, in this
order: the feature's GitHub Issue and plan; the design specification of
F123 once it exists; `docs/authoring.md`, sections "Visual design",
"Figures", and "Lesson format 2"; the tokens of `site/assets/site.css` and
the colours of `src/pbc/authoring/design.py`. Read them where Impeccable
says to read `PRODUCT.md` and `DESIGN.md`, and never invent a missing part
of them: an open design question goes into the plan or to the owner. Fonts,
palette, and components that the brief fixes are pinned aesthetics in
Impeccable's sense; its advice to self-host a new face or choose a new world
applies only when a plan asks for that.

## The modes that apply

- **Read** (`reference/mode-read.md`): lesson pages, the course pages, the
  documentation pages. The reading column stays calm; mathematics, figures,
  code, and tables sit in their standard forms.
- **Persuade** (`reference/mode-persuade.md`): the home page, within the
  restraint of the brief.
- **Operate** applies only to the interface of a widget, with
  `reference/operate.md`; **Experience** does not apply.

## The playbooks that apply

Read `reference/craft-floor.md` before any change to a visual surface, and
the playbook of the task:

| Task | Reference |
|---|---|
| Plan a surface before code | `reference/shape.md`, `reference/new-work.md` |
| Review a rendered surface | `reference/critique.md`, `reference/audit.md` |
| Final pass | `reference/polish.md` |
| Typography | `reference/typeset.md` |
| Spacing, rhythm, hierarchy | `reference/layout.md` |
| Colour | `reference/colorize.md`, `reference/quieter.md` |
| Motion | `reference/animate.md` |
| Phone and desktop widths | `reference/adapt.md` |
| Labels, messages, copy | `reference/clarify.md` |
| Remove complexity | `reference/distill.md` |
| Edge cases, errors, empty states | `reference/harden.md` |

Not used: `live.md`, `live-setup.md`, `generate.md`, `doctor.md`
(they need the launcher or change the runner), `init.md` and `document.md`
(they write `PRODUCT.md` and `DESIGN.md`), `bolder.md`, `delight.md`,
`overdrive.md` (unless the plan asks for them), the native references
(`ios.md`, `android.md`, `*.native.md`), and `reference/degraded/` (subagent
briefs of the upstream workflow).

## Where the project's rules win

- No framework, bundler, or new runtime dependency: Quarto, `.qmd`, the
  site's CSS, SVG, native MathML, and Python only.
- Accessibility is the project's floor (`docs/authoring.md`, "Visual
  design"): the contrast of `tests/unit/test_design.py`, visible keyboard
  focus, no meaning by colour alone, `prefers-reduced-motion` honoured, a
  static equivalent for anything that moves, and the payload budget of a
  page.
- A visual never changes a scientific statement, a number, a figure's
  status, or a claim label; copy that states physics is not "UX copy" and
  is changed only by the lesson's own rules.
- Impeccable's "verify by looking at the render" holds: look at the built
  page at phone and desktop width. That look is evidence for the review, not
  proof; the review of ADR 018 decision 6 and the checks decide.

Record in the completion evidence that this skill was applied, at the
revision of `PROVENANCE.yaml`, and which playbooks shaped which change.
