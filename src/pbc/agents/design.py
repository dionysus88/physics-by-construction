"""Autonomous experimental design: the build scores the agent's design and
decides what its measurements show (Issue #128, on the harness of ADR 004).

Two models compete to describe a measured quantity. The agent chooses where to
measure, through an allowlist with a budget, so that the measurements tell the
models apart. It is not the agent that says whether they did. The harness takes
every measurement the agent ran, runs it again from its arguments, and:

- **scores the design** from its arguments alone: if one model were true, with
  its nominal parameters, how much worse would the best fit of the other model
  be on noise-free data at these points, in units of the measurement noise
  (``design_score``)? A design with a small score cannot separate the models
  whatever the noise does, and the agent's prose cannot change that;
- **fits both models** to the recomputed measurements with
  ``pbc.data.fit.fit_curve`` and compares their chi-square.

The outcome is **discriminated** only when one model fits the recomputed
measurements within what the noise allows and the other is worse by at least
``design.threshold`` in chi-square. That is a statement about the computation
the build ran, so it carries the claim type ``numerically-verified``
(``docs/authoring.md``), scoped to the measurements. Anything else is
**inconclusive**: it is not a result, has no claim type, and is never reported
as "the models are equal" or "the model is true". The parameter of the
preferred model comes with the interval of its fit, a statement about the model
that fits and not about the system measured.

The agent's prose is shown, labelled, and never read by the judge.
"""

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pbc.agents.loop import Transcript
from pbc.agents.tools import Allowlist, ToolRejected
from pbc.data.fit import FitResult, fit_curve

Array = NDArray[np.float64]

DISCRIMINATED = "discriminated"
INCONCLUSIVE = "inconclusive"
# A model fits when its chi-square is within this many standard deviations of
# the expectation for its degrees of freedom (sqrt(2 dof) for the chi-square).
FIT_SIGMAS = 3.0


@dataclass(frozen=True)
class Model:
    """A model of the measured quantity: ``function(x, t, *parameters)``, with
    where each fit starts."""

    name: str
    parameters: tuple[str, ...]
    function: Callable[..., Array]
    start: tuple[float, ...]
    bounds: tuple[float, float] = (0.0, np.inf)


@dataclass(frozen=True)
class ExperimentalDesign:
    """The question put to the agent.

    ``tool`` is measured at the two inputs ``inputs`` (arguments of the tool,
    for example the starting speed and the time) and returns ``result``, with
    standard uncertainty ``sigma``. ``nominal`` holds the parameters of each
    model that the score assumes when that model is the true one, chosen before
    any measurement. ``threshold`` is the chi-square difference that counts as
    telling the models apart. ``budget`` is the number of measurements.
    """

    statement: str
    tool: str
    inputs: tuple[str, str]
    result: str
    sigma: float
    models: tuple[Model, Model]
    nominal: Mapping[str, tuple[float, ...]]
    threshold: float
    budget: int


@dataclass(frozen=True)
class Measurement:
    """One measurement the judge ran again."""

    arguments: Mapping[str, float | int | str]
    value: float


@dataclass(frozen=True)
class ModelFit:
    """A model fitted to the recomputed measurements."""

    model: Model
    fit: FitResult

    @property
    def chi2(self) -> float:
        return self.fit.chi2

    @property
    def fits(self) -> bool:
        """The chi-square is within ``FIT_SIGMAS`` of its expectation."""
        dof = self.fit.dof
        return self.fit.chi2 <= dof + FIT_SIGMAS * math.sqrt(2 * dof)


@dataclass(frozen=True)
class Assessment:
    """What the build found out about the agent's design and measurements.

    ``fits`` is empty when too few measurements were recomputed to fit two
    models, or a fit did not converge; ``reason`` then says which.
    """

    design: ExperimentalDesign
    measurements: tuple[Measurement, ...]
    score: float  # of the design, from its arguments alone
    fits: tuple[ModelFit, ModelFit] | None
    reason: str

    @property
    def preferred(self) -> ModelFit | None:
        if self.fits is None or self.outcome != DISCRIMINATED:
            return None
        return min(self.fits, key=lambda f: f.chi2)

    @property
    def difference(self) -> float | None:
        """Chi-square of the worse model minus that of the better one."""
        if self.fits is None:
            return None
        return abs(self.fits[0].chi2 - self.fits[1].chi2)

    @property
    def outcome(self) -> str:
        if self.fits is None or not self._separated:
            return INCONCLUSIVE
        best = min(self.fits, key=lambda f: f.chi2)
        if not best.fits or not all(best.fit.identifiable):
            return INCONCLUSIVE
        return DISCRIMINATED

    @property
    def _separated(self) -> bool:
        difference = self.difference
        return difference is not None and difference >= self.design.threshold

    @property
    def claim_type(self) -> str | None:
        """``numerically-verified`` for a discrimination the build recomputed,
        and nothing for any other outcome."""
        return "numerically-verified" if self.outcome == DISCRIMINATED else None


