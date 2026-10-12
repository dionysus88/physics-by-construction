"""Show an agent run and its allowlist on a lesson page.

Both are the result of a code cell, so they render as Markdown the build
produced. A run is shown from a *replay*: the model's messages are the
recorded ones, labelled as such with the model and the date, and every tool
result is the one the build recomputed. The results stored in the fixture are
never displayed.

Model text is untrusted. It is only ever placed inside a fenced code block, so
that nothing in it can become markup of the page.
"""

import json
import re

from pbc.agents.design import DISCRIMINATED, Assessment
from pbc.agents.hunter import Experiment, Verdict
from pbc.agents.loop import Transcript
from pbc.agents.messages import ToolCall, ToolResult
from pbc.agents.replay import Recording
from pbc.agents.tools import Allowlist, Choice, Tool


def _fence(text: str) -> str:
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def _block(text: str) -> str:
    fence = _fence(text)
    return f"{fence}{{.text}}\n{text.rstrip()}\n{fence}"


def _inline(text: str) -> str:
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * (longest + 1)
    return f"{fence} {text} {fence}"


def _number(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return json.dumps(value)
    return f"{value:.6g}"


def _call(call: ToolCall) -> str:
    arguments = call.arguments
    if isinstance(arguments, dict):
        shown = ", ".join(f"{key}={_number(value)}" for key, value in arguments.items())
    else:
        shown = json.dumps(arguments)
    return _inline(f"{call.name}({shown})")


def _result(result: ToolResult) -> str:
    if not result.ok:
        return f"**rejected before it ran:** {_inline(str(result.content['error']))}"
    values = ", ".join(f"{k} = {_number(v)}" for k, v in result.content.items())
    return f"**recomputed by this build:** {_inline(values)}"


class RunDisplay:
    """A replayed run, rendered with its recorded messages labelled."""

    def __init__(
        self, recording: Recording, transcript: Transcript, authored: bool = False
    ):
        self.recording = recording
        self.transcript = transcript
        self.authored = authored

    def _repr_markdown_(self) -> str:
        recording = self.recording
        if self.authored:
            opening = (
                f"**Authored example, not a recorded model run.** The messages"
                f" below were written by {_inline(recording.model)} on"
                f" {recording.recorded}, after reading the tool results. No"
                " model produced them through a provider API. This build did"
                " not call a model. It ran every tool call again; the results"
                " shown are the ones it computed."
            )
            label = "Message (authored example)"
        else:
            opening = (
                f"**Recorded run.** The model messages below were recorded from"
                f" {_inline(recording.model)} on {recording.recorded}. This build"
                " did not call a model. It ran every tool call again; the results"
                " shown are the ones it computed."
            )
            label = "Model message (recorded)"
        lines = ["::: {.agent-run}", opening, ""]
        if recording.placeholder:
            lines += [
                "**This recording is a placeholder.** Its messages were written"
                " by hand, not produced by a model, and stand in until the"
                " maintainer records a live run.",
                "",
            ]
        for number, step in enumerate(self.transcript.steps, start=1):
            lines += [f"**Step {number}. {label}:**", ""]
            lines += [_block(step.message.text or "(no text)"), ""]
            for call, result in zip(step.message.tool_calls, step.results, strict=True):
                lines.append(f"- {_call(call)}: {_result(result)}")
            lines.append("")
        ending = (
            "The model ended the run with a message that requests no tool."
            if self.transcript.finished
            else "The step limit stopped the run."
        )
        lines += [ending, ":::", ""]
        return "\n".join(lines)


def _tool_lines(tool: Tool) -> list[str]:
    lines = [f"- {_inline(tool.name)}: {tool.description}"]
    for p in tool.parameters:
        if isinstance(p, Choice):
            allowed = ", ".join(p.options)
            lines.append(f"    - {_inline(p.name)}: {p.description}; one of {allowed}")
        else:
            lines.append(
                f"    - {_inline(p.name)}: {p.description}; allowed values"
                f" {p.low:g} to {p.high:g}"
            )
    return lines


class AllowlistDisplay:
    """The allowlist of a lesson as a list of tools, arguments, and bounds.

    A list rather than a table: it wraps on a phone screen, where a wide table
    would need a scroll region.
    """

    def __init__(self, allowlist: Allowlist):
        self.allowlist = allowlist

    def _repr_markdown_(self) -> str:
        lines: list[str] = []
        for tool in self.allowlist.tools:
            lines += _tool_lines(tool)
        return "\n".join(lines) + "\n"


def _experiment(tool: str, experiment: Experiment) -> str:
    shown = ", ".join(f"{k}={_number(v)}" for k, v in experiment.arguments.items())
    return f"{tool}({shown})"


class VerdictDisplay:
    """The verdict of a hunt, as the build computed it.

    Every number is the judge's recomputation. A counterexample is printed as
    a claim of type ``numerically-verified``; an inconclusive outcome is
    labelled as such, has no claim type, and says what it does not show.
    """

    def __init__(self, verdict: Verdict):
        self.verdict = verdict

    def _repr_markdown_(self) -> str:
        verdict, claim = self.verdict, self.verdict.claim
        witness = verdict.witness
        if witness is not None:
            call = _experiment(claim.tool, witness)
            # Words, not a call: a label with a scope breaks only at spaces.
            arguments = ", ".join(
                f"{k} {_number(v)}" for k, v in witness.arguments.items()
            )
            scope = f"the experiment with {arguments}".replace('"', "")
            return (
                "::: {.verdict}\n"
                "**Verdict: counterexample, recomputed by this build.**\n\n"
                f"[The claim \u201c{claim.statement}\u201d is false: the build ran"
                f" {_inline(call)} again and got {claim.result} ="
                f" {_inline(_number(witness.value))}, which is above the limit"
                f" {_inline(_number(claim.limit))}.]"
                f'{{.claim type="numerically-verified" scope="{scope}"}}\n\n'
                f"The build ran {verdict.tested} experiment(s) of the domain and"
                " took the first one that breaks the predicate. What the agent"
                " wrote about it did not decide the verdict.\n"
                ":::\n"
            )
        if verdict.closest is None:
            nearest = "The agent ran no experiment in the domain of the claim."
        else:
            nearest = (
                "The closest the build found was"
                f" {_inline(_experiment(claim.tool, verdict.closest))} with"
                f" {claim.result} = {_inline(_number(verdict.closest.value))}, against"
                f" a limit of {_inline(_number(claim.limit))}."
            )
        return (
            "::: {.verdict .inconclusive}\n"
            "**Verdict: inconclusive.** This is not a result about the claim"
            f" \u201c{claim.statement}\u201d and has no claim type. The build ran"
            f" {verdict.tested} experiment(s) of the domain and none broke the"
            f" predicate. {nearest} Finitely many experiments cannot show that the"
            " claim holds everywhere, so this does not show that it is true.\n"
            ":::\n"
        )


class AssessmentDisplay:
    """The assessment of an experimental design, as the build computed it.

    Every number is a recomputation: the design score from the arguments of the
    measurements, the chi-square of each model from their recomputed values. A
    discrimination is printed as a claim of type ``numerically-verified``
    scoped to the measurements; an inconclusive outcome is labelled as such,
    has no claim type, and says what it does not show.
    """

    def __init__(self, assessment: Assessment):
        self.assessment = assessment

    def _fits(self) -> str:
        fits = self.assessment.fits
        if fits is None:
            return ""
        lines = []
        for item in fits:
            parameters = ", ".join(
                f"{name} = {_number(value)} \u00b1 {_number(error)}"
                for name, value, error in zip(
                    item.model.parameters,
                    item.fit.params,
                    item.fit.stderr,
                    strict=True,
                )
            )
            lines.append(
                f"- {item.model.name}: chi-square {_number(item.chi2)} for"
                f" {item.fit.dof} degrees of freedom; {parameters} (one standard"
                " error)"
            )
        return "\n".join(lines) + "\n\n"

    def _repr_markdown_(self) -> str:
        a = self.assessment
        design = a.design
        head = (
            f"The build recomputed {len(a.measurements)} measurement(s) from their"
            f" arguments and scored the design at {_inline(_number(a.score))}"
            " (chi-square by which the worse model stays behind the true one"
            " on noise-free values at these points; the smaller of the two"
            f" directions). A difference of {_inline(_number(design.threshold))}"
            " counts as telling the models apart.\n\n"
        )
        if a.outcome == DISCRIMINATED:
            best = a.preferred
            assert best is not None and a.difference is not None
            scope = (
                f"the {len(a.measurements)} measurements of this run with an"
                f" instrument noise of {design.sigma:g}"
            )
            return (
                "::: {.verdict}\n"
                "**Verdict: the measurements discriminate, recomputed by this"
                " build.**\n\n"
                + head
                + self._fits()
                + f"[The measurements favour {best.model.name}: it fits within the"
                f" noise, and the other model is worse by a chi-square of"
                f" {a.difference:.4g}.]"
                f'{{.claim type="numerically-verified" scope="{scope}"}}\n\n'
                "What the agent wrote did not decide the verdict.\n"
                ":::\n"
            )
        return (
            "::: {.verdict .inconclusive}\n"
            "**Verdict: inconclusive.** This is not a result about the models and"
            " has no claim type.\n\n"
            + head
            + self._fits()
            + f"Why: {a.reason}. Measurements that do not separate the models do"
            " not show that they are equal, and a model that fits is not thereby"
            " true.\n"
            ":::\n"
        )
