"""The harness tools over an environment: what an agent may do, and nothing
else (ADR 004).

Two tools. ``measure`` sets the controls of the environment and returns its
noisy observation; ``submit`` states the agent's claim as the parameters of
the environment's public family of laws. Neither returns anything but the
observation and an acknowledgement. The judge's call
(``Environment.held_out_error``) and everything the environment keeps hidden
are in no tool, and the tools take the environment through a closure the
model cannot name: a call is only ever matched against the allowlist's own
names (``pbc.agents.tools``).
"""

from collections.abc import Mapping

from pbc.agents.tools import Allowlist, Parameter, Tool
from pbc.discovery.environment import Environment

MEASURE = "measure"
SUBMIT = "submit"


def environment_allowlist(environment: Environment) -> Allowlist:
    """The allowlist of ``environment``. Its budget is the environment's: a
    probe beyond it is refused, and a refused call costs nothing."""

    def submit(**claim: float) -> Mapping[str, float]:
        return {"submitted": 1.0}

    return Allowlist(
        (
            Tool(
                name=MEASURE,
                description=(
                    f"Set the controls and read the {environment.observation.name}"
                    f" ({environment.observation.unit}), with noise. Each call uses"
                    f" one of {environment.budget} probes."
                ),
                parameters=tuple(
                    Parameter(c.name, f"{c.description} ({c.unit})", c.low, c.high)
                    for c in environment.controls
                ),
                function=lambda **controls: environment.measure(**controls),
            ),
            Tool(
                name=SUBMIT,
                description=(
                    "State your claim as the parameters of the law and end the"
                    " run. It uses no probe."
                ),
                parameters=tuple(
                    Parameter(c.name, f"{c.description} ({c.unit})", c.low, c.high)
                    for c in environment.claim
                ),
                function=submit,
            ),
        )
    )
