"""Lesson A4: an agent designs the measurements that tell two models of drag
apart.

A block slides on a table and slows down. Two models of the drag compete: linear
drag, which gives ``v = v0 exp(-g t)``, and quadratic drag, which gives
``v = v0 / (1 + k v0 t)`` (``pbc.mechanics.drag``). The agent may measure the
speed after a time ``t`` for a start speed ``v0``, with a noisy instrument and a
budget of measurements. It must choose the pairs ``(v0, t)`` that separate the
models. The harness, not the agent, scores the design and decides what the
measurements show (``pbc.agents.design``).

The instrument is simulated: it is the quadratic model with a hidden drag
constant plus Gaussian noise that is a function of the arguments, so the same
arguments give the same reading and a replay is exact. The page says so.

Run it live on your machine (needs ``OPENAI_API_KEY`` and the optional
dependency)::

    uv run --extra openai python -m pbc.agents.design_lab --rig full

Record the replay fixture of a rig from a live run (maintainer)::

    uv run --extra openai python -m pbc.agents.design_lab --rig full --record
"""

import argparse
import datetime
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from pbc.agents.design import Assessment, ExperimentalDesign, Model, judge
from pbc.agents.loop import Step, Transcript, run
from pbc.agents.replay import Recording, load_recording, replay, save_recording
from pbc.agents.secrets import Secret, redact
from pbc.agents.tools import Allowlist, Parameter, Tool

MASS = 2.0  # kg
HIDDEN_C = 0.1  # kg/m, quadratic drag of the simulated block
NOISE = 0.1  # m/s, standard uncertainty of one reading
BUDGET = 8  # measurements per rig
MAX_STEPS = 12  # model messages per run
# A recomputed reading may differ from the recorded one by this much: it is a
# deterministic function of the arguments, so this covers only last digits.
TOLERANCE = 1e-6
THRESHOLD = 25.0  # chi-square difference that counts as telling the models apart

TOOL = "measure_speed"
RESULT = "speed"
TIMES = (0.1, 10.0)
REPEATS = 3

SYSTEM = (
    "You are a careful experimenter who designs measurements. You can only use"
    " the tools you are given, and only a limited number of measurements. Choose"
    " each measurement so that it helps to tell the two models apart, and say"
    " why. At the end say which model the measurements favour and how sure you"
    " are, or say that they do not tell the models apart. Do not say that a"
    " model is true because it fits."
)


def linear(v0, t, g):
    """Linear drag: the speed falls exponentially, whatever the start speed."""
    return v0 * np.exp(-g * t)


def quadratic(v0, t, k):
    """Quadratic drag: the faster block loses speed faster."""
    return v0 / (1.0 + k * v0 * t)


LINEAR = Model("linear drag", ("g",), linear, (0.3,))
QUADRATIC = Model("quadratic drag", ("k",), quadratic, (0.05,))
# Nominal parameters of the score, fixed before any measurement: both models
# are made to give the same speed (5 m/s) for a block started at 10 m/s and
# measured after 2 s, the calibration run of the rig.
NOMINAL = {
    LINEAR.name: (np.log(2.0) / 2.0,),
    QUADRATIC.name: (0.05,),
}


def reading(initial_speed: float, time: float, repeat: int) -> float:
    """The simulated instrument: the quadratic model of the hidden block plus
    noise drawn from a generator seeded by the arguments."""
    seed = [round(initial_speed * 1000), round(time * 1000), repeat]
    noise = np.random.default_rng(seed).normal(0.0, NOISE)
    return float(quadratic(initial_speed, time, HIDDEN_C / MASS) + noise)


def _measure(initial_speed: float, time: float, repeat: int) -> dict[str, float]:
    return {RESULT: reading(initial_speed, time, repeat)}


@dataclass(frozen=True)
class Rig:
    """One experiment put to the agent: the design, the fastest start the rig
    allows, the task text, and the fixture."""

    design: ExperimentalDesign
    maximum_speed: float  # m/s
    task: str
    fixture: str  # the file next to the page


def _design(statement: str) -> ExperimentalDesign:
    return ExperimentalDesign(
        statement=statement,
        tool=TOOL,
        inputs=("initial_speed", "time"),
        result=RESULT,
        sigma=NOISE,
        models=(LINEAR, QUADRATIC),
        nominal=NOMINAL,
        threshold=THRESHOLD,
        budget=BUDGET,
    )


