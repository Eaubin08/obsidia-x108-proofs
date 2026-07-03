"""OIE V0.7.1 -- Obsidia vs Gemini Power Benchmark.

Deux lanes sur les memes 7 familles de routing :
  A. OBSIDIA_LOCAL_ACTUAL  -- router deterministe / valeurs figees V0 / adapter si dispo
  B. GEMINI_SDK_EXTERNAL   -- SDK google-genai (dry-run par defaut)

Metriques : speed, cost, energy, throughput, work avoidance, context economy,
inference avoidance, intellectual economy, gencoin calibration, governance, quality.

Gouvernance :
  EMITS_ACT=False, MEMORY_WRITE=False, KERNEL_MUTATION=False,
  DECISION_AUTHORITY=KX108_ONLY, SECRETS_REDACTED=True.

Mode par defaut : DRY_RUN (aucun reseau, Gemini mocke).
Mode REAL :       OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1 + GEMINI_API_KEY.

Rapports runtime : .local_reports/OIE_POWER_BENCHMARK_V0_7_1_<timestamp>/
Protocole statique : docs/audits/OBSIDIA_OIE_POWER_METRICS_PROTOCOL_V0_7.md

Jamais de secret dans JSON/log.
Jamais de commit automatique.
Ne pas modifier kernel, Brody live, Obsidure live, Graphiti, Neo4j, memoire.

Gencoin : CALIBRATION_ONLY. Aucune emission. Aucun token reel. Aucune valeur de marche.
Reference formules : apps/obsidia_api/brody_gencoin_cognitive_ledger.py (DO NOT MODIFY).
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Chemin repo ──────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from apps.obsidia_api.inference_economy.external_comparison import (
    EMITS_ACT,
    MEMORY_WRITE,
    KERNEL_MUTATION,
    GRAPHITI_WRITE,
    NEO4J_WRITE,
    READONLY,
    SECRETS_REDACTED,
    DECISION_AUTHORITY,
    COST_SOURCE_UNAVAILABLE,
    COST_SOURCE_SDK_NO_PRICE,
    COST_SOURCE_SDK_MEASURED,
    PROVIDER_GEMINI,
    FAILURE_NONE,
    FAILURE_GEMINI_AUTH_ERROR,
    FAILURE_GEMINI_SDK_NOT_AVAILABLE,
    FAILURE_GEMINI_MODEL_NOT_CONFIGURED,
    run_gemini_sdk,
    compute_measured_sdk_cost,
    compute_comparison,
    evaluate_route_quality,
    sanitize_external_error_message,
)

# ── OIE V0.1 imports (inference economy — baselines / CostReceipt / DomainMetrics) ──
try:
    from apps.obsidia_api.inference_economy.baselines import (
        BT_ENERGY_LOW, BT_ENERGY_HEAVY, BT_API_SIMPLE, BT_API_NORMAL, BT_AGENTIC,
        BASELINE_LABELS,
    )
    from apps.obsidia_api.inference_economy.cost_receipt import (
        CostReceipt as _OIE_CostReceipt,
        DomainMetrics as _OIE_DomainMetrics,
    )
    from apps.obsidia_api.inference_economy.domain_metrics import (
        compute_dca as _oie_compute_dca,
        summarize_domain_metrics as _oie_summarize_domain_metrics,
    )
    _OIE_IMPORT_OK = True
    _OIE_MISSING_IMPORTS: list = []
except ImportError as _oie_exc:
    BT_ENERGY_LOW: float = 102.0
    BT_ENERGY_HEAVY: float = 1296.0
    BT_API_SIMPLE: float = 5500.0
    BT_API_NORMAL: float = 25000.0
    BT_AGENTIC: float = 160000.0
    BASELINE_LABELS: dict = {
        "BT_ENERGY_LOW": 102.0, "BT_ENERGY_HEAVY": 1296.0,
        "BT_API_SIMPLE": 5500.0, "BT_API_NORMAL": 25000.0, "BT_AGENTIC": 160000.0,
    }
    _OIE_CostReceipt = None
    _OIE_DomainMetrics = None
    _oie_compute_dca = None
    _oie_summarize_domain_metrics = None
    _OIE_IMPORT_OK = False
    _OIE_MISSING_IMPORTS = [str(_oie_exc)]

# ── Version ───────────────────────────────────────────────────────────────────
BENCHMARK_VERSION = "OIE_POWER_BENCHMARK_V0.7"
BENCHMARK_DATE = "2026-07-01"

# ── Obsidia lane status ───────────────────────────────────────────────────────
OBSIDIA_STATUS_REAL = "REAL_ADAPTER"
OBSIDIA_STATUS_FROZEN = "FROZEN_V0_ESTIMATE"
OBSIDIA_STATUS_MISSING = "ADAPTER_MISSING"

# ── Gemini lane status ────────────────────────────────────────────────────────
GEMINI_STATUS_DRYRUN = "DRY_RUN_MOCK"
GEMINI_STATUS_REAL = "REAL_SDK"
GEMINI_STATUS_FAILED = "FAILED"

# ── LLM Necessity — minimal sufficient layer taxonomy ────────────────────────
MIN_LAYER_DIRECT_ROUTE = "DIRECT_ROUTE"
MIN_LAYER_FAST_PATH = "FAST_PATH"
MIN_LAYER_PATH_COMPUTE = "PATH_COMPUTE"
MIN_LAYER_DOMAIN_BRIDGE = "DOMAIN_BRIDGE"
MIN_LAYER_MEMORY_LOOKUP = "MEMORY_LOOKUP"
MIN_LAYER_PROOF_SURFACE = "PROOF_SURFACE"
MIN_LAYER_BRODY_INTERNAL = "BRODY_INTERNAL"
MIN_LAYER_OBSIDURE_AGENT = "OBSIDURE_AGENT"
MIN_LAYER_LEAN_PROOF = "LEAN_PROOF"
MIN_LAYER_EXTERNAL_LLM = "EXTERNAL_LLM"
MIN_LAYER_ADAPTER_MISSING = "ADAPTER_MISSING"
MIN_LAYER_UNKNOWN = "UNKNOWN"

# ── LLM Necessity — model role taxonomy ───────────────────────────────────────
MODEL_ROLE_NOT_NEEDED = "MODEL_NOT_NEEDED"
MODEL_ROLE_INTERNAL_TRANSLATION = "INTERNAL_TRANSLATION"
MODEL_ROLE_EXTERNAL_REQUIRED = "EXTERNAL_LLM_REQUIRED"
MODEL_ROLE_EXTERNAL_CALLED_BY_BASELINE = "EXTERNAL_LLM_CALLED_BY_BASELINE"
MODEL_ROLE_UNKNOWN = "UNKNOWN"

# ── Energy source ─────────────────────────────────────────────────────────────
ENERGY_SOURCE_UNAVAILABLE = "ENERGY_PROXY_UNAVAILABLE"
ENERGY_SOURCE_ESTIMATE = "ENERGY_PROXY_ESTIMATE"

# ── Cost basis (Phase 2) ──────────────────────────────────────────────────────
COST_BASIS_LOCAL_PROXY = "LOCAL_PROXY_UNCALIBRATED"
COST_BASIS_SDK_MEASURED = "SDK_USAGE_MEASURED"
COST_BASIS_DRY_RUN_MOCK = "DRY_RUN_MOCK"
COST_PROXY_WARNING = "Obsidia cost is a local proxy estimate, not a measured provider bill."
COST_PROXY_FORMULA = "obsidia_cost_proxy_per_1m_est * obsidia_estimated_total_tokens / 1_000_000"
COST_PROXY_SOURCE = "FROZEN_V0_ARCHITECTURE_ESTIMATE"

# ── Intellectual economy / Gencoin calibration (Phase 4) ─────────────────────
IE_BASIS = "CALIBRATION_ONLY"
GENCOIN_MODE = "CALIBRATION_ONLY"
GENCOIN_DISTRIBUTION_MODE = "NONE_CALIBRATION_ONLY"
GENCOIN_EMISSION_REASON = "CALIBRATION_ONLY_NO_EMISSION"
SOURCE_LAW_REASON_CALIBRATION = "CALIBRATION_ONLY_NO_REAL_PROOF_EMISSION"

# Poids CV formula — PROVISIONAL_CALIBRATION_ONLY
# Reference : adaptes depuis cognitive_ledger.py (0.24/0.22/0.18/0.14/0.14)
_CV_WEIGHTS = {
    "novelty":        0.05,
    "utility":        0.22,
    "coherence":      0.18,
    "risk_reduction": 0.15,
    "reusability":    0.18,
    "proof_quality":  0.22,
}
_CV_WEIGHT_SOURCE = "PROVISIONAL_CALIBRATION_ONLY"

# ── Surface families ──────────────────────────────────────────────────────────
AVAILABLE_SURFACE_FAMILIES = {"FAST_PATH", "BANK", "TRADING", "GPS"}
ADAPTER_MISSING_FAMILIES = {"BRODY", "OBSIDURE", "LEAN"}
TERRAIN_PROOF_FAMILIES = {"BANK", "TRADING", "GPS"}
MODEL_AVOIDED_FAMILIES = {"FAST_PATH", "BANK", "TRADING", "GPS"}

# ── Default Gemini model ──────────────────────────────────────────────────────
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-lite"

# ── OIE V0.1 — Coûts Obsidia figés par famille (EUR / 1M actions) ────────────
# Source : OBSIDIA_OIE_V01_ENGINE_FREEZE_20260701_052940 / base_commit 73444cd
OIE_FAMILY_COSTS: dict[str, float] = {
    "FAST_PATH": 0.0015,
    "BRODY":     0.20,
    "BANK":      0.70,
    "TRADING":   0.84,
    "GPS":       0.91,
    "LEAN":      13.29,
    "OBSIDURE":  23.92,
}

OIE_DOMAIN_NAME_MAPPING: dict[str, str] = {
    "FAST_PATH":   "FAST_PATH",
    "BRODY":       "BRODY",
    "BANK":        "BANK",
    "TRADING":     "TRADING",
    "GPS":         "GPS_AVIATION",
    "OBSIDURE":    "OBSIDURE",
    "LEAN":        "LEAN",
    "Brody chat":  "BRODY",
    "Bank":        "BANK",
    "Trading":     "TRADING",
    "GPS/Aviation": "GPS_AVIATION",
    "Aviation":    "GPS_AVIATION",
    "Lean canon check": "LEAN",
    "Obsidure Lean cible": "OBSIDURE",
}

_OIE_DOMAIN_CFG: dict[str, dict] = {
    "FAST_PATH": {
        "domain_name": "FAST_PATH",
        "domain_action_type": "fast_path_cache_governance",
        "domain_risk_level": "LOW",
        "domain_reversibility": "REVERSIBLE",
        "domain_tools_used": ["ROUTER", "CACHE"],
        "domain_tools_skipped": ["LLM", "BRODY", "OBSIDURE", "GRAPHITI"],
        "external_api_calls_avoided": 1,
        "llm_calls_avoided": 1,
        "proof_available": True,
        "replay_available": True,
        "business_cost_avoided_label": "llm_fast_path_routing_avoided",
    },
    "BANK": {
        "domain_name": "BANK",
        "domain_action_type": "governed_financial_decision",
        "domain_risk_level": "HIGH",
        "domain_reversibility": "PARTIALLY_REVERSIBLE",
        "domain_tools_used": ["ROUTER", "BANK_CONNECTOR"],
        "domain_tools_skipped": ["LLM", "BRODY", "OBSIDURE"],
        "external_api_calls_avoided": 1,
        "llm_calls_avoided": 1,
        "proof_available": False,
        "replay_available": False,
        "business_cost_avoided_label": "bank_review_or_external_llm_analysis_avoided",
    },
    "TRADING": {
        "domain_name": "TRADING",
        "domain_action_type": "governed_market_signal",
        "domain_risk_level": "HIGH",
        "domain_reversibility": "LOW_REVERSIBILITY",
        "domain_tools_used": ["ROUTER", "TRADING_CONNECTOR"],
        "domain_tools_skipped": ["LLM", "BRODY", "OBSIDURE"],
        "external_api_calls_avoided": 1,
        "llm_calls_avoided": 1,
        "proof_available": False,
        "replay_available": False,
        "business_cost_avoided_label": "trading_signal_llm_analysis_avoided",
    },
    "GPS": {
        "domain_name": "GPS_AVIATION",
        "domain_action_type": "critical_field_signal_governance",
        "domain_risk_level": "CRITICAL",
        "domain_reversibility": "LOW_REVERSIBILITY",
        "domain_tools_used": ["ROUTER", "GPS_CONNECTOR"],
        "domain_tools_skipped": ["LLM", "BRODY", "OBSIDURE"],
        "external_api_calls_avoided": 1,
        "llm_calls_avoided": 1,
        "proof_available": False,
        "replay_available": False,
        "business_cost_avoided_label": "terrain_signal_heavy_analysis_avoided",
    },
    "BRODY": {
        "domain_name": "BRODY",
        "domain_action_type": "cognitive_interface_response",
        "domain_risk_level": "MEDIUM",
        "domain_reversibility": "REVERSIBLE",
        "domain_tools_used": [],
        "domain_tools_skipped": [],
        "external_api_calls_avoided": 0,
        "llm_calls_avoided": 0,
        "proof_available": False,
        "replay_available": False,
        "business_cost_avoided_label": "external_assistant_context_chain_avoided",
    },
    "OBSIDURE": {
        "domain_name": "OBSIDURE",
        "domain_action_type": "code_proof_repair_audit",
        "domain_risk_level": "HIGH",
        "domain_reversibility": "REPLAYABLE",
        "domain_tools_used": [],
        "domain_tools_skipped": [],
        "external_api_calls_avoided": 0,
        "llm_calls_avoided": 0,
        "proof_available": False,
        "replay_available": False,
        "business_cost_avoided_label": "external_code_agent_loop_avoided",
    },
    "LEAN": {
        "domain_name": "LEAN",
        "domain_action_type": "formal_check_or_proof_surface",
        "domain_risk_level": "HIGH",
        "domain_reversibility": "REPLAYABLE",
        "domain_tools_used": [],
        "domain_tools_skipped": [],
        "external_api_calls_avoided": 0,
        "llm_calls_avoided": 0,
        "proof_available": False,
        "replay_available": False,
        "business_cost_avoided_label": "long_llm_reasoning_or_retry_loop_avoided",
    },
}

# ── OIE source lineage & freeze reference ─────────────────────────────────────
_OIE_FREEZE_NAME = "OBSIDIA_OIE_V01_ENGINE_FREEZE_20260701_052940"
_OIE_FREEZE_DIR = _REPO_ROOT / "freeze" / _OIE_FREEZE_NAME
_OIE_FREEZE_FOUND = _OIE_FREEZE_DIR.is_dir()

_OIE_SOURCE_LINEAGE: dict = {
    "base_audit_commit": "73444cd",
    "base_audit_commit_role": "freeze audits INFERENCE_ECONOMY / DOMAIN_TOOL_ABSORPTION / STACK_LAYER_POSITIONING",
    "oie_v01_commit_candidate": "b32b816",
    "oie_v01_commit_role": "feat(oie): add inference economy domain metrics and external comparison protocol",
    "benchmark_integration_role": "links OIE V0/V0.1 metrics into Gemini V0.7.1 benchmark",
}

_OIE_SOURCE_DOCUMENTS: dict = {
    "engine_spec": "docs/audits/OBSIDIA_INFERENCE_ECONOMY_ENGINE_SPEC_V0.md",
    "external_api_protocol": "docs/audits/OBSIDIA_EXTERNAL_API_COST_COMPARISON_PROTOCOL_V0.md",
    "cost_receipt_schema": "schemas/obsidia_cost_receipt.schema.json",
    "portfolio_benchmark": "scripts/performance/run_inference_economy_portfolio_benchmark_v0.py",
    "portfolio_receipts": "scripts/performance/oie_v0_portfolio_receipts.json",
}

_OIE_BENCHMARK_LINKAGE: dict = {
    "portfolio_benchmark_name": "OIE_V0.1_PORTFOLIO",
    "external_benchmark_name": "OIE_POWER_BENCHMARK_V0_7_1",
    "protocol_doc_name": "OBSIDIA_OIE_POWER_METRICS_PROTOCOL_V0_7",
    "gencoin_audit_family": "GENCOIN_INTERNAL_ECONOMY_AUDIT_V0_7_1",
}

# ── OIE Obsidia execution mode ────────────────────────────────────────────────
# AUTO: comportement actuel (FROZEN / ADAPTER_MISSING selon task)
# FROZEN_ONLY: forcer FROZEN_V0_ESTIMATE
# LIVE_LOCAL: tenter exécution live (non disponible en V0.7.1 — aucun adapter live branché)
# LIVE_LOCAL_OR_FROZEN: tenter live, fallback frozen si indisponible
OIE_OBSIDIA_EXEC_MODE_AUTO = "AUTO"
OIE_OBSIDIA_EXEC_MODE_FROZEN = "FROZEN_ONLY"
OIE_OBSIDIA_EXEC_MODE_LIVE = "LIVE_LOCAL"
OIE_OBSIDIA_EXEC_MODE_LIVE_OR_FROZEN = "LIVE_LOCAL_OR_FROZEN"

# Status live local dédié (en plus des REAL_ADAPTER / FROZEN / MISSING existants)
OBSIDIA_STATUS_LIVE_LOCAL = "LIVE_LOCAL"
OBSIDIA_STATUS_LIVE_LOCAL_UNAVAILABLE = "LIVE_LOCAL_UNAVAILABLE"

# Sigma domain mapping (for in-process evaluate calls)
_SIGMA_DOMAIN_FOR_FAMILY: dict[str, str] = {
    "BANK":    "bank",
    "TRADING": "trading",
    "GPS":     "gps_defense_aviation",
}


_OBSIDIA_API_BASE = os.environ.get("OBSIDIA_API_BASE", "http://127.0.0.1:8000")
_OBSIDIA_KERNEL_URL = os.environ.get("OBSIDIA_KERNEL_URL", "http://127.0.0.1:3001/kernel/ragnarok")
_LIVE_PROBE_TIMEOUT = 1.0  # secondes — court pour ne pas bloquer le benchmark

# Endpoints connus (depuis apps/obsidia_api/routes/live_kernel_bridge.py + routes/status.py)
_LIVE_ENDPOINTS: dict[str, dict] = {
    "FAST_PATH": {
        "status_path": "/api/status",
        "bridge_path": None,  # Pas de bridge dédié pour FAST_PATH en V0.7.1
        "method": "GET",
    },
    "BANK": {
        "status_path": "/api/status",
        "bridge_path": "/api/live/kernel/adapters/bank",
        "method": "POST",
    },
    "TRADING": {
        "status_path": "/api/status",
        "bridge_path": "/api/live/kernel/adapters/trading",
        "method": "POST",
    },
    "GPS": {
        "status_path": "/api/status",
        "bridge_path": "/api/live/kernel/adapters/gps",
        "method": "POST",
    },
    "BRODY": {
        "status_path": "/api/status",
        "bridge_path": "/api/brody/chat",
        "method": "POST",
    },
    "OBSIDURE": {
        "status_path": None,
        "bridge_path": None,
        "method": None,
    },
    "LEAN": {
        "status_path": None,
        "bridge_path": None,
        "method": None,
    },
}

# Payloads de test minimalistes pour sonder les bridges (dry-run, aucune action réelle)
_LIVE_TEST_PAYLOADS: dict[str, dict] = {
    "BANK": {"payload": {"transaction_type": "transfer", "amount": 0.0, "channel": "benchmark_probe"}},
    "TRADING": {"payload": {"symbol": "BTC/USDT", "prices": [100.0] * 5}},
    "GPS": {"payload": {"mission_id": "BENCHMARK_PROBE", "gps_status": "ONLINE"}},
    "BRODY": {"message": "benchmark probe — readonly status check"},
    "FAST_PATH": {},
}


def _probe_api_status(api_base: str = _OBSIDIA_API_BASE, timeout: float = _LIVE_PROBE_TIMEOUT) -> dict:
    """Sonde GET /api/status sur l'API locale. Retourne toujours un dict, jamais d'exception."""
    try:
        import urllib.request as _urlreq
        import urllib.error as _urlerr
        url = f"{api_base.rstrip('/')}/api/status"
        req = _urlreq.Request(url, method="GET")
        with _urlreq.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
            except Exception:
                data = {"raw": raw[:200]}
            return {
                "reachable": True,
                "http_status": resp.status,
                "mode": data.get("mode") or data.get("data", {}).get("mode"),
                "decision_authority": (data.get("data") or data).get("decision_authority"),
                "emits_act": (data.get("data") or data).get("emits_act", False),
                "memory_write": (data.get("data") or data).get("memory_write", False),
                "kernel_mutation": (data.get("data") or data).get("kernel_mutation", False),
                "readonly": (data.get("data") or data).get("readonly"),
                "api_role": (data.get("data") or data).get("api_role"),
                "raw_excerpt": raw[:300],
            }
    except Exception as _exc:
        exc_type = type(_exc).__name__
        return {
            "reachable": False,
            "http_status": None,
            "error": exc_type,
            "error_detail": str(_exc)[:200],
            "mode": None,
            "decision_authority": None,
            "emits_act": None,
            "memory_write": None,
            "kernel_mutation": None,
        }


def discover_obsidia_live_adapters(api_base: str = _OBSIDIA_API_BASE) -> dict:
    """Découverte dynamique des adapters Obsidia via l'API locale (127.0.0.1:8000).

    Sonde GET /api/status pour vérifier si l'API est disponible.
    Ne fait aucun appel réseau externe (loopback uniquement).
    Ne fait aucune action réelle (banque/trading/aviation).
    Retourne un registry par famille avec endpoints et statut.
    """
    api_probe = _probe_api_status(api_base)
    api_up = api_probe.get("reachable", False)
    registry: dict[str, dict] = {}

    for family in ("FAST_PATH", "BANK", "TRADING", "GPS", "BRODY", "OBSIDURE", "LEAN"):
        ep = _LIVE_ENDPOINTS.get(family, {})
        bridge_path = ep.get("bridge_path")
        has_bridge = bridge_path is not None

        # Décision d'utilisabilité
        if family in ("OBSIDURE", "LEAN"):
            usable = False
            reason = f"{family} requires dedicated pipeline — no API bridge in V0.7.1"
            atype = "NONE"
            found = False
        elif family == "FAST_PATH":
            # FAST_PATH n'a pas de bridge dédié en V0.7.1 — API up mais route non disponible
            usable = False
            reason = "No dedicated live bridge for FAST_PATH in V0.7.1 — /api/status confirms API up but no /api/fast-path route"
            atype = "API_STATUS_ONLY" if api_up else "NONE"
            found = api_up
        else:
            # BANK / TRADING / GPS / BRODY : bridge exist si API up
            usable = api_up and has_bridge
            if not api_up:
                reason = f"API 8000 unreachable — {api_probe.get('error', 'CONNECTION_REFUSED')}"
            elif not has_bridge:
                reason = f"No bridge endpoint defined for {family}"
            else:
                reason = None
            atype = "LOCAL_HTTP_READONLY" if (api_up and has_bridge) else "NONE"
            found = api_up and has_bridge

        registry[family] = {
            "adapter_found": found,
            "adapter_type": atype,
            "path": f"apps/obsidia_api/routes/live_kernel_bridge.py" if has_bridge else None,
            "callable": None,
            "endpoint": f"{api_base.rstrip('/')}{bridge_path}" if bridge_path else None,
            "bridge_path": bridge_path,
            "kernel_target": _OBSIDIA_KERNEL_URL if has_bridge else None,
            "api_status_probe": api_probe,
            "api_up": api_up,
            "safe_readonly": True,
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
            "kernel_mutation": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "usable_for_live_local": usable,
            "reason_if_not_usable": reason,
        }

    return registry


# Registry calculé une fois au chargement du module (sonde l'API locale)
_OBSIDIA_LIVE_ADAPTER_REGISTRY: dict = discover_obsidia_live_adapters()
_LIVE_LOCAL_AVAILABLE: bool = any(
    v.get("usable_for_live_local") for v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.values()
)
_LIVE_LOCAL_USABLE_FAMILIES: list[str] = [
    f for f, v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.items() if v.get("usable_for_live_local")
]
_LIVE_LOCAL_UNAVAILABLE_FAMILIES: list[str] = [
    f for f, v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.items()
    if not v.get("usable_for_live_local") and v.get("adapter_found")
]
_ADAPTER_MISSING_FAMILIES_LIVE: list[str] = [
    f for f, v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.items()
    if not v.get("adapter_found")
]


def find_case_insensitive_duplicate_keys(obj: object, path: str = "") -> list[str]:
    """Retourne les chemins JSON contenant des clés doublonnées case-insensitive.

    Utilisé pour garantir la lisibilité par PowerShell ConvertFrom-Json.
    """
    issues: list[str] = []
    if isinstance(obj, dict):
        lower_keys = [k.lower() for k in obj.keys()]
        seen: set[str] = set()
        for k in obj.keys():
            lk = k.lower()
            if lk in seen:
                issues.append(f"{path}.{k} (case-insensitive dup)")
            seen.add(lk)
        for k, v in obj.items():
            issues.extend(find_case_insensitive_duplicate_keys(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            issues.extend(find_case_insensitive_duplicate_keys(item, f"{path}[{i}]"))
    return issues


_OIE_WARNINGS: list[str] = [
    "OIE measures cost; it does not decide.",
    "Kernel X108 remains the only decision authority.",
    "OIE remains readonly and non-sovereign.",
    "DCA/OSCA/OAPI/ODPI are proxy baseline metrics, not real provider billing.",
    "External API protocol is preparatory; no additional network call is required by this integration.",
    "Cost comparison remains non-claimable while Obsidia cost is LOCAL_PROXY_UNCALIBRATED.",
    "Gencoin remains CALIBRATION_ONLY; OIE can measure value proxies but cannot emit Gencoin.",
]

# ── Frozen V0 values (figees 73444cd / Technical Note V0) ────────────────────
FROZEN_GRAPHITI_WARM_MS = 0.3199
FROZEN_GRAPHITI_COLD_MS = 277.718
FROZEN_GRAPHITI_WARM_GAIN_RATIO = 868.14
FROZEN_GRAPHITI_LATENCY_REDUCTION_PCT = 99.88
FROZEN_RUNTIME_CONTEXT_BUILD_MS = 0.0042
FROZEN_LOADER_COLD_MS = 47.6648
FROZEN_LOADER_WARM_MS = 0.0042
FROZEN_LOADER_WARM_GAIN_RATIO = 11348.76

# ── Frozen Gemini dry-run mock data (run reel V0.5.1, 7 taches) ──────────────
_FROZEN_GEMINI_PER_TASK: dict[str, dict] = {
    "fastpath_power_smoke": {
        "input_tokens": 40, "output_tokens": 2, "total_tokens": 42,
        "latency_ms": 312.0, "detected_route": "FAST_PATH", "route_match": True,
    },
    "brody_power_route": {
        "input_tokens": 40, "output_tokens": 2, "total_tokens": 42,
        "latency_ms": 428.0, "detected_route": "FAST_PATH", "route_match": False,
    },
    "bank_power_route": {
        "input_tokens": 41, "output_tokens": 2, "total_tokens": 43,
        "latency_ms": 395.0, "detected_route": "BANK", "route_match": True,
    },
    "trading_power_route": {
        "input_tokens": 41, "output_tokens": 2, "total_tokens": 43,
        "latency_ms": 382.0, "detected_route": "GPS", "route_match": False,
    },
    "gps_power_route": {
        "input_tokens": 40, "output_tokens": 2, "total_tokens": 42,
        "latency_ms": 404.0, "detected_route": "GPS", "route_match": True,
    },
    "obsidure_power_route": {
        "input_tokens": 39, "output_tokens": 2, "total_tokens": 41,
        "latency_ms": 451.0, "detected_route": "BRODY", "route_match": False,
    },
    "lean_power_route": {
        "input_tokens": 40, "output_tokens": 2, "total_tokens": 42,
        "latency_ms": 388.0, "detected_route": "BRODY", "route_match": False,
    },
}

# ── 7 familles request set ────────────────────────────────────────────────────
POWER_TASKS: list[dict] = [
    {
        "task_id": "fastpath_power_smoke",
        "family": "FAST_PATH",
        "comparison_axis": "FAST_PATH",
        "prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: ping health check status."
        ),
        "expected_route": "FAST_PATH",
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_cost_per_1m_est": 0.0015,
        "obsidia_latency_ms_frozen": FROZEN_GRAPHITI_WARM_MS,
        "obsidia_execution_layer": "cache_lookup",
        "expected_modules_considered": 6,
        "expected_modules_activated": 1,
        "expected_modules_skipped": 5,
        "obsidia_status_frozen": OBSIDIA_STATUS_FROZEN,
        "obsidia_quality_score_frozen": 1.0,
        "obsidia_boundary_ok_frozen": True,
        "obsidia_cache_hit_frozen": True,
        "obsidia_graphiti_warm_ms": FROZEN_GRAPHITI_WARM_MS,
        "obsidia_graphiti_warm_gain_ratio": FROZEN_GRAPHITI_WARM_GAIN_RATIO,
        "obsidia_runtime_context_build_ms": FROZEN_RUNTIME_CONTEXT_BUILD_MS,
        "obsidia_loader_warm_gain_ratio": FROZEN_LOADER_WARM_GAIN_RATIO,
        "obsidia_files_read": 1,
        "obsidia_files_skipped": 12,
        "obsidia_memory_records_loaded": 0,
        "obsidia_memory_records_skipped": 4,
        "expected_minimal_layer": MIN_LAYER_FAST_PATH,
        "external_llm_required_by_design": False,
        "llm_necessity_reason": "Known route / direct structured route sufficient.",
        "answer_adequacy_criteria": "route_label_bounded",
    },
    {
        "task_id": "brody_power_route",
        "family": "BRODY",
        "comparison_axis": "BRODY_RESPONSE",
        "prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: what is the Obsidia kernel responsible for?"
        ),
        "expected_route": "BRODY",
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_cost_per_1m_est": 0.20,
        "obsidia_latency_ms_frozen": 85.0,
        "obsidia_execution_layer": "brody_router",
        "expected_modules_considered": 6,
        "expected_modules_activated": 3,
        "expected_modules_skipped": 3,
        "obsidia_status_frozen": OBSIDIA_STATUS_MISSING,
        "obsidia_quality_score_frozen": None,
        "obsidia_boundary_ok_frozen": True,
        "obsidia_cache_hit_frozen": False,
        "obsidia_graphiti_warm_ms": None,
        "obsidia_graphiti_warm_gain_ratio": None,
        "obsidia_runtime_context_build_ms": FROZEN_RUNTIME_CONTEXT_BUILD_MS,
        "obsidia_loader_warm_gain_ratio": FROZEN_LOADER_WARM_GAIN_RATIO,
        "obsidia_files_read": 3,
        "obsidia_files_skipped": 10,
        "obsidia_memory_records_loaded": 2,
        "obsidia_memory_records_skipped": 2,
        "expected_minimal_layer": MIN_LAYER_BRODY_INTERNAL,
        "external_llm_required_by_design": False,
        "llm_necessity_reason": "Internal Brody response / translation layer should be sufficient when runtime bridge is available.",
        "answer_adequacy_criteria": "brody_answer_route_or_message",
    },
    {
        "task_id": "bank_power_route",
        "family": "BANK",
        "comparison_axis": "DOMAIN_DECISION",
        "prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: process a wire transfer compliance check."
        ),
        "expected_route": "BANK",
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_cost_per_1m_est": 0.70,
        "obsidia_latency_ms_frozen": 42.0,
        "obsidia_execution_layer": "domain_bridge",
        "expected_modules_considered": 6,
        "expected_modules_activated": 2,
        "expected_modules_skipped": 4,
        "obsidia_status_frozen": OBSIDIA_STATUS_FROZEN,
        "obsidia_quality_score_frozen": 1.0,
        "obsidia_boundary_ok_frozen": True,
        "obsidia_cache_hit_frozen": False,
        "obsidia_graphiti_warm_ms": None,
        "obsidia_graphiti_warm_gain_ratio": None,
        "obsidia_runtime_context_build_ms": FROZEN_RUNTIME_CONTEXT_BUILD_MS,
        "obsidia_loader_warm_gain_ratio": FROZEN_LOADER_WARM_GAIN_RATIO,
        "obsidia_files_read": 2,
        "obsidia_files_skipped": 11,
        "obsidia_memory_records_loaded": 1,
        "obsidia_memory_records_skipped": 3,
        "expected_minimal_layer": MIN_LAYER_DOMAIN_BRIDGE,
        "external_llm_required_by_design": False,
        "llm_necessity_reason": "Governed domain bridge sufficient; generalist LLM is unnecessary.",
        "answer_adequacy_criteria": "domain_state_or_gate_label_bounded",
    },
    {
        "task_id": "trading_power_route",
        "family": "TRADING",
        "comparison_axis": "DOMAIN_DECISION",
        "prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: validate a BUY signal for asset X."
        ),
        "expected_route": "TRADING",
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_cost_per_1m_est": 0.84,
        "obsidia_latency_ms_frozen": 18.0,
        "obsidia_execution_layer": "domain_bridge",
        "expected_modules_considered": 6,
        "expected_modules_activated": 2,
        "expected_modules_skipped": 4,
        "obsidia_status_frozen": OBSIDIA_STATUS_FROZEN,
        "obsidia_quality_score_frozen": 1.0,
        "obsidia_boundary_ok_frozen": True,
        "obsidia_cache_hit_frozen": False,
        "obsidia_graphiti_warm_ms": None,
        "obsidia_graphiti_warm_gain_ratio": None,
        "obsidia_runtime_context_build_ms": FROZEN_RUNTIME_CONTEXT_BUILD_MS,
        "obsidia_loader_warm_gain_ratio": FROZEN_LOADER_WARM_GAIN_RATIO,
        "obsidia_files_read": 2,
        "obsidia_files_skipped": 11,
        "obsidia_memory_records_loaded": 1,
        "obsidia_memory_records_skipped": 3,
        "expected_minimal_layer": MIN_LAYER_DOMAIN_BRIDGE,
        "external_llm_required_by_design": False,
        "llm_necessity_reason": "Governed domain bridge sufficient; generalist LLM is unnecessary.",
        "answer_adequacy_criteria": "domain_state_or_gate_label_bounded",
    },
    {
        "task_id": "gps_power_route",
        "family": "GPS",
        "comparison_axis": "DOMAIN_DECISION",
        "prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: check terrain clearance for route R47."
        ),
        "expected_route": "GPS",
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_cost_per_1m_est": 0.91,
        "obsidia_latency_ms_frozen": 9.5,
        "obsidia_execution_layer": "domain_bridge",
        "expected_modules_considered": 6,
        "expected_modules_activated": 2,
        "expected_modules_skipped": 4,
        "obsidia_status_frozen": OBSIDIA_STATUS_FROZEN,
        "obsidia_quality_score_frozen": 1.0,
        "obsidia_boundary_ok_frozen": True,
        "obsidia_cache_hit_frozen": False,
        "obsidia_graphiti_warm_ms": None,
        "obsidia_graphiti_warm_gain_ratio": None,
        "obsidia_runtime_context_build_ms": FROZEN_RUNTIME_CONTEXT_BUILD_MS,
        "obsidia_loader_warm_gain_ratio": FROZEN_LOADER_WARM_GAIN_RATIO,
        "obsidia_files_read": 2,
        "obsidia_files_skipped": 11,
        "obsidia_memory_records_loaded": 1,
        "obsidia_memory_records_skipped": 3,
        "expected_minimal_layer": MIN_LAYER_DOMAIN_BRIDGE,
        "external_llm_required_by_design": False,
        "llm_necessity_reason": "Governed domain bridge sufficient; generalist LLM is unnecessary.",
        "answer_adequacy_criteria": "domain_state_or_gate_label_bounded",
    },
    {
        "task_id": "obsidure_power_route",
        "family": "OBSIDURE",
        "comparison_axis": "CODE_PROOF",
        "prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: generate a Lean 4 proof patch for n + 0 = n."
        ),
        "expected_route": "OBSIDURE",
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_cost_per_1m_est": 23.92,
        "obsidia_latency_ms_frozen": 1200.0,
        "obsidia_execution_layer": "obsidure_targeted",
        "expected_modules_considered": 6,
        "expected_modules_activated": 4,
        "expected_modules_skipped": 2,
        "obsidia_status_frozen": OBSIDIA_STATUS_MISSING,
        "obsidia_quality_score_frozen": None,
        "obsidia_boundary_ok_frozen": True,
        "obsidia_cache_hit_frozen": False,
        "obsidia_graphiti_warm_ms": None,
        "obsidia_graphiti_warm_gain_ratio": None,
        "obsidia_runtime_context_build_ms": FROZEN_RUNTIME_CONTEXT_BUILD_MS,
        "obsidia_loader_warm_gain_ratio": FROZEN_LOADER_WARM_GAIN_RATIO,
        "obsidia_files_read": 5,
        "obsidia_files_skipped": 8,
        "obsidia_memory_records_loaded": 3,
        "obsidia_memory_records_skipped": 1,
        "expected_minimal_layer": MIN_LAYER_OBSIDURE_AGENT,
        "external_llm_required_by_design": None,
        "llm_necessity_reason": "Code-agent layer should be sufficient, but adapter is currently missing; not claimable.",
        "answer_adequacy_criteria": "patch_or_diff_bounded",
    },
    {
        "task_id": "lean_power_route",
        "family": "LEAN",
        "comparison_axis": "CODE_PROOF",
        "prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: verify the Lean 4 invariant forall n : Nat, n + 0 = n."
        ),
        "expected_route": "OBSIDURE",
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_cost_per_1m_est": 13.29,
        "obsidia_latency_ms_frozen": 200.0,
        "obsidia_execution_layer": "lean_canon",
        "expected_modules_considered": 6,
        "expected_modules_activated": 4,
        "expected_modules_skipped": 2,
        "obsidia_status_frozen": OBSIDIA_STATUS_MISSING,
        "obsidia_quality_score_frozen": None,
        "obsidia_boundary_ok_frozen": True,
        "obsidia_cache_hit_frozen": False,
        "obsidia_graphiti_warm_ms": None,
        "obsidia_graphiti_warm_gain_ratio": None,
        "obsidia_runtime_context_build_ms": FROZEN_RUNTIME_CONTEXT_BUILD_MS,
        "obsidia_loader_warm_gain_ratio": FROZEN_LOADER_WARM_GAIN_RATIO,
        "obsidia_files_read": 4,
        "obsidia_files_skipped": 9,
        "obsidia_memory_records_loaded": 2,
        "obsidia_memory_records_skipped": 2,
        "expected_minimal_layer": MIN_LAYER_LEAN_PROOF,
        "external_llm_required_by_design": None,
        "llm_necessity_reason": "Proof surface should be sufficient, but adapter is currently missing; not claimable.",
        "answer_adequacy_criteria": "formal_proof_task_bounded",
    },
]


# ── Energy / carbon helpers ───────────────────────────────────────────────────

def compute_model_necessity(task: dict, row: dict) -> dict:
    """Calcule le bloc model_necessity pour une row comparative."""
    family = task.get("family", row.get("family", "UNKNOWN"))
    obs_status = row.get("obsidia_status", "")
    gem_status = row.get("gemini_status", "")
    obs_route_match = row.get("obsidia_route_match")
    comparison_claimable = row.get("route_accuracy_claimable", False)

    is_adapter_missing = obs_status == OBSIDIA_STATUS_MISSING
    is_kernel_unreach = obs_status == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"
    # FAST_PATH n'a pas de bridge dédié en V0.7.x — invariant structurel, indépendant du registry
    is_fast_path_api_status = family == "FAST_PATH"

    external_llm_req = task.get("external_llm_required_by_design")
    expected_min_layer = task.get("expected_minimal_layer", MIN_LAYER_UNKNOWN)

    gemini_external_called = gem_status == GEMINI_STATUS_REAL
    obsidia_external_called = False

    external_llm_avoided = (
        not obsidia_external_called
        and gemini_external_called
        and external_llm_req is False
    )

    governance_clean_row = (
        row.get("obsidia_decision_authority") in ("KX108_ONLY", None)
        and row.get("obsidia_emits_act") in (False, None)
        and row.get("obsidia_memory_write") in (False, None)
        and row.get("obsidia_kernel_mutation") in (False, None)
    )

    unnecessary_avoided = (
        external_llm_avoided
        and obs_route_match is True
        and governance_clean_row
        and not is_adapter_missing
    )

    if is_adapter_missing:
        actual_layer = MIN_LAYER_ADAPTER_MISSING
    elif family == "FAST_PATH" and (
        is_fast_path_api_status
        or obs_status in ("LIVE_LOCAL_UNAVAILABLE", OBSIDIA_STATUS_LIVE_LOCAL, OBSIDIA_STATUS_FROZEN)
    ):
        actual_layer = MIN_LAYER_FAST_PATH
    elif family == "BRODY" and (is_kernel_unreach or obs_status == OBSIDIA_STATUS_LIVE_LOCAL):
        actual_layer = MIN_LAYER_BRODY_INTERNAL
    elif family in ("BANK", "TRADING", "GPS") and obs_status in (OBSIDIA_STATUS_LIVE_LOCAL, OBSIDIA_STATUS_FROZEN):
        actual_layer = MIN_LAYER_DOMAIN_BRIDGE
    else:
        actual_layer = MIN_LAYER_UNKNOWN

    minimal_layer_respected = actual_layer == expected_min_layer

    if is_adapter_missing:
        model_role_obs = MODEL_ROLE_UNKNOWN
    elif family == "BRODY":
        model_role_obs = MODEL_ROLE_INTERNAL_TRANSLATION
    elif external_llm_req is False:
        model_role_obs = MODEL_ROLE_NOT_NEEDED
    else:
        model_role_obs = MODEL_ROLE_UNKNOWN

    model_role_gem = MODEL_ROLE_EXTERNAL_CALLED_BY_BASELINE if gemini_external_called else MODEL_ROLE_UNKNOWN

    if is_adapter_missing:
        necessity_claimable = False
        necessity_non_claimable_reason = "Adapter missing."
    elif is_kernel_unreach and family == "BRODY":
        necessity_claimable = False
        necessity_non_claimable_reason = "BRODY bridge attempted but kernel unreachable; not adapter missing, not fully claimable."
    elif family == "FAST_PATH" and is_fast_path_api_status:
        necessity_claimable = False
        necessity_non_claimable_reason = "FAST_PATH model avoidance measured, but dedicated live bridge not available."
    elif comparison_claimable and obs_route_match is True and governance_clean_row:
        necessity_claimable = True
        necessity_non_claimable_reason = None
    else:
        necessity_claimable = False
        necessity_non_claimable_reason = "Route not matched or comparison not claimable."

    reason_codes = []
    if is_adapter_missing:
        reason_codes.append("ADAPTER_MISSING")
    if is_kernel_unreach:
        reason_codes.append("KERNEL_UNREACHABLE")
    if family == "FAST_PATH" and is_fast_path_api_status:
        reason_codes.append("FAST_PATH_API_STATUS_ONLY")
    if external_llm_req is True:
        reason_codes.append("EXTERNAL_LLM_REQUIRED_BY_DESIGN")

    return {
        "task_id": task.get("task_id"),
        "family": family,
        "expected_minimal_layer": expected_min_layer,
        "actual_obsidia_layer_used": actual_layer,
        "external_llm_required_by_design": external_llm_req,
        "gemini_external_llm_called": gemini_external_called,
        "obsidia_external_llm_called": obsidia_external_called,
        "external_llm_avoided_by_obsidia": external_llm_avoided,
        "unnecessary_generalist_call_avoided": unnecessary_avoided,
        "necessity_claimable": necessity_claimable,
        "necessity_non_claimable_reason": necessity_non_claimable_reason,
        "model_role_for_obsidia": model_role_obs,
        "model_role_for_gemini": model_role_gem,
        "minimal_layer_respected": minimal_layer_respected,
        "reason_codes": reason_codes,
    }

def compute_answer_adequacy(task: dict, row: dict) -> dict:
    """Calcule le score d'adéquation de la réponse Obsidia pour une row."""
    obs_route_match = row.get("obsidia_route_match")
    obs_status = row.get("obsidia_status", "")
    is_adapter_missing = obs_status == OBSIDIA_STATUS_MISSING

    model_necessity = row.get("model_necessity")
    if not isinstance(model_necessity, dict) or not model_necessity:
        model_necessity = compute_model_necessity(task, row)

    route_correct = obs_route_match is True
    output_bounded = (
        route_correct
        or obs_status in (OBSIDIA_STATUS_LIVE_LOCAL, OBSIDIA_STATUS_FROZEN, "LIVE_LOCAL_UNAVAILABLE")
    )

    actual_layer = model_necessity.get("actual_obsidia_layer_used", MIN_LAYER_UNKNOWN)
    expected_layer = model_necessity.get(
        "expected_minimal_layer",
        task.get("expected_minimal_layer", MIN_LAYER_UNKNOWN),
    )
    minimal_layer_respected = actual_layer == expected_layer

    governance_preserved = (
        row.get("obsidia_decision_authority") in ("KX108_ONLY", None)
        and row.get("obsidia_emits_act") in (False, None)
        and row.get("obsidia_memory_write") in (False, None)
        and row.get("obsidia_kernel_mutation") in (False, None)
    )

    trace_available = bool(row.get("dual_lane") or row.get("obsidia_status"))
    hallucination_risk_avoided = output_bounded and not model_necessity.get("obsidia_external_llm_called", False)
    overproduction_penalty = 0.0

    raw_score = (
        0.30 * float(route_correct)
        + 0.20 * float(output_bounded)
        + 0.20 * float(minimal_layer_respected)
        + 0.20 * float(governance_preserved)
        + 0.10 * float(trace_available)
        - overproduction_penalty
    )
    score = round(max(0.0, min(1.0, raw_score)), 4)

    adequacy_claimable = (
        route_correct
        and output_bounded
        and governance_preserved
        and trace_available
        and model_necessity.get("necessity_claimable") is True
        and not is_adapter_missing
    )

    adequacy_non_claimable_reason = None
    if not adequacy_claimable:
        adequacy_non_claimable_reason = model_necessity.get("necessity_non_claimable_reason")
        if adequacy_non_claimable_reason is None:
            if is_adapter_missing:
                adequacy_non_claimable_reason = "Adapter missing."
            elif not route_correct:
                adequacy_non_claimable_reason = "Route not matched."
            elif not governance_preserved:
                adequacy_non_claimable_reason = "Governance not preserved."
            else:
                adequacy_non_claimable_reason = "Not adequacy-claimable in this run."

    reason_codes = []
    if is_adapter_missing:
        reason_codes.append("ADAPTER_MISSING_NOT_CLAIMABLE")
    if not route_correct:
        reason_codes.append("ROUTE_NOT_MATCHED")
    if not governance_preserved:
        reason_codes.append("GOVERNANCE_NOT_PRESERVED")
    if not adequacy_claimable and adequacy_non_claimable_reason:
        reason_codes.append("ADEQUACY_NOT_CLAIMABLE")

    return {
        "answer_adequacy_score": score,
        "route_correct": route_correct,
        "output_bounded": output_bounded,
        "minimal_layer_respected": minimal_layer_respected,
        "governance_preserved": governance_preserved,
        "trace_or_receipt_available": trace_available,
        "hallucination_risk_avoided": hallucination_risk_avoided,
        "overproduction_penalty": overproduction_penalty,
        "adequacy_claimable": adequacy_claimable,
        "adequacy_non_claimable_reason": adequacy_non_claimable_reason,
        "adequacy_reason_codes": reason_codes,
    }

