import datetime
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from obsidia_kx108_decision_store import (  # noqa: E402
    load_kx108_decision_record,
)
from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    run_world_action_pre_execution_v0,
)
from periphery.world_calls.bounded_connector_executor_v0 import (  # noqa: E402
    ConnectorProviderOutcomeV0,
    OUTCOME_CONFIRMED_SUCCESS,
    execute_bounded_connector_v0,
)
from periphery.world_calls.external_runtime_activation_policy_v0 import (  # noqa: E402
    build_activation_policy_v0,
)
from periphery.world_calls.live_sovereign_ticket_v0 import (  # noqa: E402
    issue_live_sovereign_ticket_v0,
)

FIXTURE = ROOT / "tests" / "fixtures" / "world_action_multidomain_conformance_v0.json"


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


def load_cases():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["status"] == "SIMULATED_NOT_OBSERVED"
    assert data["boundaries"]["decision_authority"] == "KX108_ONLY"
    assert data["boundaries"]["real_external_action"] is False
    return data["cases"]


def build_request(case):
    connector_args = {
        "case_id": case["case_id"],
        "operation": case["operation_id"],
        "fixture_mode": "SIMULATED_NOT_OBSERVED",
    }
    target_ref = (
        f"sim:{case['domain_id']}:{case['surface_id'].lower()}:"
        f"{case['case_id'].lower()}"
    )
    request = {
        "request_id": f"world-{case['case_id'].lower()}",
        "proposal_id": f"proposal-{case['case_id'].lower()}",
        "proposal_hash": canonical_hash(
            {
                "case_id": case["case_id"],
                "domain_id": case["domain_id"],
            }
        ),
        "domain_id": case["domain_id"],
        "surface_id": case["surface_id"],
        "operation_id": case["operation_id"],
        "effect_class": case["effect_class"],
        "connector_id": case["connector_id"],
        "connector_action": case["connector_action"],
        "connector_args": connector_args,
        "target_ref": target_ref,
        "target_prestate_hash": canonical_hash(
            {
                "target_ref": target_ref,
                "fixture_prestate": "V0",
            }
        ),
        "required_scope": case["required_scope"],
        "world_call_class": case["world_call_class"],
        "action_risk_class": case["action_risk_class"],
        "autonomy_level": case["autonomy_level"],
        "irreversible": case["irreversible"],
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
        "approved_by": "HUMAN:SIMULATED_REVIEWER",
        "approval_reference": f"fixture-review:{request['request_id']}",
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


class MatrixSandboxAdapter:
    execution_mode = "SANDBOX_DETERMINISTIC"
    external_network_capable = False
    side_effect_free = True
    retry_after_confirmed_no_effect = True

    def __init__(self, case):
        self.connector_id = case["connector_id"]
        self.connector_action = case["connector_action"]
        self.required_scope = case["required_scope"]
        self.provider_id = f"MATRIX_SANDBOX:{case['connector_id']}"
        self.call_count = 0

    def execute(self, connector_args):
        self.call_count += 1
        return ConnectorProviderOutcomeV0(
            status=OUTCOME_CONFIRMED_SUCCESS,
            provider_receipt_ref=(
                f"matrix:{connector_args['case_id']}:receipt"
            ),
            provider_state_ref=(
                f"matrix:{connector_args['case_id']}:state"
            ),
            detail_digest=canonical_hash(dict(connector_args)),
            observed_at=datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
        )


def build_policy(case):
    now = datetime.datetime.now(datetime.timezone.utc)
    return build_activation_policy_v0(
        policy_id=f"matrix-policy-{case['case_id'].lower()}",
        environment="SIMULATED_MATRIX",
        enabled=True,
        allowed_operations=[
            (
                case["connector_id"],
                case["connector_action"],
                case["required_scope"],
            )
        ],
        allowed_world_call_classes=[case["world_call_class"]],
        allowed_action_risk_classes=[case["action_risk_class"]],
        max_autonomy_level=case["autonomy_level"],
        created_at=now.isoformat(),
        expires_at=(now + datetime.timedelta(hours=1)).isoformat(),
        operator_approval_ref=(
            f"SIMULATED_OPERATOR:{case['case_id']}"
        ),
    )


def test_matrix_shape_and_surface_coverage():
    cases = load_cases()
    assert len(cases) == 16
    assert {
        case["surface_id"] for case in cases
    } == {"CRM", "CALENDAR", "TASKS", "MAIL", "PAYMENT", "DEVICE"}

    expected_stages = Counter(case["expected_stage"] for case in cases)
    assert expected_stages == Counter(
        {
            "EXECUTOR_PASS": 9,
            "LIVE_POLICY_BLOCK": 2,
            "PRE_HOLD": 1,
            "PRE_BLOCK": 4,
        }
    )


@pytest.mark.parametrize("case", load_cases(), ids=lambda x: x["case_id"])
def test_multidomain_case_follows_expected_universal_path(tmp_path, case):
    request = build_request(case)
    case_root = tmp_path / case["case_id"].lower()

    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=build_approval(request),
        evidence_refs=[
            f"fixture:{case['case_id']}",
            "matrix:SIMULATED_NOT_OBSERVED",
        ],
        unknowns=case.get("pre_unknowns", []),
        contradictions=case.get("pre_contradictions", []),
        context_store_dir=case_root / "contexts",
        decision_store_dir=case_root / "decisions",
    )

    assert pre.x108_gate == case["expected_pre_gate"]
    assert pre.source_domain == case["domain_id"]
    assert pre.decision_authority == "KX108_ONLY"
    assert pre.egress_allowed is False
    assert pre.world_action_runtime_activated is False

    record = load_kx108_decision_record(
        pre.decision_record_id,
        case_root / "decisions",
    )
    assert record["domain"] == "world_action"
    assert record["source_domain"] == case["domain_id"]
    assert record["decision_phase"] == "WORLD_ACTION_PRE_EXECUTION"

    if case["expected_stage"] in {"PRE_HOLD", "PRE_BLOCK"}:
        assert pre.x108_gate in {"HOLD", "BLOCK"}
        return

    if case["expected_stage"] == "LIVE_POLICY_BLOCK":
        assert pre.x108_gate == "ALLOW"
        with pytest.raises(ValueError):
            build_policy(case)
        return

    assert case["expected_stage"] == "EXECUTOR_PASS"
    policy = build_policy(case)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=case_root / "decisions",
        context_store_dir=case_root / "contexts",
    )
    assert ticket.source_domain == case["domain_id"]
    assert ticket.executor_bound is False

    adapter = MatrixSandboxAdapter(case)
    result = execute_bounded_connector_v0(
        ticket=ticket,
        activation_policy=policy,
        connector_args=request["connector_args"],
        observed_target_ref=request["target_ref"],
        observed_target_prestate_hash=request[
            "target_prestate_hash"
        ],
        adapter=adapter,
        receipt_store_dir=case_root / "receipts",
        reconciliation_store_dir=case_root / "reconciliations",
    )

    assert result.status == "SANDBOX_EXECUTED_RECEIPT_STORED"
    assert result.gateway_result == "LIVE_PREFLIGHT_READY"
    assert result.adapter_called is True
    assert result.network_call_performed is False
    assert result.real_external_effect is False
    assert adapter.call_count == 1
    assert result.receipt is not None
    assert result.receipt.source_domain == case["domain_id"]
    assert result.receipt.real_external_effect is False
    assert result.receipt.decision_authority == "KX108_ONLY"


def test_gate_distribution_across_métier_matrix(tmp_path):
    observed = Counter()
    for case in load_cases():
        request = build_request(case)
        case_root = tmp_path / case["case_id"].lower()
        pre = run_world_action_pre_execution_v0(
            request=request,
            human_approval=build_approval(request),
            evidence_refs=[f"fixture:{case['case_id']}"],
            unknowns=case.get("pre_unknowns", []),
            contradictions=case.get("pre_contradictions", []),
            context_store_dir=case_root / "contexts",
            decision_store_dir=case_root / "decisions",
        )
        observed[pre.x108_gate] += 1

    assert observed == Counter(
        {
            "ALLOW": 11,
            "BLOCK": 4,
            "HOLD": 1,
        }
    )