def _task(statement: str, maximum_speed: float) -> str:
    return (
        f"{statement} Two models of the drag compete: linear drag, v = v0"
        " exp(-g t), and quadratic drag, v = v0 / (1 + k v0 t), with g and k"
        f" unknown. Each reading of the speed has a standard uncertainty of"
        f" {NOISE:g} m/s. Choose at most {BUDGET} measurements, with a start"
        f" speed of at most {maximum_speed:g} m/s, that tell the two models apart."
    )


_FULL = "A block of 2 kg slides on a table and slows down."
_SLOW = (
    "A block of 2 kg slides on a table and slows down; the launcher of this rig"
    " cannot start it faster than 2 m/s."
)
RIGS = {
    "full": Rig(_design(_FULL), 20.0, _task(_FULL, 20.0), "replay-full.json"),
    "slow": Rig(_design(_SLOW), 2.0, _task(_SLOW, 2.0), "replay-slow.json"),
}

LESSON = "site/lessons/agents-llm/04-an-experimental-design-agent"
RECORD_COMMAND = (
    "uv run --extra openai python -m pbc.agents.design_lab --rig {name}"
    " --record (with OPENAI_API_KEY set)"
)


def tools(maximum_speed: float = 20.0) -> Allowlist:
    """The allowlist of a rig: one function, bounded, with a budget of
    measurements. A new allowlist has a fresh budget."""
    return Allowlist(
        (
            Tool(
                name=TOOL,
                description=(
                    f"Start a block of {MASS:g} kg on a table at a given speed"
                    " and read its speed after a given time, with an"
                    f" instrument whose noise is {NOISE:g} m/s. The same"
                    " arguments give the same reading; a new value of repeat"
                    " gives an independent reading."
                ),
                parameters=(
                    Parameter(
                        "initial_speed",
                        "speed at the start, in m/s",
                        0.5,
                        maximum_speed,
                    ),
                    Parameter("time", "time after the start, in s", *TIMES),
                    Parameter(
                        "repeat",
                        "number of the repetition, for an independent reading",
                        1,
                        REPEATS,
                        integer=True,
                    ),
                ),
                function=_measure,
            ),
        ),
        budget=BUDGET,
    )


def replay_rig(
    name: str, directory: Path = Path()
) -> tuple[Recording, Transcript, Assessment]:
    """Load the fixture of rig ``name`` from ``directory``, replay it against
    the current code, and assess the replayed measurements."""
    rig = RIGS[name]
    recording = load_recording(directory / rig.fixture)
    allowlist = tools(rig.maximum_speed)
    transcript = replay(
        recording,
        allowlist,
        system=SYSTEM,
        task=rig.task,
        tolerance=TOLERANCE,
        max_steps=MAX_STEPS,
        rerecord=RECORD_COMMAND.format(name=name),
    )
    return recording, transcript, judge(rig.design, transcript, allowlist)


def _show(step: Step, *secrets: Secret) -> None:
    """Print a step; the loop removed the key already, this redacts once more."""
    if step.message.text:
        print(redact(step.message.text, *secrets))
    for call, result in zip(step.message.tool_calls, step.results, strict=False):
        print(
            redact(
                f"  {call.name}({call.arguments}) -> {dict(result.content)}", *secrets
            )
        )


def main(argv: list[str] | None = None) -> int:
    """The live entry point: ask the model, print the run and the assessment,
    optionally record. The key is the client's business, not this module's."""
    from pbc.agents.providers import PROVIDER, load_client

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--rig", choices=sorted(RIGS), required=True)
    parser.add_argument(
        "--record",
        action="store_true",
        help=f"write the run to {LESSON}/<fixture> as the replay fixture",
    )
    options = parser.parse_args(argv)
    rig = RIGS[options.rig]
    try:
        client = load_client(PROVIDER)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Task: {rig.task}\nModel: {client.model}\n")
    allowlist = tools(rig.maximum_speed)
    transcript = run(
        client,
        allowlist,
        SYSTEM,
        rig.task,
        MAX_STEPS,
        on_step=lambda step: _show(step, *client.secrets),
    )
    assessment = judge(rig.design, transcript, allowlist)
    print(f"\nAssessment (recomputed, not the model's words): {assessment.outcome}")
    print(f"  design score {assessment.score:.3g}; {assessment.reason}")
    if options.record:
        today = datetime.date.today().isoformat()
        path = Path(LESSON) / rig.fixture
        save_recording(path, transcript, today, *client.secrets)
        print(f"\nRecorded to {path}. Review it before you commit it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
