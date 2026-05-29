"""
F38 — Smoke: Multi-Domain Live Uvicorn API.

Calls POST /api/periphery/brody-runtime/f38/multi-domain-scenarios against
a real running uvicorn server (no TestClient fallback). Verifies the full
F37/F38 contract plus source=LIVE_SERVER proof.

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

ROUTE = "/api/periphery/brody-runtime/f38/multi-domain-scenarios"
LIVE_PORTS = [8000, 9010, 8011]
SMOKE_PAYLOAD: dict = {}

EXPECTED_DOMAINS = {"bank", "gps_defense_aviation", "trading", "unknown_refusal"}
KNOWN_DOMAINS = {"bank", "gps_defense_aviation", "trading"}
FORBIDDEN_RESPONSE_TOKENS = ("ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT")
FORBIDDEN_TRUE_FLAGS = (
    "emits_act", "emits_verdict", "kernel_mutation", "x108_mutation",
    "neo4j_write", "memory_write", "graphiti_write", "runtime_execute",
    "allowed_to_decide", "can_decide", "can_emit_act",
)


def _has_forbidden_token(text: str) -> bool:
    text_upper = text.upper()
    return any(
        re.search(r"\b" + re.escape(t) + r"\b", text_upper)
        for t in FORBIDDEN_RESPONSE_TOKENS
    )


def _post_live(base_url: str) -> tuple[int, dict | str]:
    url = base_url.rstrip("/") + ROUTE
    data = json.dumps(SMOKE_PAYLOAD).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _check_contract(body: dict, port: int) -> dict[str, bool]:
    checks: dict[str, bool] = {}

    checks["source_is_live"] = "TESTCLIENT" not in str(body.get("source", ""))
    checks["packet_id_correct"] = body.get("packet_id") == "F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY"
    checks["version_correct"] = body.get("version") == "F37_V1"
    checks["mode_readonly"] = body.get("mode") == "READONLY"
    checks["scenario_count_4"] = body.get("scenario_count") == 4
    checks["scenarios_run_4"] = body.get("scenarios_run") == 4
    checks["global_status_ready"] = body.get("global_status") == "READY_READONLY"
    checks["all_mutations_false"] = body.get("all_mutations_false") is True
    checks["forbidden_tokens_found_false"] = body.get("forbidden_tokens_found") is False

    scenarios = body.get("scenarios", [])
    by_domain = {s.get("domain"): s for s in scenarios}
    checks["all_domains_present"] = set(by_domain.keys()) == EXPECTED_DOMAINS

    for dom in EXPECTED_DOMAINS:
        s = by_domain.get(dom, {})
        checks[f"{dom}_cr_present"] = s.get("controlled_response_present") is True
        checks[f"{dom}_can_decide_false"] = s.get("can_decide") is False
        checks[f"{dom}_can_execute_false"] = s.get("can_execute") is False

        if dom in KNOWN_DOMAINS:
            checks[f"{dom}_status_ready"] = s.get("status") == "READY_READONLY"
            checks[f"{dom}_surfaces_7"] = s.get("surfaces_ready") == 7
        else:
            checks["refusal_status_correct"] = s.get("status") == "REFUSAL_READONLY"
            cr = s.get("controlled_response", {})
            checks["refusal_kind_correct"] = cr.get("response_kind") == "refusal_out_of_scope"

        cr = s.get("controlled_response", {})
        text = cr.get("text", "")
        checks[f"{dom}_no_forbidden_tokens"] = not _has_forbidden_token(text)
        checks[f"{dom}_text_present"] = isinstance(text, str) and len(text) > 50

        for flag in FORBIDDEN_TRUE_FLAGS:
            checks[f"{dom}_{flag}_not_true"] = s.get(flag) is not True
            checks[f"{dom}_cr_{flag}_not_true"] = cr.get(flag) is not True

    for flag in FORBIDDEN_TRUE_FLAGS:
        checks[f"global_{flag}_not_true"] = body.get(flag) is not True

    checks["global_decision_authority"] = body.get("decision_authority") == "KX108_ONLY"
    checks["global_readonly"] = body.get("readonly") is True
    checks["global_advisory_only"] = body.get("advisory_only") is True
    checks["global_context_signal_only"] = body.get("context_signal_only") is True

    return checks


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = Path("docs/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)

    source = "NO_LIVE_SERVER"
    http_status = 0
    body: dict | str = {}
    used_port = 0

    for port in LIVE_PORTS:
        status, resp = _post_live(f"http://127.0.0.1:{port}")
        if status == 200 and isinstance(resp, dict):
            http_status, body, source, used_port = status, resp, f"LIVE_SERVER_{port}", port
            break

    if source == "NO_LIVE_SERVER":
        result = {
            "ok": False,
            "source": source,
            "error": f"No live server on ports {LIVE_PORTS}. F38 requires real uvicorn.",
            "checks": {},
        }
        out_file = out_dir / f"F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_{ts}.json"
        out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_STATUS=FAIL")
        print(f"REASON=No live server on ports {LIVE_PORTS}")
        return 1

    checks = _check_contract(body, used_port)
    all_pass = all(checks.values())
    failed = {k: v for k, v in checks.items() if not v}

    scenarios = body.get("scenarios", [])
    by_domain = {s.get("domain"): s for s in scenarios}

    def _ready(dom: str) -> bool:
        s = by_domain.get(dom, {})
        return s.get("status") in ("READY_READONLY", "REFUSAL_READONLY")

    result = {
        "ok": all_pass,
        "source": source,
        "server_mode": "LIVE_UVICORN",
        "port": used_port,
        "http_status": http_status,
        "route": ROUTE,
        "timestamp": ts,
        "checks_total": len(checks),
        "checks_pass": sum(checks.values()),
        "checks_fail": len(failed),
        "failed_checks": failed,
        "summary": {
            "packet_id": body.get("packet_id"),
            "global_status": body.get("global_status"),
            "scenario_count": body.get("scenario_count"),
            "scenarios_run": body.get("scenarios_run"),
            "all_mutations_false": body.get("all_mutations_false"),
            "forbidden_tokens_found": body.get("forbidden_tokens_found"),
            "decision_authority": body.get("decision_authority"),
            "bank_status": by_domain.get("bank", {}).get("status"),
            "gps_status": by_domain.get("gps_defense_aviation", {}).get("status"),
            "trading_status": by_domain.get("trading", {}).get("status"),
            "refusal_status": by_domain.get("unknown_refusal", {}).get("status"),
        },
    }

    out_file = out_dir / f"F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    status_label = "PASS" if all_pass else "FAIL"
    print(f"\nF38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_STATUS={status_label}")
    print(f"SERVER_MODE=LIVE_UVICORN")
    print(f"PORT={used_port}")
    print(f"ROUTE={ROUTE}")
    print(f"HTTP_STATUS={http_status}")
    print(f"SOURCE={source}")
    print(f"PACKET_ID={body.get('packet_id', '')}")
    print(f"SCENARIO_COUNT={body.get('scenario_count')}")
    print(f"BANK_READY={_ready('bank')}")
    print(f"GPS_READY={_ready('gps_defense_aviation')}")
    print(f"TRADING_READY={_ready('trading')}")
    print(f"UNKNOWN_REFUSAL_READY={_ready('unknown_refusal')}")
    print(f"BOUNDARY_KX108_ONLY={body.get('decision_authority') == 'KX108_ONLY'}")
    print(f"FORBIDDEN_TOKENS_FOUND={body.get('forbidden_tokens_found')}")
    print(f"KERNEL_MUTATION={body.get('kernel_mutation')}")
    print(f"X108_MUTATION={body.get('x108_mutation')}")
    print(f"NEO4J_WRITE={body.get('neo4j_write')}")
    print(f"CHECKS={result['checks_pass']}/{result['checks_total']}")
    print(f"PROOF_FILE={out_file}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
