"""The content of a lesson's "Reproduce this" section."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from pbc.authoring.context import marker
from pbc.authoring.lean import LEAN_DIRECTORY
from pbc.authoring.repository import (
    REPOSITORY_ROOT,
    BuildCommit,
    build_commit,
    repository_url,
)
from pbc.authoring.website import PAGE_FILE, SITE_DIRECTORY, project_root


def _lesson_page(directory: Path) -> str:
    """Return the repository path of the lesson page in ``directory``."""
    if not (directory / PAGE_FILE).is_file():
        raise FileNotFoundError(f"no {PAGE_FILE} in {directory}")
    relative = directory.relative_to(project_root(directory)).as_posix()
    return f"{SITE_DIRECTORY}/{relative}/{PAGE_FILE}"


def _repository_files(kind: str, paths: Sequence[str]) -> tuple[str, ...]:
    for path in paths:
        if Path(path).is_absolute() or not (REPOSITORY_ROOT / path).is_file():
            raise FileNotFoundError(
                f"{kind} file {path!r} does not exist; name files relative to"
                " the repository root"
            )
    return tuple(paths)


@dataclass(frozen=True)
class Reproduction:
    """What a learner needs to regenerate a lesson page from a clone.

    As the result of a code cell it leaves a marker; the page the reader gets
    shows the commit, the files, and the commands, which the post-render step
    builds from the commit of the run (``pbc.authoring.context``).
    """

    page: str  # the lesson page, relative to the repository root
    code: tuple[str, ...]  # the code the page imports
    tests: tuple[str, ...]  # the tests of that code
    commit: BuildCommit
    repository: str

    @property
    def output(self) -> str:
        """The page the render command writes, relative to the repository root."""
        relative = Path(self.page).relative_to(SITE_DIRECTORY).with_suffix(".html")
        return f"{SITE_DIRECTORY}/_site/{relative.as_posix()}"

    @property
    def _lean_note(self) -> tuple[str, ...]:
        if "./scripts/check-lean.sh" not in self.commands:
            return ()
        return (
            "`./scripts/check-lean.sh` compiles the Lean proofs and checks them"
            " for `sorry` and axioms. The first run fetches the Mathlib build"
            " cache, which is large.",
            "",
        )

    @property
    def commands(self) -> tuple[str, ...]:
        """The commands, from cloning to rendering this page."""
        directory = self.repository.rsplit("/", 1)[-1]
        commands = [f"git clone {self.repository}.git", f"cd {directory}"]
        if self.commit.sha is not None:
            commands.append(f"git checkout {self.commit.sha}")
        commands.append("uv sync --locked")
        if any(path.startswith(f"{LEAN_DIRECTORY}/") for path in self.code):
            # The page reads the record this check leaves (pbc.authoring.lean).
            commands.append("./scripts/check-lean.sh")
        if self.tests:
            commands.append("uv run --locked pytest " + " ".join(self.tests))
        commands.append(f"uv run --locked quarto render {self.page}")
        return tuple(commands)

    def _link(self, path: str) -> str:
        if self.commit.sha is None:
            return f"`{path}`"
        return f"[`{path}`]({self.repository}/blob/{self.commit.sha}/{path})"

    def payload(self) -> dict:
        """What the region is built from, apart from the commit."""
        return {"page": self.page, "code": list(self.code), "tests": list(self.tests)}

    @classmethod
    def from_payload(
        cls, page: str, payload: dict, commit: BuildCommit, repository: str
    ) -> Reproduction:
        """The region of the lesson ``page`` (relative to the site) for ``commit``."""
        if payload["page"] != f"{SITE_DIRECTORY}/{page}":
            raise ValueError(f"the marker names the page {payload['page']!r}")
        return cls(
            page=payload["page"],
            code=_repository_files("code", payload["code"]),
            tests=_repository_files("test", payload["tests"]),
            commit=commit,
            repository=repository,
        )

    def _repr_markdown_(self) -> str:
        return marker(
            "reproduce",
            Path(self.page).relative_to(SITE_DIRECTORY).as_posix(),
            self.payload(),
        )

    def markdown(self) -> str:
        """The content of the section, for the commit this was built with."""
        sha = self.commit.sha
        if sha is None:
            built_from = (
                "This page was not built from a Git checkout, so the commit of"
                " its sources is unknown."
            )
        else:
            built_from = (
                f"This page was built from commit [`{sha}`]"
                f"({self.repository}/tree/{sha}) of the"
                f" [repository]({self.repository})."
            )
            if self.commit.dirty:
                built_from += (
                    " **The checkout had uncommitted changes, so that commit"
                    " does not hold exactly the files this page was built"
                    " from.**"
                )
        files = [f"- {self._link(self.page)}: this page, with every code cell."]
        for path in self.code:
            purpose = (
                "a Lean file the page shows"
                if path.startswith(f"{LEAN_DIRECTORY}/")
                else "code the cells import"
            )
            files.append(f"- {self._link(path)}: {purpose}.")
        files += [f"- {self._link(path)}: tests of that code." for path in self.tests]
        setup = self._link("docs/development.md")
        # The summary is what the first view shows; the listing is complete
        # but closed. Both are text in the page, so neither needs JavaScript.
        return "\n".join(
            [
                "::: {.reproduce}",
                built_from,
                "",
                "In a clone at that commit, with the dependencies installed,"
                " this command renders the page again:",
                "",
                "```{.bash .reproduce-summary-command}",
                self.commands[-1],
                "```",
                "",
                '<details class="reproduce-details">',
                "<summary>Files, tests, and every command</summary>",
                "",
                "The files behind it:",
                "",
                *files,
                "",
                f"With Git and uv installed (see {setup}), run:",
                "",
                "```{.bash .reproduce-commands}",
                *self.commands,
                "```",
                "",
                *self._lean_note,
                "The last command runs every code cell of this page again and"
                f" writes the result to `{self.output}`. Its numbers and figures"
                " match this page to the digits shown. Digits beyond those can"
                " differ between machines, because floating-point libraries"
                " differ; the site is built on Linux.",
                "",
                "</details>",
                ":::",
                "",
            ]
        )


def reproduce_this(*, code: Sequence[str], tests: Sequence[str] = ()) -> Reproduction:
    """Return the "Reproduce this" content for the lesson page being built.

    ``code`` and ``tests`` name the files behind the page, relative to the
    repository root: the modules its cells import and the tests of those
    modules. Call it from a cell of the lesson's ``index.qmd``; the page is
    the one in the directory the cell runs in.
    """
    return Reproduction(
        page=_lesson_page(Path.cwd().resolve()),
        code=_repository_files("code", code),
        tests=_repository_files("test", tests),
        commit=build_commit(),
        repository=repository_url(),
    )
