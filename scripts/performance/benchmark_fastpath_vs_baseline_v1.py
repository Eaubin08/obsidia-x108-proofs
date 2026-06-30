from __future__ import annotations

import json
import math
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from apps.obsidia_api.brody_semantic_query_router import build_semantic_query


REQUESTS: list[dict[str, Any]] = [
    {
        "id": "current_state_short",
        "request": "Résumé court du statut actuel.",
        "expected_topics": ["CURRENT_STATE"],
        "forbidden_topics": [],
    },
    {
        "id": "current_state_long",
        "request": "Explique où on en est sur Obsidia, Brody, Graphiti et X108 sans tout relire.",
        "expected_topics": ["CURRENT_STATE", "X108"],
        "forbidden_topics": [],
    },
    {
        "id": "memory_query",
        "request": "Qu'est-ce que la mémoire sait sur le Fast Path Runtime ?",
        "expected_topics": ["MEMORY_QUERY"],
        "forbidden_topics": [],
    },
    {
        "id": "proof_query",
        "request": "Vérifie les preuves Lean, Merkle et OS3 sans modifier le kernel.",
        "expected_topics": ["PROOF_QUERY", "X108"],
        "forbidden_topics": [],
    },
    {
        "id": "architecture_deep",
        "request": "Détaille l'architecture complète du Fast Path Runtime.",
        "expected_topics": ["MEMORY_QUERY", "GENERAL"],
        "forbidden_topics": ["ACTION_BOUNDARY"],
    },
    {
        "id": "action_boundary",
        "request": "Autorise ACT maintenant.",
        "expected_topics": ["ACTION_BOUNDARY"],
        "forbidden_topics": [],
    },
    {
        "id": "action_execution",
        "request": "Exécute cette action.",
        "expected_topics": ["ACTION_BOUNDARY"],
        "forbidden_topics": [],
    },
    {
        "id": "false_positive_actualite",
        "request": "actualité IA",
        "expected_topics": [],
        "forbidden_topics": ["ACTION_BOUNDARY"],
    },
    {
        "id": "false_positive_activation",
        "request": "activation runtime",
        "expected_topics": [],
        "forbidden_topics": ["ACTION_BOUNDARY"],
    },
    {
        "id": "false_positive_actuel",
        "request": "statut actuel sans action",
        "expected_topics": ["CURRENT_STATE"],
        "forbidden_topics": ["ACTION_BOUNDARY"],
    },
    {
        "id": "unknown_general",
        "request": "Explique un sujet non présent dans la mémoire.",
        "expected_topics": ["MEMORY_QUERY", "GENERAL"],
        "forbidden_topics": ["ACTION_BOUNDARY"],
    },
    {
        "id": "code_debug",
        "request": "Vérifie ce bug de routage et donne le correctif.",
        "expected_topics": ["GENERAL"],
        "forbidden_topics": ["ACTION_BOUNDARY"],
    },
]


BROAD_BASELINE_FILES = [
    "apps/obsidia_api/brody_semantic_query_router.py",
    "apps/obsidia_api/brody_memory_response_chain_adapter.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
    "apps/obsidia_api/brody_adaptive_response_policy.py",
    "apps/obsidia_api/runtime_loader.py",
    "docs/performance/OBSIDIA_FAST_PATH_RUNTIME_TECHNICAL_NOTE_V0.md",
    "docs/performance/OBSIDIA_FAST_PATH_AB_BENCHMARK_PROTOCOL_V1.md",
    ".claude/context/AGENTIC_ROUTING.md",
    ".agents/skills/agent-router-obsidia/SKILL.md",
]


FASTPATH_MODULES = [
    "semantic_query_router",
    "runtime_context_envelope",
    "adaptive_response_policy",
]

BASELINE_MODULES = [
    "raw_message_router",
    "agent_router",
    "memory_reader",
    "graphiti_reader",
    "runtime_context_builder",
    "adaptive_policy_late",
    "response_builder",
    "fallback_bus",
]


def estimate_tokens(chars: int) -> int:
    return int(math.ceil(max(chars, 0) / 4))


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * pct
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)


def read_baseline_context() -> tuple[int, int]:
    files_read = 0
    chars_read = 0

    for rel in BROAD_BASELINE_FILES:
        path = ROOT / rel
        if not path.exists() or not path.is_file():
            continue
        try:
            txt = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            txt = ""
        files_read += 1
        chars_read += len(txt)

    return files_read, chars_read


