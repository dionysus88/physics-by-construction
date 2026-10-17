"""The contract of a lesson's experiment: one encoder for the figure of the
page and of the learner's directory, and the numbers as the page shows them
(``pbc.experiment``, ADR 016 decision 2)."""

import json
import struct
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

from pbc.experiment import (
    FIGURE_SETTINGS,
    PIXEL_RATIO,
    RESULTS_FILE,
    Experiment,
    encode,
    main,
    png_size,
)


def _line():
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot([0.0, 1.0, 2.0], [0.0, 1.0, 4.0], label="a line")
    ax.set_xlabel("time (s)")
    ax.legend()
    return fig


def _default_size():
    fig, ax = plt.subplots()
    ax.plot([0.0, 1.0], [0.0, 1.0])
    return fig


def _chunks(png: bytes) -> list[bytes]:
    found, at = [], 8
    while at < len(png):
        (length,) = struct.unpack(">I", png[at : at + 4])
        found.append(png[at + 4 : at + 8])
        at += 12 + length
    return found


def test_the_same_figure_gives_the_same_bytes():
    assert encode(_line) == encode(_line)


def test_the_file_carries_no_metadata():
    chunks = _chunks(encode(_line))

    assert b"tEXt" not in chunks
    assert b"iTXt" not in chunks
    assert b"zTXt" not in chunks
    assert b"tIME" not in chunks


def test_the_settings_of_the_caller_do_not_change_the_figure():
    plain = encode(_line)
    with matplotlib.rc_context(
        {"lines.linewidth": 5.0, "font.size": 20.0, "figure.dpi": 50.0}
    ):
        assert encode(_line) == plain
    # Nor does encoding change the caller's settings.
    with matplotlib.rc_context({"font.size": 20.0}):
        encode(_line)
        assert matplotlib.rcParams["font.size"] == 20.0


def test_a_figure_has_the_size_of_the_page_at_twice_its_resolution():
    width, height = png_size(encode(_default_size))
    inches = FIGURE_SETTINGS["figure.figsize"]
    pixels = FIGURE_SETTINGS["figure.dpi"] * PIXEL_RATIO

    # Cropped to what it draws, never larger than the figure.
    assert 0.8 * inches[0] * pixels < width <= inches[0] * pixels
    assert 0.8 * inches[1] * pixels < height <= inches[1] * pixels


def test_encoding_closes_the_figure():
    before = plt.get_fignums()
    encode(_line)
    assert plt.get_fignums() == before


def test_the_page_shows_the_bytes_at_half_their_size():
    experiment = Experiment()
    experiment.figure("fig-line", _line)

    data, metadata = experiment.show("fig-line")._repr_mimebundle_()

    assert data["image/png"] == experiment.png("fig-line") == encode(_line)
    width, height = png_size(data["image/png"])
    assert metadata["image/png"] == {
        "width": width // PIXEL_RATIO,
        "height": height // PIXEL_RATIO,
    }


def test_a_figure_is_named_by_the_label_of_its_cell():
    with pytest.raises(ValueError, match="fig-"):
        Experiment().figure("line", _line)


def test_numbers_are_recorded_as_the_page_shows_them():
    experiment = Experiment()

    assert experiment.number("gap", 1.17654, ".3f") == "1.177"
    assert experiment.number("steps", 24) == "24"
    assert experiment["gap"] == "1.177"
    with pytest.raises(ValueError, match="already"):
        experiment.number("gap", 2.0, ".3f")


def test_a_table_is_shown_and_recorded_with_its_cells_as_text():
    experiment = Experiment()
    columns = [("t", "s", ".1f"), ("ratio", "", ".4f")]

    shown = experiment.table("t", [(0.0, None), (0.5, 2.0)], columns, caption="C.")

    assert "<caption>C.</caption>" in shown.markup
    assert '<td class="num">2.0000</td>' in shown.markup
    assert experiment.table("t").markup == shown.markup
    assert experiment.results()["tables"]["t"] == {
        "caption": "C.",
        "columns": ["t (s)", "ratio"],
        "rows": [["0.0", ""], ["0.5", "2.0000"]],
    }
    with pytest.raises(ValueError, match="columns"):
        experiment.table("u", [(1.0,)])


def test_the_program_writes_the_figures_and_the_results(tmp_path: Path):
    def run():
        experiment = Experiment()
        experiment.number("gap", 1.17654, ".3f")
        experiment.figure("fig-line", _line)
        return experiment

    main(run, [str(tmp_path / "out")])

    out = tmp_path / "out"
    assert sorted(path.name for path in out.iterdir()) == [
        "fig-line.png",
        RESULTS_FILE,
    ]
    assert (out / "fig-line.png").read_bytes() == encode(_line)
    assert json.loads((out / RESULTS_FILE).read_text()) == {
        "numbers": {"gap": "1.177"},
        "tables": {},
        "figures": ["fig-line.png"],
        "widgets": [],
        "outputs": {},
        "displays": {},
    }


def test_the_data_of_a_widget_is_written_beside_the_figures(tmp_path: Path):
    experiment = Experiment()
    data = {"t": [0.0, 0.5], "x": [1.0, 0.25]}

    assert experiment.widget("explorer", data) is data
    assert experiment.widget("explorer") is data
    experiment.write(tmp_path)

    assert json.loads((tmp_path / "explorer.json").read_text()) == data
    assert json.loads((tmp_path / RESULTS_FILE).read_text())["widgets"] == [
        "explorer.json"
    ]


def test_printed_output_is_recorded_as_the_page_prints_it(capsys):
    experiment = Experiment()

    with experiment.capture("matrix"):
        print("subject   pass")
        print("other     FAIL")

    assert capsys.readouterr().out == ""
    assert experiment.output("matrix") == "subject   pass\nother     FAIL\n"
    assert experiment.results()["outputs"] == {
        "matrix": "subject   pass\nother     FAIL\n"
    }


def test_a_display_is_recorded_and_shown_as_its_markdown():
    class Shown:
        def _repr_markdown_(self):
            return "**Recorded run.** Step 1."

    experiment = Experiment()

    shown = experiment.display("run", Shown())

    assert shown._repr_markdown_() == "**Recorded run.** Step 1."
    assert experiment.display("run") == shown
    assert experiment.results()["displays"] == {"run": "**Recorded run.** Step 1."}
