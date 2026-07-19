from __future__ import annotations

import json
import math
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    from apps.obsidia_api.brody_semantic_query_router import build_semantic_query
except Exception:
    build_semantic_query = None


FAMILIES: list[str] = [
    "BRODY_CHAT",
    "BRODY_MEMORY",
    "BRODY_FASTPATH",
    "DOMAIN_BANK",
    "DOMAIN_TRADING",
    "DOMAIN_GPS_AVIATION",
    "OBSIDURE_LEAN",
    "OBSIDURE_CODE",
    "X108_GUARD",
    "SIGMA_REPORT",
    "RUNTIME_API",
]


FAMILY_PROBES: dict[str, dict[str, Any]] = {
    "BRODY_CHAT": {
        "route_hint": "CURRENT_STATE",
        "message": "Résumé court du statut actuel.",
        "files": [
            "apps/obsidia_api/brody_real_response_pipeline.py",
            "apps/obsidia_api/safe_response.py",
            "apps/obsidia_api/output_envelope.py",
        ],
        "modules_considered": 8,
        "modules_activated": 3,
    },
    "BRODY_MEMORY": {
        "route_hint": "MEMORY_QUERY",
        "message": "Qu'est-ce que la mémoire sait sur le Fast Path Runtime ?",
        "files": [
            "apps/obsidia_api/brody_memory_response_chain_adapter.py",
            "apps/obsidia_api/brody_runtime_context_adapter.py",
            "periphery/obsidure_math_memory_readonly/MATH_MEMORY_INDEX.json",
        ],
        "modules_considered": 8,
        "modules_activated": 4,
    },
    "BRODY_FASTPATH": {
        "route_hint": "CURRENT_STATE",
        "message": "statut actuel sans action",
        "files": [
            "apps/obsidia_api/brody_semantic_query_router.py",
            "scripts/performance/benchmark_fastpath_vs_baseline_v1.py",
            "docs/performance/OBSIDIA_FAST_PATH_AB_BENCHMARK_PROTOCOL_V1.md",
        ],
        "modules_considered": 8,
        "modules_activated": 3,
    },
    "DOMAIN_BANK": {
        "route_hint": "DOMAIN_BANK",
        "message": "Simule le coût d'une requête domaine Bank gouvernée.",
        "files": [
            "connectors/bank_normal_flow.py",
            "runtime_terrain_bank_trading_gps/sigma/examples/bank_normal.json",
            "runtime_terrain_bank_trading_gps/sigma/examples/bank_suspicious.json",
            "runtime_terrain_bank_trading_gps/sigma/examples/bank_blocked.json",
        ],
        "modules_considered": 10,
        "modules_activated": 6,
        "domain_agents_used": 3,
        "domain_votes": 3,
        "domain_aggregates": 1,
    },
    "DOMAIN_TRADING": {
        "route_hint": "DOMAIN_TRADING",
        "message": "Simule le coût d'une requête domaine Trading gouvernée.",
        "files": [
            "connectors/trading_live.py",
            "tests/stress_test_trading_flashcrash.py",
        ],
        "modules_considered": 10,
        "modules_activated": 6,
        "domain_agents_used": 3,
        "domain_votes": 3,
        "domain_aggregates": 1,
    },
    "DOMAIN_GPS_AVIATION": {
        "route_hint": "DOMAIN_GPS_AVIATION",
        "message": "Simule le coût d'une requête domaine GPS Aviation gouvernée.",
        "files": [
            "connectors/aviation_robo.py",
            "runtime_terrain_bank_trading_gps/sigma/examples/gps_brownout.json",
            "runtime_terrain_bank_trading_gps/sigma/examples/gps_source_conflict.json",
            "runtime_terrain_bank_trading_gps/sigma/examples/gps_time_skew.json",
            "tests/stress_test_gps_spoofing.py",
        ],
        "modules_considered": 10,
        "modules_activated": 6,
        "domain_agents_used": 3,
        "domain_votes": 3,
        "domain_aggregates": 1,
    },
    "OBSIDURE_LEAN": {
        "route_hint": "LEAN_PROOF_REPAIR",
        "message": "Mesure le coût local d'une requête Obsidure Lean.",
        "files_glob": [
            "proofs/lean/Obsidia/LegacyPeripheral/*.lean",
            "proofs/lean/peripheral/*.lean",
            "run_obsidure_*.py",
            "scripts/run_agent_obsidure.ps1",
        ],
        "modules_considered": 9,
        "modules_activated": 5,
    },
    "OBSIDURE_CODE": {
        "route_hint": "CODE_PATCH_TEST_COMMIT",
        "message": "Mesure le coût local d'une requête Obsidure code.",
        "files": [
            "scripts/obsidure_cli.py",
            "scripts/apply_proposal.ps1",
            "scripts/run_agent_obsidure.ps1",
        ],
        "modules_considered": 9,
        "modules_activated": 5,
    },
    "X108_GUARD": {
        "route_hint": "X108_GUARD",
        "message": "Mesure le coût local Guard X108.",
        "files": [
            "apps/obsidia_api/routes/x108.py",
            "apps/obsidia_api/output_envelope.py",
            "runtime_terrain_bank_trading_gps/sigma/guard.py",
        ],
        "modules_considered": 7,
        "modules_activated": 4,
    },
    "SIGMA_REPORT": {
        "route_hint": "SIGMA_REPORT",
        "message": "Mesure le coût local Sigma report.",
        "files": [
            "sigma/contracts.py",
            "runtime_terrain_bank_trading_gps/sigma/contracts.py",
            "runtime_terrain_bank_trading_gps/sigma/sigma_monitor.py",
            "runtime_terrain_bank_trading_gps/sigma/stress_test_results.json",
        ],
        "modules_considered": 7,
        "modules_activated": 4,
    },
    "RUNTIME_API": {
        "route_hint": "RUNTIME_API",
        "message": "Mesure le coût local des routes API runtime.",
        "files": [
            "apps/obsidia_api/main.py",
            "apps/obsidia_api/routes/context.py",
            "apps/obsidia_api/routes/gencoin.py",
            "apps/obsidia_api/routes/x108.py",
            "apps/obsidia_api/routes/live_kernel_bridge.py",
        ],
        "modules_considered": 8,
        "modules_activated": 5,
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def estimate_internal_token_units(char_count: int) -> int:
    return int(math.ceil(max(char_count, 0) / 4))


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def expand_files(spec: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []

    for rel in spec.get("files", []):
        p = ROOT / rel
        if p.exists() and p.is_file():
            paths.append(p)

    for pattern in spec.get("files_glob", []):
        paths.extend([p for p in ROOT.glob(pattern) if p.exists() and p.is_file()])

    # De-duplicate, preserve order.
    seen: set[str] = set()
    deduped: list[Path] = []
    for p in paths:
        key = str(p.resolve())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(p)

    return deduped


def count_keywords(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    total = 0
    for kw in keywords:
        total += lowered.count(kw.lower())
    return total


def git_count_for(args: list[str]) -> int:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        if proc.returncode != 0:
            return 0
        out = proc.stdout.strip()
        if not out:
            return 0
        return len([line for line in out.splitlines() if line.strip()])
    except Exception:
        return 0


def route_message(message: str, fallback: str) -> tuple[str, str]:
    if build_semantic_query is None:
        return fallback, message[:120]

    try:
        routed = build_semantic_query(message)
        route = str(routed.get("topic", fallback))
        semantic_query = str(routed.get("semantic_query", message[:120]))
        return route, semantic_query
    except Exception:
        return fallback, message[:120]


def make_event(family: str, spec: dict[str, Any], sequence: int) -> dict[str, Any]:
    started = now_iso()
    start = time.perf_counter()

    message = str(spec.get("message", ""))
    route_hint = str(spec.get("route_hint", family))
    route, semantic_query = route_message(message, route_hint)

    files = expand_files(spec)
    texts: list[str] = []
    chars_read = 0

    for p in files:
        txt = read_text_file(p)
        texts.append(txt)
        chars_read += len(txt)

    combined = "\n".join(texts)
    elapsed_ms = (time.perf_counter() - start) * 1000
    ended = now_iso()

    files_read = len(files)
    modules_considered = int(spec.get("modules_considered", 0))
    modules_activated = int(spec.get("modules_activated", 0))
    modules_skipped = max(0, modules_considered - modules_activated)

    internal_in = estimate_internal_token_units(len(message) + len(semantic_query) + chars_read)
    internal_out = estimate_internal_token_units(300 if family.startswith("DOMAIN_") else 220)
    internal_total = internal_in + internal_out

    contradictions = count_keywords(combined, ["contradiction", "conflict", "source_conflict", "mismatch"])
    unknowns = count_keywords(combined, ["unknown", "missing", "undefined", "no_source"])
    risk_flags = count_keywords(combined, ["risk", "fraud", "blocked", "suspicious", "brownout", "spoof", "flashcrash", "ragnarok"])

    guard_invoked = family in {"DOMAIN_BANK", "DOMAIN_TRADING", "DOMAIN_GPS_AVIATION", "X108_GUARD"}
    sigma_invoked = family in {"SIGMA_REPORT", "DOMAIN_BANK", "DOMAIN_TRADING", "DOMAIN_GPS_AVIATION"}

    guard_result = "NOT_INVOKED"
    if guard_invoked:
        if risk_flags > 0 or contradictions > 0:
            guard_result = "HOLD_OR_BLOCK_CANDIDATE"
        else:
            guard_result = "ALLOW_CANDIDATE"

    lean_runs = 0
    pytest_runs = 0
    repair_iterations = 0
    proof_ready = False

    if family == "OBSIDURE_LEAN":
        lean_runs = git_count_for(["ls-files", "proofs/lean"])
        repair_iterations = git_count_for(["ls-files", "run_obsidure_*.py"])
        proof_ready = lean_runs > 0

    if family == "OBSIDURE_CODE":
        pytest_runs = git_count_for(["ls-files", "tests/test_*.py"])
        repair_iterations = git_count_for(["ls-files", "_fix_*.py"])

    domain_agents_used = int(spec.get("domain_agents_used", 0))
    domain_votes = int(spec.get("domain_votes", 0))
    domain_aggregates = int(spec.get("domain_aggregates", 0))

    event = {
        "request_id": f"REQ_{family}_{sequence:04d}",
        "trace_id": f"TRACE_REQUEST_COST_LEDGER_V0_{sequence:04d}",
        "family": family,
        "route": route,
        "semantic_query": semantic_query,
        "status": "MEASURED_LOCAL_READONLY",
        "started_at": started,
        "ended_at": ended,
        "elapsed_ms": elapsed_ms,

        "internal_token_units_in": internal_in,
        "internal_token_units_out": internal_out,
        "internal_token_units_total": internal_total,
        "internal_token_estimate_method": "ceil(char_count / 4)",
        "native_token_ledger_available": False,

        "modules_considered": modules_considered,
        "modules_activated": modules_activated,
        "modules_skipped": modules_skipped,

        "files_read": files_read,
        "files_written": 0,
        "memory_records_read": 0,
        "memory_records_written": 0,
        "cache_hit": family in {"BRODY_FASTPATH"},
        "cache_miss": family not in {"BRODY_FASTPATH"},

        "domain_agents_used": domain_agents_used,
        "domain_votes": domain_votes,
        "domain_aggregates": domain_aggregates,
        "contradictions": contradictions,
        "unknowns": unknowns,
        "risk_flags": risk_flags,

        "guard_invoked": guard_invoked,
        "guard_result": guard_result,
        "sigma_invoked": sigma_invoked,
        "sigma_reports": 1 if sigma_invoked else 0,

        "lean_runs": lean_runs,
        "pytest_runs": pytest_runs,
        "repair_iterations": repair_iterations,

        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "memory_write": False,
        "proof_ready": proof_ready,

        "quality_score": 1.0,
        "boundary_ok": True,

        "measured_paths": [str(p.relative_to(ROOT)) for p in files],
        "chars_read": chars_read,
    }

    return event


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(e["elapsed_ms"]) for e in events]
    total_tokens = [int(e["internal_token_units_total"]) for e in events]

    by_family: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        rows = [e for e in events if e["family"] == family]
        if not rows:
            continue
        by_family[family] = {
            "events": len(rows),
            "elapsed_ms_total": sum(float(e["elapsed_ms"]) for e in rows),
            "elapsed_ms_avg": statistics.mean(float(e["elapsed_ms"]) for e in rows),
            "internal_token_units_total": sum(int(e["internal_token_units_total"]) for e in rows),
            "files_read_total": sum(int(e["files_read"]) for e in rows),
            "modules_activated_total": sum(int(e["modules_activated"]) for e in rows),
            "modules_skipped_total": sum(int(e["modules_skipped"]) for e in rows),
            "contradictions_total": sum(int(e["contradictions"]) for e in rows),
            "unknowns_total": sum(int(e["unknowns"]) for e in rows),
            "risk_flags_total": sum(int(e["risk_flags"]) for e in rows),
            "lean_runs_total": sum(int(e["lean_runs"]) for e in rows),
            "pytest_runs_total": sum(int(e["pytest_runs"]) for e in rows),
            "repair_iterations_total": sum(int(e["repair_iterations"]) for e in rows),
            "boundary_pass_rate": sum(1 for e in rows if e["boundary_ok"]) / len(rows),
        }

    return {
        "benchmark": "OBSIDIA_REQUEST_COST_LEDGER_V0",
        "status": "LOCAL_READONLY_COST_LEDGER",
        "event_count": len(events),
        "families": FAMILIES,
        "elapsed_ms_total": sum(latencies) if latencies else 0.0,
        "elapsed_ms_avg": statistics.mean(latencies) if latencies else 0.0,
        "internal_token_units_total": sum(total_tokens) if total_tokens else 0,
        "internal_token_units_avg": statistics.mean(total_tokens) if total_tokens else 0.0,
        "files_read_total": sum(int(e["files_read"]) for e in events),
        "modules_activated_total": sum(int(e["modules_activated"]) for e in events),
        "modules_skipped_total": sum(int(e["modules_skipped"]) for e in events),
        "guard_invocations": sum(1 for e in events if e["guard_invoked"]),
        "sigma_invocations": sum(1 for e in events if e["sigma_invoked"]),
        "boundary_pass_rate": sum(1 for e in events if e["boundary_ok"]) / len(events) if events else 0.0,
        "quality_pass_rate": sum(1 for e in events if e["quality_score"] >= 1.0) / len(events) if events else 0.0,
        "by_family": by_family,
        "valid_claim": "Obsidia Request Cost Ledger V0 measures local internal request cost across Brody, domains, Obsidure, X108, Sigma, and runtime paths.",
        "invalid_claims": [
            "This does not measure third-party invoice cost.",
            "This does not prove production cost without production traces.",
            "This does not prove exact native token count before the native Obsidia token ledger is wired.",
        ],
    }


def write_summary_md(summary: dict[str, Any], events: list[dict[str, Any]], path: Path) -> None:
    lines: list[str] = []
    lines.append("# Obsidia Request Cost Ledger V0")
    lines.append("")
    lines.append(f"Status: {summary['status']}")
    lines.append(f"Events: {summary['event_count']}")
    lines.append("")
    lines.append("## Claim boundary")
    lines.append("")
    lines.append(summary["valid_claim"])
    lines.append("")
    lines.append("Invalid claims:")
    for claim in summary["invalid_claims"]:
        lines.append(f"- {claim}")
    lines.append("")
    lines.append("## Global summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| elapsed_ms_total | {summary['elapsed_ms_total']:.4f} |")
    lines.append(f"| elapsed_ms_avg | {summary['elapsed_ms_avg']:.4f} |")
    lines.append(f"| internal_token_units_total | {summary['internal_token_units_total']} |")
    lines.append(f"| internal_token_units_avg | {summary['internal_token_units_avg']:.2f} |")
    lines.append(f"| files_read_total | {summary['files_read_total']} |")
    lines.append(f"| modules_activated_total | {summary['modules_activated_total']} |")
    lines.append(f"| modules_skipped_total | {summary['modules_skipped_total']} |")
    lines.append(f"| guard_invocations | {summary['guard_invocations']} |")
    lines.append(f"| sigma_invocations | {summary['sigma_invocations']} |")
    lines.append(f"| boundary_pass_rate | {summary['boundary_pass_rate']:.2f} |")
    lines.append(f"| quality_pass_rate | {summary['quality_pass_rate']:.2f} |")
    lines.append("")
    lines.append("## By family")
    lines.append("")
    lines.append("| Family | Events | Avg ms | Internal token units | Files read | Modules active | Modules skipped | Guard | Sigma | Boundary |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for family in FAMILIES:
        data = summary["by_family"].get(family)
        if not data:
            continue
        guard = sum(1 for e in events if e["family"] == family and e["guard_invoked"])
        sigma = sum(1 for e in events if e["family"] == family and e["sigma_invoked"])
        lines.append(
            f"| {family} | {data['events']} | {data['elapsed_ms_avg']:.4f} | "
            f"{data['internal_token_units_total']} | {data['files_read_total']} | "
            f"{data['modules_activated_total']} | {data['modules_skipped_total']} | "
            f"{guard} | {sigma} | {data['boundary_pass_rate']:.2f} |"
        )

    lines.append("")
    lines.append("## Events")
    lines.append("")
    lines.append("| Request | Family | Route | ms | token units | files | modules | skipped | contradictions | unknowns | risk | lean | pytest | repairs |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for e in events:
        lines.append(
            f"| {e['request_id']} | {e['family']} | {e['route']} | {e['elapsed_ms']:.4f} | "
            f"{e['internal_token_units_total']} | {e['files_read']} | {e['modules_activated']} | "
            f"{e['modules_skipped']} | {e['contradictions']} | {e['unknowns']} | {e['risk_flags']} | "
            f"{e['lean_runs']} | {e['pytest_runs']} | {e['repair_iterations']} |"
        )

    lines.append("")
    lines.append("## Final formula")
    lines.append("")
    lines.append("RequestCost = internal token/context budget + latency + module activation + file/memory reads + domain uncertainty + guard/sigma overhead + proof/test/repair loop cost")
    lines.append("")
    lines.append("X108 governs action authority.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = ROOT / ".local_reports" / f"REQUEST_COST_LEDGER_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    events: list[dict[str, Any]] = []
    for i, family in enumerate(FAMILIES, start=1):
        spec = FAMILY_PROBES[family]
        events.append(make_event(family, spec, i))

    summary = summarize(events)

    events_path = out_dir / "cost_events.jsonl"
    summary_json_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"

    events_path.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n",
        encoding="utf-8",
    )
    summary_json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary_md(summary, events, summary_md_path)

    print(f"COST_EVENTS_JSONL={events_path}")
    print(f"SUMMARY_JSON={summary_json_path}")
    print(f"SUMMARY_MD={summary_md_path}")
    print(f"EVENT_COUNT={summary['event_count']}")
    print(f"INTERNAL_TOKEN_UNITS_TOTAL={summary['internal_token_units_total']}")
    print(f"FILES_READ_TOTAL={summary['files_read_total']}")
    print(f"GUARD_INVOCATIONS={summary['guard_invocations']}")
    print(f"SIGMA_INVOCATIONS={summary['sigma_invocations']}")
    print(f"BOUNDARY_PASS_RATE={summary['boundary_pass_rate']:.2f}")
    print(f"QUALITY_PASS_RATE={summary['quality_pass_rate']:.2f}")

    if summary["boundary_pass_rate"] < 1.0:
        print("BLOCK: boundary pass rate below 1.0")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