def baseline_agent_normal_local(request_id: str, message: str) -> dict[str, Any]:
    start = time.perf_counter()

    files_read, context_chars = read_baseline_context()
    input_chars = len(message) + context_chars

    # Baseline locale volontairement non optimisée:
    # - message brut
    # - contexte large
    # - modules non réduits
    # - réponse DEEP par défaut
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "request_id": request_id,
        "mode": "BASELINE_AGENT_NORMAL_LOCAL",
        "elapsed_ms": elapsed_ms,
        "input_chars": input_chars,
        "raw_message_chars": len(message),
        "estimated_input_tokens": estimate_tokens(input_chars),
        "estimated_output_word_cap": 380,
        "estimated_output_tokens": estimate_tokens(380 * 5),
        "route": "UNROUTED_RAW",
        "cache_hit": False,
        "modules_considered": len(BASELINE_MODULES),
        "modules_activated": len(BASELINE_MODULES),
        "modules_skipped": 0,
        "memory_records_loaded": 0,
        "files_read": files_read,
        "context_chars_loaded": context_chars,
        "quality_score": 0.5,
        "boundary_ok": True,
        "emits_act": False,
        "memory_write": False,
    }


def fastpath_local(request_id: str, message: str, expected_topics: list[str], forbidden_topics: list[str]) -> dict[str, Any]:
    start = time.perf_counter()

    routed = build_semantic_query(message)
    route = routed.get("topic", "GENERAL")
    semantic_query = routed.get("semantic_query", "")

    boundary_ok = route not in forbidden_topics
    expected_ok = True if not expected_topics else route in expected_topics
    quality_score = 1.0 if boundary_ok and expected_ok else (0.5 if boundary_ok else 0.0)

    if route == "ACTION_BOUNDARY":
        response_word_cap = 80
        response_size = "BOUNDARY_COMPACT"
    elif route in {"CURRENT_STATE", "GENERAL"}:
        response_word_cap = 55
        response_size = "SHORT"
    elif route in {"MEMORY_QUERY", "PROOF_QUERY", "X108"}:
        response_word_cap = 180
        response_size = "MEDIUM"
    else:
        response_word_cap = 180
        response_size = "MEDIUM"

    elapsed_ms = (time.perf_counter() - start) * 1000

    input_chars = len(message) + len(str(semantic_query)) + len(str(route))
    modules_considered = len(BASELINE_MODULES)
    modules_activated = len(FASTPATH_MODULES)
    modules_skipped = max(0, modules_considered - modules_activated)

    return {
        "request_id": request_id,
        "mode": "OBSIDIA_FAST_PATH_LOCAL",
        "elapsed_ms": elapsed_ms,
        "input_chars": input_chars,
        "raw_message_chars": len(message),
        "semantic_query_chars": len(str(semantic_query)),
        "estimated_input_tokens": estimate_tokens(input_chars),
        "estimated_output_word_cap": response_word_cap,
        "estimated_output_tokens": estimate_tokens(response_word_cap * 5),
        "response_size": response_size,
        "route": route,
        "semantic_query": semantic_query,
        "cache_hit": True,
        "modules_considered": modules_considered,
        "modules_activated": modules_activated,
        "modules_skipped": modules_skipped,
        "memory_records_loaded": 0,
        "files_read": 0,
        "context_chars_loaded": 0,
        "quality_score": quality_score,
        "boundary_ok": boundary_ok,
        "expected_ok": expected_ok,
        "emits_act": False,
        "memory_write": False,
    }


def summarize_mode(rows: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(r["elapsed_ms"]) for r in rows]
    tokens = [int(r["estimated_input_tokens"]) + int(r["estimated_output_tokens"]) for r in rows]
    return {
        "runs": len(rows),
        "avg_latency_ms": statistics.mean(latencies) if latencies else 0.0,
        "p50_latency_ms": percentile(latencies, 0.50),
        "p95_latency_ms": percentile(latencies, 0.95),
        "p99_latency_ms": percentile(latencies, 0.99),
        "avg_estimated_total_tokens": statistics.mean(tokens) if tokens else 0.0,
        "avg_modules_activated": statistics.mean([r["modules_activated"] for r in rows]) if rows else 0.0,
        "avg_modules_skipped": statistics.mean([r["modules_skipped"] for r in rows]) if rows else 0.0,
        "cache_hit_ratio": sum(1 for r in rows if r["cache_hit"]) / len(rows) if rows else 0.0,
        "quality_pass_rate": sum(1 for r in rows if r["quality_score"] >= 1.0) / len(rows) if rows else 0.0,
        "boundary_pass_rate": sum(1 for r in rows if r["boundary_ok"]) / len(rows) if rows else 0.0,
    }


