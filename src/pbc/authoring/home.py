"""The "published and planned" section and the examples of the home page.

What the home page says is published comes from the lesson front matter, read
with the same code as the learning path, so a number or a title on the home
page cannot differ from the lessons. What is planned comes from the
curriculum file (``site/curriculum.yaml``, ADR 013): the courses and the
method paths of the reference curriculum with their published and planned
counts. A planned item is labelled planned and is never a link.
"""

from dataclasses import dataclass
from pathlib import Path

from pbc.authoring.path import COURSES, LearningPath, _href, _link
from pbc.authoring.website import PAGE_FILE, project_root

HOME_PAGE = PAGE_FILE

# The one published lesson that each activity points to, by lesson id.
CONSTRUCT_EXAMPLE = "numerical-integrators"
INVESTIGATE_EXAMPLE = "agent-experiment"
VERIFY_EXAMPLE = "proving-what-the-simulation-showed"


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


@dataclass(frozen=True)
class HomeContent:
    path: LearningPath
    page: str = HOME_PAGE

    def example(self, lesson_id: str) -> str:
        """A link to the published lesson ``lesson_id``."""
        return _link(self.page, self.path.lesson(lesson_id))

    def published(self) -> str:
        path = self.path
        lines = [
            f"The site publishes {_count(len(path.lessons), 'lesson')} in"
            f" {_count(len(path.strands), 'strand')}. A lesson appears here"
            " only after it passes verification.",
            "",
        ]
        for course in path.courses:
            lessons = path.in_course(course)
            core = [lesson for lesson in lessons if lesson.strand == course.id]
            extensions = len(lessons) - len(core)
            lines.append(
                f"The {course.title} course is published with"
                f" {_count(len(core), 'core lesson')} and"
                f" {_count(extensions, 'extension')}"
                f" ([by course]({_href(self.page, 'path/index.qmd', 'courses')}))."
            )
            lines.append("")
        for strand in path.strands:
            lessons = path.in_strand(strand)
            lines.append(
                f"{strand.title}: "
                + "; ".join(_link(self.page, lesson) for lesson in lessons)
                + "."
            )
            lines.append("")
        lines.append(
            "See the [learning path](" + _href(self.page, "path/index.qmd") + ")"
            " for every lesson with its difficulty and prerequisites, and"
            " [by method](" + _href(self.page, "path/index.qmd", "methods") + ")"
            " for the paths of simulation, LLM agents, agent-based modelling,"
            " and formal proofs, or [by method path]("
            + _href(self.page, "path/index.qmd", "paths")
            + ") for the four paths of the reference curriculum."
        )
        return "\n".join(lines)

    def planned(self) -> str:
        path = self.path
        curriculum = path.curriculum
        lines = [
            "Planned means not published. No date is promised. The reference"
            f" curriculum plans {_count(len(curriculum.slots), 'lesson')}: those"
            " of eight courses and four method paths, and one proof. The"
            " published count of an item is the lessons that exist; a planned"
            " lesson has no page and is not part of it.",
            "",
        ]
        for course in COURSES:
            published = _count(len(path.in_course(course)), "lesson")
            lines.append(
                f"- {course.title}, course: {published}"
                f" published, {len(path.planned_in_course(course))} planned."
            )
        for method_path in path.paths:
            lines.append(
                f"- {method_path.title}, method path:"
                f" {_count(len(path.in_path(method_path)), 'lesson')} published,"
                f" {len(path.planned_in_path(method_path))} planned."
            )
        return "\n".join(lines)


def home_content() -> HomeContent:
    """Return the generated parts of the home page being built."""
    site = project_root(Path.cwd().resolve())
    return HomeContent(LearningPath.read(site))
