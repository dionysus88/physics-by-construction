// What to do next, from the prerequisite graph of the learning path and the
// results a reader has stored in this browser. Pure rules: this module reads
// no storage, touches no page, and makes no request, so that the same path
// and the same state always give the same suggestions (F14; docs/authoring.md,
// "Recommendations").
//
// A lesson is { id, title, href, prerequisites: [id] }, in the order of the
// learning path. A state is the parsed learner state of progress.js:
//   { lessons: { "<id>": { completed, selfCheck: { done, attempts } } },
//     ignored: ["<id>"] }
// Each suggestion is { lesson, kind, reason } with the reason in words.

export const LIMIT = 3;

function names(lessons) {
  const titles = lessons.map((lesson) => lesson.title);
  return titles.length < 2
    ? titles.join("")
    : titles.slice(0, -1).join(", ") + " and " + titles[titles.length - 1];
}

// Rules in order of rank. A lesson gets the suggestion of the first rule that
// applies to it. Each returns the reason for a lesson, or null.
const RULES = [
  {
    // The reader completed a lesson without a prerequisite of it.
    kind: "prerequisite",
    reason(lesson, context) {
      if (context.completed(lesson)) {
        return null;
      }
      const built = context.lessons.filter(
        (later) => context.completed(later) && later.prerequisites.includes(lesson.id)
      );
      return built.length === 0
        ? null
        : `You completed ${names(built)}, which builds on this lesson, and you have not marked it as completed.`;
    },
  },
  {
    // The self-check was tried and has not been answered correctly yet.
    kind: "retry",
    reason(lesson, context) {
      const check = context.entry(lesson)?.selfCheck;
      if (context.completed(lesson) || !check || check.done || check.attempts < 1) {
        return null;
      }
      const times = check.attempts === 1 ? "once" : `${check.attempts} times`;
      return `You checked an answer to its self-check ${times} without getting it right. Try it again, or work through the lesson's exercises.`;
    },
  },
  {
    // Everything the lesson builds on is completed.
    kind: "next",
    reason(lesson, context) {
      if (context.completed(lesson)) {
        return null;
      }
      const needed = lesson.prerequisites
        .map((id) => context.lessons.find((other) => other.id === id))
        .filter(Boolean);
      if (needed.some((other) => !context.completed(other))) {
        return null;
      }
      return needed.length === 0
        ? "It has no prerequisites, and you have not completed it."
        : `You completed ${names(needed)}, which ${needed.length === 1 ? "is its prerequisite" : "are its prerequisites"}.`;
    },
  },
];

// The suggestions for a state, best first, at most LIMIT. Without a stored
// result there are none: the page then shows the plain learning path.
export function recommend(lessons, state) {
  const results = state?.lessons ?? {};
  const known = new Set(lessons.map((lesson) => lesson.id));
  if (!Object.keys(results).some((id) => known.has(id))) {
    return [];
  }
  const ignored = new Set(state.ignored ?? []);
  const context = {
    lessons,
    entry: (lesson) => results[lesson.id],
    completed: (lesson) => results[lesson.id]?.completed === true,
  };
  const found = [];
  for (const rule of RULES) {
    for (const lesson of lessons) {
      if (ignored.has(lesson.id) || found.some((item) => item.lesson.id === lesson.id)) {
        continue;
      }
      const reason = rule.reason(lesson, context);
      if (reason !== null) {
        found.push({ lesson, kind: rule.kind, reason });
      }
    }
  }
  return found.slice(0, LIMIT);
}
