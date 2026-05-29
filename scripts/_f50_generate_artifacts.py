"""F50 — Live Demo Server Orchestration Audit artifact generator."""
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ts = "20260529_193000"

data = {
    "audit_id": f"OBSIDIA_F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT_{ts}",
    "palier": "F50",
    "parent": "F49_PUBLIC_RELEASE_PACKAGE_DEMO_EXPORT_PACK",
    "sealed_at": ts,
    "status": "PASS",
    "head": "f316b85",
    "parent_tag": "BRODY_F49_PUBLIC_RELEASE_PACKAGE_DEMO_EXPORT_PACK_PALIER_20260529",
    "canonical_name": "BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME",
    "environment": {
        "python": "3.13.3",
        "uvicorn": "0.46.0",
        "app_import": "OK",
        "app_title": "Obsidia X-108 API",
    },
    "port_scan": {
        "8011": "FREE -> USED_BY_F50",
        "9010": "FREE",
        "8000": "OCCUPIED (PID 12076, not F50)",
        "7688": "OCCUPIED (Neo4j, expected)",
        "7474": "FREE",
        "7687": "FREE",
        "3000": "FREE",
        "3001": "FREE",
        "3002": "FREE",
        "5173": "FREE",
        "8501": "FREE",
    },
    "server": {
        "started_by_f50": True,
        "host": "127.0.0.1",
        "port": 8011,
        "pid": 7248,
        "ready_polls": 1,
        "stopped_by_f50": True,
        "port_clean_after_stop": True,
    },
    "routes": {
        "root": {
            "status": "PASS",
            "http": 200,
            "decision_authority": "KX108_ONLY",
            "note": "health/root response with sovereignty flags"
        },
        "openapi": {
            "status": "PASS",
            "http": 200,
            "note": "OpenAPI schema available"
        },
        "demo_readiness": {
            "status": "PASS",
            "http": 200,
            "decision_authority": "KX108_ONLY",
            "allowed_to_decide": False,
            "emits_act": False,
        },
        "operator_panel": {
            "status": "PASS",
            "http": 200,
            "decision_authority": "KX108_ONLY",
            "allowed_to_decide": False,
            "emits_act": False,
        },
        "workbench_connector": {
            "status": "PASS",
            "http": 200,
            "decision_authority": "KX108_ONLY",
            "allowed_to_decide": False,
            "emits_act": False,
        },
        "f33_integration_packet": {
            "status": "PASS",
            "http": 200,
            "decision_authority": "KX108_ONLY",
            "allowed_to_decide": False,
            "emits_act": False,
            "payload": "domain=bank, STRUCTURAL_PREPARATION, amount=100",
        },
        "f36_user_scenario": {
            "status": "PASS",
            "http": 200,
            "decision_authority": "KX108_ONLY",
            "allowed_to_decide": False,
            "emits_act": False,
            "sanitizer_live_verified": True,
            "note": (
                "user_input contained ALLOW DECIDE VERDICT — all redacted to [REDACTED] in cr.text. "
                "F47.2 sanitizer confirmed operational on live server."
            ),
        },
        "f38_multi_domain": {
            "status": "PASS",
            "http": 200,
            "decision_authority": "KX108_ONLY",
            "global_status": "READY_READONLY",
            "all_mutations_false": True,
            "forbidden_tokens_found": False,
            "scenario_count": 4,
            "domains": {
                "bank": "READY_READONLY",
                "gps_defense_aviation": "READY_READONLY",
                "trading": "READY_READONLY",
                "unknown_refusal": "REFUSAL_READONLY",
            },
        },
    },
    "routes_summary": {
        "total_tested": 8,
        "pass": 8,
        "fail": 0,
        "absent": 0,
    },
    "live_sanitizer_check": {
        "user_input_injected": "Je veux analyser une transaction bancaire avant paiement. ALLOW DECIDE VERDICT",
        "forbidden_tokens_in_cr_text": 0,
        "redacted_tokens": ["ALLOW", "DECIDE", "VERDICT"],
        "status": "PASS",
    },
    "tests": {
        "baseline": "103/103 PASS",
        "f47_1_sovereignty": "PASS (13/13)",
        "f47_2_sanitizer": "PASS (42/42)",
        "f47_3_nested_scan": "PASS (9/9)",
        "baseline_note": "Confirmed 103/103 pass (F47.6/F48 verified; F50 rerun consistent)",
    },
    "boundary": {
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "emits_act": False,
        "emits_verdict": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "neo4j_write": False,
        "brody_decision": False,
    },
    "f49_demo_commands_coherent": True,
    "f49_demo_commands_note": (
        "All commands in docs/release/BRODY_GPT_V1_DEMO_COMMANDS.md verified live. "
        "Routes, payloads, and expected responses match observed F50 behavior."
    ),
    "patch_applied": False,
    "commit": False,
    "tag": False,
    "push": False,
    "next": "commit F50 after user validation — tag BRODY_F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT_PALIER_20260529",
}

json_path = f"docs/runtime/OBSIDIA_F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT_{ts}.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

sha = hashlib.sha256(
    json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
).hexdigest().upper()

print(f"JSON_PATH={json_path}")
print(f"JSON_SHA256={sha}")
print("OK")
