"""The data card of a measured-data lab, rendered on the page (ADR 007).

A lab page calls ``data_card`` from a cell with ``#| echo: false``. The card
shows what a reader needs to judge the data: the source and its version, the
licence and the attribution text, the type of every artifact and the figure
status it gives, where the committed sample is or how to download the full
data, and the path that works without any model. It is read from
``data/registry`` when the page is built, so the page cannot drift from it.
"""

from dataclasses import dataclass
from html import escape

from pbc.authoring.tables import table_markup
from pbc.authoring.widgets import _raw_html
from pbc.data import REGISTRY_DIR, SAMPLES_DIR
from pbc.data.card import load_card
from pbc.data.status import STATUS_OF_ARTIFACT

NO_LLM_PATH = (
    "Everything on this page, the figures included, is reproduced from the "
    "files named here by the code of the page, with no language model and no "
    "account. An agent may help you explore the data; what it says is never data."
)


def data_card_markup(card: dict) -> str:
    """The HTML of the data card of ``card`` (a loaded dataset card)."""
    ident = card["id"]
    source, rights = card["source"], card["rights"]
    artifacts = card["artifacts"]
    kinds = " ".join(sorted({a["type"] for a in artifacts}))
    rows = [
        (a["name"], a["type"], STATUS_OF_ARTIFACT[a["type"]], a["description"])
        for a in artifacts
    ]
    columns = [
        ("Artifact", "", "s"),
        ("Type", "", "s"),
        ("Figure status", "", "s"),
        ("What it is", "", "s"),
    ]
    sample_dir = SAMPLES_DIR / ident
    if card.get("samples") and sample_dir.is_dir():
        where = (
            f"A sample is committed in <code>data/samples/{escape(ident)}/</code>; "
            "the figures on this page are made from it."
        )
    else:
        where = "No sample is committed; the figures are made from the download."
    download = (
        f"The full data: <code>./scripts/fetch-data.sh {escape(ident)}</code> "
        "downloads it into <code>data/downloads/</code> and checks its digest. "
        "The site build and the checks never download anything."
    )
    doi = f", DOI {escape(str(source['doi']))}" if source.get("doi") else ""
    items = [
        ("Dataset", escape(card["title"])),
        (
            "Source",
            f'<a href="{escape(source["url"], quote=True)}">{escape(source["url"])}</a>'
            f"{doi}, {escape(source['creator'])}; {escape(source['version'])}",
        ),
        ("Licence", escape(rights["licence"])),
        ("Attribution", escape(rights["attribution"].strip())),
    ]
    for field, title in (
        ("calibration", "Calibration"),
        ("masks", "Masks"),
        ("uncertainty", "Uncertainty"),
    ):
        items.append((title, escape(" ".join(str(card[field]).split()))))
    definition = "\n".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in items)
    caption = (
        f"Artifacts of the dataset {card['title']} and the figure status each gives"
    )
    return "\n".join(
        [
            f'<section class="data-card" data-dataset="{escape(ident, quote=True)}" '
            f'data-artifacts="{escape(kinds, quote=True)}" '
            f'aria-label="Data card: {escape(card["title"], quote=True)}">',
            "<p><strong>Data card</strong></p>",
            f"<dl>{definition}</dl>",
            table_markup(rows, columns, caption),
            f"<p>{where}</p>",
            f"<p>{download}</p>",
            f"<p><strong>No-LLM path.</strong> {escape(NO_LLM_PATH)}</p>",
            "</section>",
        ]
    )


@dataclass(frozen=True)
class DataCard:
    """As the result of a code cell it renders the data card."""

    markup: str

    def _repr_markdown_(self) -> str:
        return _raw_html(self.markup)


def data_card(dataset: str) -> DataCard:
    """The data card of the dataset ``dataset`` of ``data/registry``.

    Only a dataset with a ``go`` decision has a card a lab may show.
    """
    card = load_card(REGISTRY_DIR / f"{dataset}.yaml")
    decision = (card.get("decision") or {}).get("value")
    if decision != "go":
        raise ValueError(f"{dataset}: decision is {decision!r}; a lab needs a go")
    return DataCard(data_card_markup(card))
