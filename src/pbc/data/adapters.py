"""The readers' results as ``Series``, with the artifact type of their source.

Each adapter states what the card says about the data it wraps: the type of the
artifact, the unit, and where the uncertainty comes from. Labs start here and
never decide a status by hand.
"""

import numpy as np

from pbc.data.flume import Elevation
from pbc.data.gwosc import Strain
from pbc.data.series import Series
from pbc.data.touchstone import Network
from pbc.data.uncertainty import standard_from_expanded


def strain_series(strain: Strain) -> Series:
    """Calibrated strain of one detector (the LIGO calibration pipeline output)."""
    return Series(
        x=strain.time,
        y=strain.strain,
        artifact="calibrated-observation",
        x_name="GPS time",
        x_unit="s",
        y_name=f"{strain.detector} strain",
        y_unit="1",
    )


def transmission_series(network: Network) -> Series:
    """|S21| in dB against frequency in GHz of a calibrated two-port."""
    return Series(
        x=network.frequency / 1e9,
        y=20 * np.log10(np.abs(network.s[:, 1, 0])),
        artifact="calibrated-observation",
        x_name="frequency",
        x_unit="GHz",
        y_name="|S21|",
        y_unit="dB",
    )


def measured_elevation(elevation: Elevation, gauge: int) -> Series:
    """Mean of the repetitions at ``gauge`` with the standard uncertainty.

    The file gives the expanded uncertainty of the mean at 95 % confidence; the
    series carries the standard one.
    """
    return Series(
        x=elevation.time,
        y=elevation.column(gauge, "mean"),
        sigma=standard_from_expanded(elevation.column(gauge, "expanded unc")),
        artifact="processed-measured",
        x_name="time",
        x_unit="s",
        y_name="surface elevation",
        y_unit="m",
    )


def modelled_elevation(elevation: Elevation) -> Series:
    """The single column of a numerical run, as a modelled reference."""
    return Series(
        x=elevation.time,
        y=elevation.values[:, 0],
        artifact="modelled-reference",
        x_name="time",
        x_unit="s",
        y_name="surface elevation",
        y_unit="m",
    )
