"""The data card a measured-data lab shows on its page, read from the card."""

import pytest

from pbc.authoring import data_card
from pbc.authoring.datalab import data_card_markup
from pbc.data import REGISTRY_DIR
from pbc.data.card import load_cards

CARDS = load_cards(REGISTRY_DIR)
GO = [name for name, card in CARDS.items() if card["decision"]["value"] == "go"]


@pytest.mark.parametrize("dataset", GO)
def test_the_card_of_each_go_dataset_shows_what_a_reader_needs(dataset):
    card = CARDS[dataset]
    markup = data_card(dataset).markup
    assert f'data-dataset="{dataset}"' in markup
    assert card["rights"]["licence"] in markup
    assert f"./scripts/fetch-data.sh {dataset}" in markup
    assert "No-LLM path" in markup
    assert f"data/samples/{dataset}/" in markup
    for artifact in card["artifacts"]:
        assert artifact["type"] in markup
    assert "<caption>" in markup and 'scope="col"' in markup


def test_the_card_names_the_figure_status_of_every_artifact_type():
    markup = data_card("aalborg-submerged-bar").markup
    assert "<td>processed-measured</td><td>processed</td>" in markup
    assert "<td>modelled-reference</td><td>simulated</td>" in markup


def test_the_card_escapes_the_text_of_the_dataset_card():
    card = dict(CARDS["npl-onwafer-sparameters"], title="A <b>bold</b> & title")
    markup = data_card_markup(card)
    assert (
        "<b>bold</b>" not in markup and "&lt;b&gt;bold&lt;/b&gt; &amp; title" in markup
    )


def test_a_dataset_without_a_go_decision_has_no_card_on_a_page():
    survey = next(n for n, c in CARDS.items() if c["decision"]["value"] != "go")
    with pytest.raises(ValueError, match="needs a go"):
        data_card(survey)
