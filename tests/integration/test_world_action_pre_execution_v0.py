import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import obsidia_kx108_decision_store as DS  # noqa: E402
import obsidia_world_action_pre_execution_context_v0 as CTX  # noqa: E402
from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    build_world_action_pre_dry_run_evidence_v0,
    run_world_action_pre_execution_v0,
)
from scripts.kernel.kx108_runtime_link_facts_v1 import (  # noqa: E402
    MISSING_RUNTIME_LINK_REAL_EXECUTION,
    MISSING_RUNTIME_LINK_WORLD_ACTUATION,
    runtime_link_facts,
    world_action_pre_execution_rail_present,
)


def canonical_hash(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def build_request(
    *,
    domain="administration",
    world_call_class="IRREVERSIBLE_WORLD_CALL",
    action_risk_class="ACTION_IRREVERSIBLE",
    autonomy_level=5,
    connector_args=None,
):
    connector_args = connector_args or {
        "to": "supporter@example.invalid",
        "subject": "Information CSSA",
        "body": "Coup d'envoi confirme.",
        "content_type": "text/plain",
        "reply_message_id": None,
    }
    request = {
        "request_id": f"world-{domain}-001",
        "proposal_id": f"proposal-{domain}-001",
        "proposal_hash": canonical_hash({"proposal": domain}),
        "domain_id": domain,
        "surface_id": "MAIL",
        "operation_id": "DRAFT_NOTIFICATION",
        "effect_class": "EXTERNAL_COMMUNICATION",
        "connector_id": "GMAIL",
        "connector_action": "SEND_EMAIL",
        "connector_args": connector_args,
        "target_ref": f"target:{domain}:001",
        "target_prestate_hash": canonical_hash({"target": domain}),
        "required_scope": "gmail:send",
        "world_call_class": world_call_class,
        "action_risk_class": action_risk_class,
        "autonomy_level": autonomy_level,
        "irreversible": True,
        "retry_policy": "NEVER_AUTORETRY_ON_UNKNOWN",
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
    }
    request["connector_call_hash"] = canonical_hash(
        {
            "connector_id": request["connector_id"],
            "connector_action": request["connector_action"],
            "connector_args": request["connector_args"],
        }
    )
    request["idempotency_key"] = canonical_hash(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_IDEMPOTENCY_V0",
            "proposal_hash": request["proposal_hash"],
            "connector_call_hash": request["connector_call_hash"],
            "target_prestate_hash": request["target_prestate_hash"],
            "required_scope": request["required_scope"],
        }
    )
    request["request_hash"] = canonical_hash(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_REQUEST_V0",
            "request_id": request["request_id"],
            "proposal_id": request["proposal_id"],
            "proposal_hash": request["proposal_hash"],
            "domain_id": request["domain_id"],
            "surface_id": request["surface_id"],
            "operation_id": request["operation_id"],
            "effect_class": request["effect_class"],
            "connector_id": request["connector_id"],
            "connector_action": request["connector_action"],
            "connector_args": request["connector_args"],
            "connector_call_hash": request["connector_call_hash"],
            "target_ref": request["target_ref"],
            "target_prestate_hash": request["target_prestate_hash"],
            "required_scope": request["required_scope"],
            "world_call_class": request["world_call_class"],
            "action_risk_class": request["action_risk_class"],
            "autonomy_level": request["autonomy_level"],
            "irreversible": request["irreversible"],
            "retry_policy": request["retry_policy"],
            "idempotency_key": request["idempotency_key"],
            "decision_authority": request["decision_authority"],
        }
    )
    return request


def build_approval(request):
    approval = {
        "schema": "UNIVERSAL_WORLD_ACTION_HUMAN_APPROVAL_V0",
        "approval_id": f"approval-{request['request_id']}",
        "approved_by": "HUMAN:REVIEWER",
        "approval_reference": f"review:{request['request_id']}",
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "proposal_hash": request["proposal_hash"],
        "domain_id": request["domain_id"],
        "surface_id": request["surface_id"],
        "operation_id": request["operation_id"],
        "connector_id": request["connector_id"],
        "connector_action": request["connector_action"],
        "connector_call_hash": request["connector_call_hash"],
        "target_ref": request["target_ref"],
        "target_prestate_hash": request["target_prestate_hash"],
        "required_scope": request["required_scope"],
        "idempotency_key": request["idempotency_key"],
        "decision_authority": "KX108_ONLY",
        "is_execution_authority": False,
    }
    approval["approval_hash"] = canonical_hash(approval)
    return approval