def _inputs(
    design: ExperimentalDesign, points: Sequence[Mapping]
) -> tuple[Array, Array]:
    first, second = design.inputs
    return (
        np.array([p[first] for p in points], dtype=float),
        np.array([p[second] for p in points], dtype=float),
    )


def _fit(
    design: ExperimentalDesign,
    model: Model,
    points: Sequence[Mapping],
    values: Array,
    start: Sequence[float],
) -> FitResult:
    a, b = _inputs(design, points)

    def curve(index: Array, *parameters: float) -> Array:
        return model.function(a, b, *parameters)

    return fit_curve(
        curve,
        np.arange(len(values), dtype=float),
        values,
        start,
        sigma=design.sigma,
        names=model.parameters,
        bounds=model.bounds,
    )


def design_score(design: ExperimentalDesign, points: Sequence[Mapping]) -> float:
    """How well the design can separate the two models, from its points alone.

    For each model taken as true, with its nominal parameters, the noise-free
    values at ``points`` are fitted by the other model; the chi-square of that
    best fit, in units of ``design.sigma``, is how far apart the models stay
    there. The score is the smaller of the two directions: a design must
    separate the models whichever one is true. It uses no measured value.
    Fewer points than the larger model has parameters score 0.
    """
    needed = max(len(m.parameters) for m in design.models) + 1
    if len(points) < needed:
        return 0.0
    scores = []
    for truth, other in (design.models, design.models[::-1]):
        a, b = _inputs(design, points)
        clean = truth.function(a, b, *design.nominal[truth.name])
        fit = _fit(design, other, points, clean, other.start)
        scores.append(fit.chi2)
    return float(min(scores))


def measurements(
    design: ExperimentalDesign, transcript: Transcript, allowlist: Allowlist
) -> tuple[Measurement, ...]:
    """The distinct measurements of ``transcript``, run again.

    Each accepted call of the design's tool is validated and run with the
    function of ``allowlist``, not read from the transcript. A call with the
    arguments of an earlier one is the same measurement and counts once. A
    value that is not finite is not evidence (the validation contract: not
    measured is not passed). At most ``design.budget`` count.
    """
    tool = allowlist.tool(design.tool)
    seen: set[tuple] = set()
    found: list[Measurement] = []
    for step in transcript.steps:
        for call, result in zip(step.message.tool_calls, step.results, strict=True):
            if not result.ok or call.name != design.tool:
                continue
            if len(found) >= design.budget:
                return tuple(found)
            try:
                arguments = tool.validate(call.arguments)
            except ToolRejected:
                continue  # the allowlist could not have accepted it
            key = tuple(sorted(arguments.items()))
            if key in seen:
                continue
            value = float(tool.function(**arguments)[design.result])
            if not math.isfinite(value):
                continue
            seen.add(key)
            found.append(Measurement(arguments, value))
    return tuple(found)


def judge(
    design: ExperimentalDesign, transcript: Transcript, allowlist: Allowlist
) -> Assessment:
    """Score the design and compare the models on the recomputed measurements."""
    found = measurements(design, transcript, allowlist)
    points = [m.arguments for m in found]
    score = design_score(design, points)
    needed = max(len(m.parameters) for m in design.models) + 1
    if len(found) < needed:
        return Assessment(
            design,
            found,
            score,
            None,
            f"{len(found)} measurement(s) cannot tell two models apart: at least"
            f" {needed} are needed to fit them",
        )
    values = np.array([m.value for m in found])
    fits = tuple(
        ModelFit(model, _fit(design, model, points, values, model.start))
        for model in design.models
    )
    assert len(fits) == 2
    failed = [
        f.model.name
        for f in fits
        if any("did not converge" in w for w in f.fit.warnings)
    ]
    if failed:
        return Assessment(
            design,
            found,
            score,
            None,
            "the fit of " + ", ".join(failed) + " did not converge",
        )
    pair = (fits[0], fits[1])
    return Assessment(design, found, score, pair, _reason(design, pair))


def _reason(design: ExperimentalDesign, fits: tuple[ModelFit, ModelFit]) -> str:
    """Why the outcome is not a discrimination, in words, from the recomputed
    numbers; empty when it is one."""
    difference = abs(fits[0].chi2 - fits[1].chi2)
    best = min(fits, key=lambda f: f.chi2)
    if difference < design.threshold:
        return (
            f"the chi-square of the two models differs by {difference:.3g}, less"
            f" than the {design.threshold:g} that counts as telling them apart"
        )
    if not best.fits:
        return (
            f"{best.model.name} is the better model, but its chi-square"
            f" {best.chi2:.3g} for {best.fit.dof} degrees of freedom is too high"
            " for the noise: neither model describes the measurements"
        )
    if not all(best.fit.identifiable):
        return f"the data do not determine the parameter of {best.model.name}"
    return ""
