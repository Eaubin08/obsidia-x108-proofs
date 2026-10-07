"""Common deterministic primitives for Obsidia native operations V0."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

DECISION_AUTHORITY = "KX108_ONLY"
ABSENT_STATE_HASH = hashlib.sha256(b'{"state":"ABSENT"}').hexdigest()
_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,160}$")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


@dataclass(frozen=True)
class NativeMutationV0:
    schema: str
    mutation_id: str
    domain_id: str
    entity_kind: str
    entity_id: str
    operation: str
    payload: Mapping[str, Any]
    expected_prestate_hash: str
    source_refs: tuple[str, ...]
    requested_by: str
    mutation_hash: str
    decision_authority: str = DECISION_AUTHORITY
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_refs"] = list(self.source_refs)
        return data


def build_native_mutation_v0(
    *,
    mutation_id: str,
    domain_id: str,
    entity_kind: str,
    entity_id: str,
    operation: str,
    payload: Mapping[str, Any],
    expected_prestate_hash: str,
    source_refs: tuple[str, ...],
    requested_by: str,
) -> NativeMutationV0:
    for value in (mutation_id, domain_id, entity_kind, entity_id, operation):
        if not value or str(value).strip() != str(value):
            raise ValueError("NATIVE_MUTATION_IDENTIFIER_INVALID")
    if not _ID_RE.match(entity_id):
        raise ValueError("NATIVE_ENTITY_ID_INVALID")
    if len(expected_prestate_hash) != 64:
        raise ValueError("NATIVE_PRESTATE_HASH_INVALID")
    if not source_refs:
        raise ValueError("NATIVE_MUTATION_SOURCE_REFS_REQUIRED")
    if not requested_by:
        raise ValueError("NATIVE_MUTATION_REQUESTER_REQUIRED")
    seed = {
        "schema": "NATIVE_MUTATION_V0",
        "mutation_id": mutation_id,
        "domain_id": domain_id,
        "entity_kind": entity_kind,
        "entity_id": entity_id,
        "operation": operation,
        "payload": dict(payload),
        "expected_prestate_hash": expected_prestate_hash,
        "source_refs": list(source_refs),
        "requested_by": requested_by,
        "decision_authority": DECISION_AUTHORITY,
    }
    return NativeMutationV0(
        **seed,
        source_refs=tuple(source_refs),
        mutation_hash=canonical_hash(seed),
    )


@dataclass(frozen=True)
class NativeMutationReceiptV0:
    schema: str
    receipt_id: str
    domain_id: str
    entity_kind: str
    entity_id: str
    operation: str
    mutation_id: str
    mutation_hash: str
    world_action_request_hash: str
    kx108_decision_record_id: str
    kx108_decision_record_hash: str
    before_state_hash: str
    after_state_hash: str
    before_state: Optional[Mapping[str, Any]]
    after_state: Optional[Mapping[str, Any]]
    created_at: str
    version: int
    decision_authority: str
    receipt_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _receipt_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema", "receipt_id", "domain_id", "entity_kind", "entity_id",
        "operation", "mutation_id", "mutation_hash",
        "world_action_request_hash", "kx108_decision_record_id",
        "kx108_decision_record_hash", "before_state_hash",
        "after_state_hash", "before_state", "after_state", "created_at",
        "version", "decision_authority",
    )
    return {key: value.get(key) for key in keys}


def verify_native_receipt_v0(
    receipt: NativeMutationReceiptV0 | Mapping[str, Any] | None,
) -> tuple[bool, Optional[str]]:
    if receipt is None:
        return False, "NATIVE_RECEIPT_MISSING"
    data = receipt.to_dict() if isinstance(receipt, NativeMutationReceiptV0) else dict(receipt)
    if data.get("schema") != "NATIVE_MUTATION_RECEIPT_V0":
        return False, "NATIVE_RECEIPT_SCHEMA_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "NATIVE_RECEIPT_AUTHORITY_INVALID"
    if data.get("before_state") is None:
        if data.get("before_state_hash") != ABSENT_STATE_HASH:
            return False, "NATIVE_RECEIPT_ABSENT_PRESTATE_HASH_INVALID"
    else:
        if canonical_hash(data["before_state"]) != data.get("before_state_hash"):
            return False, "NATIVE_RECEIPT_BEFORE_HASH_MISMATCH"
    if data.get("after_state") is None:
        if data.get("after_state_hash") != ABSENT_STATE_HASH:
            return False, "NATIVE_RECEIPT_ABSENT_AFTER_HASH_INVALID"
    else:
        if canonical_hash(data["after_state"]) != data.get("after_state_hash"):
            return False, "NATIVE_RECEIPT_AFTER_HASH_MISMATCH"
    if canonical_hash(_receipt_payload(data)) != data.get("receipt_hash"):
        return False, "NATIVE_RECEIPT_HASH_MISMATCH"
    return True, None


class NativeEntityStoreV0:
    """File-backed append-only receipt store plus canonical current snapshot."""

    def __init__(self, root: Path):
        self.root = root

    def _entity_dir(self, domain_id: str, entity_kind: str, entity_id: str) -> Path:
        if not _ID_RE.match(entity_id):
            raise ValueError("NATIVE_ENTITY_ID_INVALID")
        return self.root / domain_id / entity_kind / entity_id

    def load_state(
        self, domain_id: str, entity_kind: str, entity_id: str
    ) -> Optional[dict[str, Any]]:
        path = self._entity_dir(domain_id, entity_kind, entity_id) / "state.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def state_hash(
        self, domain_id: str, entity_kind: str, entity_id: str
    ) -> str:
        state = self.load_state(domain_id, entity_kind, entity_id)
        return ABSENT_STATE_HASH if state is None else canonical_hash(state)

    def receipts(
        self, domain_id: str, entity_kind: str, entity_id: str
    ) -> list[dict[str, Any]]:
        path = self._entity_dir(domain_id, entity_kind, entity_id) / "receipts"
        if not path.exists():
            return []
        out = []
        for file in sorted(path.glob("*.json")):
            data = json.loads(file.read_text(encoding="utf-8"))
            ok, reason = verify_native_receipt_v0(data)
            if not ok:
                raise ValueError(f"NATIVE_RECEIPT_CORRUPT:{reason}")
            out.append(data)
        return sorted(out, key=lambda x: (x["version"], x["created_at"], x["receipt_id"]))

    def commit(
        self,
        *,
        mutation: NativeMutationV0,
        world_action_request_hash: str,
        kx108_decision_record_id: str,
        kx108_decision_record_hash: str,
        after_state: Optional[Mapping[str, Any]],
        created_at: Optional[str] = None,
    ) -> NativeMutationReceiptV0:
        before = self.load_state(
            mutation.domain_id, mutation.entity_kind, mutation.entity_id
        )
        before_hash = ABSENT_STATE_HASH if before is None else canonical_hash(before)
        if before_hash != mutation.expected_prestate_hash:
            raise ValueError("NATIVE_PRESTATE_CHANGED")

        current_receipts = self.receipts(
            mutation.domain_id, mutation.entity_kind, mutation.entity_id
        )
        version = (current_receipts[-1]["version"] + 1) if current_receipts else 1
        after_dict = None if after_state is None else dict(after_state)
        after_hash = ABSENT_STATE_HASH if after_dict is None else canonical_hash(after_dict)
        observed = created_at or utc_now()
        seed = {
            "domain_id": mutation.domain_id,
            "entity_kind": mutation.entity_kind,
            "entity_id": mutation.entity_id,
            "operation": mutation.operation,
            "mutation_hash": mutation.mutation_hash,
            "world_action_request_hash": world_action_request_hash,
            "kx108_decision_record_hash": kx108_decision_record_hash,
            "before_state_hash": before_hash,
            "after_state_hash": after_hash,
            "version": version,
        }
        receipt_id = f"native-{canonical_hash(seed)[:32]}"
        payload = {
            "schema": "NATIVE_MUTATION_RECEIPT_V0",
            "receipt_id": receipt_id,
            "domain_id": mutation.domain_id,
            "entity_kind": mutation.entity_kind,
            "entity_id": mutation.entity_id,
            "operation": mutation.operation,
            "mutation_id": mutation.mutation_id,
            "mutation_hash": mutation.mutation_hash,
            "world_action_request_hash": world_action_request_hash,
            "kx108_decision_record_id": kx108_decision_record_id,
            "kx108_decision_record_hash": kx108_decision_record_hash,
            "before_state_hash": before_hash,
            "after_state_hash": after_hash,
            "before_state": before,
            "after_state": after_dict,
            "created_at": observed,
            "version": version,
            "decision_authority": DECISION_AUTHORITY,
        }
        payload["receipt_hash"] = canonical_hash(_receipt_payload(payload))
        receipt = NativeMutationReceiptV0(**payload)

        entity_dir = self._entity_dir(
            mutation.domain_id, mutation.entity_kind, mutation.entity_id
        )
        receipt_dir = entity_dir / "receipts"
        receipt_dir.mkdir(parents=True, exist_ok=True)
        receipt_path = receipt_dir / f"{version:08d}-{receipt_id}.json"
        if receipt_path.exists():
            existing = json.loads(receipt_path.read_text(encoding="utf-8"))
            if existing != receipt.to_dict():
                raise ValueError("NATIVE_RECEIPT_IMMUTABILITY_VIOLATION")
        else:
            receipt_path.write_text(
                json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        state_path = entity_dir / "state.json"
        if after_dict is None:
            if state_path.exists():
                state_path.unlink()
        else:
            tmp = entity_dir / f".state.{os.getpid()}.tmp"
            tmp.write_text(
                json.dumps(after_dict, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp, state_path)
        return receipt

    def replay(
        self, domain_id: str, entity_kind: str, entity_id: str
    ) -> tuple[Optional[dict[str, Any]], str]:
        state: Optional[dict[str, Any]] = None
        expected_hash = ABSENT_STATE_HASH
        for receipt in self.receipts(domain_id, entity_kind, entity_id):
            if receipt["before_state_hash"] != expected_hash:
                raise ValueError("NATIVE_REPLAY_CHAIN_BROKEN")
            state = receipt["after_state"]
            expected_hash = receipt["after_state_hash"]
        current = self.load_state(domain_id, entity_kind, entity_id)
        current_hash = ABSENT_STATE_HASH if current is None else canonical_hash(current)
        if current_hash != expected_hash:
            raise ValueError("NATIVE_REPLAY_CURRENT_STATE_MISMATCH")
        return current, current_hash
