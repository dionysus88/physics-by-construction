"""The Newtonian-order chirp of two bodies that spiral together.

Two point masses on a circular orbit (the Kepler orbit of the orbit module with
zero eccentricity) radiate gravitational waves at twice the orbital frequency.
The orbit loses energy at the rate the quadrupole formula of general relativity
gives, an input from outside Newtonian mechanics that this module states and
does not derive. With that one input, Kepler's third law and the energy of a
circular orbit give the whole chirp at leading order: the frequency, its rate of
change, and the one combination of the two masses they depend on, the chirp
mass.

Units are SI throughout; masses are in solar masses where a name says so.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp

C = 299_792_458.0  # m/s, exact
GM_SUN = 1.32712440018e20  # m^3/s^2, IAU nominal solar mass parameter
G = 6.67430e-11  # m^3/(kg s^2), CODATA 2018
M_SUN = GM_SUN / G  # kg
GM_SUN_OVER_C3 = GM_SUN / C**3  # s, about 4.925e-6
GM_SUN_OVER_C2 = GM_SUN / C**2  # m, about 1.477e3

Array = NDArray[np.float64]


def chirp_mass(m1: float, m2: float) -> float:
    """The chirp mass ``(m1 m2)^(3/5) / (m1 + m2)^(1/5)``, in the units of ``m1``."""
    if m1 <= 0 or m2 <= 0:
        raise ValueError("masses must be positive")
    return (m1 * m2) ** 0.6 / (m1 + m2) ** 0.2


def separation_from_frequency(f_gw: ArrayLike, total_mass: float) -> Array:
    """Orbital separation in metres at gravitational-wave frequency ``f_gw``.

    Kepler's third law with ``GM = G (m1 + m2)``: the orbital frequency is half
    the wave frequency, ``(2 pi f_orb)^2 a^3 = GM``.
    """
    omega = np.pi * np.asarray(f_gw, dtype=float)  # 2 pi f_orb = pi f_gw
    return (total_mass * GM_SUN / omega**2) ** (1.0 / 3.0)


def frequency_from_separation(a: ArrayLike, total_mass: float) -> Array:
    """Gravitational-wave frequency in hertz of a circular orbit of radius ``a``."""
    return np.sqrt(total_mass * GM_SUN / np.asarray(a, dtype=float) ** 3) / np.pi


def shrink_rate(a: ArrayLike, m1: float, m2: float) -> Array:
    """The rate ``da/dt`` at which a circular orbit shrinks, in m/s (negative).

    ``da/dt = -(64/5) G^3 m1 m2 (m1 + m2) / (c^5 a^3)``: the energy of the
    circular orbit, ``-G m1 m2 / (2 a)``, falls at the power of the quadrupole
    formula, ``(32/5) G^4 m1^2 m2^2 (m1 + m2) / (c^5 a^5)``. The power is the
    one input of this module that is not Newtonian.
    """
    a = np.asarray(a, dtype=float)
    return -(64.0 / 5.0) * (GM_SUN / C**2) ** 3 * C * m1 * m2 * (m1 + m2) / a**3


def chirp_frequency(t: ArrayLike, mc: float, t_c: float) -> Array:
    """Wave frequency in hertz at time ``t`` for chirp mass ``mc`` (solar masses).

    ``f = (1 / pi) (5 / (256 tau))^(3/8) (G Mc / c^3)^(-5/8)`` with the time to
    coalescence ``tau = t_c - t``. It diverges at ``t_c``, where the Newtonian
    orbit has long stopped being a good model; times at or after ``t_c`` give
    ``nan``.
    """
    tau = t_c - np.asarray(t, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        f = (5.0 / (256.0 * tau)) ** 0.375 / (np.pi * (mc * GM_SUN_OVER_C3) ** 0.625)
    return np.where(tau > 0, f, np.nan)


def chirp_phase(t: ArrayLike, mc: float, t_c: float) -> Array:
    """Phase of the wave in radians, up to a constant.

    ``-2 (tau / (5 G Mc / c^3))^(5/8)`` with ``tau = t_c - t``.
    """
    tau = np.clip(t_c - np.asarray(t, dtype=float), 0.0, None)
    return -2.0 * (tau / (5.0 * mc * GM_SUN_OVER_C3)) ** 0.625


def chirp_rate(f: ArrayLike, mc: float) -> Array:
    """``df/dt`` in Hz/s at frequency ``f``.

    ``(96/5) pi^(8/3) (G Mc / c^3)^(5/3) f^(11/3)``.
    """
    f = np.asarray(f, dtype=float)
    return (
        (96.0 / 5.0)
        * np.pi ** (8.0 / 3.0)
        * (mc * GM_SUN_OVER_C3) ** (5.0 / 3.0)
        * f ** (11.0 / 3.0)
    )


def chirp_mass_from_rate(f: ArrayLike, fdot: ArrayLike) -> Array:
    """Chirp mass in solar masses from a frequency and its rate of change.

    The inverse of ``chirp_rate``:
    ``G Mc / c^3 = ((5/96) pi^(-8/3) f^(-11/3) fdot)^(3/5)``.
    """
    f = np.asarray(f, dtype=float)
    fdot = np.asarray(fdot, dtype=float)
    return (
        (5.0 / 96.0) * np.pi ** (-8.0 / 3.0) * f ** (-11.0 / 3.0) * fdot
    ) ** 0.6 / GM_SUN_OVER_C3


def inspiral_frequency(
    t: ArrayLike, m1: float, m2: float, f_start: float
) -> tuple[Array, Array]:
    """Integrate the shrinking circular orbit and return ``(t, f_gw)`` in s and Hz.

    The orbit starts at the separation where the wave frequency is
    ``f_start`` and shrinks by ``shrink_rate``; the frequency follows from
    Kepler's third law at each separation. Nothing here uses the closed form
    of ``chirp_frequency``, so the two can be compared. ``t`` must start at 0.
    """
    t = np.asarray(t, dtype=float)
    a0 = float(separation_from_frequency(f_start, m1 + m2))
    solution = solve_ivp(
        lambda _t, a: shrink_rate(a, m1, m2),
        (t[0], t[-1]),
        [a0],
        t_eval=t,
        rtol=1e-11,
        atol=1e-3,
    )
    return solution.t, frequency_from_separation(solution.y[0], m1 + m2)


def time_to_coalescence(f: float, mc: float) -> float:
    """Seconds left at frequency ``f`` for chirp mass ``mc``.

    ``(5/256) (pi f)^(-8/3) (G Mc / c^3)^(-5/3)``.
    """
    return (
        (5.0 / 256.0)
        * (np.pi * f) ** (-8.0 / 3.0)
        * (mc * GM_SUN_OVER_C3) ** (-5.0 / 3.0)
    )


def schwarzschild_radius(mass: float) -> float:
    """``2 G M / c^2`` in metres for a mass in solar masses."""
    return 2.0 * mass * GM_SUN_OVER_C2


def chirp_waveform(
    t: ArrayLike, mc: float, t_c: float, a_cos: float = 1.0, a_sin: float = 0.0
) -> Array:
    """Leading-order waveform, zero from ``t_c`` on.

    ``f^(2/3) (a_cos cos(phi) + a_sin sin(phi))``.

    The amplitude scale is free (it depends on the distance and the angles,
    which the frequency does not); the shape is fixed by ``mc`` and ``t_c``.
    """
    t = np.asarray(t, dtype=float)
    f = chirp_frequency(t, mc, t_c)
    phase = chirp_phase(t, mc, t_c)
    envelope = np.where(np.isfinite(f), np.nan_to_num(f) ** (2.0 / 3.0), 0.0)
    return envelope * (a_cos * np.cos(phase) + a_sin * np.sin(phase))
