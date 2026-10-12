"""Analysis pipelines: parameter sweeps, repeated results, and a report that
is compared with a committed expectation.

A pipeline is a function from inputs to numbers. This module holds what every
pipeline needs and none should write again: ``sweep`` runs a function over the
values of one parameter, ``estimate`` turns repetitions into a mean with its
standard uncertainty, and ``Report`` lists the quantities of an analysis, each
with its unit and the number of decimals it is shown with. ``check_report``
renders the report and compares the text with a committed expectation, line by
line, so that two reports agree exactly when a reader sees the same numbers.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from pbc.data.uncertainty import standard_error

EXPECTED_DIR = Path(__file__).resolve().parents[3] / "reports" / "expected"


@dataclass(frozen=True)
class Sweep:
    """The results of a function for each value of one parameter.

    ``results[name][k]`` belongs to ``values[k]``.
    """

    parameter: str
    unit: str
    values: np.ndarray
    results: Mapping[str, np.ndarray]

    def argmax(self, name: str) -> float:
        """The parameter value at which the result ``name`` is largest."""
        return float(self.values[int(np.argmax(self.results[name]))])

    def rows(self, *names: str) -> list[tuple[float, ...]]:
        """One row of the parameter and the results ``names`` per value."""
        return [
            (float(v), *(float(self.results[n][k]) for n in names))
            for k, v in enumerate(self.values)
        ]


def sweep(
    parameter: str,
    values: Sequence[float],
    func: Callable[[float], Mapping[str, float]],
    *,
    unit: str = "",
) -> Sweep:
    """Evaluate ``func`` at each of ``values``; ``func`` returns named results.

    Every call has to return the same names, so that the sweep is a table.
    """
    grid = np.asarray(values, dtype=float)
    if grid.ndim != 1 or grid.size == 0:
        raise ValueError("a sweep needs a one-dimensional, non-empty list of values")
    answers = [dict(func(float(v))) for v in grid]
    names = tuple(answers[0])
    for answer in answers:
        if set(answer) != set(names):
            raise ValueError(
                "the function returned different results for different values"
            )
    results = {n: np.array([a[n] for a in answers], dtype=float) for n in names}
    return Sweep(parameter, unit, grid, results)


@dataclass(frozen=True)
class Estimate:
    """Mean of ``n`` repetitions with the standard uncertainty of the mean."""

    mean: float
    sigma: float
    n: int


def estimate(repetitions: Sequence[float]) -> Estimate:
    """The mean of independent repetitions and its standard error."""
    values = np.asarray(repetitions, dtype=float)
    return Estimate(
        mean=float(np.mean(values)),
        sigma=float(standard_error(values)),
        n=int(values.size),
    )


@dataclass(frozen=True)
class Quantity:
    """A result of an analysis, with how it is shown."""

    name: str
    value: float
    unit: str = ""
    sigma: float | None = None  # standard uncertainty, same unit
    decimals: int = 3

    def shown(self) -> str:
        """The value as a reader sees it: rounded, with its uncertainty and unit."""
        text = f"{self.value:.{self.decimals}f}"
        if self.sigma is not None:
            text += f" +/- {self.sigma:.{self.decimals}f}"
        if self.unit:
            text += f" {self.unit}"
        return text

    def render(self) -> str:
        return f"{self.name}: {self.shown()}"


@dataclass(frozen=True)
class Report:
    """The quantities of an analysis, in order, under a title."""

    title: str
    quantities: tuple[Quantity, ...] = field(default_factory=tuple)

    def with_quantity(self, quantity: Quantity) -> Report:
        names = [q.name for q in self.quantities]
        if quantity.name in names:
            raise ValueError(f"the report already has a quantity {quantity.name!r}")
        return Report(self.title, (*self.quantities, quantity))

    def add(
        self,
        name: str,
        value: float,
        unit: str = "",
        *,
        sigma: float | None = None,
        decimals: int = 3,
    ) -> Report:
        return self.with_quantity(Quantity(name, float(value), unit, sigma, decimals))

    def rows(self) -> list[tuple[str, str]]:
        """One ``(name, shown value)`` pair per quantity, for a table."""
        return [(q.name, q.shown()) for q in self.quantities]

    def render(self) -> str:
        """The report as text: the title, then one line per quantity."""
        lines = [self.title, *(q.render() for q in self.quantities)]
        return "\n".join(lines) + "\n"


class ReportMismatch(AssertionError):
    """A report differs from its committed expectation at displayed precision."""


def differences(report: Report, expected: str) -> list[str]:
    """What differs between the report as shown and the ``expected`` text.

    One message per line that is changed, missing, or new. Empty when a reader
    sees the same report.
    """
    shown = report.render().splitlines()
    wanted = expected.splitlines()
    out = []
    for k in range(max(len(shown), len(wanted))):
        got = shown[k] if k < len(shown) else None
        want = wanted[k] if k < len(wanted) else None
        if got != want:
            out.append(f"line {k + 1}: expected {want!r}, the build produced {got!r}")
    return out


def check_report(report: Report, path: Path) -> str:
    """Raise ``ReportMismatch`` unless ``path`` holds exactly what the report shows.

    Returns the rendered report, so a page can show what was compared. Update
    an expectation on purpose, with ``python -m pbc.data.reports --update``,
    and read the change in the diff.
    """
    if not path.is_file():
        raise ReportMismatch(f"no committed expectation at {path}")
    problems = differences(report, path.read_text(encoding="utf-8"))
    if problems:
        raise ReportMismatch(
            f"{path.name} differs from the report:\n" + "\n".join(problems)
        )
    return report.render()
