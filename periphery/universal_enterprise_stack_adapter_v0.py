"""UNIVERSAL_ENTERPRISE_STACK_ADAPTER_V0.

Provider-neutral binding between an enterprise's existing tools and Obsidia's
canonical source/action rails. Providers/connectors are interchangeable;
KX108_ONLY, WORLD_ACTION and receipt/replay remain invariant.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional

from periphery.common import ActionCandidate
from periphery.native_ops.common_v0 import DECISION_AUTHORITY, canonical_hash
from periphery.native_ops.native_work_to_action_projection_v0 import (
    build_world_action_request_from_action_candidate_v0,
)
from periphery.native_sources.common_v0 import (
    SOURCE_KINDS,
    validate_readonly_capabilities,
)
from periphery.native_sources.source_onboarding_v0 import (
    NativeObservedSourceCandidateV0,
    build_native_observed_source_candidate_v0,
)
from periphery.validators import validate_action_candidate

MANIFEST_SCHEMA = "UNIVERSAL_ENTERPRISE_STACK_MANIFEST_V0"
ACTION_BINDING_SCHEMA = "UNIVERSAL_ENTERPRISE_ACTION_BINDING_V0"
SOURCE_BINDING_SCHEMA = "UNIVERSAL_ENTERPRISE_SOURCE_BINDING_V0"

_CAPABILITY_RE = re.compile(r"^[A-Z][A-Z0-9_]*(?:\.[A-Z][A-Z0-9_]*)+$")
_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,180}$")
_SECRET_FRAGMENTS = (
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "authorization", "private_key", "access_key", "credential",
)


def _capability(value: str) -> str:
    if not _CAPABILITY_RE.fullmatch(value or ""):
        raise ValueError("ENTERPRISE_CAPABILITY_ID_INVALID")
    return value


def _identifier(value: str, code: str) -> str:
    if not _ID_RE.fullmatch(value or ""):
        raise ValueError(code)
    return value


def _no_secrets(value: Any, path: str = "value") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if any(x in str(key).lower() for x in _SECRET_FRAGMENTS):
                raise ValueError(
                    f"ENTERPRISE_STACK_SECRET_FIELD_FORBIDDEN:{path}.{key}"
                )
            _no_secrets(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _no_secrets(child, f"{path}[{index}]")


@dataclass(frozen=True)
class EnterpriseSourceCapabilityV0:
    capability_id: str
    source_kind: str
    native_read_capabilities: tuple[str, ...]
    adapter_ref: str

    def to_dict(self):
        value = asdict(self)
        value["native_read_capabilities"] = list(self.native_read_capabilities)
        return value


@dataclass(frozen=True)
class EnterpriseActionCapabilityV0:
    capability_id: str
    surface_id: str
    operation_id: str
    connector_id: str
    connector_action: str
    required_scope: str
    effect_class: str
    world_call_class: str
    action_risk_class: str
    autonomy_level: int
    adapter_ref: str


@dataclass(frozen=True)
class EnterpriseStackManifestV0:
    schema: str
    stack_id: str
    provider_id: str
    source_capabilities: tuple[EnterpriseSourceCapabilityV0, ...]
    action_capabilities: tuple[EnterpriseActionCapabilityV0, ...]
    manifest_hash: str
    raw_credentials_persisted: bool = False
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self):
        return {
            "schema": self.schema,
            "stack_id": self.stack_id,
            "provider_id": self.provider_id,
            "source_capabilities": [x.to_dict() for x in self.source_capabilities],
            "action_capabilities": [asdict(x) for x in self.action_capabilities],
            "manifest_hash": self.manifest_hash,
            "raw_credentials_persisted": self.raw_credentials_persisted,
            "allowed_to_decide": self.allowed_to_decide,
            "allowed_to_act": self.allowed_to_act,
            "emits_act": self.emits_act,
            "decision_authority": self.decision_authority,
        }


@dataclass(frozen=True)
class EnterpriseActionBindingV0:
    schema: str
    binding_id: str
    stack_id: str
    provider_id: str
    manifest_hash: str
    capability_id: str
    stable_intent_hash: str
    action_id: str
    surface_id: str
    operation_id: str
    connector_id: str
    connector_action: str
    connector_args: Mapping[str, Any]
    target_ref: str
    target_prestate_hash: str
    required_scope: str
    effect_class: str
    world_call_class: str
    action_risk_class: str
    autonomy_level: int
    adapter_ref: str
    binding_hash: str
    raw_credentials_persisted: bool = False
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self):
        value = asdict(self)
        value["connector_args"] = dict(self.connector_args)
        return value


@dataclass(frozen=True)
class EnterpriseSourceBindingV0:
    schema: str
    binding_id: str
    stack_id: str
    provider_id: str
    manifest_hash: str
    capability_id: str
    source_kind: str
    native_read_capabilities: tuple[str, ...]
    adapter_ref: str
    source_identity_sha256: str
    connector_reference: str
    binding_hash: str
    raw_credentials_persisted: bool = False
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    decision_authority: str = DECISION_AUTHORITY


def build_enterprise_source_capability_v0(
    *, capability_id: str, source_kind: str,
    native_read_capabilities: tuple[str, ...], adapter_ref: str,
) -> EnterpriseSourceCapabilityV0:
    _capability(capability_id)
    if source_kind not in SOURCE_KINDS:
        raise ValueError("ENTERPRISE_SOURCE_KIND_INVALID")
    return EnterpriseSourceCapabilityV0(
        capability_id=capability_id,
        source_kind=source_kind,
        native_read_capabilities=validate_readonly_capabilities(
            native_read_capabilities
        ),
        adapter_ref=_identifier(
            adapter_ref, "ENTERPRISE_SOURCE_ADAPTER_REF_INVALID"
        ),
    )


def build_enterprise_action_capability_v0(
    *, capability_id: str, surface_id: str, operation_id: str,
    connector_id: str, connector_action: str, required_scope: str,
    effect_class: str, world_call_class: str, action_risk_class: str,
    autonomy_level: int, adapter_ref: str,
) -> EnterpriseActionCapabilityV0:
    _capability(capability_id)
    for value, code in (
        (surface_id, "ENTERPRISE_SURFACE_ID_INVALID"),
        (operation_id, "ENTERPRISE_OPERATION_ID_INVALID"),
        (connector_id, "ENTERPRISE_CONNECTOR_ID_INVALID"),
        (connector_action, "ENTERPRISE_CONNECTOR_ACTION_INVALID"),
        (adapter_ref, "ENTERPRISE_ACTION_ADAPTER_REF_INVALID"),
    ):
        _identifier(value, code)
    if not all((required_scope, effect_class, world_call_class, action_risk_class)):
        raise ValueError("ENTERPRISE_ACTION_BINDING_FIELDS_REQUIRED")
    if autonomy_level not in (3, 4):
        raise ValueError("ENTERPRISE_ACTION_AUTONOMY_LEVEL_UNSUPPORTED")
    return EnterpriseActionCapabilityV0(
        capability_id, surface_id, operation_id, connector_id,
        connector_action, required_scope, effect_class, world_call_class,
        action_risk_class, autonomy_level, adapter_ref,
    )


def _manifest_payload(
    stack_id: str, provider_id: str,
    sources: tuple[EnterpriseSourceCapabilityV0, ...],
    actions: tuple[EnterpriseActionCapabilityV0, ...],
):
    return {
        "schema": MANIFEST_SCHEMA,
        "stack_id": stack_id,
        "provider_id": provider_id,
        "source_capabilities": [x.to_dict() for x in sources],
        "action_capabilities": [asdict(x) for x in actions],
        "raw_credentials_persisted": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }


def build_enterprise_stack_manifest_v0(
    *, stack_id: str, provider_id: str,
    source_capabilities: tuple[EnterpriseSourceCapabilityV0, ...] = (),
    action_capabilities: tuple[EnterpriseActionCapabilityV0, ...] = (),
) -> EnterpriseStackManifestV0:
    _identifier(stack_id, "ENTERPRISE_STACK_ID_INVALID")
    _identifier(provider_id, "ENTERPRISE_PROVIDER_ID_INVALID")
    if not source_capabilities and not action_capabilities:
        raise ValueError("ENTERPRISE_STACK_CAPABILITIES_REQUIRED")
    sources = tuple(sorted(source_capabilities, key=lambda x: x.capability_id))
    actions = tuple(sorted(action_capabilities, key=lambda x: x.capability_id))
    if len({x.capability_id for x in sources}) != len(sources):
        raise ValueError("ENTERPRISE_SOURCE_CAPABILITY_DUPLICATE")
    if len({x.capability_id for x in actions}) != len(actions):
        raise ValueError("ENTERPRISE_ACTION_CAPABILITY_DUPLICATE")
    payload = _manifest_payload(stack_id, provider_id, sources, actions)
    return EnterpriseStackManifestV0(
        MANIFEST_SCHEMA, stack_id, provider_id, sources, actions,
        canonical_hash(payload),
    )


def verify_enterprise_stack_manifest_v0(
    manifest: EnterpriseStackManifestV0 | None,
) -> tuple[bool, Optional[str]]:
    if not isinstance(manifest, EnterpriseStackManifestV0):
        return False, "ENTERPRISE_STACK_MANIFEST_TYPE_INVALID"
    if manifest.schema != MANIFEST_SCHEMA:
        return False, "ENTERPRISE_STACK_MANIFEST_SCHEMA_INVALID"
    if (
        manifest.raw_credentials_persisted
        or manifest.allowed_to_decide
        or manifest.allowed_to_act
        or manifest.emits_act
    ):
        return False, "ENTERPRISE_STACK_MANIFEST_AUTHORITY_INVALID"
    if manifest.decision_authority != DECISION_AUTHORITY:
        return False, "ENTERPRISE_STACK_AUTHORITY_INVALID"
    expected = canonical_hash(_manifest_payload(
        manifest.stack_id, manifest.provider_id,
        manifest.source_capabilities, manifest.action_capabilities,
    ))
    if manifest.manifest_hash != expected:
        return False, "ENTERPRISE_STACK_MANIFEST_HASH_MISMATCH"
    return True, None


def stable_business_intent_hash_v0(
    candidate: ActionCandidate, *, capability_id: str,
) -> str:
    validate_action_candidate(candidate)
    _capability(capability_id)
    return canonical_hash({
        "schema": "UNIVERSAL_ENTERPRISE_STABLE_BUSINESS_INTENT_V0",
        "capability_id": capability_id,
        "action_candidate": asdict(candidate),
    })


def _action(
    manifest: EnterpriseStackManifestV0, capability_id: str,
) -> EnterpriseActionCapabilityV0:
    ok, reason = verify_enterprise_stack_manifest_v0(manifest)
    if not ok:
        raise ValueError(reason)
    matches = [
        x for x in manifest.action_capabilities
        if x.capability_id == _capability(capability_id)
    ]
    if len(matches) != 1:
        raise ValueError(
            "ENTERPRISE_ACTION_CAPABILITY_UNAVAILABLE"
            if not matches else "ENTERPRISE_ACTION_CAPABILITY_AMBIGUOUS"
        )
    return matches[0]


def build_enterprise_action_binding_v0(
    *, candidate: ActionCandidate, capability_id: str,
    manifest: EnterpriseStackManifestV0,
    connector_args: Mapping[str, Any], target_ref: str,
    target_prestate_hash: str,
) -> EnterpriseActionBindingV0:
    validate_action_candidate(candidate)
    action = _action(manifest, capability_id)
    if candidate.payload.get("surface_id") != action.surface_id:
        raise ValueError("ENTERPRISE_ACTION_SURFACE_MISMATCH")
    if candidate.payload.get("operation_id") != action.operation_id:
        raise ValueError("ENTERPRISE_ACTION_OPERATION_MISMATCH")
    if not target_ref or len(target_prestate_hash) != 64:
        raise ValueError("ENTERPRISE_ACTION_TARGET_BINDING_INVALID")
    _no_secrets(connector_args, "connector_args")
    stable = stable_business_intent_hash_v0(
        candidate, capability_id=capability_id
    )
    payload = {
        "schema": ACTION_BINDING_SCHEMA,
        "stack_id": manifest.stack_id,
        "provider_id": manifest.provider_id,
        "manifest_hash": manifest.manifest_hash,
        "capability_id": capability_id,
        "stable_intent_hash": stable,
        "action_id": candidate.action_id,
        "surface_id": action.surface_id,
        "operation_id": action.operation_id,
        "connector_id": action.connector_id,
        "connector_action": action.connector_action,
        "connector_args": dict(connector_args),
        "target_ref": target_ref,
        "target_prestate_hash": target_prestate_hash,
        "required_scope": action.required_scope,
        "effect_class": action.effect_class,
        "world_call_class": action.world_call_class,
        "action_risk_class": action.action_risk_class,
        "autonomy_level": action.autonomy_level,
        "adapter_ref": action.adapter_ref,
        "raw_credentials_persisted": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    digest = canonical_hash(payload)
    return EnterpriseActionBindingV0(
        **payload,
        binding_id=f"enterprise-action-binding:{digest[:32]}",
        binding_hash=digest,
    )


def verify_enterprise_action_binding_v0(
    binding: EnterpriseActionBindingV0, *, candidate: ActionCandidate,
    manifest: EnterpriseStackManifestV0,
) -> tuple[bool, Optional[str]]:
    if binding.schema != ACTION_BINDING_SCHEMA:
        return False, "ENTERPRISE_ACTION_BINDING_SCHEMA_INVALID"
    if (
        binding.raw_credentials_persisted
        or binding.allowed_to_decide
        or binding.allowed_to_act
        or binding.emits_act
    ):
        return False, "ENTERPRISE_ACTION_BINDING_AUTHORITY_FORBIDDEN"
    if binding.decision_authority != DECISION_AUTHORITY:
        return False, "ENTERPRISE_ACTION_BINDING_AUTHORITY_INVALID"
    if (
        binding.manifest_hash != manifest.manifest_hash
        or binding.provider_id != manifest.provider_id
        or binding.stack_id != manifest.stack_id
    ):
        return False, "ENTERPRISE_ACTION_BINDING_MANIFEST_MISMATCH"
    if binding.stable_intent_hash != stable_business_intent_hash_v0(
        candidate, capability_id=binding.capability_id
    ):
        return False, "ENTERPRISE_ACTION_BINDING_INTENT_MISMATCH"
    action = _action(manifest, binding.capability_id)
    for field in (
        "surface_id", "operation_id", "connector_id", "connector_action",
        "required_scope", "effect_class", "world_call_class",
        "action_risk_class", "autonomy_level", "adapter_ref",
    ):
        if getattr(binding, field) != getattr(action, field):
            return False, f"ENTERPRISE_ACTION_BINDING_FIELD_MISMATCH:{field}"
    try:
        _no_secrets(binding.connector_args, "connector_args")
    except ValueError as exc:
        return False, str(exc)
    payload = binding.to_dict()
    payload.pop("binding_id")
    payload.pop("binding_hash")
    digest = canonical_hash(payload)
    if binding.binding_hash != digest:
        return False, "ENTERPRISE_ACTION_BINDING_HASH_MISMATCH"
    if binding.binding_id != f"enterprise-action-binding:{digest[:32]}":
        return False, "ENTERPRISE_ACTION_BINDING_ID_MISMATCH"
    return True, None


def build_world_action_request_from_enterprise_binding_v0(
    *, candidate: ActionCandidate, manifest: EnterpriseStackManifestV0,
    binding: EnterpriseActionBindingV0,
) -> dict[str, Any]:
    ok, reason = verify_enterprise_action_binding_v0(
        binding, candidate=candidate, manifest=manifest
    )
    if not ok:
        raise ValueError(reason)
    return build_world_action_request_from_action_candidate_v0(
        candidate,
        connector_id=binding.connector_id,
        connector_action=binding.connector_action,
        connector_args=binding.connector_args,
        target_ref=binding.target_ref,
        target_prestate_hash=binding.target_prestate_hash,
        required_scope=binding.required_scope,
        effect_class=binding.effect_class,
        world_call_class=binding.world_call_class,
        action_risk_class=binding.action_risk_class,
        autonomy_level=binding.autonomy_level,
    )


def build_enterprise_source_binding_v0(
    *, manifest: EnterpriseStackManifestV0, capability_id: str,
    source_identity_sha256: str, connector_reference: str,
) -> EnterpriseSourceBindingV0:
    ok, reason = verify_enterprise_stack_manifest_v0(manifest)
    if not ok:
        raise ValueError(reason)
    matches = [
        x for x in manifest.source_capabilities
        if x.capability_id == _capability(capability_id)
    ]
    if len(matches) != 1:
        raise ValueError("ENTERPRISE_SOURCE_CAPABILITY_UNAVAILABLE")
    source = matches[0]
    if len(source_identity_sha256) != 64:
        raise ValueError("ENTERPRISE_SOURCE_IDENTITY_HASH_INVALID")
    _identifier(
        connector_reference, "ENTERPRISE_SOURCE_CONNECTOR_REFERENCE_INVALID"
    )
    payload = {
        "schema": SOURCE_BINDING_SCHEMA,
        "stack_id": manifest.stack_id,
        "provider_id": manifest.provider_id,
        "manifest_hash": manifest.manifest_hash,
        "capability_id": capability_id,
        "source_kind": source.source_kind,
        "native_read_capabilities": list(source.native_read_capabilities),
        "adapter_ref": source.adapter_ref,
        "source_identity_sha256": source_identity_sha256,
        "connector_reference": connector_reference,
        "raw_credentials_persisted": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }
    digest = canonical_hash(payload)
    return EnterpriseSourceBindingV0(
        SOURCE_BINDING_SCHEMA,
        f"enterprise-source-binding:{digest[:32]}",
        manifest.stack_id,
        manifest.provider_id,
        manifest.manifest_hash,
        capability_id,
        source.source_kind,
        source.native_read_capabilities,
        source.adapter_ref,
        source_identity_sha256,
        connector_reference,
        digest,
    )


def build_native_source_candidate_from_enterprise_binding_v0(
    *, binding: EnterpriseSourceBindingV0, candidate_id: str,
    observed_at: str,
) -> NativeObservedSourceCandidateV0:
    return build_native_observed_source_candidate_v0(
        candidate_id=candidate_id,
        source_kind=binding.source_kind,
        provider=binding.provider_id,
        source_identity_sha256=binding.source_identity_sha256,
        observed_capabilities=binding.native_read_capabilities,
        connector_reference=binding.connector_reference,
        observed_at=observed_at,
    )


def provider_swap_invariant_v0(
    *, candidate: ActionCandidate, capability_id: str,
    bindings: tuple[EnterpriseActionBindingV0, ...],
) -> tuple[bool, Optional[str]]:
    if len(bindings) < 2:
        return False, "ENTERPRISE_PROVIDER_SWAP_REQUIRES_MULTIPLE_BINDINGS"
    stable = stable_business_intent_hash_v0(
        candidate, capability_id=capability_id
    )
    if any(x.capability_id != capability_id for x in bindings):
        return False, "ENTERPRISE_PROVIDER_SWAP_CAPABILITY_MISMATCH"
    if any(x.stable_intent_hash != stable for x in bindings):
        return False, "ENTERPRISE_PROVIDER_SWAP_INTENT_DRIFT"
    if len({x.provider_id for x in bindings}) != len(bindings):
        return False, "ENTERPRISE_PROVIDER_SWAP_PROVIDER_NOT_DISTINCT"
    if len({x.binding_hash for x in bindings}) != len(bindings):
        return False, "ENTERPRISE_PROVIDER_SWAP_BINDING_NOT_DISTINCT"
    return True, None
