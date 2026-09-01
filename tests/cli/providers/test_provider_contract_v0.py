from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from providers import provider_contract_v0 as P


def test_known_provider_set_is_closed():
    assert P.KNOWN_PROVIDERS == ("brody", "obsidure", "claude")
    assert P.normalize_provider("BRODY") == "brody"
    assert P.normalize_provider("unknown") is None


def test_zero_allowed_provider_fails_closed():
    out = P.select_provider([])
    assert out["status"] == "PROVIDER_SELECTION_REJECTED"
    assert out["reason"] == "NO_ALLOWED_PROVIDER"


def test_single_allowed_provider_is_deterministic():
    out = P.select_provider(["brody"])
    assert out["status"] == "PROVIDER_SELECTED"
    assert out["selected_provider"] == "brody"


def test_multiple_allowed_requires_explicit_selection():
    out = P.select_provider(["brody", "claude"])
    assert out["status"] == "PROVIDER_SELECTION_REJECTED"
    assert out["reason"] == "EXPLICIT_PROVIDER_REQUIRED"


def test_explicit_provider_must_be_allowed():
    out = P.select_provider(["brody", "claude"], selected_provider="obsidure")
    assert out["status"] == "PROVIDER_SELECTION_REJECTED"
    assert out["reason"] == "SELECTED_PROVIDER_NOT_ALLOWED"


def test_result_kind_mapping_is_fixed():
    assert P.provider_result_kind("brody") == P.RESULT_EVIDENCE
    assert P.provider_result_kind("claude") == P.RESULT_EVIDENCE
    assert P.provider_result_kind("obsidure") == P.RESULT_PROPOSAL


def test_provider_invocation_is_non_sovereign():
    rec = P.build_provider_invocation(
        relay_mission_id="rmis-" + "a" * 32,
        mission_submission_id="gsub-" + "b" * 32,
        capability_request_ref="gcap-" + "c" * 32,
        lease_id="cclease-" + "d" * 32,
        lease_record_hash="e" * 64,
        selected_provider="BRODY",
        requested_capability="ENGINEERING_REASONING",
        reason="analyse bounded engineering evidence",
    )

    assert rec["selected_provider"] == "brody"
    assert rec["result_kind_expected"] == "EVIDENCE"
    assert rec["is_execution_authority"] is False
    assert rec["is_kx_authority"] is False
    assert rec["is_sovereign"] is False
    assert rec["grants_tool_access"] is False
    assert rec["grants_scope"] is False
    assert P.verify_provider_invocation(rec) == (True, None)


def test_authority_tamper_is_rejected():
    rec = P.build_provider_invocation(
        relay_mission_id="rmis-" + "a" * 32,
        mission_submission_id="gsub-" + "b" * 32,
        capability_request_ref="gcap-" + "c" * 32,
        lease_id="cclease-" + "d" * 32,
        lease_record_hash="e" * 64,
        selected_provider="claude",
        requested_capability="ENGINEERING_REASONING",
        reason="external provider interoperability",
    )
    rec["is_execution_authority"] = True
    ok, why = P.verify_provider_invocation(rec)
    assert ok is False
    assert why == "IS_EXECUTION_AUTHORITY_FORBIDDEN"
