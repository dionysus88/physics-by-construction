"""Lesson A2: three review agents check a stepper and a faulty variant.

Each reviewer is one run of the loop of ADR 004 with its own system prompt and
its own allowlist over the checks of the scientific validation contract
(``docs/validation-contract.md``). A reviewer can run checks on two pieces of
code, called 1 and 2, and nothing else: it cannot read a file, write code, or
see the other reviewers. Both pieces claim first order and a bounded energy of
the oscillator. Piece 1 is the symplectic Euler stepper of the course; piece 2
is ``pbc.verification.faulty.explicit_euler_as_symplectic``, which has the
right order and loses the bounded energy.

What the build shows is decided by the recomputed tool results: ``verdicts``
reads them out of a replay, and ``resolve`` combines them. The words of a
reviewer are shown and never used to decide anything.

Run the reviewers live on your machine (needs ``OPENAI_API_KEY`` and the
optional dependency)::

    uv run --extra openai python -m pbc.agents.review_lab

Record the replay fixtures of the lesson from a live run (maintainer)::

    uv run --extra openai python -m pbc.agents.review_lab --record
"""

import argparse
import datetime
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from pbc.agents.loop import Step, Transcript, run
from pbc.agents.replay import Recording, load_recording, replay, save_recording
from pbc.agents.secrets import Secret, redact
from pbc.agents.tools import Allowlist, Parameter, Tool
from pbc.mechanics.dynamics import Stepper
from pbc.mechanics.integrators import symplectic_euler_step
from pbc.verification import checks
from pbc.verification.checks import CHECKS, Claim
from pbc.verification.faulty import explicit_euler_as_symplectic

# What both pieces of code claim: first order, and an oscillator energy that
# stays in a band.
CLAIM = Claim(order=1, bounded_energy=True)

# The pieces under review, by the number a reviewer uses. Nothing in a prompt
# or a tool says which one is wrong.
CANDIDATES: Mapping[int, Callable[[], Stepper]] = {
    1: lambda: symplectic_euler_step,
    2: lambda: explicit_euler_as_symplectic,
}

MAX_STEPS = 6  # model messages per reviewer
# A recomputed result may differ from the recorded one by this much, in
# relative and in absolute terms; the checks are deterministic.
TOLERANCE = 1e-6

DIRECTORY = "site/lessons/agents-llm/03-three-reviewers"
RECORD_COMMAND = (
    "uv run --extra openai python -m pbc.agents.review_lab --record"
    " (with OPENAI_API_KEY set)"
)

CANDIDATE = Parameter(
    "candidate", "the piece of code to check: 1 or 2", 1, len(CANDIDATES), integer=True
)
CHECK = Parameter(
    "check",
    "the check, by its place in the contract: 1 clock, 2 purity, 3 limits,"
    " 4 convergence-order, 5 bounded-energy",
    1,
    len(CHECKS),
    integer=True,
)
STEPS_PER_PERIOD = Parameter(
    "steps_per_period",
    "time steps in one period of the oscillator",
    20,
    800,
    integer=True,
)


# The checks by name, in the order of the contract. A name a model sends is
# never looked up here: tools hold the name, and ``CHECK`` bounds the number.
_CHECK_FUNCTIONS = dict(
    zip(
        CHECKS,
        (
            checks.check_clock,
            checks.check_purity,
            checks.check_limits,
            checks.check_convergence_order,
            checks.check_bounded_energy,
        ),
        strict=True,
    )
)


def _check_tool(name: str, description: str) -> Tool:
    """A tool that runs the check ``name`` on a candidate and returns the
    the numbers of rule 3 of the contract: measured, tolerance, passed. The
    name, the claim, and the reproducing call are those of the tool call."""

    def function(candidate: int) -> dict[str, float]:
        return _evidence(name, candidate)

    return Tool(
        name=f"check_{name.replace('-', '_')}",
        description=description,
        parameters=(CANDIDATE,),
        function=function,
    )


def _evidence(name: str, candidate: int) -> dict[str, float]:
    finding = _CHECK_FUNCTIONS[name](CANDIDATES[candidate], CLAIM)
    return {
        "measured": finding.measured,
        "tolerance": finding.tolerance,
        "passed": float(finding.passed),
    }


def _reproduce(check: int, candidate: int) -> dict[str, float]:
    return _evidence(CHECKS[check - 1], candidate)


def _error(candidate: int, steps_per_period: int) -> dict[str, float]:
    return {"error": checks.oscillator_error(CANDIDATES[candidate], steps_per_period)}


