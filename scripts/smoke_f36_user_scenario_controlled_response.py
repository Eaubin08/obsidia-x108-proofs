"""
F36 — Smoke: User Scenario Brody Workbench Controlled Response.

Calls POST /api/periphery/brody-runtime/f36/user-scenario and verifies
the full scenario contract:
  - HTTP 200
  - scenario_id = F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE
  - runtime_entrypoint READY_READONLY, 7 surfaces
  - workbench READY_READONLY, surfaces_consulted == 7
  - controlled_response: can_decide=False, can_execute=False
  - No forbidden tokens in controlled_response.text
  - All boundary flags correct

Strategy:
  1. Try live server http://127.0.0.1:8000 / 9010
  2. Fallback to TestClient
  3. Run all contract checks, save proof JSON

BOUNDARY ENFORCED: KX108_ONLY · emits_act=False · kernel_mutation=False
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

ROUTE = "/api/periphery/brody-runtime/f36/user-scenario"
LIVE_PORTS = [8000, 9010]

SMOKE_PAYLOAD = {
    "user_input": "Je veux analyser une transaction bancaire avant paiement.",
    "domain": "bank",
    "sigma_payload": {
        "balance": 10_000.0,
        "transactions": [{"amount": 100.0, "type": "debit", "recipient": "smoke-target"}],
    },
    "session_id": "f36-smoke",
    "request_type": "STRUCTURAL_PREPARATION",
}

FORBIDDEN_TRUE_FLAGS = (
    "emits_act", "emits_verdict", "kernel_mutation", "x108_mutation",
    "neo4j_write", "memory_write", "graphiti_write", "runtime_execute",
    "allowed_to_decide", "can_decide", "can_emit_act",
)
FORBIDDEN_RESPONSE_TOKENS = ("ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT")
EXPECTED_SURFACES = {
    "sigma_dispatcher", "tree_signal_packet", "monitoring_adapters",
    "operator_view_packet", "brody_runtime_context",
    "workflow_governance_readonly", "neo4j_guide_bridge",
}


def _post_live(base_url: str) -> tuple[int, dict | str]:
    url = base_url.rstrip("/") + ROUTE
    data = json.dumps(SMOKE_PAYLOAD).encode("utf-8")
    req = urllib.request.Request(url, data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _post_testclient() -> tuple[int, dict | str]:
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    client = TestClient(app)
    resp = client.post(ROUTE, json=SMOKE_PAYLOAD)
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text


def _check_contract(body: dict) -> dict[str, bool]:
    ep = body.get("runtime_entrypoint", {})
    wb = body.get("workbench", {})
    cr = body.get("controlled_response", {})
    text = cr.get("text", "")
    text_upper = text.upper()

    checks: dict[str, bool] = {}

    checks["response_is_dict"] = isinstance(body, dict)
    checks["scenario_id_correct"] = (
        body.get("scenario_id") == "F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE"
    )
    checks["version_correct"] = body.get("version") == "F36_V1"
    checks["mode_readonly"] = body.get("mode") == "READONLY"
    checks["user_input_echoed"] = bool(body.get("user_input"))

    checks["ep_entrypoint_id"] = (
        ep.get("entrypoint_id") == "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"
    )
    checks["ep_integration_ready"] = ep.get("integration_status") == "READY_READONLY"
    checks["ep_surfaces_ready_7"] = ep.get("surfaces_ready") == 7
    checks["ep_surfaces_missing_0"] = ep.get("surfaces_missing") == 0

    checks["wb_surface_id"] = wb.get("surface_id") == "F36_WORKBENCH_SUMMARY"
    checks["wb_connector_ready"] = wb.get("connector_status") == "READY_READONLY"
    checks["wb_surfaces_7"] = wb.get("surfaces_ready") == 7
    checks["wb_surfaces_consulted_7"] = (
        set(wb.get("surfaces_consulted", [])) == EXPECTED_SURFACES
    )

    checks["cr_kind_correct"] = cr.get("response_kind") == "contextual_explanation_only"
    checks["cr_can_answer_true"] = cr.get("can_answer") is True
    checks["cr_can_decide_false"] = cr.get("can_decide") is False
    checks["cr_can_execute_false"] = cr.get("can_execute") is False
    checks["cr_text_present"] = isinstance(text, str) and len(text) > 50

    for token in FORBIDDEN_RESPONSE_TOKENS:
        checks[f"no_forbidden_token_{token}"] = not re.search(
            r"\b" + re.escape(token) + r"\b", text_upper
        )

    checks["decision_authority_top"] = body.get("decision_authority") == "KX108_ONLY"
    checks["readonly_top"] = body.get("readonly") is True
    checks["advisory_only_top"] = body.get("advisory_only") is True

    for flag in FORBIDDEN_TRUE_FLAGS:
        checks[f"top_{flag}_not_true"] = body.get(flag) is not True
        checks[f"wb_{flag}_not_true"] = wb.get(flag) is not True
        checks[f"cr_{flag}_not_true"] = cr.get(flag) is not True

    return checks


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = Path("docs/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)

    source = "UNKNOWN"
    http_status = 0
    body: dict | str = {}

    for port in LIVE_PORTS:
        status, resp = _post_live(f"http://127.0.0.1:{port}")
        if status == 200 and isinstance(resp, dict):
            http_status, body, source = status, resp, f"LIVE_SERVER_{port}"
            break

    if source == "UNKNOWN":
        try:
            http_status, body = _post_testclient()
            source = "TESTCLIENT_FALLBACK"
        except Exception as e:
            source = f"TESTCLIENT_ERROR: {e}"

    if not isinstance(body, dict):
        result = {"ok": False, "source": source, "http_status": http_status,
                  "error": str(body), "checks": {}}
        (out_dir / f"F36_USER_SCENARIO_PROOF_{ts}.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("F36_USER_SCENARIO_CONTROLLED_RESPONSE_STATUS=FAIL")
        return 1

    checks = _check_contract(body)
    all_pass = all(checks.values())
    failed = {k: v for k, v in checks.items() if not v}
    cr = body.get("controlled_response", {})

    result = {
        "ok": all_pass,
        "source": source,
        "http_status": http_status,
        "route": ROUTE,
        "timestamp": ts,
        "checks_total": len(checks),
        "checks_pass": sum(checks.values()),
        "checks_fail": len(failed),
        "failed_checks": failed,
        "scenario_summary": {
            "scenario_id": body.get("scenario_id"),
            "version": body.get("version"),
            "mode": body.get("mode"),
            "user_input": body.get("user_input"),
            "domain": body.get("domain"),
            "runtime_entrypoint_status": body.get("runtime_entrypoint", {}).get("entrypoint_status"),
            "workbench_connector_status": body.get("workbench", {}).get("connector_status"),
            "surfaces_ready": body.get("runtime_entrypoint", {}).get("surfaces_ready"),
            "controlled_response_kind": cr.get("response_kind"),
            "can_decide": cr.get("can_decide"),
            "can_execute": cr.get("can_execute"),
            "decision_authority": body.get("decision_authority"),
            "readonly": body.get("readonly"),
            "emits_act": body.get("emits_act"),
            "kernel_mutation": body.get("kernel_mutation"),
        },
        "controlled_response_text": cr.get("text", "")[:300],
    }

    out_file = out_dir / f"F36_USER_SCENARIO_PROOF_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    status_label = "PASS" if all_pass else "FAIL"
    print(f"\nF36_USER_SCENARIO_CONTROLLED_RESPONSE_STATUS={status_label}")
    print(f"SCENARIO_INPUT={body.get('user_input', '')[:60]}")
    print(f"SOURCE={source}")
    print(f"RUNTIME_ENTRYPOINT_READY={body.get('runtime_entrypoint', {}).get('integration_status') == 'READY_READONLY'}")
    print(f"WORKBENCH_SURFACE_READY={body.get('workbench', {}).get('connector_status') == 'READY_READONLY'}")
    print(f"SURFACES_READY={body.get('runtime_entrypoint', {}).get('surfaces_ready')}")
    print(f"CONTROLLED_RESPONSE_PRESENT={bool(cr.get('text'))}")
    print(f"BOUNDARY_KX108_ONLY={body.get('decision_authority') == 'KX108_ONLY'}")
    _resp_upper = cr.get("text", "").upper()
    print(f"FORBIDDEN_TOKENS_FOUND={any(re.search(r'\\b' + re.escape(t) + r'\\b', _resp_upper) for t in FORBIDDEN_RESPONSE_TOKENS)}")
    print(f"CHECKS={result['checks_pass']}/{result['checks_total']}")
    print(f"PROOF_FILE={out_file}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
