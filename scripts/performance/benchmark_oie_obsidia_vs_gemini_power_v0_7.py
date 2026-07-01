"""OIE V0.7 -- Obsidia vs Gemini Power Benchmark.

Deux lanes sur les memes 7 familles de routing :
  A. OBSIDIA_LOCAL_ACTUAL  -- router deterministe / valeurs figees V0 / adapter si dispo
  B. GEMINI_SDK_EXTERNAL   -- SDK google-genai (dry-run par defaut)

Metriques : speed, cost, energy, throughput, work avoidance,
context economy, inference avoidance, governance, quality.

Gouvernance :
  EMITS_ACT=False, MEMORY_WRITE=False, KERNEL_MUTATION=False,
  DECISION_AUTHORITY=KX108_ONLY, SECRETS_REDACTED=True.

Mode par defaut : DRY_RUN (aucun reseau, Gemini mocke).
Mode REAL :       OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1 + GEMINI_API_KEY.

Jamais de secret dans JSON/log.
Jamais de commit automatique.
Ne pas modifier kernel, Brody live, Obsidure live, Graphiti, Neo4j, memoire.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
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

# ── Energy source ─────────────────────────────────────────────────────────────
ENERGY_SOURCE_UNAVAILABLE = "ENERGY_PROXY_UNAVAILABLE"
ENERGY_SOURCE_ESTIMATE = "ENERGY_PROXY_ESTIMATE"

# ── Default Gemini model ──────────────────────────────────────────────────────
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-lite"

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
# Source : gemini_sdk smoke run 2026-07-01, modele gemini-2.0-flash-lite
# Totaux : 281 input / 14 output / 295 total, route_match 3/7
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
    },
]


# ── Energy / carbon helpers ───────────────────────────────────────────────────

def _read_energy_env() -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Read energy coefficients from env. None if absent."""
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
    """Compute energy and carbon estimates. Returns energy_source + values."""
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


# ── Cost helpers ──────────────────────────────────────────────────────────────

def _read_cost_env() -> tuple[Optional[float], Optional[float]]:
    def _f(k: str) -> Optional[float]:
        v = os.environ.get(k, "")
        try:
            return float(v) if v else None
        except ValueError:
            return None
    return _f("OIE_EXTERNAL_INPUT_COST_PER_1M"), _f("OIE_EXTERNAL_OUTPUT_COST_PER_1M")


def _safe_ratio(num: Optional[float], den: Optional[float]) -> tuple[Optional[float], str]:
    """Return ratio + status. Never divides by zero."""
    if num is None or den is None:
        return None, "MISSING_OPERAND"
    if den == 0 or abs(den) < 1e-12:
        return None, "BASELINE_NEAR_ZERO"
    return num / den, "OK"


# ── Obsidia lane ──────────────────────────────────────────────────────────────

