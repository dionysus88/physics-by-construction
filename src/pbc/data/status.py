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


def _statuses_of_type(kind: str) -> set[str]:
    status = STATUS_OF_ARTIFACT[kind]
    # A figure of a raw or calibrated artifact selects or scales.
    return {status, "processed"} if status in ("measured", "calibrated") else {status}


def artifact_types(card: dict) -> set[str]:
    """The known artifact types on ``card``."""
    kinds = {artifact.get("type") for artifact in card.get("artifacts") or []}
    return {kind for kind in kinds if kind in STATUS_OF_ARTIFACT}


def needs_artifact(card: dict) -> bool:
    """Whether a figure of the dataset has to say which artifact it shows.

    A card that holds measurements and a modelled or synthetic artifact
    allows ``simulated`` for the one and not for the other, so the dataset
    alone does not decide the status of a figure.
    """
    statuses = {STATUS_OF_ARTIFACT[kind] for kind in artifact_types(card)}
    return "simulated" in statuses and len(statuses) > 1


def allowed_statuses(card: dict, artifact_type: str | None = None) -> set[str]:
    """Statuses a figure from the dataset of ``card`` may carry.

    A raw or calibrated artifact also allows ``processed``, since a figure
    selects or scales. ``conceptual`` is never allowed for a figure of the data
    itself, and ``simulated`` only for a modelled or synthetic artifact. With
    ``artifact_type`` the answer is for a figure of that artifact alone; it is
    empty when the card has no such artifact.
    """
    kinds = artifact_types(card)
    if artifact_type is not None:
        kinds &= {artifact_type}
    allowed: set[str] = set()
    for kind in kinds:
        allowed |= _statuses_of_type(kind)
    return allowed
