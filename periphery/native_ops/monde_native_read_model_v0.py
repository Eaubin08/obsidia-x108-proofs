"""MONDE_OBSIDIA_NATIVE_READ_MODEL_V0: non-sovereign, file-backed projection.

Only canonical persisted artefacts are rendered. Unpersisted runtime products
(interpretations, action candidates and provider bindings) remain unavailable,
never synthesized. No filesystem writes, provider calls, or decision execution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from periphery.native_ops.common_v0 import (
    DECISION_AUTHORITY, NativeEntityStoreV0, canonical_hash,
)
from periphery.native_sources.source_runtime_v0 import _packet_payload
from periphery.world_calls.bounded_connector_executor_v0 import (
    verify_execution_receipt_v0,
)

SCHEMA = "MONDE_OBSIDIA_NATIVE_READ_MODEL_V0"
CATEGORY_KINDS = (
    "source", "case", "task", "followup", "interaction", "relationship",
    "interpretation", "action_candidate", "provider_binding",
    "decision", "world_action", "receipt", "alert",
)
STATE_KIND = {
    "TASK_NATIVE_V0": ("task", "native_tasks", "task", "task_id"),
    "CRM_RECORD_NATIVE_V0": ("record", "native_crm", "record", "record_id"),
    "CRM_FOLLOWUP_NATIVE_V0": ("followup", "native_crm", "followup", "followup_id"),
    "CRM_INTERACTION_NATIVE_V0": ("interaction", "native_crm", "interaction", "interaction_id"),
    "CRM_RELATIONSHIP_NATIVE_V0": ("relationship", "native_crm", "relationship", "relationship_id"),
}
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 500


def _safe_files(root: Path | None, pattern: str):
    if root is None or not root.is_dir():
        return []
    base = root.resolve()
    files = sorted(root.rglob(pattern))
    if len(files) > MAX_FILES:
        raise ValueError("MONDE_READ_MODEL_FILE_LIMIT")
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(base):
            raise ValueError("MONDE_READ_MODEL_PATH_ESCAPE")
        if path.is_file():
            yield path


def _json(path: Path) -> dict[str, Any]:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("MONDE_READ_MODEL_FILE_TOO_LARGE")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("MONDE_READ_MODEL_OBJECT_REQUIRED")
    return value


def _node(kind: str, identifier: str, label: str, evidence_hash: str,
          verification: str, **fields: Any) -> dict[str, Any]:
    return {
        "id": f"{kind}:{identifier}", "kind": kind, "label": str(label),
        "evidence_hash": evidence_hash, "verification": verification,
        "source": "CANONICAL_PERSISTED", **fields,
    }


def build_monde_native_read_model_v0(
    *,
    source_runtime_root: Path | None = None,
    native_store_root: Path | None = None,
    governance_root: Path | None = None,
    execution_root: Path | None = None,
) -> dict[str, Any]:
    """Read only, verify available receipts/replay, project allowlisted metadata.

    Missing stores return explicit UNAVAILABLE categories; no mocks are allowed.
    Corruption fails closed instead of silently dropping forged proof objects.
    """
    entities: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    nodes: set[str] = set()
    observed_categories: set[str] = set()

    def add(node: dict[str, Any]):
        if node["id"] in nodes:
            raise ValueError("MONDE_READ_MODEL_DUPLICATE_ID")
        nodes.add(node["id"])
        entities.append(node)
        observed_categories.add(node["kind"])

    def link(a: str, relation: str, b: str):
        if a in nodes and b in nodes:
            item = {"from": a, "type": relation, "to": b}
            if item not in relations:
                relations.append(item)

    # SOURCE_RUNTIME persists content fingerprints, never raw source bodies.
    for path in _safe_files(
        source_runtime_root / "packets" if source_runtime_root else None, "*.json"
    ):
        data = _json(path)
        if data.get("schema") != "OBSIDIA_NATIVE_SOURCE_CONTEXT_PACKET_V0":
            raise ValueError("MONDE_READ_MODEL_PACKET_SCHEMA_INVALID")
        if data.get("allowed_to_decide") is not False or data.get("allowed_to_act") is not False:
            raise ValueError("MONDE_READ_MODEL_PACKET_AUTHORITY_INVALID")
        if data.get("decision_authority") != DECISION_AUTHORITY:
            raise ValueError("MONDE_READ_MODEL_PACKET_AUTHORITY_INVALID")
        if data.get("packet_hash") != canonical_hash(_packet_payload(data)):
            raise ValueError("MONDE_READ_MODEL_PACKET_HASH_MISMATCH")
        add(_node("source", data["packet_id"],
                  f'{data["source_kind"]} · {data["provider"]}',
                  data["packet_hash"], "HASH_VERIFIED",
                  packet_id=data["packet_id"], source_id=data["source_id"],
                  provider=data["provider"], observed_at=data["observed_at"],
                  content_sha256=data["content_sha256"],
                  observation_hash=data["observation_hash"]))

    store = NativeEntityStoreV0(native_store_root) if native_store_root else None
    for path in _safe_files(native_store_root, "state.json"):
        state = _json(path)
        kind_info = STATE_KIND.get(state.get("schema"))
        if kind_info is None:
            # The reader does not reinterpret unknown schemas as canonical.
            continue
        kind, domain, entity_kind, id_field = kind_info
        identifier = state.get(id_field)
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("MONDE_READ_MODEL_ENTITY_ID_INVALID")
        assert store is not None
        expected = store._entity_dir(domain, entity_kind, identifier) / "state.json"
        if path.resolve() != expected.resolve():
            raise ValueError("MONDE_READ_MODEL_ENTITY_PATH_MISMATCH")
        replayed, state_hash = store.replay(domain, entity_kind, identifier)
        if replayed != state or state_hash != canonical_hash(state):
            raise ValueError("MONDE_READ_MODEL_REPLAY_MISMATCH")
        if kind == "record":
            kind = "case" if state.get("record_type") == "CASE" else "record"
        # Deliberately omit free-text descriptions, personal fields and raw content.
        label = state.get("title") or state.get("display_label") or kind.upper()
        node = _node(
            kind, identifier, label, state_hash, "REPLAY_VERIFIED",
            status=state.get("status") or state.get("lifecycle_status"),
            priority=state.get("priority"),
            due_at=state.get("due_at"),
            owner_known=bool(state.get("owner_ref") or state.get("assignee_ref")),
            version=state.get("version"),
        )
        if kind == "followup":
            node["record_ref"] = state.get("record_id")
            node["task_ref"] = state.get("task_ref")
        add(node)
        for receipt in store.receipts(domain, entity_kind, identifier):
            add(_node("receipt", receipt["receipt_id"], "Native mutation receipt",
                      receipt["receipt_hash"], "REPLAY_VERIFIED",
                      receipt_type="NATIVE_MUTATION", version=receipt["version"],
                      created_at=receipt["created_at"]))
            link(node["id"], "HAS_RECEIPT", f'receipt:{receipt["receipt_id"]}')

    for node in list(entities):
        if node["kind"] == "followup":
            link(node["id"], "FOLLOWS_CASE", f'case:{node.get("record_ref")}')
            link(node["id"], "TRACKS_TASK", f'task:{node.get("task_ref")}')

    # PRE decisions are observable but not incorrectly called receipt-verified.
    if governance_root:
        for path in _safe_files(governance_root, "*.json"):
            if path.parent.name != "decisions":
                continue
            data = _json(path)
            did = data.get("decision_record_id")
            digest = data.get("decision_record_hash")
            if not isinstance(did, str) or not isinstance(digest, str) or len(digest) != 64:
                continue
            if data.get("decision_authority") != DECISION_AUTHORITY:
                raise ValueError("MONDE_READ_MODEL_DECISION_AUTHORITY_INVALID")
            add(_node("decision", did, data.get("x108_gate") or "KX108 decision",
                      digest, "OBSERVED_NOT_REPLAY_VERIFIED",
                      gate=data.get("x108_gate"), reason=data.get("reason_code")))

    if execution_root:
        for path in _safe_files(execution_root, "*.json"):
            if path.parent.name != "receipts":
                continue
            receipt = _json(path)
            ok, reason = verify_execution_receipt_v0(receipt)
            if not ok:
                raise ValueError(f"MONDE_READ_MODEL_EXECUTION_RECEIPT_INVALID:{reason}")
            add(_node(
                "receipt", receipt["receipt_id"], "World action execution receipt",
                receipt["receipt_hash"], "HASH_VERIFIED",
                receipt_type="WORLD_ACTION_EXECUTION",
                status=receipt["provider_outcome_status"],
                execution_mode=receipt["execution_mode"],
                real_external_effect=receipt["real_external_effect"],
            ))
            # A receipt proves an action occurred in sandbox, not a provider-live action.
            aid = str(receipt.get("action_id") or "")
            if aid:
                add(_node("world_action", receipt["receipt_id"],
                          "Governed world action · sandbox",
                          receipt["world_action_request_hash"],
                          "EXECUTION_RECEIPT_LINKED",
                          action_id=aid, mode=receipt["execution_mode"]))
                link(f'world_action:{receipt["receipt_id"]}', "HAS_RECEIPT",
                     f'receipt:{receipt["receipt_id"]}')

    entities.sort(key=lambda n: (n["kind"], n["id"]))
    relations.sort(key=lambda n: (n["from"], n["type"], n["to"]))
    availability = {
        category: ("OBSERVED" if category in observed_categories else "UNAVAILABLE")
        for category in CATEGORY_KINDS
    }
    result = {
        "schema": SCHEMA,
        "readonly": True,
        "canonical_truth": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "decision_authority": DECISION_AUTHORITY,
        "observation_scope": "LOCAL_PERSISTED_ONLY",
        "availability": availability,
        "entities": entities,
        "relations": relations,
    }
    result["projection_hash"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("source-runtime-root", "native-store-root", "governance-root", "execution-root"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    try:
        result = build_monde_native_read_model_v0(
            source_runtime_root=args.source_runtime_root,
            native_store_root=args.native_store_root,
            governance_root=args.governance_root,
            execution_root=args.execution_root,
        )
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": SCHEMA, "available": False,
                          "error": str(exc), "readonly": True}))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
