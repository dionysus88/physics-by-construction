"""Which names of a lesson are derived from a dataset (ADR 007)."""

import pytest
from support.data_use import DataUse, is_source


@pytest.mark.parametrize(
    "dotted",
    [
        "pbc.data.SAMPLES_DIR",
        "pbc.data.DOWNLOADS_DIR",
        "pbc.data.gwosc.read_strain",
        "pbc.data.touchstone",
        "pbc.data.adapters.strain_series",
        "pbc.data.reference.gw150914.load",
        "pbc.data.a_reader_added_later.read",
    ],
)
def test_what_reads_or_holds_data_is_a_source(dotted: str):
    assert is_source(dotted)


@pytest.mark.parametrize(
    "dotted",
    [
        "pbc.data",
        "pbc.data.REGISTRY_DIR",
        "pbc.data.plotting.series_with_band",
        "pbc.data.series.Series",
        "pbc.data.fit.fit_curve",
        # Imports modules that import each other, and one that names the
        # sample directory to render a card: neither makes it a reader.
        "pbc.authoring.excerpt",
        "pbc.authoring.data_card",
        "pbc.no_such_module.name",
        "numpy.loadtxt",
    ],
)
def test_tools_and_other_modules_are_not_a_source(dotted: str):
    assert not is_source(dotted)


def test_a_name_is_followed_through_the_cells_whatever_their_order():
    use = DataUse(
        [
            "curve = [2 * value for value in samples]\n",
            "from pbc.data.flume import read_elevation\n"
            "samples = read_elevation(path).elevation\n",
            "other = 3.0\n",
        ]
    )

    assert use.uses("plt.plot(curve)\n")
    assert not use.uses("plt.plot([other])\n")


def test_a_module_does_not_become_data_by_drawing_it():
    use = DataUse(
        [
            "import matplotlib.pyplot as plt\n"
            "from pbc.data.flume import read_elevation\n"
            "plt.plot(read_elevation(path).elevation)\n"
        ]
    )

    assert not use.uses("plt.plot([0.0, 1.0])\n")


def test_a_star_import_of_a_reader_makes_every_cell_a_data_cell():
    use = DataUse(["from pbc.data.gwosc import *\n"])

    assert use.uses("plt.plot(values)\n")


def test_a_star_import_of_the_package_brings_the_sample_directory():
    use = DataUse(
        [
            "import numpy as np\nfrom pbc.data import *\n"
            'values = np.loadtxt(SAMPLES_DIR / "a" / "a.csv")\n'
        ]
    )

    assert use.uses("plt.plot(values)\n")
    assert use.uses("plt.plot(np.loadtxt(DOWNLOADS_DIR / 'b.csv'))\n")
    # A figure of numbers the lesson made itself stays what it is.
    assert not use.uses("plt.plot(np.linspace(0.0, 1.0))\n")


def test_a_star_import_of_a_tool_brings_no_data():
    use = DataUse(["from pbc.data.plotting import *\nvalues = [0.0, 1.0]\n"])

    assert not use.uses("plt.plot(values)\n")


def test_a_cell_that_is_not_plain_python_is_read_by_its_words():
    use = DataUse(
        [
            "from pbc.data.gwosc import read_strain\n",
            "%%time\nstrain = read_strain(path)\n",
        ]
    )

    assert use.uses("plt.plot(strain.strain)\n")
    assert use.uses("%%time\nread_strain(path)\n")
