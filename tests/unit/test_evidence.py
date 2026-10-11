"""Reading the claims of a lesson for the evidence map."""

from pbc.authoring.evidence import COMPUTED, cell_labels, read_claims

PAGE = "lessons/mechanics/01-sample/index.qmd"

SOURCE = """\
---
title: "Sample"
---

```{python}
#| label: result
claim = "[Not a claim]{.claim type='observational'}"
```

[The energy is `{python} f"{energy:.1f}"` J, or $a | b$ for
[a value]{.not-verified}.]{.claim type="numerically-verified"
scope="one step" evidence="result, euler-error  card"}

::: {.claim type="formal-theorem"}
First paragraph.

Second paragraph.
:::
"""


def test_claims_are_read_in_document_order_with_their_attributes():
    first, second = read_claims(PAGE, SOURCE)

    assert (first.number, first.anchor) == (1, "claim-1")
    assert first.type == "numerically-verified"
    assert first.scope == "one step"
    assert first.evidence == ("result", "euler-error", "card")
    assert (second.number, second.type, second.evidence) == (2, "formal-theorem", ())


def test_a_claim_in_a_code_cell_is_no_claim():
    assert len(read_claims(PAGE, SOURCE)) == 2


def test_a_statement_hides_computed_values_and_marks_unverified_text():
    first, second = read_claims(PAGE, SOURCE)

    assert COMPUTED in first.statement
    assert "energy:" not in first.statement
    assert "a value (not verified)" in first.statement
    # A pipe would end the cell of the table the statement goes into.
    assert "a \\| b" in first.statement
    assert second.statement == "First paragraph. Second paragraph."


def test_only_labelled_executed_python_cells_are_evidence():
    text = (
        "```{python}\n#| label: ran\nx = 1\n```\n\n"
        "```{python}\n#| label: skipped\n#| eval: false\nx = 1\n```\n\n"
        "```{python}\nx = 2\n```\n\n"
        "```{r}\n#| label: other-engine\n```\n"
    )

    assert cell_labels(text) == {"ran"}
