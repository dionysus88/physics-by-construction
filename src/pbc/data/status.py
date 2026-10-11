"""The figure status that follows from the type of an artifact (ADR 007).

A figure carries one of ``measured``, ``calibrated``, ``processed``,
``simulated``, or ``conceptual``. For a figure made from data the status is not
a free choice: it comes from the artifact type on the dataset card.
"""

STATUS_OF_ARTIFACT = {
    "raw-measured": "measured",
    "processed-measured": "processed",
    "calibrated-observation": "calibrated",
    "modelled-reference": "simulated",
    "synthetic-test": "simulated",
}
MEASURED_STATUSES = ("measured", "calibrated", "processed")
FIGURE_STATUSES = (*MEASURED_STATUSES, "simulated", "conceptual")


def status_of(artifact_type: str, steps: tuple[str, ...] = ()) -> str:
    """Status of data of ``artifact_type`` after the disclosed ``steps``.

    A measured or calibrated artifact that went through any step (selected,
    smoothed, interpolated) is ``processed``; a modelled reference never
    becomes a measurement.
    """
    if artifact_type not in STATUS_OF_ARTIFACT:
        raise ValueError(f"unknown artifact type {artifact_type!r}")
    status = STATUS_OF_ARTIFACT[artifact_type]
    if steps and status in ("measured", "calibrated"):
        return "processed"
    return status


def allowed_statuses(card: dict) -> set[str]:
    """Statuses a figure from the dataset of ``card`` may carry.

    A raw or calibrated artifact also allows ``processed``, since a figure
    selects or scales. ``conceptual`` is never allowed for a figure of the data
    itself, and ``simulated`` only for a card with a modelled or synthetic
    artifact.
    """
    allowed: set[str] = set()
    for artifact in card.get("artifacts") or []:
        kind = artifact.get("type")
        if kind not in STATUS_OF_ARTIFACT:
            continue
        status = STATUS_OF_ARTIFACT[kind]
        allowed.add(status)
        if status in ("measured", "calibrated"):
            allowed.add("processed")
    return allowed