def run(tmp_path, request=None, *, unknowns=None, contradictions=None, risk_flags=None):
    request = request or build_request()
    return run_world_action_pre_execution_v0(
        request=request,
        human_approval=build_approval(request),
        evidence_refs=("fixture:world-action",),
        unknowns=list(unknowns or []),
        contradictions=list(contradictions or []),
        risk_flags=list(risk_flags or []),
        context_store_dir=tmp_path / "contexts",
        decision_store_dir=tmp_path / "decisions",
    )


def test_exact_request_hashes_are_recomputed_not_trusted():
    request = build_request()
    assert CTX.verify_world_action_request_mapping(request) == (True, None)

    request["connector_call_hash"] = "0" * 64
    ok, reason = CTX.verify_world_action_request_mapping(request)
    assert ok is False
    assert reason == "WORLD_ACTION_REQUEST_CONNECTOR_CALL_HASH_MISMATCH"


def test_request_hash_and_idempotency_are_recomputed():
    request = build_request()
    request["idempotency_key"] = "1" * 64
    ok, reason = CTX.verify_world_action_request_mapping(request)
    assert ok is False
    assert reason == "WORLD_ACTION_REQUEST_IDEMPOTENCY_KEY_MISMATCH"

    request = build_request()
    request["request_hash"] = "2" * 64
    ok, reason = CTX.verify_world_action_request_mapping(request)
    assert ok is False
    assert reason == "WORLD_ACTION_REQUEST_HASH_MISMATCH"


def test_secret_material_is_rejected_before_context():
    request = build_request(
        connector_args={
            "to": "x@example.invalid",
            "authorization_token": "must-never-reach-kx108",
        }
    )
    ok, reason = CTX.verify_world_action_request_mapping(request)
    assert ok is False
    assert reason.startswith("SECRET_FIELD_FORBIDDEN_IN_WORLD_ACTION:")


def test_human_approval_is_exact_and_non_sovereign():
    request = build_request()
    approval = build_approval(request)
    assert CTX.verify_world_action_human_approval(
        approval, request
    ) == (True, None)

    approval["connector_call_hash"] = "3" * 64
    ok, reason = CTX.verify_world_action_human_approval(
        approval, request
    )
    assert ok is False
    assert reason == (
        "WORLD_ACTION_HUMAN_APPROVAL_CONNECTOR_CALL_HASH_MISMATCH"
    )


def test_context_persists_hashes_not_raw_connector_payload(tmp_path):
    request = build_request()
    context = CTX.create_world_action_pre_execution_context(
        request=request,
        human_approval=build_approval(request),
        evidence_refs=["fixture:evidence"],
    )
    assert "connector_args" not in context
    assert context["runtime_allowed_now"] is False
    assert context["emits_act"] is False
    assert context["memory_write"] is False
    assert context["kernel_mutation"] is False
    assert context["decision_authority"] == "KX108_ONLY"

    stored = CTX.store_world_action_pre_execution_context(
        context, tmp_path
    )
    assert stored["status"] == "STORED"
    loaded = CTX.load_world_action_pre_execution_context(
        context["context_id"], tmp_path
    )
    assert CTX.verify_world_action_pre_execution_context(
        loaded
    ) == (True, None)


def test_clean_world_action_gets_real_kx108_allow_but_no_egress(tmp_path):
    result = run(tmp_path)

    assert result.x108_gate == "ALLOW"
    assert result.decision_phase == "WORLD_ACTION_PRE_EXECUTION"
    assert result.decision_record_id.startswith("kxworld-")
    assert result.decision_record_verified is True
    assert result.context_verified is True
    assert result.dry_run_only is True
    assert result.egress_allowed is False
    assert result.world_action_runtime_activated is False
    assert result.emits_act is False
    assert result.memory_write is False
    assert result.kernel_mutation is False
    assert result.decision_authority == "KX108_ONLY"

    record = DS.load_kx108_decision_record(
        result.decision_record_id,
        tmp_path / "decisions",
    )
    assert DS.verify_kx108_decision_record(record) == (True, None)
    assert record["decision_phase"] == "WORLD_ACTION_PRE_EXECUTION"
    assert record["domain"] == "world_action"
    assert record["source_domain"] == "administration"


