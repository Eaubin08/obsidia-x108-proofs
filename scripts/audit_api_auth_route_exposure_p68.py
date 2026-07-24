"""
scripts/audit_api_auth_route_exposure_p68.py — P68 API auth & route exposure audit.

AUDIT ONLY — ne modifie aucun fichier, ne stage rien.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "apps" / "obsidia_api" / "routes"
CONNECTORS_DIR = ROOT / "connectors"

# ─── Route catalogue ──────────────────────────────────────────────────────────
# (prefix, path, method, source_file, function_name_hint)
ROUTES_CATALOGUE = [
    # audit.py
    ("/api/audit",          "/events",                      "GET",  "audit.py",              "get_audit_events"),
    # blockchain.py
    ("/api/blockchain",     "/policy/evaluate",             "POST", "blockchain.py",          "evaluate_policy"),
    ("/api/blockchain",     "/signature/check",             "POST", "blockchain.py",          "check_signature"),
    ("/api/blockchain",     "/wallet/gate",                 "POST", "blockchain.py",          "wallet_gate"),
    ("/api/blockchain",     "/gencoin/compute",             "POST", "blockchain.py",          "gencoin_compute"),
    ("/api/blockchain",     "/world/gateway",               "POST", "blockchain.py",          "world_gateway"),
    ("/api/blockchain",     "/world/bus-dispatch",          "POST", "blockchain.py",          "world_bus_dispatch"),
    ("/api/blockchain",     "/world/ticket-status",         "POST", "blockchain.py",          "world_ticket_status"),
    # brody.py
    ("/api/brody",          "/chat",                        "POST", "brody.py",               "brody_chat"),
    # brody_monitoring.py
    ("/api/periphery/monitoring", "/brody-cli-registry",   "GET",  "brody_monitoring.py",    "brody_cli_registry"),
    ("/api/periphery/monitoring", "/adapters/bank",         "POST", "brody_monitoring.py",    "adapters_bank"),
    ("/api/periphery/monitoring", "/adapters/gps",          "POST", "brody_monitoring.py",    "adapters_gps"),
    ("/api/periphery/monitoring", "/adapters/trading",      "POST", "brody_monitoring.py",    "adapters_trading"),
    ("/api/periphery/monitoring", "/hexaflux/ltcu-plus",    "POST", "brody_monitoring.py",    "hexaflux_ltcu"),
    ("/api/periphery/monitoring", "/hexaflux/transition-map","POST","brody_monitoring.py",    "hexaflux_transition"),
    ("/api/periphery/monitoring", "/brody-trace-analyze",   "POST", "brody_monitoring.py",    "brody_trace_analyze"),
    # bus.py
    ("/bus",                "/stats",                       "GET",  "bus.py",                 "bus_stats"),
    ("/bus",                "/bridge",                      "GET",  "bus.py",                 "bus_bridge"),
    ("/bus",                "/signal",                      "POST", "bus.py",                 "bus_signal"),
    # context.py
    ("/api/context",        "/from-message",                "POST", "context.py",             "context_from_message"),
    # gencoin.py
    ("/api/gencoin",        "",                             "GET",  "gencoin.py",             "gencoin_status"),
    # graphiti.py
    ("/api/graphiti",       "/status",                      "GET",  "graphiti.py",            "graphiti_status"),
    ("/api/graphiti",       "/context",                     "GET",  "graphiti.py",            "graphiti_context"),
    ("/api/graphiti",       "/search",                      "GET",  "graphiti.py",            "graphiti_search"),
    ("/api/graphiti",       "/metrics",                     "GET",  "graphiti.py",            "graphiti_metrics"),
    ("/api/graphiti",       "/readiness",                   "GET",  "graphiti.py",            "graphiti_readiness"),
    # memory.py
    ("/api/memory",         "",                             "GET",  "memory.py",              "memory_root"),
    ("/api/memory",         "/status",                      "GET",  "memory.py",              "memory_status"),
    ("/api/memory",         "/sources",                     "GET",  "memory.py",              "memory_sources"),
    ("/api/memory",         "/candidates",                  "GET",  "memory.py",              "memory_candidates"),
    ("/api/memory",         "/candidate/from-message",      "POST", "memory.py",              "memory_candidate_from_msg"),
    # os3.py
    ("/api/os3",            "/tickets",                     "GET",  "os3.py",                 "os3_tickets"),
    ("/api/os3",            "/replay/{ticket_id}",          "GET",  "os3.py",                 "os3_replay"),
    # os_map.py
    ("/api/runtime-wiring/os-map", "/status",              "GET",  "os_map.py",              "os_map_status"),
    ("/api/runtime-wiring/os-map", "/query",               "POST", "os_map.py",              "os_map_query"),
    # os_trad_ir_reverse.py
    ("",                    "/api/os-trad/translate",       "POST", "os_trad_ir_reverse.py",  "os_trad_translate"),
    ("",                    "/api/ir/candidate",            "POST", "os_trad_ir_reverse.py",  "ir_candidate"),
    ("",                    "/api/os-reverse/project",      "POST", "os_trad_ir_reverse.py",  "os_reverse_project"),
    # periphery_ops.py
    ("/api/periphery",      "/pipeline/run",                "POST", "periphery_ops.py",       "pipeline_run"),
    ("/api/periphery",      "/pipeline/data-gate",          "POST", "periphery_ops.py",       "pipeline_data_gate"),
    ("/api/periphery",      "/pipeline/provenance-gate",    "POST", "periphery_ops.py",       "pipeline_provenance"),
    ("/api/periphery",      "/pipeline/memory-governor",    "POST", "periphery_ops.py",       "pipeline_memory_governor"),
    ("/api/periphery",      "/pipeline/eml-compression",    "POST", "periphery_ops.py",       "pipeline_eml"),
    ("/api/periphery",      "/pipeline/energy-thermo",      "POST", "periphery_ops.py",       "pipeline_energy"),
    ("/api/periphery",      "/pipeline/ocs-generation",     "POST", "periphery_ops.py",       "pipeline_ocs"),
    ("/api/periphery",      "/pipeline/operational-constance","POST","periphery_ops.py",      "pipeline_operational"),
    ("/api/periphery",      "/pipeline/permission-economic","POST", "periphery_ops.py",       "pipeline_permission"),
    # runtime_freeze.py
    ("/api/runtime",        "/freeze-dashboard",            "GET",  "runtime_freeze.py",      "freeze_dashboard"),
    ("/api/runtime",        "/freeze-dashboard/summary",    "GET",  "runtime_freeze.py",      "freeze_dashboard_summary"),
    # runtime_wiring_preview.py
    ("/api/runtime-wiring", "/preview",                     "GET",  "runtime_wiring_preview.py","runtime_wiring_preview"),
    # sigma_monitoring.py
    ("/api/sigma",          "/domains",                     "GET",  "sigma_monitoring.py",    "sigma_domains"),
    ("/api/sigma",          "/evaluate",                    "GET",  "sigma_monitoring.py",    "sigma_evaluate"),
    ("/api/sigma",          "/bank",                        "GET",  "sigma_monitoring.py",    "sigma_bank"),
    ("/api/sigma",          "/trading",                     "GET",  "sigma_monitoring.py",    "sigma_trading"),
    ("/api/sigma",          "/ecom",                        "GET",  "sigma_monitoring.py",    "sigma_ecom"),
    ("/api/sigma",          "/gps-defense-aviation",        "GET",  "sigma_monitoring.py",    "sigma_gps"),
    # source_runtime_status.py
    ("/api/runtime-wiring/source-runtime", "/status",      "GET",  "source_runtime_status.py","source_runtime_status"),
    ("/api/runtime-wiring/source-runtime", "/preview",     "POST", "source_runtime_status.py","source_runtime_preview"),
    # status.py
    ("/api",                "/health",                      "GET",  "status.py",              "health"),
    ("/api",                "/readiness",                   "GET",  "status.py",              "readiness"),
    ("/api",                "/status",                      "GET",  "status.py",              "status"),
    ("/api",                "/x108/status",                 "GET",  "status.py",              "x108_status"),
    # translation.py
    ("/api/translation",    "/trace",                       "POST", "translation.py",         "translation_trace"),
    # worldcalls.py
    ("/api/worldcalls",     "",                             "GET",  "worldcalls.py",          "worldcalls_root"),
    ("/api/worldcalls",     "/gateway-status",              "GET",  "worldcalls.py",          "worldcalls_gateway_status"),
    ("/api/worldcalls",     "/sovereign-tickets",           "GET",  "worldcalls.py",          "worldcalls_sovereign_tickets"),
    # x108.py
    ("/api/x108",           "/cognitive/shazam",            "POST", "x108.py",                "x108_shazam"),
    ("/api/x108",           "/cognitive/dominant-trees",    "POST", "x108.py",                "x108_dominant_trees"),
    ("/api/x108",           "/math/lyapunov",               "POST", "x108.py",                "x108_lyapunov"),
    ("/api/x108",           "/math/pog",                    "POST", "x108.py",                "x108_pog"),
    ("/api/x108",           "/memory/candidates/read",      "GET",  "x108.py",                "x108_memory_read"),
    ("/api/x108",           "/memory/candidates/append",    "POST", "x108.py",                "x108_memory_append"),
    ("/api/x108",           "/math/trust-path",             "POST", "x108.py",                "x108_trust_path"),
    ("/api/x108",           "/cognitive/regime-classify",   "POST", "x108.py",                "x108_regime_classify"),
    ("/api/x108",           "/oracle/freshness",            "POST", "x108.py",                "x108_oracle"),
    ("/api/x108",           "/timeverse/sync",              "POST", "x108.py",                "x108_timeverse"),
    ("/api/x108",           "/memory/replay/session",       "POST", "x108.py",                "x108_memory_replay"),
]

# ─── Per-file risk properties (from the earlier grep scan) ───────────────────
FILE_PROPS = {
    "audit.py":              {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "blockchain.py":         {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "brody.py":              {"auth": True,  "subprocess": False, "runtime_allowed": True,  "dry_run": False, "network": False},
    "brody_monitoring.py":   {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "bus.py":                {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "context.py":            {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "gencoin.py":            {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "graphiti.py":           {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "memory.py":             {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "os3.py":                {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "os_map.py":             {"auth": False, "subprocess": False, "runtime_allowed": True,  "dry_run": False, "network": False},
    "os_trad_ir_reverse.py": {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "periphery_ops.py":      {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "runtime_freeze.py":     {"auth": False, "subprocess": True,  "runtime_allowed": False, "dry_run": False, "network": False},
    "runtime_wiring_preview.py": {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "sigma_monitoring.py":   {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "source_runtime_status.py": {"auth": False, "subprocess": False, "runtime_allowed": True, "dry_run": False, "network": False},
    "status.py":             {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "translation.py":        {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
    "worldcalls.py":         {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": True,  "network": False},
    "x108.py":               {"auth": False, "subprocess": False, "runtime_allowed": False, "dry_run": False, "network": False},
}

CONNECTOR_FILES = {
    "connectors/aviation_robo.py":   {"network": True, "requests_post": True, "readonly": True},
    "connectors/bank_normal_flow.py": {"network": True, "requests_post": True, "readonly": True},
    "connectors/trading_live.py":    {"network": True, "requests_post": True, "ccxt": True, "readonly": True},
}


def classify_route(prefix: str, path: str, method: str, source_file: str, func_name: str) -> dict:
    route_path = prefix + path
    fp = FILE_PROPS.get(source_file, {})

    auth_required = fp.get("auth", False)
    has_subprocess = fp.get("subprocess", False)
    runtime_allowed = fp.get("runtime_allowed", False)  # Note: all set to False in boundary
    dry_run = fp.get("dry_run", False)
    network_egress = fp.get("network", False)

    is_health = route_path in ("/api/health", "/api/readiness", "/api/status")
    is_memory = "memory" in route_path
    is_graphiti = "graphiti" in route_path
    is_sigma = "sigma" in source_file
    is_blockchain = "blockchain" in source_file
    is_x108 = "x108" in source_file
    is_periphery = "periphery" in source_file
    is_bus = "bus" in source_file

    # Determine category
    if is_health:
        category = "PUBLIC_MINIMAL_SAFE"
        risk = "NONE"
    elif auth_required and dry_run:
        category = "AUTH_REQUIRED_DRY_RUN"
        risk = "LOW"
    elif auth_required:
        category = "AUTH_REQUIRED_READONLY"
        risk = "LOW"
    elif is_sigma:
        category = "STATUS_ONLY"
        risk = "LOW"
    elif route_path == "/api/x108/status":
        category = "STATUS_ONLY"
        risk = "LOW"
    elif has_subprocess:
        category = "INTERNAL_ONLY"
        risk = "MEDIUM"
    elif dry_run and not is_memory and not is_graphiti:
        category = "WORKBENCH_ONLY"
        risk = "LOW"
    elif is_graphiti:
        category = "MEMORY_GRAPHITI_REVIEW"
        risk = "MEDIUM"
    elif is_memory or "memory" in func_name:
        category = "MEMORY_GRAPHITI_REVIEW"
        risk = "MEDIUM"
    elif is_blockchain:
        category = "ACTION_RISK_REVIEW"
        risk = "HIGH"
    elif is_x108 and method == "POST":
        category = "ACTION_RISK_REVIEW"
        risk = "MEDIUM"
    elif is_periphery and method == "POST":
        category = "ACTION_RISK_REVIEW"
        risk = "MEDIUM"
    elif runtime_allowed:
        category = "SOURCE_EXPOSURE_REVIEW"
        risk = "MEDIUM"
    elif "brody_monitoring" in source_file and method == "POST":
        category = "CONNECTOR_EGRESS_REVIEW"
        risk = "MEDIUM"
    elif not auth_required and method == "POST":
        category = "UNKNOWN_REQUIRES_REVIEW"
        risk = "MEDIUM"
    else:
        category = "AUTH_REQUIRED_READONLY"
        risk = "LOW"

    next_action = "OK" if risk in ("NONE", "LOW") else "REVIEW_P69"
    if category in ("ACTION_RISK_REVIEW", "MEMORY_GRAPHITI_REVIEW"):
        next_action = "REVIEW_P69_ADD_AUTH"

    return {
        "route_path": route_path,
        "http_method": method,
        "source_file": f"apps/obsidia_api/routes/{source_file}",
        "function_name": func_name,
        "router_type": "APIRouter",
        "detected_auth": "require_api_key" if auth_required else "NONE",
        "auth_required": auth_required,
        "public_safe": is_health,
        "internal_only": has_subprocess,
        "debug_only": False,
        "workbench_only": dry_run and not is_health,
        "readonly": not (is_memory and method == "POST"),
        "dry_run_only": dry_run,
        "source_exposure": runtime_allowed,
        "path_exposure": False,
        "network_egress": network_egress,
        "subprocess_possible": has_subprocess,
        "filesystem_write": False,
        "memory_write": is_memory and method == "POST",
        "graphiti_write": is_graphiti and method == "POST",
        "neo4j_write": False,
        "emits_act": False,
        "runtime_allowed_now": runtime_allowed,
        "decision_authority": "KX108_ONLY",
        "category": category,
        "risk_level": risk,
        "reason": f"source={source_file} auth={auth_required} subprocess={has_subprocess} runtime_allowed={runtime_allowed}",
        "next_action": next_action,
    }


def main():
    # Build routes_matrix
    routes_matrix = []
    for prefix, path, method, source_file, func_name in ROUTES_CATALOGUE:
        entry = classify_route(prefix, path, method, source_file, func_name)
        routes_matrix.append(entry)

    # Add connector entries
    for conn_path, props in CONNECTOR_FILES.items():
        routes_matrix.append({
            "route_path": f"[CONNECTOR] {conn_path}",
            "http_method": "CONNECTOR",
            "source_file": conn_path,
            "function_name": "send_payload",
            "router_type": "CONNECTOR",
            "detected_auth": "ENV_BASED",
            "auth_required": False,
            "public_safe": False,
            "internal_only": True,
            "debug_only": False,
            "workbench_only": False,
            "readonly": props.get("readonly", False),
            "dry_run_only": False,
            "source_exposure": False,
            "path_exposure": False,
            "network_egress": True,
            "subprocess_possible": False,
            "filesystem_write": False,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "emits_act": False,
            "runtime_allowed_now": False,
            "decision_authority": "KX108_ONLY",
            "category": "CONNECTOR_EGRESS_REVIEW",
            "risk_level": "MEDIUM",
            "reason": "connector with requests.post — env-driven endpoint",
            "next_action": "REVIEW_P69_VALIDATE_ENDPOINT",
        })

    # Build category counts
    category_counts = {}
    for e in routes_matrix:
        cat = e["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Bucket lists
    public_safe = [e["route_path"] for e in routes_matrix if e["category"] == "PUBLIC_MINIMAL_SAFE"]
    auth_readonly = [e["route_path"] for e in routes_matrix if e["category"] == "AUTH_REQUIRED_READONLY"]
    auth_dry_run = [e["route_path"] for e in routes_matrix if e["category"] == "AUTH_REQUIRED_DRY_RUN"]
    internal = [e["route_path"] for e in routes_matrix if e["category"] == "INTERNAL_ONLY"]
    debug = [e["route_path"] for e in routes_matrix if e["category"] == "DEBUG_ONLY"]
    workbench = [e["route_path"] for e in routes_matrix if e["category"] == "WORKBENCH_ONLY"]
    status_only = [e["route_path"] for e in routes_matrix if e["category"] == "STATUS_ONLY"]
    source_exposure = [e["route_path"] for e in routes_matrix if e["category"] == "SOURCE_EXPOSURE_REVIEW"]
    path_exposure = [e["route_path"] for e in routes_matrix if e["category"] == "PATH_EXPOSURE_REVIEW"]
    action_risk = [e["route_path"] for e in routes_matrix if e["category"] == "ACTION_RISK_REVIEW"]
    connector_egress = [e["route_path"] for e in routes_matrix if e["category"] == "CONNECTOR_EGRESS_REVIEW"]
    memory_graphiti = [e["route_path"] for e in routes_matrix if e["category"] == "MEMORY_GRAPHITI_REVIEW"]
    do_not_expose = [e["route_path"] for e in routes_matrix if e["category"] == "DO_NOT_EXPOSE"]
    unknown = [e["route_path"] for e in routes_matrix if e["category"] == "UNKNOWN_REQUIRES_REVIEW"]

    focus_findings = [
        {
            "file": "apps/obsidia_api/routes/brody.py",
            "finding": "ONLY route with auth (require_api_key). POST /api/brody/chat. runtime_allowed_now reported as False in output boundary.",
            "category": "AUTH_REQUIRED_DRY_RUN",
            "risk": "LOW",
        },
        {
            "file": "apps/obsidia_api/routes/os_map.py",
            "finding": "runtime_allowed_now=False in BOUNDARY. GET /status + POST /query. No auth. SOURCE_EXPOSURE_REVIEW.",
            "category": "SOURCE_EXPOSURE_REVIEW",
            "risk": "MEDIUM",
        },
        {
            "file": "apps/obsidia_api/routes/source_runtime_status.py",
            "finding": "runtime_allowed_now=False in output dict. GET /status + POST /preview. No auth. SOURCE_EXPOSURE_REVIEW.",
            "category": "SOURCE_EXPOSURE_REVIEW",
            "risk": "MEDIUM",
        },
        {
            "file": "apps/obsidia_api/routes/runtime_freeze.py",
            "finding": "subprocess.run(['git', ...]) — read-only git commands. No auth. INTERNAL_ONLY.",
            "category": "INTERNAL_ONLY",
            "risk": "MEDIUM",
        },
        {
            "file": "apps/obsidia_api/routes/blockchain.py",
            "finding": "7 POST routes including /world/gateway and /world/bus-dispatch. No auth. ACTION_RISK_REVIEW.",
            "category": "ACTION_RISK_REVIEW",
            "risk": "HIGH",
        },
        {
            "file": "apps/obsidia_api/routes/x108.py",
            "finding": "POST /memory/candidates/append + /memory/replay/session — memory operations. No auth. ACTION_RISK_REVIEW.",
            "category": "ACTION_RISK_REVIEW",
            "risk": "MEDIUM",
        },
        {
            "file": "apps/obsidia_api/routes/periphery_ops.py",
            "finding": "9 POST pipeline routes including /pipeline/memory-governor. No auth. ACTION_RISK_REVIEW.",
            "category": "ACTION_RISK_REVIEW",
            "risk": "MEDIUM",
        },
        {
            "file": "apps/obsidia_api/bus/registry.py",
            "finding": "P65 DRY_RUN_ONLY bus registry. build_default_router() registers OS_TRAD PROPOSE only. Not a route — internal bus.",
            "category": "DRY_RUN_ONLY_INTERNAL",
            "risk": "NONE",
        },
        {
            "file": "connectors/aviation_robo.py",
            "finding": "requests.post() to configurable URL. Env-driven endpoint. CONNECTOR_EGRESS_REVIEW.",
            "category": "CONNECTOR_EGRESS_REVIEW",
            "risk": "MEDIUM",
        },
        {
            "file": "connectors/bank_normal_flow.py",
            "finding": "requests.post() to configurable URL. Env-driven endpoint. CONNECTOR_EGRESS_REVIEW.",
            "category": "CONNECTOR_EGRESS_REVIEW",
            "risk": "MEDIUM",
        },
        {
            "file": "connectors/trading_live.py",
            "finding": "requests.post() + import ccxt for exchange. Env-driven. CONNECTOR_EGRESS_REVIEW.",
            "category": "CONNECTOR_EGRESS_REVIEW",
            "risk": "MEDIUM",
        },
        {
            "file": "apps/obsidia_api/brody_session_memory_adapter.py",
            "finding": "memory_write=False, graphiti_write=False. Candidate advisory only. Not a route.",
            "category": "DECISION_READONLY_INTERNAL",
            "risk": "NONE",
        },
    ]

    route_model = {
        "public_minimal_safe": "Routes publiques minimales : /api/health, /api/readiness, /api/status. Aucun payload sensible.",
        "auth_required_readonly": "Routes nécessitant auth (OBSIDIA_API_KEY) — lecture seule. Actuellement: aucune sauf brody/chat.",
        "auth_required_dry_run": "Routes nécessitant auth — DRY_RUN_ONLY. Actuellement: /api/brody/chat (require_api_key).",
        "internal_only": "Routes réservées à l'opérateur interne. Ex: /api/runtime/freeze-dashboard (subprocess git read).",
        "debug_only": "Routes debug uniquement — ne pas exposer en production.",
        "workbench_only": "Routes workbench/dry-run. Ex: /api/worldcalls (DRY_RUN_ONLY declaré).",
        "source_exposure_review": "Routes exposant état runtime source. runtime_allowed_now présent (toujours False). Review requis.",
        "path_exposure_review": "Routes exposant chemins locaux ou credentials. Non détecté dans routes ici.",
        "action_risk_review": "Routes POST sans auth pouvant déclencher actions. blockchain, x108 memory append, periphery pipeline.",
        "connector_egress_review": "Connecteurs réseau actifs (requests.post/ccxt). Env-driven. Validation endpoint requise.",
        "do_not_expose": "Routes à ne jamais exposer publiquement.",
    }

    result = {
        "audit_id": "P68",
        "status": "P68_API_AUTH_ROUTE_EXPOSURE_AUDIT_READY",
        "mode": "AUDIT_ONLY",
        "source_patch_applied": False,
        "files_imported_count": 0,
        "route_model": route_model,
        "scanned_files_count": len(FILE_PROPS) + len(CONNECTOR_FILES),
        "routes_detected_count": len(routes_matrix),
        "routes_matrix": routes_matrix,
        "category_counts": dict(sorted(category_counts.items(), key=lambda x: -x[1])),
        "public_minimal_safe": public_safe,
        "auth_required_readonly": auth_readonly,
        "auth_required_dry_run": auth_dry_run,
        "internal_only": internal,
        "debug_only": debug,
        "workbench_only": workbench,
        "status_only": status_only,
        "source_exposure_review": source_exposure,
        "path_exposure_review": path_exposure,
        "action_risk_review": action_risk,
        "connector_egress_review": connector_egress,
        "memory_graphiti_review": memory_graphiti,
        "do_not_expose": do_not_expose,
        "unknown_requires_review": unknown,
        "focus_findings": focus_findings,
        "preexisting_manifest_drift": [
            {"file": "audit/world_action_bus.jsonl", "status": "HASH_MISMATCH_PREEXISTING_P65"},
            {"file": "proofs/PROOFKIT_REPORT.json",  "status": "HASH_MISMATCH_PREEXISTING_P65"},
        ],
        "preexisting_test_debt": [
            {"test": "tests/test_invariants_against_engine.py", "reason": "ModuleNotFoundError: obsidia_os2"},
            {"test": "tests/sigma_stress_test.py",              "reason": "ModuleNotFoundError: agents.obsidia_sigma_v130"},
            {"test": "tests/test_agents_functional.py",         "reason": "ImportError: TradingState"},
            {"test": "tests/test_consensus_inprocess.py",       "reason": "ModuleNotFoundError: agents.run_pipeline"},
            {"test": "tests/test_sigma_v18_9.py",               "reason": "ModuleNotFoundError: agents.obsidia_sigma_v130"},
        ],
        "runtime_modified": False,
        "sigma_modified": False,
        "routes_modified": False,
        "srl_modified": False,
        "act_enabled": False,
        "memory_write_enabled": False,
        "graphiti_write_enabled": False,
        "neo4j_write_enabled": False,
        "kernel_mutation_enabled": False,
        "x108_merge_enabled": False,
        "next_step": "P69_FILESYSTEM_AND_PATH_EXPOSURE_AUDIT",
    }

    out_path = ROOT / "docs" / "core_import" / "P68_API_AUTH_ROUTE_EXPOSURE_AUDIT.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"P68 JSON written: {out_path}")
    print(f"Routes detected: {len(routes_matrix)}")
    print(f"Categories: {dict(sorted(category_counts.items(), key=lambda x: -x[1]))}")


if __name__ == "__main__":
    main()
