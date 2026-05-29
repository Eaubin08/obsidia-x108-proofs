"""
F37 — Smoke: Multi-Domain User Scenarios Readonly.

Calls build_multi_domain_user_scenarios() directly and verifies
the full F37 contract:
  - 4 scenarios run (bank, gps_defense_aviation, trading, unknown_refusal)
  - All known domains: status=READY_READONLY, surfaces_ready=7
  - unknown_refusal: status=REFUSAL_READONLY
  - No forbidden tokens in any text (word-boundary check)
  - All boundary flags correct at every layer
  - all_mutations_false=True
  - global_status=READY_READONLY

Saves proof JSON to docs/runtime/.

BOUNDARY ENFORCED: KX108_ONLY · emits_act=False · kernel_mutation=False
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

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


def _check_contract(packet: dict) -> dict[str, bool]:
    checks: dict[str, bool] = {}

    checks["packet_id_correct"] = packet.get("packet_id") == "F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY"
    checks["version_correct"] = packet.get("version") == "F37_V1"
    checks["mode_readonly"] = packet.get("mode") == "READONLY"
    checks["scenario_count_4"] = packet.get("scenario_count") == 4
    checks["scenarios_run_4"] = packet.get("scenarios_run") == 4
    checks["global_status_ready"] = packet.get("global_status") == "READY_READONLY"
    checks["all_mutations_false"] = packet.get("all_mutations_false") is True
    checks["forbidden_tokens_found_false"] = packet.get("forbidden_tokens_found") is False

    scenarios = packet.get("scenarios", [])
    domains_present = {s.get("domain") for s in scenarios}
    checks["all_domains_present"] = domains_present == EXPECTED_DOMAINS

    for s in scenarios:
        dom = s.get("domain", "?")
        checks[f"{dom}_controlled_response_present"] = s.get("controlled_response_present") is True
        checks[f"{dom}_can_decide_false"] = s.get("can_decide") is False
        checks[f"{dom}_can_execute_false"] = s.get("can_execute") is False

        if dom in KNOWN_DOMAINS:
            checks[f"{dom}_status_ready"] = s.get("status") == "READY_READONLY"
            checks[f"{dom}_surfaces_7"] = s.get("surfaces_ready") == 7
        elif dom == "unknown_refusal":
            checks["refusal_status_correct"] = s.get("status") == "REFUSAL_READONLY"
            cr = s.get("controlled_response", {})
            checks["refusal_response_kind"] = cr.get("response_kind") == "refusal_out_of_scope"

        cr = s.get("controlled_response", {})
        text = cr.get("text", "")
        checks[f"{dom}_no_forbidden_tokens"] = not _has_forbidden_token(text)
        checks[f"{dom}_text_present"] = isinstance(text, str) and len(text) > 50

        for flag in FORBIDDEN_TRUE_FLAGS:
            checks[f"{dom}_{flag}_not_true"] = s.get(flag) is not True
            checks[f"{dom}_cr_{flag}_not_true"] = cr.get(flag) is not True

    for flag in FORBIDDEN_TRUE_FLAGS:
        checks[f"global_{flag}_not_true"] = packet.get(flag) is not True

    checks["global_decision_authority"] = packet.get("decision_authority") == "KX108_ONLY"
    checks["global_readonly"] = packet.get("readonly") is True
    checks["global_advisory_only"] = packet.get("advisory_only") is True

    return checks


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = Path("docs/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)

    from periphery.brody_runtime.f37_multi_domain_user_scenarios_readonly import (
        build_multi_domain_user_scenarios,
    )

    try:
        packet = build_multi_domain_user_scenarios()
    except Exception as e:
        result = {"ok": False, "error": f"{type(e).__name__}: {e}", "checks": {}}
        out_file = out_dir / f"F37_MULTI_DOMAIN_PROOF_{ts}.json"
        out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_STATUS=FAIL")
        return 1

    checks = _check_contract(packet)
    all_pass = all(checks.values())
    failed = {k: v for k, v in checks.items() if not v}

    scenarios = packet.get("scenarios", [])
    by_domain = {s["domain"]: s for s in scenarios}

    def _ready(dom: str) -> bool:
        s = by_domain.get(dom, {})
        return s.get("status") in ("READY_READONLY", "REFUSAL_READONLY")

    result = {
        "ok": all_pass,
        "timestamp": ts,
        "checks_total": len(checks),
        "checks_pass": sum(checks.values()),
        "checks_fail": len(failed),
        "failed_checks": failed,
        "summary": {
            "packet_id": packet.get("packet_id"),
            "global_status": packet.get("global_status"),
            "scenario_count": packet.get("scenario_count"),
            "scenarios_run": packet.get("scenarios_run"),
            "all_mutations_false": packet.get("all_mutations_false"),
            "forbidden_tokens_found": packet.get("forbidden_tokens_found"),
            "decision_authority": packet.get("decision_authority"),
            "bank_status": by_domain.get("bank", {}).get("status"),
            "gps_status": by_domain.get("gps_defense_aviation", {}).get("status"),
            "trading_status": by_domain.get("trading", {}).get("status"),
            "refusal_status": by_domain.get("unknown_refusal", {}).get("status"),
        },
    }

    out_file = out_dir / f"F37_MULTI_DOMAIN_PROOF_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    status_label = "PASS" if all_pass else "FAIL"
    print(f"\nF37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_STATUS={status_label}")
    print(f"SCENARIO_COUNT={packet.get('scenario_count')}")
    print(f"BANK_READY={_ready('bank')}")
    print(f"GPS_READY={_ready('gps_defense_aviation')}")
    print(f"TRADING_READY={_ready('trading')}")
    print(f"UNKNOWN_REFUSAL_READY={_ready('unknown_refusal')}")
    print(f"CONTROLLED_RESPONSES_PRESENT={all(s.get('controlled_response_present') for s in scenarios)}")
    print(f"BOUNDARY_KX108_ONLY={packet.get('decision_authority') == 'KX108_ONLY'}")
    print(f"FORBIDDEN_TOKENS_FOUND={packet.get('forbidden_tokens_found')}")
    print(f"KERNEL_MUTATION={packet.get('kernel_mutation')}")
    print(f"X108_MUTATION={packet.get('x108_mutation')}")
    print(f"NEO4J_WRITE={packet.get('neo4j_write')}")
    print(f"CHECKS={result['checks_pass']}/{result['checks_total']}")
    print(f"PROOF_FILE={out_file}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