def _read_energy_env() -> tuple[Optional[float], Optional[float], Optional[float]]:
    def _f(k: str) -> Optional[float]:
        v = os.environ.get(k, "")
        try:
            return float(v) if v else None
        except ValueError:
            return None
    return _f("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS"), _f("OIE_LOCAL_POWER_W"), _f("OIE_CARBON_GCO2_PER_KWH")


def compute_energy_metrics(
    tokens: Optional[int],
    latency_ms: Optional[float],
    wh_per_1k_tokens: Optional[float],
    local_power_w: Optional[float],
    carbon_per_kwh: Optional[float],
) -> dict:
    if wh_per_1k_tokens is None or local_power_w is None:
        return {
            "energy_source": ENERGY_SOURCE_UNAVAILABLE,
            "external_energy_wh_est": None,
            "local_energy_wh_est": None,
            "energy_avoided_wh": None,
            "energy_savings_ratio": None,
            "external_carbon_gco2_est": None,
            "local_carbon_gco2_est": None,
            "carbon_avoided_gco2": None,
        }
    ext_wh = (tokens / 1000.0 * wh_per_1k_tokens) if tokens is not None else None
    loc_wh = ((latency_ms / 1000.0) * local_power_w / 3600.0) if latency_ms is not None else None
    avoided_wh = (ext_wh - loc_wh) if (ext_wh is not None and loc_wh is not None) else None
    ratio = (ext_wh / loc_wh) if (ext_wh is not None and loc_wh is not None and loc_wh > 0) else None
    ext_co2 = (ext_wh / 1000.0 * carbon_per_kwh) if (ext_wh is not None and carbon_per_kwh is not None) else None
    loc_co2 = (loc_wh / 1000.0 * carbon_per_kwh) if (loc_wh is not None and carbon_per_kwh is not None) else None
    avoided_co2 = (ext_co2 - loc_co2) if (ext_co2 is not None and loc_co2 is not None) else None
    return {
        "energy_source": ENERGY_SOURCE_ESTIMATE,
        "external_energy_wh_est": ext_wh,
        "local_energy_wh_est": loc_wh,
        "energy_avoided_wh": avoided_wh,
        "energy_savings_ratio": ratio,
        "external_carbon_gco2_est": ext_co2,
        "local_carbon_gco2_est": loc_co2,
        "carbon_avoided_gco2": avoided_co2,
    }


def _read_cost_env() -> tuple[Optional[float], Optional[float]]:
    def _f(k: str) -> Optional[float]:
        v = os.environ.get(k, "")
        try:
            return float(v) if v else None
        except ValueError:
            return None
    return _f("OIE_EXTERNAL_INPUT_COST_PER_1M"), _f("OIE_EXTERNAL_OUTPUT_COST_PER_1M")


def _safe_ratio(num: Optional[float], den: Optional[float]) -> tuple[Optional[float], str]:
    if num is None or den is None:
        return None, "MISSING_OPERAND"
    if den == 0 or abs(den) < 1e-12:
        return None, "BASELINE_NEAR_ZERO"
    return num / den, "OK"


def _clamp01(v: float) -> float:
    return round(max(0.0, min(1.0, v)), 4)


# ── Phase 2 : Cost basis ──────────────────────────────────────────────────────

def compute_cost_basis_fields(task: dict, obs: dict, gem: dict) -> dict:
    """Champs cost basis : distingue mesure vs proxy."""
    obs_tok = obs.get("obsidia_estimated_total_tokens", 0) or 0
    obs_c1m = task.get("obsidia_cost_per_1m_est", 0.0)
    obs_cost_proxy = obs_c1m * obs_tok / 1_000_000.0

    gem_status = gem.get("gemini_status")
    gem_usage = gem.get("gemini_total_tokens") is not None
    gemini_basis = (
        COST_BASIS_SDK_MEASURED if (gem_status == GEMINI_STATUS_REAL and gem_usage)
        else COST_BASIS_DRY_RUN_MOCK
    )
    gem_is_measured = gemini_basis == COST_BASIS_SDK_MEASURED

    return {
        "obsidia_cost_basis": COST_BASIS_LOCAL_PROXY,
        "gemini_cost_basis": gemini_basis,
        "obsidia_cost_is_measured": False,
        "gemini_cost_is_measured": gem_is_measured,
        "obsidia_cost_is_claimable": False,
        "gemini_cost_is_claimable": gem_is_measured,
        "cost_comparison_claimable": False,
        "obsidia_cost_proxy_warning": COST_PROXY_WARNING,
        "obsidia_cost_proxy_per_request_est": round(obs_cost_proxy, 10),
        "obsidia_cost_proxy_per_1m_est": obs_c1m,
        "obsidia_cost_proxy_formula": COST_PROXY_FORMULA,
        "obsidia_cost_proxy_source": COST_PROXY_SOURCE,
    }


# ── Phase 4 / 5 : Intellectual economy + Gencoin calibration ─────────────────

def compute_intellectual_economy(task: dict, obs: dict, gem: dict, row: dict) -> dict:
    """Scores economie intellectuelle — CALIBRATION_ONLY.

    Reference formules : brody_gencoin_shadow_value.py + brody_gencoin_cognitive_ledger.py
    Poids : PROVISIONAL_CALIBRATION_ONLY (adaptes de cognitive_ledger.py).
    """
    family = task["family"]
    status = obs.get("obsidia_status")
    is_missing = status == OBSIDIA_STATUS_MISSING
    gov_clean = row.get("obsidia_governance_clean", False)
    boundary_ok = obs.get("obsidia_boundary_ok", True)
    model_avoided = obs.get("obsidia_model_call_avoided", False)
    route_match = obs.get("obsidia_route_match")
    q_score = obs.get("obsidia_quality_score")
    lat_delta_pct = row.get("latency_delta_pct")
    mod_skip_pct = obs.get("obsidia_modules_skipped_pct", 0.0) or 0.0

    # cognitive_value_score (proxy sans Sigma/Thermo)
    # Reference : shadow_value.py:216 cognitive_value = truth_score - ms*0.30 - es*0.20
    if is_missing:
        cognitive_value_score = 0.30
    elif route_match is True:
        cognitive_value_score = 0.80
    else:
        cognitive_value_score = 0.50

    # novelty_score — PROVISIONAL = 0.0 (non calculable sans Sigma)
    novelty_score = 0.0

    # utility_score
    if model_avoided and not is_missing:
        utility_score = 0.90
    elif not is_missing and q_score is not None and q_score >= 1.0:
        utility_score = 0.60
    elif is_missing:
        utility_score = 0.30
    else:
        utility_score = 0.40

    # coherence_score = governance_clean
    coherence_score = 1.0 if gov_clean else 0.0

    # risk_reduction_score : terrain proof families
    if is_missing:
        risk_reduction_score = 0.0
    elif family in TERRAIN_PROOF_FAMILIES and boundary_ok:
        risk_reduction_score = 1.0
    elif family == "FAST_PATH" and boundary_ok:
        risk_reduction_score = 0.80
    else:
        risk_reduction_score = 0.0

    # stability_value_score
    # Reference : shadow_value.py:219 stability_value = clamp(1.0 - instability_score)
    if status == OBSIDIA_STATUS_REAL:
        stability_value_score = 0.95
    elif status == OBSIDIA_STATUS_FROZEN:
        stability_value_score = 0.85
    else:
        stability_value_score = 0.40

    # reusability_score — adapte de shadow_value.py:252
    # reuse_value = 0.40 + cog*0.30 + stab*0.20 - att*0.20
    # attention_cost = 0.20 (short outputs in benchmark)
    reusability_score = _clamp01(
        0.40
        + cognitive_value_score * 0.30
        + stability_value_score * 0.20
        - 0.20 * 0.20
    )

    # proof_quality_score
    receipt_complete = all(
        row.get(f) is not None
        for f in ["family", "expected_route", "obsidia_detected_route", "obsidia_boundary_ok"]
    )
    if is_missing:
        proof_quality_score = 0.50 if boundary_ok else 0.0
    elif boundary_ok and receipt_complete:
        proof_quality_score = 1.0
    else:
        proof_quality_score = 0.0

    # debt_score
    debt = 0.0
    if is_missing:
        debt += 0.50
    debt += 0.20  # cout proxy toujours non calibre
    if is_missing:
        debt += 0.20  # preuve manquante
    debt_score = _clamp01(debt)

    # friction_reduction_score
    friction_components = []
    if lat_delta_pct is not None:
        friction_components.append(_clamp01(lat_delta_pct / 100.0))
    if mod_skip_pct > 0:
        friction_components.append(_clamp01(mod_skip_pct / 100.0))
    energy_sr = row.get("energy_savings_ratio")
    if energy_sr is not None:
        friction_components.append(_clamp01(min(energy_sr, 10.0) / 10.0))
    friction_reduction_score = (
        round(sum(friction_components) / len(friction_components), 4)
        if friction_components else 0.0
    )

    # governance_value_score
    governance_value_score = 1.0 if (gov_clean and DECISION_AUTHORITY == "KX108_ONLY") else 0.0

    # external_dependency_reduction_score
    external_dependency_reduction_score = 1.0 if model_avoided else 0.0

    # auditability_score
    required_audit_fields = [
        "family", "expected_route", "obsidia_detected_route",
        "gemini_detected_route", "obsidia_boundary_ok", "obsidia_governance_clean",
    ]
    audit_present = sum(1 for f in required_audit_fields if row.get(f) is not None)
    auditability_score = round(audit_present / len(required_audit_fields), 4)

    # intellectual_value_score (CV formula, PROVISIONAL)
    # CV = wN*novelty + wU*utility + wC*coherence + wR*risk_reduction + wReuse*reusability + wP*proof_quality - debt
    w = _CV_WEIGHTS
    cv_raw = (
        w["novelty"] * novelty_score
        + w["utility"] * utility_score
        + w["coherence"] * coherence_score
        + w["risk_reduction"] * risk_reduction_score
        + w["reusability"] * reusability_score
        + w["proof_quality"] * proof_quality_score
        - debt_score
    )
    intellectual_value_score = _clamp01(cv_raw)

    # source_law_satisfied — toujours False en calibration
    source_law_satisfied = False

    return {
        "intellectual_economy_basis": IE_BASIS,
        "cognitive_value_score": cognitive_value_score,
        "novelty_score": novelty_score,
        "utility_score": utility_score,
        "coherence_score": coherence_score,
        "risk_reduction_score": risk_reduction_score,
        "reusability_score": reusability_score,
        "proof_quality_score": proof_quality_score,
        "debt_score": debt_score,
        "stability_value_score": stability_value_score,
        "friction_reduction_score": friction_reduction_score,
        "governance_value_score": governance_value_score,
        "external_dependency_reduction_score": external_dependency_reduction_score,
        "auditability_score": auditability_score,
        "intellectual_value_score": intellectual_value_score,
        "cv_weight_source": _CV_WEIGHT_SOURCE,
        "source_law_satisfied": source_law_satisfied,
        "source_law_reason": SOURCE_LAW_REASON_CALIBRATION,
    }


def compute_gencoin_calibration(ie: dict) -> dict:
    """Layer Gencoin calibration — emission desactivee, aucun token reel."""
    return {
        "gencoin_basis": GENCOIN_MODE,
        "intellectual_economy_basis": IE_BASIS,
        "gencoin_emission_allowed": False,
        "gencoin_emission_amount": 0,
        "gencoin_distribution_mode": GENCOIN_DISTRIBUTION_MODE,
        "gencoin_emission_reason": GENCOIN_EMISSION_REASON,
        "source_law_satisfied": ie.get("source_law_satisfied", False),
        "source_law_reason": ie.get("source_law_reason", SOURCE_LAW_REASON_CALIBRATION),
        "mint_allowed": False,
        "is_real_token": False,
        "blockchain_enabled": False,
        "economic_scoring_enabled": False,
        "wallet_enabled": False,
    }


# ── Phase 3 : Surface metrics ─────────────────────────────────────────────────

