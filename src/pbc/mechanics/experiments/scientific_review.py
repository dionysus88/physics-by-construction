"""The experiment of the lesson "Three reviewers".

Three reviewers, each with its own allowlist of checks
(``pbc.agents.review_lab``), review two pieces of code that claim to be
symplectic Euler; their recorded runs are replayed and their verdicts are
taken from the recomputed checks. Run it as a program to write the figure
and numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.scientific_review out

The live run, which asks a model and needs its key, is a separate command
behind the optional dependency ``openai``: the module ``LIVE``, run with
``uv run --locked --no-dev --extra openai python -m pbc.agents.review_lab``.
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.agents import ModelMessage, ReplayMismatch, ToolCall
from pbc.agents import run as run_agent
from pbc.agents.display import RunDisplay
from pbc.agents.review_lab import (
    CANDIDATES,
    CLAIM,
    MAX_STEPS,
    REVIEWERS,
    TOLERANCE,
    ReviewDisplay,
    Verdict,
    replay_fixtures,
    replay_reviewer,
    resolve,
    verdicts,
)
from pbc.authoring.repository import REPOSITORY_ROOT
from pbc.experiment import Experiment, main
from pbc.verification import checks, oscillator_error, verify

# The live run of the lesson: a model, its key, and the extra openai.
LIVE = "pbc.agents.review_lab"

# The recorded reviews, next to the page that shows them.
LESSON = REPOSITORY_ROOT / "site/lessons/agents-llm/03-three-reviewers"


class Boaster:
    model = "a reviewer that does not tell the truth"
    secrets = ()

    def __init__(self):
        self.messages = [
            ModelMessage(
                "I will check the energy.",
                (ToolCall("1", "check_bounded_energy", {"candidate": 2}),),
            ),
            ModelMessage("Piece 2 passes every check, with a wide margin."),
        ]

    def complete(self, system, conversation, tools):
        return self.messages.pop(0)


def boasting_reviewer():
    """Exercise 1: a reviewer that runs one check and then claims the
    opposite of its result."""
    physics = REVIEWERS[0]
    transcript = run_agent(
        Boaster(), physics.allowlist, physics.system, physics.task, MAX_STEPS
    )
    print("what it said: ", transcript.steps[-1].message.text)
    for v in verdicts(physics, transcript):
        print(
            f"what it ran:   {v.check} on piece {v.candidate}:",
            "passed" if v.passed else "FAILED",
            f"(measured {v.measured:.1e}, tolerance {v.tolerance})",
        )


def stricter_check(replays):
    """Exercise 2: the replay of the physics reviewer against a check whose
    tolerance has changed."""
    physics = REVIEWERS[0]
    original = checks.EXACT
    checks.EXACT = 1e-30
    try:
        replay_reviewer(physics, replays["physics"][0])
    except ReplayMismatch as mismatch:
        print(mismatch)
    finally:
        checks.EXACT = original


def draw_review_evidence(replays) -> Figure:
    """The error of the two pieces against the steps per period, with the
    experiments the evidence reviewer ran."""
    counts = np.array([20, 40, 80, 160, 320, 640])
    colors = {1: "#00429d", 2: "#93003a"}
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for piece, build in CANDIDATES.items():
        ax.loglog(
            counts,
            [oscillator_error(build, n) for n in counts],
            color=colors[piece],
            label=f"piece {piece}",
        )
        asked = {}
        for step in replays["evidence"][1].steps:
            for call, result in zip(step.message.tool_calls, step.results, strict=True):
                if (
                    result.ok
                    and call.name == "oscillator_error"
                    and call.arguments["candidate"] == piece
                ):
                    asked[call.arguments["steps_per_period"]] = result.content["error"]
        ax.loglog(list(asked), list(asked.values()), "o", color=colors[piece])
    ax.set_xlabel("time steps per period")
    ax.set_ylabel("error")
    ax.legend()
    return fig


def every_check():
    """Exercise 3: every check of the claim on both pieces, without a
    reviewer."""
    for piece, build in CANDIDATES.items():
        for finding in verify(build, CLAIM):
            print(
                f"piece {piece}  {'pass' if finding.passed else 'FAIL'}"
                f"  {finding.check:18} {finding.detail}"
            )


def a_conflict():
    """Exercise 4: two reviewers that disagree on one check."""
    found = [
        Verdict("physics", 1, "limits", 7e-15, 1e-12, True),
        Verdict("evidence", 1, "limits", 3e-3, 1e-12, False),
    ]
    resolution = resolve(found, 1)
    print("rejected:", resolution.rejected, "| conflicts:", resolution.conflicts)


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    experiment.number("claim", f"{CLAIM}")

    # region: replay
    replays = replay_fixtures(LESSON)
    review = ReviewDisplay(
        {name: transcript for name, (_, transcript) in replays.items()}
    )
    growth = next(
        v.measured
        for v in review.verdicts
        if v.candidate == 2 and v.check == "bounded-energy"
    )
    # endregion: replay
    for name in ("physics", "numerics", "evidence"):
        experiment.display(f"{name}-run", RunDisplay(*replays[name]))
    experiment.display("review", review)
    experiment.number("growth", growth, ".1e")
    experiment.number("tolerance", TOLERANCE, "g")

    with experiment.capture("boasting-reviewer"):
        boasting_reviewer()
    with experiment.capture("stricter-check"):
        stricter_check(replays)
    experiment.figure("fig-review-evidence", partial(draw_review_evidence, replays))
    with experiment.capture("every-check"):
        every_check()
    with experiment.capture("a-conflict"):
        a_conflict()
    return experiment


if __name__ == "__main__":
    main(run)
