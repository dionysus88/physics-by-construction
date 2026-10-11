"""Helpers that draw conceptual diagrams: arrows, labelled boxes, and curves.

A conceptual diagram shows an idea, not a result: it is drawn by an executed
cell, with the figure colours of the page, and it carries the status
``conceptual``. The helpers work in the data coordinates of one axes that has
no frame, so a diagram is a list of calls and is the same on every build.
"""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle, FancyBboxPatch

from pbc.authoring.design import FIGURE_COLOURS

Point = Sequence[float]

INK = "#1f2328"
FONT_SIZE = 9


def canvas(
    width: float,
    height: float,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
) -> tuple[Figure, Axes]:
    """A figure of ``width`` by ``height`` inches with one frameless axes in
    data units, scaled equally in x and y."""
    fig, ax = plt.subplots(figsize=(width, height))
    frame(ax, xlim, ylim)
    return fig, ax


def frame(ax: Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    """Make ``ax`` frameless, in data units, scaled equally in x and y; for
    a figure of several panels made with ``plt.subplots``."""
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


def arrow(
    ax: Axes,
    start: Point,
    end: Point,
    *,
    colour: int | str = 0,
    linestyle: str = "-",
    width: float = 1.6,
) -> None:
    """An arrow from ``start`` to ``end``; ``colour`` is an index into
    ``FIGURE_COLOURS`` or a hex colour."""
    ax.annotate(
        "",
        xy=tuple(end),
        xytext=tuple(start),
        arrowprops={
            "arrowstyle": "-|>",
            "color": _colour(colour),
            "linewidth": width,
            "linestyle": linestyle,
            "shrinkA": 0,
            "shrinkB": 0,
        },
    )


def text(
    ax: Axes,
    position: Point,
    string: str,
    *,
    ha: str = "center",
    va: str = "center",
    colour: int | str | None = None,
) -> None:
    """A label at ``position``."""
    ax.text(
        position[0],
        position[1],
        string,
        ha=ha,
        va=va,
        fontsize=FONT_SIZE,
        color=INK if colour is None else _colour(colour),
    )


def state_box(
    ax: Axes,
    centre: Point,
    string: str,
    *,
    width: float = 2.0,
    height: float = 0.8,
    colour: int | str = 0,
) -> None:
    """A rounded box with a label, for a state or a step."""
    x, y = centre
    box = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        facecolor="white",
        edgecolor=_colour(colour),
        linewidth=1.4,
    )
    ax.add_patch(box)
    text(ax, centre, string)


def circle(
    ax: Axes,
    centre: Point,
    radius: float,
    *,
    colour: int | str = 0,
    filled: bool = False,
    linestyle: str = "-",
) -> None:
    """A circle of ``radius`` in data units."""
    ax.add_patch(
        Circle(
            tuple(centre),
            radius,
            facecolor=_colour(colour) if filled else "white",
            edgecolor=_colour(colour),
            linewidth=1.4,
            linestyle=linestyle,
            alpha=1.0,
        )
    )


def line(
    ax: Axes,
    points: Sequence[Point],
    *,
    colour: int | str = 0,
    linestyle: str = "-",
    width: float = 1.4,
) -> None:
    """A polyline through ``points``."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.plot(xs, ys, color=_colour(colour), linestyle=linestyle, linewidth=width)


def _colour(colour: int | str) -> str:
    if isinstance(colour, str):
        return colour
    return FIGURE_COLOURS[colour % len(FIGURE_COLOURS)]
