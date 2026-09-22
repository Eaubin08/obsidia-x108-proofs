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

# Closed by the dedicated agent rail (decision_phase=AGENT_PRE_EXECUTION).
# Kept as a name so existing consumers importing it keep working.
MISSING_RUNTIME_LINK_AGENT_DECISION_RECORD = (
    "KX108_DECISION_RECORD_PERSISTENCE_FOR_AGENT_CYCLE"
)

# Modules that together carry the internal governed chain end to end.
AGENT_PRE_EXECUTION_CONTEXT_PATH = (
    "scripts/obsidia_agent_pre_execution_context_v1.py"
)

FEEDBACK_CONTEXT_ADAPTER_PATH = (
    "periphery/context/feedback_result_context_adapter.py"
)

DECISION_STORE_PATH = "scripts/obsidia_kx108_decision_store.py"

# Multi-domain proof surfaces.
MULTIDOMAIN_PROOF_PATH = (
    "tests/integration/test_canonical_governed_runtime_multidomain_v1.py"
)

CROSS_DOMAIN_ISOLATION_PROOF_PATH = (
    "tests/integration/test_canonical_governed_runtime_cross_domain_isolation_v1.py"
)

PROVIDER_SURFACE_PROOF_PATH = (
    "tests/integration/test_canonical_governed_runtime_provider_surface_v1.py"
)

SIGMA_BRIDGE_PATH = "periphery/sigma_bridge.py"

# Domains carrying a REAL canonical sigma bridge, with the gates each one
# can actually reach through its real agents. Recorded as observed, never
# engineered: gps and trading have no agent emitting a contradiction, so
# BLOCK is unreachable from those domains; ecom's state contract cannot
# satisfy its own proof agent, so it stays on HOLD.
CANONICAL_DOMAIN_GATE_REACHABILITY = {
    "bank": ("ALLOW", "HOLD", "BLOCK"),
    "gps_defense_aviation": ("ALLOW", "HOLD"),
    "trading": ("ALLOW", "HOLD"),
    "ecom": ("HOLD",),
}

# The links required before any INTERNAL GLOBAL runtime claim (R7-J).
REQUIRED_GLOBAL_RUNTIME_LINKS = (
    "MULTI_DOMAIN_RUNTIME",
    "COMMON_CANONICAL_CYCLE",
    "DOMAIN_ISOLATION",
    "REAL_KX108_PER_DOMAIN",
    "DECISION_RECORD_PER_DOMAIN",
    "CROSS_DOMAIN_ANTI_SUBSTITUTION",
    "COMMON_EXECUTION_GATE",
    "COMMON_RECEIPT_LIFECYCLE",
    "COMMON_FEEDBACK_REENTRY",
    "PROVIDER_REGISTRY_BOUNDING",
    "NON_SOVEREIGNTY_GLOBAL",
    "FAIL_CLOSED_UNSUPPORTED_DOMAIN",
)

# The chain required before any internal end-to-end claim (R6-L).
INTERNAL_E2E_REQUIRED_LINKS = (
    "REAL_AGENT_INVOCATION",
    "REAL_AGENT_RESULT",
    "REAL_CONTEXT_BINDER",
    "REAL_CONTEXT_VALIDATION",
    "REAL_PRE_EXECUTION_CONTEXT",
    "REAL_KX108_DECISION",
    "REAL_DECISION_RECORD_PERSISTED",
    "REAL_DECISION_RECORD_VERIFIED",
    "REAL_EXECUTION_GATE",
    "REAL_PROVIDER_INVOCATION",
    "REAL_SEALED_EXECUTION_ENVELOPE",
    "REAL_TERMINAL_RECEIPT",
    "REAL_READONLY_FEEDBACK",
    "REAL_NEXT_CONTEXT_REENTRY",
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


def agent_decision_record_rail_present() -> bool:
    """
    True when the agent PRE_EXECUTION rail exists: the frozen context
    module, the feedback re-entry adapter, and the AGENT_PRE_EXECUTION
    phase in the canonical decision store.
    """
    if not (
        _exists(AGENT_PRE_EXECUTION_CONTEXT_PATH)
        and _exists(FEEDBACK_CONTEXT_ADAPTER_PATH)
        and _exists(DECISION_STORE_PATH)
    ):
        return False
    store_source = (_REPO_ROOT / DECISION_STORE_PATH).read_text(encoding="utf-8")
    return (
        "AGENT_PRE_DECISION_PHASE" in store_source
        and "persist_kx108_agent_pre_execution_decision" in store_source
    )


def runtime_internal_end_to_end_validated() -> bool:
    """
    Internal governed runtime, end to end — agent through verified KX108
    decision record, bounded provider execution, sealed envelope, terminal
    receipt, read-only feedback and re-entry as a fresh context.

    This says NOTHING about the external world: no world action is ever
    executed, and runtime_end_to_end_validated keeps its historical, wider
    meaning and stays False.
    """
    return (
        canonical_agent_context_adapter_present()
        and governed_runtime_cycle_present()
        and agent_decision_record_rail_present()
    )


def multi_domain_runtime_present() -> bool:
    """
    True when several REAL canonical domains run on the single governed
    cycle, with cross-domain isolation and the real provider surface proven.

    Presence is read from disk; the behaviour itself is proven by the named
    suites, which run the real bridges, the real kernel and the real store.
    """
    if not (
        _exists(MULTIDOMAIN_PROOF_PATH)
        and _exists(CROSS_DOMAIN_ISOLATION_PROOF_PATH)
        and _exists(PROVIDER_SURFACE_PROOF_PATH)
        and _exists(SIGMA_BRIDGE_PATH)
    ):
        return False

    bridge_source = (_REPO_ROOT / SIGMA_BRIDGE_PATH).read_text(encoding="utf-8")
    return all(
        f"def run_{name}_with_periphery" in bridge_source
        for name in ("bank", "trading", "ecom", "gps")
    )


def runtime_internal_globally_validated() -> bool:
    """
    Internal runtime, globally: the same canonical cycle carries several
    real domains and several real internal providers, isolated from one
    another, each with its own verified KX108 decision record.

    This says NOTHING about external actuation. runtime_globally_validated
    keeps its historical, wider meaning and stays False.
    """
    return (
        runtime_internal_end_to_end_validated()
        and multi_domain_runtime_present()
    )


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

    if not agent_decision_record_rail_present():
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

        "agent_decision_record_rail_present":
            agent_decision_record_rail_present(),

        "runtime_internal_end_to_end_validated":
            runtime_internal_end_to_end_validated(),

        "internal_e2e_required_links":
            INTERNAL_E2E_REQUIRED_LINKS,

        "multi_domain_runtime_present":
            multi_domain_runtime_present(),

        "canonical_domain_gate_reachability":
            CANONICAL_DOMAIN_GATE_REACHABILITY,

        "runtime_internal_globally_validated":
            runtime_internal_globally_validated(),

        "required_global_runtime_links":
            REQUIRED_GLOBAL_RUNTIME_LINKS,

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
