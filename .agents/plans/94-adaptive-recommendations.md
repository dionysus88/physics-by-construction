# Plan: F14 — adaptive recommendations (Issue #94)

## Design

- **Rules.** `site/learner/recommend.js`, a pure ES module (no DOM, no storage,
  no request). `recommend(lessons, state)` takes the path (lessons in path
  order, each with `id`, `title`, `href`, `prerequisites`) and the parsed
  learner state, and returns at most 3 recommendations
  `{lesson, kind, reason}`, deterministic. With no stored lesson entry it
  returns nothing (the plain path). Kinds, in rank order:
  1. `prerequisite`: a prerequisite not completed of a lesson the learner has
     completed ("You completed X, which builds on Y.").
  2. `retry`: a lesson whose self-check was tried and not answered correctly.
  3. `next`: a lesson not completed whose prerequisites are all completed
     (first by path order).
  A lesson gets its first rule only. Ignored lessons are skipped.
- **Ignore.** Optional `ignored` list of lesson ids in the stored record
  (format stays version 1; absent means none). A recommendation has an
  "Ignore" button; the path page and lesson pages offer "Show ignored
  suggestions again". Clear-data removes it with everything.
- **Data.** The page's JSON data element gets `path`: the lessons with hrefs
  relative to the page, so computing makes no request (`path.json` is not
  fetched).
- **Display.** `#recommendations` (`data-enhancement`) on lesson pages (after
  the header) and the path page (after "Your progress"); hidden with no
  suggestions.

## Tests

- Rules: run `recommend.js` in the browser on a fixed state (tests/e2e).
- Unit: markup carries the path; export unchanged.
- Built site: no request while computing; no state, no JavaScript shows the
  plain path; ignore persists; keyboard; axe.
- Source scan covers `recommend.js`.
