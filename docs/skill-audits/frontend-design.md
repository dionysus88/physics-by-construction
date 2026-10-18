# Audit: Anthropic Frontend Design

Audited 2026-10-18 for F122 (Issue #215). Owner decision (2026-10-18, on the
Issue): vendor as is.

## 1. Upstream

- Repository: <https://github.com/anthropics/skills>, the skill at
  `anthropics/skills/skills/frontend-design/`.
- Pinned commit: `dbd4588f9e1033efb41dad4bef2f7947c8993d44` (2026-10-09), the
  head of `main` when cloned. The skill's own last change is
  `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f` (2026-09-03, "Update
  frontend-design skill to avoid generic design defaults").
- The same skill is also distributed as a Claude Code plugin; the skills
  repository is the canonical source and the one audited.

## 2. Files

| File | Bytes | SHA-256 |
|---|---|---|
| `SKILL.md` | 9 390 | `d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3` |
| `LICENSE.txt` | 10 174 | `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` |

Directory digest: `180ab393af52fde72c621db7a1236e48c3b6769682961ea8cada4d9fac454d1c`
(two files).

## 3. Scripts

None. The skill is prose only: no script, no reference file, no asset, no
hook, no subagent.

## 4. Licence

Apache License 2.0, full text in `LICENSE.txt` beside the skill. It permits
redistribution of the unmodified files with the licence. Redistribution
decision: vendoring is allowed; the licence file is kept beside the copy.

## 5. Dependencies and security assumptions

No dependency. The skill asks the agent to plan a token system before
writing code, to review the plan against the brief, to take screenshots of
its own work "if your environment supports it", and, when the brief does not
name the subject, to "confirm with the client". It fetches nothing, names no
URL, and asks for no installation. It does not mention fonts from a remote
service, a framework, or a build tool.

## 6. Compatibility

- **Stack:** plain CSS and HTML guidance; nothing in it requires a framework
  or bundler, so it fits Quarto pages, `.qmd`, the site's SCSS, SVG, and
  GitHub Pages. Its "quality floor" (responsive to phone width, visible
  keyboard focus, reduced motion, accessible colour) agrees with the visual
  quality gate and `docs/authoring.md`, "Visual design".
- **Points that need the project's rule to win:** it pushes for "aesthetic
  risk" and a "distinct point of view"; in this project the design
  specification of F123 and `docs/authoring.md` are the brief, and the skill
  itself says the brief's own words always win. Its advice to choose
  typefaces "not the default families" is subordinate to the fonts the
  specification fixes. "Confirm with the client" cannot happen in an
  unattended session: the feature plan is the confirmed brief.
- **Runners:** a two-file `SKILL.md` directory; both runners can read it by
  path, which is what the role instructions will name (criterion 2).

## 7. Removed or adapted

Nothing removed. The project's precedence (specification and authoring rules
over the skill) goes in the skills README and the selection policy, not into
the vendored file, so the copy stays byte-identical to the pin.

## 8. Recommended outcome

**Vendor as is** at `dbd4588f9e1033efb41dad4bef2f7947c8993d44`, both files,
at `.agents/skills/frontend-design/`, with a provenance record. Small,
scriptless, permissively licensed, and compatible with the stack.
