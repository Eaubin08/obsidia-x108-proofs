"""Common connector contracts for native READONLY source adapters V0."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional

from .common_v0 import DECISION_AUTHORITY, canonical_hash
from .source_runtime_v0 import NativeSourceContextPacketV0
from .source_registry_v0 import NativeSourceObservationV0


@dataclass(frozen=True)
class NativeConnectorReadReceiptV0:
    schema: str
    receipt_id: str
    connector_kind: str
    source_id: str
    source_kind: str
    provider: str
    registration_hash: str
    provider_item_id_sha256: str
    observation_id: str
    observation_hash: str
    packet_id: str
    packet_hash: str
    read_operation: str
    raw_material_persisted: bool
    external_mutation_performed: bool
    network_call_performed: bool
    decision_authority: str
    receipt_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _receipt_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema",
        "receipt_id",
        "connector_kind",
        "source_id",
        "source_kind",
        "provider",
        "registration_hash",
        "provider_item_id_sha256",
        "observation_id",
        "observation_hash",
        "packet_id",
        "packet_hash",
        "read_operation",
        "raw_material_persisted",
        "external_mutation_performed",
        "network_call_performed",
        "decision_authority",
    )
    return {key: value[key] for key in keys}


def build_native_connector_read_receipt_v0(
    *,
    connector_kind: str,
    read_operation: str,
    observation: NativeSourceObservationV0,
    packet: NativeSourceContextPacketV0,
    network_call_performed: bool,
) -> NativeConnectorReadReceiptV0:
    seed = {
        "connector_kind": connector_kind,
        "source_id": observation.source_id,
        "provider_item_id_sha256": observation.provider_item_id_sha256,
        "observation_hash": observation.observation_hash,
        "packet_hash": packet.packet_hash,
        "read_operation": read_operation,
    }
    payload = {
        "schema": "OBSIDIA_NATIVE_CONNECTOR_READ_RECEIPT_V0",
        "receipt_id": f"connectorread-{canonical_hash(seed)[:32]}",
        "connector_kind": connector_kind,
        "source_id": observation.source_id,
        "source_kind": observation.source_kind,
        "provider": observation.provider,
        "registration_hash": observation.registration_hash,
        "provider_item_id_sha256": observation.provider_item_id_sha256,
        "observation_id": observation.observation_id,
        "observation_hash": observation.observation_hash,
        "packet_id": packet.packet_id,
        "packet_hash": packet.packet_hash,
        "read_operation": read_operation,
        "raw_material_persisted": False,
        "external_mutation_performed": False,
        "network_call_performed": bool(network_call_performed),
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeConnectorReadReceiptV0(
        **payload,
        receipt_hash=canonical_hash(payload),
    )


def verify_native_connector_read_receipt_v0(
    receipt: NativeConnectorReadReceiptV0 | Mapping[str, Any],
) -> tuple[bool, Optional[str]]:
    data = (
        receipt.to_dict()
        if isinstance(receipt, NativeConnectorReadReceiptV0)
        else dict(receipt)
    )
    if data.get("schema") != "OBSIDIA_NATIVE_CONNECTOR_READ_RECEIPT_V0":
        return False, "NATIVE_CONNECTOR_RECEIPT_SCHEMA_INVALID"
    if data.get("raw_material_persisted") is not False:
        return False, "NATIVE_CONNECTOR_RAW_MATERIAL_PERSISTENCE_FORBIDDEN"
    if data.get("external_mutation_performed") is not False:
        return False, "NATIVE_CONNECTOR_EXTERNAL_MUTATION_FORBIDDEN"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_CONNECTOR_AUTHORITY_INVALID"
    if canonical_hash(_receipt_payload(data)) != data.get("receipt_hash"):
        return False, "NATIVE_CONNECTOR_RECEIPT_HASH_MISMATCH"
    return True, None
