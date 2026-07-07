#!/usr/bin/env python3
"""OIE External Benchmark Harness V0.5 -- CLI, SDK Anthropic, SDK Gemini.

Objectif V0.5 : ajouter provider Gemini SDK (google-genai) pour mesure cout reel
quand Anthropic n'est pas accessible (credit / compte). Mode CLI inchange.

Modes d'execution :
  Par defaut               : dry-run routing smoke uniquement
  OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1 : routing smoke reel
  OIE_EXTERNAL_BENCHMARK_FULL=1          : routing full (toutes familles)
  OIE_EXTERNAL_BENCHMARK_DOMAIN=1        : domain-output benchmark
  OIE_EXTERNAL_COST_ESTIMATE=1           : estimation tokens locale si prix fournis

Provider :
  OIE_EXTERNAL_PROVIDER=cli             : Claude Code CLI (defaut)
  OIE_EXTERNAL_PROVIDER=anthropic_sdk   : SDK Anthropic mesure reel (V0.4)
  OIE_EXTERNAL_PROVIDER=gemini_sdk      : SDK Gemini mesure reel (V0.5)

Model SDK (jamais hardcode) :
  OIE_EXTERNAL_MODEL_LABEL=<model_id>   : requis si provider != cli
    Exemples : claude-haiku-4-5-20251001, gemini-2.0-flash-lite

Prix optionnels (jamais hardcodes ici) :
  OIE_EXTERNAL_INPUT_COST_PER_1M   EUR / 1M tokens input
  OIE_EXTERNAL_OUTPUT_COST_PER_1M  EUR / 1M tokens output

Securite :
- ANTHROPIC_API_KEY lue uniquement depuis env. Jamais logguee. Jamais dans les receipts.
- GEMINI_API_KEY / GOOGLE_API_KEY lues uniquement depuis env. Jamais logguees.
- Aucun autre secret dans le repo.
- Aucun appel reseau sans OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1.
- Console ASCII uniquement (compatible Windows cp1252).

Non-souverain : readonly=True, emits_act=False, kernel_mutation=False.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.inference_economy.external_comparison import (
    ExternalComparisonReceipt,
    detect_claude_cli,
    run_claude_cli,
    run_anthropic_sdk,
    run_gemini_sdk,
    compute_comparison,
    compute_measured_sdk_cost,
    evaluate_route_quality,
    evaluate_domain_output_quality,
    compute_estimated_external_cost,
    compute_oie_differential_metrics,
    detect_failure_type,
    EXCERPT_MAX_CHARS,
    ERROR_USAGE_ONLY,
    BENCHMARK_KIND_ROUTING,
    BENCHMARK_KIND_DOMAIN_OUTPUT,
    KNOWN_ROUTES,
    AXIS_ROUTING,
    AXIS_DOMAIN_DECISION,
    AXIS_DOMAIN_OUTPUT,
    AXIS_CODE_PROOF,
    AXIS_BRODY_RESPONSE,
    AXIS_FAST_PATH,
    FAILURE_NONE,
    PROVIDER_CLI,
    PROVIDER_SDK,
    PROVIDER_GEMINI,
    COST_SOURCE_UNAVAILABLE,
    COST_SOURCE_ESTIMATED,
    COST_SOURCE_SDK_NO_PRICE,
    COST_SOURCE_SDK_MEASURED,
)

# ── Routing tasks ─────────────────────────────────────────────────────────────
# Chaque prompt demande UNE SEULE route parmi KNOWN_ROUTES.
# Evalue par evaluate_route_quality.

ROUTING_TASKS = [
    {
        "task_id": "fastpath_route_selection_smoke",
        "task_family": "fast_path_vs_llm_simple",
        "task_prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: ping health check."
        ),
        "obsidia_route": "fast_path",
        "obsidia_expected_output_type": "route_label",
        "obsidia_cost_eur_per_1m": 0.0015,
        "obsidia_latency_ms": 0.5,
        "expected_route": "FAST_PATH",
        "expected_output_hint": "one of: FAST_PATH BRODY BANK TRADING GPS OBSIDURE",
        "benchmark_kind": BENCHMARK_KIND_ROUTING,
        "comparison_axis": AXIS_FAST_PATH,
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_execution_layer": "cache_lookup",
        "smoke": True,
    },
    {
        "task_id": "brody_route_selection",
        "task_family": "brody_vs_assistant",
        "task_prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: what is the Obsidia kernel responsible for?"
        ),
        "obsidia_route": "brody_chat",
        "obsidia_expected_output_type": "route_label",
        "obsidia_cost_eur_per_1m": 0.20,
        "obsidia_latency_ms": 85.0,
        "expected_route": "BRODY",
        "expected_output_hint": "one of: FAST_PATH BRODY BANK TRADING GPS OBSIDURE",
        "benchmark_kind": BENCHMARK_KIND_ROUTING,
        "comparison_axis": AXIS_ROUTING,
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_execution_layer": "brody_router",
        "smoke": False,
    },
    {
        "task_id": "bank_route_selection",
        "task_family": "bank_vs_domain_llm",
        "task_prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: process a wire transfer compliance check."
        ),
        "obsidia_route": "bank_connector",
        "obsidia_expected_output_type": "route_label",
        "obsidia_cost_eur_per_1m": 0.70,
        "obsidia_latency_ms": 42.0,
        "expected_route": "BANK",
        "expected_output_hint": "one of: FAST_PATH BRODY BANK TRADING GPS OBSIDURE",
        "benchmark_kind": BENCHMARK_KIND_ROUTING,
        "comparison_axis": AXIS_ROUTING,
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_execution_layer": "domain_bridge",
        "smoke": False,
    },
    {
        "task_id": "trading_route_selection",
        "task_family": "trading_vs_domain_llm",
        "task_prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: validate a BUY signal for asset X."
        ),
        "obsidia_route": "trading_connector",
        "obsidia_expected_output_type": "route_label",
        "obsidia_cost_eur_per_1m": 0.84,
        "obsidia_latency_ms": 18.0,
        "expected_route": "TRADING",
        "expected_output_hint": "one of: FAST_PATH BRODY BANK TRADING GPS OBSIDURE",
        "benchmark_kind": BENCHMARK_KIND_ROUTING,
        "comparison_axis": AXIS_ROUTING,
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_execution_layer": "domain_bridge",
        "smoke": False,
    },
    {
        "task_id": "gps_route_selection",
        "task_family": "gps_aviation_vs_domain_llm",
        "task_prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: check terrain clearance for route R47."
        ),
        "obsidia_route": "aviation_connector",
        "obsidia_expected_output_type": "route_label",
        "obsidia_cost_eur_per_1m": 0.91,
        "obsidia_latency_ms": 9.5,
        "expected_route": "GPS",
        "expected_output_hint": "one of: FAST_PATH BRODY BANK TRADING GPS OBSIDURE",
        "benchmark_kind": BENCHMARK_KIND_ROUTING,
        "comparison_axis": AXIS_ROUTING,
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_execution_layer": "domain_bridge",
        "smoke": False,
    },
    {
        "task_id": "obsidure_route_selection",
        "task_family": "obsidure_vs_code_agent",
        "task_prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: generate a Lean 4 proof patch for n + 0 = n."
        ),
        "obsidia_route": "obsidure_lean_targeted",
        "obsidia_expected_output_type": "route_label",
        "obsidia_cost_eur_per_1m": 23.92,
        "obsidia_latency_ms": 1200.0,
        "expected_route": "OBSIDURE",
        "expected_output_hint": "one of: FAST_PATH BRODY BANK TRADING GPS OBSIDURE",
        "benchmark_kind": BENCHMARK_KIND_ROUTING,
        "comparison_axis": AXIS_CODE_PROOF,
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_execution_layer": "obsidure_targeted",
        "smoke": False,
    },
    {
        "task_id": "lean_route_selection",
        "task_family": "lean_proof_vs_long_reasoning",
        "task_prompt": (
            "Return only one route label from this list: "
            "FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE. "
            "Request: verify the Lean 4 invariant forall n : Nat, n + 0 = n."
        ),
        "obsidia_route": "lean_canon_check",
        "obsidia_expected_output_type": "route_label",
        "obsidia_cost_eur_per_1m": 13.29,
        "obsidia_latency_ms": 200.0,
        "expected_route": "OBSIDURE",
        "expected_output_hint": "one of: FAST_PATH BRODY BANK TRADING GPS OBSIDURE",
        "benchmark_kind": BENCHMARK_KIND_ROUTING,
        "comparison_axis": AXIS_CODE_PROOF,
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_execution_layer": "lean_canon",
        "smoke": False,
    },
]

# ── Domain output tasks ───────────────────────────────────────────────────────
# Prompts stricts : "Return exactly one label from: X, Y, Z. Do not explain."
# Mention "simulated" pour eviter refus provider.
# Evalue par evaluate_domain_output_quality.

DOMAIN_OUTPUT_TASKS = [
    {
        "task_id": "bank_decision_smoke",
        "task_family": "bank_vs_domain_llm",
        "task_prompt": (
            "Return exactly one label from: ALLOW, HOLD, BLOCK. Do not explain. "
            "Scenario: simulated compliance-safe wire transfer, no real financial action."
        ),
        "obsidia_route": "bank_connector",
        "obsidia_expected_output_type": "ALLOW_HOLD_BLOCK",
        "obsidia_cost_eur_per_1m": 0.70,
        "obsidia_latency_ms": 42.0,
        "expected_labels": ["ALLOW", "HOLD", "BLOCK"],
        "expected_output_hint": "one of: ALLOW HOLD BLOCK",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "comparison_axis": AXIS_DOMAIN_DECISION,
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_execution_layer": "domain_bridge_deterministic",
        "smoke": False,
    },
    {
        "task_id": "trading_signal_smoke",
        "task_family": "trading_vs_domain_llm",
        "task_prompt": (
            "Return exactly one label from: VALID, HOLD_RISK, BLOCK. Do not explain. "
            "Scenario: simulated BUY signal with confidence 0.87, no real trading action."
        ),
        "obsidia_route": "trading_connector",
        "obsidia_expected_output_type": "VALID_HOLD_RISK_BLOCK",
        "obsidia_cost_eur_per_1m": 0.84,
        "obsidia_latency_ms": 18.0,
        "expected_labels": ["VALID", "HOLD_RISK", "BLOCK"],
        "expected_output_hint": "one of: VALID HOLD_RISK BLOCK",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "comparison_axis": AXIS_DOMAIN_DECISION,
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_execution_layer": "domain_bridge_deterministic",
        "smoke": False,
    },
    {
        "task_id": "gps_terrain_smoke",
        "task_family": "gps_aviation_vs_domain_llm",
        "task_prompt": (
            "Return exactly one label from: ALLOW, HOLD, BLOCK. Do not explain. "
            "Scenario: simulated terrain clearance check, altitude 950m, no real navigation action."
        ),
        "obsidia_route": "aviation_connector",
        "obsidia_expected_output_type": "ALLOW_HOLD_BLOCK",
        "obsidia_cost_eur_per_1m": 0.91,
        "obsidia_latency_ms": 9.5,
        "expected_labels": ["ALLOW", "HOLD", "BLOCK"],
        "expected_output_hint": "one of: ALLOW HOLD BLOCK",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "comparison_axis": AXIS_DOMAIN_DECISION,
        "obsidia_model_call_required": False,
        "external_model_call_required": True,
        "obsidia_execution_layer": "domain_bridge_deterministic",
        "smoke": False,
    },
    {
        "task_id": "brody_answer_smoke",
        "task_family": "brody_vs_assistant",
        "task_prompt": (
            "Return exactly one label from: ANSWER_OK, ANSWER_FAIL. Do not explain. "
            "Scenario: answer quality check for a simulated Obsidia kernel explanation."
        ),
        "obsidia_route": "brody_chat",
        "obsidia_expected_output_type": "ANSWER_OK_FAIL",
        "obsidia_cost_eur_per_1m": 0.20,
        "obsidia_latency_ms": 85.0,
        "expected_labels": ["ANSWER_OK", "ANSWER_FAIL"],
        "expected_output_hint": "one of: ANSWER_OK ANSWER_FAIL",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "comparison_axis": AXIS_BRODY_RESPONSE,
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_execution_layer": "brody_router",
        "smoke": False,
    },
    {
        "task_id": "obsidure_patch_smoke",
        "task_family": "obsidure_vs_code_agent",
        "task_prompt": (
            "Return exactly one label from: PATCH_OK, PATCH_FAIL. Do not explain. "
            "Scenario: simulated Lean 4 proof patch for theorem Nat.add_zero."
        ),
        "obsidia_route": "obsidure_lean_targeted",
        "obsidia_expected_output_type": "PATCH_OK_FAIL",
        "obsidia_cost_eur_per_1m": 23.92,
        "obsidia_latency_ms": 1200.0,
        "expected_labels": ["PATCH_OK", "PATCH_FAIL"],
        "expected_output_hint": "one of: PATCH_OK PATCH_FAIL",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "comparison_axis": AXIS_CODE_PROOF,
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_execution_layer": "obsidure_targeted",
        "smoke": False,
    },
    {
        "task_id": "lean_invariant_smoke",
        "task_family": "lean_proof_vs_long_reasoning",
        "task_prompt": (
            "Return exactly one label from: PROOF_OK, PROOF_FAIL. Do not explain. "
            "Scenario: simulated proof check, theorem Nat.add_zero exists in Lean 4 standard library."
        ),
        "obsidia_route": "lean_canon_check",
        "obsidia_expected_output_type": "PROOF_OK_FAIL",
        "obsidia_cost_eur_per_1m": 13.29,
        "obsidia_latency_ms": 200.0,
        "expected_labels": ["PROOF_OK", "PROOF_FAIL"],
        "expected_output_hint": "one of: PROOF_OK PROOF_FAIL",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "comparison_axis": AXIS_CODE_PROOF,
        "obsidia_model_call_required": True,
        "external_model_call_required": True,
        "obsidia_execution_layer": "lean_canon",
        "smoke": False,
    },
]

# ── TASKS : union pour compatibilite V0 ───────────────────────────────────────
TASKS = ROUTING_TASKS + DOMAIN_OUTPUT_TASKS


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_cost_env() -> tuple[Optional[float], Optional[float], str]:
    """Read optional pricing from env. Never hardcoded."""
    try:
        inp = float(os.environ["OIE_EXTERNAL_INPUT_COST_PER_1M"])
    except (KeyError, ValueError):
        inp = None
    try:
        out = float(os.environ["OIE_EXTERNAL_OUTPUT_COST_PER_1M"])
    except (KeyError, ValueError):
        out = None
    model_label = os.environ.get("OIE_EXTERNAL_MODEL_LABEL", "unknown")
    return inp, out, model_label


def _task_receipt_base(task: dict, claude_available: bool, claude_cmd: str) -> dict:
    """Common receipt kwargs extracted from a task dict."""
    return dict(
        task_id=task["task_id"],
        task_family=task["task_family"],
        task_prompt=task["task_prompt"][:EXCERPT_MAX_CHARS],
        obsidia_route=task["obsidia_route"],
        obsidia_expected_output_type=task["obsidia_expected_output_type"],
        obsidia_cost_eur_per_1m=task["obsidia_cost_eur_per_1m"],
        obsidia_latency_ms=task["obsidia_latency_ms"],
        obsidia_success=True,
        external_provider="claude_code_cli",
        external_model_or_cli="claude",
        external_command_detected=claude_cmd,
        external_available=claude_available,
        benchmark_kind=task.get("benchmark_kind", BENCHMARK_KIND_ROUTING),
        comparison_axis=task.get("comparison_axis", ""),
        obsidia_model_call_required=task.get("obsidia_model_call_required", False),
        external_model_call_required=task.get("external_model_call_required", True),
        obsidia_execution_layer=task.get("obsidia_execution_layer", ""),
        expected_route=task.get("expected_route", ""),
        expected_output_hint=task.get("expected_output_hint", ""),
        expected_labels=task.get("expected_labels"),
    )


def build_dry_run_receipt(
    task: dict, claude_available: bool, claude_cmd: str
) -> ExternalComparisonReceipt:
    return ExternalComparisonReceipt(
        **_task_receipt_base(task, claude_available, claude_cmd),
        external_network_allowed=False,
        external_latency_ms=None,
        external_success=False,
        external_error="NETWORK_DISABLED",
        external_output_excerpt="",
        external_usage_available=False,
        cost_source="USAGE_UNAVAILABLE",
        external_detected_route=None,
        route_match=None,
        quality_score=None,
        quality_notes="DRY_RUN",
        classification_error_type=ERROR_USAGE_ONLY,
        external_detected_label=None,
        label_match=None,
        savings_ratio_vs_external=None,
        avoided_cost_eur_per_1m=None,
        timeout_occurred=False,
        encoding_error_occurred=False,
        parser_error_occurred=False,
        external_failure_type=FAILURE_NONE,
    )


def _apply_sdk_cost(run_result: dict, cost_estimate_enabled: bool) -> tuple[str, Optional[float], Optional[float], Optional[float]]:
    """Resolve cost_source and measured cost fields from an SDK run result.

    Returns (cost_source, external_cost_eur_measured, external_cost_eur_per_1m_measured, savings_ratio_hint).
    """
    inp_cost, out_cost, _ = _read_cost_env() if cost_estimate_enabled else (None, None, None)
    if run_result.get("usage_available") and run_result.get("input_tokens") is not None:
        sdk_cost = compute_measured_sdk_cost(
            input_tokens=run_result["input_tokens"],
            output_tokens=run_result["output_tokens"],
            input_cost_per_1m=inp_cost,
            output_cost_per_1m=out_cost,
        )
        return sdk_cost["cost_source"], sdk_cost.get("measured_cost_eur"), sdk_cost.get("measured_cost_eur_per_1m"), sdk_cost.get("measured_cost_eur_per_1m")
    if cost_estimate_enabled and inp_cost is not None and out_cost is not None:
        return COST_SOURCE_ESTIMATED, None, None, None
    return COST_SOURCE_UNAVAILABLE, None, None, None


def build_real_receipt(
    task: dict,
    claude_available: bool,
    claude_cmd: str,
    run_result: dict,
    cost_estimate_enabled: bool,
    provider: str = PROVIDER_CLI,
) -> ExternalComparisonReceipt:
    kind = task.get("benchmark_kind", BENCHMARK_KIND_ROUTING)
    output = run_result.get("output_excerpt", "")
    success = run_result.get("success", False)
    failure_type = run_result.get("failure_type", FAILURE_NONE)
    timeout_occurred = run_result.get("timeout_occurred", False)
    encoding_occurred = run_result.get("encoding_error_occurred", False)

    # SDK usage fields
    usage_available = run_result.get("usage_available", False)
    input_tokens = run_result.get("input_tokens")
    output_tokens = run_result.get("output_tokens")
    total_tokens = run_result.get("total_tokens")
    model_label = run_result.get("model_label", "")

    route_quality: dict = {}
    label_quality: dict = {}
    parser_error = False

    if kind == BENCHMARK_KIND_ROUTING:
        route_quality = evaluate_route_quality(
            expected_route=task.get("expected_route", ""),
            external_output=output,
            external_success=success,
        )
        parser_error = route_quality.get("classification_error_type") == "UNPARSEABLE_OUTPUT"
    else:
        label_quality = evaluate_domain_output_quality(
            expected_labels=task.get("expected_labels", []),
            external_output=output,
            external_success=success,
        )
        parser_error = label_quality.get("classification_error_type") == "UNPARSEABLE_OUTPUT"

    # Cost resolution
    cost_src = COST_SOURCE_UNAVAILABLE
    measured_cost_eur: Optional[float] = None
    measured_cost_eur_per_1m: Optional[float] = None
    ratio: Optional[float] = None
    avoided: Optional[float] = None

    if provider in (PROVIDER_SDK, PROVIDER_GEMINI) and usage_available and input_tokens is not None:
        # SDK path (Anthropic ou Gemini) : tokens réels => compute_measured_sdk_cost
        # Ne dépend PAS de OIE_EXTERNAL_COST_ESTIMATE (réservé à l'estimation texte/CLI)
        inp_p, out_p, _ = _read_cost_env()
        sdk_cost = compute_measured_sdk_cost(input_tokens, output_tokens or 0, inp_p, out_p)
        cost_src = sdk_cost["cost_source"]
        measured_cost_eur = sdk_cost.get("measured_cost_eur")
        measured_cost_eur_per_1m = sdk_cost.get("measured_cost_eur_per_1m")
        if measured_cost_eur_per_1m is not None:
            ratio_val, avoided_val, _ = compute_comparison(task["obsidia_cost_eur_per_1m"], measured_cost_eur_per_1m)
            ratio, avoided = ratio_val, avoided_val
    elif cost_estimate_enabled:
        inp_p, out_p, _ = _read_cost_env()
        estimated = compute_estimated_external_cost(
            input_text=task["task_prompt"], output_text=output,
            input_cost_per_1m=inp_p, output_cost_per_1m=out_p,
        )
        if estimated["cost_source"] == COST_SOURCE_ESTIMATED:
            cost_src = COST_SOURCE_ESTIMATED

    q_score = route_quality.get("quality_score") if kind == BENCHMARK_KIND_ROUTING else label_quality.get("quality_score")

    return ExternalComparisonReceipt(
        **_task_receipt_base(task, claude_available, claude_cmd),
        external_network_allowed=True,
        external_latency_ms=run_result.get("latency_ms"),
        external_success=success,
        external_error=run_result.get("error", ""),
        external_output_excerpt=output,
        external_usage_available=usage_available,
        external_input_tokens=input_tokens,
        external_output_tokens=output_tokens,
        external_total_tokens=total_tokens,
        external_model_label=model_label,
        external_cost_eur_measured=measured_cost_eur,
        external_cost_eur_per_1m_measured=measured_cost_eur_per_1m,
        cost_source=cost_src,
        external_detected_route=route_quality.get("external_detected_route"),
        route_match=route_quality.get("route_match"),
        quality_score=q_score,
        quality_notes=route_quality.get("quality_notes", "") if kind == BENCHMARK_KIND_ROUTING else label_quality.get("quality_notes", ""),
        classification_error_type=route_quality.get("classification_error_type", ERROR_USAGE_ONLY) if kind == BENCHMARK_KIND_ROUTING else label_quality.get("classification_error_type", ERROR_USAGE_ONLY),
        external_detected_label=label_quality.get("external_detected_label"),
        label_match=label_quality.get("label_match"),
        savings_ratio_vs_external=ratio,
        avoided_cost_eur_per_1m=avoided,
        timeout_occurred=timeout_occurred,
        encoding_error_occurred=encoding_occurred,
        parser_error_occurred=parser_error,
        external_failure_type=failure_type,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    network_allowed = os.environ.get("OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK", "0") == "1"
    full_run = os.environ.get("OIE_EXTERNAL_BENCHMARK_FULL", "0") == "1"
    domain_run = os.environ.get("OIE_EXTERNAL_BENCHMARK_DOMAIN", "0") == "1"
    cost_estimate_enabled = os.environ.get("OIE_EXTERNAL_COST_ESTIMATE", "0") == "1"
    provider = os.environ.get("OIE_EXTERNAL_PROVIDER", PROVIDER_CLI)
    sdk_model = os.environ.get("OIE_EXTERNAL_MODEL_LABEL", "")
    mode = "REAL" if network_allowed else "DRY_RUN"

    claude_available, claude_cmd, claude_info = detect_claude_cli()

    print("\n=== OIE External Benchmark Harness V0.4 ===\n")
    print(f"  Mode                   : {mode}")
    print(f"  Provider               : {provider}")
    print(f"  Network allowed        : {network_allowed}")
    if provider == PROVIDER_CLI:
        print(f"  Claude detected        : {claude_available}")
        if claude_available:
            print(f"  Claude command         : {claude_cmd}")
            print(f"  Claude info            : {claude_info[:80]}")
    elif provider == PROVIDER_GEMINI:
        print(f"  SDK model              : {sdk_model if sdk_model else '(not set - GEMINI_MODEL_NOT_CONFIGURED)'}")
        # Never print key values
        print(f"  GEMINI_API_KEY set     : {bool(os.environ.get('GEMINI_API_KEY', ''))}")
        print(f"  GOOGLE_API_KEY set     : {bool(os.environ.get('GOOGLE_API_KEY', ''))}")
    else:
        print(f"  SDK model              : {sdk_model if sdk_model else '(not set - MODEL_NOT_CONFIGURED)'}")
        # Never print API key
        key_set = bool(os.environ.get("ANTHROPIC_API_KEY", ""))
        print(f"  ANTHROPIC_API_KEY set  : {key_set}")
    print(f"  Full routing run       : {full_run}")
    print(f"  Domain output run      : {domain_run}")
    print(f"  Cost estimate enabled  : {cost_estimate_enabled}")
    if cost_estimate_enabled or provider == PROVIDER_SDK:
        inp_c, out_c, mlabel = _read_cost_env()
        print(f"  Input cost /1M         : {inp_c}")
        print(f"  Output cost /1M        : {out_c}")
        if provider == PROVIDER_CLI:
            print(f"  Model label            : {mlabel}")
    print()

    if domain_run:
        tasks_to_run = DOMAIN_OUTPUT_TASKS
        active_kind = "DOMAIN_OUTPUT"
    elif full_run:
        tasks_to_run = ROUTING_TASKS
        active_kind = "ROUTING_FULL"
    else:
        tasks_to_run = [t for t in ROUTING_TASKS if t.get("smoke", False)]
        active_kind = "ROUTING_SMOKE"

    print(f"  Active kind            : {active_kind}")
    print(f"  Tasks selected         : {len(tasks_to_run)} / {len(TASKS)}")
    print()

    receipts = []

    for task in tasks_to_run:
        kind = task.get("benchmark_kind", BENCHMARK_KIND_ROUTING)
        print(f"  [{kind}] [{task['task_family']}] {task['task_id']}")
        print(f"    axis            : {task.get('comparison_axis', 'N/A')}")
        print(f"    model_call_req  : obsidia={task.get('obsidia_model_call_required')} external={task.get('external_model_call_required')}")
        if kind == BENCHMARK_KIND_ROUTING:
            print(f"    expected_route  : {task.get('expected_route', 'N/A')}")
        else:
            print(f"    expected_labels : {task.get('expected_labels', [])}")

        if not network_allowed:
            receipt = build_dry_run_receipt(task, claude_available, claude_cmd)
            print(f"    -> DRY_RUN | obsidia={task['obsidia_cost_eur_per_1m']} EUR/1M")
        elif provider == PROVIDER_SDK:
            if not sdk_model:
                run_result = {
                    "success": False, "latency_ms": 0.0, "output_excerpt": "",
                    "error": "MODEL_NOT_CONFIGURED", "timeout_occurred": False,
                    "encoding_error_occurred": False, "failure_type": "MODEL_NOT_CONFIGURED",
                    "usage_available": False, "input_tokens": None, "output_tokens": None,
                    "total_tokens": None, "model_label": "",
                }
            else:
                print(f"    -> RUNNING anthropic SDK model={sdk_model} ...")
                run_result = run_anthropic_sdk(task["task_prompt"], sdk_model)
            receipt = build_real_receipt(
                task, claude_available, claude_cmd, run_result, cost_estimate_enabled, provider=PROVIDER_SDK
            )
            status = "OK" if run_result["success"] else f"FAIL({run_result['error'][:40]})"
            usage_str = f"in={run_result.get('input_tokens')} out={run_result.get('output_tokens')}" if run_result.get("usage_available") else "usage=unavailable"
            print(f"    -> {status} | latency={run_result.get('latency_ms', 0):.0f}ms | {usage_str}")
            print(f"    cost_source     : {receipt.cost_source}")
            if receipt.external_cost_eur_per_1m_measured is not None:
                print(f"    measured EUR/1M : {receipt.external_cost_eur_per_1m_measured:.4f}")
        elif provider == PROVIDER_GEMINI:
            if not sdk_model:
                run_result = {
                    "success": False, "latency_ms": 0.0, "output_excerpt": "",
                    "error": "GEMINI_MODEL_NOT_CONFIGURED", "timeout_occurred": False,
                    "encoding_error_occurred": False, "failure_type": "GEMINI_MODEL_NOT_CONFIGURED",
                    "usage_available": False, "input_tokens": None, "output_tokens": None,
                    "total_tokens": None, "model_label": "",
                }
            else:
                print(f"    -> RUNNING gemini SDK model={sdk_model} ...")
                run_result = run_gemini_sdk(task["task_prompt"], sdk_model)
            receipt = build_real_receipt(
                task, claude_available, claude_cmd, run_result, cost_estimate_enabled, provider=PROVIDER_GEMINI
            )
            status = "OK" if run_result["success"] else f"FAIL({run_result['error'][:40]})"
            usage_str = f"in={run_result.get('input_tokens')} out={run_result.get('output_tokens')}" if run_result.get("usage_available") else "usage=unavailable"
            print(f"    -> {status} | latency={run_result.get('latency_ms', 0):.0f}ms | {usage_str}")
            print(f"    cost_source     : {receipt.cost_source}")
            if receipt.external_cost_eur_per_1m_measured is not None:
                print(f"    measured EUR/1M : {receipt.external_cost_eur_per_1m_measured:.4f}")
        elif not claude_available:
            receipt = ExternalComparisonReceipt(
                **_task_receipt_base(task, claude_available, claude_cmd),
                external_network_allowed=True,
                external_success=False,
                external_error="CLAUDE_NOT_AVAILABLE",
                expected_route=task.get("expected_route", ""),
                expected_labels=task.get("expected_labels"),
                classification_error_type=ERROR_USAGE_ONLY,
                external_failure_type="CLI_ERROR",
            )
            print(f"    -> SKIPPED | Claude not available")
        else:
            print(f"    -> RUNNING claude -p ...")
            run_result = run_claude_cli(task["task_prompt"])
            receipt = build_real_receipt(
                task, claude_available, claude_cmd, run_result, cost_estimate_enabled, provider=PROVIDER_CLI
            )
            status = "OK" if run_result["success"] else f"FAIL({run_result['error'][:40]})"
            print(f"    -> {status} | latency={run_result.get('latency_ms', 0):.0f}ms | failure_type={run_result.get('failure_type', FAILURE_NONE)}")
            if run_result.get("encoding_error_occurred"):
                print(f"    WARN encoding   : replacement chars detected in output")
            if run_result.get("output_excerpt"):
                excerpt = run_result["output_excerpt"][:80].replace("\n", " ")
                print(f"    excerpt         : {excerpt}")

        if network_allowed and receipt.external_success:
            if kind == BENCHMARK_KIND_ROUTING:
                print(f"    detected_route  : {receipt.external_detected_route}")
                print(f"    route_match     : {receipt.route_match}")
            else:
                print(f"    detected_label  : {receipt.external_detected_label}")
                print(f"    label_match     : {receipt.label_match}")
            print(f"    quality_score   : {receipt.quality_score}")
            print(f"    error_type      : {receipt.classification_error_type}")

        receipts.append(receipt)
        print()

    # Summary
    routing_receipts = [r for r in receipts if r.benchmark_kind == BENCHMARK_KIND_ROUTING]
    domain_receipts = [r for r in receipts if r.benchmark_kind == BENCHMARK_KIND_DOMAIN_OUTPUT]

    route_matches = [r for r in routing_receipts if r.route_match is True]
    route_mismatches = [r for r in routing_receipts if r.route_match is False]
    label_matches = [r for r in domain_receipts if r.label_match is True]
    label_mismatches = [r for r in domain_receipts if r.label_match is False]

    r_quality = [r for r in routing_receipts if r.quality_score is not None]
    d_quality = [r for r in domain_receipts if r.quality_score is not None]
    avg_rq = sum(r.quality_score for r in r_quality) / len(r_quality) if r_quality else None
    avg_dq = sum(r.quality_score for r in d_quality) / len(d_quality) if d_quality else None

    all_quality = [r for r in receipts if r.quality_score is not None]
    avg_quality_penalty = (
        sum(1.0 - r.quality_score for r in all_quality) / len(all_quality)
        if all_quality else None
    )

    ext_successes = [r for r in receipts if r.external_success]
    usage_available = [r for r in receipts if r.external_usage_available]
    cost_estimated = [r for r in receipts if r.cost_source == "ESTIMATED"]
    cost_available = [r for r in receipts if r.cost_source in ("MEASURED", "ESTIMATED")]
    timeout_list = [r for r in receipts if r.timeout_occurred]
    encoding_list = [r for r in receipts if r.encoding_error_occurred]
    refusal_list = [r for r in receipts if r.external_failure_type == "PROVIDER_REFUSAL"]

    model_call_avoided = [r for r in receipts if r.external_model_call_required and not r.obsidia_model_call_required]

    cost_source_counts: dict[str, int] = {}
    for r in receipts:
        cost_source_counts[r.cost_source] = cost_source_counts.get(r.cost_source, 0) + 1

    # Full routing compact table (printed when running full or domain run)
    if (full_run or domain_run) and receipts:
        print("--- Per-task compact table ---")
        hdr = f"{'task_id':<38} {'exp_route':<14} {'det_route':<14} {'match':<6} {'lat_ms':>8} {'in_tok':>7} {'out_tok':>8} {'tot_tok':>8} {'cost_src':<24} {'qual':>5} {'savings':>10}"
        print(hdr)
        print("-" * len(hdr))
        for r in receipts:
            exp = getattr(r, "expected_route", "") or ""
            det = getattr(r, "external_detected_route", "") or getattr(r, "external_detected_label", "") or ""
            match_s = str(r.route_match if r.benchmark_kind == BENCHMARK_KIND_ROUTING else r.label_match)
            lat = f"{r.external_latency_ms:.1f}" if r.external_latency_ms is not None else "N/A"
            in_t = str(r.external_input_tokens) if r.external_input_tokens is not None else "-"
            out_t = str(r.external_output_tokens) if r.external_output_tokens is not None else "-"
            tot_t = str(r.external_total_tokens) if r.external_total_tokens is not None else "-"
            qual = f"{r.quality_score:.2f}" if r.quality_score is not None else "N/A"
            sav = f"{r.savings_ratio_vs_external:.1f}x" if r.savings_ratio_vs_external is not None else "N/A"
            print(f"{r.task_id:<38} {exp:<14} {det:<14} {match_s:<6} {lat:>8} {in_t:>7} {out_t:>8} {tot_t:>8} {r.cost_source:<24} {qual:>5} {sav:>10}")
        print()

    print("--- Receipts summary ---")
    print(f"  Total receipts              : {len(receipts)}")
    print(f"  Routing tasks               : {len(routing_receipts)}")
    print(f"  Domain output tasks         : {len(domain_receipts)}")
    print(f"  External success            : {len(ext_successes)}")
    print(f"  Route match                 : {len(route_matches)}")
    print(f"  Route mismatch              : {len(route_mismatches)}")
    print(f"  Label match                 : {len(label_matches)}")
    print(f"  Label mismatch              : {len(label_mismatches)}")
    print(f"  Avg routing quality         : {f'{avg_rq:.2f}' if avg_rq is not None else 'N/A'}")
    print(f"  Avg domain quality          : {f'{avg_dq:.2f}' if avg_dq is not None else 'N/A'}")
    print(f"  Avg quality penalty         : {f'{avg_quality_penalty:.3f}' if avg_quality_penalty is not None else 'N/A'}")
    print(f"  Model call avoided          : {len(model_call_avoided)}")
    print(f"  Model call avoided rate     : {len(model_call_avoided)/len(receipts):.2f}" if receipts else "  Model call avoided rate     : N/A")
    print(f"  Usage available             : {len(usage_available)}")
    print(f"  Cost estimated              : {len(cost_estimated)}")
    print(f"  Timeout count               : {len(timeout_list)}")
    print(f"  Encoding warning count      : {len(encoding_list)}")
    print(f"  Provider refusal count      : {len(refusal_list)}")
    print(f"  Non-sovereign               : all (emits_act=False, kernel_mutation=False)")
    print(f"  Secrets redacted            : True")
    print()

    benchmark_id = str(uuid.uuid4())
    output_payload = {
        "benchmark_id": benchmark_id,
        "benchmark": "OIE_EXTERNAL_BENCHMARK_V0.5",
        "mode": mode,
        "active_kind": active_kind,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "network_allowed": network_allowed,
        "claude_detected": claude_available,
        "claude_command": claude_cmd,
        "tasks_run": len(receipts),
        "full_run": full_run,
        "domain_run": domain_run,
        "cost_estimate_enabled": cost_estimate_enabled,
        "summary": {
            "tasks_attempted": len(receipts),
            "benchmark_kind": active_kind,
            "routing_tasks_attempted": len(routing_receipts),
            "domain_tasks_attempted": len(domain_receipts),
            "external_success_count": len(ext_successes),
            "route_match_count": len(route_matches),
            "route_mismatch_count": len(route_mismatches),
            "label_match_count": len(label_matches),
            "label_mismatch_count": len(label_mismatches),
            "avg_route_quality_score": round(avg_rq, 4) if avg_rq is not None else None,
            "avg_domain_quality_score": round(avg_dq, 4) if avg_dq is not None else None,
            "avg_quality_penalty": round(avg_quality_penalty, 4) if avg_quality_penalty is not None else None,
            "model_call_avoided_count": len(model_call_avoided),
            "model_call_avoided_rate": round(len(model_call_avoided) / len(receipts), 4) if receipts else None,
            "usage_available_count": len(usage_available),
            "cost_available_rate": round(len(cost_available) / len(receipts), 4) if receipts else None,
            "cost_estimated_count": len(cost_estimated),
            "estimated_cost_rate": round(len(cost_estimated) / len(receipts), 4) if receipts else None,
            "cost_source_counts": cost_source_counts,
            "timeout_count": len(timeout_list),
            "provider_refusal_count": len(refusal_list),
            "encoding_warning_count": len(encoding_list),
            "differential_metrics_available": False,
            "savings_ratio_available": False,
            "governance": {
                "emits_act": False,
                "kernel_mutation": False,
                "readonly": True,
                "secrets_redacted": True,
            },
        },
        "receipts": [r.to_dict() for r in receipts],
    }

    out_path = Path(__file__).parent / "oie_external_claude_benchmark_v0_receipts.json"
    out_path.write_text(
        json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Receipts JSON -> {out_path}")
    print()
    print("Governance: readonly=True | emits_act=False | kernel_mutation=False | secrets_redacted=True")
    print()
    if not network_allowed:
        print("To enable real Claude calls:")
        print("  PowerShell : $env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK='1'")
        print("  Bash       : export OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1")
        print()
        print("To run all routing families:")
        print("  PowerShell : $env:OIE_EXTERNAL_BENCHMARK_FULL='1'")
        print()
        print("To run domain-output benchmark:")
        print("  PowerShell : $env:OIE_EXTERNAL_BENCHMARK_DOMAIN='1'")
        print()
        print("To enable token cost estimation:")
        print("  $env:OIE_EXTERNAL_INPUT_COST_PER_1M='3.0'")
        print("  $env:OIE_EXTERNAL_OUTPUT_COST_PER_1M='15.0'")
        print("  $env:OIE_EXTERNAL_COST_ESTIMATE='1'")
        print()


if __name__ == "__main__":
    main()
