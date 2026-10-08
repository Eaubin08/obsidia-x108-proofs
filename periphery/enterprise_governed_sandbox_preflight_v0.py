"""V0.1 C3: tenant-scoped, SANDBOX-ONLY action preparation over C2 evidence.

Never issues permission, KX verdict, sovereign ticket, credentials, or provider
calls. Must not be inserted into a LIVE executor as an authorization bypass.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from periphery.common import ActionCandidate
from periphery.enterprise_org_stack_lifecycle_v0 import (
    CompanyStackLifecycleV0, CompanyStackLinkV0, LINK_STATUS,
)
from periphery.native_ops.common_v0 import canonical_hash
from periphery.universal_enterprise_stack_adapter_v0 import (
    EnterpriseStackManifestV0, EnterpriseActionBindingV0,
    build_enterprise_action_binding_v0,
    build_world_action_request_from_enterprise_binding_v0,
    verify_enterprise_stack_manifest_v0,
)

SCHEMA = "V01_ENTERPRISE_C3_SANDBOX_PREPARATION_V0"
SAFE_WORLD_CALLS = frozenset({"READ_ONLY_WORLD_CALL", "REVERSIBLE_WORLD_CALL"})
SAFE_RISK = frozenset({"ACTION_READ_ONLY", "ACTION_EXTERNAL_API"})


@dataclass(frozen=True)
class EnterpriseSandboxPreparationV0:
    organization_id: str
    source_link_id: str
    source_link_hash: str
    source_domain: str
    source_snapshot_hash: str
    scoped_action_candidate: ActionCandidate
    action_binding: EnterpriseActionBindingV0
    world_action_request: Mapping[str, Any]
    sandbox_only: bool = True
    real_provider_calls_permitted: bool = False
    is_execution_authority: bool = False
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    decision_authority: str = "KX108_ONLY"


def prepare_enterprise_sandbox_action_v0(
    *, lifecycle: CompanyStackLifecycleV0,
    link: CompanyStackLinkV0,
    source_proofs: Mapping[str, Any],
    candidate: ActionCandidate, manifest: EnterpriseStackManifestV0,
    capability_id: str, connector_args: Mapping[str, Any],
    target_ref: str, target_prestate_hash: str,
) -> EnterpriseSandboxPreparationV0:
    if not isinstance(link, CompanyStackLinkV0):
        raise ValueError("C3_LINK_REQUIRED")
    if not isinstance(candidate, ActionCandidate):
        raise ValueError("C3_CANDIDATE_REQUIRED")
    if candidate.domain != link.domain_id:
        raise ValueError("C3_CROSS_DOMAIN_INTENT_FORBIDDEN")
    # The caller cannot swap a source's company by attaching an arbitrary
    # source_proofs object; C2 revalidates the company snapshot and registration.
    state = lifecycle.inspect(link.link_id, organization_id=link.organization_id,
                              **dict(source_proofs))
    if state.get("status") != LINK_STATUS:
        raise ValueError("C3_SOURCE_LINK_NOT_CURRENT:" + str(state.get("reason")))
    valid, reason = verify_enterprise_stack_manifest_v0(manifest)
    if not valid:
        raise ValueError("C3_ACTION_MANIFEST_INVALID:" + str(reason))
    if (manifest.manifest_hash != link.manifest_hash
            or manifest.provider_id != link.provider_id
            or manifest.stack_id != link.stack_id
            or source_proofs.get("manifest") != manifest):
        raise ValueError("C3_ACTION_STACK_MUST_EQUAL_ONBOARDED_STACK")
    if candidate.irreversible:
        raise ValueError("C3_SANDBOX_IRREVERSIBLE_CANDIDATE_FORBIDDEN")
    if candidate.payload.get("organization_id") not in (None, link.organization_id):
        raise ValueError("C3_CROSS_TENANT_PAYLOAD_FORBIDDEN")
    if not candidate.action_id or not candidate.actor_id:
        raise ValueError("C3_ACTION_IDENTITY_MISSING")
    # Stable within organization and action; independent from provider identity.
    source_intent = {
        "organization_id": link.organization_id,
        "domain": candidate.domain,
        "action_id": candidate.action_id,
        "actor_id": candidate.actor_id,
    }
    action_scope = canonical_hash(source_intent)[:32]
    scoped = replace(
        candidate,
        action_id="orgsim:" + action_scope,
        actor_id="ENTERPRISE_SANDBOX:" + link.organization_id,
        payload={
            **candidate.payload,
            "organization_id": link.organization_id,
            "source_link_hash": link.link_hash,
            "source_snapshot_hash": link.company_snapshot_hash,
            "evidence_class": "SIMULATED_NOT_OBSERVED",
        },
    )
    binding = build_enterprise_action_binding_v0(
        candidate=scoped, capability_id=capability_id, manifest=manifest,
        connector_args={
            **dict(connector_args),
            "enterprise_org": link.organization_id,
            "enterprise_source_link": link.link_id,
            "sandbox_only": True,
        },
        target_ref="orgsim:" + link.organization_id + ":" + target_ref,
        target_prestate_hash=target_prestate_hash,
    )
    if (binding.world_call_class not in SAFE_WORLD_CALLS
            or binding.action_risk_class not in SAFE_RISK
            or binding.autonomy_level not in (3, 4)):
        raise ValueError("C3_SANDBOX_UNSAFE_ACTION_CAPABILITY")
    request = build_world_action_request_from_enterprise_binding_v0(
        candidate=scoped, manifest=manifest, binding=binding
    )
    if (request.get("allowed_to_act") is not False
            or request.get("allowed_to_decide") is not False
            or request.get("decision_authority") != "KX108_ONLY"):
        raise ValueError("C3_WORLD_ACTION_NON_SOVEREIGN_BOUNDARY_FAILED")
    return EnterpriseSandboxPreparationV0(
        organization_id=link.organization_id,
        source_link_id=link.link_id,
        source_link_hash=link.link_hash,
        source_domain=link.domain_id,
        source_snapshot_hash=link.company_snapshot_hash,
        scoped_action_candidate=scoped,
        action_binding=binding,
        world_action_request=request,
    )
