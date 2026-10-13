"""Physics environments for law discovery, with the hidden truth kept apart
from the agent, baselines without an agent, and the evaluation protocol (F65;
``docs/discovery-protocol.md``).

The harness is ``pbc.agents`` (ADR 004). This package adds what the lessons of
the law-discovery and benchmarking paths share, so that none builds its own:
``Environment`` and the worked environments, ``environment_allowlist`` (the
tools over one), the baselines, and the protocol with its scoring.
"""

from pbc.discovery.baselines import (
    BaselineResult,
    Dataset,
    grid_probe,
    least_squares,
    random_probe,
    run_baselines,
    sparse_identification,
)
from pbc.discovery.environment import (
    ENVIRONMENTS,
    CentralForceEnvironment,
    Control,
    Environment,
    Observation,
    OscillatorEnvironment,
    ProjectileEnvironment,
    library,
)
from pbc.discovery.protocol import (
    CONDITIONS,
    PROMPT_VERSION,
    CostRecord,
    Protocol,
    Score,
    TraceInfo,
    comparison,
    load_trace,
    prompt_sha,
    prompts,
    save_trace,
    score_transcript,
)
from pbc.discovery.tools import MEASURE, SUBMIT, environment_allowlist

__all__ = [
    "CONDITIONS",
    "ENVIRONMENTS",
    "MEASURE",
    "PROMPT_VERSION",
    "SUBMIT",
    "BaselineResult",
    "CentralForceEnvironment",
    "Control",
    "CostRecord",
    "Dataset",
    "Environment",
    "Observation",
    "OscillatorEnvironment",
    "ProjectileEnvironment",
    "Protocol",
    "Score",
    "TraceInfo",
    "comparison",
    "environment_allowlist",
    "grid_probe",
    "least_squares",
    "library",
    "load_trace",
    "prompt_sha",
    "prompts",
    "random_probe",
    "run_baselines",
    "save_trace",
    "score_transcript",
    "sparse_identification",
]
