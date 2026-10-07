"""SOURCE_RUNTIME_NATIVE_V0 façade.

This module is the canonical provider-neutral entry point for external
READONLY sources. It does not perform network I/O. Provider adapters feed it
observed source identity/capabilities and item payloads.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from .common_v0 import DECISION_AUTHORITY, canonical_hash, filesystem_component_v0
from .source_onboarding_v0 import (
    NativeHumanSourceAuthorizationV0,
    NativeObservedSourceCandidateV0,
    NativeSourceActivationReceiptV0,
    activate_native_source_v0,
)
from .source_registry_v0 import (
    NativeSourceObservationV0,
    NativeSourceRegistrationV0,
    NativeSourceRegistryV0,
    NativeSourceRevocationV0,
    build_native_source_observation_v0,
    build_native_source_revocation_v0,
    verify_native_source_observation_v0,
)

@dataclass(frozen=True)
class NativeSourceContextPacketV0:
    schema: str
    packet_id: str
    source_id: str
    source_kind: str
    provider: str
    registration_hash: str
    observation_id: str
    observation_hash: str
    content_sha256: str
    metadata_sha256: str
    observed_at: str
    provenance_complete: bool
    allowed_to_decide: bool
    allowed_to_act: bool
    decision_authority: str
    packet_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _packet_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "packet_id", "source_id", "source_kind", "provider",
        "registration_hash", "observation_id", "observation_hash",
        "content_sha256", "metadata_sha256", "observed_at",
        "provenance_complete", "allowed_to_decide", "allowed_to_act",
        "decision_authority",
    )
    return {key: value[key] for key in keys}


class NativeSourceRuntimeV0:
    def __init__(self, root: Path):
        self.root = root
        self.registry = NativeSourceRegistryV0(root / "registry")
        self.observations_root = root / "observations"
        self.packets_root = root / "packets"

    def activate(
        self,
        *,
        candidate: NativeObservedSourceCandidateV0,
        authorization: NativeHumanSourceAuthorizationV0,
        source_id: str,
        activated_at: str,
    ) -> tuple[NativeSourceRegistrationV0, NativeSourceActivationReceiptV0]:
        return activate_native_source_v0(
            candidate=candidate,
            authorization=authorization,
            registry=self.registry,
            source_id=source_id,
            activated_at=activated_at,
        )

    def revoke(
        self,
        *,
        source_id: str,
        revocation_id: str,
        reason: str,
        revoked_by: str,
        revoked_at: str,
    ) -> NativeSourceRevocationV0:
        registration = self.registry.load(source_id)
        if registration is None:
            raise ValueError("NATIVE_SOURCE_NOT_FOUND")
        revocation = build_native_source_revocation_v0(
            registration=registration,
            revocation_id=revocation_id,
            reason=reason,
            revoked_by=revoked_by,
            revoked_at=revoked_at,
        )
        return self.registry.revoke(revocation)

    def observe(
        self,
        *,
        source_id: str,
        provider_item_id: str,
        content: str,
        metadata: Mapping[str, Any],
        observed_at: str,
    ) -> tuple[NativeSourceObservationV0, NativeSourceContextPacketV0]:
        registration = self.registry.load(source_id)
        if registration is None:
            raise ValueError("NATIVE_SOURCE_NOT_FOUND")
        observation = build_native_source_observation_v0(
            registration=registration,
            registry=self.registry,
            provider_item_id=provider_item_id,
            content=content,
            metadata=metadata,
            observed_at=observed_at,
        )
        ok, reason = verify_native_source_observation_v0(
            observation,
            registration=registration,
        )
        if not ok:
            raise ValueError(reason)

        obs_dir = self.observations_root / filesystem_component_v0(source_id)
        obs_dir.mkdir(parents=True, exist_ok=True)
        obs_path = obs_dir / f"{observation.observation_id}.json"
        payload = observation.to_dict()
        if obs_path.exists():
            import json
            existing = json.loads(obs_path.read_text(encoding="utf-8"))
            if existing != payload:
                raise ValueError("NATIVE_SOURCE_OBSERVATION_IMMUTABILITY_CONFLICT")
        else:
            import json
            obs_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        packet_seed = {
            "registration_hash": registration.registration_hash,
            "observation_hash": observation.observation_hash,
        }
        packet_id = f"sourcepacket-{canonical_hash(packet_seed)[:32]}"
        packet_payload = {
            "schema": "OBSIDIA_NATIVE_SOURCE_CONTEXT_PACKET_V0",
            "packet_id": packet_id,
            "source_id": registration.source_id,
            "source_kind": registration.source_kind,
            "provider": registration.provider,
            "registration_hash": registration.registration_hash,
            "observation_id": observation.observation_id,
            "observation_hash": observation.observation_hash,
            "content_sha256": observation.content_sha256,
            "metadata_sha256": observation.metadata_sha256,
            "observed_at": observation.observed_at,
            "provenance_complete": True,
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "decision_authority": DECISION_AUTHORITY,
        }
        packet = NativeSourceContextPacketV0(
            **packet_payload,
            packet_hash=canonical_hash(packet_payload),
        )
        packet_dir = self.packets_root / filesystem_component_v0(source_id)
        packet_dir.mkdir(parents=True, exist_ok=True)
        packet_path = packet_dir / f"{packet.packet_id}.json"
        import json
        packet_dict = packet.to_dict()
        if packet_path.exists():
            existing = json.loads(packet_path.read_text(encoding="utf-8"))
            if existing != packet_dict:
                raise ValueError("NATIVE_SOURCE_PACKET_IMMUTABILITY_CONFLICT")
        else:
            packet_path.write_text(
                json.dumps(packet_dict, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return observation, packet

    def list_observations(self, source_id: str) -> list[dict[str, Any]]:
        directory = self.observations_root / filesystem_component_v0(source_id)
        if not directory.exists():
            return []
        import json
        return [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(directory.glob("*.json"))
        ]

    def list_packets(self, source_id: str) -> list[dict[str, Any]]:
        directory = self.packets_root / filesystem_component_v0(source_id)
        if not directory.exists():
            return []
        import json
        return [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(directory.glob("*.json"))
        ]

    def verify_packet(
        self,
        packet: NativeSourceContextPacketV0 | Mapping[str, Any],
    ) -> tuple[bool, Optional[str]]:
        data = packet.to_dict() if isinstance(packet, NativeSourceContextPacketV0) else dict(packet)
        if data.get("schema") != "OBSIDIA_NATIVE_SOURCE_CONTEXT_PACKET_V0":
            return False, "NATIVE_SOURCE_PACKET_SCHEMA_INVALID"
        registration = self.registry.load(str(data.get("source_id", "")))
        if registration is None:
            return False, "NATIVE_SOURCE_PACKET_SOURCE_NOT_FOUND"
        if not self.registry.is_active(registration.source_id):
            return False, "NATIVE_SOURCE_PACKET_SOURCE_REVOKED"
        if data.get("registration_hash") != registration.registration_hash:
            return False, "NATIVE_SOURCE_PACKET_REGISTRATION_MISMATCH"
        if data.get("source_kind") != registration.source_kind:
            return False, "NATIVE_SOURCE_PACKET_KIND_MISMATCH"
        if data.get("provider") != registration.provider:
            return False, "NATIVE_SOURCE_PACKET_PROVIDER_MISMATCH"
        if data.get("provenance_complete") is not True:
            return False, "NATIVE_SOURCE_PACKET_PROVENANCE_INCOMPLETE"
        if data.get("allowed_to_decide") is not False:
            return False, "NATIVE_SOURCE_PACKET_DECISION_FORBIDDEN"
        if data.get("allowed_to_act") is not False:
            return False, "NATIVE_SOURCE_PACKET_ACTION_FORBIDDEN"
        if data.get("decision_authority") != DECISION_AUTHORITY:
            return False, "NATIVE_SOURCE_PACKET_AUTHORITY_INVALID"
        if canonical_hash(_packet_payload(data)) != data.get("packet_hash"):
            return False, "NATIVE_SOURCE_PACKET_HASH_MISMATCH"
        observations = self.list_observations(registration.source_id)
        matching = [
            obs for obs in observations
            if obs["observation_id"] == data.get("observation_id")
            and obs["observation_hash"] == data.get("observation_hash")
        ]
        if len(matching) != 1:
            return False, "NATIVE_SOURCE_PACKET_OBSERVATION_MISSING"
        return True, None
