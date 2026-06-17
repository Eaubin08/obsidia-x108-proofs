"""Boundary contract for Path Compute V0."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PathComputeV0Boundary:
    decision_authority: str = "KX108_ONLY"
    path_compute_authority: str = "NONE"
    advisory_only: bool = True
    runtime_enabled: bool = False
    implementation_allowed_now: bool = False
    activation_allowed_now: bool = False
    emits_act: bool = False
    emits_verdict: bool = False
    emits_allow_hold_block: bool = False
    constructs_canonical_envelope: bool = False
    mutates_kernel: bool = False
    mutates_domain_state: bool = False
    writes_memory: bool = False
    calls_mcp: bool = False
    binds_graphiti: bool = False
    binds_neo4j: bool = False
    external_network_call: bool = False
    subprocess_allowed: bool = False
    path_compute_runtime_enabled: bool = False


PATH_COMPUTE_V0_BOUNDARY = PathComputeV0Boundary()