_CLOCK = _check_tool("clock", "A step of length dt advances the time by dt.")
_PURITY = _check_tool(
    "purity", "A step depends only on its arguments, not on earlier steps."
)
_LIMITS = _check_tool(
    "limits",
    "No force gives uniform motion; a constant force gives the exact velocity.",
)
_ORDER = _check_tool(
    "convergence-order",
    "The fitted order of the error against the exact oscillator;"
    " measured is the order, tolerance the allowed distance from the claim.",
)
_BOUNDED = _check_tool(
    "bounded-energy",
    "The energy band of the oscillator over 100 periods, last 5 periods"
    " against first 5; measured is the growth factor.",
)
_REPRODUCE = Tool(
    name="reproduce_check",
    description=(
        "Run one check of the contract on a candidate and return its evidence:"
        " measured value, tolerance, and passed (1 or 0)."
    ),
    parameters=(CHECK, CANDIDATE),
    function=_reproduce,
)
_ERROR = Tool(
    name="oscillator_error",
    description=(
        "The largest distance of the candidate from the exact oscillator over"
        " two periods, for a number of time steps per period."
    ),
    parameters=(CANDIDATE, STEPS_PER_PERIOD),
    function=_error,
)

SHARED = (
    "You review code against its claim. Both pieces of code, 1 and 2, claim to"
    " be a first-order method for Newton's second law whose energy, for the"
    " harmonic oscillator, stays in a band that does not grow. You can only use"
    " the tools you are given, and a tool is the only source of a result: do"
    " not give a verdict a tool did not produce. Report each check you ran with"
    " its measured value and tolerance, then say what you did not check."
)


@dataclass(frozen=True)
class Reviewer:
    """One reviewer: a role, a system prompt, a task, and its allowlist."""

    id: str
    role: str
    system: str
    task: str
    allowlist: Allowlist

    @property
    def fixture(self) -> str:
        return f"replay-{self.id}.json"


REVIEWERS = (
    Reviewer(
        "physics",
        "physical assumptions",
        SHARED
        + " Your part is the physics: does the code obey the motion it models and"
        " the conservation it claims?",
        "Check pieces 1 and 2 against the physical claim: no force and constant"
        " force give the exact motion, and the oscillator energy stays bounded."
        " Say which piece you would accept, and which assumption of the checks"
        " it rests on.",
        Allowlist((_LIMITS, _BOUNDED)),
    ),
    Reviewer(
        "numerics",
        "numerical implementation",
        SHARED + " Your part is the implementation: does a step behave as a step of a"
        " method of the claimed order must?",
        "Check pieces 1 and 2 as numerical methods: the clock, the purity of a"
        " step, and the order of convergence. Say which piece you would accept,"
        " and what your checks cannot see.",
        Allowlist((_CLOCK, _PURITY, _ORDER)),
    ),
    Reviewer(
        "evidence",
        "evidence",
        SHARED + " Your part is the evidence: reproduce the checks in the order of the"
        " contract and report them in its form, so that a reader can rerun them.",
        "Reproduce all five checks of the contract, in order, for pieces 1 and"
        " 2, and tabulate the error against the exact oscillator at 50, 100 and"
        " 200 steps per period. Say which piece the evidence supports, and what"
        " it does not cover.",
        Allowlist((_REPRODUCE, _ERROR)),
    ),
)


def replay_reviewer(reviewer: Reviewer, recording: Recording) -> Transcript:
    """Replay ``recording`` against the current checks."""
    return replay(
        recording,
        reviewer.allowlist,
        system=reviewer.system,
        task=reviewer.task,
        tolerance=TOLERANCE,
        max_steps=MAX_STEPS,
        rerecord=RECORD_COMMAND,
    )


def replay_fixtures(
    directory: Path = Path(),
) -> dict[str, tuple[Recording, Transcript]]:
    """Replay the fixture of every reviewer found in ``directory``, by id."""
    replays = {}
    for reviewer in REVIEWERS:
        recording = load_recording(directory / reviewer.fixture)
        replays[reviewer.id] = (recording, replay_reviewer(reviewer, recording))
    return replays


@dataclass(frozen=True)
class Verdict:
    """One recomputed check of one reviewer on one candidate."""

    reviewer: str
    candidate: int
    check: str
    measured: float
    tolerance: float
    passed: bool


def verdicts(reviewer: Reviewer, transcript: Transcript) -> list[Verdict]:
    """The checks a reviewer ran, from the recomputed results of its tools.

    The text of the model is not read. A call that was refused, and a tool
    that is not a check (``oscillator_error``), gives no verdict.
    """
    found = []
    for step in transcript.steps:
        for call, result in zip(step.message.tool_calls, step.results, strict=True):
            if not result.ok:
                continue
            if call.name == "reproduce_check":
                check = CHECKS[call.arguments["check"] - 1]
            elif call.name.startswith("check_"):
                check = call.name.removeprefix("check_").replace("_", "-")
            else:
                continue
            found.append(
                Verdict(
                    reviewer.id,
                    call.arguments["candidate"],
                    check,
                    result.content["measured"],
                    result.content["tolerance"],
                    bool(result.content["passed"]),
                )
            )
    return found


