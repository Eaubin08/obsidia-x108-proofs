"""
KX108 Runtime Link Facts V1.

Post-CG100 factual detection of the runtime links the CG93/CG97 proof
layers reason about. These are repository facts, not claims: presence is
read from the filesystem, never asserted by a caller.

Detecting a link does NOT validate the runtime. A present adapter proves
one binding exists; it proves nothing about real execution.

No authority. No decision. No IO beyond existence checks. stdlib only.
"""

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

# The canonical AgentResult -> ContextPacket binder and the flow that runs
# it into the existing X108 dry-run admission path.
CANONICAL_AGENT_CONTEXT_ADAPTER_PATH = (
    "periphery/context/agent_result_context_adapter.py"
)

CANONICAL_AGENT_CONTEXT_FLOW_PATH = (
    "periphery/context/agent_x108_context_flow.py"
)

# Runtime links that remain deliberately not activated.
MISSING_RUNTIME_LINK_ADAPTER = (
    "AGENT_RESULT_TO_CONTEXT_PACKET_CANONICAL_ADAPTER"
)

MISSING_RUNTIME_LINK_REAL_EXECUTION = (
    "REAL_X108_GATED_EXECUTION_PATH_NOT_ACTIVATED"
)


def _exists(relative_path: str) -> bool:
    return (_REPO_ROOT / relative_path).is_file()


def canonical_agent_context_adapter_present() -> bool:
    """True when the canonical binder AND its X108 flow both exist."""
    return _exists(CANONICAL_AGENT_CONTEXT_ADAPTER_PATH) and _exists(
        CANONICAL_AGENT_CONTEXT_FLOW_PATH
    )


def missing_runtime_links() -> tuple[str, ...]:
    """
    Runtime links still absent or not activated.

    The real X108-gated execution path is always listed: every observable
    decision on this perimeter stays BLOCK / HOLD / ALLOW_CONTEXT_ONLY and
    no world action is ever executed.
    """
    links = []

    if not canonical_agent_context_adapter_present():
        links.append(MISSING_RUNTIME_LINK_ADAPTER)

    links.append(MISSING_RUNTIME_LINK_REAL_EXECUTION)

    return tuple(links)


def runtime_link_facts() -> dict:
    """Observable, non-authoritative snapshot of the runtime link facts."""
    return {
        "canonical_agent_context_adapter_present":
            canonical_agent_context_adapter_present(),

        "canonical_agent_context_adapter_path":
            CANONICAL_AGENT_CONTEXT_ADAPTER_PATH,

        "canonical_agent_context_flow_path":
            CANONICAL_AGENT_CONTEXT_FLOW_PATH,

        "missing_runtime_links":
            missing_runtime_links(),

        "runtime_end_to_end_validated":
            False,

        "runtime_globally_validated":
            False,

        "runtime_allowed_now":
            False,

        "decision_authority":
            "KX108_ONLY",

        "execution_authority":
            False,

        "memory_write":
            False,

        "kernel_mutation":
            False,

        "emits_act":
            False,
    }