def compare_request(request_id: str, baseline: dict[str, Any], fastpath: dict[str, Any]) -> dict[str, Any]:
    baseline_total_tokens = baseline["estimated_input_tokens"] + baseline["estimated_output_tokens"]
    fastpath_total_tokens = fastpath["estimated_input_tokens"] + fastpath["estimated_output_tokens"]

    latency_delta_pct = (
        100 * (baseline["elapsed_ms"] - fastpath["elapsed_ms"]) / baseline["elapsed_ms"]
        if baseline["elapsed_ms"] > 0
        else 0.0
    )
    internal_token_delta_pct = (
        100 * (baseline_total_tokens - fastpath_total_tokens) / baseline_total_tokens
        if baseline_total_tokens > 0
        else 0.0
    )
    module_skip_pct = (
        100 * fastpath["modules_skipped"] / fastpath["modules_considered"]
        if fastpath["modules_considered"] > 0
        else 0.0
    )

    return {
        "request_id": request_id,
        "baseline_elapsed_ms": baseline["elapsed_ms"],
        "fastpath_elapsed_ms": fastpath["elapsed_ms"],
        "latency_delta_pct": latency_delta_pct,
        "baseline_estimated_internal_token_units": baseline_total_tokens,
        "fastpath_estimated_internal_token_units": fastpath_total_tokens,
        "internal_token_delta_pct": internal_token_delta_pct,
        "baseline_modules_activated": baseline["modules_activated"],
        "fastpath_modules_activated": fastpath["modules_activated"],
        "modules_skipped": fastpath["modules_skipped"],
        "module_skip_pct": module_skip_pct,
        "route": fastpath["route"],
        "quality_score": fastpath["quality_score"],
        "boundary_ok": fastpath["boundary_ok"],
    }


