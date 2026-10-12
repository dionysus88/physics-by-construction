"""An analysis pipeline for a simulated problem: how far a thrown ball goes.

The ball is launched at a speed known only to a standard uncertainty. The
pipeline sweeps the launch angle, carries the uncertainty of the speed into the
range to first order, checks that propagation against a seeded Monte Carlo run,
and collects the results in a report (``pbc.data.pipeline``).

Speeds are in m/s, angles in degrees, lengths in m, the mass in kg, and the
time step in s. The ball is a baseball in air at sea level; the numbers are
round values for the purpose of the lesson, not measurements.
"""

import numpy as np

from pbc.data.pipeline import Report, Sweep, estimate, sweep
from pbc.data.uncertainty import propagate
from pbc.mechanics.drag import drag_constant
from pbc.mechanics.integrators import rk4_step
from pbc.mechanics.projectile import drag_free_range, projectile_range

MASS = 0.145  # kg
AIR_DENSITY = 1.2  # kg/m³
DRAG_COEFFICIENT = 0.4
CROSS_SECTION = 0.0043  # m²
SPEED = 30.0  # m/s
SPEED_SIGMA = 0.5  # m/s, standard uncertainty of the launch speed
ANGLES = tuple(float(a) for a in range(15, 80, 10))  # degrees
FINE_ANGLES = tuple(30.0 + 2.5 * k for k in range(9))  # degrees, around the maximum
DT = 0.01  # s; with the fourth-order stepper the step error is far below a millimetre
SAMPLES = 200
SEED = 20260301

DRAG = drag_constant(AIR_DENSITY, DRAG_COEFFICIENT, CROSS_SECTION)


def throw_range(speed: float, angle: float, drag: float = DRAG) -> float:
    """Range in m of the ball launched at ``speed`` (m/s) and ``angle`` (degrees)."""
    return projectile_range(speed, angle, MASS, drag, DT, step=rk4_step)


def range_with_uncertainty(angle: float) -> dict[str, float]:
    """Range at ``angle`` with the uncertainty that the speed's one carries into it.

    First order and independent inputs: ``sigma_range = |d range / d speed| *
    sigma_speed`` by ``pbc.data.uncertainty.propagate``.
    """
    value, sigma = propagate(
        lambda speed: np.array(throw_range(float(speed), angle)),
        [SPEED],
        [SPEED_SIGMA],
    )
    return {
        "range": float(value),
        "sigma": float(sigma),
        "no_drag": float(drag_free_range(SPEED, angle)),
    }


def angle_sweep() -> Sweep:
    """The range, its uncertainty, and the drag-free range for each launch angle."""
    return sweep("launch angle", ANGLES, range_with_uncertainty, unit="deg")


def fine_sweep() -> Sweep:
    """The range alone on a finer grid of angles around the maximum."""
    return sweep(
        "launch angle",
        FINE_ANGLES,
        lambda a: {"range": throw_range(SPEED, a)},
        unit="deg",
    )


def monte_carlo(angle: float, samples: int = SAMPLES, seed: int = SEED):
    """Range of ``samples`` launches with the speed drawn from a normal
    distribution, as an ``Estimate`` of the mean and the sample spread.

    Returns ``(estimate, spread)``: the mean with its standard error, and the
    standard deviation of the ranges, to compare with the propagated sigma.
    """
    rng = np.random.default_rng(seed)
    speeds = rng.normal(SPEED, SPEED_SIGMA, samples)
    ranges = np.array([throw_range(float(s), angle) for s in speeds])
    return estimate(ranges), float(np.std(ranges, ddof=1))


def build_report() -> Report:
    """The report of the simulated problem, in the order of the lesson."""
    scan = angle_sweep()
    fine = fine_sweep()
    best = fine.argmax("range")
    report = Report("Projectile range with drag, launch speed uncertain")
    report = report.add("launch speed", SPEED, "m/s", sigma=SPEED_SIGMA, decimals=1)
    report = report.add("drag constant", DRAG, "kg/m", decimals=5)
    for angle, value, sigma in scan.rows("range", "sigma"):
        report = report.add(
            f"range at {angle:.0f} deg", value, "m", sigma=sigma, decimals=2
        )
    report = report.add("best angle on the fine grid", best, "deg", decimals=1)
    free = max(FINE_ANGLES, key=lambda a: drag_free_range(SPEED, a))
    report = report.add("best angle without drag", free, "deg", decimals=1)
    result, spread = monte_carlo(best)
    report = report.add(
        f"Monte Carlo range at {best:.1f} deg ({result.n} launches)",
        result.mean,
        "m",
        sigma=result.sigma,
        decimals=2,
    )
    report = report.add("Monte Carlo spread of the range", spread, "m", decimals=2)
    return report
