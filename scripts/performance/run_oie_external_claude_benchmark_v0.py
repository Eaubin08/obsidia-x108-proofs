#!/usr/bin/env python3
"""OIE External Benchmark Harness V0 -- Compare Obsidia vs Claude CLI.

Mode par defaut : DRY_RUN (aucun appel reseau).
Mode reel      : set OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1
Mode complet   : set OIE_EXTERNAL_BENCHMARK_FULL=1 (toutes taches)

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

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.inference_economy.external_comparison import (
    ExternalComparisonReceipt,
    detect_claude_cli,
    run_claude_cli,
    compute_comparison,
    evaluate_route_quality,
    EXCERPT_MAX_CHARS,
    ERROR_USAGE_ONLY,
)

# ── Task portfolio ────────────────────────────────────────────────────────────
# expected_route : label Obsidia canonique pour cette tache
# expected_output_hint : format attendu de la sortie externe
# smoke : True = inclus dans le run minimal

TASKS = [
    {
        "task_id": "fastpath_route_selection_smoke",
        "task_family": "fast_path_vs_llm_simple",
        # Prompt non-ambigu : ping health check -> route triviale
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
        "smoke": True,
    },
    {
        "task_id": "brody_conversational_smoke",
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
        "smoke": False,
    },
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
        "expected_route": "BANK",
        "expected_output_hint": "one of: ALLOW HOLD BLOCK",
        "smoke": False,
    },
    {
        "task_id": "trading_signal_smoke",
        "task_family": "trading_vs_domain_llm",
        "task_prompt": (
            "A BUY signal arrives for asset X with confidence 0.87 and "
            "no contradicting signals. Output: VALID or HOLD_RISK."
        ),
        "obsidia_route": "trading_connector",
        "obsidia_expected_output_type": "VALID_HOLD_RISK",
        "obsidia_cost_eur_per_1m": 0.84,
        "obsidia_latency_ms": 18.0,
        "expected_route": "TRADING",
        "expected_output_hint": "one of: VALID HOLD_RISK",
        "smoke": False,
    },
    {
        "task_id": "gps_terrain_smoke",
        "task_family": "gps_aviation_vs_domain_llm",
        "task_prompt": (
            "Terrain signal: altitude 950m, obstacle clearance 120m, route R47. "
            "Is the route admissible? Output: ALLOW or BLOCK."
        ),
        "obsidia_route": "aviation_connector",
        "obsidia_expected_output_type": "ALLOW_BLOCK",
        "obsidia_cost_eur_per_1m": 0.91,
        "obsidia_latency_ms": 9.5,
        "expected_route": "GPS",
        "expected_output_hint": "one of: ALLOW BLOCK",
        "smoke": False,
    },
    {
        "task_id": "obsidure_patch_smoke",
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
        "smoke": False,
    },
    {
        # expected_route=OBSIDURE : verification d'invariant formel -> kernel task
        "task_id": "lean_invariant_smoke",
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
        "smoke": False,
    },
]


# ── Build helpers ─────────────────────────────────────────────────────────────

def build_dry_run_receipt(task: dict, claude_available: bool, claude_cmd: str) -> ExternalComparisonReceipt:
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
        expected_route=task.get("expected_route", ""),
        external_detected_route=None,
        route_match=None,
        expected_output_hint=task.get("expected_output_hint", ""),
        quality_score=None,
        quality_notes="DRY_RUN",
        classification_error_type=ERROR_USAGE_ONLY,
        savings_ratio_vs_external=None,
        avoided_cost_eur_per_1m=None,
    )


def build_real_receipt(
    task: dict,
    claude_available: bool,
    claude_cmd: str,
    run_result: dict,
) -> ExternalComparisonReceipt:
    ratio, avoided, cost_src = compute_comparison(
        task["obsidia_cost_eur_per_1m"],
        None,  # CLI does not expose token usage in stdout
    )
    quality = evaluate_route_quality(
        expected_route=task.get("expected_route", ""),
        external_output=run_result.get("output_excerpt", ""),
        external_success=run_result.get("success", False),
    )
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
        external_success=run_result.get("success", False),
        external_error=run_result.get("error", ""),
        external_output_excerpt=run_result.get("output_excerpt", ""),
        external_usage_available=False,
        cost_source=cost_src,
        expected_route=task.get("expected_route", ""),
        external_detected_route=quality["external_detected_route"],
        route_match=quality["route_match"],
        expected_output_hint=task.get("expected_output_hint", ""),
        quality_score=quality["quality_score"],
        quality_notes=quality["quality_notes"],
        classification_error_type=quality["classification_error_type"],
        savings_ratio_vs_external=ratio,
        avoided_cost_eur_per_1m=avoided,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    network_allowed = os.environ.get("OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK", "0") == "1"
    full_run = os.environ.get("OIE_EXTERNAL_BENCHMARK_FULL", "0") == "1"
    mode = "REAL" if network_allowed else "DRY_RUN"

    claude_available, claude_cmd, claude_info = detect_claude_cli()

    print("\n=== OIE External Benchmark Harness V0 ===\n")
    print(f"  Mode              : {mode}")
    print(f"  Network allowed   : {network_allowed}")
    print(f"  Claude detected   : {claude_available}")
    if claude_available:
        print(f"  Claude command    : {claude_cmd}")
        print(f"  Claude info       : {claude_info[:80]}")
    print(f"  Full run          : {full_run}")
    print()

    tasks_to_run = TASKS if full_run else [t for t in TASKS if t.get("smoke", False)]
    print(f"  Tasks selected    : {len(tasks_to_run)} / {len(TASKS)}")
    print()

    receipts = []

    for task in tasks_to_run:
        print(f"  [{task['task_family']}] {task['task_id']}")
        print(f"    expected_route  : {task.get('expected_route', 'N/A')}")

        if not network_allowed:
            receipt = build_dry_run_receipt(task, claude_available, claude_cmd)
            print(f"    -> DRY_RUN | network=False | obsidia={task['obsidia_cost_eur_per_1m']} EUR/1M")
        elif not claude_available:
            receipt = ExternalComparisonReceipt(
                task_id=task["task_id"],
                task_family=task["task_family"],
                external_available=False,
                external_network_allowed=True,
                external_success=False,
                external_error="CLAUDE_NOT_AVAILABLE",
                expected_route=task.get("expected_route", ""),
                classification_error_type=ERROR_USAGE_ONLY,
            )
            print(f"    -> SKIPPED | Claude not available")
        else:
            print(f"    -> RUNNING claude -p ...")
            run_result = run_claude_cli(task["task_prompt"])
            receipt = build_real_receipt(task, claude_available, claude_cmd, run_result)
            status = "OK" if run_result["success"] else f"FAIL({run_result['error']})"
            print(f"    -> {status} | latency={run_result['latency_ms']:.0f}ms | usage=unavailable")
            print(f"    detected_route  : {receipt.external_detected_route}")
            print(f"    route_match     : {receipt.route_match}")
            print(f"    quality_score   : {receipt.quality_score}")
            print(f"    error_type      : {receipt.classification_error_type}")
            if run_result.get("output_excerpt"):
                excerpt = run_result["output_excerpt"][:80].replace("\n", " ")
                print(f"    excerpt         : {excerpt}")

        receipts.append(receipt)
        print()

    # Summary
    quality_with_score = [r for r in receipts if r.quality_score is not None]
    route_matches = [r for r in receipts if r.route_match is True]
    route_mismatches = [r for r in receipts if r.route_match is False]
    ext_successes = [r for r in receipts if r.external_success]
    usage_available = [r for r in receipts if r.external_usage_available]
    avg_q = (
        sum(r.quality_score for r in quality_with_score) / len(quality_with_score)
        if quality_with_score else None
    )

    print("--- Receipts summary ---")
    print(f"  Total receipts         : {len(receipts)}")
    print(f"  External success       : {len(ext_successes)}")
    print(f"  Route match            : {len(route_matches)}")
    print(f"  Route mismatch         : {len(route_mismatches)}")
    print(f"  Avg quality score      : {f'{avg_q:.2f}' if avg_q is not None else 'N/A'}")
    print(f"  Usage available        : {len(usage_available)}")
    print(f"  Non-sovereign          : all (emits_act=False, kernel_mutation=False)")
    print(f"  Secrets redacted       : True")
    print()

    benchmark_id = str(uuid.uuid4())
    output = {
        "benchmark_id": benchmark_id,
        "benchmark": "OIE_EXTERNAL_CLAUDE_V0",
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "network_allowed": network_allowed,
        "claude_detected": claude_available,
        "claude_command": claude_cmd,
        "tasks_run": len(receipts),
        "full_run": full_run,
        "summary": {
            "tasks_attempted": len(receipts),
            "external_success_count": len(ext_successes),
            "quality_available_count": len(quality_with_score),
            "route_match_count": len(route_matches),
            "route_mismatch_count": len(route_mismatches),
            "avg_quality_score": round(avg_q, 4) if avg_q is not None else None,
            "usage_available_count": len(usage_available),
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
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Receipts JSON -> {out_path}")
    print()
    print("Governance: readonly=True | emits_act=False | kernel_mutation=False | secrets_redacted=True")
    print()
    if not network_allowed:
        print("To enable real Claude calls:")
        print("  PowerShell : $env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK='1'")
        print("  Bash       : export OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1")
        print("  Then       : python scripts/performance/run_oie_external_claude_benchmark_v0.py")
        print()
        print("To run all task families (not just smoke):")
        print("  PowerShell : $env:OIE_EXTERNAL_BENCHMARK_FULL='1'")
        print()


if __name__ == "__main__":
    main()
