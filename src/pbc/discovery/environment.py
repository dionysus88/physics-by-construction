"""A physics environment with a hidden truth (F65, ADR 004).

An environment wraps a model of ``pbc.mechanics`` as a system an agent, or a
baseline, can only probe: it sets the **controls** within their bounds and
reads one noisy **observation**, for as long as the **budget** lasts. The
law that produced the observation, its parameters, and the settings held out
for scoring belong to the environment. No public attribute or method returns
them; the only thing that uses them is the judge's ``held_out_error``, which
returns one number about a claim and nothing about the law.

The noise is a function of the seed and the controls, so the same probe gives
the same reading and a replay is exact.
"""

import hashlib
import math
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass

import numpy as np

from pbc.mechanics.dynamics import State
from pbc.mechanics.oscillator import harmonic_motion
from pbc.mechanics.projectile import drag_free_range


@dataclass(frozen=True)
class Control:
    """A quantity the experimenter sets, or a parameter of a claim."""

    name: str
    unit: str
    low: float
    high: float
    description: str


@dataclass(frozen=True)
class Observation:
    """The quantity read, with the standard deviation of its noise."""

    name: str
    unit: str
    sigma: float
    description: str


class Environment(ABC):
    """A system to probe. Subclasses declare ``controls``, ``observation``, and
    ``claim`` (the parameters of the family of laws a claim is made in), and
    implement ``_law`` (the truth) and ``predict`` (the family)."""

    name: str
    controls: tuple[Control, ...]
    observation: Observation
    claim: tuple[Control, ...]
    # Settings outside the bounds of the controls, never probed by the agent.
    _held_out: tuple[Mapping[str, float], ...]
    # Public: the form of the family a claim is made in, and where the
    # baselines start their fits.
    family: str
    starts: tuple[tuple[float, ...], ...]

    def __init__(self, *, budget: int = 30, seed: int = 0):
        if budget < 1:
            raise ValueError(f"the budget must be at least 1, got {budget}")
        self.budget = budget
        self.seed = seed
        self._used = 0

    @property
    def used(self) -> int:
        return self._used

    @property
    def remaining(self) -> int:
        return self.budget - self._used

    def reset(self) -> None:
        """Start a new episode: the budget is whole again. The truth and the
        noise stay as they are."""
        self._used = 0

    def measure(self, **controls: float) -> dict[str, float]:
        """One probe: the observation at ``controls``, with noise.

        Raises ``ValueError`` for a missing, unknown, or out-of-bounds control
        and ``RuntimeError`` when the budget is spent; neither costs anything.
        """
        settings = self._validated(controls)
        if self._used >= self.budget:
            raise RuntimeError(f"the budget of {self.budget} probes is spent")
        self._used += 1
        value = self._law(settings) + self.observation.sigma * self._noise(settings)
        return {self.observation.name: float(value)}

    def held_out_error(self, claim: Mapping[str, float]) -> float:
        """The error of ``claim`` on the held-out settings: see
        ``score_predictor``."""
        return self.score_predictor(lambda s: self.predict(claim, s))

    def score_predictor(
        self, predictor: Callable[[Mapping[str, float]], float]
    ) -> float:
        """The root-mean-square error of ``predictor`` on the held-out
        settings, against the noise-free law and relative to the scale of the
        observation there; ``inf`` if a prediction is not a number.

        This is the judge's call. It gives one number about a prediction and
        is in no allowlist."""
        try:
            predicted = np.array([predictor(s) for s in self._held_out], dtype=float)
        except ArithmeticError, ValueError, TypeError, KeyError:
            return math.inf
        if not np.all(np.isfinite(predicted)):
            return math.inf
        truth = np.array([self._law(s) for s in self._held_out])
        scale = np.array([self._scale(s) for s in self._held_out])
        return float(np.sqrt(np.mean(((predicted - truth) / scale) ** 2)))

    def _scale(self, settings: Mapping[str, float]) -> float:
        """What an error is relative to: the size of the observation."""
        return abs(self._law(settings))

    @abstractmethod
    def _law(self, settings: Mapping[str, float]) -> float:
        """The noise-free observation. Private: this is the truth."""

    @abstractmethod
    def predict(
        self, claim: Mapping[str, float], settings: Mapping[str, float]
    ) -> float:
        """The observation a claim, as parameters of the public family,
        predicts at ``settings``."""

    def _validated(self, controls: Mapping[str, float]) -> dict[str, float]:
        declared = {c.name: c for c in self.controls}
        unknown = sorted(set(controls) - set(declared))
        if unknown:
            raise ValueError(f"unknown controls: {', '.join(unknown)}")
        missing = sorted(set(declared) - set(controls))
        if missing:
            raise ValueError(f"missing controls: {', '.join(missing)}")
        for name, control in declared.items():
            value = controls[name]
            if not math.isfinite(value) or not control.low <= value <= control.high:
                raise ValueError(
                    f"{name} must be between {control.low:g} and {control.high:g},"
                    f" got {value!r}"
                )
        return {name: float(controls[name]) for name in declared}

    def _noise(self, settings: Mapping[str, float]) -> float:
        key = f"{self.seed}|{self.name}|" + "|".join(
            f"{k}={v:.12g}" for k, v in sorted(settings.items())
        )
        digest = hashlib.sha256(key.encode()).digest()
        rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
        return float(rng.standard_normal())