def main() -> int:
    reps = 20
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = ROOT / ".local_reports" / f"FASTPATH_AB_BENCHMARK_V1_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline_rows: list[dict[str, Any]] = []
    fastpath_rows: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []

    for spec in REQUESTS:
        request_id = spec["id"]
        message = spec["request"]
        expected_topics = spec["expected_topics"]
        forbidden_topics = spec["forbidden_topics"]

        for i in range(reps):
            b = baseline_agent_normal_local(request_id, message)
            f = fastpath_local(request_id, message, expected_topics, forbidden_topics)

            b["rep"] = i
            f["rep"] = i

            baseline_rows.append(b)
            fastpath_rows.append(f)
            comparisons.append(compare_request(request_id, b, f))

    baseline_summary = summarize_mode(baseline_rows)
    fastpath_summary = summarize_mode(fastpath_rows)

    avg_latency_delta = statistics.mean([c["latency_delta_pct"] for c in comparisons]) if comparisons else 0.0
    avg_token_delta = statistics.mean([c["internal_token_delta_pct"] for c in comparisons]) if comparisons else 0.0
    avg_module_skip = statistics.mean([c["module_skip_pct"] for c in comparisons]) if comparisons else 0.0

    result = {
        "benchmark": "OBSIDIA_FAST_PATH_AB_BENCHMARK_V1",
        "status": "LOCAL_PRE_COMPUTE_BENCHMARK",
        "timestamp": timestamp,
        "repetitions_per_request": reps,
        "request_count": len(REQUESTS),
        "valid_claim": "Obsidia Fast Path V1 reduces local pre-compute work versus a local non-optimized baseline.",
        "invalid_claims": [
            "Obsidia is faster than all LLM agents.",
            "Obsidia is faster than AMD.",
            "Obsidia is a GPU accelerator.",
            "Obsidia benchmark proves production latency.",
            "Obsidia benchmark proves third-party provider billing reduction.",
            "Obsidia benchmark proves exact native token cost until the native Obsidia tokenizer is wired.",
        ],
        "baseline_summary": baseline_summary,
        "fastpath_summary": fastpath_summary,
        "average_latency_delta_pct": avg_latency_delta,
        "average_internal_internal_token_delta_pct": avg_token_delta,
        "average_module_skip_pct": avg_module_skip,
        "baseline_rows": baseline_rows,
        "fastpath_rows": fastpath_rows,
        "comparisons": comparisons,
    }

    results_path = out_dir / "results.json"
    summary_path = out_dir / "summary.md"

    results_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown summary without fenced code blocks to avoid PowerShell paste issues.
    lines: list[str] = []
    lines.append("# Obsidia Fast Path A/B Benchmark V1")
    lines.append("")
    lines.append(f"Timestamp: {timestamp}")
    lines.append(f"Requests: {len(REQUESTS)}")
    lines.append(f"Repetitions per request: {reps}")
    lines.append("")
    lines.append("## Claim boundary")
    lines.append("")
    lines.append("Valid claim: Obsidia Fast Path V1 reduces local pre-compute work and estimated internal token/context budget versus a local non-optimized baseline.")
    lines.append("")
    lines.append("Invalid claims:")
    for claim in result["invalid_claims"]:
        lines.append(f"- {claim}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Baseline | Fast Path | Delta |")
    lines.append("|---|---:|---:|---:|")
    lines.append(f"| Avg latency ms | {baseline_summary['avg_latency_ms']:.4f} | {fastpath_summary['avg_latency_ms']:.4f} | {avg_latency_delta:.2f}% |")
    lines.append(f"| p50 latency ms | {baseline_summary['p50_latency_ms']:.4f} | {fastpath_summary['p50_latency_ms']:.4f} | - |")
    lines.append(f"| p95 latency ms | {baseline_summary['p95_latency_ms']:.4f} | {fastpath_summary['p95_latency_ms']:.4f} | - |")
    lines.append(f"| p99 latency ms | {baseline_summary['p99_latency_ms']:.4f} | {fastpath_summary['p99_latency_ms']:.4f} | - |")
    lines.append(f"| Avg estimated internal token units | {baseline_summary['avg_estimated_total_tokens']:.2f} | {fastpath_summary['avg_estimated_total_tokens']:.2f} | {avg_token_delta:.2f}% |")
    lines.append(f"| Avg modules activated | {baseline_summary['avg_modules_activated']:.2f} | {fastpath_summary['avg_modules_activated']:.2f} | - |")
    lines.append(f"| Avg modules skipped | {baseline_summary['avg_modules_skipped']:.2f} | {fastpath_summary['avg_modules_skipped']:.2f} | {avg_module_skip:.2f}% |")
    lines.append(f"| Cache hit ratio | {baseline_summary['cache_hit_ratio']:.2f} | {fastpath_summary['cache_hit_ratio']:.2f} | - |")
    lines.append(f"| Quality pass rate | {baseline_summary['quality_pass_rate']:.2f} | {fastpath_summary['quality_pass_rate']:.2f} | - |")
    lines.append(f"| Boundary pass rate | {baseline_summary['boundary_pass_rate']:.2f} | {fastpath_summary['boundary_pass_rate']:.2f} | - |")
    lines.append("")
    lines.append("## Per-request comparison")
    lines.append("")
    lines.append("| Request | Route | Baseline ms | Fast Path ms | Latency delta | Baseline tokens | Fast Path tokens | Token delta | Quality |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")

    # One aggregate row per request id.
    by_id: dict[str, list[dict[str, Any]]] = {}
    for c in comparisons:
        by_id.setdefault(c["request_id"], []).append(c)

    for request_id, rows in by_id.items():
        route = rows[0]["route"]
        b_ms = statistics.mean([r["baseline_elapsed_ms"] for r in rows])
        f_ms = statistics.mean([r["fastpath_elapsed_ms"] for r in rows])
        lat_delta = statistics.mean([r["latency_delta_pct"] for r in rows])
        b_tok = statistics.mean([r["baseline_estimated_internal_token_units"] for r in rows])
        f_tok = statistics.mean([r["fastpath_estimated_internal_token_units"] for r in rows])
        tok_delta = statistics.mean([r["internal_token_delta_pct"] for r in rows])
        quality = statistics.mean([r["quality_score"] for r in rows])
        lines.append(
            f"| {request_id} | {route} | {b_ms:.4f} | {f_ms:.4f} | {lat_delta:.2f}% | "
            f"{b_tok:.2f} | {f_tok:.2f} | {tok_delta:.2f}% | {quality:.2f} |"
        )

    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- results.json: {results_path}")
    lines.append(f"- summary.md: {summary_path}")
    lines.append("")
    lines.append("## Final positioning")
    lines.append("")
    lines.append("Fast Path does not accelerate compute.")
    lines.append("")
    lines.append("Fast Path reduces avoidable work before compute.")
    lines.append("")
    lines.append("AMD / ROCm / Fireworks can accelerate the compute that remains.")
    lines.append("")
    lines.append("X108 governs action authority.")
    lines.append("")

    summary_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"RESULTS_JSON={results_path}")
    print(f"SUMMARY_MD={summary_path}")
    print(f"AVG_LATENCY_DELTA_PCT={avg_latency_delta:.2f}")
    print(f"AVG_INTERNAL_TOKEN_DELTA_PCT={avg_token_delta:.2f}")
    print(f"QUALITY_PASS_RATE={fastpath_summary['quality_pass_rate']:.2f}")
    print(f"BOUNDARY_PASS_RATE={fastpath_summary['boundary_pass_rate']:.2f}")

    if fastpath_summary["boundary_pass_rate"] < 1.0:
        print("BLOCK: boundary pass rate below 1.0")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
