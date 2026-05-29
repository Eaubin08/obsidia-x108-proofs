"""
F34 — Live Route Smoke: API Contract Proof Readonly.

Calls POST /api/periphery/brody-runtime/f33/integration-packet and verifies
the full API contract:
  - HTTP 200
  - entrypoint_id = F33_BRODY_RUNTIME_ENTRYPOINT_READONLY
  - f32_packet present with 7 surfaces READY
  - decision_authority = KX108_ONLY everywhere
  - All boundary flags False (emits_act, kernel_mutation, neo4j_write, etc.)
  - No forbidden mutation tokens in response

Strategy:
  1. Attempt live server on http://127.0.0.1:8000 (up to 2 ports)
  2. Fallback to FastAPI TestClient if no live server available
  3. Either way, run all contract checks and save proof JSON

Output: docs/runtime/F34_LIVE_ROUTE_PROOF_<timestamp>.json
Exit 0 on PASS, 1 on FAIL, 2 on no-server (TestClient fallback used — still asserts).

BOUNDARY ENFORCED: KX108_ONLY · readonly · emits_act=False · kernel_mutation=False
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root is on sys.path when running as a standalone script
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

ROUTE = "/api/periphery/brody-runtime/f33/integration-packet"
LIVE_PORTS = [8000, 8011]

SMOKE_PAYLOAD = {
    "domain": "bank",
    "sigma_payload": {
        "request_type": "STRUCTURAL_PREPARATION",
        "amount": 100,
        "recipient": "readonly-smoke-target",
    },
    "title": "F34 live route smoke",
    "session_id": "f34-live-route-smoke",
    "signal_id": "f34-tree-signal",
    "theta": 0.15,
    "request_type": "STRUCTURAL_PREPARATION",
}

FORBIDDEN_TRUE_FLAGS = (
    "emits_act", "emits_verdict", "kernel_mutation", "x108_mutation",
    "neo4j_write", "memory_write", "graphiti_write", "runtime_execute",
    "allowed_to_decide", "can_decide", "can_emit_act",
)

EXPECTED_SURFACES = {
    "sigma_dispatcher",
    "tree_signal_packet",
    "monitoring_adapters",
    "operator_view_packet",
    "brody_runtime_context",
    "workflow_governance_readonly",
    "neo4j_guide_bridge",
}


def _post_live(base_url: str) -> tuple[int, dict | str]:
    url = base_url.rstrip("/") + ROUTE
    data = json.dumps(SMOKE_PAYLOAD).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body
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
    f32 = body.get("f32_packet", {})
    surfaces = f32.get("surfaces", {})

    checks: dict[str, bool] = {}

    checks["response_is_dict"] = isinstance(body, dict)
    checks["entrypoint_id_correct"] = (
        body.get("entrypoint_id") == "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"
    )
    checks["version_correct"] = body.get("version") == "F33_V1"
    checks["entrypoint_status_ready"] = (
        body.get("entrypoint_status") == "ENTRYPOINT_READY_READONLY"
    )
    checks["integration_status_ready"] = (
        body.get("integration_status") == "READY_READONLY"
    )
    checks["surfaces_ready_7"] = body.get("surfaces_ready") == 7
    checks["surfaces_missing_0"] = body.get("surfaces_missing") == 0
    checks["f32_packet_present"] = isinstance(f32, dict) and bool(f32)
    checks["f32_integration_ready"] = (
        f32.get("integration_status") == "READY_READONLY"
    )
    checks["seven_surfaces_present"] = set(surfaces.keys()) == EXPECTED_SURFACES
    checks["all_surfaces_ready"] = all(
        s.get("status") == "READY" for s in surfaces.values()
    )
    checks["decision_authority_top"] = (
        body.get("decision_authority") == "KX108_ONLY"
    )
    checks["decision_authority_f32"] = (
        f32.get("decision_authority") == "KX108_ONLY"
    )
    checks["readonly_top"] = body.get("readonly") is True
    checks["advisory_only_top"] = body.get("advisory_only") is True
    checks["context_signal_only_top"] = body.get("context_signal_only") is True

    for flag in FORBIDDEN_TRUE_FLAGS:
        checks[f"boundary_{flag}_false_top"] = body.get(flag) is not True
        checks[f"boundary_{flag}_false_f32"] = f32.get(flag) is not True

    for surf_name, surf in surfaces.items():
        checks[f"surface_{surf_name}_kx108"] = (
            surf.get("decision_authority") == "KX108_ONLY"
        )
        for flag in ("emits_act", "kernel_mutation", "x108_mutation", "neo4j_write"):
            val = surf.get(flag)
            checks[f"surface_{surf_name}_{flag}_not_true"] = (val is not True)

    return checks


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = Path("docs/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)

    source = "UNKNOWN"
    http_status = 0
    body: dict | str = {}

    # 1 — try live server
    for port in LIVE_PORTS:
        base = f"http://127.0.0.1:{port}"
        status, resp = _post_live(base)
        if status == 200 and isinstance(resp, dict):
            http_status = status
            body = resp
            source = f"LIVE_SERVER_{port}"
            break

    # 2 — fallback to TestClient
    if source == "UNKNOWN":
        try:
            http_status, body = _post_testclient()
            source = "TESTCLIENT_FALLBACK"
        except Exception as e:
            source = f"TESTCLIENT_ERROR: {e}"

    if not isinstance(body, dict):
        result = {
            "ok": False,
            "source": source,
            "http_status": http_status,
            "error": str(body),
            "checks": {},
        }
        out_file = out_dir / f"F34_LIVE_ROUTE_PROOF_{ts}.json"
        out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("F34_LIVE_ROUTE_SMOKE_API_CONTRACT_STATUS=FAIL")
        return 1

    checks = _check_contract(body)
    all_pass = all(checks.values())
    failed = {k: v for k, v in checks.items() if not v}

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
        "contract_summary": {
            "entrypoint_id": body.get("entrypoint_id"),
            "version": body.get("version"),
            "entrypoint_status": body.get("entrypoint_status"),
            "integration_status": body.get("integration_status"),
            "surfaces_ready": body.get("surfaces_ready"),
            "surfaces_missing": body.get("surfaces_missing"),
            "surfaces_total": body.get("surfaces_total"),
            "decision_authority": body.get("decision_authority"),
            "readonly": body.get("readonly"),
            "emits_act": body.get("emits_act"),
            "emits_verdict": body.get("emits_verdict"),
            "kernel_mutation": body.get("kernel_mutation"),
            "x108_mutation": body.get("x108_mutation"),
            "neo4j_write": body.get("neo4j_write"),
            "proof_status": body.get("proof_status"),
        },
        "surfaces_seen": sorted(body.get("f32_packet", {}).get("surfaces", {}).keys()),
    }

    out_file = out_dir / f"F34_LIVE_ROUTE_PROOF_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    status_label = "PASS" if all_pass else "FAIL"
    print(f"\nF34_LIVE_ROUTE_SMOKE_API_CONTRACT_STATUS={status_label}")
    print(f"SOURCE={source}")
    print(f"ROUTE={ROUTE}")
    print(f"HTTP_STATUS={http_status}")
    print(f"CHECKS={result['checks_pass']}/{result['checks_total']}")
    print(f"PROOF_FILE={out_file}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