class ProjectileEnvironment(Environment):
    """The range of a projectile launched from the ground, in a world whose
    gravity is hidden (``pbc.mechanics.projectile.drag_free_range``)."""

    name = "projectile"
    controls = (
        Control("speed", "m/s", 5.0, 40.0, "launch speed"),
        Control("angle", "degrees", 10.0, 80.0, "launch angle above the horizontal"),
    )
    observation = Observation("range", "m", 0.5, "distance to the landing point")
    claim = (Control("g", "m/s^2", 0.5, 50.0, "gravity of the world"),)
    family = "range = speed^2 sin(2 angle) / g"
    starts = ((9.8,), (3.0,))
    _held_out = (
        {"speed": 60.0, "angle": 30.0},
        {"speed": 80.0, "angle": 45.0},
        {"speed": 100.0, "angle": 60.0},
    )

    def __init__(self, *, gravity: float = 3.7, budget: int = 30, seed: int = 0):
        super().__init__(budget=budget, seed=seed)
        self._gravity = gravity

    def _law(self, settings):
        return float(
            drag_free_range(settings["speed"], settings["angle"], self._gravity)
        )

    def predict(self, claim, settings):
        return float(drag_free_range(settings["speed"], settings["angle"], claim["g"]))


class OscillatorEnvironment(Environment):
    """The displacement of a mass on a spring of hidden stiffness
    (``pbc.mechanics.oscillator.harmonic_motion``), released at rest."""

    name = "oscillator"
    controls = (
        Control("amplitude", "m", 0.1, 2.0, "starting displacement, released at rest"),
        Control("time", "s", 0.0, 3.0, "time since the release"),
    )
    observation = Observation("displacement", "m", 0.02, "position at that time")
    claim = (Control("omega", "rad/s", 0.1, 20.0, "angular frequency"),)
    family = "displacement = amplitude cos(omega time)"
    starts = tuple((w,) for w in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0))
    _held_out = (
        {"amplitude": 1.0, "time": 5.0},
        {"amplitude": 1.5, "time": 8.0},
        {"amplitude": 0.5, "time": 12.0},
    )
    _MASS = 1.0  # kg, the mass is known; the stiffness is not

    def __init__(self, *, stiffness: float = 6.0, budget: int = 30, seed: int = 0):
        super().__init__(budget=budget, seed=seed)
        self._stiffness = stiffness

    def _law(self, settings):
        start = State(t=0.0, x=[settings["amplitude"]], v=[0.0])
        motion = harmonic_motion(start, self._MASS, self._stiffness, settings["time"])
        return float(motion.x[0, 0])

    def predict(self, claim, settings):
        return float(
            settings["amplitude"] * math.cos(claim["omega"] * settings["time"])
        )

    def _scale(self, settings):
        # The displacement passes through zero; the scale is the amplitude.
        return settings["amplitude"]


class CentralForceEnvironment(Environment):
    """The force on a test mass at a distance from a fixed centre, in a world
    whose law is modified: ``F = strength * m * r ** -exponent``, with
    ``strength`` and ``exponent`` hidden. Newton's inverse-square law is the
    exponent 2 (``pbc.mechanics.orbit.central_gravity``); the worked
    environment hides a different one."""

    name = "central-force"
    controls = (
        Control("distance", "m", 1.0, 4.0, "distance from the centre"),
        Control("mass", "kg", 0.5, 5.0, "mass of the test body"),
    )
    observation = Observation("force", "N", 0.02, "attraction toward the centre")
    claim = (
        Control("strength", "N m^p/kg", 0.1, 100.0, "coefficient of the law"),
        Control("exponent", "1", 0.0, 6.0, "power p of the distance"),
    )
    family = "force = strength mass distance^-exponent"
    starts = ((10.0, 2.0), (30.0, 1.0), (5.0, 3.0))
    _held_out = (
        {"distance": 6.0, "mass": 1.0},
        {"distance": 9.0, "mass": 2.0},
        {"distance": 12.0, "mass": 4.0},
    )

    def __init__(
        self,
        *,
        strength: float = 20.0,
        exponent: float = 2.5,
        budget: int = 30,
        seed: int = 0,
    ):
        super().__init__(budget=budget, seed=seed)
        self._strength = strength
        self._exponent = exponent

    def _law(self, settings):
        return (
            self._strength * settings["mass"] * settings["distance"] ** -self._exponent
        )

    def predict(self, claim, settings):
        return float(
            claim["strength"]
            * settings["mass"]
            * settings["distance"] ** -claim["exponent"]
        )


ENVIRONMENTS: dict[str, type[Environment]] = {
    cls.name: cls
    for cls in (ProjectileEnvironment, OscillatorEnvironment, CentralForceEnvironment)
}


def library(
    environment: Environment,
) -> dict[str, Callable[[Mapping[str, float]], float]]:
    """The candidate terms of the sparse baseline: the observation is looked
    for as a sum of these. Terms are public; they say nothing of the law."""
    if isinstance(environment, CentralForceEnvironment):
        return {
            f"mass*distance^-{n}": (lambda s, n=n: s["mass"] * s["distance"] ** -n)
            for n in range(5)
        }
    if isinstance(environment, ProjectileEnvironment):
        return {
            "speed^2*sin(2 angle)": lambda s: (
                s["speed"] ** 2 * math.sin(math.radians(2 * s["angle"]))
            ),
            "speed^2": lambda s: s["speed"] ** 2,
            "speed": lambda s: s["speed"],
        }
    return {}