@dataclass(frozen=True)
class Resolution:
    """What the recomputed findings say about one candidate."""

    candidate: int
    failed: tuple[str, ...]  # checks some reviewer ran and the code failed
    flagged_by: tuple[str, ...]  # reviewers that ran a failing check
    clear_by: tuple[str, ...]  # reviewers that ran checks, all passed
    not_covered: tuple[str, ...]  # checks no reviewer ran
    conflicts: tuple[str, ...]  # checks two reviewers recomputed differently

    @property
    def rejected(self) -> bool:
        return bool(self.failed)

    @property
    def disagreement(self) -> bool:
        """Some reviewers found a failure and others, which ran other
        checks, did not."""
        return bool(self.flagged_by) and bool(self.clear_by)


def resolve(all_verdicts: list[Verdict], candidate: int) -> Resolution:
    """Combine the verdicts on ``candidate`` by one rule.

    A failed recomputed check stands, whoever else passed the code: a reviewer
    that did not run the check has no standing against it. A check that two
    reviewers recomputed with different outcomes is a conflict (the checks
    are deterministic, so it means the reviewers did not run the same check).
    """
    mine = [v for v in all_verdicts if v.candidate == candidate]
    outcomes: dict[str, set[bool]] = {}
    for verdict in mine:
        outcomes.setdefault(verdict.check, set()).add(verdict.passed)
    flagged = sorted({v.reviewer for v in mine if not v.passed})
    clear = sorted({v.reviewer for v in mine} - set(flagged))
    return Resolution(
        candidate=candidate,
        failed=tuple(c for c in CHECKS if False in outcomes.get(c, ())),
        flagged_by=tuple(flagged),
        clear_by=tuple(clear),
        not_covered=tuple(c for c in CHECKS if c not in outcomes),
        conflicts=tuple(c for c in CHECKS if len(outcomes.get(c, ())) > 1),
    )


class ReviewDisplay:
    """The verdicts and the resolution of the reviews, as a list for a page.

    Every line is built from recomputed results; no text of a model is in it.
    A list rather than a table: it wraps on a phone screen.
    """

    def __init__(self, transcripts: Mapping[str, Transcript]):
        self.verdicts = [
            verdict
            for reviewer in REVIEWERS
            for verdict in verdicts(reviewer, transcripts[reviewer.id])
        ]

    def resolution(self, candidate: int) -> Resolution:
        return resolve(self.verdicts, candidate)

    def _repr_markdown_(self) -> str:
        lines = []
        for candidate in CANDIDATES:
            resolution = self.resolution(candidate)
            lines.append(f"- **Piece {candidate}**")
            for reviewer in REVIEWERS:
                ran = [
                    v
                    for v in self.verdicts
                    if v.candidate == candidate and v.reviewer == reviewer.id
                ]
                shown = "; ".join(
                    f"`{v.check}` {'passed' if v.passed else '**failed**'}"
                    f" (measured {v.measured:.3g}, tolerance {v.tolerance:.3g})"
                    for v in ran
                )
                lines.append(f"    - {reviewer.role}: {shown}")
            if resolution.rejected:
                names = ", ".join(f"`{c}`" for c in resolution.failed)
                outcome = f"**rejected**, because of {names}"
            else:
                outcome = "**not rejected** by the checks that were run"
            if resolution.disagreement:
                outcome += (
                    ". The reviewers disagreed: "
                    + " and ".join(resolution.flagged_by)
                    + " found a failure that "
                    + " and ".join(resolution.clear_by)
                    + " did not see, because the checks they ran do not include it"
                )
            if resolution.not_covered:
                outcome += ". No reviewer ran " + ", ".join(
                    f"`{c}`" for c in resolution.not_covered
                )
            lines.append(f"    - resolution: {outcome}.")
        return "\n".join(lines) + "\n"


def _show(step: Step, *secrets: Secret) -> None:
    if step.message.text:
        print(redact(step.message.text, *secrets))
    for call, result in zip(step.message.tool_calls, step.results, strict=False):
        print(
            redact(
                f"  {call.name}({call.arguments}) -> {dict(result.content)}", *secrets
            )
        )


def main(argv: list[str] | None = None) -> int:
    """The live entry point: run the three reviewers one after the other and
    optionally record each run. The reviewers share nothing but the code."""
    from pbc.agents.providers import PROVIDER, load_client

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--record",
        action="store_true",
        help=f"write each run to {DIRECTORY}/replay-<reviewer>.json",
    )
    options = parser.parse_args(argv)
    try:
        client = load_client(PROVIDER)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    today = datetime.date.today().isoformat()
    for reviewer in REVIEWERS:
        print(f"\n== {reviewer.role} ({client.model}) ==\nTask: {reviewer.task}\n")
        transcript = run(
            client,
            reviewer.allowlist,
            reviewer.system,
            reviewer.task,
            MAX_STEPS,
            on_step=lambda step: _show(step, *client.secrets),
        )
        if options.record:
            path = Path(DIRECTORY) / reviewer.fixture
            save_recording(path, transcript, today, *client.secrets)
            print(f"\nRecorded to {path}. Review it before you commit it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
