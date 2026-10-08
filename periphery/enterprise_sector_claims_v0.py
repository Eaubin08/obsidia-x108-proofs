"""V0.1 C4 cross-sector EVIDENCE/CLAIM inventory, not a business classifier.

Profiles transcribe pinned repository documents. Their hashes/commit refs are
references only, never proof of signed provenance or attestation of a client.
This module cannot grant source access, Binder permission, KX decisions or
external execution. Sector-specific semantics remain inside domain adapters.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from periphery.native_ops.common_v0 import canonical_hash

SCHEMA = "OBSIDIA_V01_C4_SECTOR_EVIDENCE_REGISTRY_V0"
AUTHORITY = "KX108_ONLY"
STATUS_ACCEPT = "DOCUMENTED_CLAIM_ONLY_NO_EXECUTION_PERMISSION"
STATUS_REFUSE = "CLAIM_UNSUPPORTED_HOLD"
STATUS_CONFLICT = "SOURCE_EVIDENCE_LABEL_CONFLICT_REVIEW_REQUIRED"
_STATUS = {
    "PARTIAL_REFERENCE_VALIDATED",
    "PARTIAL_RECORDED_PHYSICAL_EVIDENCE",
    "CONTRACT_SHADOW_REAL_INTERNAL_BLOCKED",
}
_GRADE = {
    "REFERENCE_IMPLEMENTATION", "DOCUMENTED_HISTORICAL_TEST",
    "REFERENCE_PAPER_ONLY", "DOCUMENTED_RECORDED_REAL",
    "PARTIAL_TEMPORAL_NOT_CAUSAL", "DOMAIN_CONTRACT_TESTED",
    "DOCUMENTED_PERSONAL_READONLY_SAMPLE", "PREFLIGHT_CONTRACT_ONLY",
}
_MODES = {
    "DESCRIPTIVE_REFERENCE_ONLY", "HISTORICAL_EVIDENCE_ONLY",
    "PAPER_ONLY", "READONLY_EVIDENCE_ONLY", "READONLY_FORENSIC_ONLY",
    "NON_SOVEREIGN_CONTRACT_ONLY",
    "PERSONAL_SHADOW_NO_INTERNAL_PROMOTION", "PREPARATION_ONLY",
}
_TOKEN = re.compile(r"^[A-Z][A-Z0-9_]{2,119}$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_REF = re.compile(r"^[A-Za-z0-9_./-]{1,220}$")


def load_c4_evidence_registry_v0(path: Path) -> dict[str, Any]:
    result = json.loads(Path(path).read_text(encoding="utf-8"))
    verify_c4_evidence_registry_v0(result)
    return result


def verify_c4_evidence_registry_v0(data: Mapping[str, Any]) -> str:
    """Fail-closed schema and vocabulary check; not third-party source attestation."""
    if not isinstance(data, Mapping):
        raise ValueError("C4_REGISTRY_MAPPING_REQUIRED")
    if (data.get("schema") != SCHEMA
            or data.get("authority") != AUTHORITY
            or data.get("verified_production_integration") is not False
            or data.get("registry_role") != "READONLY_CLAIM_CONFORMANCE_NOT_A_DOMAIN_ADAPTER"):
        raise ValueError("C4_REGISTRY_AUTHORITY_OR_SCHEMA_INVALID")
    profiles = data.get("source_contracts")
    if not isinstance(profiles, list) or len(profiles) != 3:
        raise ValueError("C4_REGISTRY_EXACT_THREE_SECTOR_PROFILES_REQUIRED")
    seen: set[str] = set()
    for profile in profiles:
        if not isinstance(profile, Mapping):
            raise ValueError("C4_SECTOR_MAPPING_REQUIRED")
        sid = profile.get("sector_id")
        if not isinstance(sid, str) or not _TOKEN.fullmatch(sid) or sid in seen:
            raise ValueError("C4_SECTOR_ID_INVALID_OR_DUPLICATE")
        seen.add(sid)
        if (not isinstance(profile.get("domain_id"), str)
                or not isinstance(profile.get("repo"), str)
                or not isinstance(profile.get("ref"), str)
                or not isinstance(profile.get("commit"), str)
                or not _SHA.fullmatch(profile["commit"])
                or profile.get("status") not in _STATUS):
            raise ValueError("C4_SECTOR_REFERENCE_OR_STATUS_INVALID")
        paths = profile.get("source_paths")
        if not isinstance(paths, list) or len(set(paths)) != len(paths) or not paths:
            raise ValueError("C4_SECTOR_SOURCE_PATHS_MISSING_OR_DUPLICATE")
        if any(not isinstance(p, str) or not _REF.fullmatch(p) for p in paths):
            raise ValueError("C4_SECTOR_SOURCE_PATH_INVALID")
        claims = profile.get("claims")
        denied = profile.get("forbidden_claims")
        unresolved = profile.get("unresolved")
        if (not isinstance(claims, list) or not claims
                or not isinstance(denied, list) or not denied
                or not isinstance(unresolved, list) or not unresolved):
            raise ValueError("C4_SECTOR_CLAIMS_OR_BLOCKERS_MISSING")
        allow_ids: set[str] = set()
        for item in claims:
            if not isinstance(item, Mapping):
                raise ValueError("C4_CLAIM_MAPPING_REQUIRED")
            cid = item.get("claim_id")
            if (not isinstance(cid, str) or not _TOKEN.fullmatch(cid)
                    or cid in allow_ids
                    or item.get("evidence_grade") not in _GRADE
                    or item.get("allowed_mode") not in _MODES):
                raise ValueError("C4_CLAIM_ID_GRADE_OR_MODE_INVALID")
            allow_ids.add(cid)
            refs = item.get("source_paths")
            if not isinstance(refs, list) or not refs or any(p not in paths for p in refs):
                raise ValueError("C4_CLAIM_SOURCE_REFERENCE_NOT_PINNED")
        if any(not isinstance(x, str) or not _TOKEN.fullmatch(x) for x in denied):
            raise ValueError("C4_DENIED_CLAIM_INVALID")
        if set(denied) & allow_ids or len(denied) != len(set(denied)):
            raise ValueError("C4_FORBIDDEN_CLAIM_COLLISION")
        if not isinstance(profile.get("known_drift"), list):
            raise ValueError("C4_DRIFT_MUST_BE_EXPLICIT")
        if profile.get("quarantined_source_proof_levels", []):
            values = profile["quarantined_source_proof_levels"]
            if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                raise ValueError("C4_QUARANTINE_VALUES_INVALID")
            conflict = profile.get("observed_claim_conflict")
            if (not isinstance(conflict, Mapping)
                    or conflict.get("path") not in paths
                    or conflict.get("field") != "proof_level"):
                raise ValueError("C4_QUARANTINE_CONFLICT_SOURCE_INVALID")
            if conflict.get("observed_value") not in values:
                raise ValueError("C4_QUARANTINE_CONFLICT_LEVEL_MISMATCH")
    if seen != {"TRADING_REFERENCE", "GPS_DEFENSE_PUBLIC_EXPORT", "CSSA_ADMIN_SHADOW"}:
        raise ValueError("C4_SECTOR_PROFILE_SET_INVALID")
    return canonical_hash(dict(data))


def assess_sector_claim_v0(
    registry: Mapping[str, Any], *, sector_id: str, domain_id: str,
    claim_id: str, requested_external_effect: bool = False,
    source_proof_level: str | None = None,
) -> dict[str, Any]:
    """Return only claim readability; success is never authority or a permit."""
    registry_hash = verify_c4_evidence_registry_v0(registry)
    found = next((x for x in registry["source_contracts"]
                  if x["sector_id"] == sector_id), None)
    result = {
        "schema": "OBSIDIA_V01_C4_CLAIM_ASSESSMENT_V0",
        "sector_id": sector_id,
        "domain_id": domain_id,
        "claim_id": claim_id,
        "status": STATUS_REFUSE,
        "reason": "C4_SECTOR_CLAIM_NOT_REGISTERED",
        "evidence_grade": None,
        "allowed_mode": None,
        "source_commit": None,
        "source_paths": [],
        "registry_hash": registry_hash,
        "evidence_sources_independently_verified": False,
        "organizational_authority_verified": False,
        "source_access_authorized": False,
        "runtime_permission_granted": False,
        "real_external_effect_permitted": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": AUTHORITY,
    }
    if found is None or found["domain_id"] != domain_id:
        result["reason"] = "C4_SECTOR_DOMAIN_MISMATCH_OR_UNKNOWN"
    elif requested_external_effect:
        result["reason"] = "C4_EXTERNAL_EFFECT_NOT_PERMITTED"
    elif claim_id in found["forbidden_claims"]:
        result["reason"] = "C4_CLAIM_EXPLICITLY_FORBIDDEN_BY_SECTOR_EVIDENCE"
    else:
        claim = next((x for x in found["claims"] if x["claim_id"] == claim_id), None)
        if claim is not None:
            result.update({
                "source_commit": found["commit"],
                "source_paths": list(claim["source_paths"]),
                "evidence_grade": claim["evidence_grade"],
                "allowed_mode": claim["allowed_mode"],
            })
            if source_proof_level in found.get("quarantined_source_proof_levels", []):
                result["status"] = STATUS_CONFLICT
                result["reason"] = "C4_CONFLICT_WITH_PINNED_SECTOR_CLAIM_MATRIX"
            else:
                result["status"] = STATUS_ACCEPT
                result["reason"] = "C4_REVIEWED_DOCUMENTED_CLAIM_NOT_ATTESTATION"
    result["assessment_hash"] = canonical_hash(result)
    return result
