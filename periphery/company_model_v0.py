"""V0.1 Company Model C1 — evidence-aware non-sovereign ORGANIZATION view.

This is a detached, deterministic *projection* of explicitly supplied claims.
It never discovers accounts, checks organizational ownership, issues permission,
mutates a source/CRM, dispatches a provider or invokes KX108.

DECLARED, OBSERVED_CLAIM, TESTED_CLAIM and PROVEN_CLAIM describe what the
submitter CLAIMS; none are promoted to verified organizational truth by this
module. Proof references are references, not attestation.
"""
from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, asdict
from typing import Iterable

from periphery.native_ops.common_v0 import canonical_hash

SCHEMA = "OBSIDIA_V01_COMPANY_MODEL_V0"
AUTHORITY = "KX108_ONLY"
KINDS = frozenset({
    "ORGANIZATION", "TEAM_ROLE", "TOOL_INSTANCE", "PROCESS",
    "RESPONSIBILITY", "DEPENDENCY", "SOURCE", "DOMAIN_BINDING",
})
RELATIONS = frozenset({
    "HAS_ROLE", "USES_TOOL", "OPERATES_PROCESS", "HAS_RESPONSIBILITY",
    "DEPENDS_ON", "HAS_SOURCE", "BINDS_DOMAIN", "REPORTS_TO",
})
STATES = frozenset({"DECLARED", "OBSERVED_CLAIM", "TESTED_CLAIM", "PROVEN_CLAIM"})
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,200}$")


