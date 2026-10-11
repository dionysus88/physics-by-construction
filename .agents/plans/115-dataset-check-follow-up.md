# Plan — Issue #115: the dataset check of a figure cannot be bypassed

Follow-up of F51 (#102). No detailed plan expected; the Issue lists the scope.

1. `tests/support/data_use.py`: follow names through the executed Python cells
   of a lesson from the readers, loaders, and sample directories of `pbc.data`;
   the source check asks every figure cell that uses such a name for
   `fig-dataset` or `fig-model-of`.
2. `pbc.data.status`: `allowed_statuses(card, artifact_type)` and
   `needs_artifact(card)`; the source check, the lesson filter, and the
   built-site check carry and enforce `fig-artifact`.
3. `Series.interpolate_to`: propagate the uncertainty of both samples.
4. `docs/architecture.md`, `docs/authoring.md`: what the check establishes and
   what it cannot see.
5. Tests for each; the rendering check page shows a model figure.
