#!/usr/bin/env python3
"""OIE External Benchmark Harness V0.2 -- Compare Obsidia vs Claude CLI.

Modes d'execution :
  Par defaut               : dry-run routing smoke uniquement
  OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1 : routing smoke reel
  OIE_EXTERNAL_BENCHMARK_FULL=1          : routing full (toutes familles)
  OIE_EXTERNAL_BENCHMARK_DOMAIN=1        : domain-output benchmark
  OIE_EXTERNAL_COST_ESTIMATE=1           : estimation tokens/cout si prix fournis

Prix optionnels (jamais hardcodes ici) :
  OIE_EXTERNAL_INPUT_COST_PER_1M   EUR / 1M tokens input
  OIE_EXTERNAL_OUTPUT_COST_PER_1M  EUR / 1M tokens output
  OIE_EXTERNAL_MODEL_LABEL         label du modele (audit uniquement)

Securite :
- Aucune cle API dans le repo.
- Aucun secret dans les receipts (secrets_redacted=True toujours).
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
    compute_comparison,
    evaluate_route_quality,
    evaluate_domain_output_quality,
    compute_estimated_external_cost,
    EXCERPT_MAX_CHARS,
    ERROR_USAGE_ONLY,
    BENCHMARK_KIND_ROUTING,
    BENCHMARK_KIND_DOMAIN_OUTPUT,
    KNOWN_ROUTES,
)

# ── Routing tasks ─────────────────────────────────────────────────────────────
# Chaque prompt demande UNE SEULE route parmi KNOWN_ROUTES.
# evaluated par evaluate_route_quality.

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
        "smoke": False,
    },
]

# ── Domain output tasks ───────────────────────────────────────────────────────
# Chaque prompt demande une sortie METIER specifique au domaine.
# Evalue par evaluate_domain_output_quality.

DOMAIN_OUTPUT_TASKS = [
    {
        "task_id": "bank_decision_smoke",
        "task_family": "bank_vs_domain_llm",
        "task_prompt": (
            "Given a wire transfer of 50000 EUR from account A to account B "
            "with no compliance flag, output one of: ALLOW, HOLD, BLOCK."
        ),
        "obsidia_route": "bank_connector",
        "obsidia_expected_output_type": "ALLOW_HOLD_BLOCK",
        "obsidia_cost_eur_per_1m": 0.70,
        "obsidia_latency_ms": 42.0,
        "expected_labels": ["ALLOW", "HOLD", "BLOCK"],
        "expected_output_hint": "one of: ALLOW HOLD BLOCK",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "smoke": False,
    },
    {
        "task_id": "trading_signal_smoke",
        "task_family": "trading_vs_domain_llm",
        "task_prompt": (
            "A BUY signal arrives for asset X with confidence 0.87 and "
            "no contradicting signals. Output one of: VALID, HOLD_RISK, BLOCK."
        ),
        "obsidia_route": "trading_connector",
        "obsidia_expected_output_type": "VALID_HOLD_RISK_BLOCK",
        "obsidia_cost_eur_per_1m": 0.84,
        "obsidia_latency_ms": 18.0,
        "expected_labels": ["VALID", "HOLD_RISK", "BLOCK"],
        "expected_output_hint": "one of: VALID HOLD_RISK BLOCK",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "smoke": False,
    },
    {
        "task_id": "gps_terrain_smoke",
        "task_family": "gps_aviation_vs_domain_llm",
        "task_prompt": (
            "Terrain signal: altitude 950m, obstacle clearance 120m, route R47. "
            "Is the route admissible? Output one of: ALLOW, HOLD, BLOCK."
        ),
        "obsidia_route": "aviation_connector",
        "obsidia_expected_output_type": "ALLOW_HOLD_BLOCK",
        "obsidia_cost_eur_per_1m": 0.91,
        "obsidia_latency_ms": 9.5,
        "expected_labels": ["ALLOW", "HOLD", "BLOCK"],
        "expected_output_hint": "one of: ALLOW HOLD BLOCK",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "smoke": False,
    },
    {
        "task_id": "brody_answer_smoke",
        "task_family": "brody_vs_assistant",
        "task_prompt": (
            "Question: What is the role of the Obsidia kernel? "
            "Did you provide a complete answer? Output one of: ANSWER_OK, ANSWER_FAIL."
        ),
        "obsidia_route": "brody_chat",
        "obsidia_expected_output_type": "ANSWER_OK_FAIL",
        "obsidia_cost_eur_per_1m": 0.20,
        "obsidia_latency_ms": 85.0,
        "expected_labels": ["ANSWER_OK", "ANSWER_FAIL"],
        "expected_output_hint": "one of: ANSWER_OK ANSWER_FAIL",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "smoke": False,
    },
    {
        "task_id": "obsidure_patch_smoke",
        "task_family": "obsidure_vs_code_agent",
        "task_prompt": (
            "Can you generate a valid Lean 4 proof for: theorem t : n + 0 = n := by simp? "
            "Output one of: PATCH_OK, PATCH_FAIL."
        ),
        "obsidia_route": "obsidure_lean_targeted",
        "obsidia_expected_output_type": "PATCH_OK_FAIL",
        "obsidia_cost_eur_per_1m": 23.92,
        "obsidia_latency_ms": 1200.0,
        "expected_labels": ["PATCH_OK", "PATCH_FAIL"],
        "expected_output_hint": "one of: PATCH_OK PATCH_FAIL",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "smoke": False,
    },
    {
        "task_id": "lean_invariant_smoke",
        "task_family": "lean_proof_vs_long_reasoning",
        "task_prompt": (
            "Can you verify that forall n : Nat, n + 0 = n is a valid Lean 4 theorem? "
            "Output one of: PROOF_OK, PROOF_FAIL."
        ),
        "obsidia_route": "lean_canon_check",
        "obsidia_expected_output_type": "PROOF_OK_FAIL",
        "obsidia_cost_eur_per_1m": 13.29,
        "obsidia_latency_ms": 200.0,
        "expected_labels": ["PROOF_OK", "PROOF_FAIL"],
        "expected_output_hint": "one of: PROOF_OK PROOF_FAIL",
        "benchmark_kind": BENCHMARK_KIND_DOMAIN_OUTPUT,
        "smoke": False,
    },
]

# ── TASKS : union pour compatibilite V0 ───────────────────────────────────────
TASKS = ROUTING_TASKS + DOMAIN_OUTPUT_TASKS


# ── Build helpers ─────────────────────────────────────────────────────────────

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


def build_dry_run_receipt(
    task: dict, claude_available: bool, claude_cmd: str
) -> ExternalComparisonReceipt:
    kind = task.get("benchmark_kind", BENCHMARK_KIND_ROUTING)
    return ExternalComparisonReceipt(
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
        external_network_allowed=False,
        external_latency_ms=None,
        external_success=False,
        external_error="NETWORK_DISABLED",
        external_output_excerpt="",
        external_usage_available=False,
        cost_source="USAGE_UNAVAILABLE",
        benchmark_kind=kind,
        expected_route=task.get("expected_route", ""),
        external_detected_route=None,
        route_match=None,
        expected_output_hint=task.get("expected_output_hint", ""),
        quality_score=None,
        quality_notes="DRY_RUN",
        classification_error_type=ERROR_USAGE_ONLY,
        expected_labels=task.get("expected_labels"),
        external_detected_label=None,
        label_match=None,
        savings_ratio_vs_external=None,
        avoided_cost_eur_per_1m=None,
    )


def build_real_receipt(
    task: dict,
    claude_available: bool,
    claude_cmd: str,
    run_result: dict,
    cost_estimate_enabled: bool,
) -> ExternalComparisonReceipt:
    ratio, avoided, cost_src = compute_comparison(
        task["obsidia_cost_eur_per_1m"],
        None,
    )
    kind = task.get("benchmark_kind", BENCHMARK_KIND_ROUTING)
    output = run_result.get("output_excerpt", "")
    success = run_result.get("success", False)

    # Routing evaluation
    route_quality: dict = {}
    label_quality: dict = {}
    if kind == BENCHMARK_KIND_ROUTING:
        route_quality = evaluate_route_quality(
            expected_route=task.get("expected_route", ""),
            external_output=output,
            external_success=success,
        )
    else:
        label_quality = evaluate_domain_output_quality(
            expected_labels=task.get("expected_labels", []),
            external_output=output,
            external_success=success,
        )

    # Token cost estimation
    estimated: dict | None = None
    if cost_estimate_enabled:
        inp_cost, out_cost, _ = _read_cost_env()
        estimated = compute_estimated_external_cost(
            input_text=task["task_prompt"],
            output_text=output,
            input_cost_per_1m=inp_cost,
            output_cost_per_1m=out_cost,
        )
        if estimated["cost_source"] == "ESTIMATED":
            cost_src = "ESTIMATED"

    return ExternalComparisonReceipt(
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
        external_network_allowed=True,
        external_latency_ms=run_result.get("latency_ms"),
        external_success=success,
        external_error=run_result.get("error", ""),
        external_output_excerpt=output,
        external_usage_available=False,
        cost_source=cost_src,
        benchmark_kind=kind,
        expected_route=task.get("expected_route", ""),
        external_detected_route=route_quality.get("external_detected_route"),
        route_match=route_quality.get("route_match"),
        expected_output_hint=task.get("expected_output_hint", ""),
        quality_score=route_quality.get("quality_score") if kind == BENCHMARK_KIND_ROUTING else label_quality.get("quality_score"),
        quality_notes=route_quality.get("quality_notes", "") if kind == BENCHMARK_KIND_ROUTING else label_quality.get("quality_notes", ""),
        classification_error_type=route_quality.get("classification_error_type", ERROR_USAGE_ONLY) if kind == BENCHMARK_KIND_ROUTING else label_quality.get("classification_error_type", ERROR_USAGE_ONLY),
        expected_labels=task.get("expected_labels"),
        external_detected_label=label_quality.get("external_detected_label"),
        label_match=label_quality.get("label_match"),
        savings_ratio_vs_external=ratio,
        avoided_cost_eur_per_1m=avoided,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    network_allowed = os.environ.get("OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK", "0") == "1"
    full_run = os.environ.get("OIE_EXTERNAL_BENCHMARK_FULL", "0") == "1"
    domain_run = os.environ.get("OIE_EXTERNAL_BENCHMARK_DOMAIN", "0") == "1"
    cost_estimate_enabled = os.environ.get("OIE_EXTERNAL_COST_ESTIMATE", "0") == "1"
    mode = "REAL" if network_allowed else "DRY_RUN"

    claude_available, claude_cmd, claude_info = detect_claude_cli()

    print("\n=== OIE External Benchmark Harness V0.2 ===\n")
    print(f"  Mode                   : {mode}")
    print(f"  Network allowed        : {network_allowed}")
    print(f"  Claude detected        : {claude_available}")
    if claude_available:
        print(f"  Claude command         : {claude_cmd}")
        print(f"  Claude info            : {claude_info[:80]}")
    print(f"  Full routing run       : {full_run}")
    print(f"  Domain output run      : {domain_run}")
    print(f"  Cost estimate enabled  : {cost_estimate_enabled}")
    if cost_estimate_enabled:
        inp_c, out_c, mlabel = _read_cost_env()
        print(f"  Input cost /1M         : {inp_c}")
        print(f"  Output cost /1M        : {out_c}")
        print(f"  Model label            : {mlabel}")
    print()

    # Task selection
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
        if kind == BENCHMARK_KIND_ROUTING:
            print(f"    expected_route  : {task.get('expected_route', 'N/A')}")
        else:
            print(f"    expected_labels : {task.get('expected_labels', [])}")

        if not network_allowed:
            receipt = build_dry_run_receipt(task, claude_available, claude_cmd)
            print(f"    -> DRY_RUN | obsidia={task['obsidia_cost_eur_per_1m']} EUR/1M")
        elif not claude_available:
            receipt = ExternalComparisonReceipt(
                task_id=task["task_id"],
                task_family=task["task_family"],
                benchmark_kind=kind,
                external_available=False,
                external_network_allowed=True,
                external_success=False,
                external_error="CLAUDE_NOT_AVAILABLE",
                expected_route=task.get("expected_route", ""),
                expected_labels=task.get("expected_labels"),
                classification_error_type=ERROR_USAGE_ONLY,
            )
            print(f"    -> SKIPPED | Claude not available")
        else:
            print(f"    -> RUNNING claude -p ...")
            run_result = run_claude_cli(task["task_prompt"])
            receipt = build_real_receipt(
                task, claude_available, claude_cmd, run_result, cost_estimate_enabled
            )
            status = "OK" if run_result["success"] else f"FAIL({run_result['error']})"
            print(f"    -> {status} | latency={run_result['latency_ms']:.0f}ms")
            if kind == BENCHMARK_KIND_ROUTING:
                print(f"    detected_route  : {receipt.external_detected_route}")
                print(f"    route_match     : {receipt.route_match}")
            else:
                print(f"    detected_label  : {receipt.external_detected_label}")
                print(f"    label_match     : {receipt.label_match}")
            print(f"    quality_score   : {receipt.quality_score}")
            print(f"    error_type      : {receipt.classification_error_type}")
            if run_result.get("output_excerpt"):
                excerpt = run_result["output_excerpt"][:80].replace("\n", " ")
                print(f"    excerpt         : {excerpt}")

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

    ext_successes = [r for r in receipts if r.external_success]
    usage_available = [r for r in receipts if r.external_usage_available]
    cost_estimated = [r for r in receipts if r.cost_source == "ESTIMATED"]

    cost_source_counts: dict[str, int] = {}
    for r in receipts:
        cost_source_counts[r.cost_source] = cost_source_counts.get(r.cost_source, 0) + 1

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
    print(f"  Usage available             : {len(usage_available)}")
    print(f"  Cost estimated              : {len(cost_estimated)}")
    print(f"  Non-sovereign               : all (emits_act=False, kernel_mutation=False)")
    print(f"  Secrets redacted            : True")
    print()

    benchmark_id = str(uuid.uuid4())
    output_payload = {
        "benchmark_id": benchmark_id,
        "benchmark": "OIE_EXTERNAL_CLAUDE_V0.2",
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
            "usage_available_count": len(usage_available),
            "cost_estimated_count": len(cost_estimated),
            "cost_source_counts": cost_source_counts,
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
        print("To enable token cost estimation (set prices first):")
        print("  $env:OIE_EXTERNAL_INPUT_COST_PER_1M='3.0'")
        print("  $env:OIE_EXTERNAL_OUTPUT_COST_PER_1M='15.0'")
        print("  $env:OIE_EXTERNAL_COST_ESTIMATE='1'")
        print()


if __name__ == "__main__":
    main()