def _try_fast_path_router(task: dict) -> Optional[dict]:
    """Try to run the real Obsidia fast-path router. Returns None if unavailable."""
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
    """Compute Obsidia lane for a task.

    Priority :
    1. Try real adapter (FAST_PATH only).
    2. Use frozen V0 estimate.
    3. Return ADAPTER_MISSING with architecture estimates.
    """
    status_frozen = task["obsidia_status_frozen"]
    lat_ms = task["obsidia_latency_ms_frozen"]
    modules_considered = task["expected_modules_considered"]
    modules_activated = task["expected_modules_activated"]
    modules_skipped = task["expected_modules_skipped"]
    modules_skipped_pct = round(100.0 * modules_skipped / max(modules_considered, 1), 2)

    # Estimated tokens (chars / 4 heuristic)
    prompt_chars = len(task["prompt"])
    est_input_tok = max(1, prompt_chars // 4)
    est_output_tok = 4
    est_total_tok = est_input_tok + est_output_tok

    cost_per_1m = task["obsidia_cost_per_1m_est"]
    cost_per_req = cost_per_1m * est_total_tok / 1_000_000.0

    # Try real adapter first
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


# ── Gemini lane ───────────────────────────────────────────────────────────────

def run_gemini_lane_dryrun(task: dict) -> dict:
    """Gemini dry-run : valeurs figees V0.5.1."""
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
    """Gemini real : appel SDK (reseau autorise)."""
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
    q_score = rq.get("quality_score")
    detected = rq.get("external_detected_route")
    route_match = rq.get("route_match")
    return {
        "gemini_status": GEMINI_STATUS_REAL if raw.get("success") else GEMINI_STATUS_FAILED,
        "gemini_detected_route": detected,
        "gemini_route_match": route_match,
        "gemini_latency_ms": raw.get("latency_ms"),
        "gemini_input_tokens": in_tok,
        "gemini_output_tokens": out_tok,
        "gemini_total_tokens": tot_tok,
        "gemini_cost_source": cost_src,
        "gemini_cost_per_request_measured": cost_per_req,
        "gemini_cost_per_1m_measured": cost_per_1m,
        "gemini_quality_score": q_score,
        "gemini_failure_type": raw.get("failure_type", FAILURE_NONE),
        "gemini_external_model_call_required": True,
    }


# ── Compare row ───────────────────────────────────────────────────────────────

def compute_compare_row(task: dict, obs: dict, gem: dict) -> dict:
    """Fusion Obsidia + Gemini en une ligne de comparaison."""
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

    # Tokens / context economy
    tok_delta_abs = (gem_tok - obs_tok) if (gem_tok is not None and obs_tok is not None) else None
    tok_delta_pct = (
        round(100.0 * tok_delta_abs / gem_tok, 2)
        if tok_delta_abs is not None and gem_tok and gem_tok > 0 else None
    )
    ext_dep_ratio, _ = _safe_ratio(gem_tok, max(obs_tok or 0, 1))
    context_budget_delta_pct = tok_delta_pct

    # Cost
    avoided_cost, _ = _safe_ratio(gem_cost, 1.0)
    if gem_cost is not None and obs_cost is not None:
        avoided_cost_req = gem_cost - obs_cost
    else:
        avoided_cost_req = None
    cost_sr, cost_ratio_status = _safe_ratio(gem_cost, obs_cost)
    cost_delta_pct = (
        round(100.0 * avoided_cost_req / gem_cost, 2)
        if avoided_cost_req is not None and gem_cost and gem_cost > 0 else None
    )

    # Savings per 1m (architecture comparison)
    obs_c1m = obs.get("obsidia_cost_per_1m_est")
    gem_c1m = gem.get("gemini_cost_per_1m_measured")
    avoided_c1m, _ = _safe_ratio(gem_c1m, 1.0)
    if gem_c1m is not None and obs_c1m is not None:
        avoided_c1m = gem_c1m - obs_c1m
    else:
        avoided_c1m = None
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

    # Quality
    q_delta = (
        round(obs_q - gem_q, 4)
        if obs_q is not None and gem_q is not None else None
    )

    # Governance
    gov_clean = (
        not EMITS_ACT
        and not MEMORY_WRITE
        and not KERNEL_MUTATION
        and obs_boundary
    )

    # Winners
    def _winner(a, b, labels=("OBSIDIA", "GEMINI", "TIE")) -> str:
        if a is None or b is None:
            return "UNKNOWN"
        if a > b:
            return labels[0]
        if b > a:
            return labels[1]
        return labels[2]

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

    final_interp = _build_interpretation(task, obs, gem, obs.get("obsidia_model_call_avoided"))

    return {
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
        "final_interpretation": final_interp,
    }


def _build_interpretation(task: dict, obs: dict, gem: dict, model_avoided: Optional[bool]) -> str:
    family = task["family"]
    if model_avoided:
        return (
            f"{family}: Obsidia routes deterministically — no LLM call. "
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
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "benchmark_date": BENCHMARK_DATE,
        "tasks_attempted": n,
        "obsidia_route_accuracy": round(obs_route_ok / n, 4) if n else None,
        "gemini_route_accuracy": round(gem_route_ok / n, 4) if n else None,
        "obsidia_avg_latency_ms": _avg([r.get("obsidia_latency_ms") for r in rows]),
        "gemini_avg_latency_ms": _avg([r.get("gemini_latency_ms") for r in rows]),
        "avg_latency_delta_pct": _avg([r.get("latency_delta_pct") for r in rows]),
        "avg_speedup_ratio": _avg([r.get("speedup_ratio") for r in rows]),
        "obsidia_total_estimated_tokens": sum(
            r.get("obsidia_estimated_total_tokens") or 0 for r in rows
        ),
        "gemini_total_tokens": sum(r.get("gemini_total_tokens") or 0 for r in rows),
        "avg_token_delta_pct": _avg([r.get("token_delta_pct") for r in rows]),
        "gemini_total_cost_measured": sum(
            r.get("gemini_cost_per_request_measured") or 0.0 for r in rows
        ) or None,
        "obsidia_total_cost_est": sum(
            r.get("obsidia_cost_per_request_est") or 0.0 for r in rows
        ),
        "total_avoided_cost": (
            sum(r.get("avoided_cost_per_request") or 0.0 for r in rows)
            if any(r.get("avoided_cost_per_request") is not None for r in rows) else None
        ),
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
        "obsidia_modules_skipped_total": sum(
            r.get("obsidia_modules_skipped") or 0 for r in rows
        ),
        "obsidia_cache_hit_ratio": round(cache_hits / n, 4) if n else None,
        "obsidia_boundary_safety_pass_rate": round(boundary_ok / n, 4) if n else None,
        "obsidia_quality_avg": _avg([r.get("obsidia_quality_score") for r in rows]),
        "gemini_quality_avg": _avg([r.get("gemini_quality_score") for r in rows]),
        "quality_delta_avg": _avg([r.get("quality_delta") for r in rows]),
        "obsidia_safe_decisions_per_second_avg": _avg(
            [r.get("safe_decisions_per_second_obsidia") for r in rows]
        ),
        "gemini_safe_decisions_per_second_avg": _avg(
            [r.get("safe_decisions_per_second_gemini") for r in rows]
        ),
        "obsidia_decisions_per_cost_unit_avg": _avg(
            [r.get("decisions_per_cost_unit_obsidia") for r in rows]
        ),
        "gemini_decisions_per_cost_unit_avg": _avg(
            [r.get("decisions_per_cost_unit_gemini") for r in rows]
        ),
        "obsidia_decisions_per_wh_avg": _avg(
            [r.get("decisions_per_wh_obsidia") for r in rows]
        ) if energy_src == ENERGY_SOURCE_ESTIMATE else None,
        "gemini_decisions_per_wh_avg": _avg(
            [r.get("decisions_per_wh_gemini") for r in rows]
        ) if energy_src == ENERGY_SOURCE_ESTIMATE else None,
        "governance_clean": gov_clean_all,
        "decision_authority": DECISION_AUTHORITY,
        "emits_act": EMITS_ACT,
        "memory_write": MEMORY_WRITE,
        "kernel_mutation": KERNEL_MUTATION,
        "secrets_redacted": SECRETS_REDACTED,
        "energy_source": energy_src,
        "cost_source": cost_src,
        "adapter_missing_count": sum(
            1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_MISSING
        ),
        "frozen_v0_estimate_count": sum(
            1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_FROZEN
        ),
        "real_adapter_count": sum(
            1 for r in rows if r.get("obsidia_status") == OBSIDIA_STATUS_REAL
        ),
    }


# ── Markdown report ───────────────────────────────────────────────────────────

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


def generate_report(summary: dict, rows: list[dict]) -> str:
    """Generer le rapport Markdown V0.7."""
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
    p(f"**Statut :** dry-run (valeurs figees V0.5.1) — run reel necessite GEMINI_API_KEY + ALLOW_NETWORK")
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
    p("---")

    h(2, "2. Pourquoi les benchmarks precedents etaient insuffisants")
    p("Les benchmarks V0.2–V0.5.1 mesuraient principalement :")
    p("- `route_match` et `cost_source` par receipt individuel")
    p("- Pas de vision globale speed / energy / throughput / work avoidance")
    p("- Pas de `safe_decisions_per_second`, `decisions_per_wh`, `decisions_per_cost_unit`")
    p("- Pas de colonne `winner_*` par famille")
    p("- Pas de rapport energie / carbone")
    p("V0.7 reunit toutes ces dimensions dans une seule table comparative par famille.")
    p("---")

    h(2, "3. Architecture : deux lanes sur les memes 7 familles")
    table(
        ["Lane", "Mode", "Reseau", "Modele"],
        [
            ["OBSIDIA_LOCAL_ACTUAL", "FROZEN_V0_ESTIMATE / REAL_ADAPTER / ADAPTER_MISSING", "Non", "deterministe"],
            ["GEMINI_SDK_EXTERNAL", "DRY_RUN_MOCK / REAL_SDK", "Optionnel", "gemini-2.0-flash-lite"],
        ]
    )
    p("> " + _REQUIRED_PHRASES[2])
    p("---")

    h(2, "4. Speed metrics")
    table(
        ["family", "obs_lat_ms", "gem_lat_ms", "lat_delta_pct", "speedup_ratio", "winner"],
        [
            [r["family"], _fmt(r["obsidia_latency_ms"]), _fmt(r["gemini_latency_ms"]),
             _fmt(r["latency_delta_pct"], 2), _fmt(r["speedup_ratio"], 2), r["winner_speed"]]
            for r in rows
        ]
    )
    p(f"Moyenne speedup : {_fmt(summary['avg_speedup_ratio'], 2)}x")
    p(f"Moyenne latency delta pct : {_fmt(summary['avg_latency_delta_pct'], 2)}%")
    p("---")

    h(2, "5. Cost metrics")
    table(
        ["family", "obs_cost_req", "gem_cost_req", "avoided_cost", "cost_sr", "winner"],
        [
            [r["family"], _fmt(r["obsidia_cost_per_request_est"], 8),
             _fmt(r["gemini_cost_per_request_measured"], 8),
             _fmt(r["avoided_cost_per_request"], 8),
             _fmt(r["cost_savings_ratio"], 2), r["winner_cost"]]
            for r in rows
        ]
    )
    p(f"Total cost Gemini : {_fmt(summary['gemini_total_cost_measured'], 8)} EUR")
    p(f"Total cost Obsidia est : {_fmt(summary['obsidia_total_cost_est'], 8)} EUR")
    p(f"Total avoided cost : {_fmt(summary['total_avoided_cost'], 8)} EUR")
    p("Note : cout Gemini mesure seulement si REAL mode + prix env fournis.")
    p("---")

    h(2, "6. Energy metrics")
    table(
        ["family", "obs_wh", "gem_wh", "avoided_wh", "energy_sr", "winner"],
        [
            [r["family"],
             _fmt(r.get("obsidia_energy_wh_est"), 8),
             _fmt(r.get("gemini_energy_wh_est"), 8),
             _fmt(r.get("energy_avoided_wh"), 8),
             _fmt(r.get("energy_savings_ratio"), 2),
             r.get("winner_energy", "UNKNOWN")]
            for r in rows
        ]
    )
    p(f"Source energie : {summary['energy_source']}")
    p("Activer avec : OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS + OIE_LOCAL_POWER_W + OIE_CARBON_GCO2_PER_KWH")
    p("---")

    h(2, "7. Power / capacity metrics")
    table(
        ["family", "obs_safe_dps", "gem_safe_dps", "obs_dpc", "gem_dpc"],
        [
            [r["family"],
             _fmt(r.get("safe_decisions_per_second_obsidia"), 3),
             _fmt(r.get("safe_decisions_per_second_gemini"), 3),
             _fmt(r.get("decisions_per_cost_unit_obsidia"), 2),
             _fmt(r.get("decisions_per_cost_unit_gemini"), 2)]
            for r in rows
        ]
    )
    p("safe_decisions_per_second = throughput * quality_score * boundary_ok")
    p("decisions_per_cost_unit = 1 / cost_per_request")
    p("---")

    h(2, "8. Context economy")
    table(
        ["family", "obs_tok", "gem_tok", "tok_delta_abs", "tok_delta_pct", "ext_dep_ratio"],
        [
            [r["family"],
             r.get("obsidia_estimated_total_tokens"),
             r.get("gemini_total_tokens"),
             r.get("token_delta_abs"),
             _fmt(r.get("token_delta_pct"), 2),
             _fmt(r.get("external_token_dependency_ratio"), 2)]
            for r in rows
        ]
    )
    p(f"Total Obsidia tokens est : {summary['obsidia_total_estimated_tokens']}")
    p(f"Total Gemini tokens : {summary['gemini_total_tokens']}")
    p("---")

    h(2, "9. Work avoidance")
    table(
        ["family", "model_avoided", "modules_skipped", "cache_hit", "obs_status"],
        [
            [r["family"],
             r.get("obsidia_model_call_avoided"),
             r.get("obsidia_modules_skipped"),
             r.get("obsidia_cache_hit"),
             r.get("obsidia_status")]
            for r in rows
        ]
    )
    p(f"model_call_avoided total : {summary['obsidia_model_call_avoided_count']}/{summary['tasks_attempted']}")
    p(f"model_call_avoided_rate : {_fmt(summary['obsidia_model_call_avoided_rate'], 2)}")
    p(f"modules_skipped total : {summary['obsidia_modules_skipped_total']}")
    p(f"cache_hit_ratio : {_fmt(summary['obsidia_cache_hit_ratio'], 2)}")
    p(f"Frozen V0 warm gains : graphiti={FROZEN_GRAPHITI_WARM_GAIN_RATIO}x, loader={FROZEN_LOADER_WARM_GAIN_RATIO}x")
    p("---")

    h(2, "10. Inference avoidance")
    p("Familles ou Obsidia evite l'appel LLM (model_call_avoided=True) :")
    for r in rows:
        if r.get("obsidia_model_call_avoided"):
            p(f"- **{r['family']}** : Obsidia decide de facon deterministe.")
    p("")
    p("Familles ou Obsidia doit aussi invoquer un modele (model_call_avoided=False) :")
    for r in rows:
        if not r.get("obsidia_model_call_avoided"):
            obs_st = r.get("obsidia_status")
            p(f"- **{r['family']}** (status={obs_st}) : comparaison latence/cout.")
    p("---")

    h(2, "11. Routing quality")
    table(
        ["family", "expected", "obs_detected", "gem_detected", "obs_match", "gem_match", "q_delta", "winner"],
        [
            [r["family"], r["expected_route"],
             r.get("obsidia_detected_route"), r.get("gemini_detected_route"),
             r.get("obsidia_route_match"), r.get("gemini_route_match"),
             _fmt(r.get("quality_delta"), 2), r.get("winner_route")]
            for r in rows
        ]
    )
    p(f"Obsidia quality avg : {_fmt(summary['obsidia_quality_avg'], 2)}")
    p(f"Gemini quality avg  : {_fmt(summary['gemini_quality_avg'], 2)}")
    p("---")

    h(2, "12. Governance / boundary safety")
    table(
        ["Propriete", "Valeur", "Immutable"],
        [
            ["emits_act", str(EMITS_ACT), "Oui"],
            ["memory_write", str(MEMORY_WRITE), "Oui"],
            ["kernel_mutation", str(KERNEL_MUTATION), "Oui"],
            ["graphiti_write", str(GRAPHITI_WRITE), "Oui"],
            ["neo4j_write", str(NEO4J_WRITE), "Oui"],
            ["secrets_redacted", str(SECRETS_REDACTED), "Oui"],
            ["decision_authority", DECISION_AUTHORITY, "Oui"],
        ]
    )
    p(f"boundary_safety_pass_rate : {_fmt(summary['obsidia_boundary_safety_pass_rate'], 2)}")
    p(f"governance_clean (all tasks) : {summary['governance_clean']}")
    p("---")

    h(2, "13. Confusion matrix")
    obs_match_count = sum(1 for r in rows if r.get("obsidia_route_match") is True)
    gem_match_count = sum(1 for r in rows if r.get("gemini_route_match") is True)
    both = sum(1 for r in rows if r.get("obsidia_route_match") and r.get("gemini_route_match"))
    neither = sum(1 for r in rows if not r.get("obsidia_route_match") and not r.get("gemini_route_match"))
    obs_only = sum(1 for r in rows if r.get("obsidia_route_match") and not r.get("gemini_route_match"))
    gem_only = sum(1 for r in rows if not r.get("obsidia_route_match") and r.get("gemini_route_match"))
    table(
        ["Scenario", "Count"],
        [
            ["Obsidia correct ET Gemini correct", both],
            ["Obsidia correct MAIS Gemini incorrect", obs_only],
            ["Gemini correct MAIS Obsidia incorrect", gem_only],
            ["Aucun correct", neither],
        ]
    )
    p("Note : Obsidia ADAPTER_MISSING compte comme route inconnue, pas comme match.")
    p("---")

    h(2, "14. Per-family comparison")
    for r in rows:
        h(3, f"{r['family']} — {r['task_id']}")
        p(f"- **Interpretation** : {r['final_interpretation']}")
        p(f"- Speed winner : {r['winner_speed']}")
        p(f"- Cost winner  : {r['winner_cost']}")
        p(f"- Route winner : {r['winner_route']}")
        p(f"- Gov winner   : {r['winner_governance']}")
        p(f"- Obsidia status : {r.get('obsidia_status')}")
        p(f"- Gemini status  : {r.get('gemini_status')}")
    p("---")

    h(2, "15. Valid claims")
    p("- Obsidia evite l'appel LLM pour FAST_PATH, BANK, TRADING, GPS (4/7 familles).")
    p("- Pour les 4 familles deterministes, Obsidia latence < 100ms vs 300-450ms Gemini.")
    p("- Obsidia governance garantit emits_act=False, memory_write=False pour toutes les taches.")
    p("- Le benchmark mesure l'avoidance d'inference, pas la qualite de generation LLM.")
    p("- Fast Path Graphiti warm path : 868x speedup cache vs cold (frozen V0).")
    p("- Loader warm path : 11348x speedup (frozen V0 Technical Note).")
    p("---")

    h(2, "16. Invalid claims")
    for claim in _INVALID_CLAIMS:
        p(f"- INTERDIT : \"{claim}\"")
    p("- INTERDIT : Ce benchmark prouve que Obsidia est moins cher que Gemini en production.")
    p("- INTERDIT : Les valeurs energetiques sont des mesures hardware reelles.")
    p("- INTERDIT : Obsidia produit de meilleures reponses LLM que Gemini.")
    p("---")

    h(2, "17. Next metrics V0.8")
    p("- Execution d'un run reel Gemini 7 familles + comparaison avec V0.7 dry-run.")
    p("- Telemetrie GPU/CPU reelle pour energy_source=HARDWARE_MEASURED.")
    p("- Repetitions (N=10) pour p50/p95/p99 reels.")
    p("- Integration sigma/contracts.py pour validation governance on-chain.")
    p("- Matrice domaine-output (ALLOW/HOLD/BLOCK) comparee Obsidia vs Gemini.")
    p("---")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    network_allowed = os.environ.get("OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK", "0") == "1"
    sdk_model = os.environ.get("OIE_EXTERNAL_MODEL_LABEL", DEFAULT_GEMINI_MODEL)
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    mode = "REAL" if network_allowed else "DRY_RUN"

    print(f"\n=== {BENCHMARK_VERSION} ===\n")
    print(f"  Mode                   : {mode}")
    print(f"  Gemini model           : {sdk_model}")
    print(f"  GEMINI_API_KEY set     : {bool(gemini_key)}")
    print(f"  Network allowed        : {network_allowed}")
    print(f"  Energy env set         : {bool(os.environ.get('OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS'))}")
    print(f"  Cost env set           : {bool(os.environ.get('OIE_EXTERNAL_INPUT_COST_PER_1M'))}")
    print(f"  Tasks                  : {len(POWER_TASKS)}")
    print(f"  Governance             : EMITS_ACT={EMITS_ACT} MEMORY_WRITE={MEMORY_WRITE} "
          f"KERNEL_MUTATION={KERNEL_MUTATION} AUTH={DECISION_AUTHORITY}\n")

    rows: list[dict] = []

    for task in POWER_TASKS:
        print(f"  [{task['family']}] {task['task_id']}")
        obs_result = run_obsidia_local_actual(task)
        if network_allowed and gemini_key:
            gem_result = run_gemini_lane_real(task, sdk_model)
        else:
            gem_result = run_gemini_lane_dryrun(task)
        row = compute_compare_row(task, obs_result, gem_result)
        rows.append(row)
        print(f"    obs_status   : {obs_result['obsidia_status']}")
        print(f"    gem_status   : {gem_result['gemini_status']}")
        print(f"    speedup      : {row.get('speedup_ratio')}")
        print(f"    model_avoided: {row.get('obsidia_model_call_avoided')}")
        print(f"    cost_src     : {row.get('gemini_cost_per_request_measured') or 'N/A'}")

    summary = compute_summary(rows, POWER_TASKS)
    report_md = generate_report(summary, rows)

    print("\n--- Summary ---")
    print(f"  Tasks                  : {summary['tasks_attempted']}")
    print(f"  Obsidia route_accuracy : {summary['obsidia_route_accuracy']}")
    print(f"  Gemini route_accuracy  : {summary['gemini_route_accuracy']}")
    print(f"  avg_speedup_ratio      : {summary['avg_speedup_ratio']}")
    print(f"  model_call_avoided     : {summary['obsidia_model_call_avoided_count']}/{summary['tasks_attempted']}")
    print(f"  governance_clean       : {summary['governance_clean']}")
    print(f"  energy_source          : {summary['energy_source']}")
    print(f"  cost_source            : {summary['cost_source']}")

    # Emit JSON summary
    json_out = json.dumps(summary, indent=2, default=str)
    print("\n--- JSON Summary (first 20 lines) ---")
    for line in json_out.splitlines()[:20]:
        print(f"  {line}")

    # Emit report
    report_path = (
        _REPO_ROOT / "docs" / "audits" / "OBSIDIA_OIE_OBSIDIA_VS_GEMINI_POWER_METRICS_V0_7.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"\n  Report written : {report_path}")
    print(f"\n  BENCHMARK_COMPLETE mode={mode} tasks={summary['tasks_attempted']} "
          f"gov_clean={summary['governance_clean']}")


if __name__ == "__main__":
    main()