def _ident(value: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("COMPANY_MODEL_ID_INVALID")
    return value


def _refs(values: Iterable[str], *, required: bool = False) -> tuple[str, ...]:
    if isinstance(values, str):
        raise ValueError("COMPANY_MODEL_REF_SEQUENCE_REQUIRED")
    refs = tuple(values)
    if required and not refs:
        raise ValueError("COMPANY_MODEL_PROVENANCE_REQUIRED")
    if len(refs) > 30 or len(set(refs)) != len(refs):
        raise ValueError("COMPANY_MODEL_REFS_DUPLICATE_OR_TOO_MANY")
    if any(not isinstance(v, str) or not _REF.fullmatch(v) for v in refs):
        raise ValueError("COMPANY_MODEL_REF_INVALID")
    return refs


def _at(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("COMPANY_MODEL_TIME_INVALID")
    try:
        if datetime.datetime.fromisoformat(value).utcoffset() is None:
            raise ValueError("COMPANY_MODEL_TIME_UNAWARE")
    except (TypeError, ValueError) as exc:
        raise ValueError("COMPANY_MODEL_TIME_INVALID") from exc
    return value


@dataclass(frozen=True)
class CompanyNodeV0:
    schema: str
    organization_id: str
    record_id: str
    kind: str
    claim_state: str
    valid_at: str
    provenance_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    verification: str
    decision_authority: str
    allowed_to_decide: bool
    allowed_to_act: bool
    node_hash: str


@dataclass(frozen=True)
class CompanyRelationV0:
    schema: str
    organization_id: str
    relation_id: str
    from_record_id: str
    to_record_id: str
    relation_kind: str
    claim_state: str
    valid_at: str
    provenance_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    verification: str
    decision_authority: str
    allowed_to_decide: bool
    allowed_to_act: bool
    relation_hash: str


def _make_payload(schema: str, fields: dict) -> dict:
    return {
        "schema": schema, **fields,
        "verification": "UNVERIFIED_ORGANIZATIONAL_CLAIM",
        "decision_authority": AUTHORITY,
        "allowed_to_decide": False,
        "allowed_to_act": False,
    }


def company_node_v0(
    *, organization_id: str, record_id: str, kind: str, claim_state: str,
    valid_at: str, provenance_refs: Iterable[str], evidence_refs: Iterable[str] = (),
) -> CompanyNodeV0:
    org, rid = _ident(organization_id), _ident(record_id)
    if kind not in KINDS or claim_state not in STATES:
        raise ValueError("COMPANY_MODEL_KIND_OR_STATE_INVALID")
    if kind == "ORGANIZATION" and rid != org:
        raise ValueError("COMPANY_MODEL_ORGANIZATION_ROOT_ID_MISMATCH")
    provenance = _refs(provenance_refs, required=True)
    evidence = _refs(evidence_refs)
    if claim_state != "DECLARED" and not evidence:
        raise ValueError("COMPANY_MODEL_NONDECLARED_EVIDENCE_REQUIRED")
    data = _make_payload("COMPANY_NODE_V0", {
        "organization_id": org, "record_id": rid, "kind": kind,
        "claim_state": claim_state, "valid_at": _at(valid_at),
        "provenance_refs": provenance, "evidence_refs": evidence,
    })
    return CompanyNodeV0(**data, node_hash=canonical_hash(data))


def company_relation_v0(
    *, organization_id: str, relation_id: str, from_record_id: str,
    to_record_id: str, relation_kind: str, claim_state: str, valid_at: str,
    provenance_refs: Iterable[str], evidence_refs: Iterable[str] = (),
) -> CompanyRelationV0:
    org, rid = _ident(organization_id), _ident(relation_id)
    source, target = _ident(from_record_id), _ident(to_record_id)
    if relation_kind not in RELATIONS or claim_state not in STATES:
        raise ValueError("COMPANY_MODEL_RELATION_KIND_OR_STATE_INVALID")
    if source == target:
        raise ValueError("COMPANY_MODEL_SELF_RELATION_FORBIDDEN")
    provenance = _refs(provenance_refs, required=True)
    evidence = _refs(evidence_refs)
    if claim_state != "DECLARED" and not evidence:
        raise ValueError("COMPANY_MODEL_NONDECLARED_EVIDENCE_REQUIRED")
    data = _make_payload("COMPANY_RELATION_V0", {
        "organization_id": org, "relation_id": rid,
        "from_record_id": source, "to_record_id": target,
        "relation_kind": relation_kind, "claim_state": claim_state,
        "valid_at": _at(valid_at),
        "provenance_refs": provenance, "evidence_refs": evidence,
    })
    return CompanyRelationV0(**data, relation_hash=canonical_hash(data))


def _verify_obj(item: CompanyNodeV0 | CompanyRelationV0, digest_key: str) -> None:
    data = asdict(item)
    if (
        data["schema"] not in {"COMPANY_NODE_V0", "COMPANY_RELATION_V0"}
        or data["verification"] != "UNVERIFIED_ORGANIZATIONAL_CLAIM"
        or data["decision_authority"] != AUTHORITY
        or data["allowed_to_decide"] is not False
        or data["allowed_to_act"] is not False
    ):
        raise ValueError("COMPANY_MODEL_AUTHORITY_OR_CONTRACT_INVALID")
    digest = data.pop(digest_key)
    if canonical_hash(data) != digest:
        raise ValueError("COMPANY_MODEL_OBJECT_HASH_INVALID")


def company_model_snapshot_v0(
    organization_id: str,
    nodes: Iterable[CompanyNodeV0],
    relations: Iterable[CompanyRelationV0],
) -> dict:
    """Read-only, tenant-isolated claim graph; never implies permission."""
    org = _ident(organization_id)
    nodes, relations = tuple(nodes), tuple(relations)
    if not nodes or len(nodes) > 1000 or len(relations) > 3000:
        raise ValueError("COMPANY_MODEL_BOUNDS_INVALID")
    identifiers: set[str] = set()
    roots = 0
    for node in nodes:
        if not isinstance(node, CompanyNodeV0):
            raise ValueError("COMPANY_MODEL_NODE_TYPE_INVALID")
        _verify_obj(node, "node_hash")
        if node.organization_id != org:
            raise ValueError("COMPANY_MODEL_CROSS_TENANT_NODE")
        if node.record_id in identifiers:
            raise ValueError("COMPANY_MODEL_DUPLICATE_NODE")
        identifiers.add(node.record_id)
        roots += int(node.kind == "ORGANIZATION" and node.record_id == org)
    if roots != 1:
        raise ValueError("COMPANY_MODEL_ORGANIZATION_ROOT_REQUIRED")
    relation_ids: set[str] = set()
    for relation in relations:
        if not isinstance(relation, CompanyRelationV0):
            raise ValueError("COMPANY_MODEL_RELATION_TYPE_INVALID")
        _verify_obj(relation, "relation_hash")
        if relation.organization_id != org:
            raise ValueError("COMPANY_MODEL_CROSS_TENANT_RELATION")
        if relation.relation_id in relation_ids:
            raise ValueError("COMPANY_MODEL_DUPLICATE_RELATION")
        relation_ids.add(relation.relation_id)
        if relation.from_record_id not in identifiers or relation.to_record_id not in identifiers:
            raise ValueError("COMPANY_MODEL_DANGLING_RELATION")
    def public_record(item):
        value = asdict(item)
        value["provenance_refs"] = list(value["provenance_refs"])
        value["evidence_refs"] = list(value["evidence_refs"])
        return value

    records = [public_record(v) for v in sorted(nodes, key=lambda n: n.record_id)]
    links = [public_record(v) for v in sorted(relations, key=lambda n: n.relation_id)]
    model = {
        "schema": SCHEMA,
        "organization_id": org,
        "readonly": True,
        "canonical_truth": False,
        "organization_authority_verified": False,
        "is_execution_authority": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": AUTHORITY,
        "truth_scope": "PROVENANCE_BOUND_CLAIMS_NOT_VERIFIED_ORG_TRUTH",
        "nodes": records,
        "relations": links,
    }
    model["snapshot_hash"] = canonical_hash(model)
    return model


def verify_company_model_snapshot_v0(model: dict) -> tuple[bool, str | None]:
    """Recompute the deterministic graph instead of trusting self-signed hashes."""
    try:
        if not isinstance(model, dict) or model.get("schema") != SCHEMA:
            return False, "COMPANY_MODEL_SCHEMA_INVALID"
        if set(model) != {
            "schema", "organization_id", "readonly", "canonical_truth",
            "organization_authority_verified", "is_execution_authority",
            "allowed_to_decide", "allowed_to_act", "decision_authority",
            "truth_scope", "nodes", "relations", "snapshot_hash",
        }:
            return False, "COMPANY_MODEL_FIELDS_INVALID"
        if model["readonly"] is not True or model["canonical_truth"] is not False or model["organization_authority_verified"] is not False:
            return False, "COMPANY_MODEL_TRUTH_ESCALATION"
        nodes = [CompanyNodeV0(**{**node, "provenance_refs": tuple(node["provenance_refs"]), "evidence_refs": tuple(node["evidence_refs"])}) for node in model["nodes"]]
        links = [CompanyRelationV0(**{**link, "provenance_refs": tuple(link["provenance_refs"]), "evidence_refs": tuple(link["evidence_refs"])}) for link in model["relations"]]
        expected = company_model_snapshot_v0(model["organization_id"], nodes, links)
        if expected != model:
            return False, "COMPANY_MODEL_SNAPSHOT_MISMATCH"
        return True, None
    except (ValueError, TypeError, KeyError, AttributeError):
        return False, "COMPANY_MODEL_VERIFICATION_FAILED"