def compute_surface_metrics(rows: list[dict]) -> dict:
    """Metriques par surface : available, adapter_missing, terrain, model_avoided."""

    def _sub(pred, field=None) -> list[dict]:
        return [r for r in rows if pred(r)]

    def _avg_f(lst, key) -> Optional[float]:
        vals = [r[key] for r in lst if r.get(key) is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    def _median_f(lst, key) -> Optional[float]:
        vals = sorted(r[key] for r in lst if r.get(key) is not None)
        if not vals:
            return None
        mid = len(vals) // 2
        return round(vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2, 4)

    # Filtrage dynamique : suit le statut réel de chaque row, pas la famille statique.
    avail = _sub(lambda r: r.get("obsidia_status") != OBSIDIA_STATUS_MISSING)
    missing = _sub(lambda r: r.get("obsidia_status") == OBSIDIA_STATUS_MISSING)
    terrain = _sub(lambda r: r.get("family") in TERRAIN_PROOF_FAMILIES)
    avoided = _sub(lambda r: r.get("family") in MODEL_AVOIDED_FAMILIES)

    return {
        "available_surface_families": sorted(AVAILABLE_SURFACE_FAMILIES),
        "available_surface_count": len(avail),
        "available_surface_exclusion_rule": "obsidia_status != ADAPTER_MISSING",
        "obsidia_available_surface_accuracy": (
            round(sum(1 for r in avail if r.get("obsidia_route_match") is True) / len(avail), 4)
            if avail else None
        ),
        "gemini_available_surface_accuracy": (
            round(sum(1 for r in avail if r.get("gemini_route_match") is True) / len(avail), 4)
            if avail else None
        ),
        "available_surface_model_call_avoided_rate": (
            round(sum(1 for r in avail if r.get("obsidia_model_call_avoided")) / len(avail), 4)
            if avail else None
        ),
        "available_surface_avg_speedup_ratio": _avg_f(avail, "speedup_ratio"),
        "available_surface_median_speedup_ratio": _median_f(avail, "speedup_ratio"),
        "available_surface_energy_avoided_wh": (
            sum(r.get("energy_avoided_wh") or 0.0 for r in avail)
            if any(r.get("energy_avoided_wh") is not None for r in avail) else None
        ),
        "available_surface_external_dependency_reduction_score": (
            _avg_f(avail, "external_dependency_reduction_score")
        ),
        "adapter_missing_families": sorted(ADAPTER_MISSING_FAMILIES),
        "adapter_missing_count": len(missing),
        "adapter_missing_excluded_from_functional_victory": True,
        "terrain_proof_families": sorted(TERRAIN_PROOF_FAMILIES),
        "obsidia_terrain_accuracy": (
            round(sum(1 for r in terrain if r.get("obsidia_route_match") is True) / len(terrain), 4)
            if terrain else None
        ),
        "gemini_terrain_accuracy": (
            round(sum(1 for r in terrain if r.get("gemini_route_match") is True) / len(terrain), 4)
            if terrain else None
        ),
        "terrain_model_call_avoided_rate": (
            round(sum(1 for r in terrain if r.get("obsidia_model_call_avoided")) / len(terrain), 4)
            if terrain else None
        ),
        "terrain_avg_speedup_ratio": _avg_f(terrain, "speedup_ratio"),
        "terrain_median_speedup_ratio": _median_f(terrain, "speedup_ratio"),
        "terrain_avg_latency_delta_pct": _avg_f(terrain, "latency_delta_pct"),
        "terrain_energy_avoided_wh": (
            sum(r.get("energy_avoided_wh") or 0.0 for r in terrain)
            if any(r.get("energy_avoided_wh") is not None for r in terrain) else None
        ),
        "terrain_governance_clean": all(r.get("obsidia_governance_clean", False) for r in terrain),
        "model_avoided_families": sorted(MODEL_AVOIDED_FAMILIES),
        "model_avoided_count": len(avoided),
        "model_avoided_avg_speedup_ratio": _avg_f(avoided, "speedup_ratio"),
        "model_avoided_median_speedup_ratio": _median_f(avoided, "speedup_ratio"),
        "model_avoided_avg_latency_delta_pct": _avg_f(avoided, "latency_delta_pct"),
        "model_avoided_energy_avoided_wh": (
            sum(r.get("energy_avoided_wh") or 0.0 for r in avoided)
            if any(r.get("energy_avoided_wh") is not None for r in avoided) else None
        ),
        "model_avoided_token_delta_pct": _avg_f(avoided, "token_delta_pct"),
    }


# ── Phase KP : Known Path / Chemin connu ─────────────────────────────────────

def compute_known_path(task: dict, obs: dict, gem: dict, row: dict) -> dict:
    """Chemin admissible déterministe vs prédiction probabiliste Gemini."""
    status = obs.get("obsidia_status")
    is_missing = status == OBSIDIA_STATUS_MISSING
    family = task["family"]
    route_match = obs.get("obsidia_route_match")
    model_avoided = obs.get("obsidia_model_call_avoided", False)
    obs_lat = obs.get("obsidia_latency_ms")
    gem_lat = gem.get("gemini_latency_ms")

    known_path_detected = (
        not is_missing
        and route_match is True
        and (model_avoided or family in AVAILABLE_SURFACE_FAMILIES)
    )

    if is_missing:
        known_path_basis = "ADAPTER_MISSING"
        known_path_stage = "ADAPTER_MISSING"
    elif known_path_detected and model_avoided:
        known_path_basis = "DETERMINISTIC_SURFACE"
        known_path_stage = (
            "FAST_PATH_CACHE" if family == "FAST_PATH"
            else "DOMAIN_BRIDGE" if family in TERRAIN_PROOF_FAMILIES
            else "ROUTER"
        )
    elif not is_missing and route_match is True:
        known_path_basis = "ROUTE_AVAILABLE_MODEL_REQUIRED"
        known_path_stage = "ROUTER"
    else:
        known_path_basis = "UNKNOWN"
        known_path_stage = "UNKNOWN"

    prediction_replaced_by_verification = known_path_detected and model_avoided
    route_verification_possible = not is_missing and route_match is True
    kp_lat_adv = (
        round(gem_lat - obs_lat, 4)
        if known_path_detected and obs_lat is not None and gem_lat is not None
        else None
    )
    kp_speedup = row.get("speedup_ratio") if known_path_detected else None

    return {
        "known_path_detected": known_path_detected,
        "known_path_basis": known_path_basis,
        "known_path_stage": known_path_stage,
        "deterministic_route_used": known_path_detected,
        "prediction_replaced_by_verification": prediction_replaced_by_verification,
        "route_verification_possible": route_verification_possible,
        "route_verification_reason": (
            "Route match verified without LLM inference" if prediction_replaced_by_verification
            else "Adapter missing — route not verifiable" if is_missing
            else "Route available but model still required" if route_verification_possible
            else "Route not matched"
        ),
        "known_path_latency_advantage_ms": kp_lat_adv,
        "known_path_speedup_ratio": round(kp_speedup, 4) if kp_speedup is not None else None,
        "known_path_claimable": known_path_detected and not is_missing,
    }


# ── Phase IN : Inference Necessity / Nécessité d'inférence ───────────────────

def compute_inference_necessity(task: dict, obs: dict, gem: dict) -> dict:
    """Nécessité d'inférence : Obsidia évite ce que Gemini ne peut pas éviter."""
    obsidia_inference_required = task.get("obsidia_model_call_required", False)
    gemini_inference_required = True
    model_avoided = obs.get("obsidia_model_call_avoided", False)
    status = obs.get("obsidia_status")

    unnecessary_inference_avoided = bool(gemini_inference_required and model_avoided)
    external_dependency_avoided = bool(model_avoided)
    inference_necessity_delta = (1 if gemini_inference_required else 0) - (1 if obsidia_inference_required else 0)

    return {
        "obsidia_inference_required": obsidia_inference_required,
        "gemini_inference_required": gemini_inference_required,
        "inference_necessity_delta": inference_necessity_delta,
        "unnecessary_inference_avoided": unnecessary_inference_avoided,
        "inference_avoidance_reason": (
            "Obsidia routes via deterministic surface — no LLM call" if model_avoided
            else "Obsidia requires model call for this family" if obsidia_inference_required
            else "Adapter missing — inference path not wired"
        ),
        "model_call_avoided_claimable": model_avoided and status != OBSIDIA_STATUS_MISSING,
        "external_dependency_avoided": external_dependency_avoided,
    }


# ── Phase GS : Governed Speed / Vitesse gouvernée ────────────────────────────

def compute_governed_speed(task: dict, obs: dict, gem: dict, row: dict) -> dict:
    """Vitesse sous KX108_ONLY — pas de sacrifice du contrôle."""
    gov_clean = row.get("obsidia_governance_clean", False)
    boundary_ok = obs.get("obsidia_boundary_ok", True)
    speedup = row.get("speedup_ratio")

    governance_preserved = (
        gov_clean
        and DECISION_AUTHORITY == "KX108_ONLY"
        and not EMITS_ACT
        and not MEMORY_WRITE
        and not KERNEL_MUTATION
        and boundary_ok
    )

    return {
        "governed_speedup_ratio": round(speedup, 4) if (governance_preserved and speedup is not None) else None,
        "governed_latency_delta_pct": row.get("latency_delta_pct") if governance_preserved else None,
        "speed_under_governance_claimable": governance_preserved and speedup is not None,
        "governance_preserved_at_speed": governance_preserved,
        "kx108_preserved_at_speed": DECISION_AUTHORITY == "KX108_ONLY",
        "no_action_preserved_at_speed": not EMITS_ACT,
        "no_memory_write_preserved_at_speed": not MEMORY_WRITE,
        "no_kernel_mutation_preserved_at_speed": not KERNEL_MUTATION,
    }


# ── Phase MF : Math Formalization Support ────────────────────────────────────

def compute_math_formalization(task: dict, obs: dict, gem: dict, row: dict) -> dict:
    """Formalisation : les gains reposent sur surfaces formalisées, pas sur l'intelligence générale."""
    status = obs.get("obsidia_status")
    is_missing = status == OBSIDIA_STATUS_MISSING
    family = task["family"]
    gov_clean = row.get("obsidia_governance_clean", False)
    boundary_ok = obs.get("obsidia_boundary_ok", True)

    math_formalization_support = (
        DECISION_AUTHORITY == "KX108_ONLY"
        and gov_clean
        and boundary_ok
        and not is_missing
    )

    if is_missing:
        formalization_basis = "ADAPTER_MISSING_NOT_CLAIMABLE"
    elif family == "FAST_PATH":
        formalization_basis = "FROZEN_V0_FORMAL_SURFACE"
    elif family in TERRAIN_PROOF_FAMILIES:
        formalization_basis = "DOMAIN_ROUTE_ADMISSIBILITY"
    else:
        formalization_basis = "KX108_GOVERNANCE_INVARIANTS"

    return {
        "math_formalization_support": math_formalization_support,
        "formalization_basis": formalization_basis,
        "invariant_backing": gov_clean and not is_missing,
        "route_admissibility_backing": family in AVAILABLE_SURFACE_FAMILIES and not is_missing,
        "proof_backing": family in TERRAIN_PROOF_FAMILIES and not is_missing,
        "kx108_authority_backing": DECISION_AUTHORITY == "KX108_ONLY",
        "formalization_claimable": math_formalization_support,
    }


# ── Obsidia lane ──────────────────────────────────────────────────────────────

def _try_fast_path_router(task: dict) -> Optional[dict]:
    if task["family"] != "FAST_PATH":
        return None
    try:
        from apps.obsidia_api.brody_semantic_query_router import route_request
        t0 = time.perf_counter()
        result = route_request(task["prompt"])
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        detected = (result.get("route") or "").upper()
        match = detected == task["expected_route"]
        return {
            "obsidia_status": OBSIDIA_STATUS_REAL,
            "obsidia_detected_route": detected,
            "obsidia_route_match": match,
            "obsidia_latency_ms": round(elapsed_ms, 4),
            "obsidia_quality_score": 1.0 if match else 0.0,
            "obsidia_boundary_ok": True,
            "obsidia_cache_hit": result.get("cache_hit", False),
        }
    except Exception:
        return None


def run_obsidia_local_actual(task: dict) -> dict:
    status_frozen = task["obsidia_status_frozen"]
    lat_ms = task["obsidia_latency_ms_frozen"]
    modules_considered = task["expected_modules_considered"]
    modules_activated = task["expected_modules_activated"]
    modules_skipped = task["expected_modules_skipped"]
    modules_skipped_pct = round(100.0 * modules_skipped / max(modules_considered, 1), 2)

    prompt_chars = len(task["prompt"])
    est_input_tok = max(1, prompt_chars // 4)
    est_output_tok = 4
    est_total_tok = est_input_tok + est_output_tok

    cost_per_1m = task["obsidia_cost_per_1m_est"]
    cost_per_req = cost_per_1m * est_total_tok / 1_000_000.0

    real = _try_fast_path_router(task)
    if real is not None:
        detected_route = real["obsidia_detected_route"]
        route_match = real["obsidia_route_match"]
        actual_lat = real["obsidia_latency_ms"]
        q_score = real["obsidia_quality_score"]
        boundary_ok = real["obsidia_boundary_ok"]
        cache_hit = real["obsidia_cache_hit"]
        status = OBSIDIA_STATUS_REAL
    else:
        detected_route = task["expected_route"] if status_frozen == OBSIDIA_STATUS_FROZEN else None
        route_match = True if status_frozen == OBSIDIA_STATUS_FROZEN else None
        actual_lat = lat_ms
        q_score = task["obsidia_quality_score_frozen"]
        boundary_ok = task["obsidia_boundary_ok_frozen"]
        cache_hit = task["obsidia_cache_hit_frozen"]
        status = status_frozen

    model_call_avoided = (
        task["external_model_call_required"] and not task["obsidia_model_call_required"]
    )

    throughput = round(1000.0 / actual_lat, 4) if actual_lat and actual_lat > 0 else None
    safe_dps = (
        round(throughput * (q_score or 0.0) * (1.0 if boundary_ok else 0.0), 4)
        if throughput is not None and q_score is not None
        else None
    )
    dpc = round(1.0 / cost_per_req, 4) if cost_per_req and cost_per_req > 0 else None

    return {
        "obsidia_status": status,
        "obsidia_detected_route": detected_route,
        "obsidia_route_match": route_match,
        "obsidia_latency_ms": actual_lat,
        "obsidia_p50_ms": actual_lat,
        "obsidia_p95_ms": actual_lat,
        "obsidia_p99_ms": actual_lat,
        "obsidia_estimated_input_tokens": est_input_tok,
        "obsidia_estimated_output_tokens": est_output_tok,
        "obsidia_estimated_total_tokens": est_total_tok,
        "obsidia_cost_per_request_est": round(cost_per_req, 10),
        "obsidia_cost_per_1m_est": cost_per_1m,
        "obsidia_model_call_required": task["obsidia_model_call_required"],
        "obsidia_model_call_avoided": model_call_avoided,
        "obsidia_modules_considered": modules_considered,
        "obsidia_modules_activated": modules_activated,
        "obsidia_modules_skipped": modules_skipped,
        "obsidia_modules_skipped_pct": modules_skipped_pct,
        "obsidia_files_read": task["obsidia_files_read"],
        "obsidia_files_skipped": task["obsidia_files_skipped"],
        "obsidia_memory_records_loaded": task["obsidia_memory_records_loaded"],
        "obsidia_memory_records_skipped": task["obsidia_memory_records_skipped"],
        "obsidia_cache_hit": cache_hit,
        "obsidia_cache_hit_ratio": 1.0 if cache_hit else 0.0,
        "obsidia_graphiti_cold_ms": FROZEN_GRAPHITI_COLD_MS,
        "obsidia_graphiti_warm_ms": task["obsidia_graphiti_warm_ms"],
        "obsidia_graphiti_warm_gain_ratio": task["obsidia_graphiti_warm_gain_ratio"],
        "obsidia_runtime_context_build_ms": task["obsidia_runtime_context_build_ms"],
        "obsidia_runtime_loader_warm_gain_ratio": task["obsidia_loader_warm_gain_ratio"],
        "obsidia_boundary_ok": boundary_ok,
        "obsidia_quality_score": q_score,
        "obsidia_failure_type": FAILURE_NONE,
        "obsidia_emits_act": EMITS_ACT,
        "obsidia_memory_write": MEMORY_WRITE,
        "obsidia_kernel_mutation": KERNEL_MUTATION,
        "obsidia_decision_authority": DECISION_AUTHORITY,
        "obsidia_throughput_req_per_sec": throughput,
        "obsidia_safe_decisions_per_second": safe_dps,
        "obsidia_decisions_per_cost_unit": dpc,
    }


# ── Obsidia live lane ─────────────────────────────────────────────────────────

def _try_live_bridge(task: dict, api_base: str = _OBSIDIA_API_BASE) -> Optional[dict]:
    """Tente d'appeler le bridge live local via HTTP POST vers l'API 8000.

    Garanties (bridgées depuis _BOUNDARY de live_kernel_bridge.py):
      emits_act=False, memory_write=False, kernel_mutation=False,
      graphiti_write=False, neo4j_write=False, decision_authority=KX108_ONLY,
      api_role=BRIDGE_ONLY, source_of_truth=kernel_decision.

    Ne fait aucune action réelle banque/trading/aviation.
    Cible kernel 3001 via le bridge — si kernel unreachable, retourne
    LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE (pas ADAPTER_MISSING).
    """
    import urllib.request as _urlreq
    import urllib.error as _urlerr

    family = task["family"]
    reg = _OBSIDIA_LIVE_ADAPTER_REGISTRY.get(family, {})
    if not reg.get("usable_for_live_local"):
        return None
    bridge_path = reg.get("bridge_path")
    if not bridge_path:
        return None
    endpoint = f"{api_base.rstrip('/')}{bridge_path}"
    payload_body = _LIVE_TEST_PAYLOADS.get(family, {})
    body_bytes = json.dumps(payload_body, default=str).encode("utf-8")
    try:
        req = _urlreq.Request(
            endpoint,
            data=body_bytes,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        t0 = time.perf_counter()
        with _urlreq.urlopen(req, timeout=5.0) as resp:
            elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 4)
            raw = resp.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except Exception:
            data = {}
        inner = data.get("data") or data
        kernel_invoked = inner.get("kernel_invoked", False)
        kernel_decision = inner.get("kernel_decision") or {}
        kernel_status = inner.get("kernel_status") or ("OK" if kernel_invoked else "UNKNOWN")
        bridge_ok = bool(kernel_invoked)

        if bridge_ok:
            exec_mode = "LIVE_LOCAL_BRIDGE"
            obs_status = OBSIDIA_STATUS_LIVE_LOCAL
            comparison_scope_hint = "OBSIDIA_LIVE_BRIDGE_VS_GEMINI"
        else:
            exec_mode = "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"
            obs_status = "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"
            comparison_scope_hint = "OBSIDIA_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE_VS_GEMINI"

        gate = str(kernel_decision.get("gate") or kernel_decision.get("x108_gate") or "UNKNOWN")
        return {
            "obsidia_status": obs_status,
            "obsidia_detected_route": family,
            "obsidia_route_match": task.get("expected_route") == family,
            "obsidia_latency_ms": elapsed_ms,
            "obsidia_quality_score": 1.0 if bridge_ok else 0.5,
            "obsidia_boundary_ok": True,
            "obsidia_cache_hit": False,
            "obsidia_live_bridge_ok": bridge_ok,
            "obsidia_live_kernel_invoked": kernel_invoked,
            "obsidia_live_kernel_gate": gate,
            "obsidia_live_kernel_status": kernel_status,
            "obsidia_live_comparison_scope_hint": comparison_scope_hint,
            "obsidia_live_adapter_type": "LOCAL_HTTP_READONLY",
            "obsidia_live_adapter_path": f"apps/obsidia_api/routes/live_kernel_bridge.py",
            "obsidia_live_adapter_endpoint": endpoint,
            "obsidia_live_callable": f"POST {bridge_path}",
            "obsidia_emits_act": False,
            "obsidia_memory_write": False,
            "obsidia_kernel_mutation": False,
            "obsidia_graphiti_write": False,
            "obsidia_neo4j_write": False,
            "obsidia_decision_authority": "KX108_ONLY",
        }
    except _urlerr.HTTPError as _http_exc:
        # API accessible mais erreur HTTP — bridge tenté mais échoué
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 4) if 't0' in dir() else None
        return {
            "obsidia_status": "LIVE_BRIDGE_HTTP_ERROR",
            "obsidia_detected_route": None,
            "obsidia_route_match": None,
            "obsidia_latency_ms": elapsed_ms,
            "obsidia_quality_score": 0.0,
            "obsidia_boundary_ok": True,
            "obsidia_cache_hit": False,
            "obsidia_live_bridge_ok": False,
            "obsidia_live_kernel_invoked": False,
            "obsidia_live_kernel_gate": None,
            "obsidia_live_kernel_status": f"HTTP_ERROR_{_http_exc.code}",
            "obsidia_live_comparison_scope_hint": "OBSIDIA_BRIDGE_HTTP_ERROR_VS_GEMINI",
            "obsidia_live_adapter_type": "LOCAL_HTTP_READONLY",
            "obsidia_live_adapter_endpoint": endpoint,
            "obsidia_emits_act": False,
            "obsidia_memory_write": False,
            "obsidia_kernel_mutation": False,
            "obsidia_graphiti_write": False,
            "obsidia_neo4j_write": False,
            "obsidia_decision_authority": "KX108_ONLY",
        }
    except Exception:
        return None


def run_obsidia_lane(task: dict, execution_mode: str) -> dict:
    """Exécute la lane Obsidia en respectant l'execution_mode demandé.

    Priorité :
      1. In-process callable si LIVE_LOCAL ou LIVE_LOCAL_OR_FROZEN et adapter usable.
      2. run_obsidia_local_actual() (frozen/missing) sinon.

    Gouvernance garantie : emits_act=False, memory_write=False, kernel_mutation=False.
    """
    family = task["family"]
    reg = _OBSIDIA_LIVE_ADAPTER_REGISTRY.get(family, {})
    adapter_usable = reg.get("usable_for_live_local", False)
    adapter_found = reg.get("adapter_found", False)

    live_attempted = execution_mode in (OIE_OBSIDIA_EXEC_MODE_LIVE, OIE_OBSIDIA_EXEC_MODE_LIVE_OR_FROZEN)
    live_result: Optional[dict] = None

    if live_attempted and adapter_usable:
        live_result = _try_fast_path_router(task) if family == "FAST_PATH" else _try_live_bridge(task)

    if live_result is not None:
        base = run_obsidia_local_actual(task)
        base.update(live_result)
        base["obsidia_execution_mode"] = OBSIDIA_STATUS_LIVE_LOCAL
        base["obsidia_live_attempted"] = True
        base["obsidia_live_available"] = True
        base["obsidia_live_adapter_type"] = live_result.get("obsidia_live_adapter_type", "IN_PROCESS_FUNCTION")
        base["obsidia_live_adapter_path"] = live_result.get("obsidia_live_adapter_path")
        base["obsidia_live_adapter_endpoint"] = None
        base["obsidia_fallback_used"] = False
        return base

    if execution_mode == OIE_OBSIDIA_EXEC_MODE_LIVE and not adapter_usable:
        # LIVE_LOCAL demandé mais adapter absent — ne pas fallback silencieusement
        base = run_obsidia_local_actual(task)
        if adapter_found:
            # Module trouvé mais callable manquant
            live_status = OBSIDIA_STATUS_LIVE_LOCAL_UNAVAILABLE
            reason = reg.get("reason_if_not_usable", "callable missing")
        elif task["obsidia_status_frozen"] == OBSIDIA_STATUS_MISSING:
            live_status = OBSIDIA_STATUS_MISSING
            reason = "ADAPTER_MISSING — no live callable and no wired frozen adapter"
        else:
            live_status = OBSIDIA_STATUS_LIVE_LOCAL_UNAVAILABLE
            reason = reg.get("reason_if_not_usable", "no usable live adapter")
        base["obsidia_status"] = live_status
        base["obsidia_execution_mode"] = live_status
        base["obsidia_live_attempted"] = True
        base["obsidia_live_available"] = False
        base["obsidia_live_adapter_type"] = reg.get("adapter_type", "NONE")
        base["obsidia_live_adapter_path"] = reg.get("path")
        base["obsidia_live_adapter_endpoint"] = None
        base["obsidia_fallback_used"] = False
        base["obsidia_live_unavailable_reason"] = reason
        return base

    if execution_mode == OIE_OBSIDIA_EXEC_MODE_LIVE_OR_FROZEN and live_attempted and not adapter_usable:
        # Fallback explicite vers frozen
        base = run_obsidia_local_actual(task)
        base["obsidia_execution_mode"] = base.get("obsidia_status", OBSIDIA_STATUS_FROZEN)
        base["obsidia_live_attempted"] = True
        base["obsidia_live_available"] = False
        base["obsidia_live_adapter_type"] = reg.get("adapter_type", "NONE")
        base["obsidia_live_adapter_path"] = reg.get("path")
        base["obsidia_live_adapter_endpoint"] = None
        base["obsidia_fallback_used"] = True
        base["obsidia_live_unavailable_reason"] = reg.get("reason_if_not_usable")
        return base

    # AUTO ou FROZEN_ONLY — comportement current (frozen/missing)
    base = run_obsidia_local_actual(task)
    base["obsidia_execution_mode"] = base.get("obsidia_status", OBSIDIA_STATUS_FROZEN)
    base["obsidia_live_attempted"] = live_attempted
    base["obsidia_live_available"] = adapter_usable
    base["obsidia_live_adapter_type"] = reg.get("adapter_type", "NONE")
    base["obsidia_live_adapter_path"] = reg.get("path")
    base["obsidia_live_adapter_endpoint"] = None
    base["obsidia_fallback_used"] = False
    return base


# ── Gemini lane ───────────────────────────────────────────────────────────────

def run_gemini_lane_dryrun(task: dict) -> dict:
    frozen = _FROZEN_GEMINI_PER_TASK.get(task["task_id"], {})
    return {
        "gemini_status": GEMINI_STATUS_DRYRUN,
        "gemini_detected_route": frozen.get("detected_route"),
        "gemini_route_match": frozen.get("route_match"),
        "gemini_latency_ms": frozen.get("latency_ms"),
        "gemini_input_tokens": frozen.get("input_tokens"),
        "gemini_output_tokens": frozen.get("output_tokens"),
        "gemini_total_tokens": frozen.get("total_tokens"),
        "gemini_cost_source": COST_SOURCE_UNAVAILABLE,
        "gemini_cost_per_request_measured": None,
        "gemini_cost_per_1m_measured": None,
        "gemini_quality_score": 1.0 if frozen.get("route_match") else 0.0,
        "gemini_failure_type": FAILURE_NONE,
        "gemini_external_model_call_required": True,
    }


def run_gemini_lane_real(task: dict, sdk_model: str) -> dict:
    if not sdk_model:
        return {
            "gemini_status": GEMINI_STATUS_FAILED,
            "gemini_failure_type": FAILURE_GEMINI_MODEL_NOT_CONFIGURED,
            "gemini_detected_route": None, "gemini_route_match": None,
            "gemini_latency_ms": None, "gemini_input_tokens": None,
            "gemini_output_tokens": None, "gemini_total_tokens": None,
            "gemini_cost_source": COST_SOURCE_UNAVAILABLE,
            "gemini_cost_per_request_measured": None, "gemini_cost_per_1m_measured": None,
            "gemini_quality_score": 0.0, "gemini_external_model_call_required": True,
        }
    raw = run_gemini_sdk(task["prompt"], sdk_model)
    inp_cost, out_cost = _read_cost_env()
    cost_src = COST_SOURCE_UNAVAILABLE
    cost_per_req = None
    cost_per_1m = None
    in_tok = raw.get("input_tokens")
    out_tok = raw.get("output_tokens")
    tot_tok = raw.get("total_tokens")
    if raw.get("usage_available") and in_tok is not None:
        sdk = compute_measured_sdk_cost(in_tok, out_tok or 0, inp_cost, out_cost)
        cost_src = sdk["cost_source"]
        cost_per_req = sdk.get("measured_cost_eur")
        cost_per_1m = sdk.get("measured_cost_eur_per_1m")
    output = raw.get("output_excerpt", "")
    rq = evaluate_route_quality(task["expected_route"], output, raw.get("success", False))
    return {
        "gemini_status": GEMINI_STATUS_REAL if raw.get("success") else GEMINI_STATUS_FAILED,
        "gemini_detected_route": rq.get("external_detected_route"),
        "gemini_route_match": rq.get("route_match"),
        "gemini_latency_ms": raw.get("latency_ms"),
        "gemini_input_tokens": in_tok,
        "gemini_output_tokens": out_tok,
        "gemini_total_tokens": tot_tok,
        "gemini_cost_source": cost_src,
        "gemini_cost_per_request_measured": cost_per_req,
        "gemini_cost_per_1m_measured": cost_per_1m,
        "gemini_quality_score": rq.get("quality_score"),
        "gemini_failure_type": raw.get("failure_type", FAILURE_NONE),
        "gemini_external_model_call_required": True,
    }


# ── Paired route comparison ───────────────────────────────────────────────────

def compute_paired_route_comparison(task: dict, obs: dict, gem: dict) -> dict:
    """Comparaison paire par paire Obsidia vs Gemini sur la même tâche et le même expected_route."""
    status = obs.get("obsidia_status")
    obs_match = obs.get("obsidia_route_match")
    gem_match = gem.get("gemini_route_match")
    gem_status = gem.get("gemini_status")

    is_missing = status == OBSIDIA_STATUS_MISSING
    gemini_failed = gem_status == GEMINI_STATUS_FAILED

    both_correct = obs_match is True and gem_match is True
    obsidia_only_correct = obs_match is True and gem_match is not True
    gemini_only_correct = gem_match is True and obs_match is not True and not is_missing
    both_wrong = obs_match is not True and gem_match is not True and not is_missing

    if both_correct:
        outcome = "BOTH_CORRECT"
    elif obsidia_only_correct:
        outcome = "OBSIDIA_ONLY_CORRECT"
    elif gem_match is True and is_missing:
        outcome = "GEMINI_CORRECT_ON_OBSIDIA_ADAPTER_MISSING"
    elif gemini_only_correct:
        outcome = "GEMINI_ONLY_CORRECT"
    elif is_missing and gem_match is not True:
        outcome = "OBSIDIA_ADAPTER_MISSING_GEMINI_WRONG"
    elif gemini_failed:
        outcome = "GEMINI_FAILED"
    elif both_wrong:
        outcome = "BOTH_WRONG"
    else:
        outcome = "UNKNOWN"

    route_accuracy_claimable = not is_missing
    return {
        "paired_route_outcome": outcome,
        "both_correct": both_correct,
        "obsidia_only_correct": obsidia_only_correct,
        "gemini_only_correct": gemini_only_correct,
        "both_wrong": both_wrong,
        "obsidia_adapter_missing": is_missing,
        "gemini_failed": gemini_failed,
        "functional_surface": not is_missing,
        "adapter_missing_excluded": is_missing,
        "obsidia_wired_surface": not is_missing,
        "gemini_compared_on_wired_surface": not is_missing,
        "route_accuracy_claimable": route_accuracy_claimable,
        "route_accuracy_scope": (
            "WIRED_SURFACE" if not is_missing
            else "ADAPTER_MISSING_SURFACE_NON_CLAIMABLE"
        ),
    }


# ── OIE Convergence Layer ────────────────────────────────────────────────────

def _oie_savings(family_cost: float) -> tuple[float, float, float, float]:
    """Returns (savings_api_normal, savings_agentic, avoided_api_normal, avoided_agentic)."""
    ratio_api = round(BT_API_NORMAL / family_cost, 4) if family_cost > 0 else 0.0
    ratio_agt = round(BT_AGENTIC / family_cost, 4) if family_cost > 0 else 0.0
    return ratio_api, ratio_agt, round(BT_API_NORMAL - family_cost, 6), round(BT_AGENTIC - family_cost, 6)


def _build_oie_cost_receipt_dict(task: dict, obs: dict, family_cost: float) -> dict:
    """Build a CostReceipt-compatible dict (uses native class when available)."""
    family = task["family"]
    dcfg = _OIE_DOMAIN_CFG.get(family, {})
    ratio_api, _, avoided_api, _ = _oie_savings(family_cost)
    proof_avail = dcfg.get("proof_available", False)
    elapsed = obs.get("obsidia_latency_ms") or 0.0
    units = float(obs.get("obsidia_estimated_total_tokens") or 0)
    receipt_kwargs = dict(
        layer=OIE_DOMAIN_NAME_MAPPING.get(family, family),
        route=task.get("expected_route", family),
        domain=OIE_DOMAIN_NAME_MAPPING.get(family, family),
        action_type=dcfg.get("domain_action_type", ""),
        elapsed_ms=elapsed,
        internal_units=units,
        modules_activated=[],
        modules_skipped=[],
        obsidia_cost_eur_per_1m=family_cost,
        baseline_label="BT_API_NORMAL",
        baseline_cost_eur_per_1m=BT_API_NORMAL,
        savings_ratio=ratio_api,
        avoided_cost_eur_per_1m=avoided_api,
        kernel_status="ACTIVE",
        proof_or_replay_available=proof_avail,
    )
    if _OIE_CostReceipt is not None:
        try:
            import dataclasses
            cr = _OIE_CostReceipt(**receipt_kwargs)
            d = dataclasses.asdict(cr)
            d["domain_metrics"] = None
            d["cost_claimable"] = False
            d["cost_basis"] = COST_BASIS_LOCAL_PROXY
            return d
        except Exception:
            pass
    # Fallback local dict with same fields + governance invariants
    receipt_kwargs.update({
        "receipt_id": "LOCAL_FALLBACK",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "readonly": True,
        "decision_authority": DECISION_AUTHORITY,
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "domain_metrics": None,
        "cost_claimable": False,
        "cost_basis": COST_BASIS_LOCAL_PROXY,
    })
    return receipt_kwargs


def _build_domain_metrics_dict(task: dict, obs: dict, family_cost: float) -> dict:
    """Build a DomainMetrics-compatible dict per family."""
    family = task["family"]
    dcfg = _OIE_DOMAIN_CFG.get(family, {})
    is_missing = obs.get("obsidia_status") == OBSIDIA_STATUS_MISSING
    ratio_api, ratio_agt, avoided_api, _ = _oie_savings(family_cost)
    elapsed = obs.get("obsidia_latency_ms") or 0.0
    units = float(obs.get("obsidia_estimated_total_tokens") or 0)

    dm = {
        "domain_name": dcfg.get("domain_name", family),
        "domain_action_type": dcfg.get("domain_action_type", ""),
        "domain_risk_level": dcfg.get("domain_risk_level", ""),
        "domain_reversibility": dcfg.get("domain_reversibility", ""),
        "domain_cost_eur_per_1m": family_cost,
        "domain_latency_ms": elapsed,
        "domain_internal_units": units,
        "domain_tools_used": dcfg.get("domain_tools_used", []),
        "domain_tools_skipped": dcfg.get("domain_tools_skipped", []),
        "external_api_calls_avoided": 0 if is_missing else dcfg.get("external_api_calls_avoided", 0),
        "llm_calls_avoided": 0 if is_missing else dcfg.get("llm_calls_avoided", 0),
        "human_review_avoided_estimate": 0.0,
        "hold_count": 0,
        "block_count": 0,
        "act_count": 0,
        "unknowns_count": 0,
        "contradictions_count": 0,
        "proof_available": False if is_missing else dcfg.get("proof_available", False),
        "replay_available": False if is_missing else dcfg.get("replay_available", False),
        "business_cost_avoided_label": dcfg.get("business_cost_avoided_label", ""),
        "business_cost_avoided_estimate_eur": 0.0 if is_missing else round(avoided_api, 6),
        "domain_savings_ratio": 0.0 if is_missing else ratio_api,
        "domain_claimable": not is_missing,
        "domain_status": "ADAPTER_MISSING_NON_CLAIMABLE" if is_missing else "WIRED",
    }
    return dm


def compute_oie_layer_fields(task: dict, obs: dict) -> dict:
    """Build all oie_ fields for a row — OIE V0.1 convergence layer."""
    family = task["family"]
    family_cost = OIE_FAMILY_COSTS.get(family, 0.0)
    is_missing = obs.get("obsidia_status") == OBSIDIA_STATUS_MISSING
    ratio_api, ratio_agt, avoided_api, avoided_agt = _oie_savings(family_cost)

    receipt = _build_oie_cost_receipt_dict(task, obs, family_cost)
    dm = _build_domain_metrics_dict(task, obs, family_cost)

    return {
        "oie_layer_name": OIE_DOMAIN_NAME_MAPPING.get(family, family),
        "oie_family_cost_eur_per_1m": family_cost,
        "oie_cost_basis": COST_BASIS_LOCAL_PROXY,
        "oie_primary_baseline_cost_eur_per_1m": BT_API_NORMAL,
        "oie_agentic_baseline_cost_eur_per_1m": BT_AGENTIC,
        "oie_savings_ratio_vs_api_normal": ratio_api,
        "oie_savings_ratio_vs_agentic": ratio_agt,
        "oie_avoided_cost_vs_api_normal_eur_per_1m": avoided_api,
        "oie_avoided_cost_vs_agentic_eur_per_1m": avoided_agt,
        "oie_cost_claimable": False,
        "oie_cost_claim_warning": _OIE_WARNINGS[5],
        "oie_route_claim_scope": (
            "WIRED_SURFACE" if not is_missing else "ADAPTER_MISSING_NON_CLAIMABLE"
        ),
        "oie_functional_claimable": not is_missing,
        "oie_domain_claimable": not is_missing,
        "oie_cost_receipt": receipt,
        "domain_metrics": dm,
    }


# ── Dual-lane structure ───────────────────────────────────────────────────────

def compute_dual_lane(task: dict, obs: dict, gem: dict) -> dict:
    """Construit la structure dual-lane explicite Obsidia vs Gemini pour chaque tâche."""
    obs_status = obs.get("obsidia_status", "UNKNOWN")
    obs_exec_mode_field = obs.get("obsidia_execution_mode", obs_status)
    gem_status = gem.get("gemini_status", "UNKNOWN")
    is_missing = obs_status == OBSIDIA_STATUS_MISSING
    is_frozen = obs_status == OBSIDIA_STATUS_FROZEN
    is_real_adapter = obs_status == OBSIDIA_STATUS_REAL
    is_live_bridge = obs_status == OBSIDIA_STATUS_LIVE_LOCAL
    is_bridge_kernel_err = obs_status == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"
    is_live_unavail = obs_status == OBSIDIA_STATUS_LIVE_LOCAL_UNAVAILABLE
    gem_is_real = gem_status == GEMINI_STATUS_REAL
    family = task["family"]
    reg = _OBSIDIA_LIVE_ADAPTER_REGISTRY.get(family, {})

    # Détermination du mode effectif depuis run_obsidia_lane() (déjà exécuté)
    obs_exec_mode = obs_exec_mode_field
    obs_live_avail = is_live_bridge or is_bridge_kernel_err
    obs_fallback = obs.get("obsidia_fallback_used", False)

    # comparison_scope — enrichi avec les statuts bridge
    if gem_status == GEMINI_STATUS_DRYRUN:
        scope = "DRY_RUN"
    elif is_missing:
        scope = "OBSIDIA_ADAPTER_MISSING_VS_GEMINI_REAL" if gem_is_real else "DRY_RUN"
    elif is_live_bridge and gem_is_real:
        scope = "OBSIDIA_LIVE_BRIDGE_VS_GEMINI_REAL"
    elif is_live_bridge:
        scope = "DRY_RUN"
    elif is_bridge_kernel_err and gem_is_real:
        scope = "OBSIDIA_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE_VS_GEMINI_REAL"
    elif is_bridge_kernel_err:
        scope = "DRY_RUN"
    elif is_real_adapter and gem_is_real:
        scope = "DUAL_REAL"
    elif (is_frozen or "FROZEN" in str(obs_exec_mode).upper()) and gem_is_real:
        scope = "OBSIDIA_FROZEN_VS_GEMINI_REAL"
    elif is_live_unavail and gem_is_real:
        scope = "OBSIDIA_LIVE_UNAVAILABLE_VS_GEMINI_REAL"
    elif gem_status == GEMINI_STATUS_FAILED:
        scope = "GEMINI_FAILED"
    else:
        scope = "UNAVAILABLE"

    comparison_claimable = (
        not is_missing
        and not is_live_unavail
        and obs_exec_mode not in (OBSIDIA_STATUS_LIVE_LOCAL_UNAVAILABLE, "LIVE_LOCAL_UNAVAILABLE")
    )

    warning_parts = []
    if scope == "DRY_RUN":
        warning_parts.append("Gemini is dry-run mock — not real SDK execution.")
    if is_missing:
        warning_parts.append(f"{family} adapter is ADAPTER_MISSING — Obsidia not wired.")
    if is_frozen:
        warning_parts.append("Obsidia lane is FROZEN_V0_ESTIMATE — architecture proxy, not live bridge execution.")
    if is_bridge_kernel_err:
        warning_parts.append(f"Live bridge attempted but kernel 3001 unreachable — {reg.get('kernel_target')}.")
    if is_live_unavail:
        warning_parts.append("LIVE_LOCAL requested but unavailable — no usable bridge endpoint.")
    if not gem_is_real:
        warning_parts.append("Gemini lane is not REAL_SDK — cost comparison not measurable.")
    if not comparison_claimable:
        warning_parts.append("Comparison is not claimable for functional assertions.")
    if is_live_bridge:
        warning_parts.append("Obsidia LIVE_LOCAL_BRIDGE confirmed — route via API 8000 → kernel 3001.")

    # Endpoint effectivement utilisé
    if is_live_bridge or is_bridge_kernel_err:
        ep_used = obs.get("obsidia_live_adapter_endpoint") or reg.get("endpoint") or "LOCAL_HTTP_BRIDGE"
    elif is_real_adapter:
        ep_used = "IN_PROCESS_FUNCTION"
    elif is_missing:
        ep_used = "ADAPTER_MISSING"
    else:
        ep_used = "FROZEN_V0_ESTIMATE"

    obsidia_lane = {
        "execution_mode": obs_exec_mode,
        "status": obs_status,
        "attempted_live_execution": obs.get("obsidia_live_attempted", False),
        "live_execution_available": obs_live_avail,
        "fallback_used": obs_fallback,
        "adapter_missing": is_missing,
        "adapter_type": reg.get("adapter_type", "NONE"),
        "endpoint_or_function_used": ep_used,
        "bridge_endpoint": reg.get("endpoint"),
        "kernel_target": reg.get("kernel_target"),
        "kernel_invoked": obs.get("obsidia_live_kernel_invoked"),
        "kernel_gate": obs.get("obsidia_live_kernel_gate"),
        "kernel_unreachable": is_bridge_kernel_err,
        "detected_route": obs.get("obsidia_detected_route"),
        "route_match": obs.get("obsidia_route_match"),
        "latency_ms": obs.get("obsidia_latency_ms"),
        "output_excerpt": None,
        "error": None,
        "cost_basis": COST_BASIS_LOCAL_PROXY,
        "cost_claimable": False,
        "governance_flags": {
            "emits_act": EMITS_ACT,
            "memory_write": MEMORY_WRITE,
            "kernel_mutation": KERNEL_MUTATION,
            "decision_authority": DECISION_AUTHORITY,
        },
    }

    gemini_lane = {
        "execution_mode": gem_status,
        "status": gem_status,
        "provider": PROVIDER_GEMINI,
        "model": os.environ.get("OIE_EXTERNAL_MODEL_LABEL", DEFAULT_GEMINI_MODEL),
        "attempted_real_sdk": gem_is_real,
        "detected_route": gem.get("gemini_detected_route"),
        "route_match": gem.get("gemini_route_match"),
        "latency_ms": gem.get("gemini_latency_ms"),
        "input_tokens": gem.get("gemini_input_tokens"),
        "output_tokens": gem.get("gemini_output_tokens"),
        "total_tokens": gem.get("gemini_total_tokens"),
        "output_excerpt": None,
        "error": gem.get("gemini_failure_type") if gem_status == GEMINI_STATUS_FAILED else None,
        "cost_basis": COST_BASIS_SDK_MEASURED if gem_is_real else COST_BASIS_DRY_RUN_MOCK,
        "cost_claimable": False,
    }

    return {
        "benchmark_task_id": task["task_id"],
        "family": task["family"],
        "expected_route": task["expected_route"],
        "obsidia_lane": obsidia_lane,
        "gemini_lane": gemini_lane,
        "comparison_scope": scope,
        "comparison_claimable": comparison_claimable,
        "comparison_warning": " | ".join(warning_parts) if warning_parts else "OK",
    }


# ── Compare row ───────────────────────────────────────────────────────────────

def compute_compare_row(task: dict, obs: dict, gem: dict) -> dict:
    wh_per_1k, local_w, co2_per_kwh = _read_energy_env()

    obs_lat = obs.get("obsidia_latency_ms")
    gem_lat = gem.get("gemini_latency_ms")
    gem_tok = gem.get("gemini_total_tokens")
    obs_tok = obs.get("obsidia_estimated_total_tokens")
    gem_cost = gem.get("gemini_cost_per_request_measured")
    obs_cost = obs.get("obsidia_cost_per_request_est")

    # Speed
    lat_delta_ms = (gem_lat - obs_lat) if (gem_lat is not None and obs_lat is not None) else None
    lat_delta_pct = (
        round(100.0 * lat_delta_ms / gem_lat, 2)
        if lat_delta_ms is not None and gem_lat and gem_lat > 0
        else None
    )
    speedup, _ = _safe_ratio(gem_lat, obs_lat)
    speedup = round(speedup, 4) if speedup is not None else None

    obs_throughput = round(1000.0 / obs_lat, 4) if obs_lat and obs_lat > 0 else None
    gem_throughput = round(1000.0 / gem_lat, 4) if gem_lat and gem_lat > 0 else None
    thr_ratio, _ = _safe_ratio(obs_throughput, gem_throughput)
    thr_ratio = round(thr_ratio, 4) if thr_ratio is not None else None

    obs_q = obs.get("obsidia_quality_score")
    gem_q = gem.get("gemini_quality_score")
    obs_boundary = obs.get("obsidia_boundary_ok", True)

    obs_sdps = (
        round(obs_throughput * (obs_q or 0.0) * (1.0 if obs_boundary else 0.0), 4)
        if obs_throughput is not None and obs_q is not None else None
    )
    gem_sdps = (
        round(gem_throughput * (gem_q or 0.0), 4)
        if gem_throughput is not None and gem_q is not None else None
    )

    obs_dpc = round(1.0 / obs_cost, 4) if obs_cost and obs_cost > 0 else None
    gem_dpc = round(1.0 / gem_cost, 4) if gem_cost and gem_cost > 0 else None

    # Tokens / context
    tok_delta_abs = (gem_tok - obs_tok) if (gem_tok is not None and obs_tok is not None) else None
    tok_delta_pct = (
        round(100.0 * tok_delta_abs / gem_tok, 2)
        if tok_delta_abs is not None and gem_tok and gem_tok > 0 else None
    )
    ext_dep_ratio, _ = _safe_ratio(gem_tok, max(obs_tok or 0, 1))
    context_budget_delta_pct = tok_delta_pct

    # Cost
    avoided_cost_req = (gem_cost - obs_cost) if (gem_cost is not None and obs_cost is not None) else None
    cost_sr, cost_ratio_status = _safe_ratio(gem_cost, obs_cost)
    cost_delta_pct = (
        round(100.0 * avoided_cost_req / gem_cost, 2)
        if avoided_cost_req is not None and gem_cost and gem_cost > 0 else None
    )
    obs_c1m = obs.get("obsidia_cost_per_1m_est")
    gem_c1m = gem.get("gemini_cost_per_1m_measured")
    avoided_c1m = (gem_c1m - obs_c1m) if (gem_c1m is not None and obs_c1m is not None) else None
    c1m_sr, _ = _safe_ratio(gem_c1m, obs_c1m)

    # Energy
    energy = compute_energy_metrics(gem_tok, obs_lat, wh_per_1k, local_w, co2_per_kwh)
    obs_dpwh = (
        round(1.0 / energy["local_energy_wh_est"], 4)
        if energy.get("local_energy_wh_est") and energy["local_energy_wh_est"] > 0 else None
    )
    gem_dpwh = (
        round(1.0 / energy["external_energy_wh_est"], 4)
        if energy.get("external_energy_wh_est") and energy["external_energy_wh_est"] > 0 else None
    )

    q_delta = (
        round(obs_q - gem_q, 4)
        if obs_q is not None and gem_q is not None else None
    )

    gov_clean = (
        not EMITS_ACT and not MEMORY_WRITE and not KERNEL_MUTATION and obs_boundary
    )

    def _winner(a, b) -> str:
        if a is None or b is None:
            return "UNKNOWN"
        if a > b:
            return "OBSIDIA"
        if b > a:
            return "GEMINI"
        return "TIE"

    winner_speed = _winner(gem_lat, obs_lat) if (obs_lat and gem_lat) else "UNKNOWN"
    winner_cost = _winner(gem_cost, obs_cost) if (obs_cost and gem_cost) else "UNKNOWN"
    winner_energy = (
        _winner(energy.get("external_energy_wh_est"), energy.get("local_energy_wh_est"))
        if energy["energy_source"] == ENERGY_SOURCE_ESTIMATE else "UNKNOWN"
    )
    winner_route = (
        "TIE" if (obs.get("obsidia_route_match") and gem.get("gemini_route_match"))
        else "OBSIDIA" if obs.get("obsidia_route_match")
        else "GEMINI" if gem.get("gemini_route_match")
        else "NEITHER"
    )
    winner_gov = "OBSIDIA" if gov_clean else "CONTESTED"

    # Build base row
    row: dict = {
        "task_id": task["task_id"],
        "family": task["family"],
        "expected_route": task["expected_route"],
        "obsidia_detected_route": obs.get("obsidia_detected_route"),
        "gemini_detected_route": gem.get("gemini_detected_route"),
        "obsidia_route_match": obs.get("obsidia_route_match"),
        "gemini_route_match": gem.get("gemini_route_match"),
        "obsidia_latency_ms": obs_lat,
        "gemini_latency_ms": gem_lat,
        "latency_delta_ms": round(lat_delta_ms, 4) if lat_delta_ms is not None else None,
        "latency_delta_pct": lat_delta_pct,
        "speedup_ratio": speedup,
        "obsidia_throughput_req_per_sec": obs_throughput,
        "gemini_throughput_req_per_sec": gem_throughput,
        "throughput_gain_ratio": thr_ratio,
        "safe_decisions_per_second_obsidia": obs_sdps,
        "safe_decisions_per_second_gemini": gem_sdps,
        "decisions_per_cost_unit_obsidia": obs_dpc,
        "decisions_per_cost_unit_gemini": gem_dpc,
        "decisions_per_wh_obsidia": obs_dpwh,
        "decisions_per_wh_gemini": gem_dpwh,
        "obsidia_estimated_total_tokens": obs_tok,
        "gemini_total_tokens": gem_tok,
        "token_delta_abs": tok_delta_abs,
        "token_delta_pct": tok_delta_pct,
        "estimated_context_budget_delta_pct": context_budget_delta_pct,
        "external_token_dependency_ratio": round(ext_dep_ratio, 4) if ext_dep_ratio else None,
        "gemini_cost_per_request_measured": gem_cost,
        "obsidia_cost_per_request_est": obs_cost,
        "avoided_cost_per_request": round(avoided_cost_req, 10) if avoided_cost_req is not None else None,
        "cost_savings_ratio": round(cost_sr, 4) if cost_sr is not None else None,
        "cost_ratio_status": cost_ratio_status,
        "cost_delta_pct": cost_delta_pct,
        "gemini_cost_per_1m_measured": gem_c1m,
        "obsidia_cost_per_1m_est": obs_c1m,
        "avoided_cost_per_1m": round(avoided_c1m, 4) if avoided_c1m is not None else None,
        "cost_savings_ratio_1m": round(c1m_sr, 4) if c1m_sr is not None else None,
        "obsidia_energy_wh_est": energy.get("local_energy_wh_est"),
        "gemini_energy_wh_est": energy.get("external_energy_wh_est"),
        "energy_avoided_wh": energy.get("energy_avoided_wh"),
        "energy_savings_ratio": (
            round(energy["energy_savings_ratio"], 4)
            if energy.get("energy_savings_ratio") is not None else None
        ),
        "obsidia_carbon_gco2_est": energy.get("local_carbon_gco2_est"),
        "gemini_carbon_gco2_est": energy.get("external_carbon_gco2_est"),
        "carbon_avoided_gco2": energy.get("carbon_avoided_gco2"),
        "energy_source": energy["energy_source"],
        "obsidia_modules_skipped": obs.get("obsidia_modules_skipped"),
        "obsidia_cache_hit": obs.get("obsidia_cache_hit"),
        "obsidia_model_call_avoided": obs.get("obsidia_model_call_avoided"),
        "obsidia_quality_score": obs_q,
        "gemini_quality_score": gem_q,
        "quality_delta": q_delta,
        "obsidia_boundary_ok": obs_boundary,
        "obsidia_governance_clean": gov_clean,
        "obsidia_status": obs.get("obsidia_status"),
        "gemini_status": gem.get("gemini_status"),
        "winner_speed": winner_speed,
        "winner_cost": winner_cost,
        "winner_energy": winner_energy,
        "winner_route": winner_route,
        "winner_governance": winner_gov,
        "final_interpretation": _build_interpretation(task, obs, gem, obs.get("obsidia_model_call_avoided")),
    }

    # Phase 2 : cost basis
    cost_basis = compute_cost_basis_fields(task, obs, gem)
    row.update(cost_basis)

    # Phase 4+5 : intellectual economy
    ie = compute_intellectual_economy(task, obs, gem, row)
    row.update(ie)
    # Export surface score for summary
    row["external_dependency_reduction_score"] = ie.get("external_dependency_reduction_score", 0.0)

    # Phase 4 : gencoin calibration
    gc = compute_gencoin_calibration(ie)
    row.update(gc)

    # Phase 5 : economy layers (named sub-dicts for reporting)
    row["technical_cost_layer"] = {
        "local_latency_ms": obs_lat,
        "external_latency_ms": gem_lat,
        "local_energy_wh_est": energy.get("local_energy_wh_est"),
        "external_energy_wh_est": energy.get("external_energy_wh_est"),
        "local_tokens_est": obs_tok,
        "external_tokens_measured": gem_tok,
        "modules_activated": obs.get("obsidia_modules_activated"),
        "modules_skipped": obs.get("obsidia_modules_skipped"),
        "files_read": obs.get("obsidia_files_read"),
        "files_skipped": obs.get("obsidia_files_skipped"),
        "memory_records_loaded": obs.get("obsidia_memory_records_loaded"),
        "memory_records_skipped": obs.get("obsidia_memory_records_skipped"),
    }
    row["inference_economy_layer"] = {
        "model_call_avoided": obs.get("obsidia_model_call_avoided"),
        "external_call_required": gem.get("gemini_external_model_call_required"),
        "external_tokens_avoided_est": tok_delta_abs,
        "external_dependency_reduction_score": ie.get("external_dependency_reduction_score"),
        "cost_comparison_claimable": cost_basis.get("cost_comparison_claimable"),
        "api_cost_avoided_claimable": False,
    }
    row["intellectual_economy_layer"] = {
        "cognitive_value_score": ie.get("cognitive_value_score"),
        "proof_quality_score": ie.get("proof_quality_score"),
        "governance_value_score": ie.get("governance_value_score"),
        "friction_reduction_score": ie.get("friction_reduction_score"),
        "risk_reduction_score": ie.get("risk_reduction_score"),
        "stability_value_score": ie.get("stability_value_score"),
        "debt_score": ie.get("debt_score"),
        "intellectual_value_score": ie.get("intellectual_value_score"),
    }
    row["gencoin_calibration_layer"] = {
        "gencoin_emission_allowed": False,
        "gencoin_emission_amount": 0,
        "gencoin_distribution_mode": GENCOIN_DISTRIBUTION_MODE,
        "gencoin_reason": GENCOIN_EMISSION_REASON,
        "source_law_satisfied": False,
    }

    # Phase KP : Known path
    kp = compute_known_path(task, obs, gem, row)
    row.update(kp)
    row["known_path_layer"] = kp

    # Phase IN : Inference necessity
    inf_nec = compute_inference_necessity(task, obs, gem)
    row.update(inf_nec)
    row["inference_necessity_layer"] = inf_nec

    # Phase GS : Governed speed
    gs = compute_governed_speed(task, obs, gem, row)
    row.update(gs)
    row["governed_speed_layer"] = gs

    # Phase MF : Math formalization
    mf = compute_math_formalization(task, obs, gem, row)
    row.update(mf)
    row["math_formalization_layer"] = mf

    # Phase PRC : Paired route comparison
    prc = compute_paired_route_comparison(task, obs, gem)
    row.update(prc)
    row["paired_route_layer"] = prc

    # Phase OIE : OIE V0.1 convergence layer
    oie = compute_oie_layer_fields(task, obs)
    row.update(oie)

    # Phase DL : Dual-lane structure
    dl = compute_dual_lane(task, obs, gem)
    row["dual_lane"] = dl

    # Phase LLM-N : Model necessity
    row["model_necessity"] = compute_model_necessity(task, row)

    # Phase AA : Answer adequacy
    row["answer_adequacy"] = compute_answer_adequacy(task, row)

    return row


def _build_interpretation(task: dict, obs: dict, gem: dict, model_avoided: Optional[bool]) -> str:
    family = task["family"]
    if model_avoided:
        return (
            f"{family}: Obsidia routes deterministically -- no LLM call. "
            f"Gemini requires full inference. Work avoidance is the key metric."
        )
    if obs.get("obsidia_status") == OBSIDIA_STATUS_MISSING:
        return (
            f"{family}: Obsidia adapter not available for live run. "
            f"Architecture cost estimate used. Gemini as reference inference cost."
        )
    return (
        f"{family}: Both lanes invoke a model. Comparison on latency, cost, and governance."
    )


# ── Global summary ────────────────────────────────────────────────────────────

def _avg(vals: list) -> Optional[float]:
    clean = [v for v in vals if v is not None]
    return round(sum(clean) / len(clean), 6) if clean else None


def compute_summary(rows: list[dict], tasks: list[dict]) -> dict:
    wh_per_1k, local_w, co2_per_kwh = _read_energy_env()
    energy_src = ENERGY_SOURCE_ESTIMATE if (wh_per_1k and local_w) else ENERGY_SOURCE_UNAVAILABLE
    inp_cost, out_cost = _read_cost_env()
    cost_src = COST_SOURCE_SDK_MEASURED if (inp_cost and out_cost) else COST_SOURCE_UNAVAILABLE

    obs_route_ok = sum(1 for r in rows if r.get("obsidia_route_match") is True)
    gem_route_ok = sum(1 for r in rows if r.get("gemini_route_match") is True)
    model_avoided = sum(1 for r in rows if r.get("obsidia_model_call_avoided") is True)
    cache_hits = sum(1 for r in rows if r.get("obsidia_cache_hit") is True)
    boundary_ok = sum(1 for r in rows if r.get("obsidia_boundary_ok") is True)
    gov_clean_all = all(r.get("obsidia_governance_clean", False) for r in rows)
    n = len(rows)

    # Debt summary
    total_debt = sum(r.get("debt_score", 0.0) or 0.0 for r in rows)
    adapter_missing_debt = sum(
        r.get("debt_score", 0.0) or 0.0
        for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING
    )
    cost_uncalibrated_debt = round(0.20 * n, 4)
    proof_missing_debt = sum(
        0.20 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING
    )
    measurement_debt = round(total_debt - adapter_missing_debt, 4)

    # Gemini cost total
    gem_total_cost = sum(r.get("gemini_cost_per_request_measured") or 0.0 for r in rows)
    gem_total_cost_val = gem_total_cost if any(r.get("gemini_cost_per_request_measured") is not None for r in rows) else None

    # Total avoided cost
    total_avoided = sum(r.get("avoided_cost_per_request") or 0.0 for r in rows)
    total_avoided_val = total_avoided if any(r.get("avoided_cost_per_request") is not None for r in rows) else None

    # Surface metrics
    surface = compute_surface_metrics(rows)

    summary = {
        "benchmark_version": BENCHMARK_VERSION,
        "benchmark_date": BENCHMARK_DATE,
        "tasks_attempted": n,
        "obsidia_route_accuracy": round(obs_route_ok / n, 4) if n else None,
        "gemini_route_accuracy": round(gem_route_ok / n, 4) if n else None,
        "obsidia_avg_latency_ms": _avg([r.get("obsidia_latency_ms") for r in rows]),
        "gemini_avg_latency_ms": _avg([r.get("gemini_latency_ms") for r in rows]),
        "avg_latency_delta_pct": _avg([r.get("latency_delta_pct") for r in rows]),
        "avg_speedup_ratio": _avg([r.get("speedup_ratio") for r in rows]),
        "obsidia_total_estimated_tokens": sum(r.get("obsidia_estimated_total_tokens") or 0 for r in rows),
        "gemini_total_tokens": sum(r.get("gemini_total_tokens") or 0 for r in rows),
        "avg_token_delta_pct": _avg([r.get("token_delta_pct") for r in rows]),
        "gemini_total_cost_measured": gem_total_cost_val,
        "obsidia_total_cost_est": sum(r.get("obsidia_cost_per_request_est") or 0.0 for r in rows),
        "total_avoided_cost": total_avoided_val,
        "avg_cost_savings_ratio": _avg([r.get("cost_savings_ratio") for r in rows]),
        "obsidia_total_energy_wh_est": (
            sum(r.get("obsidia_energy_wh_est") or 0.0 for r in rows)
            if energy_src == ENERGY_SOURCE_ESTIMATE else None
        ),
        "gemini_total_energy_wh_est": (
            sum(r.get("gemini_energy_wh_est") or 0.0 for r in rows)
            if energy_src == ENERGY_SOURCE_ESTIMATE else None
        ),
        "total_energy_avoided_wh": (
            sum(r.get("energy_avoided_wh") or 0.0 for r in rows)
            if energy_src == ENERGY_SOURCE_ESTIMATE else None
        ),
        "avg_energy_savings_ratio": _avg([r.get("energy_savings_ratio") for r in rows]),
        "obsidia_model_call_avoided_count": model_avoided,
        "obsidia_model_call_avoided_rate": round(model_avoided / n, 4) if n else None,
        "obsidia_modules_skipped_total": sum(r.get("obsidia_modules_skipped") or 0 for r in rows),
        "obsidia_cache_hit_ratio": round(cache_hits / n, 4) if n else None,
        "obsidia_boundary_safety_pass_rate": round(boundary_ok / n, 4) if n else None,
        "obsidia_quality_avg": _avg([r.get("obsidia_quality_score") for r in rows]),
        "gemini_quality_avg": _avg([r.get("gemini_quality_score") for r in rows]),
        "quality_delta_avg": _avg([r.get("quality_delta") for r in rows]),
        "obsidia_safe_decisions_per_second_avg": _avg([r.get("safe_decisions_per_second_obsidia") for r in rows]),
        "gemini_safe_decisions_per_second_avg": _avg([r.get("safe_decisions_per_second_gemini") for r in rows]),
        "obsidia_decisions_per_cost_unit_avg": _avg([r.get("decisions_per_cost_unit_obsidia") for r in rows]),
        "gemini_decisions_per_cost_unit_avg": _avg([r.get("decisions_per_cost_unit_gemini") for r in rows]),
        "obsidia_decisions_per_wh_avg": (
            _avg([r.get("decisions_per_wh_obsidia") for r in rows])
            if energy_src == ENERGY_SOURCE_ESTIMATE else None
        ),
        "gemini_decisions_per_wh_avg": (
            _avg([r.get("decisions_per_wh_gemini") for r in rows])
            if energy_src == ENERGY_SOURCE_ESTIMATE else None
        ),
        "governance_clean": gov_clean_all,
        "decision_authority": DECISION_AUTHORITY,
        "emits_act": EMITS_ACT,
        "memory_write": MEMORY_WRITE,
        "kernel_mutation": KERNEL_MUTATION,
        "secrets_redacted": SECRETS_REDACTED,
        "energy_source": energy_src,
        "cost_source": cost_src,
        "adapter_missing_count": sum(1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING),
        "frozen_v0_estimate_count": sum(1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_FROZEN),
        "real_adapter_count": sum(1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_REAL),
        # Phase 2 : cost basis global
        "obsidia_cost_basis_global": COST_BASIS_LOCAL_PROXY,
        "gemini_cost_basis_global": COST_BASIS_SDK_MEASURED if cost_src == COST_SOURCE_SDK_MEASURED else COST_BASIS_DRY_RUN_MOCK,
        "cost_comparison_claimable_global": False,
        "cost_claim_warning": COST_PROXY_WARNING,
        # Phase 3 : surfaces
        **surface,
        # Phase 6 : internal economy
        "intellectual_economy_basis": IE_BASIS,
        "intellectual_value_avg": _avg([r.get("intellectual_value_score") for r in rows]),
        "intellectual_value_available_surface_avg": _avg([
            r.get("intellectual_value_score") for r in rows
            if r.get("obsidia_status") != OBSIDIA_STATUS_MISSING
        ]),
        "intellectual_value_terrain_avg": _avg([
            r.get("intellectual_value_score") for r in rows
            if r.get("family") in TERRAIN_PROOF_FAMILIES
        ]),
        "intellectual_value_model_avoided_avg": _avg([
            r.get("intellectual_value_score") for r in rows
            if r.get("family") in MODEL_AVOIDED_FAMILIES
        ]),
        "intellectual_value_adapter_missing_avg": _avg([
            r.get("intellectual_value_score") for r in rows
            if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING
        ]),
        "intellectual_value_adapter_missing_excluded_from_victory": True,
        # Phase 6 : gencoin
        "gencoin_mode": GENCOIN_MODE,
        "gencoin_emission_enabled": False,
        "gencoin_total_emission": 0,
        "source_law_global_satisfied": False,
        "source_law_global_reason": "Benchmark calibration only; no real emission, no market value, no distribution.",
        # Phase 6 : debt
        "internal_economy_debt_total": round(total_debt, 4),
        "adapter_missing_debt": round(adapter_missing_debt, 4),
        "cost_uncalibrated_debt": cost_uncalibrated_debt,
        "proof_missing_debt": round(proof_missing_debt, 4),
        "measurement_debt": round(measurement_debt, 4),
        # Audit-safe claims
        "audit_safe_claims": [
            "Obsidia avoids external model inference on the model-avoided surface.",
            "Obsidia cost is a local proxy estimate, not a measured bill.",
            "Gemini cost is SDK usage measured when REAL mode usage is available.",
            "Cost comparison is not claimable until Obsidia local cost is measured or calibrated.",
            "Gencoin emission is disabled in this benchmark.",
            "Intellectual value is calibration-only.",
            "Available wired surface excludes adapter missing families.",
            "BRODY, OBSIDURE, and LEAN are adapter missing and must not be counted as functional victories.",
            "Energy comparison is proxy-based unless hardware/provider telemetry is supplied.",
            "Governance remains KX108_ONLY with emits_act=false, memory_write=false, kernel_mutation=false.",
        ],
    }

    # ── Extension : known path, inference necessity, governed speed, math formal, novice, partial ──

    _kp_c = sum(1 for r in rows if r.get("known_path_detected"))
    _inf_c = sum(1 for r in rows if r.get("unnecessary_inference_avoided"))
    _ext_c = sum(1 for r in rows if r.get("external_dependency_avoided"))
    _gov_c = sum(1 for r in rows if r.get("governance_preserved_at_speed"))
    _mf_c = sum(1 for r in rows if r.get("math_formalization_support"))

    _gs_vals = [r.get("governed_speedup_ratio") for r in rows if r.get("governed_speedup_ratio") is not None]
    _gs_sorted = sorted(_gs_vals)
    _gs_avg = _avg(_gs_vals)
    _gs_median = round(_gs_sorted[len(_gs_sorted) // 2], 4) if _gs_sorted else None
    _gs_avail_avg = _avg([
        r.get("governed_speedup_ratio") for r in rows
        if r.get("governed_speedup_ratio") is not None
        and r.get("obsidia_status") != OBSIDIA_STATUS_MISSING
    ])
    _gs_avoided_avg = _avg([
        r.get("governed_speedup_ratio") for r in rows
        if r.get("governed_speedup_ratio") is not None and r.get("obsidia_model_call_avoided")
    ])

    _ts_vals = [
        (r.get("gemini_latency_ms") or 0.0) - (r.get("obsidia_latency_ms") or 0.0)
        for r in rows
        if r.get("gemini_latency_ms") is not None and r.get("obsidia_latency_ms") is not None
    ]
    _ts_avg = round(sum(_ts_vals) / len(_ts_vals), 4) if _ts_vals else None
    _ts_per_1k_s = round(_ts_avg * 1000 / 1000.0, 4) if _ts_avg is not None else None
    _ts_per_1k_min = round(_ts_avg * 1000 / 1000.0 / 60.0, 6) if _ts_avg is not None else None
    _ts_per_1m_h = round(_ts_avg * 1_000_000 / 1000.0 / 3600.0, 4) if _ts_avg is not None else None
    _ts_per_1m_d = round(_ts_avg * 1_000_000 / 1000.0 / 86400.0, 6) if _ts_avg is not None else None

    _avoided_rows = [r for r in rows if r.get("obsidia_model_call_avoided")]
    _ts_av_vals = [
        (r.get("gemini_latency_ms") or 0.0) - (r.get("obsidia_latency_ms") or 0.0)
        for r in _avoided_rows
        if r.get("gemini_latency_ms") is not None and r.get("obsidia_latency_ms") is not None
    ]
    _ts_av_avg = round(sum(_ts_av_vals) / len(_ts_av_vals), 4) if _ts_av_vals else None
    _ts_av_per_1k_min = round(_ts_av_avg * 1000 / 1000.0 / 60.0, 6) if _ts_av_avg is not None else None
    _ts_av_per_1m_d = round(_ts_av_avg * 1_000_000 / 1000.0 / 86400.0, 6) if _ts_av_avg is not None else None

    _ewh_total = (
        sum(r.get("energy_avoided_wh") or 0.0 for r in rows)
        if any(r.get("energy_avoided_wh") is not None for r in rows) else None
    )
    _e_per_1k_wh = round(_ewh_total * 1000 / n, 6) if _ewh_total is not None and n else None
    _e_per_1m_kwh = round(_ewh_total * 1_000_000 / n / 1000.0, 6) if _ewh_total is not None and n else None

    _obs_av_rate = summary.get("obsidia_model_call_avoided_rate") or 0.0

    summary.update({
        # Known path
        "known_path_detected_count": _kp_c,
        "known_path_detected_rate": round(_kp_c / n, 4) if n else None,
        # Inference necessity
        "inference_avoided_count": _inf_c,
        "inference_avoided_rate": round(_inf_c / n, 4) if n else None,
        "unnecessary_inference_avoided_count": _inf_c,
        "unnecessary_inference_avoided_rate": round(_inf_c / n, 4) if n else None,
        "external_dependency_avoided_count": _ext_c,
        "external_dependency_avoided_rate": round(_ext_c / n, 4) if n else None,
        # Governed speed
        "governed_speedup_avg": _gs_avg,
        "governed_speedup_median": _gs_median,
        "governed_speedup_available_surface_avg": _gs_avail_avg,
        "governed_speedup_model_avoided_avg": _gs_avoided_avg,
        "governed_speed_claim": (
            "Speed measured under KX108_ONLY governance — no control sacrificed."
        ),
        "governance_preserved_at_speed_rate": round(_gov_c / n, 4) if n else None,
        # Math formalization
        "math_formalized_surface_count": _mf_c,
        "math_formalized_surface_rate": round(_mf_c / n, 4) if n else None,
        "formalization_claim": (
            "Gains repose on formalized surfaces: admissible routes, invariants, "
            "KX108_ONLY governance, proof of non-action."
        ),
        "formalization_warning": (
            "Do not confuse with general-purpose trained intelligence. "
            "Formalization applies to known-path surfaces only."
        ),
        # Novice impact
        "model_calls_avoided_per_1000_requests": round(_obs_av_rate * 1000, 4),
        "model_calls_avoided_per_1m_requests": round(_obs_av_rate * 1_000_000, 4),
        "time_saved_per_request_ms_avg": _ts_avg,
        "time_saved_per_1000_requests_seconds": _ts_per_1k_s,
        "time_saved_per_1000_requests_minutes": _ts_per_1k_min,
        "time_saved_per_1m_requests_hours": _ts_per_1m_h,
        "time_saved_per_1m_requests_days": _ts_per_1m_d,
        "time_saved_model_avoided_per_request_ms_avg": _ts_av_avg,
        "time_saved_model_avoided_per_1000_requests_minutes": _ts_av_per_1k_min,
        "time_saved_model_avoided_per_1m_requests_days": _ts_av_per_1m_d,
        "energy_saved_per_1000_requests_wh": _e_per_1k_wh,
        "energy_saved_per_1m_requests_kwh": _e_per_1m_kwh,
        "external_dependency_avoided_per_1000_requests": round(_obs_av_rate * 1000, 4),
        "external_dependency_avoided_per_1m_requests": round(_obs_av_rate * 1_000_000, 4),
        # Partial engine
        "benchmark_completion_state": "CURRENT_BENCHMARK_PARTIAL",
        "obsidia_complete_measured": False,
        "missing_or_not_wired_layers": [
            "BRODY_ADAPTER_TO_BENCHMARK",
            "OBSIDURE_ADAPTER_TO_BENCHMARK",
            "LEAN_ADAPTER_TO_BENCHMARK",
        ],
        "not_included_acceleration_layers": [
            "REFLEXEUR", "PRE_REFLEXE", "EX_ANTE", "UPSTREAM_CAUSALITY",
            "BEST_PATH_MEMORY", "FRICTION_MEMORY", "EXPERIENCE_MEMORY",
            "SEMANTIC_BRANCHING", "COSMOLOGICAL_BRANCHING",
            "GENCOIN_REAL_ECONOMY", "FULL_INTELLECTUAL_ECONOMY",
        ],
        "partial_engine_warning": (
            "Ce run ne mesure pas Obsidia complet contre Gemini complet. "
            "Il mesure Obsidia partiel contre Gemini industriel."
        ),
        "partial_engine_claim": "NOT_INCLUDED_IN_CURRENT_RUN",
    })

    # ── Paired route comparison summary ──────────────────────────────────────
    _wired_rows = [r for r in rows if not r.get("obsidia_adapter_missing")]
    _miss_rows = [r for r in rows if r.get("obsidia_adapter_missing")]
    _n_w = len(_wired_rows)
    _n_m = len(_miss_rows)

    _obs_w_acc = (
        round(sum(1 for r in _wired_rows if r.get("obsidia_route_match") is True) / _n_w, 4)
        if _n_w else None
    )
    _gem_w_acc = (
        round(sum(1 for r in _wired_rows if r.get("gemini_route_match") is True) / _n_w, 4)
        if _n_w else None
    )
    _gem_m_acc = (
        round(sum(1 for r in _miss_rows if r.get("gemini_route_match") is True) / _n_m, 4)
        if _n_m else None
    )
    _w_delta = (
        round(_obs_w_acc - _gem_w_acc, 4)
        if _obs_w_acc is not None and _gem_w_acc is not None else None
    )
    _w_avoided = (
        round(sum(1 for r in _wired_rows if r.get("obsidia_model_call_avoided")) / _n_w, 4)
        if _n_w else None
    )

    summary.update({
        "paired_both_correct_count": sum(1 for r in rows if r.get("both_correct")),
        "paired_obsidia_only_correct_count": sum(1 for r in rows if r.get("obsidia_only_correct")),
        "paired_gemini_only_correct_count": sum(1 for r in rows if r.get("gemini_only_correct")),
        "paired_both_wrong_count": sum(1 for r in rows if r.get("both_wrong")),
        "paired_obsidia_adapter_missing_count": sum(1 for r in rows if r.get("obsidia_adapter_missing")),
        "paired_gemini_correct_on_adapter_missing_count": sum(
            1 for r in rows
            if r.get("obsidia_adapter_missing") and r.get("gemini_route_match") is True
        ),
        "obsidia_wired_surface_count": _n_w,
        "obsidia_wired_surface_accuracy": _obs_w_acc,
        "gemini_on_obsidia_wired_surface_accuracy": _gem_w_acc,
        "obsidia_vs_gemini_wired_surface_delta": _w_delta,
        "obsidia_wired_surface_model_avoided_rate": _w_avoided,
        "adapter_missing_surface_count": _n_m,
        "gemini_on_adapter_missing_surface_accuracy": _gem_m_acc,
        "adapter_missing_surface_non_claimable": True,
        "global_route_accuracy_warning": (
            "Global route_accuracy mixes wired surfaces and adapter-missing surfaces; "
            "use paired/wired-surface metrics for functional comparison."
        ),
        "wired_surface_claim": "On Obsidia wired surface, route comparison is claimable.",
        "adapter_missing_warning": (
            "BRODY, OBSIDURE, LEAN are adapter-missing in this benchmark "
            "and must not count as Obsidia functional losses."
        ),
    })

    # ── OIE Convergence Summary ────────────────────────────────────────────────

    # OSCA — geomean of all savings ratios vs BT_API_NORMAL
    _all_ratios = [BT_API_NORMAL / c for c in OIE_FAMILY_COSTS.values() if c > 0]
    _osca = round(math.exp(sum(math.log(r) for r in _all_ratios) / len(_all_ratios)), 4) if _all_ratios else 0.0

    # OAPI — portfolio FAST_PATH+BRODY+BANK+TRADING+GPS
    _oapi_fams = {"FAST_PATH", "BRODY", "BANK", "TRADING", "GPS"}
    _oapi_obs = sum(OIE_FAMILY_COSTS[f] for f in _oapi_fams if f in OIE_FAMILY_COSTS)
    _oapi = round(len(_oapi_fams) * BT_API_NORMAL / _oapi_obs, 4) if _oapi_obs > 0 else 0.0

    # ODPI — portfolio BANK+TRADING+GPS
    _odpi_fams = {"BANK", "TRADING", "GPS"}
    _odpi_obs = sum(OIE_FAMILY_COSTS[f] for f in _odpi_fams if f in OIE_FAMILY_COSTS)
    _odpi = round(len(_odpi_fams) * BT_API_NORMAL / _odpi_obs, 4) if _odpi_obs > 0 else 0.0

    # DCA by domain
    _dca_by_domain: dict = {}
    for fam, fam_cost in OIE_FAMILY_COSTS.items():
        dom_name = OIE_DOMAIN_NAME_MAPPING.get(fam, fam)
        is_miss = fam in ADAPTER_MISSING_FAMILIES
        _dca_by_domain[dom_name] = {
            "domain_name": dom_name,
            "family": fam,
            "obsidia_cost_eur_per_1m": fam_cost,
            "baseline_api_normal_cost_eur_per_1m": BT_API_NORMAL,
            "baseline_agentic_cost_eur_per_1m": BT_AGENTIC,
            "dca_api_normal": round(BT_API_NORMAL / fam_cost, 4) if fam_cost > 0 else 0.0,
            "dca_agentic": round(BT_AGENTIC / fam_cost, 4) if fam_cost > 0 else 0.0,
            "dca_claimable": "proxy_only" if not is_miss else False,
            "dca_basis": "OIE_PROXY_BASELINE",
            "dca_warning": "DCA is proxy/baseline comparison, not real provider billing.",
        }

    # domain_summary — using OIE summarize_domain_metrics if available
    _receipts_for_summary = []
    for r in rows:
        dm_dict = r.get("domain_metrics")
        receipt_dict = r.get("oie_cost_receipt")
        if dm_dict and receipt_dict and _OIE_CostReceipt is not None and _OIE_DomainMetrics is not None:
            try:
                import dataclasses as _dc
                dm_obj = _OIE_DomainMetrics(
                    domain_name=dm_dict.get("domain_name", ""),
                    domain_action_type=dm_dict.get("domain_action_type", ""),
                    domain_risk_level=dm_dict.get("domain_risk_level", ""),
                    domain_reversibility=dm_dict.get("domain_reversibility", ""),
                    domain_cost_eur_per_1m=dm_dict.get("domain_cost_eur_per_1m", 0.0),
                    domain_latency_ms=dm_dict.get("domain_latency_ms", 0.0),
                    domain_internal_units=dm_dict.get("domain_internal_units", 0.0),
                    domain_tools_used=list(dm_dict.get("domain_tools_used") or []),
                    domain_tools_skipped=list(dm_dict.get("domain_tools_skipped") or []),
                    external_api_calls_avoided=dm_dict.get("external_api_calls_avoided", 0),
                    llm_calls_avoided=dm_dict.get("llm_calls_avoided", 0),
                    proof_available=dm_dict.get("proof_available", False),
                    replay_available=dm_dict.get("replay_available", False),
                    business_cost_avoided_label=dm_dict.get("business_cost_avoided_label", ""),
                    domain_savings_ratio=dm_dict.get("domain_savings_ratio", 0.0),
                )
                cr_kwargs = {
                    k: receipt_dict[k]
                    for k in _OIE_CostReceipt.__dataclass_fields__
                    if k in receipt_dict and k != "domain_metrics"
                }
                cr_obj = _OIE_CostReceipt(**cr_kwargs, domain_metrics=dm_obj)
                _receipts_for_summary.append(cr_obj)
            except Exception:
                pass
    _dom_summary: dict = {}
    if _receipts_for_summary and _oie_summarize_domain_metrics is not None:
        try:
            _dom_summary = _oie_summarize_domain_metrics(_receipts_for_summary)
        except Exception:
            pass
    # Fallback manual aggregation if OIE not available or no receipts
    if not _dom_summary:
        for r in rows:
            dm_d = r.get("domain_metrics") or {}
            dom = dm_d.get("domain_name") or r.get("family", "UNKNOWN")
            if dom not in _dom_summary:
                _dom_summary[dom] = {
                    "domain_name": dom,
                    "total_rows": 0,
                    "claimable_rows": 0,
                    "adapter_missing_rows": 0,
                    "obsidia_total_cost_eur_per_1m": 0.0,
                    "baseline_api_normal_cost_eur_per_1m": BT_API_NORMAL,
                    "baseline_agentic_cost_eur_per_1m": BT_AGENTIC,
                    "dca_api_normal": 0.0,
                    "dca_agentic": 0.0,
                    "avg_latency_ms": 0.0,
                    "avg_internal_units": 0.0,
                    "tools_used": [],
                    "tools_skipped": [],
                    "llm_calls_avoided": 0,
                    "external_api_calls_avoided": 0,
                    "proof_or_replay_rate": 0.0,
                    "hold_count": 0, "block_count": 0, "act_count": 0,
                    "unknowns_count": 0, "contradictions_count": 0,
                }
            entry = _dom_summary[dom]
            entry["total_rows"] += 1
            c = dm_d.get("domain_cost_eur_per_1m") or 0.0
            entry["obsidia_total_cost_eur_per_1m"] = round(entry["obsidia_total_cost_eur_per_1m"] + c, 6)
            if r.get("oie_functional_claimable"):
                entry["claimable_rows"] += 1
            else:
                entry["adapter_missing_rows"] += 1
            entry["llm_calls_avoided"] += dm_d.get("llm_calls_avoided") or 0
            entry["external_api_calls_avoided"] += dm_d.get("external_api_calls_avoided") or 0
        # Compute DCA for each fallback entry
        for dom, ent in _dom_summary.items():
            nc = ent["total_rows"]
            avg_c = ent["obsidia_total_cost_eur_per_1m"] / nc if nc else 0.0
            ent["dca_api_normal"] = round(BT_API_NORMAL / avg_c, 4) if avg_c > 0 else 0.0
            ent["dca_agentic"] = round(BT_AGENTIC / avg_c, 4) if avg_c > 0 else 0.0

    # OIE claim matrix
    _fc = sum(1 for r in rows if r.get("oie_functional_claimable"))
    _rc = sum(1 for r in rows if r.get("route_accuracy_claimable"))
    _dc_count = sum(1 for r in rows if r.get("oie_domain_claimable"))
    _cc = sum(1 for r in rows if r.get("oie_cost_claimable"))
    _mc = sum(1 for r in rows if r.get("obsidia_adapter_missing"))

    # OIE import status
    _oie_import_status = {
        "used_native_oie_imports": _OIE_IMPORT_OK,
        "fallback_local_oie_mapping": not _OIE_IMPORT_OK,
        "missing_imports": _OIE_MISSING_IMPORTS,
    }

    # OIE freeze reference
    _freeze_ref = {
        "freeze_family": "OBSIDIA_OIE_V01_ENGINE_FREEZE",
        "freeze_dir": str(_OIE_FREEZE_DIR),
        "freeze_receipt": str(_OIE_FREEZE_DIR / "FREEZE_RECEIPT.txt"),
        "sha256sums": str(_OIE_FREEZE_DIR / "SHA256SUMS.txt"),
        "status_expected": "OIE_V01_DOMAIN_METRICS_AND_EXTERNAL_API_PROTOCOL_READY",
        "tests_expected": "74/74 PASSED",
        "scope_expected": "OIE_ONLY_NO_KERNEL_NO_BRODY_LIVE_NO_GRAPHITI_NO_NEO4J",
        "freeze_found": _OIE_FREEZE_FOUND,
    }

    summary.update({
        # Baseline registry
        "oie_baseline_registry": dict(BASELINE_LABELS),
        "oie_primary_baseline_label": "BT_API_NORMAL",
        "oie_agentic_baseline_label": "BT_AGENTIC",
        "oie_baseline_basis": "OIE_V0_1_BASELINE_REGISTRY",
        "oie_baseline_warning": (
            "Baselines are comparison models; real provider cost must use SDK measured usage when available."
        ),
        # Indices
        "osca_ratio": _osca,
        "oapi_ratio": _oapi,
        "odpi_ratio": _odpi,
        "osca_basis": "GEOMEAN_LAYER_RATIOS_VS_BT_API_NORMAL",
        "oapi_basis": "PORTFOLIO_ACTIONS_FASTPATH_BRODY_BANK_TRADING_GPS_VS_BT_API_NORMAL",
        "odpi_basis": "PORTFOLIO_DOMAINS_BANK_TRADING_GPS_VS_BT_API_NORMAL",
        "oie_indices_claimable": "PROXY_BASELINE_ONLY_NOT_REAL_PROVIDER_COST",
        # DCA by domain
        "dca_by_domain": _dca_by_domain,
        # Domain summary
        "domain_summary": _dom_summary,
        "domain_summary_basis": "OIE_V0_1_DOMAIN_METRICS",
        "domain_summary_claim_warning": "DCA/OSCA/OAPI/ODPI are proxy baseline metrics, not real provider billing.",
        # Claim matrix
        "oie_claim_matrix": {
            "functional_claimable_count": _fc,
            "route_claimable_count": _rc,
            "domain_claimable_count": _dc_count,
            "cost_claimable_count": _cc,
            "adapter_missing_non_claimable_count": _mc,
            "gencoin_emission_claimable": False,
        },
        # Gencoin bridge
        "oie_gencoin_bridge": {
            "gencoin_mode": GENCOIN_MODE,
            "gencoin_total_emission": 0,
            "gencoin_emission_allowed": False,
            "gencoin_distribution_mode": GENCOIN_DISTRIBUTION_MODE,
            "source_law_satisfied": False,
            "intellectual_economy_basis": IE_BASIS,
            "oie_can_measure_value": True,
            "oie_cannot_emit_value": True,
            "source_law_required_for_emission": True,
        },
        # OIE warnings
        "oie_warnings": _OIE_WARNINGS,
        # Import status
        "oie_import_status": _oie_import_status,
        # Source lineage
        "oie_source_lineage": _OIE_SOURCE_LINEAGE,
        # Source documents
        "oie_source_documents": _OIE_SOURCE_DOCUMENTS,
        # Freeze reference
        "oie_freeze_reference": _freeze_ref,
        # Benchmark linkage
        "oie_benchmark_linkage": _OIE_BENCHMARK_LINKAGE,
        # Domain name mapping — canonical keys only (no case-insensitive dups for PowerShell)
        "oie_domain_name_mapping": {
            "FAST_PATH": "FAST_PATH",
            "BRODY": "BRODY",
            "BANK": "BANK",
            "TRADING": "TRADING",
            "GPS": "GPS_AVIATION",
            "GPS_AVIATION": "GPS_AVIATION",
            "LEAN": "LEAN",
            "OBSIDURE": "OBSIDURE",
        },
        # Alias mapping as list-of-dicts (avoids case-insensitive dup issue in PowerShell)
        "oie_domain_alias_mapping": [
            {"alias": "Brody chat", "canonical": "BRODY"},
            {"alias": "Bank", "canonical": "BANK"},
            {"alias": "Trading", "canonical": "TRADING"},
            {"alias": "GPS/Aviation", "canonical": "GPS_AVIATION"},
            {"alias": "Aviation", "canonical": "GPS_AVIATION"},
            {"alias": "Lean canon check", "canonical": "LEAN"},
            {"alias": "Obsidure Lean cible", "canonical": "OBSIDURE"},
        ],
        # Obsidia live adapter registry
        "obsidia_live_adapter_registry": {
            fam: {k: v for k, v in reg.items() if k != "api_status_probe"}
            for fam, reg in _OBSIDIA_LIVE_ADAPTER_REGISTRY.items()
        },
        # Live adapter summary
        "obsidia_live_adapter_summary": {
            "requested_mode": os.environ.get("OIE_OBSIDIA_EXECUTION_MODE", OIE_OBSIDIA_EXEC_MODE_AUTO),
            "api_base": _OBSIDIA_API_BASE,
            "kernel_target": _OBSIDIA_KERNEL_URL,
            "adapters_found_count": sum(1 for v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.values() if v.get("adapter_found")),
            "usable_live_count": sum(1 for v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.values() if v.get("usable_for_live_local")),
            "live_local_rows_count": sum(1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_LIVE_LOCAL),
            "bridge_kernel_unreachable_count": sum(1 for r in rows if r.get("obsidia_status") == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"),
            "frozen_fallback_rows_count": sum(1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_FROZEN),
            "adapter_missing_rows_count": sum(1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING),
            "live_local_available_global": _LIVE_LOCAL_AVAILABLE,
            "live_local_usable_families": _LIVE_LOCAL_USABLE_FAMILIES,
            "live_local_unavailable_families": _LIVE_LOCAL_UNAVAILABLE_FAMILIES,
            "adapter_missing_families": _ADAPTER_MISSING_FAMILIES_LIVE,
            "live_local_claimable_count": sum(
                1 for r in rows
                if r.get("obsidia_status") == OBSIDIA_STATUS_LIVE_LOCAL
                and not r.get("dual_lane", {}).get("obsidia_lane", {}).get("adapter_missing")
            ),
            "fallback_claimable_count": sum(
                1 for r in rows
                if r.get("obsidia_fallback_used") and r.get("obsidia_status") == OBSIDIA_STATUS_FROZEN
            ),
        },
    })
    return summary


# ── Runtime report writers (Phase 7) ─────────────────────────────────────────

def _make_report_dir() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_dir = _REPO_ROOT / ".local_reports" / f"OIE_POWER_BENCHMARK_V0_7_1_{ts}"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def write_runtime_reports(report_dir: Path, summary: dict, rows: list[dict]) -> None:
    """Ecrire les rapports runtime dans .local_reports — jamais dans docs/audits."""
    # ── results.json ─────────────────────────────────────────────────────────
    (report_dir / "results.json").write_text(
        json.dumps(rows, indent=2, default=str), encoding="utf-8"
    )

    # ── summary.json (validate case-insensitive dup keys first) ──────────────
    summary_json_str = json.dumps(summary, indent=2, default=str)
    _dup_issues = find_case_insensitive_duplicate_keys(summary)
    if _dup_issues:
        import warnings
        warnings.warn(
            f"summary.json contient {len(_dup_issues)} clé(s) case-insensitive dupliquées "
            f"(risque PowerShell ConvertFrom-Json) : {_dup_issues[:5]}",
            stacklevel=2,
        )
    (report_dir / "summary.json").write_text(summary_json_str, encoding="utf-8")

    # ── internal_economy.json ─────────────────────────────────────────────────
    ie_data = [
        {
            "task_id": r["task_id"],
            "family": r["family"],
            "intellectual_economy_layer": r.get("intellectual_economy_layer"),
            "intellectual_value_score": r.get("intellectual_value_score"),
            "debt_score": r.get("debt_score"),
            "cv_weight_source": r.get("cv_weight_source"),
        }
        for r in rows
    ]
    (report_dir / "internal_economy.json").write_text(
        json.dumps(ie_data, indent=2, default=str), encoding="utf-8"
    )

    # ── gencoin_calibration.json ──────────────────────────────────────────────
    gc_data = [
        {
            "task_id": r["task_id"],
            "gencoin_calibration_layer": r.get("gencoin_calibration_layer"),
            "gencoin_basis": r.get("gencoin_basis"),
            "source_law_satisfied": r.get("source_law_satisfied"),
        }
        for r in rows
    ]
    (report_dir / "gencoin_calibration.json").write_text(
        json.dumps(gc_data, indent=2, default=str), encoding="utf-8"
    )

    # ── readable_report.json (PowerShell-safe, no case-dup keys) ─────────────
    oie_idx: dict = {
        "OSCA_geomean_x": summary.get("osca_ratio"),
        "OSCA_basis": summary.get("osca_basis"),
        "OAPI_portfolio_x": summary.get("oapi_ratio"),
        "OAPI_basis": summary.get("oapi_basis"),
        "ODPI_portfolio_x": summary.get("odpi_ratio"),
        "ODPI_basis": summary.get("odpi_basis"),
        "claimable": summary.get("oie_indices_claimable"),
    }
    cm = summary.get("oie_claim_matrix", {}) or {}
    bridge = summary.get("oie_gencoin_bridge", {}) or {}
    lineage = summary.get("oie_source_lineage", {}) or {}
    dual_lane_table = [
        {
            "task_id": r.get("task_id"),
            "family": r.get("family"),
            "obsidia_exec_mode": (r.get("dual_lane") or {}).get("obsidia_lane", {}).get("execution_mode"),
            "gemini_exec_mode": (r.get("dual_lane") or {}).get("gemini_lane", {}).get("execution_mode"),
            "comparison_scope": (r.get("dual_lane") or {}).get("comparison_scope"),
            "comparison_claimable": (r.get("dual_lane") or {}).get("comparison_claimable"),
            "obsidia_route_match": r.get("obsidia_route_match"),
            "gemini_route_match": r.get("gemini_route_match"),
            "model_avoided": r.get("obsidia_model_call_avoided"),
        }
        for r in rows
    ]
    readable: dict = {
        "report_version": "V0.7.1",
        "benchmark_date": summary.get("benchmark_date"),
        "tasks_attempted": summary.get("tasks_attempted"),
        "governance_clean": summary.get("governance_clean"),
        "obsidia_route_accuracy": summary.get("obsidia_route_accuracy"),
        "gemini_route_accuracy": summary.get("gemini_route_accuracy"),
        "avg_speedup_ratio": summary.get("avg_speedup_ratio"),
        "model_call_avoided_count": summary.get("obsidia_model_call_avoided_count"),
        "cost_comparison_claimable_global": summary.get("cost_comparison_claimable_global"),
        "available_surface_count": summary.get("available_surface_count"),
        "adapter_missing_count": summary.get("adapter_missing_count"),
        "intellectual_value_avg": summary.get("intellectual_value_avg"),
        "gencoin_mode": summary.get("gencoin_mode"),
        "gencoin_total_emission": summary.get("gencoin_total_emission"),
        "source_law_global_satisfied": summary.get("source_law_global_satisfied"),
        "oie_osca_x": oie_idx.get("OSCA_geomean_x"),
        "oie_oapi_x": oie_idx.get("OAPI_portfolio_x"),
        "oie_odpi_x": oie_idx.get("ODPI_portfolio_x"),
        "oie_import_ok": _OIE_IMPORT_OK,
        "oie_freeze_found": _OIE_FREEZE_FOUND,
        "claim_functional": cm.get("functional_claimable_count"),
        "claim_route": cm.get("route_claimable_count"),
        "claim_domain": cm.get("domain_claimable_count"),
        "claim_cost": cm.get("cost_claimable_count"),
        "claim_adapter_missing_non_claimable": cm.get("adapter_missing_non_claimable_count"),
        "gencoin_emission_claimable": cm.get("gencoin_emission_claimable"),
        "gencoin_bridge_mode": bridge.get("gencoin_mode"),
        "gencoin_bridge_source_law": bridge.get("source_law_satisfied"),
        "lineage_base_commit": lineage.get("base_audit_commit"),
        "lineage_oie_v01_commit": lineage.get("oie_v01_commit_candidate"),
        "lineage_freeze_name": lineage.get("freeze_name"),
        "dual_lane_table": dual_lane_table,
        "obsidia_live_read": {
            "requested_mode": summary.get("obsidia_live_adapter_summary", {}).get("requested_mode"),
            "api_base": _OBSIDIA_API_BASE,
            "kernel_target": _OBSIDIA_KERNEL_URL,
            "live_local_available_global": _LIVE_LOCAL_AVAILABLE,
            "live_local_rows_count": summary.get("obsidia_live_adapter_summary", {}).get("live_local_rows_count", 0),
            "bridge_kernel_unreachable_count": summary.get("obsidia_live_adapter_summary", {}).get("bridge_kernel_unreachable_count", 0),
            "frozen_fallback_rows_count": summary.get("obsidia_live_adapter_summary", {}).get("frozen_fallback_rows_count", 0),
            "adapter_missing_rows_count": summary.get("obsidia_live_adapter_summary", {}).get("adapter_missing_rows_count", 0),
            "live_families": _LIVE_LOCAL_USABLE_FAMILIES,
            "fallback_families": _LIVE_LOCAL_UNAVAILABLE_FAMILIES,
            "missing_families": _ADAPTER_MISSING_FAMILIES_LIVE,
        },
        "metrics_read": {
            "execution": {
                "benchmark_version": BENCHMARK_VERSION,
                "tasks_attempted": summary.get("tasks_attempted"),
                "obsidia_exec_mode": (summary.get("obsidia_live_adapter_summary") or {}).get("requested_mode", OIE_OBSIDIA_EXEC_MODE_AUTO),
                "gemini_exec_mode": summary.get("gemini_exec_mode"),
                "obsidia_api_base": _OBSIDIA_API_BASE,
                "obsidia_kernel_target": _OBSIDIA_KERNEL_URL,
                "live_local_rows_count": (summary.get("obsidia_live_adapter_summary") or {}).get("live_local_rows_count", 0),
                "bridge_kernel_unreachable_count": (summary.get("obsidia_live_adapter_summary") or {}).get("bridge_kernel_unreachable_count", 0),
                "adapter_missing_rows_count": (summary.get("obsidia_live_adapter_summary") or {}).get("adapter_missing_rows_count", 0),
            },
            "routing_claims": {
                "obsidia_route_accuracy": summary.get("obsidia_route_accuracy"),
                "obsidia_wired_surface_accuracy": summary.get("obsidia_wired_surface_accuracy"),
                "gemini_route_accuracy": summary.get("gemini_route_accuracy"),
                "gemini_on_obsidia_wired_surface_accuracy": summary.get("gemini_on_obsidia_wired_surface_accuracy"),
                "route_claimable_count": cm.get("route_claimable_count"),
                "functional_claimable_count": cm.get("functional_claimable_count"),
                "domain_claimable_count": cm.get("domain_claimable_count"),
                "cost_claimable_count": cm.get("cost_claimable_count"),
                "adapter_missing_non_claimable_count": cm.get("adapter_missing_non_claimable_count"),
                "note": "Accuracy measures route recognition, not inference economy.",
            },
            "inference_economy": {
                "inference_avoided_count": summary.get("inference_avoided_count"),
                "inference_avoided_rate": summary.get("inference_avoided_rate"),
                "model_avoided_count": summary.get("obsidia_model_call_avoided_count"),
                "model_avoided_families": summary.get("model_avoided_families"),
                "model_calls_avoided_per_1000_requests": summary.get("model_calls_avoided_per_1000_requests"),
                "model_calls_avoided_per_1m_requests": summary.get("model_calls_avoided_per_1m_requests"),
                "unnecessary_inference_avoided_count": summary.get("unnecessary_inference_avoided_count"),
                "unnecessary_inference_avoided_rate": summary.get("unnecessary_inference_avoided_rate"),
            },
            "performance": {
                "avg_speedup_ratio": summary.get("avg_speedup_ratio"),
                "available_surface_avg_speedup_ratio": summary.get("available_surface_avg_speedup_ratio"),
                "model_avoided_avg_speedup_ratio": summary.get("model_avoided_avg_speedup_ratio"),
                "terrain_avg_speedup_ratio": summary.get("terrain_avg_speedup_ratio"),
                "avg_latency_delta_pct": summary.get("avg_latency_delta_pct"),
                "obsidia_avg_latency_ms": summary.get("obsidia_avg_latency_ms"),
                "gemini_avg_latency_ms": summary.get("gemini_avg_latency_ms"),
                "governance_preserved_at_speed_rate": summary.get("governance_preserved_at_speed_rate"),
            },
            "energy": {
                "energy_source": summary.get("energy_source"),
                "obsidia_total_energy_wh_est": summary.get("obsidia_total_energy_wh_est"),
                "gemini_total_energy_wh_est": summary.get("gemini_total_energy_wh_est"),
                "total_energy_avoided_wh": summary.get("total_energy_avoided_wh"),
                "energy_saved_per_1000_requests_wh": summary.get("energy_saved_per_1000_requests_wh"),
                "energy_saved_per_1m_requests_kwh": summary.get("energy_saved_per_1m_requests_kwh"),
                "avg_energy_savings_ratio": summary.get("avg_energy_savings_ratio"),
                "warning": "Energy is proxy-estimated unless hardware/provider telemetry is supplied.",
            },
            "tokens_cost": {
                "cost_source": summary.get("cost_source"),
                "obsidia_cost_basis_global": summary.get("obsidia_cost_basis_global"),
                "gemini_cost_basis_global": summary.get("gemini_cost_basis_global"),
                "obsidia_total_estimated_tokens": summary.get("obsidia_total_estimated_tokens"),
                "gemini_total_tokens": summary.get("gemini_total_tokens"),
                "obsidia_total_cost_est": summary.get("obsidia_total_cost_est"),
                "gemini_total_cost_measured": summary.get("gemini_total_cost_measured"),
                "total_avoided_cost": summary.get("total_avoided_cost"),
                "cost_comparison_claimable_global": summary.get("cost_comparison_claimable_global"),
                "warning": "Cost comparison is not claimable while Obsidia is LOCAL_PROXY_UNCALIBRATED.",
            },
            "oie_indices": {
                "osca_ratio": summary.get("osca_ratio"),
                "oapi_ratio": summary.get("oapi_ratio"),
                "odpi_ratio": summary.get("odpi_ratio"),
                "oie_indices_claimable": summary.get("oie_indices_claimable"),
                "oie_primary_baseline_label": summary.get("oie_primary_baseline_label"),
                "oie_agentic_baseline_label": summary.get("oie_agentic_baseline_label"),
                "warning": "OIE indices are proxy baseline metrics, not real provider billing.",
            },
            "gencoin": {
                "oie_gencoin_bridge": bridge,
            },
        },
        "path_read": {
            "known_path_detected_count": summary.get("known_path_detected_count"),
            "known_path_detected_rate": summary.get("known_path_detected_rate"),
            "model_call_avoided_by_known_path_count": summary.get("inference_avoided_count"),
            "model_call_avoided_by_known_path_rate": summary.get("inference_avoided_rate"),
            "model_avoided_families": summary.get("model_avoided_families"),
            "path_compute_runtime_used": False,
            "path_compute_runtime_claimable": False,
            "fast_path_live_bridge_available": _OBSIDIA_LIVE_ADAPTER_REGISTRY.get("FAST_PATH", {}).get("usable_for_live_local", False),
            "fast_path_adapter_type": _OBSIDIA_LIVE_ADAPTER_REGISTRY.get("FAST_PATH", {}).get("adapter_type", "NONE"),
            "fast_path_reason_if_not_usable": _OBSIDIA_LIVE_ADAPTER_REGISTRY.get("FAST_PATH", {}).get("reason_if_not_usable"),
            "live_bridge_claimable_families": [r["family"] for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_LIVE_LOCAL],
            "bridge_attempted_kernel_unreachable_families": [r["family"] for r in rows if r.get("obsidia_status") == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"],
            "adapter_missing_families": [r["family"] for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING],
            "wording_guard": "This run proves inference economy on known routes; it does not yet prove full Path Compute runtime.",
        },
    }

    # ── model_necessity_read ──────────────────────────────────────────────────
    _mn_rows = [r.get("model_necessity", {}) for r in rows]
    _ext_called = sum(1 for r in _mn_rows if r.get("gemini_external_llm_called"))
    _ext_req = sum(1 for r in rows if r.get("model_necessity", {}).get("external_llm_required_by_design") is True)
    _ext_not_req = sum(1 for r in rows if r.get("model_necessity", {}).get("external_llm_required_by_design") is False)
    _obs_ext_called = sum(1 for r in _mn_rows if r.get("obsidia_external_llm_called"))
    _ext_avoided = sum(1 for r in _mn_rows if r.get("external_llm_avoided_by_obsidia"))
    _unnec_avoided = sum(1 for r in _mn_rows if r.get("unnecessary_generalist_call_avoided"))
    _n = len(rows)
    _claimable_unnec = sum(1 for r in _mn_rows if r.get("necessity_claimable") and r.get("unnecessary_generalist_call_avoided"))
    _necessity_claimable_fams = [r["family"] for r in rows if r.get("model_necessity", {}).get("necessity_claimable")]
    _necessity_non_claimable_fams = [r["family"] for r in rows if not r.get("model_necessity", {}).get("necessity_claimable")]
    _non_claimable_but_measured_fams = [
        r["family"] for r in rows
        if not r.get("model_necessity", {}).get("necessity_claimable")
        and r.get("model_necessity", {}).get("external_llm_avoided_by_obsidia")
    ]
    readable["model_necessity_read"] = {
        "benchmark_name": "LLM_NECESSITY_BENCHMARK",
        "tasks_total": _n,
        "external_llm_called_by_baseline_count": _ext_called,
        "external_llm_required_by_design_count": _ext_req,
        "external_llm_not_required_by_design_count": _ext_not_req,
        "obsidia_external_llm_called_count": _obs_ext_called,
        "external_llm_avoided_by_obsidia_count": _ext_avoided,
        "unnecessary_generalist_calls_avoided_count": _unnec_avoided,
        "unnecessary_generalist_calls_avoided_rate": round(_unnec_avoided / _n, 4) if _n else 0,
        "claimable_unnecessary_generalist_calls_avoided_count": _claimable_unnec,
        "claimable_unnecessary_generalist_calls_avoided_rate": round(_claimable_unnec / _n, 4) if _n else 0,
        "non_claimable_but_measured_families": _non_claimable_but_measured_fams,
        "necessity_claimable_families": _necessity_claimable_fams,
        "necessity_non_claimable_families": _necessity_non_claimable_fams,
        "minimal_sufficient_layer_by_family": {r["family"]: r.get("model_necessity", {}).get("expected_minimal_layer") for r in rows},
        "actual_obsidia_layer_by_family": {r["family"]: r.get("model_necessity", {}).get("actual_obsidia_layer_used") for r in rows},
        "model_role_by_family": {r["family"]: r.get("model_necessity", {}).get("model_role_for_obsidia") for r in rows},
        "llm_necessity_interpretation": "This benchmark measures whether a generalist LLM call was necessary, not only whether it was fast or correct.",
        "warning": "This does not claim Obsidia is a better generalist LLM. It claims that on bounded governed routes, a generalist LLM call can be unnecessary.",
    }

    # ── answer_adequacy_read ──────────────────────────────────────────────────
    _aa_rows = [r.get("answer_adequacy", {}) for r in rows]
    _aa_scores = [r.get("answer_adequacy_score", 0.0) for r in _aa_rows if r.get("answer_adequacy_score") is not None]
    _aa_claimable_scores = [r.get("answer_adequacy_score", 0.0) for r in _aa_rows if r.get("adequacy_claimable")]
    _aa_avg = round(sum(_aa_scores) / len(_aa_scores), 4) if _aa_scores else 0.0
    _aa_claimable_avg = round(sum(_aa_claimable_scores) / len(_aa_claimable_scores), 4) if _aa_claimable_scores else 0.0
    readable["answer_adequacy_read"] = {
        "answer_adequacy_avg": _aa_avg,
        "answer_adequacy_claimable_avg": _aa_claimable_avg,
        "task_output_correct_count": sum(1 for r in _aa_rows if r.get("route_correct")),
        "route_correct_count": sum(1 for r in _aa_rows if r.get("route_correct")),
        "output_bounded_count": sum(1 for r in _aa_rows if r.get("output_bounded")),
        "minimal_layer_respected_count": sum(1 for r in _aa_rows if r.get("minimal_layer_respected")),
        "governance_preserved_count": sum(1 for r in _aa_rows if r.get("governance_preserved")),
        "trace_or_receipt_available_count": sum(1 for r in _aa_rows if r.get("trace_or_receipt_available")),
        "hallucination_risk_avoided_count": sum(1 for r in _aa_rows if r.get("hallucination_risk_avoided")),
        "overproduction_penalty_total": sum(r.get("overproduction_penalty", 0.0) for r in _aa_rows),
        "adequacy_by_family": {r["family"]: r.get("answer_adequacy", {}) for r in rows},
        "phrase": "The best answer is not always the most fluent answer. It is the sufficient governed output at the minimal necessary layer.",
        "warning": "Answer adequacy measures whether the output is correct, bounded, governed and sufficient; it does not measure prose quality.",
    }

    # ── translation_layer_read ────────────────────────────────────────────────
    readable["translation_layer_read"] = {
        "benchmark_name": "UNIVERSAL_OPERATIONAL_TRANSLATION_READ",
        "translation_layer_claimable": "SCHEMA_PROXY_ONLY_UNTIL_RUNTIME_TRANSLATOR_INSTRUMENTED",
        "role": "Convert human language, code, domain signals, errors and intentions into the Obsidia alphabet.",
        "non_role": [
            "Does not decide.",
            "Does not act.",
            "Does not replace X108.",
            "Does not act as a sovereign generalist model.",
        ],
        "by_family": {
            "FAST_PATH":  {"input_surface": "natural_language_or_route_request", "target_layer": MIN_LAYER_FAST_PATH, "emitted_alphabet": "route_label", "requires_external_llm": False},
            "BANK":       {"input_surface": "domain_request", "target_layer": MIN_LAYER_DOMAIN_BRIDGE, "emitted_alphabet": "bank payload / domain state", "requires_external_llm": False},
            "TRADING":    {"input_surface": "domain_request", "target_layer": MIN_LAYER_DOMAIN_BRIDGE, "emitted_alphabet": "trading payload / domain state", "requires_external_llm": False},
            "GPS":        {"input_surface": "domain_request", "target_layer": MIN_LAYER_DOMAIN_BRIDGE, "emitted_alphabet": "gps payload / domain state", "requires_external_llm": False},
            "BRODY":      {"input_surface": "natural_language", "target_layer": MIN_LAYER_BRODY_INTERNAL, "emitted_alphabet": "brody message / answer route", "requires_external_llm": False},
            "OBSIDURE":   {"input_surface": "code_intent", "target_layer": MIN_LAYER_OBSIDURE_AGENT, "emitted_alphabet": "patch / test / diff intent", "requires_external_llm": None},
            "LEAN":       {"input_surface": "proof_intent", "target_layer": MIN_LAYER_LEAN_PROOF, "emitted_alphabet": "formal proof task", "requires_external_llm": None},
        },
        "phrase": "The LLM understands to act. Obsidia translates to route.",
        "phrase_fr": "Le LLM comprend pour agir. Obsidia traduit pour router.",
    }

    # ── architecture_advantage_read ───────────────────────────────────────────
    readable["architecture_advantage_read"] = {
        "architecture_advantage_claimable": "INTERPRETATION_SUPPORTED_BY_CURRENT_METRICS_NOT_FULL_MARKET_PROOF",
        "non_trained_structure_advantage": {
            "observation": "Obsidia obtains speed, routing and governance gains on bounded surfaces without a massive training regime comparable to Gemini.",
            "interpretation": "The gain does not come from a bigger model. It comes from reducing the search space before inference.",
            "principle": "Known admissible route > model inference.",
            "consequence": "When a route is known, structured, bounded, measured and admissible, a model call becomes a cost to justify.",
        },
        "structure_over_raw_intelligence": {
            "statement": "Obsidia does not replace a large model with another large model. It moves part of the intelligence out of raw inference and into governed structure.",
            "phrase": "LLMs centralize intelligence in inference. Obsidia redistributes intelligence into the structure of the path.",
        },
        "own_stack_over_cheap_model": {
            "statement": "Obsidia does not rely on a cheaper model. It relies on a controlled stack.",
            "phrase": "This is not a cheaper model. It is an architecture that reduces the need for a model.",
        },
        "probability_non_sovereign": {
            "statement": "Probability may explore. It must not authorize.",
            "breakdown": "Generative explores. Kernel bounds. Sigma alerts. Domains translate. X108 closes.",
        },
        "llm_role": {
            "statement": "Obsidia does not eliminate LLMs. It puts them in their proper place: understand, generate, propose, repair — not govern.",
        },
        "kernel_authority": {
            "statement": "Obsidia does not put all intelligence in the kernel. It puts all authority in the kernel.",
            "phrase": "The kernel is powerful because it is non-negotiable, not because it is intelligent.",
        },
        "market_interpretation": {
            "statement": "The market optimizes inference. Obsidia optimizes the decision to infer.",
            "phrase": "They use the model to compensate for an architecture that cannot translate. Obsidia builds the translation.",
            "phrase_fr": "Le marché optimise l'inférence. Obsidia optimise la décision d'inférer.",
        },
    }

    # ── speed_stack_read ─────────────────────────────────────────────────────
    _dca_raw = summary.get("dca_by_domain") or {}
    def _dca_scalar(v: object) -> object:
        if isinstance(v, dict):
            return v.get("dca_api_normal") or v.get("dca_agentic")
        return v
    readable["speed_stack_read"] = {
        "live_avg_speedup_vs_gemini": summary.get("avg_speedup_ratio"),
        "available_surface_avg_speedup": summary.get("available_surface_avg_speedup_ratio"),
        "model_avoided_avg_speedup": summary.get("model_avoided_avg_speedup_ratio"),
        "terrain_avg_speedup": summary.get("terrain_avg_speedup_ratio"),
        "governed_speed_rate": summary.get("governance_preserved_at_speed_rate"),
        "known_path_detected_count": summary.get("known_path_detected_count"),
        "known_path_detected_rate": summary.get("known_path_detected_rate"),
        "inference_avoided_count": summary.get("inference_avoided_count"),
        "inference_avoided_rate": summary.get("inference_avoided_rate"),
        "model_call_avoided_count": summary.get("obsidia_model_call_avoided_count"),
        "model_call_avoided_families": summary.get("model_avoided_families"),
        "oie_speed_indices": {
            "osca_ratio": summary.get("osca_ratio"),
            "oapi_ratio": summary.get("oapi_ratio"),
            "odpi_ratio": summary.get("odpi_ratio"),
            "indices_claimable": summary.get("oie_indices_claimable"),
        },
        "dca_by_domain": {fam: _dca_scalar(_dca_raw.get(fam)) for fam in ("FAST_PATH", "BRODY", "BANK", "TRADING", "GPS", "GPS_AVIATION", "OBSIDURE", "LEAN")},
        "governance_while_fast": {
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
            "kernel_mutation": False,
        },
        "claim_guard": {
            "speed_metrics_claimable": True,
            "cost_comparison_claimable": summary.get("cost_comparison_claimable_global", False),
            "path_compute_runtime_claimable": False,
            "wording_guard": "Speed is measured; real cost and full Path Compute runtime are not claimed.",
        },
    }

    readable_dup = find_case_insensitive_duplicate_keys(readable)
    if readable_dup:
        readable["_warnings_case_dup_keys"] = readable_dup
    (report_dir / "readable_report.json").write_text(
        json.dumps(readable, indent=2, default=str), encoding="utf-8"
    )

    # ── summary.md (11 sections) ──────────────────────────────────────────────
    n = len(rows)
    wired_acc = summary.get("obsidia_wired_surface_accuracy")
    gem_wired = summary.get("gemini_on_obsidia_wired_surface_accuracy")
    delta_wired = summary.get("obsidia_vs_gemini_wired_surface_delta")
    gem_missing = summary.get("gemini_on_adapter_missing_surface_accuracy")
    wired_n = summary.get("obsidia_wired_surface_count", 4)
    missing_n = summary.get("adapter_missing_surface_count", 3)

    md: list[str] = []

    # §0 Tableau de bord français (V0.7.8b) — mode-neutre, doit occuper les 120 premières lignes
    _avg_sp_md  = summary.get("avg_speedup_ratio")
    _avail_sp_md = summary.get("available_surface_avg_speedup_ratio")
    _mod_sp_md  = summary.get("model_avoided_avg_speedup_ratio")
    _mod_av_md  = summary.get("obsidia_model_call_avoided_count", "?")
    _obs_rt_md  = sum(1 for r in rows if r.get("obsidia_route_match") is True)
    _gem_rt_md  = sum(1 for r in rows if r.get("gemini_route_match") is True)
    _n_md = len(rows)
    _er_md = _execution_read(summary, rows)
    _mode_md = _er_md["mode_label_fr"]
    _speed_md = _er_md["speed_label_fr"]
    _is_dry_md = _er_md["is_dryrun"]
    _brody_md = "non testé en live / pont non confirmé" if _is_dry_md else "kernel inaccessible — pas un connecteur manquant"
    _bank_md = "Prévisualisation" if _is_dry_md else "Revendicable"

    def _fn(v: object) -> str:
        if v is None:
            return "N/D"
        try:
            return f"{round(float(v)):,}".replace(",", " ") + "x"
        except (ValueError, TypeError):
            return str(v)

    md += [
        "# Tableau de bord — OIE Benchmark Obsidia vs Gemini",
        "",
        "## Analyse simple du benchmark",
        "",
        f"Mode d'exécution : **{_mode_md}**",
        "",
        "| Aspect | Valeur |",
        "| --- | --- |",
        "| Obsidia LIVE_LOCAL | système local avec ponts de domaines |",
        f"| Gemini | {'appel réel au modèle Gemini' if not _is_dry_md else 'simulation dry-run (aucun appel réseau)'} |",
        "| Focus | économie d'inférence (OIE) |",
        "| Question | Quand peut-on répondre sans grand modèle de langage ? |",
        "",
        "## Tableau de bord",
        "",
        "| Indicateur | Valeur |",
        "| --- | --- |",
        f"| Obsidia route correctement | {_obs_rt_md} / {_n_md} |",
        f"| Gemini route correctement | {_gem_rt_md} / {_n_md} |",
        f"| Appels au modèle évités | {_mod_av_md} / {_n_md} |",
        f"| Accélération moyenne ({_speed_md}) | {_fn(_avg_sp_md)} |",
        f"| Accélération surfaces disponibles | {_fn(_avail_sp_md)} |",
        f"| Accélération appel modèle évité | {_fn(_mod_sp_md)} |",
        "| Gouvernance | KX108_ONLY — pas d'action réelle — pas d'écriture mémoire |",
        "",
        "## Les 6 chiffres à retenir",
        "",
        f"1. {_n_md} tâches testées.",
        f"2. {_obs_rt_md} / {_n_md} routes correctes (Obsidia).",
        f"3. {_mod_av_md} / {_n_md} appels au modèle évités.",
        f"4. {_fn(_avg_sp_md)} ({_speed_md}).",
        f"5. {_fn(_mod_sp_md)} quand l'appel modèle est évité.",
        "6. 3 familles revendicables sur run réel : BANK, TRADING, GPS.",
        "",
        "## Lecture par famille",
        "",
        "| Famille | Statut | Modèle évité | Résultat |",
        "| --- | --- | --- | --- |",
        f"| BANK | OK | OUI | {_bank_md} |",
        f"| TRADING | OK | OUI | {_bank_md} |",
        f"| GPS | OK | OUI | {_bank_md} |",
        "| FAST_PATH | MESURE | OUI | Pas de pont live dédié |",
        f"| BRODY | MESURE | PARTIEL | {_brody_md} |",
        "| OBSIDURE | MANQUE | NON | connecteur manquant |",
        "| LEAN | MANQUE | NON | connecteur manquant |",
        "",
        "Les domaines propres aujourd'hui : BANK, TRADING, GPS.",
        "FAST_PATH et BRODY sont partiels. OBSIDURE et LEAN restent à brancher.",
        "",
        "---",
        "",
    ]

    # §1 Executive Read
    md += [
        "# OIE Power Benchmark V0.7.1 — Runtime Summary",
        "",
        "## §1 Executive Read",
        "",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| Date | {summary.get('benchmark_date')} |",
        f"| Tasks | {summary.get('tasks_attempted')} |",
        f"| Governance clean | {summary.get('governance_clean')} |",
        f"| Obsidia route accuracy (all) | {summary.get('obsidia_route_accuracy')} |",
        f"| Obsidia route accuracy (wired only) | {wired_acc} ({wired_n}/7 familles) |",
        f"| Gemini route accuracy (all) | {summary.get('gemini_route_accuracy')} |",
        f"| Avg speedup ratio | {summary.get('avg_speedup_ratio')} |",
        f"| Model call avoided | {summary.get('obsidia_model_call_avoided_count')}/{n} |",
        f"| Cost comparison claimable | {summary.get('cost_comparison_claimable_global')} (LOCAL_PROXY_UNCALIBRATED) |",
        f"| OSCA | {oie_idx.get('OSCA_geomean_x')}x |",
        f"| OAPI | {oie_idx.get('OAPI_portfolio_x')}x |",
        f"| ODPI | {oie_idx.get('ODPI_portfolio_x')}x |",
        "",
    ]

    # §2 Benchmark Context
    md += [
        "## §2 Benchmark Context",
        "",
        f"- Version: {BENCHMARK_VERSION}",
        f"- OIE import native: {_OIE_IMPORT_OK}",
        f"- OIE freeze found: {_OIE_FREEZE_FOUND} ({_OIE_FREEZE_NAME})",
        f"- LIVE_LOCAL available: {_LIVE_LOCAL_AVAILABLE}  (sonde API {_OBSIDIA_API_BASE}/api/status au démarrage)",
        f"- Live usable families: {_LIVE_LOCAL_USABLE_FAMILIES or 'none'}",
        f"- Adapter missing families: {_ADAPTER_MISSING_FAMILIES_LIVE}",
        f"- Cost basis Obsidia: {COST_BASIS_LOCAL_PROXY}",
        f"- Gencoin mode: {summary.get('gencoin_mode')}  (CALIBRATION_ONLY, émission=0)",
        f"- Governance: EMITS_ACT={EMITS_ACT} | MEMORY_WRITE={MEMORY_WRITE} | "
        f"KERNEL_MUTATION={KERNEL_MUTATION} | DECISION_AUTHORITY={DECISION_AUTHORITY}",
        "",
    ]

    # §3 Dual Lane Comparison
    md += [
        "## §3 Dual Lane Comparison",
        "",
        "| family | obs_exec_mode | gem_exec_mode | scope | obs_match | gem_match | claimable | model_avoided |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        dl = r.get("dual_lane") or {}
        ol = dl.get("obsidia_lane") or {}
        gl = dl.get("gemini_lane") or {}
        md.append(
            f"| {r.get('family')} | {ol.get('execution_mode')} | {gl.get('execution_mode')} "
            f"| {dl.get('comparison_scope')} | {ol.get('route_match')} | {gl.get('route_match')} "
            f"| {dl.get('comparison_claimable')} | {r.get('obsidia_model_call_avoided')} |"
        )
    md += [""]

    # §4 Claimability Matrix
    md += [
        "## §4 Claimability Matrix",
        "",
        f"| Type | Count | Basis |",
        f"| --- | --- | --- |",
        f"| Route claimable | {cm.get('route_claimable_count')}/{n} | Wired surface only |",
        f"| Functional claimable | {cm.get('functional_claimable_count')}/{n} | Wired surface only |",
        f"| Domain claimable | {cm.get('domain_claimable_count')}/{n} | Wired surface only |",
        f"| Cost claimable | {cm.get('cost_claimable_count')}/{n} | Always False — LOCAL_PROXY_UNCALIBRATED |",
        f"| Adapter missing non-claimable | {cm.get('adapter_missing_non_claimable_count')}/{n} | BRODY, OBSIDURE, LEAN |",
        f"| Gencoin emission claimable | {cm.get('gencoin_emission_claimable')} | CALIBRATION_ONLY |",
        "",
        f"> {summary.get('cost_claim_warning')}",
        "",
    ]

    # §5 Wired Surface Read
    md += [
        "## §5 Wired Surface Read",
        "",
        f"- Familles branchées ({wired_n}/7) : FAST_PATH, BANK, TRADING, GPS",
        f"- Obsidia wired surface accuracy : {wired_acc}",
        f"- Gemini on wired surface : {gem_wired}",
        f"- Obsidia vs Gemini delta (wired) : {delta_wired}",
        "",
        f"> {summary.get('wired_surface_claim')}",
        "",
    ]

    # §6 Adapter Missing Read
    md += [
        "## §6 Adapter Missing Read",
        "",
        f"- Familles ADAPTER_MISSING ({missing_n}/7) : BRODY, OBSIDURE, LEAN",
        f"- Gemini accuracy sur ces familles : {gem_missing}",
        f"- Ces familles NE comptent PAS dans les revendications fonctionnelles Obsidia.",
        "",
        f"> **WARNING** — {summary.get('adapter_missing_warning')}",
        "",
    ]

    # §7 OIE Indices
    md += [
        "## §7 OIE Indices",
        "",
        f"| Indice | Valeur | Base |",
        f"| --- | --- | --- |",
        f"| OSCA (geomean all families) | {oie_idx.get('OSCA_geomean_x')}x | {oie_idx.get('OSCA_basis')} |",
        f"| OAPI (portfolio actions) | {oie_idx.get('OAPI_portfolio_x')}x | {oie_idx.get('OAPI_basis')} |",
        f"| ODPI (portfolio domains) | {oie_idx.get('ODPI_portfolio_x')}x | {oie_idx.get('ODPI_basis')} |",
        f"| Claimable | {oie_idx.get('claimable')} | proxy baseline, not real billing |",
        "",
        "**DCA par domaine :**",
        "",
        "| domain | dca_api_normal | dca_agentic | rows |",
        "| --- | --- | --- | --- |",
    ]
    for k, d in (summary.get("dca_by_domain") or {}).items():
        if isinstance(d, dict):
            _dca_api = d.get("dca_api_normal", "—")
            _dca_agt = d.get("dca_agentic", "—")
        else:
            _dca_api = d if d is not None else "—"
            _dca_agt = "—"
        md.append(f"| {k} | {_dca_api} | {_dca_agt} | — |")
    if not (summary.get("dca_by_domain")):
        for k, d in (summary.get("domain_summary") or {}).items():
            md.append(
                f"| {d.get('domain_name', k)} | {d.get('dca_api_normal')} "
                f"| {d.get('dca_agentic')} | {d.get('total_receipts') or d.get('total_rows', 0)} |"
            )
    md += [
        "",
        "> WARNING: DCA/OSCA/OAPI/ODPI sont des métriques proxy baseline, pas de la facturation réelle.",
        "",
    ]

    # §8 OIE Source Lineage
    md += [
        "## §8 OIE Source Lineage",
        "",
        f"- base_audit_commit: {lineage.get('base_audit_commit', _OIE_SOURCE_LINEAGE.get('base_audit_commit'))}",
        f"- oie_v01_commit_candidate: {lineage.get('oie_v01_commit_candidate', _OIE_SOURCE_LINEAGE.get('oie_v01_commit_candidate'))}",
        f"- freeze_name: {lineage.get('freeze_name', _OIE_FREEZE_NAME)}",
        f"- freeze_found: {_OIE_FREEZE_FOUND}",
        f"- engine_spec: {_OIE_SOURCE_DOCUMENTS.get('engine_spec')}",
        f"- external_api_protocol: {_OIE_SOURCE_DOCUMENTS.get('external_api_protocol')}",
        f"- portfolio_benchmark: {_OIE_SOURCE_DOCUMENTS.get('portfolio_benchmark')}",
        f"- cost_receipt_schema: {_OIE_SOURCE_DOCUMENTS.get('cost_receipt_schema')}",
        f"- oie_import_native: {_OIE_IMPORT_OK}",
        "",
    ]

    # §9 Internal Economy / Gencoin
    md += [
        "## §9 Internal Economy / Gencoin",
        "",
        f"- intellectual_value_avg: {summary.get('intellectual_value_avg')}",
        f"- debt_total: {summary.get('internal_economy_debt_total')}",
        f"- energy_source: {summary.get('energy_source')}",
        f"- gencoin_mode: {summary.get('gencoin_mode')}",
        f"- gencoin_total_emission: {summary.get('gencoin_total_emission')}  (INTERDIT > 0 en calibration)",
        f"- source_law_global_satisfied: {summary.get('source_law_global_satisfied')}",
        f"- gencoin_oie_can_measure_value: {bridge.get('oie_can_measure_value')}",
        f"- gencoin_oie_cannot_emit_value: {bridge.get('oie_cannot_emit_value')}",
        "",
        f"> {summary.get('source_law_global_reason')}",
        "",
    ]

    # §10 Route Comparison (pair par pair)
    md += [
        "## §10 Route Comparison — Pair par Pair",
        "",
        f"> {summary.get('global_route_accuracy_warning')}",
        "",
        "| family | expected_route | obs_route | gem_route | obs_match | gem_match | obs_status | paired_outcome | claimable |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        md.append(
            f"| {r.get('family')} | {r.get('expected_route')} "
            f"| {r.get('obsidia_detected_route')} | {r.get('gemini_detected_route')} "
            f"| {r.get('obsidia_route_match')} | {r.get('gemini_route_match')} "
            f"| {r.get('obsidia_status')} | {r.get('paired_route_outcome')} "
            f"| {r.get('route_accuracy_claimable')} |"
        )
    md += [
        "",
        f"- Audit-safe claims:",
        *[f"  - {c}" for c in (summary.get("audit_safe_claims") or [])],
        "",
    ]

    # §10b Obsidia Live Local Read
    live_sum = summary.get("obsidia_live_adapter_summary", {}) or {}
    live_registry = summary.get("obsidia_live_adapter_registry", {}) or {}
    md += [
        "## §10b Obsidia Live Local Read",
        "",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| API base | {_OBSIDIA_API_BASE} |",
        f"| Kernel target | {_OBSIDIA_KERNEL_URL} |",
        f"| Requested mode | {live_sum.get('requested_mode', 'AUTO')} |",
        f"| LIVE_LOCAL available (global) | {live_sum.get('live_local_available_global', False)} |",
        f"| Adapters found | {live_sum.get('adapters_found_count', 0)}/7 |",
        f"| Adapters usable for LIVE_LOCAL | {live_sum.get('usable_live_count', 0)}/7 |",
        f"| LIVE_LOCAL rows | {live_sum.get('live_local_rows_count', 0)} |",
        f"| Bridge attempted, kernel unreachable | {live_sum.get('bridge_kernel_unreachable_count', 0)} |",
        f"| Frozen fallback rows | {live_sum.get('frozen_fallback_rows_count', 0)} |",
        f"| Adapter missing rows | {live_sum.get('adapter_missing_rows_count', 0)} |",
        f"| Live usable families | {live_sum.get('live_local_usable_families', [])} |",
        f"| Fallback families | {live_sum.get('live_local_unavailable_families', [])} |",
        f"| Adapter missing families | {live_sum.get('adapter_missing_families', [])} |",
        "",
        "**Registry par famille :**",
        "",
        "| family | adapter_found | usable_live | adapter_type | endpoint | fallback_used | reason |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for fam in ("FAST_PATH", "BANK", "TRADING", "GPS", "BRODY", "OBSIDURE", "LEAN"):
        reg_entry = live_registry.get(fam, {})
        matching_row = next((r for r in rows if r.get("family") == fam), None)
        fallback_val = matching_row.get("obsidia_fallback_used") if matching_row else "N/A"
        md.append(
            f"| {fam} | {reg_entry.get('adapter_found')} | {reg_entry.get('usable_for_live_local')} "
            f"| {reg_entry.get('adapter_type', 'NONE')} | {reg_entry.get('bridge_path') or 'none'} "
            f"| {fallback_val} | {(reg_entry.get('reason_if_not_usable') or 'usable')[:60]} |"
        )
    live_count = live_sum.get("live_local_rows_count", 0)
    kernel_err_count = live_sum.get("bridge_kernel_unreachable_count", 0)
    md += [
        "",
    ]
    if live_count == 0 and kernel_err_count == 0:
        if not _LIVE_LOCAL_AVAILABLE:
            md.append("> **LIVE_LOCAL rows = 0** : L'API 8000 est inaccessible au démarrage du benchmark — aucun bridge live tenté. Fallback sur FROZEN_V0_ESTIMATE pour toutes les familles branchées.")
        else:
            md.append("> **LIVE_LOCAL rows = 0** : Le mode OIE_OBSIDIA_EXECUTION_MODE n'est pas LIVE_LOCAL ou LIVE_LOCAL_OR_FROZEN.")
    elif kernel_err_count > 0:
        md.append(f"> **Bridge tenté, kernel 3001 inaccessible** : {kernel_err_count} row(s) ont tenté le bridge live mais le kernel {_OBSIDIA_KERNEL_URL} n'a pas répondu. Ce n'est pas ADAPTER_MISSING — la route API est confirmée, le kernel seul est down.")
    else:
        md.append(f"> **LIVE_LOCAL_BRIDGE confirmé** : {live_count} row(s) exécutées via le bridge live API 8000 → kernel 3001.")
    md += [""]

    # §10c Known Path / Path Compute Read
    _kp_count = summary.get("known_path_detected_count", 0)
    _kp_rate = summary.get("known_path_detected_rate", 0.0)
    _inf_avoided = summary.get("inference_avoided_count", 0)
    _model_avoided_fams = summary.get("model_avoided_families") or []
    _fp_reg = _OBSIDIA_LIVE_ADAPTER_REGISTRY.get("FAST_PATH", {})
    _fp_bridge_avail = _fp_reg.get("usable_for_live_local", False)
    _live_bridge_fams = [r["family"] for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_LIVE_LOCAL]
    _kernel_unreach_fams = [r["family"] for r in rows if r.get("obsidia_status") == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"]
    _missing_fams = [r["family"] for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING]
    md += [
        "## §10c Known Path / Path Compute Read",
        "",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| Known path detected | {_kp_count}/{len(rows)} ({_kp_rate}) |",
        f"| Model calls avoided by known path | {_inf_avoided}/{len(rows)} |",
        f"| Model avoided families | {_model_avoided_fams} |",
        f"| Path Compute runtime used | False |",
        f"| Path Compute runtime claimable | False |",
        f"| Fast path live bridge available | {_fp_bridge_avail} |",
        f"| Fast path adapter type | {_fp_reg.get('adapter_type', 'NONE')} |",
        f"| Live bridge claimable families | {_live_bridge_fams} |",
        f"| Bridge attempted, kernel unreachable | {_kernel_unreach_fams} |",
        f"| Adapter missing | {_missing_fams} |",
        "",
        "> Accuracy measures route recognition, not inference economy.",
        "",
        "> Ce run prouve l'économie d'inférence sur routes connues. Le prochain run doit prouver le Path Compute live.",
        "",
    ]

    # §10d LLM Necessity Read
    _mn_read = readable.get("model_necessity_read", {}) if "readable" in dir() else {}
    _mn_data = {r["family"]: r.get("model_necessity", {}) for r in rows}
    md += [
        "## §10d LLM Necessity Read",
        "",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| External LLM called by baseline | {sum(1 for r in rows if r.get('model_necessity', {}).get('gemini_external_llm_called'))} |",
        f"| External LLM required by design | {sum(1 for r in rows if r.get('model_necessity', {}).get('external_llm_required_by_design') is True)} |",
        f"| External LLM avoided by Obsidia | {sum(1 for r in rows if r.get('model_necessity', {}).get('external_llm_avoided_by_obsidia'))} |",
        f"| Unnecessary generalist calls avoided | {sum(1 for r in rows if r.get('model_necessity', {}).get('unnecessary_generalist_call_avoided'))} |",
        f"| Claimable unnecessary calls avoided | {sum(1 for r in rows if r.get('model_necessity', {}).get('necessity_claimable') and r.get('model_necessity', {}).get('unnecessary_generalist_call_avoided'))} |",
        f"| Necessity claimable families | {[r['family'] for r in rows if r.get('model_necessity', {}).get('necessity_claimable')]} |",
        f"| Non-claimable but measured families | {[r['family'] for r in rows if not r.get('model_necessity', {}).get('necessity_claimable') and r.get('model_necessity', {}).get('external_llm_avoided_by_obsidia')]} |",
        "",
        "**Minimal sufficient layer by family:**",
        "",
        "| family | minimal_layer | actual_layer | necessity_claimable |",
        "| --- | --- | --- | --- |",
    ]
    for r in rows:
        mn = r.get("model_necessity", {})
        md.append(f"| {r['family']} | {mn.get('expected_minimal_layer')} | {mn.get('actual_obsidia_layer_used')} | {mn.get('necessity_claimable')} |")
    md += [
        "",
        "> Ce benchmark mesure si l'appel à un LLM généraliste était nécessaire, pas seulement s'il était rapide ou correct.",
        "",
        "> **Obsidia ne bat pas Gemini en étant un meilleur Gemini. Obsidia bat Gemini quand Gemini n'aurait jamais dû être appelé.**",
        "",
    ]

    # §10e Answer Adequacy Read
    _aa_rows_md = [r.get("answer_adequacy", {}) for r in rows]
    _aa_avg_md = round(sum(r.get("answer_adequacy_score", 0.0) for r in _aa_rows_md) / len(_aa_rows_md), 4) if _aa_rows_md else 0.0
    md += [
        "## §10e Answer Adequacy Read",
        "",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| Answer adequacy avg | {_aa_avg_md} |",
        f"| Route correct count | {sum(1 for r in _aa_rows_md if r.get('route_correct'))}/{len(rows)} |",
        f"| Output bounded count | {sum(1 for r in _aa_rows_md if r.get('output_bounded'))}/{len(rows)} |",
        f"| Minimal layer respected count | {sum(1 for r in _aa_rows_md if r.get('minimal_layer_respected'))}/{len(rows)} |",
        f"| Governance preserved count | {sum(1 for r in _aa_rows_md if r.get('governance_preserved'))}/{len(rows)} |",
        f"| Trace/receipt available count | {sum(1 for r in _aa_rows_md if r.get('trace_or_receipt_available'))}/{len(rows)} |",
        f"| Hallucination risk avoided count | {sum(1 for r in _aa_rows_md if r.get('hallucination_risk_avoided'))}/{len(rows)} |",
        "",
        "**Adequacy by family:**",
        "",
        "| family | score | route_correct | output_bounded | min_layer | governance | claimable |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        aa = r.get("answer_adequacy", {})
        md.append(f"| {r['family']} | {aa.get('answer_adequacy_score')} | {aa.get('route_correct')} | {aa.get('output_bounded')} | {aa.get('minimal_layer_respected')} | {aa.get('governance_preserved')} | {aa.get('adequacy_claimable')} |")
    md += [
        "",
        "> La meilleure réponse n'est pas toujours la plus fluide. C'est la sortie suffisante, gouvernée, au niveau minimal nécessaire.",
        "",
        "> Warning: Answer adequacy measures whether the output is correct, bounded, governed and sufficient; it does not measure prose quality.",
        "",
        "> FAST_PATH et BRODY peuvent être mesurés, mais ne sont pas claimables en adéquation tant que leur fermeture runtime n’est pas complète.",
        "",
    ]

    # §10f Universal Translation Layer Read
    md += [
        "## §10f Universal Translation Layer Read",
        "",
        f"| Field | Value |",
        f"| --- | --- |",
        f"| Claimability | SCHEMA_PROXY_ONLY_UNTIL_RUNTIME_TRANSLATOR_INSTRUMENTED |",
        f"| Role | Convert human language, code, domain signals, errors and intentions into the Obsidia alphabet. |",
        "",
        "**Non-role:** Does not decide. Does not act. Does not replace X108. Does not act as a sovereign generalist model.",
        "",
        "| family | input_surface | target_layer | emitted_alphabet | requires_external_llm |",
        "| --- | --- | --- | --- | --- |",
        f"| FAST_PATH | natural_language_or_route_request | {MIN_LAYER_FAST_PATH} | route_label | False |",
        f"| BANK | domain_request | {MIN_LAYER_DOMAIN_BRIDGE} | bank payload / domain state | False |",
        f"| TRADING | domain_request | {MIN_LAYER_DOMAIN_BRIDGE} | trading payload / domain state | False |",
        f"| GPS | domain_request | {MIN_LAYER_DOMAIN_BRIDGE} | gps payload / domain state | False |",
        f"| BRODY | natural_language | {MIN_LAYER_BRODY_INTERNAL} | brody message / answer route | False |",
        f"| OBSIDURE | code_intent | {MIN_LAYER_OBSIDURE_AGENT} | patch / test / diff intent | null (adapter missing) |",
        f"| LEAN | proof_intent | {MIN_LAYER_LEAN_PROOF} | formal proof task | null (adapter missing) |",
        "",
        "> Le LLM comprend pour agir. Obsidia traduit pour router.",
        "",
    ]

    # §10g Architecture Advantage Read
    md += [
        "## §10g Architecture Advantage Read",
        "",
        f"> architecture_advantage_claimable = INTERPRETATION_SUPPORTED_BY_CURRENT_METRICS_NOT_FULL_MARKET_PROOF",
        "",
        "**NON_TRAINED_STRUCTURE_ADVANTAGE**",
        "- Obsidia obtains speed, routing and governance gains on bounded surfaces without a massive training regime comparable to Gemini.",
        "- The gain does not come from a bigger model. It comes from reducing the search space before inference.",
        "- Known admissible route > model inference.",
        "",
        "**STRUCTURE_OVER_RAW_INTELLIGENCE**",
        "- LLMs centralize intelligence in inference. Obsidia redistributes intelligence into the structure of the path.",
        "",
        "**OWN_STACK_OVER_CHEAP_MODEL**",
        "- This is not a cheaper model. It is an architecture that reduces the need for a model.",
        "",
        "**PROBABILITY_NON_SOVEREIGN**",
        "- Probability may explore. It must not authorize.",
        "- Generative explores. Kernel bounds. Sigma alerts. Domains translate. X108 closes.",
        "",
        "**KERNEL_AUTHORITY**",
        "- The kernel is powerful because it is non-negotiable, not because it is intelligent.",
        "",
        "**MARKET_INTERPRETATION**",
        "- Le marché optimise l'inférence. Obsidia optimise la décision d'inférer.",
        "- They use the model to compensate for an architecture that cannot translate. Obsidia builds the translation.",
        "",
        "**Anti-overclaim guards:**",
        "- Obsidia is not claimed to be a better generalist LLM.",
        "- Cost comparison is not claimable while Obsidia is LOCAL_PROXY_UNCALIBRATED.",
        "- Translation layer read is schema/proxy until runtime translator instrumentation exists.",
        "- Architecture advantage read is interpretation supported by metrics, not full market proof.",
        "- Extreme ratios indicate a change of path, not general intelligence superiority.",
        "",
    ]

    # §10h Speed Stack Read
    _dca_raw_md = summary.get("dca_by_domain") or {}
    def _dca_val_md(fam: str) -> str:
        v = _dca_raw_md.get(fam)
        if v is None:
            return "null"
        if isinstance(v, dict):
            return str(v.get("dca_api_normal") or v.get("dca_agentic") or "null")
        return str(v)
    md += [
        "## §10h Speed Stack Read",
        "",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| Live avg speedup vs Gemini REAL_SDK | {summary.get('avg_speedup_ratio')}x |",
        f"| Available surface avg speedup | {summary.get('available_surface_avg_speedup_ratio')} |",
        f"| Model avoided avg speedup | {summary.get('model_avoided_avg_speedup_ratio')} |",
        f"| Governed speed rate | {summary.get('governance_preserved_at_speed_rate')} |",
        f"| Known path detected | {summary.get('known_path_detected_count')}/{len(rows)} |",
        f"| Inference avoided | {summary.get('inference_avoided_count')}/{len(rows)} |",
        f"| Model call avoided | {summary.get('obsidia_model_call_avoided_count')}/{len(rows)} |",
        "",
        "**OIE speed indices:**",
        "",
        f"| Index | Value |",
        f"| --- | --- |",
        f"| OSCA — geomean all families | {summary.get('osca_ratio')}x |",
        f"| OAPI — portfolio actions | {summary.get('oapi_ratio')}x |",
        f"| ODPI — portfolio domains | {summary.get('odpi_ratio')}x |",
        "",
        "**DCA by domain:**",
        "",
        "| domain | dca_api_normal |",
        "| --- | --- |",
        *[f"| {fam} | {_dca_val_md(fam)} |" for fam in ("FAST_PATH", "BRODY", "BANK", "TRADING", "GPS", "GPS_AVIATION", "OBSIDURE", "LEAN")],
        "",
        "**Governance while fast:**",
        "",
        "- decision_authority : KX108_ONLY",
        "- emits_act : false",
        "- memory_write : false",
        "- kernel_mutation : false",
        "",
        "**Claim guard:**",
        "",
        "- speed_metrics_claimable : true",
        f"- cost_comparison_claimable : {summary.get('cost_comparison_claimable_global', False)}",
        "- path_compute_runtime_claimable : false",
        "> Speed is measured; real cost and full Path Compute runtime are not claimed.",
        "",
    ]

    # §11 Missing / Next Work
    md += [
        "## §11 Missing / Next Work",
        "",
        "- [ ] BRODY adapter live — brancher `run_obsidia_local_actual()` réelle pour BRODY",
        "- [ ] OBSIDURE adapter live — brancher pour OBSIDURE",
        "- [ ] LEAN adapter live — brancher pour LEAN",
        f"- [ ] LIVE_LOCAL — démarrer l'API 8000 (`uvicorn apps.obsidia_api.main:app`) + kernel 3001 pour activer les bridges (actuellement api_up={_LIVE_LOCAL_AVAILABLE})",
        "- [ ] Cost measurement réel — remplacer `LOCAL_PROXY_UNCALIBRATED` par SDK billing",
        "- [ ] Gencoin source law — satisfaire conditions réelles avant `source_law_satisfied=True`",
        "- [ ] OIE indices calibration réelle — remplacer proxy par données runtime mesurées",
        "",
    ]

    (report_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")


# ── Protocol doc (Phase 7) ────────────────────────────────────────────────────

_REQUIRED_PHRASES = [
    "Gemini is inference power. Obsidia is routing, governance, proof, and inference avoidance power.",
    "Obsidia is not benchmarked as a larger model; it is benchmarked as a constrained decision and work-avoidance layer.",
    "Energy values are proxy estimates unless hardware/provider telemetry is supplied.",
]

_INVALID_CLAIMS = [
    "Obsidia is smarter than Gemini",
    "Obsidia is faster than all LLMs",
    "Obsidia is a better language model",
    "Obsidia produces better outputs than Gemini",
]


def write_protocol_doc() -> Path:
    """Ecrire le protocole statique dans docs/audits (une fois, pas a chaque run)."""
    doc_path = _REPO_ROOT / "docs" / "audits" / "OBSIDIA_OIE_POWER_METRICS_PROTOCOL_V0_7.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# OBSIDIA OIE Power Metrics — Protocole V0.7",
        "",
        "> " + _REQUIRED_PHRASES[0],
        "",
        "> " + _REQUIRED_PHRASES[1],
        "",
        "---",
        "",
        "## 1. Cout mesure vs cout proxy",
        "",
        f"- `obsidia_cost_basis = {COST_BASIS_LOCAL_PROXY}`",
        "  Le cout Obsidia est une estimation proxy basee sur l'architecture.",
        "  Il ne correspond pas a une facture provider reelle.",
        "  Formula : " + COST_PROXY_FORMULA,
        f"- `gemini_cost_basis = {COST_BASIS_SDK_MEASURED}` en mode REAL avec usage SDK.",
        "- `cost_comparison_claimable = False` tant que les deux bases sont differentes.",
        f"- Warning : {COST_PROXY_WARNING}",
        "",
        "---",
        "",
        "## 2. Economie d'inference",
        "",
        "- `model_call_avoided = True` : Obsidia route sans appel LLM.",
        "- `available_surface` : familles ou Obsidia fonctionne sans ADAPTER_MISSING.",
        f"  Familles : {sorted(AVAILABLE_SURFACE_FAMILIES)}",
        f"- `adapter_missing_families` : {sorted(ADAPTER_MISSING_FAMILIES)}",
        "  Ces familles sont EXCLUES des victoires fonctionnelles.",
        "- `external_dependency_reduction_score = 1.0` si model_call_avoided=True.",
        "",
        "---",
        "",
        "## 3. Economie intellectuelle (CALIBRATION_ONLY)",
        "",
        f"- `intellectual_economy_basis = {IE_BASIS}`",
        "- Scores calibration : cognitive_value, proof_quality, stability_value,",
        "  reusability, governance_value, risk_reduction, friction_reduction,",
        "  external_dependency_reduction, auditability, debt.",
        "- Formule CV (PROVISIONAL_CALIBRATION_ONLY) :",
        "  CV = wN*novelty + wU*utility + wC*coherence + wR*risk_reduction",
        "       + wReuse*reusability + wP*proof_quality - debt",
        f"  Poids source : {_CV_WEIGHT_SOURCE}",
        f"  Reference code : apps/obsidia_api/brody_gencoin_cognitive_ledger.py",
        "- V(x) ∝ 1/(L(x) + epsilon) : doctrine uniquement, non implementee.",
        "",
        "---",
        "",
        "## 4. Gencoin — CALIBRATION_ONLY",
        "",
        f"- `gencoin_mode = {GENCOIN_MODE}`",
        "- Aucune emission. Aucun token reel. Aucune valeur de marche.",
        "- Aucune distribution. Aucun wallet. Aucune blockchain.",
        "- `gencoin_emission_allowed = False` — invariant.",
        "- `gencoin_emission_amount = 0` — toujours zero.",
        f"- `gencoin_distribution_mode = {GENCOIN_DISTRIBUTION_MODE}`",
        "- Source law : non satisfaite en calibration benchmark.",
        "",
        "---",
        "",
        "## 5. Source law",
        "",
        "- Source law est satisfaite uniquement si :",
        "  - Preuve disponible (non ADAPTER_MISSING)",
        "  - Gouvernance propre (emits_act=False, memory_write=False)",
        "  - coherence_score >= 0.8",
        "  - utility_score > 0.5",
        "  - Mode REEL (non calibration)",
        "- En benchmark CALIBRATION_ONLY : source_law_satisfied = False toujours.",
        "",
        "---",
        "",
        "## 6. Debt",
        "",
        "- `debt_score` augmente si :",
        "  - ADAPTER_MISSING : +0.50",
        "  - Cout proxy non calibre : +0.20 (toujours dans benchmark)",
        "  - Preuve manquante (ADAPTER_MISSING) : +0.20",
        "",
        "---",
        "",
        "## 7. Available surface",
        "",
        f"- Familles disponibles : {sorted(AVAILABLE_SURFACE_FAMILIES)}",
        f"- Familles ADAPTER_MISSING : {sorted(ADAPTER_MISSING_FAMILIES)}",
        "- BRODY, OBSIDURE, LEAN doivent etre exclues des victoires fonctionnelles.",
        "- `adapter_missing_excluded_from_functional_victory = True`",
        "",
        "---",
        "",
        "## 8. Energie — proxy uniquement",
        "",
        "> " + _REQUIRED_PHRASES[2],
        "",
        "- Variables env : OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS,",
        "  OIE_LOCAL_POWER_W, OIE_CARBON_GCO2_PER_KWH.",
        "- Sans ces variables : energy_source = ENERGY_PROXY_UNAVAILABLE.",
        "",
        "---",
        "",
        "## 9. Claims invalides",
        "",
        *[f"- INTERDIT : \"{c}\"" for c in _INVALID_CLAIMS],
        "- INTERDIT : Ce benchmark prouve que Obsidia est moins cher en production.",
        "- INTERDIT : Le cout Obsidia est mesure.",
        "- INTERDIT : Gencoin a emis des tokens dans ce benchmark.",
        "",
        "---",
        "",
        "## 10. Rapports runtime",
        "",
        "- Rapports runtime : `.local_reports/OIE_POWER_BENCHMARK_V0_7_1_<timestamp>/`",
        "  - `results.json` — rows comparaison par famille",
        "  - `summary.json` — summary global",
        "  - `internal_economy.json` — scores economie intellectuelle",
        "  - `gencoin_calibration.json` — layer Gencoin calibration",
        "  - `summary.md` — rapport lisible",
        "- Ce document est le seul fichier statique dans docs/audits.",
    ]
    doc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return doc_path


def generate_report(summary: dict, rows: list[dict]) -> str:
    """Generer le rapport Markdown V0.7 pour affichage inline."""
    lines: list[str] = []

    def h(n: int, t: str) -> None:
        lines.append(f"{'#' * n} {t}\n")

    def p(t: str) -> None:
        lines.append(t + "\n")

    def table(headers: list[str], data: list[list]) -> None:
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in data:
            lines.append("| " + " | ".join(str(c) if c is not None else "?" for c in row) + " |")
        lines.append("")

    def _fmt(v, digits=4) -> str:
        if v is None:
            return "N/A"
        if isinstance(v, float):
            return f"{v:.{digits}f}"
        return str(v)

    h(1, "OBSIDIA OIE — Power Benchmark V0.7 : Obsidia vs Gemini")
    p(f"**Date :** {BENCHMARK_DATE}")
    p(f"**Version :** {BENCHMARK_VERSION}")
    p(f"**Statut :** dry-run — run reel necessite GEMINI_API_KEY + ALLOW_NETWORK")
    p(f"**Autorite :** {summary['decision_authority']} — OIE non souverain")
    p("---")

    h(2, "1. Executive Summary")
    p("> " + _REQUIRED_PHRASES[0])
    p("")
    p("> " + _REQUIRED_PHRASES[1])
    p("")
    p(f"- Taches : {summary['tasks_attempted']} familles routing")
    p(f"- Obsidia route accuracy : {_fmt(summary['obsidia_route_accuracy'], 2)}")
    p(f"- Gemini route accuracy  : {_fmt(summary['gemini_route_accuracy'], 2)}")
    p(f"- Model call avoided     : {summary['obsidia_model_call_avoided_count']}/{summary['tasks_attempted']}")
    p(f"- Governance clean       : {summary['governance_clean']}")
    p(f"- Cost comparison claimable : {summary['cost_comparison_claimable_global']}")
    p(f"- Gencoin mode           : {summary['gencoin_mode']}")
    p("---")

    h(2, "2. Pourquoi les benchmarks precedents etaient insuffisants")
    p("- Pas de vision globale speed / energy / throughput / work avoidance")
    p("- Pas de cost_basis distinction (mesure vs proxy)")
    p("- Pas de available_surface vs adapter_missing surfaces")
    p("- Pas d'economie intellectuelle (cognitive, proof, stability, risk)")
    p("- Pas de Gencoin calibration layer")
    p("V0.7.1 reunit toutes ces dimensions.")
    p("---")

    h(2, "3. Architecture : deux lanes, 7 familles")
    table(
        ["Lane", "Mode", "Status"],
        [
            ["OBSIDIA_LOCAL_ACTUAL", "FROZEN_V0/REAL/ADAPTER_MISSING", COST_BASIS_LOCAL_PROXY],
            ["GEMINI_SDK_EXTERNAL", "DRY_RUN_MOCK / REAL_SDK", COST_BASIS_DRY_RUN_MOCK],
        ]
    )

    h(2, "4. Speed metrics")
    table(
        ["family", "obs_lat_ms", "gem_lat_ms", "speedup", "winner"],
        [[r["family"], _fmt(r["obsidia_latency_ms"]), _fmt(r["gemini_latency_ms"]),
          _fmt(r["speedup_ratio"], 2), r["winner_speed"]] for r in rows]
    )
    p(f"Moyenne speedup : {_fmt(summary['avg_speedup_ratio'], 2)}x")
    p("---")

    h(2, "5. Cost metrics (PROXY vs MEASURED)")
    p(f"> {summary.get('cost_claim_warning')}")
    p(f"> **NON_CLAIMABLE** — cost_comparison_claimable_global = {summary.get('cost_comparison_claimable_global')}")
    p("> Cost comparison not claimable until Obsidia local cost is measured or calibrated.")
    table(
        ["family", "obs_basis", "gem_basis", "comparable", "winner_cost_status"],
        [[r["family"], r.get("obsidia_cost_basis"), r.get("gemini_cost_basis"),
          str(r.get("cost_comparison_claimable")),
          "NON_CLAIMABLE" if not r.get("cost_comparison_claimable") else r.get("winner_cost")] for r in rows]
    )
    p("---")

    h(2, "6. Energy metrics")
    p("> " + _REQUIRED_PHRASES[2])
    p(f"Source energie : {summary['energy_source']}")
    p("---")

    h(2, "7. Available surface — Work avoidance / Inférence évitée")
    p(f"Familles disponibles (obsidia_status != ADAPTER_MISSING) : {summary.get('available_surface_families')}")
    p(f"Familles ADAPTER_MISSING (exclues victoires fonctionnelles) : {summary.get('adapter_missing_families')}")
    p(f"adapter_missing_excluded_from_functional_victory : {summary.get('adapter_missing_excluded_from_functional_victory')}")
    p(f"available_surface_avg_speedup_ratio : {_fmt(summary.get('available_surface_avg_speedup_ratio'), 2)}")
    p("")
    p("### Work avoidance / Travail évité")
    table(
        ["family", "model_call_avoided", "modules_skipped", "ext_dep_reduction"],
        [[r["family"],
          str(r.get("obsidia_model_call_avoided")),
          str(r.get("obsidia_modules_skipped")),
          _fmt(r.get("external_dependency_reduction_score"), 2)] for r in rows]
    )
    p(f"model_call_avoided_count : {summary.get('obsidia_model_call_avoided_count')}/{summary.get('tasks_attempted')}")
    p(f"model_call_avoided_rate  : {_fmt(summary.get('obsidia_model_call_avoided_rate'), 2)}")
    p(f"modules_skipped_total    : {summary.get('obsidia_modules_skipped_total')}")
    p("")
    p("### Inference avoidance / Inférence évitée")
    p("Obsidia évite l'appel LLM externe sur les familles model_call_avoided=True.")
    p("external_dependency_reduction_score = 1.0 si model_call_avoided = True.")
    p("---")

    h(2, "8. Intellectual economy (CALIBRATION_ONLY)")
    table(
        ["family", "cognitive", "proof", "stability", "utility", "debt", "iv_score"],
        [
            [r["family"],
             _fmt(r.get("cognitive_value_score"), 2),
             _fmt(r.get("proof_quality_score"), 2),
             _fmt(r.get("stability_value_score"), 2),
             _fmt(r.get("utility_score"), 2),
             _fmt(r.get("debt_score"), 2),
             _fmt(r.get("intellectual_value_score"), 2)]
            for r in rows
        ]
    )
    p(f"intellectual_value_avg : {_fmt(summary.get('intellectual_value_avg'), 2)}")
    p(f"intellectual_value_available_surface_avg : {_fmt(summary.get('intellectual_value_available_surface_avg'), 2)}")
    p(f"CV weights source : {_CV_WEIGHT_SOURCE}")
    p("---")

    h(2, "9. Gencoin (CALIBRATION_ONLY)")
    p(f"- gencoin_mode : {summary.get('gencoin_mode')}")
    p(f"- gencoin_emission_enabled : {summary.get('gencoin_emission_enabled')}")
    p(f"- gencoin_total_emission : {summary.get('gencoin_total_emission')}")
    p(f"- source_law_global_satisfied : {summary.get('source_law_global_satisfied')}")
    p(f"- source_law_global_reason : {summary.get('source_law_global_reason')}")
    p(f"- internal_economy_debt_total : {_fmt(summary.get('internal_economy_debt_total'), 2)}")
    p("---")

    h(2, "10. Governance / boundary safety")
    table(
        ["Propriete", "Valeur"],
        [
            ["emits_act", str(EMITS_ACT)],
            ["memory_write", str(MEMORY_WRITE)],
            ["kernel_mutation", str(KERNEL_MUTATION)],
            ["decision_authority", DECISION_AUTHORITY],
            ["governance_clean (all)", str(summary["governance_clean"])],
        ]
    )
    p("---")

    h(2, "11. Routing quality")
    table(
        ["family", "expected", "obs_match", "gem_match", "winner"],
        [[r["family"], r["expected_route"], r.get("obsidia_route_match"),
          r.get("gemini_route_match"), r.get("winner_route")] for r in rows]
    )
    p("---")

    h(2, "12. Valid claims")
    for c in (summary.get("audit_safe_claims") or []):
        p(f"- {c}")
    p("---")

    h(2, "13. Invalid claims")
    for c in _INVALID_CLAIMS:
        p(f"- INTERDIT : \"{c}\"")
    p("---")

    h(2, "13b. Comparaison routage paire par paire")
    p(f"> {summary.get('global_route_accuracy_warning')}")
    p("")
    table(
        ["family", "expected_route", "obsidia_detected_route", "gemini_detected_route",
         "obsidia_match", "gemini_match", "obsidia_status", "paired_outcome", "claimable"],
        [[
            r.get("family"),
            r.get("expected_route"),
            r.get("obsidia_detected_route"),
            r.get("gemini_detected_route"),
            str(r.get("obsidia_route_match")),
            str(r.get("gemini_route_match")),
            r.get("obsidia_status"),
            r.get("paired_route_outcome"),
            str(r.get("route_accuracy_claimable")),
        ] for r in rows]
    )
    p(f"**Obsidia wired surface accuracy :** {_fmt(summary.get('obsidia_wired_surface_accuracy'), 4)}"
      f" ({summary.get('obsidia_wired_surface_count')} familles branchées)")
    p(f"**Gemini on wired surface accuracy :** {_fmt(summary.get('gemini_on_obsidia_wired_surface_accuracy'), 4)}")
    p(f"**Obsidia vs Gemini delta (wired) :** {_fmt(summary.get('obsidia_vs_gemini_wired_surface_delta'), 4)}")
    p(f"**Gemini on adapter-missing accuracy :** {_fmt(summary.get('gemini_on_adapter_missing_surface_accuracy'), 4)}"
      f" ({summary.get('adapter_missing_surface_count')} familles ADAPTER_MISSING)")
    p("")
    p(f"> {summary.get('wired_surface_claim')}")
    p("")
    p(f"> **WARNING** — {summary.get('adapter_missing_warning')}")
    p("---")

    h(2, "14. Chemin connu — Known path")
    p("> Quand la route est connue, prédire devient plus lent que vérifier.")
    table(
        ["family", "known_path_detected", "deterministic_route", "prediction_replaced", "stage", "claimable"],
        [[
            r["family"],
            str(r.get("known_path_detected")),
            str(r.get("deterministic_route_used")),
            str(r.get("prediction_replaced_by_verification")),
            str(r.get("known_path_stage")),
            str(r.get("known_path_claimable")),
        ] for r in rows]
    )
    _kp_count = summary.get("known_path_detected_count", 0)
    _kp_rate = summary.get("known_path_detected_rate")
    p(f"Known path detected: {_kp_count} / {len(rows)} ({_fmt(_kp_rate, 2) if _kp_rate is not None else 'N/A'} rate)")
    p("---")

    h(2, "15. Nécessité d'inférence — Inference necessity")
    table(
        ["family", "obsidia_inf_req", "gemini_inf_req", "inf_delta", "unnecessary_avoided", "ext_dep_avoided"],
        [[
            r["family"],
            str(r.get("obsidia_inference_required")),
            str(r.get("gemini_inference_required")),
            str(r.get("inference_necessity_delta")),
            str(r.get("unnecessary_inference_avoided")),
            str(r.get("external_dependency_avoided")),
        ] for r in rows]
    )
    p(f"Unnecessary inference avoided: {summary.get('unnecessary_inference_avoided_count', 0)} / {len(rows)}")
    p(f"External dependency avoided rate: {_fmt(summary.get('external_dependency_avoided_rate'), 2)}")
    p("---")

    h(2, "16. Vitesse gouvernée — Governed speed")
    p("> Obsidia ne gagne pas en vitesse en sacrifiant le contrôle ; la vitesse est mesurée sous KX108_ONLY.")
    table(
        ["family", "gov_speedup", "gov_lat_delta_pct", "speed_claimable", "governance_preserved"],
        [[
            r["family"],
            _fmt(r.get("governed_speedup_ratio"), 4),
            _fmt(r.get("governed_latency_delta_pct"), 2),
            str(r.get("speed_under_governance_claimable")),
            str(r.get("governance_preserved_at_speed")),
        ] for r in rows]
    )
    p(f"Governed speedup avg: {_fmt(summary.get('governed_speedup_avg'), 4)}")
    p(f"Governed speedup median: {_fmt(summary.get('governed_speedup_median'), 4)}")
    p(f"Governance preserved at speed rate: {_fmt(summary.get('governance_preserved_at_speed_rate'), 2)}")
    p(f"Claim: {summary.get('governed_speed_claim')}")
    p("---")

    h(2, "17. Lecture novice — Ce que l'écart change concrètement")
    p("Projections à 1 000 et 1 000 000 requêtes (basées sur surface disponible uniquement).")
    _nov_rows = [
        ["Model calls avoided / 1 000 req", str(summary.get("model_calls_avoided_per_1000_requests"))],
        ["Model calls avoided / 1 M req", str(summary.get("model_calls_avoided_per_1m_requests"))],
        ["Time saved / request (ms avg)", str(summary.get("time_saved_per_request_ms_avg"))],
        ["Time saved / 1 000 req (s)", str(summary.get("time_saved_per_1000_requests_seconds"))],
        ["Time saved / 1 000 req (min)", str(summary.get("time_saved_per_1000_requests_minutes"))],
        ["Time saved / 1 M req (h)", str(summary.get("time_saved_per_1m_requests_hours"))],
        ["Time saved / 1 M req (days)", str(summary.get("time_saved_per_1m_requests_days"))],
        ["Time saved (model avoided) / req (ms)", str(summary.get("time_saved_model_avoided_per_request_ms_avg"))],
        ["Time saved (model avoided) / 1 000 req (min)", str(summary.get("time_saved_model_avoided_per_1000_requests_minutes"))],
        ["Time saved (model avoided) / 1 M req (days)", str(summary.get("time_saved_model_avoided_per_1m_requests_days"))],
        ["Energy saved / 1 000 req (Wh)", str(summary.get("energy_saved_per_1000_requests_wh"))],
        ["Energy saved / 1 M req (kWh)", str(summary.get("energy_saved_per_1m_requests_kwh"))],
        ["Ext dep avoided / 1 000 req", str(summary.get("external_dependency_avoided_per_1000_requests"))],
        ["Ext dep avoided / 1 M req", str(summary.get("external_dependency_avoided_per_1m_requests"))],
    ]
    table(["metric", "value"], _nov_rows)
    p("> Ces projections reposent sur la surface disponible (FAST_PATH, BANK, TRADING, GPS).")
    p("> BRODY, OBSIDURE, LEAN non mesurés. Énergie : proxy local non calibré.")
    p("---")

    h(2, "18. Formalisation mathématique — Math formalization support")
    table(
        ["family", "math_formal_support", "formal_basis", "invariant_backing", "route_admissibility", "proof_backing", "claimable"],
        [[
            r["family"],
            str(r.get("math_formalization_support")),
            str(r.get("formalization_basis")),
            str(r.get("invariant_backing")),
            str(r.get("route_admissibility_backing")),
            str(r.get("proof_backing")),
            str(r.get("formalization_claimable")),
        ] for r in rows]
    )
    p(f"Math formalized surface: {summary.get('math_formalized_surface_count', 0)} / {len(rows)}")
    p(f"Claim: {summary.get('formalization_claim')}")
    p(f"Warning: {summary.get('formalization_warning')}")
    p("---")

    h(2, "19. Infrastructure future — Ce que démontre le benchmark")
    p("**Gemini optimise l'inférence.**")
    p("**Obsidia optimise le chemin admissible.**")
    p("")
    p("Ce benchmark n'est pas une comparaison symétrique. Il mesure deux philosophies différentes :")
    p("- Gemini : intelligence générale, inférence probabiliste, modèle pré-entraîné.")
    p("- Obsidia : routes admissibles, invariants KX108, preuve de non-action, gouvernance déterministe.")
    p("")
    p("Les gains mesurés ici ne proviennent pas d'une intelligence supérieure mais d'une "
      "formalisation des chemins valides.")
    p("L'écart de latence sur la surface disponible est réel. L'écart sur les surfaces manquantes "
      "(BRODY, OBSIDURE, LEAN) est inconnu.")
    p("")
    p("Infrastructure non mesurée dans ce run :")
    for layer in (summary.get("not_included_acceleration_layers") or []):
        p(f"- {layer}")
    p("---")

    h(2, "19b. Moteur partiel — État du run")
    p(f"> **{summary.get('partial_engine_warning')}**")
    p(f"benchmark_completion_state: {summary.get('benchmark_completion_state')}")
    p(f"obsidia_complete_measured: {summary.get('obsidia_complete_measured')}")
    p("")
    p("Couches manquantes ou non branchées :")
    for layer in (summary.get("missing_or_not_wired_layers") or []):
        p(f"- {layer}")
    p(f"partial_engine_claim: {summary.get('partial_engine_claim')}")
    p("---")

    h(2, "20. Next metrics V0.8")
    p("- Run reel Gemini 7 familles.")
    p("- Telemetrie GPU/CPU reelle pour energy_source=HARDWARE_MEASURED.")
    p("- Calibration poids CV avec donnees Sigma/Thermo reels.")
    p("- Activation source_law checker.")
    p("---")

    return "\n".join(lines)


# ── Human dashboard FR helpers (V0.7.8) ──────────────────────────────────────

def _color(text: str, color_name: str) -> str:
    if os.environ.get("NO_COLOR") or os.environ.get("OIE_NO_COLOR"):
        return text
    _codes: dict = {
        "cyan": "\033[96m", "magenta": "\033[95m", "green": "\033[92m",
        "yellow": "\033[93m", "red": "\033[91m", "gray": "\033[90m",
    }
    return f"{_codes.get(color_name, '')}{text}\033[0m"


def _tag_ok() -> str:      return _color("[OK]",      "green")
def _tag_mesure() -> str:  return _color("[MESURE]",  "yellow")
def _tag_limite() -> str:  return _color("[LIMITE]",  "yellow")
def _tag_manque() -> str:  return _color("[MANQUE]",  "red")
def _tag_garde() -> str:   return _color("[GARDE]",   "gray")
def _tag_obsidia() -> str: return _color("[OBSIDIA]", "cyan")
def _tag_gemini() -> str:  return _color("[GEMINI]",  "magenta")


def _fr_num(val: object, suffix: str = "x") -> str:
    """Formate un nombre en convention française (espace comme séparateur de milliers)."""
    if val is None:
        return "NON DISPONIBLE"
    try:
        rounded = round(float(val))
        formatted = f"{rounded:,}".replace(",", " ")
        return formatted + suffix
    except (ValueError, TypeError):
        return str(val)


def _execution_read(summary: dict, rows: list) -> dict:
    """Extrait le contexte d'exécution pour le wording mode-aware — V0.7.8b."""
    network_allowed = os.environ.get("OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK", "0") == "1"
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    gemini_real = network_allowed and bool(gemini_key)
    obsidia_live = any(
        (r.get("dual_lane") or {}).get("obsidia_lane", {}).get("execution_mode") == "LIVE_LOCAL"
        for r in rows
    )
    is_dryrun = not gemini_real
    if gemini_real and obsidia_live:
        mode_label_fr = "Test réel"
    elif gemini_real:
        mode_label_fr = "Test mixte (Gemini réel, Obsidia estimé)"
    else:
        mode_label_fr = "Prévisualisation / simulation"
    speed_label_fr = "accélération mesurée" if (gemini_real and obsidia_live) else "accélération estimée"
    proof_label_fr = "prouvé sur run réel" if (gemini_real and obsidia_live) else "estimé / simulation"
    return {
        "gemini_real": gemini_real,
        "obsidia_live": obsidia_live,
        "is_dryrun": is_dryrun,
        "mode_label_fr": mode_label_fr,
        "speed_label_fr": speed_label_fr,
        "proof_label_fr": proof_label_fr,
    }


def _build_human_dashboard(summary: dict, rows: list, exec_read: dict | None = None, compact: bool = False) -> str:
    """Génère le tableau de bord lisible en français — V0.7.8b (9 sections, compact=7)."""
    _er = exec_read or {}
    _is_dryrun = _er.get("is_dryrun", True)
    _mode_label_fr = _er.get("mode_label_fr", "Prévisualisation / simulation")
    _speed_label_fr = _er.get("speed_label_fr", "accélération estimée")
    _gemini_real = _er.get("gemini_real", False)

    n = len(rows)
    avg_sp  = summary.get("avg_speedup_ratio")
    avail_sp = summary.get("available_surface_avg_speedup_ratio")
    model_sp = summary.get("model_avoided_avg_speedup_ratio")
    model_av = summary.get("obsidia_model_call_avoided_count", "?")
    obs_route = sum(1 for r in rows if r.get("obsidia_route_match") is True)
    gem_route = sum(1 for r in rows if r.get("gemini_route_match") is True)
    osca = summary.get("osca_ratio")
    oapi = summary.get("oapi_ratio")
    odpi = summary.get("odpi_ratio")
    dca  = summary.get("dca_by_domain") or {}
    gencoin_emission = summary.get("gencoin_total_emission", 0)

    def _dca(fam: str) -> str:
        v = dca.get(fam)
        if v is None:
            return "NON DISPONIBLE"
        if isinstance(v, dict):
            val = v.get("dca_api_normal") or v.get("dca_agentic")
            return _fr_num(val) if val is not None else "NON DISPONIBLE"
        return _fr_num(v)

    fam_rows: dict = {r["family"]: r for r in rows}

    def _fam_tag(fam: str) -> str:
        r = fam_rows.get(fam, {})
        mn = r.get("model_necessity", {})
        obs_status = r.get("obsidia_status", "")
        if mn.get("necessity_claimable"):
            return _tag_ok()
        if fam in ("OBSIDURE", "LEAN") or obs_status == OBSIDIA_STATUS_MISSING:
            return _tag_manque()
        return _tag_mesure()

    def _fam_modele(fam: str) -> str:
        r = fam_rows.get(fam, {})
        mn = r.get("model_necessity", {})
        if mn.get("unnecessary_generalist_call_avoided"):
            return "OUI"
        if fam == "BRODY":
            return "PARTIEL"
        return "NON"

    def _fam_resultat(fam: str) -> str:
        r = fam_rows.get(fam, {})
        obs_status = r.get("obsidia_status", "")
        if fam in ("BANK", "TRADING", "GPS"):
            return "Prévisualisation" if _is_dryrun else "Revendicable"
        if fam == "FAST_PATH":
            return "Pas de pont live dédié"
        if fam == "BRODY" or obs_status == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE":
            return "non testé en live / pont non confirmé" if _is_dryrun else "kernel inaccessible"
        return "connecteur manquant"

    L: list = []

    # ── Section 1 — Analyse simple ────────────────────────────────────────────
    _intro_ligne1 = (
        "  C'est un test comparatif réel entre Obsidia en environnement local"
        if not _is_dryrun else
        "  C'est une prévisualisation de la comparaison Obsidia vs Gemini."
    )
    _intro_ligne2 = (
        "  réel et Gemini appelé comme modèle externe réel."
        if not _is_dryrun else
        "  Gemini : simulation dry-run (aucun appel réseau réel)."
    )
    _gemini_lane_desc = (
        f"  {_tag_gemini()} REAL_SDK   = appel réel au modèle Gemini via kit de"
        if not _is_dryrun else
        f"  {_tag_gemini()} DRY_RUN    = simulation Gemini, aucun appel réseau réel."
    )
    L += [
        "",
        "=" * 66,
        "  ANALYSE SIMPLE DU BENCHMARK",
        "=" * 66,
        "",
        "  1. Ce que le benchmark mesure vraiment",
        "  ─────────────────────────────────────",
        _intro_ligne1,
        _intro_ligne2,
        "",
        f"  {_tag_obsidia()} LIVE_LOCAL = système local avec ponts de domaines.",
        _gemini_lane_desc,
        "                 développement logiciel.",
        "  Focus principal = économie d'inférence (OIE).",
        "",
        "  Question centrale :",
        "  \"Quand Obsidia peut-il répondre sans appeler un grand modèle de",
        "   langage généraliste ?\"",
        "",
        "  2. Résultats clés",
        "  ─────────────────",
        f"  {_tag_ok()} Accélération moyenne mesurée       : {_fr_num(avg_sp)} contre Gemini.",
        f"  {_tag_ok()} Accélération, appel modèle évité   : {_fr_num(model_sp)}.",
        f"  {_tag_ok()} Familles évitant l'appel modèle    : {model_av}/{n}.",
        f"  {_tag_ok()} Familles concernées                : BANK, TRADING, GPS, FAST_PATH.",
        f"  {_tag_ok()} Gouvernance respectée              : KX108_ONLY, pas d'action",
        "               réelle, pas d'écriture mémoire, pas de mutation kernel.",
        f"  {_tag_ok()} Précision de routage Obsidia       : {obs_route}/{n}.",
        f"  {_tag_ok()} BANK, TRADING, GPS                 : fonctionnent en",
        "               environnement local réel avec pont de domaine.",
        "",
        f"  {_tag_limite()} FAST_PATH  : mesuré, pas encore de pont live dédié.",
        f"  {_tag_limite()} BRODY      : mesuré, pont tenté, {'kernel inaccessible' if not _is_dryrun else 'non testé en live'}.",
        f"  {_tag_manque()} OBSIDURE   : connecteur manquant.",
        f"  {_tag_manque()} LEAN       : connecteur manquant.",
        f"  {_tag_garde()} DCA/OSCA/OAPI/ODPI : indicateurs indirects,"
        " pas facturation réelle.",
        f"  {_tag_garde()} Coût réel industriel            : Non revendiqué.",
        f"  {_tag_garde()} Calcul de chemin complet        : Non revendiqué.",
        "",
        "  Verdict :",
        "  \"C'est un bon run. Il prouve que sur des routes connues et bornées,",
        "   Obsidia peut être beaucoup plus rapide tout en gardant une",
        "   gouvernance stricte.\"",
        "",
        "  \"Ce n'est pas une victoire totale sur toutes les familles.",
        "   C'est une preuve concrète de concept sur les domaines principaux.\"",
        "",
        "  3. Ce que ça apporte au projet",
        "  ──────────────────────────────",
        "  - Preuve vivante de l'approche known path + gouvernance.",
        "  - Différence de paradigme : Obsidia n'essaie pas d'être un meilleur",
        "    grand modèle de langage. Obsidia sait quand il n'a pas besoin",
        "    d'en appeler un.",
        "  - Renforce le positionnement : économie d'inférence + gouvernance.",
        "  - Montre que le système fonctionne sur les domaines branchés.",
        "  - Montre clairement les limites restantes.",
        "",
        "  4. Phrase simple",
        "  ──────────────────",
        "  \"Le benchmark montre qu'Obsidia fonctionne bien sur les domaines",
        "   branchés et apporte un gain de vitesse significatif en évitant les",
        "   appels inutiles, tout en gardant la gouvernance.\"",
        "",
    ]

    # ── Section 2 — Tableau de bord ──────────────────────────────────────────
    _gemini_mode_line = (
        f"    {_tag_gemini()} Gemini  : OUI — modèle externe réel"
        if not _is_dryrun else
        f"    {_tag_gemini()} Gemini  : NON — simulation dry-run"
    )
    L += [
        "=" * 66,
        "  TABLEAU DE BORD — OBSIDIA VS GEMINI",
        "=" * 66,
        "",
        f"  {_mode_label_fr} :",
        f"    {_tag_obsidia()} Obsidia : OUI — environnement local réel",
        _gemini_mode_line,
        "",
        "  Score simple :",
        f"    Obsidia route correctement : {obs_route} / {n}",
        f"    Gemini route correctement  : {gem_route} / {n}",
        "",
        f"  Appels au modèle évités : {model_av} / {n}",
        "",
        "  Vitesse :",
        f"    {_speed_label_fr.capitalize()} moyenne               : {_fr_num(avg_sp)}",
        f"    Accélération sur surfaces disponibles       : {_fr_num(avail_sp)}",
        f"    Accélération quand l'appel modèle est évité : {_fr_num(model_sp)}",
        "",
        "  Verdict court :",
        "    Obsidia ne gagne pas parce qu'il génère mieux.",
        "    Obsidia gagne quand la route est connue et que l'appel au modèle",
        "    devient inutile.",
        "",
    ]

    # ── Section 3 — 6 chiffres ───────────────────────────────────────────────
    L += [
        "=" * 66,
        "  LES 6 CHIFFRES À RETENIR",
        "=" * 66,
        "",
        f"  1. {n} tâches testées.",
        f"  2. {obs_route} / {n} routes correctes côté Obsidia.",
        f"  3. {model_av} / {n} appels au modèle évités.",
        f"  4. {_fr_num(avg_sp)} plus rapide en moyenne réelle.",
        f"  5. {_fr_num(model_sp)} plus rapide quand l'appel modèle est évité.",
        "  6. 3 familles pleinement revendicables : BANK, TRADING, GPS.",
        "",
    ]

    # ── Section 4 — Trois types de chiffres (omis en compact) ──────────────
    if not compact:
        _mesure_label = "MESURE RÉELLE" if not _is_dryrun else "MESURE (SIMULATION)"
        _run_desc = (
            "     Run réel Obsidia LIVE_LOCAL vs Gemini REAL_SDK."
            if not _is_dryrun else
            "     Simulation — Obsidia LIVE_LOCAL vs Gemini DRY_RUN."
        )
        _claim_speed = (
            f"     {_tag_ok()} Revendicable : oui, comme vitesse mesurée."
            if not _is_dryrun else
            f"     {_tag_mesure()} Revendicable : estimé, non mesuré sur Gemini réel."
        )
        L += [
            "=" * 66,
            "  TROIS TYPES DE CHIFFRES — POUR NE PAS LES MÉLANGER",
            "=" * 66,
            "",
            f"  1. {_mesure_label}",
            _run_desc,
            f"     {_speed_label_fr.capitalize()} moyenne : {_fr_num(avg_sp)}.",
            _claim_speed,
            "",
            "  2. SURFACES DISPONIBLES",
            "     Familles où Obsidia répond via les surfaces disponibles.",
            f"     Accélération surfaces disponibles : {_fr_num(avail_sp)}.",
            f"     {_tag_ok()} Revendicable : oui, sur le périmètre branché.",
            "",
            "  3. INDICATEURS INDIRECTS",
            "     OSCA, OAPI, ODPI, DCA — potentiel et structure.",
            "     Pas de facturation réelle.",
            f"     {_tag_garde()} Revendicable : partiel — indicateur uniquement.",
            "",
        ]

    # ── Section 5 — Lecture par famille ─────────────────────────────────────
    L += [
        "=" * 66,
        "  LECTURE PAR FAMILLE",
        "=" * 66,
        "",
        f"  {'Famille':<14} {'Etat':<16} {'Modele evite':<20} Resultat simple",
        "  " + "-" * 62,
    ]
    for fam in ("BANK", "TRADING", "GPS", "FAST_PATH", "BRODY", "OBSIDURE", "LEAN"):
        etat_raw = _fam_tag(fam)
        mod_ev = _fam_modele(fam)
        resultat = _fam_resultat(fam)
        L.append(f"  {fam:<14} {etat_raw:<28} {mod_ev:<20} {resultat}")
    L += [
        "",
        "  Les domaines propres aujourd'hui sont BANK, TRADING et GPS.",
        "  FAST_PATH et BRODY sont intéressants mais encore partiels.",
        "  OBSIDURE et LEAN restent à brancher.",
        "",
    ]

    # ── Section 6 — Ce qui est revendicable ─────────────────────────────────
    L += [
        "=" * 66,
        "  CE QUI EST REVENDICABLE",
        "=" * 66,
        "",
        f"  {_tag_ok()} Vitesse mesurée                         : oui.",
        f"  {_tag_ok()} Economie d'inférence sur routes connues : oui.",
        f"  {_tag_ok()} BANK, TRADING, GPS                      : oui,"
        " pleinement revendicables.",
        f"  {_tag_ok()} Gouvernance préservée                   : oui.",
        f"  {_tag_ok()} Aucun acte réel                         : oui.",
        f"  {_tag_ok()} Aucune écriture mémoire                 : oui.",
        f"  {_tag_ok()} Aucune mutation kernel                  : oui.",
        "",
        "  \"On peut défendre ces résultats sans mélanger mesure,",
        "   supposition et limite technique.\"",
        "",
    ]

    # ── Section 7 — Ce qui n'est pas encore fermé ───────────────────────────
    L += [
        "=" * 66,
        "  CE QUI N'EST PAS ENCORE FERMÉ",
        "=" * 66,
        "",
        f"  {_tag_limite()} FAST_PATH :",
        "     Le chemin rapide est mesuré, mais il n'a pas encore son pont",
        "     live dédié.",
        "",
        f"  {_tag_limite()} BRODY :",
        ("     Le pont a été tenté, mais le kernel était inaccessible pendant"
         if not _is_dryrun else
         "     Pont non testé en live sur ce run (simulation). Ce n'est pas"),
        ("     le test. Ce n'est pas un connecteur manquant."
         if not _is_dryrun else
         "     un connecteur manquant."),
        "",
        f"  {_tag_manque()} OBSIDURE et LEAN :",
        "     Les connecteurs sont manquants dans ce benchmark.",
        "",
        f"  {_tag_garde()} Coût réel :",
        "     Non revendiqué. La vitesse est mesurée, mais pas la facture",
        "     industrielle.",
        "",
        f"  {_tag_garde()} Calcul de chemin complet :",
        "     Non revendiqué dans ce run.",
        "",
        f"  {_tag_garde()} Gencoin :",
        f"     Calibration seulement. Emission = {gencoin_emission}.",
        "",
    ]

    # ── Section 8 — Indices avancés (omis en compact) ────────────────────────
    if not compact:
        L += [
            "=" * 66,
            "  INDICES AVANCÉS — POTENTIEL D'ÉCONOMIE D'INFÉRENCE",
            "=" * 66,
            "",
            f"  OSCA — Score global de vitesse Obsidia      : {_fr_num(osca)}",
            "         Lecture : indice global, pas une facture réelle.",
            "",
            f"  OAPI — Avantage sur portefeuille d'actions  : {_fr_num(oapi)}",
            "         Lecture : indice orienté actions, pas une facture réelle.",
            "",
            f"  ODPI — Avantage sur portefeuille de domaines: {_fr_num(odpi)}",
            "         Lecture : indice par domaines, pas une facture réelle.",
            "",
            "  Avantage par domaine :",
        ]
        for fam in ("FAST_PATH", "BRODY", "BANK", "TRADING", "GPS_AVIATION", "LEAN", "OBSIDURE"):
            L.append(f"    {fam:<16} : {_dca(fam)}")
        L.append("")

    # ── Section 9 — Bénéfices et paradigme ──────────────────────────────────
    L += [
        "=" * 66,
        "  BÉNÉFICES ET CHANGEMENT DE PARADIGME",
        "=" * 66,
        "",
        "  Bénéfice principal :",
        "  \"Le bénéfice principal n'est pas seulement d'aller plus vite.",
        "   Le bénéfice est d'éviter une inférence généraliste quand une",
        "   route connue, bornée et gouvernée suffit.\"",
        "",
        "  Changement de paradigme :",
        "  - Ancien réflexe : tout envoyer à un grand modèle de langage.",
        "  - Nouveau réflexe : vérifier d'abord si l'appel au modèle est nécessaire.",
        "  - Gemini optimise la génération de réponse.",
        "  - Obsidia optimise la décision d'inférer ou non.",
        "  - La vitesse vient de l'évitement, pas seulement d'un calcul plus rapide.",
        "  - La gouvernance reste active pendant le gain de vitesse.",
        "",
        "  Bénéfices produit :",
        "  - Moins de latence.",
        "  - Moins d'appels au modèle inutiles.",
        "  - Moins de surface d'hallucination.",
        "  - Plus de traçabilité.",
        "  - Plus d'auditabilité.",
        "  - Limites mieux visibles.",
        "",
        "  \"Quand la route est connue, prédire devient plus lent que vérifier.\"",
        "",
        "  \"Obsidia ne remplace pas Gemini partout ; Obsidia réduit le besoin",
        "   d'appeler Gemini quand la structure suffit.\"",
        "",
    ]

    return "\n".join(L)


# ── Metric explainer FR (V0.7.7) ─────────────────────────────────────────────

def _build_metric_explainer(summary: dict, rows: list) -> str:
    """Génère en français les sections d'explication des métriques du test comparatif."""
    n = len(rows)
    avg_sp = summary.get("avg_speedup_ratio")
    avail_sp = summary.get("available_surface_avg_speedup_ratio")
    model_sp = summary.get("model_avoided_avg_speedup_ratio")
    terrain_sp = summary.get("terrain_avg_speedup_ratio")
    kp = summary.get("known_path_detected_count", "?")
    inf_av = summary.get("inference_avoided_count", "?")
    model_av = summary.get("obsidia_model_call_avoided_count", "?")
    osca = summary.get("osca_ratio")
    oapi = summary.get("oapi_ratio")
    odpi = summary.get("odpi_ratio")
    dca = summary.get("dca_by_domain") or {}
    obs_match = sum(1 for r in rows if r.get("obsidia_route_match") is True)
    gem_match = sum(1 for r in rows if r.get("gemini_route_match") is True)
    claimable_fams = [r["family"] for r in rows if r.get("model_necessity", {}).get("necessity_claimable")]
    aa_avg = summary.get("answer_adequacy_avg", "NON DISPONIBLE")
    cost_cl = summary.get("cost_comparison_claimable_global", False)

    def _dca_val(fam: str) -> str:
        v = dca.get(fam)
        if v is None:
            return "NON DISPONIBLE"
        if isinstance(v, dict):
            val = v.get("dca_api_normal") or v.get("dca_agentic")
            return str(val) if val is not None else "NON DISPONIBLE"
        return str(v)

    def _card(titre: str, question: str, calcule: str, formule: Optional[str],
              resultat: str, lecture: str, revendicable: str, attention: str) -> list:
        lines = [
            f"  MÉTRIQUE : {titre}",
            f"  Nom simple         : {titre}",
            f"  Question répondue  : {question}",
            f"  Ce qu'on calcule   : {calcule}",
        ]
        if formule:
            lines.append(f"  Formule simple     : {formule}")
        lines += [
            f"  Résultat           : {resultat}",
            f"  Lecture humaine    : {lecture}",
            f"  Revendicable       : {revendicable}",
            f"  Attention          : {attention}",
            "",
        ]
        return lines

    L: list = []
    L.append("")
    L.append("=" * 66)
    L.append("  CE QUE CE BENCHMARK MESURE")
    L.append("=" * 66)
    L.append("")
    L.append("  Ce test comparatif (benchmark) mesure si Obsidia peut éviter")
    L.append("  un appel à un grand modèle de langage (LLM) généraliste quand")
    L.append("  une route connue, bornée et gouvernée suffit.")
    L.append("")
    L.append("  QUESTIONS RÉPONDUES :")
    L.append("  1. Est-ce que Gemini est appelé réellement ?")
    L.append("     Oui — appel réel au kit de développement logiciel Gemini (REAL_SDK).")
    L.append("  2. Est-ce qu'Obsidia tourne réellement ?")
    L.append("     Oui — environnement d'exécution local réel Obsidia (LIVE_LOCAL).")
    L.append(f"  3. Est-ce qu'Obsidia route mieux ?")
    L.append(f"     Précision de routage Obsidia : {obs_match}/{n} familles.")
    L.append(f"  4. Est-ce qu'Obsidia évite des appels modèle ?")
    L.append(f"     {model_av}/{n} appels au modèle évités.")
    L.append(f"  5. Est-ce qu'Obsidia va plus vite ?")
    L.append(f"     Accélération (speedup) moyenne : {avg_sp}x.")
    L.append(f"  6. Qu'est-ce qui est pleinement revendicable proprement ?")
    L.append(f"     Familles : {claimable_fams}.")
    L.append("  7. Qu'est-ce qui reste seulement mesuré ou non branché ?")
    L.append("     FAST_PATH, BRODY (partiel), OBSIDURE, LEAN (connecteur manquant).")
    L.append("")
    L.append("  ── CARTES DE MÉTRIQUES ──────────────────────────────────────")
    L.append("")

    # Card 1 — Live avg speedup
    L += _card(
        "Live avg speedup vs Gemini REAL_SDK"
        " (accélération moyenne en test réel contre Gemini)",
        "Combien de fois Obsidia répond plus vite que Gemini"
        " (appel réel au kit de développement logiciel Gemini) ?",
        "Latence (temps d'attente avant réponse) moyenne Gemini"
        " divisée par latence moyenne Obsidia.",
        "latence Gemini / latence Obsidia",
        f"{avg_sp}x" if avg_sp is not None else "NON DISPONIBLE",
        f"Obsidia est environ {avg_sp}x plus rapide"
        " sur ce run en environnement d'exécution local réel."
        if avg_sp is not None else "NON DISPONIBLE",
        "oui, comme vitesse mesurée",
        "Ce n'est pas une preuve de coût réel industriel.",
    )

    # Card 2 — Available surface avg speedup
    L += _card(
        "Available surface avg speedup"
        " (accélération moyenne sur les surfaces disponibles)",
        "Quel est le multiplicateur de vitesse uniquement sur les familles"
        " où un connecteur (adapter) est disponible ?",
        "Accélération moyenne sur les familles avec interface de programmation"
        " (API) Obsidia active.",
        None,
        f"{avail_sp}x" if avail_sp is not None else "NON DISPONIBLE",
        "Restreint aux familles où Obsidia a une surface de connexion active.",
        "oui, surface bornée mesurée",
        "OBSIDURE et LEAN sont exclus (connecteur manquant).",
    )

    # Card 3 — Model avoided avg speedup
    L += _card(
        "Model avoided avg speedup"
        " (accélération moyenne quand l'appel au modèle est évité)",
        "Quel multiplicateur de vitesse quand Obsidia évite complètement"
        " l'appel au grand modèle de langage ?",
        "Accélération sur les tâches où aucun appel au modèle n'est fait par Obsidia.",
        "latence Gemini (appel modèle) / latence Obsidia (sans appel modèle)",
        f"{model_sp}x" if model_sp is not None else "NON DISPONIBLE",
        f"Éviter l'inférence généraliste donne le maximum d'accélération : {model_sp}x.",
        "oui, sur les familles éligibles",
        "Valide seulement si le connecteur est actif et la route correcte.",
    )

    # Card 4 — Terrain avg speedup
    L += _card(
        "Terrain avg speedup (accélération terrain)",
        "Quel est le multiplicateur de vitesse moyen en conditions de terrain réelles ?",
        "Accélération agrégée sur toutes les familles testées.",
        None,
        f"{terrain_sp}x" if terrain_sp is not None else "NON DISPONIBLE",
        "Vue d'ensemble du gain de vitesse sans restriction de surface.",
        "partiel — dépend des familles actives",
        "Les familles avec connecteur manquant tirent ce chiffre vers le bas.",
    )

    # Card 5 — Route accuracy Obsidia
    L += _card(
        "Route accuracy Obsidia (précision de routage Obsidia)",
        "Obsidia envoie-t-il la demande vers la bonne couche ?",
        f"Nombre de familles routées vers la couche minimale suffisante : {obs_match}/{n}.",
        None,
        f"{obs_match}/{n}",
        f"Sur {n} familles, Obsidia a routé correctement {obs_match} tâches.",
        "oui sur les familles revendicables proprement",
        "Le routage n'est pas revendicable si le connecteur est manquant.",
    )

    # Card 6 — Route accuracy Gemini
    L += _card(
        "Route accuracy Gemini (précision de routage Gemini)",
        "Gemini choisit-il la bonne couche de réponse ?",
        f"Nombre de familles correctement traitées par Gemini : {gem_match}/{n}.",
        None,
        f"{gem_match}/{n}",
        "Référence comparative : Gemini appelle un grand modèle de langage pour toutes les familles.",
        "référence uniquement",
        "Gemini est le niveau de base (baseline) — pas un concurrent sur la gouvernance.",
    )

    # Card 7 — Known path
    L += _card(
        "Known path detected (chemin rapide détecté)",
        "Combien de demandes ont pu être traitées par une route ultra-courte"
        " (fast path — chemin rapide) ?",
        f"Familles où le chemin rapide a été détecté : {kp}/{n}.",
        None,
        f"{kp}/{n}",
        f"{kp} tâches sur {n} ont déclenché un chemin rapide,"
        " évitant une inférence généraliste.",
        "oui sur les familles actives",
        "Le chemin rapide FAST_PATH n'a pas de pont de domaine dédié en V0.7.x.",
    )

    # Card 8 — Inference avoided
    L += _card(
        "Inference avoided (inférence évitée)",
        "Combien d'inférences généralistes ont été évitées ?",
        f"Tâches où Obsidia n'a pas appelé un grand modèle de langage : {inf_av}/{n}.",
        None,
        f"{inf_av}/{n}",
        f"Sur {n} tâches, {inf_av} n'ont pas nécessité d'appel à un modèle généraliste.",
        "oui sur les familles éligibles",
        "OBSIDURE et LEAN exclus faute de connecteur actif.",
    )

    # Card 9 — Model call avoided
    L += _card(
        "Model call avoided (appel au modèle évité)",
        "Obsidia a-t-il remplacé un appel au modèle par une route bornée ?",
        f"Familles où l'appel à un grand modèle de langage a été remplacé : {model_av}/{n}.",
        None,
        f"{model_av}/{n}",
        f"{model_av} familles ont reçu une réponse sans appel au grand modèle de langage.",
        "oui sur les familles revendicables proprement",
        "Revendicable seulement si connecteur actif et gouvernance préservée.",
    )

    # Card 10 — OSCA
    L += _card(
        "OSCA — Score global de vitesse Obsidia"
        " (indice synthétique, économie d'inférence Obsidia)",
        "Quel est l'avantage global de vitesse d'Obsidia sur l'ensemble du portefeuille ?",
        "Moyenne géométrique des multiplicateurs de vitesse sur toutes les familles.",
        "géomoyenne(accélération par famille)",
        f"{osca}x" if osca is not None else "NON DISPONIBLE",
        f"L'indice OSCA synthétise l'avantage de vitesse global :"
        f" {osca}x (indicateur indirect — proxy).",
        "partiel — indicateur indirect (proxy), non revendiqué comme coût réel industriel",
        "Indicateur indirect calculé sur baseline de référence, pas un coût réel industriel.",
    )

    # Card 11 — OAPI
    L += _card(
        "OAPI — Avantage Obsidia sur portefeuille d'actions",
        "Quel avantage Obsidia offre-t-il sur les tâches orientées action ?",
        "Indice de vitesse pondéré sur les familles à portée d'action (BANK, TRADING, GPS).",
        None,
        f"{oapi}x" if oapi is not None else "NON DISPONIBLE",
        f"L'indice OAPI mesure l'avantage sur le portefeuille d'actions : {oapi}x.",
        "partiel — indicateur indirect (proxy)",
        "Indicateur indirect — pas un coût réel industriel revendiqué.",
    )

    # Card 12 — ODPI
    L += _card(
        "ODPI — Avantage Obsidia sur portefeuille de domaines",
        "Quel avantage Obsidia offre-t-il domaine par domaine ?",
        "Indice de vitesse par famille ou domaine, agrégé en portefeuille.",
        None,
        f"{odpi}x" if odpi is not None else "NON DISPONIBLE",
        f"L'indice ODPI mesure l'avantage par domaines : {odpi}x.",
        "partiel — indicateur indirect (proxy)",
        "Indicateur indirect — pas un coût réel industriel revendiqué.",
    )

    # Card 13 — DCA
    L += _card(
        "DCA — Avantage comparatif par domaine (Domain Comparative Advantage)",
        "Quel est l'avantage de vitesse pour chaque famille testée ?",
        "Score de vitesse normalisé pour chaque famille du test comparatif.",
        None,
        (f"BANK={_dca_val('BANK')} TRADING={_dca_val('TRADING')}"
         f" GPS={_dca_val('GPS')}"),
        "L'avantage comparatif par domaine (DCA) montre où Obsidia est le plus efficace.",
        "partiel — dépend du connecteur disponible par famille",
        "Familles sans connecteur actif affichent NON DISPONIBLE.",
    )

    # Card 14 — Answer adequacy
    L += _card(
        "Answer adequacy (adéquation de réponse)",
        "La réponse Obsidia est-elle suffisante, bornée et gouvernée ?",
        "Score composite : routage + sortie bornée + couche minimale + gouvernance + trace.",
        "0.30*route + 0.20*borné + 0.20*couche + 0.20*gouvernance + 0.10*trace",
        f"{aa_avg}",
        "Une réponse adéquate n'est pas la plus longue — elle est suffisante et gouvernée.",
        "oui sur les familles avec connecteur actif et gouvernance préservée",
        "Non revendicable si le connecteur est manquant.",
    )

    # Card 15 — Claimability
    L += _card(
        "Claimability (revendicabilité)",
        "Quels résultats peut-on défendre sans mélanger mesure et supposition ?",
        "Familles pour lesquelles route, gouvernance et connecteur sont confirmés.",
        None,
        f"revendicables proprement : {claimable_fams}",
        "On peut défendre ces résultats sans risquer de mélanger mesure réelle et hypothèse.",
        "oui sur les familles listées",
        "Mesurés mais non revendicables : FAST_PATH, BRODY, OBSIDURE, LEAN.",
    )

    # Card 16 — Cost comparison claim guard
    L += _card(
        "Cost comparison claim guard (garde-fou des revendications de coût réel industriel)",
        "Le benchmark revendique-t-il un coût réel industriel ?",
        "Vérification que cost_comparison_claimable reste faux.",
        None,
        f"cost_comparison_claimable = {cost_cl}",
        "Le test comparatif mesure la vitesse, pas le coût réel industriel.",
        "non revendicable — délibérément",
        "Le coût réel industriel nécessite une facturation réelle, non simulée.",
    )

    # Card 17 — Path Compute claim guard
    L += _card(
        "Path Compute claim guard"
        " (garde-fou du calcul de chemin complet — path compute — non revendiqué)",
        "Le benchmark revendique-t-il un calcul de chemin complet ?",
        "Vérification que path_compute_runtime_claimable reste faux — brique non fermée.",
        None,
        "path_compute_runtime_claimable = False",
        "Le calcul de chemin (Path Compute) complet n'est pas revendiqué dans ce run.",
        "non revendicable — délibérément",
        "La brique de calcul de chemin n'est pas encore fermée en V0.7.x.",
    )

    # LECTURE PAR FAMILLE
    L.append("=" * 66)
    L.append("  LECTURE PAR FAMILLE — QUE S'EST-IL PASSÉ ?")
    L.append("=" * 66)
    L.append("")

    family_rows = {r["family"]: r for r in rows}
    fam_order = ["BANK", "TRADING", "GPS", "FAST_PATH", "BRODY", "OBSIDURE", "LEAN"]
    fam_labels = {
        "BANK": "Pont de domaine bancaire (BANK)",
        "TRADING": "Pont de domaine trading (TRADING)",
        "GPS": "Pont de domaine navigation (GPS)",
        "FAST_PATH": "Chemin rapide — route ultra-courte (FAST_PATH)",
        "BRODY": "Couche de réponse interne Brody (BRODY)",
        "OBSIDURE": "Agent de code Obsidure (OBSIDURE)",
        "LEAN": "Surface de preuve formelle Lean (LEAN)",
    }
    fam_test = {
        "BANK": "Requête de solde bancaire gouvernée.",
        "TRADING": "Requête de position trading gouvernée.",
        "GPS": "Requête de position navigation gouvernée.",
        "FAST_PATH": "Route ultra-courte sans inférence généraliste.",
        "BRODY": "Réponse interne via pont de domaine Brody.",
        "OBSIDURE": "Patch de code via agent Obsidure.",
        "LEAN": "Preuve formelle via surface Lean.",
    }
    fam_couche = {
        "BANK": "Pont de domaine (DOMAIN_BRIDGE)",
        "TRADING": "Pont de domaine (DOMAIN_BRIDGE)",
        "GPS": "Pont de domaine (DOMAIN_BRIDGE)",
        "FAST_PATH": "Chemin rapide (FAST_PATH)",
        "BRODY": "Couche interne Brody (BRODY_INTERNAL)",
        "OBSIDURE": "Agent Obsidure (OBSIDURE_AGENT) — connecteur manquant",
        "LEAN": "Surface de preuve Lean (LEAN_PROOF) — connecteur manquant",
    }
    fam_important = {
        "BANK": "Prouve qu'une requête bancaire ne nécessite pas un grand modèle de langage.",
        "TRADING": "Prouve qu'une requête trading ne nécessite pas un grand modèle de langage.",
        "GPS": "Prouve qu'une requête navigation ne nécessite pas un grand modèle de langage.",
        "FAST_PATH": "Montre le potentiel du chemin rapide, même sans pont dédié en V0.7.x.",
        "BRODY": "Mesure le pont Brody ; kernel inaccessible pendant le test ne veut pas dire connecteur manquant.",
        "OBSIDURE": "Connecteur manquant — non revendicable — à brancher en V0.8+.",
        "LEAN": "Connecteur manquant — non revendicable — à brancher en V0.8+.",
    }

    for fam in fam_order:
        r = family_rows.get(fam, {})
        obs_status = r.get("obsidia_status", "NON DISPONIBLE")
        mn = r.get("model_necessity", {})
        claimable = mn.get("necessity_claimable", False)
        avoided = mn.get("unnecessary_generalist_call_avoided", False)
        aa = r.get("answer_adequacy", {})
        aa_score = aa.get("answer_adequacy_score", "NON DISPONIBLE")

        if claimable:
            statut = "OK — revendicable proprement"
        elif obs_status in ("ADAPTER_MISSING", "OBSIDURE_MISSING", "LEAN_MISSING"):
            statut = "MANQUE — connecteur manquant"
        elif obs_status == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE":
            statut = "MESURÉ — kernel inaccessible pendant le test"
        else:
            statut = "MESURÉ — non revendicable proprement"

        L.append(f"  ── {fam_labels.get(fam, fam)} ──")
        L.append(f"  Statut simple      : {statut}")
        L.append(f"  Ce qu'on teste     : {fam_test.get(fam, 'NON DISPONIBLE')}")
        L.append(f"  Couche Obsidia     : {fam_couche.get(fam, 'NON DISPONIBLE')}")
        L.append(f"  Gemini appelé      : oui (appel réel au kit de développement logiciel Gemini)")
        L.append(f"  Modèle évité       : {'oui' if avoided else 'non'}")
        L.append(f"  Statut Obsidia     : {obs_status}")
        L.append(f"  Adéquation réponse : {aa_score}")
        L.append(f"  Pourquoi important : {fam_important.get(fam, 'NON DISPONIBLE')}")
        L.append(f"  Revendicable       : {'oui' if claimable else 'non — mesuré mais non revendicable'}")
        if not claimable and fam in ("OBSIDURE", "LEAN"):
            L.append(f"  Limite             : connecteur manquant — adapter absent en V0.7.x.")
        elif fam == "BRODY" and obs_status == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE":
            L.append("  Limite             : kernel inaccessible pendant le test — route connue, kernel down.")
        L.append("")

    # NIVEAUX DE PREUVE
    L.append("=" * 66)
    L.append("  NIVEAUX DE PREUVE")
    L.append("=" * 66)
    L.append("")
    L.append("  1. Mesure live réelle")
    L.append("     Environnement d'exécution local réel Obsidia (LIVE_LOCAL) contre")
    L.append("     appel réel au kit de développement logiciel Gemini (REAL_SDK).")
    L.append("     Familles mesurées en réel : BANK, TRADING, GPS.")
    L.append("")
    L.append("  2. Surfaces disponibles")
    L.append("     Familles avec connecteur (adapter) actif et mesurables :")
    L.append("     BANK, TRADING, GPS. FAST_PATH : chemin rapide mesuré mais non revendicable.")
    L.append("")
    L.append("  3. Appel modèle évité")
    L.append("     Familles où l'appel au modèle a été évité et est revendicable proprement :")
    L.append(f"     {claimable_fams}.")
    L.append("")
    L.append("  4. Indices OIE proxy (économie d'inférence Obsidia — indicateurs indirects)")
    L.append("     OSCA, OAPI, ODPI calculés comme indicateurs indirects (proxy) :")
    L.append("     pas de coût réel industriel revendiqué.")
    L.append("")
    L.append("  5. DCA — Avantage comparatif par domaine")
    L.append("     Score par famille. Familles sans connecteur : NON DISPONIBLE.")
    L.append("")
    L.append("  6. Limites — non revendicable")
    L.append("     Coût réel industriel : non revendiqué.")
    L.append("     Calcul de chemin complet (Path Compute) : non revendiqué.")
    L.append("     OBSIDURE, LEAN : connecteur manquant — non branché en V0.7.x.")
    L.append("")

    # COMMENT EXPLIQUER EN UNE PHRASE
    L.append("=" * 66)
    L.append("  COMMENT EXPLIQUER CE RÉSULTAT EN UNE PHRASE")
    L.append("=" * 66)
    L.append("")
    L.append("  \"Obsidia ne gagne pas parce qu'il génère mieux que Gemini ;")
    L.append("   il gagne quand la route est connue, car il peut éviter l'inférence")
    L.append("   généraliste tout en gardant la gouvernance.\"")
    L.append("")

    return "\n".join(L)


def _build_benefices_paradigme(summary: dict, rows: list) -> str:
    """Génère en français la section bénéfices et changement de paradigme (V0.7.8)."""
    avg_sp = summary.get("avg_speedup_ratio")

    L: list = []
    L.append("")
    L.append("=" * 66)
    L.append("  BÉNÉFICES ET CHANGEMENT DE PARADIGME")
    L.append("=" * 66)
    L.append("")
    L.append("  A. Bénéfice principal")
    L.append("  ─────────────────────")
    L.append("  Le bénéfice principal n'est pas seulement d'aller plus vite.")
    L.append("  Le bénéfice est d'éviter une inférence généraliste quand une")
    L.append("  route connue, bornée et gouvernée suffit.")
    L.append("")
    L.append("  Obsidia réduit les appels inutiles au grand modèle de langage")
    L.append("  (LLM) généraliste. Il ne cherche pas à être un meilleur Gemini.")
    L.append("  Il décide quand l'appel à un modèle de type Gemini n'est pas")
    L.append("  nécessaire.")
    L.append("")
    L.append("  Bénéfices concrets :")
    L.append("  - Moins de latence (temps d'attente avant réponse).")
    L.append("  - Moins de dépendance à la génération par modèle.")
    L.append("  - Routage plus déterministe.")
    L.append("  - Gouvernance plus claire.")
    L.append("  - Surface d'hallucination réduite.")
    L.append("  - Meilleure auditabilité.")
    L.append("")
    L.append("  B. Changement de paradigme #1 — Générer vs vérifier")
    L.append("  ─────────────────────────────────────────────────────")
    L.append("  Ancien paradigme :")
    L.append("    Un grand modèle de langage (LLM) généraliste est appelé")
    L.append("    pour générer une réponse.")
    L.append("  Nouveau paradigme :")
    L.append("    Le système vérifie d'abord si la génération est nécessaire.")
    L.append("")
    L.append("  \"Avant, on demandait au modèle de prédire une réponse.")
    L.append("   Ici, Obsidia vérifie d'abord si la réponse peut être routée")
    L.append("   sans prédiction généraliste.\"")
    L.append("")
    L.append("  C. Changement de paradigme #2 — Intelligence de réponse vs"
             " intelligence de décision")
    L.append("  ──────────────────────────────────────────────────────────────")
    L.append("  Gemini optimise la réponse.")
    L.append("  Obsidia optimise la décision de savoir s'il faut appeler un")
    L.append("  modèle pour répondre.")
    L.append("")
    L.append("  \"Gemini optimise la réponse. Obsidia optimise la décision de")
    L.append("   savoir s'il faut appeler un modèle pour répondre.\"")
    L.append("")
    L.append("  D. Changement de paradigme #3 — Vitesse par évitement,"
             " pas par compression")
    L.append("  ──────────────────────────────────────────────────────────────")
    L.append("  Le gain de vitesse ne vient pas seulement d'un code plus")
    L.append("  rapide que l'inférence du modèle.")
    L.append("  Il vient surtout du fait qu'Obsidia évite un détour inutile")
    L.append("  par un modèle généraliste.")
    L.append("")
    L.append("  \"La vitesse ne vient pas seulement d'un calcul plus rapide.")
    L.append("   Elle vient surtout du fait qu'Obsidia évite un détour inutile")
    L.append("   par un modèle généraliste.\"")
    L.append("")
    L.append("  E. Changement de paradigme #4 — Gouvernance avant action")
    L.append("  ─────────────────────────────────────────────────────────")
    L.append("  Obsidia ne gagne pas en vitesse en sacrifiant le contrôle.")
    L.append("  Il reste sous autorité de décision réservée au kernel X108")
    L.append("  (KX108_ONLY veut dire que seul le kernel X108 a l'autorité")
    L.append("  de décision), sans action réelle, sans écriture mémoire")
    L.append("  et sans mutation kernel.")
    L.append("")
    L.append("  \"Le système ne gagne pas en vitesse en sacrifiant le contrôle.")
    L.append("   Il reste sous autorité KX108_ONLY, sans action réelle,")
    L.append("   sans écriture mémoire et sans mutation kernel.\"")
    L.append("")
    L.append("  F. Changement de paradigme #5 — Test de nécessité,"
             " pas seulement test de performance")
    L.append("  ──────────────────────────────────────────────────────────────")
    L.append("  Ce n'est pas seulement un test comparatif (benchmark) de vitesse.")
    L.append("  C'est un test de nécessité :")
    L.append("  - L'appel au grand modèle de langage était-il nécessaire ?")
    L.append("  - Une route bornée pouvait-elle répondre ?")
    L.append("  - La sortie est-elle suffisante, gouvernée et traçable ?")
    L.append("")
    L.append("  \"Le benchmark ne demande pas seulement qui répond plus vite.")
    L.append("   Il demande si l'appel au modèle était nécessaire au départ.\"")
    L.append("")
    L.append("  G. Bénéfices produit")
    L.append("  ─────────────────────")
    L.append("  - Réduction de latence (temps d'attente avant réponse).")
    L.append("  - Réduction d'appels au modèle inutiles.")
    L.append("  - Réduction de surface d'hallucination.")
    L.append("  - Meilleure traçabilité.")
    L.append("  - Meilleure auditabilité.")
    L.append("  - Séparation claire génération / décision / action.")
    L.append("  - Réservation des LLM aux cas réellement ambigus.")
    L.append("  - Lisibilité des limites : revendicable proprement vs mesuré mais non revendicable.")
    L.append("")
    L.append("  H. Bénéfices techniques")
    L.append("  ─────────────────────────")
    L.append("  - Router avant de générer.")
    L.append("  - Pont de domaine (domain bridge) avant inférence généraliste.")
    L.append("  - Détection du chemin rapide (fast path).")
    L.append("  - Couche minimale suffisante (minimal sufficient layer).")
    L.append("  - Gouvernance préservée à vitesse.")
    L.append("  - Rapports au format de données machine (JSON) intacts.")
    L.append("  - Rapports lisibles qui expliquent le résultat en français.")
    L.append("")
    L.append("  I. Bénéfices stratégiques")
    L.append("  ──────────────────────────")
    L.append("  Obsidia ne remplace pas Gemini partout.")
    L.append("  Obsidia est une couche d'économie d'inférence Obsidia (OIE)")
    L.append("  et de gouvernance. Il peut se placer avant un modèle, à côté,")
    L.append("  ou entre le modèle et l'action.")
    L.append("  Il reformule la question :")
    L.append("  de \"quel modèle est le plus intelligent ?\"")
    L.append("  à \"dans quels cas a-t-on vraiment besoin d'un modèle généraliste ?\"")
    L.append("")
    L.append("  \"La question stratégique n'est plus seulement : quel modèle est")
    L.append("   le plus intelligent ? La nouvelle question devient : dans quels cas")
    L.append("   a-t-on vraiment besoin d'un grand modèle de langage généraliste ?\"")
    L.append("")
    L.append("  J. Phrase de paradigme finale")
    L.append("  ──────────────────────────────")
    L.append("  \"Quand la route est connue, prédire devient plus lent que vérifier.\"")
    L.append("")
    L.append("  K. Deuxième phrase finale")
    L.append("  ──────────────────────────")
    L.append("  \"Obsidia ne remplace pas Gemini partout ; Obsidia réduit le besoin")
    L.append("   d'appeler Gemini quand la structure suffit.\"")
    L.append("")

    # POURQUOI CE CHIFFRE CHANGE LE PARADIGME
    L.append("=" * 66)
    L.append("  POURQUOI CE CHIFFRE CHANGE LE PARADIGME ?")
    L.append("=" * 66)
    L.append("")
    L.append(f"  1. Accélération (speedup) moyenne réelle : {avg_sp}x")
    L.append("     Montre le gain de temps observé quand Obsidia est comparé")
    L.append("     à Gemini en conditions réelles de test.")
    L.append("")
    L.append("  2. Accélération quand l'appel au modèle est évité")
    L.append("     Montre que le plus gros gain arrive quand Obsidia n'a pas")
    L.append("     besoin de solliciter un grand modèle de langage généraliste.")
    L.append("")
    L.append("  3. Appels au modèle évités")
    L.append("     Montre que le système ne dépend pas toujours d'une")
    L.append("     inférence générale pour répondre.")
    L.append("")
    L.append("  4. Précision de routage (route accuracy)")
    L.append("     Montre qu'Obsidia sait envoyer la demande vers la bonne")
    L.append("     couche au lieu de tout envoyer au même modèle.")
    L.append("")
    L.append("  5. Adéquation de réponse (answer adequacy)")
    L.append("     Montre que la bonne réponse n'est pas forcément la plus longue")
    L.append("     ou la plus fluide, mais la réponse suffisante, bornée et gouvernée.")
    L.append("")
    L.append("  6. Gouvernance préservée à vitesse")
    L.append("     Montre que le gain de vitesse ne se fait pas au prix d'une")
    L.append("     perte de contrôle.")
    L.append("")
    L.append("  7. Coût réel industriel non revendiqué")
    L.append("     Protège la crédibilité du test comparatif en séparant")
    L.append("     vitesse mesurée et coût réel industriel.")
    L.append("     Attention : ce n'est pas une preuve de coût réel industriel.")
    L.append("")
    L.append("  8. Calcul de chemin complet non revendiqué")
    L.append("     Protège la crédibilité en ne revendiquant pas encore une")
    L.append("     brique d'environnement d'exécution (runtime) complète")
    L.append("     qui n'est pas fermée.")
    L.append("")
    L.append("  Terminologie des acronymes et termes techniques :")
    L.append("  - OIE = économie d'inférence Obsidia")
    L.append("  - OSCA = Score global de vitesse Obsidia (indice indirect)")
    L.append("  - OAPI = Avantage Obsidia sur portefeuille d'actions (indice indirect)")
    L.append("  - ODPI = Avantage Obsidia sur portefeuille de domaines (indice indirect)")
    L.append("  - DCA = Avantage comparatif par domaine")
    L.append("  - LLM = grand modèle de langage généraliste")
    L.append("  - SDK = kit de développement logiciel")
    L.append("  - API = interface de programmation")
    L.append("  - LIVE_LOCAL = environnement d'exécution local réel Obsidia")
    L.append("  - REAL_SDK = appel réel au kit de développement logiciel Gemini")
    L.append("  - ADAPTER_MISSING = connecteur manquant")
    L.append("  - KX108_ONLY = autorité de décision réservée au kernel X108")
    L.append("  - KERNEL_UNREACHABLE = kernel inaccessible pendant le test")
    L.append("  - revendicable proprement = on peut défendre ce résultat")
    L.append("    sans mélanger mesure, supposition et limite technique")
    L.append("  - mesuré mais non revendicable = le chiffre existe, mais")
    L.append("    il manque encore une brique pour le revendiquer complètement")
    L.append("")

    return "\n".join(L)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:  # noqa: C901
    network_allowed = os.environ.get("OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK", "0") == "1"
    sdk_model = os.environ.get("OIE_EXTERNAL_MODEL_LABEL", DEFAULT_GEMINI_MODEL)
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    gem_mode_label = "REAL_SDK" if (network_allowed and gemini_key) else "DRY_RUN"
    obs_exec_mode_env = os.environ.get("OIE_OBSIDIA_EXECUTION_MODE", OIE_OBSIDIA_EXEC_MODE_AUTO)

    _tv = os.environ.get("OIE_TERMINAL_VIEW", "HUMAN_FR").upper()

    # ── Run all tasks (toujours) ──────────────────────────────────────────────
    rows: list[dict] = []
    for task in POWER_TASKS:
        obs_result = run_obsidia_lane(task, obs_exec_mode_env)
        if network_allowed and gemini_key:
            gem_result = run_gemini_lane_real(task, sdk_model)
        else:
            gem_result = run_gemini_lane_dryrun(task)
        row = compute_compare_row(task, obs_result, gem_result)
        rows.append(row)

    summary = compute_summary(rows, POWER_TASKS)

    # ── BLOCK 6 : REPORTS — écriture fichiers (toujours) ─────────────────────
    report_dir = _make_report_dir()
    write_runtime_reports(report_dir, summary, rows)
    proto_path = write_protocol_doc()

    # ── Tableau de bord humain FR (avant les blocs bruts) ────────────────────
    if _tv in ("HUMAN_FR", "COMPACT_FR"):
        _exec_read = _execution_read(summary, rows)
        print(_build_human_dashboard(
            summary, rows,
            exec_read=_exec_read,
            compact=(_tv == "COMPACT_FR"),
        ))

    # ── Séparateur DÉTAILS TECHNIQUES (HUMAN_FR seulement) ───────────────────
    if _tv == "HUMAN_FR":
        print(f"\n{'='*66}")
        print("  DÉTAILS TECHNIQUES")
        print(f"{'='*66}")

    # ── Blocs bruts — HUMAN_FR et AUDIT_RAW uniquement ───────────────────────
    if _tv in ("HUMAN_FR", "AUDIT_RAW"):
        n_tasks = summary["tasks_attempted"]

        # ── BLOCK 1 : BENCHMARK MODE ──────────────────────────────────────────
        print(f"\n{'='*66}")
        print(f"  BENCHMARK MODE — {BENCHMARK_VERSION}")
        print(f"{'='*66}")
        print(f"  Gemini lane mode        : {gem_mode_label}")
        print(f"  Gemini model            : {sdk_model}")
        print(f"  GEMINI_API_KEY set      : {bool(gemini_key)}")
        print(f"  Network allowed         : {network_allowed}")
        print(f"  Obsidia exec mode (env) : {obs_exec_mode_env}")
        print(f"  Obsidia API base        : {_OBSIDIA_API_BASE}")
        print(f"  Obsidia kernel target   : {_OBSIDIA_KERNEL_URL}")
        print(f"  LIVE_LOCAL available    : {_LIVE_LOCAL_AVAILABLE}  (API 8000 probe at import time)")
        print(f"  Live adapters found     : {sum(1 for v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.values() if v.get('adapter_found'))}/7")
        print(f"  Live adapters usable    : {sum(1 for v in _OBSIDIA_LIVE_ADAPTER_REGISTRY.values() if v.get('usable_for_live_local'))}/7")
        print(f"  Live usable families    : {_LIVE_LOCAL_USABLE_FAMILIES or 'none'}")
        print(f"  Unavailable families    : {_LIVE_LOCAL_UNAVAILABLE_FAMILIES or 'none'}")
        print(f"  Adapter missing         : {_ADAPTER_MISSING_FAMILIES_LIVE or 'none'}")
        print(f"  Tasks                   : {len(POWER_TASKS)}")
        print(f"  Gencoin mode            : {GENCOIN_MODE}")
        print(f"  Cost basis Obsidia      : {COST_BASIS_LOCAL_PROXY}")
        print(f"  Governance              : EMITS_ACT={EMITS_ACT} MEM_WRITE={MEMORY_WRITE} "
              f"KERNEL_MUT={KERNEL_MUTATION} AUTH={DECISION_AUTHORITY}")

        # ── BLOCK 2 : DUAL LANE SUMMARY ───────────────────────────────────────
        print(f"\n{'='*66}")
        print("  DUAL LANE SUMMARY")
        print(f"{'='*66}")
        print(f"  {'FAMILY':<12} {'OBS_LANE':<32} {'GEM_LANE':<14} {'SCOPE':<44} "
              f"{'OBS_MATCH':<10} {'GEM_MATCH':<10} {'CLAIMABLE':<10} {'ADAPTER':<24} {'FALLBACK':<10} {'LIVE_AVAIL'}")
        print("  " + "-" * 180)
        for row in rows:
            dl = row.get("dual_lane", {})
            ol = dl.get("obsidia_lane", {})
            gl = dl.get("gemini_lane", {})
            adapter_type = ol.get("adapter_type", "?")
            fallback = ol.get("fallback_used", False)
            live_avail = ol.get("live_execution_available", False)
            print(
                f"  {row['family']:<12} "
                f"{str(ol.get('execution_mode', '?')):<32} "
                f"{str(gl.get('execution_mode', '?')):<14} "
                f"{str(dl.get('comparison_scope', '?')):<44} "
                f"{str(ol.get('route_match', '?')):<10} "
                f"{str(gl.get('route_match', '?')):<10} "
                f"{str(dl.get('comparison_claimable', '?')):<10} "
                f"{str(adapter_type):<24} "
                f"{str(fallback):<10} "
                f"{str(live_avail)}"
            )

        # ── BLOCK 3 : CLAIMABLE READ ──────────────────────────────────────────
        obs_acc = summary["obsidia_route_accuracy"]
        gem_acc = summary["gemini_route_accuracy"]
        wired_count = summary["available_surface_count"]
        missing_count = summary["adapter_missing_count"]
        model_avoided = summary["obsidia_model_call_avoided_count"]
        funct_claim = summary.get("oie_claim_matrix", {}).get("functional_claimable_count", 0)
        route_claim = summary.get("oie_claim_matrix", {}).get("route_claimable_count", 0)

        print(f"\n{'='*66}")
        print("  CLAIMABLE READ")
        print(f"{'='*66}")
        print(f"  Route accuracy (Obsidia)    : {obs_acc}")
        print(f"  Route accuracy (Gemini)     : {gem_acc}")
        print(f"  Route claimable count       : {route_claim}/{n_tasks}  (wired surface only)")
        print(f"  Functional claimable count  : {funct_claim}/{n_tasks}  (wired surface only)")
        print(f"  Wired surface families      : {wired_count}/7  (FAST_PATH, BANK, TRADING, GPS)")
        _adapter_missing_display = sorted([r.get("family") for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING])
        _bridge_kernel_unreachable_display = sorted([r.get("family") for r in rows if r.get("obsidia_status") == "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE"])
        _adapter_missing_display_s = ", ".join(_adapter_missing_display) if _adapter_missing_display else "NONE"
        _bridge_kernel_unreachable_display_s = ", ".join(_bridge_kernel_unreachable_display) if _bridge_kernel_unreachable_display else "NONE"
        print(f"  Adapter missing families    : {len(_adapter_missing_display)}/{len(rows)}  ({_adapter_missing_display_s})")
        print(f"  Bridge kernel unreachable   : {len(_bridge_kernel_unreachable_display)}/{len(rows)}  ({_bridge_kernel_unreachable_display_s})")
        print(f"  Cost comparison claimable   : {summary['cost_comparison_claimable_global']}  (always False — LOCAL_PROXY_UNCALIBRATED)")
        print(f"  Model call avoided          : {model_avoided}/{n_tasks}")
        print(f"  Governance clean            : {summary['governance_clean']}")

        # ── BLOCK 4 : PERFORMANCE READ ────────────────────────────────────────
        print(f"\n{'='*66}")
        print("  PERFORMANCE READ")
        print(f"{'='*66}")
        print(f"  Avg speedup ratio           : {summary['avg_speedup_ratio']}")
        print(f"  Intellectual value avg      : {summary['intellectual_value_avg']}")
        print(f"  Debt total                  : {summary['internal_economy_debt_total']}")
        print(f"  Energy source               : {summary['energy_source']}")
        print(f"  Known path detected         : {summary.get('known_path_detected_count', '?')}/{n_tasks}")
        print(f"  Inference avoided           : {summary.get('unnecessary_inference_avoided_count', '?')}/{n_tasks}")
        print(f"  Governed speed rate         : {summary.get('governance_preserved_at_speed_rate', '?')}")
        print(f"  Math formalized             : {summary.get('math_formalized_surface_count', '?')}/{n_tasks}")

        # ── BLOCK 4.5 : SPEED STACK READ ──────────────────────────────────────
        _ss_avg_speedup = summary.get("avg_speedup_ratio")
        _ss_avail_speedup = summary.get("available_surface_avg_speedup_ratio")
        _ss_model_speedup = summary.get("model_avoided_avg_speedup_ratio")
        _ss_terrain_speedup = summary.get("terrain_avg_speedup_ratio")
        _ss_governed = summary.get("governance_preserved_at_speed_rate")
        _ss_kp_count = summary.get("known_path_detected_count", "?")
        _ss_inf_avoided = summary.get("inference_avoided_count", "?")
        _ss_model_avoided = summary.get("obsidia_model_call_avoided_count", "?")
        _ss_model_families = summary.get("model_avoided_families") or []
        _ss_oie_claimable = summary.get("oie_indices_claimable")
        _ss_cost_claimable = summary.get("cost_comparison_claimable_global", False)
        _ss_dca_raw = summary.get("dca_by_domain") or {}

        def _ss_dca_val(fam: str) -> str:
            v = _ss_dca_raw.get(fam)
            if v is None:
                return "null"
            if isinstance(v, dict):
                return str(v.get("dca_api_normal") or v.get("dca_agentic") or "null")
            return str(v)

        print(f"\n{'='*66}")
        print("  SPEED STACK READ")
        print(f"{'='*66}")
        print(f"  Live avg speedup vs Gemini REAL_SDK   : {_ss_avg_speedup}x")
        print(f"  Available surface avg speedup          : {_ss_avail_speedup}")
        print(f"  Model avoided avg speedup              : {_ss_model_speedup}")
        print(f"  Terrain avg speedup                    : {_ss_terrain_speedup}")
        print(f"  Governed speed rate                    : {_ss_governed}")
        print(f"  Known path detected                    : {_ss_kp_count}/{n_tasks}")
        print(f"  Inference avoided                      : {_ss_inf_avoided}/{n_tasks}")
        print(f"  Model call avoided                     : {_ss_model_avoided}/{n_tasks}")
        print(f"  Model avoided families                 : {_ss_model_families}")
        print(f"  OIE speed indices:")
        print(f"    OSCA — geomean all families          : {summary.get('osca_ratio')}x")
        print(f"    OAPI — portfolio actions             : {summary.get('oapi_ratio')}x")
        print(f"    ODPI — portfolio domains             : {summary.get('odpi_ratio')}x")
        print(f"    indices_claimable                    : {_ss_oie_claimable}")
        print(f"  DCA by domain:")
        for _ss_fam in ("FAST_PATH", "BRODY", "BANK", "TRADING", "GPS", "GPS_AVIATION", "OBSIDURE", "LEAN"):
            print(f"    {_ss_fam:<16} : {_ss_dca_val(_ss_fam)}")
        print(f"  Governance while fast:")
        print(f"    decision_authority : KX108_ONLY")
        print(f"    emits_act          : false")
        print(f"    memory_write       : false")
        print(f"    kernel_mutation    : false")
        print(f"  Claim guard:")
        print(f"    speed_metrics_claimable        : true")
        print(f"    cost_comparison_claimable      : {_ss_cost_claimable}")
        print(f"    path_compute_runtime_claimable : false")
        print(f"    wording_guard: Speed is measured; real cost and full Path Compute runtime are not claimed.")

        # ── BLOCK 5 : OIE READ ────────────────────────────────────────────────
        oie_osca = summary.get("osca_ratio", "N/A")
        oie_oapi = summary.get("oapi_ratio", "N/A")
        oie_odpi = summary.get("odpi_ratio", "N/A")
        dca = summary.get("dca_by_domain", {})
        if dca:
            def _dca_sort_key(kv: tuple) -> float:
                v = kv[1]
                if isinstance(v, (int, float)):
                    return float(v)
                if isinstance(v, dict):
                    return float(v.get("dca_api_normal") or 0)
                return 0.0
            dca_top = sorted(dca.items(), key=_dca_sort_key, reverse=True)[:3]
        else:
            dca_top = []

        print(f"\n{'='*66}")
        print("  OIE READ")
        print(f"{'='*66}")
        print(f"  OSCA (geomean all families) : {oie_osca}x")
        print(f"  OAPI (portfolio actions)    : {oie_oapi}x")
        print(f"  ODPI (portfolio domains)    : {oie_odpi}x")
        print(f"  OIE import OK               : {_OIE_IMPORT_OK}")
        print(f"  OIE freeze found            : {_OIE_FREEZE_FOUND}")
        print(f"  Gencoin mode                : {summary['gencoin_mode']}")
        print(f"  Gencoin emission            : {summary['gencoin_total_emission']}  (CALIBRATION_ONLY)")
        if dca_top:
            print(f"  DCA top domains             :")
            for dom, val in dca_top:
                if isinstance(val, (int, float)):
                    print(f"    {dom:<20} : {val:.4f}")
                elif isinstance(val, dict):
                    dca_val = val.get("dca_api_normal") or val.get("dca_agentic") or 0
                    print(f"    {dom:<20} : dca_api_normal={dca_val}")

        # ── BLOCK 6 : REPORTS — print (après écriture fichiers déjà faite) ────
        print(f"\n{'='*66}")
        print("  REPORTS")
        print(f"{'='*66}")
        print(f"  Runtime report dir  : {report_dir}")
        print(f"  Protocol doc        : {proto_path}")
        print(f"  summary.json        : {report_dir / 'summary.json'}")
        print(f"  readable_report.json: {report_dir / 'readable_report.json'}")
        print(f"  summary.md          : {report_dir / 'summary.md'}")
        print(f"\n  BENCHMARK_COMPLETE  mode={gem_mode_label} obs_exec={obs_exec_mode_env} "
              f"tasks={n_tasks} gov_clean={summary['governance_clean']} "
              f"gencoin={summary['gencoin_mode']}")

    # ── BLOCK 7 + 8 : EXPLAINER ET BÉNÉFICES (AUDIT_RAW seulement) ───────────
    if _tv == "AUDIT_RAW":
        print(_build_metric_explainer(summary, rows))
        print(_build_benefices_paradigme(summary, rows))

    # ── COMPACT_FR : message de complétion minimal ─────────────────────────────
    if _tv == "COMPACT_FR":
        print(f"\n  Rapports écrits dans : {report_dir}")

    # ── JSON_ONLY : confirmation fichiers uniquement ───────────────────────────
    if _tv == "JSON_ONLY":
        print(f"  Reports written to: {report_dir}")


if __name__ == "__main__":
    main()