def test_two_unknowns_hold_and_two_contradictions_block(tmp_path):
    hold = run(
        tmp_path / "hold",
        unknowns=("RECIPIENT_SCOPE_UNKNOWN", "FACT_FRESHNESS_UNKNOWN"),
    )
    assert hold.x108_gate == "HOLD"

    block = run(
        tmp_path / "block",
        contradictions=("TARGET_CONFLICT", "AUTHORITY_CONFLICT"),
    )
    assert block.x108_gate == "BLOCK"


@pytest.mark.parametrize(
    "world_call_class,action_risk_class",
    [
        ("CRITICAL_WORLD_CALL", "ACTION_SENSITIVE"),
        ("FORBIDDEN_WORLD_CALL", "ACTION_EXTERNAL_API"),
        ("REVERSIBLE_WORLD_CALL", "ACTION_FORBIDDEN"),
    ],
)
def test_critical_or_forbidden_classes_are_structurally_blocked(
    tmp_path,
    world_call_class,
    action_risk_class,
):
    request = build_request(
        world_call_class=world_call_class,
        action_risk_class=action_risk_class,
        autonomy_level=5,
    )
    result = run(tmp_path, request)
    assert result.x108_gate == "BLOCK"


def test_source_domains_share_one_world_action_kernel_domain(tmp_path):
    admin = run(tmp_path / "admin", build_request(domain="administration"))
    trading = run(tmp_path / "trading", build_request(domain="trading"))
    gps = run(
        tmp_path / "gps",
        build_request(domain="gps_defense_aviation"),
    )

    assert admin.x108_gate == trading.x108_gate == gps.x108_gate == "ALLOW"
    assert {
        admin.source_domain,
        trading.source_domain,
        gps.source_domain,
    } == {"administration", "trading", "gps_defense_aviation"}

    for result, store in (
        (admin, tmp_path / "admin" / "decisions"),
        (trading, tmp_path / "trading" / "decisions"),
        (gps, tmp_path / "gps" / "decisions"),
    ):
        record = DS.load_kx108_decision_record(
            result.decision_record_id, store
        )
        assert record["domain"] == "world_action"


def test_dry_run_evidence_cannot_masquerade_as_live_authority(tmp_path):
    result = run(tmp_path)
    evidence = build_world_action_pre_dry_run_evidence_v0(result)

    assert evidence["x108_gate"] == "ALLOW"
    assert evidence["dry_run_only"] is True
    assert evidence["egress_allowed"] is False
    assert evidence["world_action_runtime_activated"] is False
    assert evidence["sovereign_ticket_id"] is None
    assert evidence["emits_act"] is False


def test_decision_store_refuses_caller_forged_gate():
    request = build_request()
    context = CTX.create_world_action_pre_execution_context(
        request=request,
        human_approval=build_approval(request),
        evidence_refs=["fixture:evidence"],
    )
    out = DS.persist_kx108_world_action_pre_execution_decision(
        {"x108_gate": "ALLOW"},
        CTX.decision_binding_context(context),
    )
    assert out["status"] == "REJECTED"
    assert out["reason"] == "DECISION_ENVELOPE_NOT_A_KERNEL_DATACLASS"


def test_tampered_world_action_decision_record_fails_verification(tmp_path):
    result = run(tmp_path)
    record = DS.load_kx108_decision_record(
        result.decision_record_id,
        tmp_path / "decisions",
    )
    record["connector_call_hash"] = "f" * 64
    ok, reason = DS.verify_kx108_decision_record(record)
    assert ok is False
    assert reason == "DECISION_RECORD_HASH_MISMATCH"


def test_runtime_facts_detect_pre_rail_but_keep_real_world_blocked():
    facts = runtime_link_facts()

    assert world_action_pre_execution_rail_present() is True
    assert facts["world_action_pre_execution_rail_present"] is True
    assert facts["world_action_runtime_activated"] is False
    assert facts["execution_authority"] is False
    assert facts["emits_act"] is False
    assert MISSING_RUNTIME_LINK_WORLD_ACTUATION in facts["missing_runtime_links"]
    assert MISSING_RUNTIME_LINK_REAL_EXECUTION in facts["missing_runtime_links"]
