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

# The governed internal runtime cycle: a real GuardX108 verdict gating the
# real canonical execution rail.
GOVERNED_RUNTIME_CYCLE_PATH = (
    "scripts/obsidia_governed_runtime_cycle_v1.py"
)

# Runtime links that remain deliberately not activated.
MISSING_RUNTIME_LINK_ADAPTER = (
    "AGENT_RESULT_TO_CONTEXT_PACKET_CANONICAL_ADAPTER"
)

# Kept for compatibility with existing consumers. Since the governed
# internal cycle exists, this name denotes what is still missing: a real
# X108-gated path acting on the EXTERNAL world.
MISSING_RUNTIME_LINK_REAL_EXECUTION = (
    "REAL_X108_GATED_EXECUTION_PATH_NOT_ACTIVATED"
)

MISSING_RUNTIME_LINK_WORLD_ACTUATION = (
    "EXTERNAL_WORLD_ACTUATION_NOT_ACTIVATED"
)

# The agent cycle cannot produce a canonical KX108 decision record: the
# binding contract of run_and_persist_kx108_pre_execution_decision requires
# remediation-rail artefacts an agent cycle does not have.
MISSING_RUNTIME_LINK_AGENT_DECISION_RECORD = (
    "KX108_DECISION_RECORD_PERSISTENCE_FOR_AGENT_CYCLE"
)


def _exists(relative_path: str) -> bool:
    return (_REPO_ROOT / relative_path).is_file()


def canonical_agent_context_adapter_present() -> bool:
    """True when the canonical binder AND its X108 flow both exist."""
    return _exists(CANONICAL_AGENT_CONTEXT_ADAPTER_PATH) and _exists(
        CANONICAL_AGENT_CONTEXT_FLOW_PATH
    )


def governed_runtime_cycle_present() -> bool:
    """True when the governed internal runtime cycle module exists.

    Presence proves one internal path exists where a real GuardX108 ALLOW
    gates a real canonical provider execution. It proves nothing about the
    external world, which stays dry-run.
    """
    return _exists(GOVERNED_RUNTIME_CYCLE_PATH)


def missing_runtime_links() -> tuple[str, ...]:
    """
    Runtime links still absent or not activated.

    External world actuation is always listed: no world action is ever
    executed on this perimeter. The canonical decision-record persistence
    for an agent cycle is always listed too: it has no applicable binding
    contract, and none is fabricated.
    """
    links = []

    if not canonical_agent_context_adapter_present():
        links.append(MISSING_RUNTIME_LINK_ADAPTER)

    links.append(MISSING_RUNTIME_LINK_AGENT_DECISION_RECORD)
    links.append(MISSING_RUNTIME_LINK_WORLD_ACTUATION)
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

        "governed_runtime_cycle_present":
            governed_runtime_cycle_present(),

        "governed_runtime_cycle_path":
            GOVERNED_RUNTIME_CYCLE_PATH,

        "world_action_runtime_activated":
            False,

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
