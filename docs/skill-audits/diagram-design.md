# Audit: Diagram Design

Audited 2026-10-18 for F122 (Issue #215). Owner decision (2026-10-18, on the
Issue): a thin adapter with the general principles in project words.

## 1. Upstream

- Repository: <https://github.com/cathrynlavery/diagram-design> (Cathryn
  Lavery). The owner's name "Diagram Design" matches this skill; no
  Anthropic skill of that name exists. A different `diagram` skill of the
  gstack suite was not audited.
- The skill: `cathrynlavery/diagram-design/skills/diagram-design/`, version
  2.6 (front matter).
- Pinned commit: `550fd66edff058bc73056c3416b76d69cfe865ba` (2026-10-16), the
  head of `main` when cloned. The skill directory's own last change is
  `05a858c92880ae550be9290bbfd3e8301f8d5d91` (2026-10-16).
- The repository also carries plugin manifests for several runners,
  slash-command prompts (`commands/`, `prompts/`), and about ninety
  maintainer scripts and tests at its root; they are not part of the skill.

## 2. Files

287 files, 5.6 MB, directory digest
`667e01aa63bad59d8d6e17fbcf88fb679de83b89507e36d3763f3e2caccc026b`:

- `SKILL.md` (394 lines): first-run style-guide gate, philosophy, a selection
  table of 45 visual types, layout and arrow rules, a checklist (the "taste
  gate"), import, output, and export.
- `references/` (63 Markdown files): one per visual type
  (`type-architecture.md`, `type-flowchart.md`, `type-line.md`, …), the
  style guide, onboarding and profiles, semantic patterns, animation,
  export, and icon primitives.
- `assets/` (217 files): example diagrams as standalone HTML, HTML templates
  (`template.html`, `template-motion.html`, `template-terminal.html`), and
  an icon sheet.
- `scripts/` (6 Python files), below.

Section 9 lists every file with its disposition.

## 3. Scripts

All Python 3, standard library except one:

- `self_check.py`: reads a generated HTML file and checks the accessible-SVG
  contract, single-file safety (no remote resource except Google Fonts),
  content inside the viewBox, and motion basics. Imports `argparse`, `re`,
  `html.parser`, `urllib.parse`; reads one file, writes nothing, no network.
  `SKILL.md` asks the agent to run it on every diagram.
- `drawio_extract.py`, `mermaid_extract.py`, `excalidraw_extract.py`: parse
  an imported diagram file and print a digest (nodes, edges, groups).
  Standard library (`zlib`, `base64`, `json`, `re`); read one file, write to
  standard output, no network.
- `export_svg.py`: extracts the `<svg>` of a generated HTML file into a
  standalone SVG, adding an `@import` of Google Fonts. Standard library;
  writes the output file.
- `export_png.py`: renders the HTML in a headless browser through
  **Playwright** (`playwright.sync_api`), which loads the page and its web
  fonts from the network and writes a PNG. Playwright and a browser are not
  in the project's locked environment.

The repository-root scripts (`verify-*.py`, `lint-*.py`) that `SKILL.md`
mentions "from a repository checkout" are not in the skill directory.

## 4. Licence

MIT (`LICENSE`, Copyright (c) 2025 Cathryn Lavery). Bundled content listed
in `THIRD_PARTY_LICENSES.md`: Tabler Icons (MIT), Simple Icons (CC0 1.0),
log-z/logos (MIT), Devicon (MIT), one-off brand marks (public domain and an
IcePanel collection); brand logos remain trademarks of their owners.
Redistribution is allowed with the MIT notice; the brand icons would carry
trademark considerations the project does not need.

## 5. Dependencies and security assumptions

- Before the first diagram in a project the skill **pauses and asks the
  user** to customise the style guide, offering to fetch a website, read
  another skill, or load a saved profile; it writes a `.diagram-design`
  marker and profile into the project. An unattended session cannot answer.
- The onboarding "URL" branch fetches an external page and its resources
  (it warns and asks first, and treats the page as untrusted data).
- Output is a standalone HTML file with inline SVG, inline CSS, and a Google
  Fonts link (Instrument Serif, Geist, Geist Mono); motion uses a small
  inline script.
- PNG export needs Playwright and network access.

## 6. Compatibility

- **Subject:** the 45 types are those of software, business, and data
  communication (architecture, ER, Gantt, Sankey, Wardley, kanban, service
  blueprint, …). None is a physics schematic (a free-body diagram, a field
  sketch, a phase portrait, an apparatus); the conceptual-diagram use the
  change request names (section 7) is outside its catalogue.
- **Stack:** its output format, a standalone HTML page with its own fonts and
  palette, does not fit a figure inside a Quarto lesson: the site's design
  system (`docs/authoring.md`, "Visual design") fixes fonts and colours,
  and a lesson figure is SVG or a Python-generated image in the page, not a
  separate HTML document with remote fonts.
- **What does fit:** the general principles of `SKILL.md` §1 (deletion,
  every node a distinct idea, every line carries information, one or two
  accent nodes, a density budget, split above about nine nodes), the
  "don't draw" test, the arrow and label rules, the accessible-SVG contract
  that `self_check.py` checks (an accessible SVG with title and description, content in
  the viewBox), and the static-first rule with a complete no-JavaScript
  frame and reduced-motion handling in `references/animation.md`.
- **Runners:** prose readable by both; `self_check.py` would need a shell
  and is not available to the read-only reviewing roles.

## 7. Removed or adapted

Not vendored: the style-guide gate and onboarding (interactive, network,
project markers), the 45 type references and their templates and examples
(outside the subject and the stack), the icon set (trademarks, not needed),
the export scripts (Playwright, remote fonts), and the import extractors (no
use in the project). The useful principles of section 6 would be carried in
project words, with attribution under the MIT licence.

## 8. Recommended outcome

**Adapter, or drop.** A thin project-owned
`SKILL.md` in `.agents/skills/diagram-design/` that states the general diagram
principles listed in section 6 for conceptual physics diagrams in the site's
SVG and palette, cites the upstream at the pinned commit as its source
material with the MIT notice, and runs no upstream script. Nothing of the
upstream is vendored. If the owner prefers, the same principles can go into
the project-owned PBC Scientific Visualization skill (whose topics already
include conceptual diagrams) and Diagram Design is dropped with the reason
"outside the subject and the output format of the project".

## 9. File inventory

Every file of the skill directory `skills/diagram-design/` at the pinned
commit (287), and the two repository-root licence files, enumerated from the
pinned tree (read 2026-10-18 with a shallow fetch of the commit into an
empty directory; nothing executed). Paths are relative to the skill
directory, except `LICENSE` and `THIRD_PARTY_LICENSES.md` (repository root).
"Git blob" is the first twelve hex digits of the file's Git object id at the
pin. Nothing of the skill is vendored; the adapter's `LICENSE` is
byte-identical to the upstream's.

| File | Bytes | Git blob | What it is | Disposition |
|---|---:|---|---|---|
| SKILL.md | 30799 | 4e70b3569d5f | Upstream entry point: style-guide gate, philosophy, type table, layout and arrow rules, taste gate, import, output, export | Not vendored: the general principles of sections 1, 2, 4, 6, 7, 9, and 12 are carried in project words in the adapter's `SKILL.md` (source material) |
| references/animation.md | 12437 | 150c71857ca4 | Optional animation: modes, static-first contract, reduced motion | Not vendored: its static-first contract is carried in project words (source material) |
| references/doctor.md | 6152 | 14ff30a474a6 | Environment diagnostics of import, export, and command routing | Not vendored: runner and environment maintenance |
| references/export-registry.md | 6319 | b150f0fb8b0c | Manual export of a block-metadata sidecar `.registry.json` | Not vendored: export to a standalone format |
| references/export.md | 28753 | 93aaac08a34f | Manual export of a generated HTML diagram to SVG or PNG | Not vendored: export scripts (Playwright, remote fonts) |
| references/import-drawio.md | 14302 | 67c760766c0a | Redraw of a draw.io file | Not vendored: import, no use in the project |
| references/import-excalidraw.md | 11278 | a03dfdb18df0 | Redraw of an Excalidraw board | Not vendored: import, no use in the project |
| references/import-mermaid.md | 11647 | 4a5c20d5e547 | Redraw of Mermaid source | Not vendored: import, no use in the project |
| references/layout-budget.md | 4440 | 3f3239eb7cbe | Layout grid, per-type budgets, page layout, summary cards | Not vendored: the complexity budget of `SKILL.md` section 7 is carried; the per-type budgets are for the upstream types |
| references/onboarding.md | 16928 | 2a0dd188ea6b | Onboarding: derive a skin from a website, a skill, or a folder | Not vendored: interactive, fetches pages, writes project markers |
| references/output-spec.md | 19200 | 9ae661c8617e | Output dials of a draw.io import (format, size, detail, audience) | Not vendored: import, no use in the project |
| references/primitive-annotation.md | 1661 | 3b596cff2be3 | Primitive: italic-serif annotation callout | Not vendored: the upstream skin; the site's design system fixes fonts |
| references/primitive-icons.md | 105941 | 9a2287c0a863 | Primitive: monochrome IT and cloud icon library (brand marks) | Not vendored: icon set, brand trademarks, not needed |
| references/primitive-sketchy.md | 1700 | a27902457149 | Primitive: hand-drawn displacement filter | Not vendored: the upstream skin |
| references/primitive-terminal.md | 3915 | 4d65ab32fe22 | Primitive: terminal-window skin | Not vendored: the upstream skin |
| references/primitives-core.md | 12935 | fdfd63818668 | Core SVG primitives: connectors, arrows, node boxes | Not vendored: the connector rules of `SKILL.md` section 6 are carried; the drawing code is the upstream's HTML |
| references/profiles.md | 14434 | ba8dccd9ca32 | Named client profiles and their verbs | Not vendored: writes project markers and profiles |
| references/semantic-patterns.md | 16679 | 637ba9db9966 | Semantic patterns of system behaviour | Not vendored: software-system patterns, outside the subject |
| references/style-guide.md | 20915 | b6045a819a42 | Colours, typography, and tokens of the upstream skin | Not vendored: the site's design system (`docs/authoring.md`, "Visual design") fixes fonts and colours |
| references/type-architecture-delta.md | 14595 | e418fb6c75da | Visual type reference: architecture delta | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-architecture.md | 10485 | 139082e743df | Visual type reference: architecture | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-axonometric-plan.md | 7184 | e27283dd1daa | Visual type reference: axonometric plan | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-bar.md | 14056 | 3654304041d5 | Visual type reference: bar | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-data-flow.md | 20858 | dab7447ed6c6 | Visual type reference: data flow | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-db-schema.md | 4954 | e1ab89fd3492 | Visual type reference: db schema | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-dependency.md | 4309 | 3a01e1649f05 | Visual type reference: dependency | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-deployment.md | 4295 | e757a3aec0ee | Visual type reference: deployment | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-dp-integration.md | 22057 | 2da6f558e06c | Visual type reference: dp integration | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-dp-security-matrix.md | 19086 | 4b099ec38535 | Visual type reference: dp security matrix | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-er.md | 1531 | 5792e978f77b | Visual type reference: er | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-exploded.md | 11157 | c7849d8ed390 | Visual type reference: exploded | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-fishbone.md | 5796 | c735730870a6 | Visual type reference: fishbone | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-flowchart.md | 1079 | 1042be73817e | Visual type reference: flowchart | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-gantt.md | 2433 | 2fed6693e677 | Visual type reference: gantt | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-heatmap.md | 7696 | bdd3272ead9d | Visual type reference: heatmap | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-high-level.md | 28325 | 1a34c9117e2d | Visual type reference: high level | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-it-state.md | 29677 | a1b1cec56fb6 | Visual type reference: it state | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-journey.md | 5385 | cd041a095a2b | Visual type reference: journey | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-kanban.md | 4531 | 5bbec1cfa263 | Visual type reference: kanban | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-layers.md | 1570 | fb3b436350fc | Visual type reference: layers | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-line.md | 43194 | 6781c247d411 | Visual type reference: line | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-loop.md | 12609 | b4b30e32b24b | Visual type reference: loop | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-medallion.md | 22226 | 63afec9a4da3 | Visual type reference: medallion | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-nested.md | 1363 | ae2fa31ed1ee | Visual type reference: nested | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-org-chart.md | 3101 | c22ceaaebdb2 | Visual type reference: org chart | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-polar.md | 7998 | e630b93b4c2b | Visual type reference: polar | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-process.md | 28224 | 91e28e210594 | Visual type reference: process | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-pyramid.md | 1805 | 703f15aa549a | Visual type reference: pyramid | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-quadrant.md | 6256 | 186399a6652a | Visual type reference: quadrant | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-radar.md | 5626 | a26fea65b201 | Visual type reference: radar | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-sankey.md | 9389 | b801f134be7a | Visual type reference: sankey | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-scatter.md | 20433 | 80c44fafab76 | Visual type reference: scatter | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-sequence.md | 6798 | 0a26f9cb8d91 | Visual type reference: sequence | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-service-blueprint.md | 7700 | e13899751f37 | Visual type reference: service blueprint | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-state.md | 1958 | 85b8cdda0544 | Visual type reference: state | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-story-map.md | 4882 | 391972ca360a | Visual type reference: story map | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-swimlane.md | 1197 | c93183952bc7 | Visual type reference: swimlane | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-timeline.md | 1091 | e0e8d9b65028 | Visual type reference: timeline | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-tree.md | 1517 | 439efd41c11d | Visual type reference: tree | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-treemap.md | 18520 | 1ed6c5edb756 | Visual type reference: treemap | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-uml-class.md | 4902 | 0c8af2222106 | Visual type reference: uml class | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-venn.md | 1659 | c93392c25aca | Visual type reference: venn | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-wardley.md | 5778 | 0b76832640d8 | Visual type reference: wardley | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| references/type-waterfall.md | 8987 | 4b702e024850 | Visual type reference: waterfall | Not vendored: a software or business visual type, outside the subject and the stack (section 6) |
| scripts/drawio_extract.py | 34723 | ea3a4ef76cf4 | Parses a draw.io file and prints a digest; standard library, no network | Not vendored: import extractor, no use |
| scripts/excalidraw_extract.py | 26355 | 6b57876425fc | Parses an Excalidraw file and prints a digest; standard library, no network | Not vendored: import extractor, no use |
| scripts/export_png.py | 3682 | 0bc16e9e3b35 | Renders the HTML to PNG through Playwright and the network | Not vendored: needs Playwright and the network |
| scripts/export_svg.py | 51919 | 0bf43c0a8364 | Extracts the SVG of a generated HTML file, adding a Google Fonts import | Not vendored: export, remote fonts |
| scripts/mermaid_extract.py | 57048 | c86d84692543 | Parses Mermaid source and prints a digest; standard library, no network | Not vendored: import extractor, no use |
| scripts/self_check.py | 29433 | 11cd1039201b | Checks a generated HTML diagram: accessible SVG, single-file safety, content in the viewBox, motion basics; reads one file, no network | Not vendored: runs nothing; the accessible-SVG contract it checks is carried in prose |
| assets/example-architecture-containment-dark.html | 14552 | cd5743840768 | Example diagram: architecture containment, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture-containment-full.html | 17524 | 0b9fdf3ce45f | Example diagram: architecture containment, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture-containment.html | 14411 | ab1dff6c5201 | Example diagram: architecture containment | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture-dark.html | 12036 | 435e2ec89742 | Example diagram: architecture, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture-delta-dark.html | 20558 | 0b1da51999f7 | Example diagram: architecture delta, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture-delta-full.html | 22225 | c35794228780 | Example diagram: architecture delta, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture-delta.html | 20459 | c9dfc5fc042e | Example diagram: architecture delta | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture-full.html | 14981 | e33a359c4ff7 | Example diagram: architecture, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-architecture.html | 12099 | dee30d264a3f | Example diagram: architecture | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-campus-animated.html | 47875 | 706b31be9451 | Example diagram: axonometric plan campus, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-campus-dark.html | 31662 | 69e1a2a67645 | Example diagram: axonometric plan campus, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-campus-full.html | 34299 | da17392f07ab | Example diagram: axonometric plan campus, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-campus.html | 31659 | 7559a84bcf4e | Example diagram: axonometric plan campus | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-coffee-shop-animated.html | 55593 | d89d3b5d876f | Example diagram: axonometric plan coffee shop, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-coffee-shop-dark.html | 39572 | f207674b3343 | Example diagram: axonometric plan coffee shop, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-coffee-shop-full.html | 42146 | bf8516527a95 | Example diagram: axonometric plan coffee shop, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-coffee-shop.html | 39381 | f61d965ead18 | Example diagram: axonometric plan coffee shop | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-dark.html | 28850 | 53a5e45f0894 | Example diagram: axonometric plan, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-full.html | 31351 | f717c54e921a | Example diagram: axonometric plan, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-warehouse-animated.html | 54978 | 8c32c86e037f | Example diagram: axonometric plan warehouse, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-warehouse-dark.html | 39154 | 0302fa0c7d08 | Example diagram: axonometric plan warehouse, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-warehouse-full.html | 41540 | 592cab6a983f | Example diagram: axonometric plan warehouse, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan-warehouse.html | 38780 | cb79b797900d | Example diagram: axonometric plan warehouse | Not vendored: example of an upstream type, standalone HTML |
| assets/example-axonometric-plan.html | 28651 | aa76f4118ac1 | Example diagram: axonometric plan | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bar-dark.html | 9122 | 0d9aa66b3949 | Example diagram: bar, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bar-full.html | 11252 | c4533c7c7d42 | Example diagram: bar, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bar.html | 8917 | 7340852f39cf | Example diagram: bar | Not vendored: example of an upstream type, standalone HTML |
| assets/example-beeswarm-dark.html | 32654 | 9746cf6b4db4 | Example diagram: beeswarm, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-beeswarm-full.html | 36450 | 19899cbdef3a | Example diagram: beeswarm, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-beeswarm.html | 32180 | 0bf5c803d345 | Example diagram: beeswarm | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bubble-dark.html | 11428 | 626f6e4d92ed | Example diagram: bubble, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bubble-full.html | 15124 | 3e322f51689e | Example diagram: bubble, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bubble.html | 11335 | 484fb393b089 | Example diagram: bubble | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bump-dark.html | 12926 | 01a085fe4469 | Example diagram: bump, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bump-full.html | 16635 | fc1461a348b0 | Example diagram: bump, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-bump.html | 12807 | 52a1b043f8cf | Example diagram: bump | Not vendored: example of an upstream type, standalone HTML |
| assets/example-data-flow-dark.html | 12966 | 22b75a35e6ec | Example diagram: data flow, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-data-flow-full.html | 15830 | 15c464697066 | Example diagram: data flow, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-data-flow.html | 12798 | 2c4a28f7d28f | Example diagram: data flow | Not vendored: example of an upstream type, standalone HTML |
| assets/example-datalake-dark.html | 25092 | 61f485971905 | Example diagram: datalake, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-datalake-full.html | 28598 | 6d7faf546b60 | Example diagram: datalake, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-datalake.html | 26674 | 0846dd3493a8 | Example diagram: datalake | Not vendored: example of an upstream type, standalone HTML |
| assets/example-db-schema-dark.html | 24740 | 18d7c014c5eb | Example diagram: db schema, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-db-schema-full.html | 27627 | 2bbad9b0f18f | Example diagram: db schema, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-db-schema.html | 24523 | 4bbb2d6f2516 | Example diagram: db schema | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dependency-dark.html | 17822 | bbbfd2c177ab | Example diagram: dependency, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dependency-full.html | 21122 | c8faff05a147 | Example diagram: dependency, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dependency.html | 17607 | 8f040159be8a | Example diagram: dependency | Not vendored: example of an upstream type, standalone HTML |
| assets/example-deployment-dark.html | 13554 | dd3c0d876ab0 | Example diagram: deployment, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-deployment-full.html | 16827 | dc04ed7df01e | Example diagram: deployment, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-deployment.html | 13448 | 774e01454e64 | Example diagram: deployment | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dp-integration-dark.html | 14745 | 86b2e7b67bd9 | Example diagram: dp integration, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dp-integration-full.html | 17262 | d95f287565f1 | Example diagram: dp integration, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dp-integration.html | 14714 | 9d20f230ffc8 | Example diagram: dp integration | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dp-security-matrix-dark.html | 10279 | f71aa8c86f52 | Example diagram: dp security matrix, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dp-security-matrix-full.html | 12601 | 181dde242c08 | Example diagram: dp security matrix, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-dp-security-matrix.html | 10905 | 6b69cf05de11 | Example diagram: dp security matrix | Not vendored: example of an upstream type, standalone HTML |
| assets/example-er-dark.html | 14198 | a21c32e68cac | Example diagram: er, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-er-full.html | 17123 | 8ceeec0903a1 | Example diagram: er, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-er.html | 14134 | 5fd3bcf42c8d | Example diagram: er | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-ai-stack-animated.html | 53486 | b57052458246 | Example diagram: exploded ai stack, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-ai-stack-dark.html | 36043 | cba3faf4625f | Example diagram: exploded ai stack, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-ai-stack-full.html | 38911 | b04ca261b271 | Example diagram: exploded ai stack, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-ai-stack.html | 36058 | 2f8066518f48 | Example diagram: exploded ai stack | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-dark.html | 8543 | da38b5c36d44 | Example diagram: exploded, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-full.html | 11447 | 21c44a86602e | Example diagram: exploded, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-keyboard-animated.html | 208294 | 04cd068932af | Example diagram: exploded keyboard, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-keyboard-dark.html | 180795 | 6c4a3ff65410 | Example diagram: exploded keyboard, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-keyboard-full.html | 193684 | fa242d9f13e4 | Example diagram: exploded keyboard, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-keyboard.html | 190868 | cfebe94e795c | Example diagram: exploded keyboard | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-phone-animated.html | 34616 | dd67f0833163 | Example diagram: exploded phone, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-phone-dark.html | 17431 | 8808014dfcd8 | Example diagram: exploded phone, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-phone-full.html | 20048 | 6e38feeeba9d | Example diagram: exploded phone, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-phone.html | 17302 | c243788230de | Example diagram: exploded phone | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-unboxing-animated.html | 34065 | a14bd803fb3f | Example diagram: exploded unboxing, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-unboxing-dark.html | 16707 | b66cac1935ec | Example diagram: exploded unboxing, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-unboxing-full.html | 19391 | 9e60aaa7b1e8 | Example diagram: exploded unboxing, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded-unboxing.html | 16644 | 1bfc7a444132 | Example diagram: exploded unboxing | Not vendored: example of an upstream type, standalone HTML |
| assets/example-exploded.html | 8724 | 04c3d89236b0 | Example diagram: exploded | Not vendored: example of an upstream type, standalone HTML |
| assets/example-fishbone-dark.html | 8675 | 46e6c2fca4e6 | Example diagram: fishbone, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-fishbone-full.html | 11407 | d461dab269f6 | Example diagram: fishbone, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-fishbone.html | 8648 | 554a4ace4476 | Example diagram: fishbone | Not vendored: example of an upstream type, standalone HTML |
| assets/example-flowchart-dark.html | 9446 | e918695855b7 | Example diagram: flowchart, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-flowchart-full.html | 12295 | 42df4401f58e | Example diagram: flowchart, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-flowchart.html | 9395 | cf9053045f85 | Example diagram: flowchart | Not vendored: example of an upstream type, standalone HTML |
| assets/example-gantt-dark.html | 10331 | 35a71807adb4 | Example diagram: gantt, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-gantt-full.html | 11895 | c0d47865fe90 | Example diagram: gantt, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-gantt.html | 10072 | 06d68820e688 | Example diagram: gantt | Not vendored: example of an upstream type, standalone HTML |
| assets/example-heatmap-dark.html | 18248 | 5e35f908f17a | Example diagram: heatmap, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-heatmap-full.html | 22036 | 5c917de2817e | Example diagram: heatmap, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-heatmap.html | 18108 | 043b40f7562b | Example diagram: heatmap | Not vendored: example of an upstream type, standalone HTML |
| assets/example-high-level-dark.html | 24080 | 899cd54dcdce | Example diagram: high level, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-high-level-full.html | 28360 | d92aca58b974 | Example diagram: high level, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-high-level-vertical-dark.html | 24854 | a1cd5653dbc1 | Example diagram: high level vertical, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-high-level-vertical-full.html | 28619 | 396b913d02a3 | Example diagram: high level vertical, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-high-level-vertical.html | 30391 | 2892399bcc33 | Example diagram: high level vertical | Not vendored: example of an upstream type, standalone HTML |
| assets/example-high-level.html | 26902 | 7ed148b77bff | Example diagram: high level | Not vendored: example of an upstream type, standalone HTML |
| assets/example-import-drawio.html | 12079 | 429d716142aa | Example diagram: import drawio | Not vendored: example of an import |
| assets/example-import-excalidraw.html | 7689 | 273a7e8f9ec0 | Example diagram: import excalidraw | Not vendored: example of an import |
| assets/example-import-mermaid.html | 8105 | dc77361bc55f | Example diagram: import mermaid | Not vendored: example of an import |
| assets/example-it-state-dark.html | 11992 | 69e7e485c32f | Example diagram: it state, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-it-state-full.html | 14223 | 835afb113fbe | Example diagram: it state, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-it-state.html | 12498 | 8481df94002b | Example diagram: it state | Not vendored: example of an upstream type, standalone HTML |
| assets/example-journey-dark.html | 9153 | 1111ff0d932a | Example diagram: journey, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-journey-full.html | 11721 | df7d946355c1 | Example diagram: journey, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-journey.html | 9109 | f09031f73c8b | Example diagram: journey | Not vendored: example of an upstream type, standalone HTML |
| assets/example-kanban-dark.html | 11036 | bf6643cc76b5 | Example diagram: kanban, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-kanban-full.html | 13899 | d7ee559ea32d | Example diagram: kanban, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-kanban.html | 10945 | 4ed1e033b4c0 | Example diagram: kanban | Not vendored: example of an upstream type, standalone HTML |
| assets/example-layers-dark.html | 6913 | c03f897714fd | Example diagram: layers, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-layers-full.html | 10023 | 1779f0c6a04a | Example diagram: layers, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-layers.html | 6875 | 92faaafc3b87 | Example diagram: layers | Not vendored: example of an upstream type, standalone HTML |
| assets/example-line-dark.html | 7608 | 87294a6c22da | Example diagram: line, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-line-full.html | 10051 | 2ec71a97705e | Example diagram: line, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-line.html | 7440 | e59922159af3 | Example diagram: line | Not vendored: example of an upstream type, standalone HTML |
| assets/example-loop-dark.html | 6821 | ecad93f0701a | Example diagram: loop, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-loop-full.html | 9964 | cde9ee5be1b7 | Example diagram: loop, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-loop-terminal.html | 9993 | 2e22273acb39 | Example diagram: loop, terminal skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-loop.html | 6789 | c9d7ac5cbaff | Example diagram: loop | Not vendored: example of an upstream type, standalone HTML |
| assets/example-marimekko-dark.html | 13604 | 5134a660a789 | Example diagram: marimekko, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-marimekko-full.html | 17040 | 271ed6bd757b | Example diagram: marimekko, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-marimekko.html | 13496 | 6ea9884b8368 | Example diagram: marimekko | Not vendored: example of an upstream type, standalone HTML |
| assets/example-medallion-dark.html | 13052 | 5019dbced2c9 | Example diagram: medallion, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-medallion-full.html | 15894 | 69eee77f0fa9 | Example diagram: medallion, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-medallion.html | 12861 | a75304d4e00b | Example diagram: medallion | Not vendored: example of an upstream type, standalone HTML |
| assets/example-nested-dark.html | 6735 | bebcbdb01a0e | Example diagram: nested, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-nested-full.html | 9844 | 911f53f1c16f | Example diagram: nested, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-nested.html | 6854 | 2b1413caf0a4 | Example diagram: nested | Not vendored: example of an upstream type, standalone HTML |
| assets/example-org-chart-dark.html | 11599 | b1ebf40523af | Example diagram: org chart, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-org-chart-full.html | 12049 | e0b3b5479154 | Example diagram: org chart, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-org-chart.html | 11527 | 5191b2a397ae | Example diagram: org chart | Not vendored: example of an upstream type, standalone HTML |
| assets/example-paved-road-animated.html | 28321 | 526b5d3d1d0b | Example diagram: paved road, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-polar-dark.html | 10447 | fcb1944f8567 | Example diagram: polar, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-polar-full.html | 12653 | e2967fc4a239 | Example diagram: polar, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-polar.html | 10385 | bbe1e8c5d672 | Example diagram: polar | Not vendored: example of an upstream type, standalone HTML |
| assets/example-policy-trace-animated.html | 25465 | c36b415e2969 | Example diagram: policy trace, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-process-dark.html | 15033 | 502c89cadeb1 | Example diagram: process, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-process-full.html | 17467 | 16fa0dd73a3b | Example diagram: process, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-process.html | 14997 | 8e72e9621578 | Example diagram: process | Not vendored: example of an upstream type, standalone HTML |
| assets/example-pyramid-dark.html | 6682 | b86fb668b43e | Example diagram: pyramid, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-pyramid-full.html | 9731 | 140092656bc3 | Example diagram: pyramid, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-pyramid.html | 6576 | 51b5a382d609 | Example diagram: pyramid | Not vendored: example of an upstream type, standalone HTML |
| assets/example-quadrant-consultant.html | 11881 | c8beafd1b65a | Example diagram: quadrant consultant | Not vendored: example of an upstream type, standalone HTML |
| assets/example-quadrant-dark.html | 6606 | 0d600cfa52a8 | Example diagram: quadrant, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-quadrant-full.html | 9620 | 2834c5d1b27f | Example diagram: quadrant, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-quadrant.html | 6573 | 8cef09aeb021 | Example diagram: quadrant | Not vendored: example of an upstream type, standalone HTML |
| assets/example-queue-animated.html | 30003 | e42358d1abda | Example diagram: queue, animated | Not vendored: example of an upstream type, standalone HTML |
| assets/example-radar-dark.html | 7687 | 9ad78d503b8d | Example diagram: radar, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-radar-full.html | 10429 | 81ae22939929 | Example diagram: radar, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-radar.html | 7863 | 9e303522030e | Example diagram: radar | Not vendored: example of an upstream type, standalone HTML |
| assets/example-ridgeline-dark.html | 10354 | ae9dab65626d | Example diagram: ridgeline, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-ridgeline-full.html | 14273 | 7afd9653a753 | Example diagram: ridgeline, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-ridgeline.html | 10281 | a2b620eb1931 | Example diagram: ridgeline | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sankey-dark.html | 8969 | ee7909797066 | Example diagram: sankey, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sankey-full.html | 11814 | 72d4b9bfd499 | Example diagram: sankey, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sankey.html | 8921 | 910c214f56f3 | Example diagram: sankey | Not vendored: example of an upstream type, standalone HTML |
| assets/example-scatter-dark.html | 9666 | 47198f6059d4 | Example diagram: scatter, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-scatter-full.html | 11577 | b6a2f7c6b1c8 | Example diagram: scatter, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-scatter.html | 9423 | 11fc90d03c29 | Example diagram: scatter | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sequence-dark.html | 13794 | 9365d054ab6d | Example diagram: sequence, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sequence-full.html | 18212 | a270dbc2264f | Example diagram: sequence, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sequence-oauth-dark.html | 12113 | 7434166ece2a | Example diagram: sequence oauth, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sequence-oauth-full.html | 16581 | ffddee4a849d | Example diagram: sequence oauth, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sequence-oauth.html | 14362 | ff48c14353ae | Example diagram: sequence oauth | Not vendored: example of an upstream type, standalone HTML |
| assets/example-sequence.html | 13723 | 070d7e68b127 | Example diagram: sequence | Not vendored: example of an upstream type, standalone HTML |
| assets/example-service-blueprint-dark.html | 14978 | 67033fb6048c | Example diagram: service blueprint, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-service-blueprint-full.html | 19464 | 38401d935565 | Example diagram: service blueprint, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-service-blueprint.html | 15842 | fa480e95d366 | Example diagram: service blueprint | Not vendored: example of an upstream type, standalone HTML |
| assets/example-slopegraph-dark.html | 10452 | 0535a9eae6e4 | Example diagram: slopegraph, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-slopegraph-full.html | 13992 | 456c19c1bb27 | Example diagram: slopegraph, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-slopegraph.html | 10370 | 88f888af8b94 | Example diagram: slopegraph | Not vendored: example of an upstream type, standalone HTML |
| assets/example-state-dark.html | 8698 | 3f9b0236d62c | Example diagram: state, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-state-full.html | 11623 | 423f24740ae5 | Example diagram: state, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-state-lifecycle-dark.html | 9633 | b30555ad082f | Example diagram: state lifecycle, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-state-lifecycle-full.html | 12624 | 48599fdae978 | Example diagram: state lifecycle, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-state-lifecycle.html | 10236 | 3c53a1d505a3 | Example diagram: state lifecycle | Not vendored: example of an upstream type, standalone HTML |
| assets/example-state.html | 8662 | 223c40c5bc35 | Example diagram: state | Not vendored: example of an upstream type, standalone HTML |
| assets/example-story-map-dark.html | 12247 | 2815f1b5dc8c | Example diagram: story map, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-story-map-full.html | 15483 | 463a28d7bf2d | Example diagram: story map, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-story-map.html | 12186 | b9e960e7d9ae | Example diagram: story map | Not vendored: example of an upstream type, standalone HTML |
| assets/example-streamgraph-dark.html | 13002 | 1ae4ad39d908 | Example diagram: streamgraph, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-streamgraph-full.html | 16442 | 83372bfc80c7 | Example diagram: streamgraph, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-streamgraph.html | 12941 | f7d1e9be0abd | Example diagram: streamgraph | Not vendored: example of an upstream type, standalone HTML |
| assets/example-swimlane-dark.html | 10580 | 2a7a3a8c37b4 | Example diagram: swimlane, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-swimlane-full.html | 13524 | 106638df7ee3 | Example diagram: swimlane, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-swimlane.html | 10534 | 45aaa9635cce | Example diagram: swimlane | Not vendored: example of an upstream type, standalone HTML |
| assets/example-timeline-dark.html | 7390 | 7b2c140c4cd2 | Example diagram: timeline, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-timeline-full.html | 10391 | e0b53484f2d6 | Example diagram: timeline, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-timeline.html | 7338 | e5399e49da9d | Example diagram: timeline | Not vendored: example of an upstream type, standalone HTML |
| assets/example-tree-block-decomposition-dark.html | 8303 | e90284d7e61e | Example diagram: tree block decomposition, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-tree-block-decomposition-full.html | 11639 | 51390e318751 | Example diagram: tree block decomposition, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-tree-block-decomposition.html | 8224 | 575d52078c4f | Example diagram: tree block decomposition | Not vendored: example of an upstream type, standalone HTML |
| assets/example-tree-dark.html | 11029 | 6cdbedd83198 | Example diagram: tree, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-tree-full.html | 13990 | fb4e28f239ba | Example diagram: tree, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-tree.html | 10913 | e60c59d495f5 | Example diagram: tree | Not vendored: example of an upstream type, standalone HTML |
| assets/example-treemap-dark.html | 7651 | 635ef3564398 | Example diagram: treemap, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-treemap-full.html | 10737 | 0f385bbf7839 | Example diagram: treemap, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-treemap.html | 7579 | d04ae8223918 | Example diagram: treemap | Not vendored: example of an upstream type, standalone HTML |
| assets/example-uml-class-dark.html | 12400 | 481bae4a477a | Example diagram: uml class, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-uml-class-full.html | 15679 | c3716a2d682b | Example diagram: uml class, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-uml-class.html | 12355 | 94013df59239 | Example diagram: uml class | Not vendored: example of an upstream type, standalone HTML |
| assets/example-venn-dark.html | 6699 | 6fa75202f7d5 | Example diagram: venn, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-venn-full.html | 9901 | 10081997e432 | Example diagram: venn, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-venn.html | 5079 | ac35a0570ac3 | Example diagram: venn | Not vendored: example of an upstream type, standalone HTML |
| assets/example-wardley-dark.html | 8924 | c7c2cfb82bc7 | Example diagram: wardley, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-wardley-full.html | 11344 | c0523f5d8f42 | Example diagram: wardley, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-wardley.html | 8881 | b7a131c2ac84 | Example diagram: wardley | Not vendored: example of an upstream type, standalone HTML |
| assets/example-waterfall-dark.html | 9844 | 2e7d0275061c | Example diagram: waterfall, dark skin | Not vendored: example of an upstream type, standalone HTML |
| assets/example-waterfall-full.html | 11594 | 9430ced261b0 | Example diagram: waterfall, full-page layout | Not vendored: example of an upstream type, standalone HTML |
| assets/example-waterfall.html | 9760 | 528420c4051f | Example diagram: waterfall | Not vendored: example of an upstream type, standalone HTML |
| assets/icons.html | 108545 | 942041f988ec | Icon sheet | Not vendored: icon set, brand trademarks |
| assets/index.html | 27128 | 205e63781203 | Gallery page of the examples | Not vendored: example of the upstream types |
| assets/template-dark.html | 4080 | cc2652504cd2 | HTML template, dark skin | Not vendored: standalone HTML with Google Fonts |
| assets/template-full.html | 23154 | 07cbe6bd23b5 | HTML template, full-page layout | Not vendored: standalone HTML with Google Fonts |
| assets/template-motion.html | 20935 | 0e3449e83fe0 | HTML template with motion | Not vendored: standalone HTML with Google Fonts |
| assets/template-terminal.html | 5481 | dfd9384e5fd2 | HTML template, terminal skin | Not vendored: standalone HTML with Google Fonts |
| assets/template.html | 4202 | 054e5c34961d | HTML template, light skin | Not vendored: standalone HTML with Google Fonts |
| LICENSE | 1071 | 5270ecfc4094 | MIT licence of the repository root | Copied unmodified as `LICENSE`: the adapter's `SKILL.md` derives from the upstream text |
| THIRD_PARTY_LICENSES.md | 3143 | 5311158e2621 | Licences of the bundled icons and brand marks | Not copied: no icon is vendored |
