"""The experiment of the lesson "An agent runs an experiment".

The allowlist that stands between a language model and the projectile
simulation (``pbc.agents.projectile_lab``), and the replay of a recorded
run: every tool call of the recording runs again, without a model and
without a credential, and the evidence is checked independently. Run it as
a program to write the figures and numbers of the page:

    uv run --locked --no-dev python -m pbc.mechanics.experiments.agent_experiment out

The live run, which asks a model and needs its key, is a separate command
behind the optional dependency ``openai``: the module ``LIVE``, run with
``uv run --locked --no-dev --extra openai python -m pbc.agents.projectile_lab``.
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from scipy.constants import g

from pbc.agents import Allowlist, ReplayMismatch, Tool, ToolCall
from pbc.agents.display import AllowlistDisplay, RunDisplay
from pbc.agents.projectile_lab import (
    ANGLE,
    DRAG,
    FIXTURE,
    MASS,
    MAX_STEPS,
    SPEED,
    SYSTEM,
    TASK,
    TIME_STEP,
    TOLERANCE,
    replay_fixture,
    tools,
)
from pbc.agents.replay import replay
from pbc.authoring import diagrams
from pbc.authoring.repository import REPOSITORY_ROOT
from pbc.experiment import Experiment, main
from pbc.mechanics.projectile import projectile_range

# The live run of the lesson: a model, its key, and the extra openai.
LIVE = "pbc.agents.projectile_lab"

# The recorded run, next to the page that shows it.
LESSON = (REPOSITORY_ROOT / FIXTURE).parent


def draw_tool_flow() -> Figure:
    """The model, the harness, the allowlist, and the simulation, as a
    sketch."""
    fig, ax = diagrams.canvas(6.4, 3.0, (-0.2, 12.6), (-1.6, 3.4))
    names = (("model", 0), ("harness", 1), ("allowlist", 2), ("simulation", 3))
    centres = {name: (1.1 + 3.4 * i, 2.0) for name, i in names}
    for name, _ in names:
        diagrams.state_box(
            ax,
            centres[name],
            name,
            width=2.2,
            height=0.9,
            colour=0 if name == "model" else 1,
        )
    for left, right, label in (
        ("model", "harness", "tool call"),
        ("harness", "allowlist", "name, bounds"),
        ("allowlist", "simulation", "only if it passes"),
    ):
        (x0, y), (x1, _) = centres[left], centres[right]
        diagrams.arrow(ax, (x0 + 1.15, y), (x1 - 1.15, y), colour=1)
        diagrams.text(
            ax, ((x0 + x1) / 2 + (0.0 if left != "model" else 0.9), y + 0.65), label
        )
    diagrams.line(ax, [(2.8, 3.1), (2.8, -0.9)], colour="#57606a", linestyle=":")
    diagrams.text(ax, (2.6, 3.2), "untrusted", ha="right", colour="#57606a")
    diagrams.text(ax, (3.0, 3.2), "trusted", ha="left", colour="#57606a")
    back = -0.4
    diagrams.line(
        ax,
        [
            (centres["simulation"][0], 1.5),
            (centres["simulation"][0], back),
            (centres["model"][0] + 0.6, back),
        ],
        colour=0,
        linestyle="--",
    )
    diagrams.arrow(
        ax,
        (centres["model"][0] + 0.6, back),
        (centres["model"][0] + 0.6, 1.5),
        colour=0,
        linestyle="--",
    )
    diagrams.text(ax, (6.3, back - 0.4), "result, as text", colour=0)
    diagrams.arrow(
        ax,
        (centres["allowlist"][0] - 0.4, 1.5),
        (centres["harness"][0] + 0.4, 1.5),
        colour=0,
        linestyle="--",
    )
    diagrams.text(
        ax, (centres["harness"][0] + 1.7, 0.95), "rejected, with a reason", colour=0
    )
    fig.tight_layout()
    return fig


def misbehaving_calls(experiment: Experiment) -> None:
    """Six calls that a misbehaving model might send, through the allowlist;
    record the table."""
    allowlist = tools()
    attempts = [
        ToolCall("1", "range_with_drag", {"speed": 25, "angle": 40, "dt": 0.01}),
        ToolCall("2", "os.system", {"command": "echo hello"}),
        ToolCall("3", "range_with_drag", {"speed": 25, "angle": 40, "dt": 0.0}),
        ToolCall("4", "range_with_drag", {"speed": 25, "angle": 40}),
        ToolCall("5", "range_with_drag", {"speed": "25", "angle": 40, "dt": 0.01}),
        ToolCall("6", "range_without_drag", {"speed": 25, "angle": 40, "code": "1+1"}),
    ]
    rows = []
    for attempt in attempts:
        result = allowlist.dispatch(attempt)
        shown = ", ".join(
            f"{key}={value!r}" for key, value in attempt.arguments.items()
        )
        rows.append(
            (
                attempt.name,
                shown,
                result.content["range_m"] if result.ok else None,
                "ran" if result.ok else result.content["error"],
            )
        )
    experiment.table(
        "misbehaving-calls",
        rows,
        [
            ("tool the model named", "", ""),
            ("arguments", "", ""),
            ("range", "m", ".3f"),
            ("outcome", "", ""),
        ],
        "Six calls that a misbehaving model might send, and what the allowlist did "
        "with each; the range is empty where nothing ran.",
    )


def draw_replay_check() -> Figure:
    """What the replay compares, as a sketch."""
    fig, ax = diagrams.canvas(6.4, 3.4, (-0.2, 12.6), (-1.0, 4.4))
    diagrams.state_box(
        ax, (1.4, 3.4), "recorded messages", width=2.8, height=0.8, colour=0
    )
    diagrams.state_box(
        ax, (1.4, 0.6), "recorded results", width=2.8, height=0.8, colour=0
    )
    diagrams.state_box(
        ax, (5.4, 3.4), "allowlist + simulation", width=3.2, height=0.8, colour=1
    )
    diagrams.state_box(ax, (7.4, 0.6), "compare", width=2.0, height=0.8, colour=2)
    diagrams.state_box(ax, (11.2, 2.2), "page", width=1.8, height=0.8, colour=1)
    diagrams.state_box(ax, (11.2, 0.0), "build fails", width=1.8, height=0.8, colour=3)
    diagrams.arrow(ax, (2.8, 3.4), (3.8, 3.4), colour=0)
    diagrams.text(ax, (3.3, 3.9), "same calls", colour=0)
    diagrams.arrow(ax, (5.4, 3.0), (7.0, 1.0), colour=1)
    diagrams.text(ax, (6.9, 2.3), "new results", ha="left", colour=1)
    diagrams.arrow(ax, (2.8, 0.6), (6.4, 0.6), colour=0)
    diagrams.arrow(ax, (8.4, 0.9), (10.3, 2.0), colour=1)
    diagrams.text(ax, (8.9, 1.9), "agree", ha="left", colour=1)
    diagrams.arrow(ax, (8.4, 0.4), (10.3, 0.1), colour=3)
    diagrams.text(ax, (9.3, -0.35), "differ", colour=3)
    diagrams.text(
        ax, (1.4, 2.0), "the words are shown,\nnever compared", colour="#57606a"
    )
    fig.tight_layout()
    return fig


def rough_ball(recording) -> None:
    """The replay against a ball with one per cent more drag, which the
    comparison of the results must catch."""
    original = tools()
    rough = Allowlist(
        (
            Tool(
                "range_with_drag",
                "rough ball",
                (SPEED, ANGLE, TIME_STEP),
                lambda speed, angle, dt: {
                    "range_m": projectile_range(speed, angle, MASS, 1.01 * DRAG, dt)
                },
            ),
            original.tools[1],
        )
    )

    try:
        replay(
            recording,
            rough,
            system=SYSTEM,
            task=TASK,
            tolerance=TOLERANCE,
            max_steps=MAX_STEPS,
            rerecord="uv run --extra openai python -m pbc.agents.projectile_lab"
            " --record",
        )
    except ReplayMismatch as mismatch:
        print(mismatch)


def draw_agent_evidence(transcript) -> Figure:
    """The ranges the agent asked for at a fine step, on an independent
    scan."""
    fine = 0.002
    angles = np.arange(30.0, 50.5, 1.0)
    scan = [projectile_range(25.0, a, MASS, DRAG, fine) for a in angles]

    asked = {}
    for step in transcript.steps:
        for call, result in zip(step.message.tool_calls, step.results, strict=True):
            if (
                result.ok
                and call.name == "range_with_drag"
                and call.arguments["dt"] <= fine
            ):
                asked[call.arguments["angle"]] = result.content["range_m"]

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(angles, scan, color="#00429d", label="scan, dt = 0.002 s")
    ax.plot(
        list(asked),
        list(asked.values()),
        "o",
        color="#93003a",
        label="asked by the agent",
    )
    ax.set_xlabel("launch angle (degrees)")
    ax.set_ylabel("range (m)")
    ax.legend()
    return fig


def agent_conclusion(experiment: Experiment, transcript):
    """The ranges the agent asked for at its smallest step, and an
    independent scan around its best two angles; record the table of the
    scan and return the bracket and its best angle, in degrees."""
    smallest = min(
        call.arguments["dt"]
        for step in transcript.steps
        for call in step.message.tool_calls
        if call.name == "range_with_drag"
    )
    at_smallest = {}
    for step in transcript.steps:
        for call, result in zip(step.message.tool_calls, step.results, strict=True):
            if (
                result.ok
                and call.name == "range_with_drag"
                and call.arguments["dt"] == smallest
            ):
                at_smallest[call.arguments["angle"]] = result.content["range_m"]

    best_two = sorted(sorted(at_smallest, key=at_smallest.get)[-2:])
    bracket_low, bracket_high = best_two
    grid = np.arange(bracket_low - 2.0, bracket_high + 2.0 + 1e-9, 0.25)
    grid_ranges = [projectile_range(25.0, a, MASS, DRAG, smallest) for a in grid]
    best_angle = grid[int(np.argmax(grid_ranges))]
    best_range = max(grid_ranges)
    range_at_45 = projectile_range(25.0, 45.0, MASS, DRAG, smallest)

    experiment.table(
        "agent-conclusion",
        [
            ("best angle of the scan", best_angle, "degrees"),
            ("range at the best angle", best_range, "m"),
            ("range at 45 degrees", range_at_45, "m"),
            ("gain over 45 degrees", best_range - range_at_45, "m"),
            (
                "gain over 45 degrees",
                100 * (best_range - range_at_45) / range_at_45,
                "per cent",
            ),
        ],
        [("quantity", "", ""), ("value", "", ".4g"), ("unit", "", "")],
        "An independent scan of the same simulation at the agent's smallest step, "
        "in steps of a quarter of a degree.",
    )
    return bracket_low, bracket_high, best_angle


def step_bounds(experiment: Experiment) -> None:
    """Exercise 1: the range at forty degrees with the smallest and the
    largest step the allowlist accepts; record the table."""
    allowlist = tools()
    fine = allowlist.dispatch(
        ToolCall("a", "range_with_drag", {"speed": 25, "angle": 40, "dt": 0.001})
    )
    coarse = allowlist.dispatch(
        ToolCall("b", "range_with_drag", {"speed": 25, "angle": 40, "dt": 0.05})
    )
    experiment.table(
        "step-bounds",
        [
            ("smallest allowed step", 0.001, fine.content["range_m"]),
            ("largest allowed step", 0.05, coarse.content["range_m"]),
            ("difference", None, coarse.content["range_m"] - fine.content["range_m"]),
        ],
        [("step", "", ""), ("time step", "s", ".3f"), ("range", "m", ".3f")],
        "The range of the throw at forty degrees with the smallest and the largest "
        "time step the allowlist accepts.",
    )


def new_tool(experiment: Experiment) -> None:
    """Exercise 2: a new tool for the flight time, called inside and outside
    its bounds; record the table."""
    flight_time = Tool(
        "flight_time_without_drag",
        "Flight time in seconds of the same throw in vacuum.",
        (SPEED, ANGLE),
        lambda speed, angle: {
            "time_s": float(2 * speed * np.sin(np.radians(angle)) / g)
        },
    )
    extended = Allowlist((*tools().tools, flight_time))
    rows = []
    for angle in (90, 60):
        result = extended.dispatch(
            ToolCall("c", "flight_time_without_drag", {"speed": 25, "angle": angle})
        )
        rows.append(
            (
                angle,
                "ran" if result.ok else "rejected",
                result.content["time_s"] if result.ok else None,
                "" if result.ok else result.content["error"],
            )
        )
    experiment.table(
        "new-tool",
        rows,
        [
            ("angle", "degrees", "d"),
            ("outcome", "", ""),
            ("flight time", "s", ".3f"),
            ("reason", "", ""),
        ],
        "The new tool called with an angle outside its bounds and with one inside "
        "them.",
    )


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    experiment.number("max-steps", MAX_STEPS)
    experiment.number("mass-g", MASS * 1000, "g")
    experiment.number("drag", DRAG, ".3g")
    experiment.figure("fig-tool-flow", draw_tool_flow)
    experiment.display("allowlist", AllowlistDisplay(tools()))
    misbehaving_calls(experiment)

    # region: replay
    recording, transcript = replay_fixture(LESSON)
    experiment.display("run", RunDisplay(recording, transcript))
    # endregion: replay
    experiment.number("model", recording.model)
    experiment.number("recorded", recording.recorded)
    experiment.figure("fig-replay-check", draw_replay_check)
    experiment.number("tolerance", TOLERANCE, "g")
    with experiment.capture("rough-ball"):
        rough_ball(recording)

    experiment.figure("fig-agent-evidence", partial(draw_agent_evidence, transcript))
    bracket_low, bracket_high, best_angle = agent_conclusion(experiment, transcript)
    experiment.number("bracket-low", bracket_low, ".0f")
    experiment.number("bracket-high", bracket_high, ".0f")
    experiment.number("best-angle", best_angle, ".2f")
    step_bounds(experiment)
    new_tool(experiment)
    return experiment


if __name__ == "__main__":
    main(run)
