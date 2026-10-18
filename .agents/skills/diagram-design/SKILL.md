---
name: diagram-design
description: "Physics by Construction adapter of Diagram Design (cathrynlavery/diagram-design at 550fd66e): principles for a conceptual physics diagram (a state and its update, the forces on a body, a phase plane, an apparatus) drawn by an executed cell with pbc.authoring.diagrams. Prose only; it runs no command. Use when a feature plan selects it for a new or substantially changed conceptual diagram."
license: "Project-owned adapter; the upstream is MIT, see LICENSE"
---

# Diagram Design, adapted for Physics by Construction

The general principles of Cathryn Lavery's Diagram Design skill
(`cathrynlavery/diagram-design`, `skills/diagram-design/SKILL.md` §1, §2,
§4, §6, §7, §9, §12 and `references/animation.md`, at
`550fd66edff058bc73056c3416b76d69cfe865ba`), restated in the project's
words for conceptual physics diagrams. Nothing of the upstream is copied
here except its licence (`LICENSE`, MIT), kept because this text derives
from it. The audit is `docs/skill-audits/diagram-design.md`; the
provenance is `PROVENANCE.yaml`.

Not taken over, and not to be fetched or run: the first-run style-guide
questions, the 45 software and business diagram types, the standalone HTML
output with its own fonts and palette, the icons, and the upstream scripts.

## How a diagram is made here

`docs/authoring.md` decides, and this skill does not change it: a
conceptual diagram is drawn by an executed cell with the helpers of
`pbc.authoring.diagrams` (`canvas` or `frame`, then `arrow`, `state_box`,
`circle`, `line`, `text`) in the figure colours; the cell has
`#| fig-status: conceptual`, a `fig-alt` that conveys the insight, and a
caption that states it; the sentence after it says that the diagram is a
sketch and which question it answers. No image file. The diagrams of F32
are the examples: `fig-state-and-update` (mechanics 01),
`fig-forces-on-a-falling-particle` (mechanics 02),
`fig-drag-against-speed` (mechanics 03), `fig-oscillator-energy-ellipse`
(mechanics 04), and `fig-update-orderings` (mechanics 05, drawn by
`draw_update_orderings` of `pbc.mechanics.experiments.numerical_integrators`).

## Principles

1. **Draw only when a picture teaches more than a sentence.** Ask whether
   the reader would learn more from the diagram than from a good
   paragraph, a table, or a list. A one-shape diagram is a sentence.
2. **Deletion is the best move.** Every element is one distinct idea; two
   elements that always go together are one. Every arrow carries
   information that the layout does not already show. The diagram is done
   when nothing can be removed.
3. **A budget.** About nine elements and a dozen arrows at most; above
   that, split into an overview and a detail. One or two accented elements
   carry the point; an accent on everything is no accent.
4. **Arrows mean something physical, and the legend or caption says
   what.** A force, a velocity, a flow, a step of an update: a different
   meaning gets a different line style or head, not only a different
   colour. Arrows do not cross or overlap where a reroute avoids it, each
   ends at its own point of an edge, and none passes behind an element it
   does not connect.
5. **Labels are readable.** Horizontal, short, beside their line and never
   on it, clear of the elements; symbols match the lesson's notation
   (the same letter, the same subscript, the same unit).
6. **The legend explains every kind of mark used, and nothing else**, at
   the edge of the figure, never over the content.
7. **The remove test before shipping.** Can an element, an arrow, or a
   label go? Can two elements merge? Is the accent on at most two things?
8. **Accessible by construction.** The meaning survives without colour
   (line style, marker, shape, label), the `fig-alt` says what the diagram
   shows and what it means, not its coordinates, and the contrast follows
   the figure colours. Where a diagram is SVG outside a lesson (for
   example, a fallback card), the SVG has `role="img"` with a `<title>` and
   a `<desc>` that it names, and a decorative SVG is `aria-hidden`.
9. **Static first.** The complete diagram is the static figure. Motion is
   added only where order or accumulation is the point, never supplies
   meaning that the static frame lacks, stops under
   `prefers-reduced-motion: reduce`, and has controls; the widget rules of
   `docs/authoring.md` apply.

## What this skill does not decide

A diagram is a sketch, not a result: it carries no computed value, no
invented equation, and no datum, and it is never evidence for a claim. The
physics it shows is checked against the lesson's text and its sources by
the review, independently of this skill. When a diagram needs a computed
curve (a trajectory, an energy ellipse), the curve comes from the verified
implementation in `src/pbc`, and the figure follows the PBC Scientific
Visualization skill as well.

Record in the completion evidence that this skill was applied, at the
revision of `PROVENANCE.yaml`, and which diagram it shaped.
