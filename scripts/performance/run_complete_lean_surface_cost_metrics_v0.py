from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

# OBSIDIA_HARD_EXCLUDE_PATCH_V1
HARD_EXCLUDED_LEAN_PATH_PARTS = (
    "_BACKUP_ORIGINALS_",
    "_EPHEMERAL_CODE_SANDBOX_",
    "ci_recheck_optional_publication",
    ".lake",
    ".git",
    "__pycache__",
)

def obsidia_is_hard_excluded_lean_path(path: Path) -> bool:
    raw = str(path).replace("\\", "/")
    try:
        rel_raw = str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        rel_raw = raw
    return any(part in raw or part in rel_raw for part in HARD_EXCLUDED_LEAN_PATH_PARTS)

sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from apps.obsidia_api.request_cost_event_writer import build_cost_event, now_iso, write_cost_event


RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DIR = ROOT / ".local_reports" / f"OBSIDURE_COMPLETE_LEAN_SURFACE_COST_METRICS_{RUN_ID}"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST = ROOT / "proofs" / "LEAN_PROOF_SURFACE_MANIFEST.json"

EXCLUDED_PARTS = {
    ".git",
    ".lake",
    "lake-packages",
    "node_modules",
    ".local_reports",
    ".local_audits",
    ".local_exports",
    ".local_freezes",
    ".local_test_runs",
    ".runtime_freezes",
    "_PATCH_PROPOSALS",
}

EXCLUDED_PREFIXES = (
    "_EPHEMERAL_CODE_SANDBOX_",
    "LOCAL_AUDIT_",
    "AUDIT_",
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def is_excluded(path: Path) -> bool:
    try:
        r = path.relative_to(ROOT)
    except ValueError:
        return True

    parts = set(r.parts)
    if parts & EXCLUDED_PARTS:
        return True

    for part in r.parts:
        if part.startswith(EXCLUDED_PREFIXES):
            return True

    return False


def add_candidate(candidates: dict[str, Path], source_map: dict[str, set[str]], path: Path, source: str) -> None:
    # OBSIDIA_ADD_CANDIDATE_HARD_EXCLUDE_V1
    if obsidia_is_hard_excluded_lean_path(p):
        return
    try:
        p = path.resolve()
    except Exception:
        return

    if not p.exists() or not p.is_file() or p.suffix.lower() != ".lean":
        return

    if is_excluded(p):
        return

    try:
        key = rel(p)
    except Exception:
        return

    candidates[key] = p
    source_map.setdefault(key, set()).add(source)


def git_files(args: list[str]) -> list[Path]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    except Exception:
        return []

    if proc.returncode != 0:
        return []

    out: list[Path] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.endswith(".lean"):
            out.append(ROOT / line)
    return out


def collect_manifest_lean_paths(value: Any) -> list[str]:
    out: list[str] = []

    if isinstance(value, str):
        if value.endswith(".lean") or ".lean" in value:
            out.append(value)
        return out

    if isinstance(value, list):
        for item in value:
            out.extend(collect_manifest_lean_paths(item))
        return out

    if isinstance(value, dict):
        for item in value.values():
            out.extend(collect_manifest_lean_paths(item))
        return out

    return out


def manifest_files() -> list[Path]:
    if not MANIFEST.exists():
        return []

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []

    paths = collect_manifest_lean_paths(data)
    out: list[Path] = []
    for raw in paths:
        clean = raw.replace("\\", "/").strip()

        # If the string contains a larger message around the path, keep the likely suffix around proofs/ or src/.
        for marker in ["proofs/", "src/", "Obsidia/"]:
            if marker in clean:
                clean = clean[clean.index(marker):]
                break

        clean = clean.strip("`'\" ")
        if clean.endswith(".lean"):
            out.append(ROOT / clean)

    return out


def discover_complete_lean_surface() -> tuple[list[Path], dict[str, set[str]]]:
    candidates: dict[str, Path] = {}
    source_map: dict[str, set[str]] = {}

    # 1. Explicit manifest surface.
    for p in manifest_files():
        add_candidate(candidates, source_map, p, "manifest")

    # 2. Git tracked Lean files.
    for p in git_files(["ls-files", "*.lean"]):
        add_candidate(candidates, source_map, p, "git_tracked")

    # 3. Git untracked Lean files.
    for p in git_files(["ls-files", "--others", "--exclude-standard", "*.lean"]):
        add_candidate(candidates, source_map, p, "git_untracked")

    # 4. Explicit proof surfaces.
    for pattern in [
        "proofs/lean/**/*.lean",
        "proofs/**/*.lean",
        "src/**/*.lean",
        "Obsidia/**/*.lean",
        "*.lean",
    ]:
        for p in ROOT.glob(pattern):
            add_candidate(candidates, source_map, p, f"glob:{pattern}")

    # 5. Repo scan fallback, filtered.
    for p in ROOT.rglob("*.lean"):
        add_candidate(candidates, source_map, p, "repo_scan")

    ordered = [candidates[k] for k in sorted(candidates)]
    return ordered, source_map


def classify(path: Path) -> dict[str, str]:
    r = rel(path)
    parts = r.split("/")
    low = r.lower()

    if "LegacyPeripheral" in parts:
        group = "LEGACY_PERIPHERAL_27"
    elif "Peripheral" in parts:
        group = "PERIPHERAL_15"
    elif "peripheral" in parts:
        group = "LOWERCASE_PERIPHERAL_OR_V3"
    elif (
        "base" in low
        or "l1" in low
        or "core" in low
        or "kernel" in low
        or "canonical" in low
        or "proofs/lean/" in low
    ):
        group = "BASE57_ORIGINAL_OR_CORE"
    else:
        group = "OTHER_LEAN"

    return {
        "path": r,
        "group": group,
        "name": path.name,
    }


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    idx = int(round((len(ordered) - 1) * pct))
    return float(ordered[max(0, min(idx, len(ordered) - 1))])


def run_lean(path: Path, source_map: dict[str, set[str]], timeout_sec: float = 300.0) -> dict[str, Any]:
    info = classify(path)
    path_rel = rel(path)
    command = ["lake", "env", "lean", path_rel]

    started = now_iso()
    start = time.perf_counter()

    timed_out = False
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
        )
        exit_code = proc.returncode
        stdout_text = proc.stdout or ""
        stderr_text = proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout_text = exc.stdout or ""
        stderr_text = exc.stderr or ""
        if isinstance(stdout_text, bytes):
            stdout_text = stdout_text.decode("utf-8", errors="replace")
        if isinstance(stderr_text, bytes):
            stderr_text = stderr_text.decode("utf-8", errors="replace")
        stderr_text += f"\nTIMEOUT_AFTER_SECONDS={timeout_sec}\n"

    elapsed_ms = (time.perf_counter() - start) * 1000
    ended = now_iso()

    status = "TIMEOUT" if timed_out else ("PASS" if exit_code == 0 else "FAIL")
    combined = "\n".join([" ".join(command), stdout_text, stderr_text]).lower()

    event = build_cost_event(
        family="OBSIDURE_LEAN",
        route=f"COMPLETE_LEAN::{path_rel}",
        status=status,
        started_at=started,
        ended_at=ended,
        elapsed_ms=elapsed_ms,
        command=command,
        request_text=f"obsidure_complete_lean_surface::{path_rel}",
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        exit_code=exit_code,
        modules_considered=9,
        modules_activated=5,
        modules_skipped=4,
        files_read=1,
        files_written=0,
        memory_records_read=0,
        memory_records_written=0,
        cache_hit=False,
        cache_miss=True,
        domain_agents_used=0,
        domain_votes=0,
        domain_aggregates=0,
        contradictions=combined.count("contradiction") + combined.count("conflict"),
        unknowns=combined.count("unknown") + combined.count("missing") + combined.count("undefined"),
        risk_flags=combined.count("risk") + combined.count("blocked") + combined.count("fail") + combined.count("error"),
        guard_invoked=False,
        guard_result="NOT_INVOKED",
        sigma_invoked=False,
        sigma_reports=0,
        lean_runs=1,
        pytest_runs=0,
        repair_iterations=0,
        proof_ready=exit_code == 0,
        quality_score=1.0 if exit_code == 0 else 0.0,
        boundary_ok=True,
        extra={
            "runner": "run_complete_lean_surface_cost_metrics_v0",
            "case_id": f"complete_lean::{path_rel}",
            "lean_group": info["group"],
            "sources": sorted(source_map.get(path_rel, set())),
            "timeout_sec": timeout_sec,
            "required": True,
        },
    )
    write_cost_event(event)

    return {
        "path": path_rel,
        "name": info["name"],
        "group": info["group"],
        "sources": sorted(source_map.get(path_rel, set())),
        "status": status,
        "exit_code": exit_code,
        "elapsed_ms": elapsed_ms,
        "internal_token_units_total": int(event["internal_token_units_total"]),
        "stdout_chars": len(stdout_text),
        "stderr_chars": len(stderr_text),
        "stdout_preview": stdout_text[:1200],
        "stderr_preview": stderr_text[:2400],
        "route": event["route"],
    }



OBSIDIA_METRICS_HELP_GUARD_V1 = """Usage: python scripts/performance/run_complete_lean_surface_cost_metrics_v0.py [--help]

Obsidure complete Lean surface cost metrics.

Discovers current Lean surface material and excludes backups/ephemeral/generated local cache paths.

Safety:
- no network call
- no kernel mutation
- no X108 mutation
- no ACT emission
- writes only local metric reports
"""

def main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(OBSIDIA_METRICS_HELP_GUARD_V1)
        return 0

    lean_files, source_map = discover_complete_lean_surface()

    print(f"COMPLETE_LEAN_DISCOVERED={len(lean_files)}")
    print(f"MANIFEST_PRESENT={MANIFEST.exists()}")

    group_preview: dict[str, int] = {}
    for p in lean_files:
        g = classify(p)["group"]
        group_preview[g] = group_preview.get(g, 0) + 1

    for group, count in sorted(group_preview.items()):
        print(f"DISCOVERED_GROUP={group} COUNT={count}")

    for p in lean_files:
        print(f"LEAN_TARGET={rel(p)} SOURCES={','.join(sorted(source_map.get(rel(p), set())))}")

    if not lean_files:
        print("BLOCK: no Lean files discovered")
        return 1

    results: list[dict[str, Any]] = []

    for i, path in enumerate(lean_files, start=1):
        print("")
        print(f"=== COMPLETE LEAN {i}/{len(lean_files)} :: {rel(path)} ===")
        result = run_lean(path, source_map=source_map)
        results.append(result)
        print(
            f"{result['status']} ms={result['elapsed_ms']:.2f} "
            f"units={result['internal_token_units_total']} "
            f"group={result['group']}"
        )
        if result["status"] != "PASS":
            print("STDERR_PREVIEW:")
            print(result["stderr_preview"])

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    timeout_count = sum(1 for r in results if r["status"] == "TIMEOUT")

    elapsed_values = [float(r["elapsed_ms"]) for r in results]
    token_values = [int(r["internal_token_units_total"]) for r in results]

    by_group: dict[str, dict[str, Any]] = {}
    by_source: dict[str, dict[str, Any]] = {}

    for r in results:
        for bucket_map, keys in [
            (by_group, [r["group"]]),
            (by_source, r["sources"] or ["unknown_source"]),
        ]:
            for key in keys:
                bucket = bucket_map.setdefault(
                    key,
                    {
                        "total": 0,
                        "pass": 0,
                        "fail": 0,
                        "timeout": 0,
                        "elapsed_ms_total": 0.0,
                        "internal_token_units_total": 0,
                        "elapsed_values": [],
                    },
                )
                bucket["total"] += 1
                bucket["elapsed_ms_total"] += float(r["elapsed_ms"])
                bucket["internal_token_units_total"] += int(r["internal_token_units_total"])
                bucket["elapsed_values"].append(float(r["elapsed_ms"]))
                if r["status"] == "PASS":
                    bucket["pass"] += 1
                elif r["status"] == "TIMEOUT":
                    bucket["timeout"] += 1
                else:
                    bucket["fail"] += 1

    for bucket_map in [by_group, by_source]:
        for bucket in bucket_map.values():
            vals = bucket["elapsed_values"]
            bucket["elapsed_ms_avg"] = bucket["elapsed_ms_total"] / bucket["total"] if bucket["total"] else 0.0
            bucket["elapsed_ms_p50"] = percentile(vals, 0.50)
            bucket["elapsed_ms_p95"] = percentile(vals, 0.95)
            bucket.pop("elapsed_values", None)

    slowest = sorted(results, key=lambda r: float(r["elapsed_ms"]), reverse=True)[:20]
    failures = [r for r in results if r["status"] != "PASS"]

    base57_count = by_group.get("BASE57_ORIGINAL_OR_CORE", {}).get("total", 0)

    summary = {
        "run_id": RUN_ID,
        "scope": "complete Lean surface: manifest + git tracked + git untracked + filtered repo scan",
        "manifest_present": MANIFEST.exists(),
        "event_count": len(results),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "timeout_count": timeout_count,
        "complete_lean_fail_count": fail_count + timeout_count,
        "base57_original_or_core_count": base57_count,
        "elapsed_ms_total": sum(elapsed_values),
        "elapsed_ms_avg": sum(elapsed_values) / len(elapsed_values) if elapsed_values else 0.0,
        "elapsed_ms_p50": percentile(elapsed_values, 0.50),
        "elapsed_ms_p95": percentile(elapsed_values, 0.95),
        "internal_token_units_total": sum(token_values),
        "by_group": by_group,
        "by_source": by_source,
        "slowest": slowest,
        "failures": failures,
        "results": results,
    }

    (REPORT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# Obsidure Complete Lean Surface Cost Metrics V0")
    lines.append("")
    lines.append(f"Run ID: {RUN_ID}")
    lines.append("Scope: manifest + git tracked + git untracked + filtered repo scan")
    lines.append(f"Manifest present: {MANIFEST.exists()}")
    lines.append(f"Events: {len(results)}")
    lines.append(f"PASS: {pass_count}")
    lines.append(f"FAIL: {fail_count}")
    lines.append(f"TIMEOUT: {timeout_count}")
    lines.append(f"COMPLETE_LEAN_FAIL_COUNT: {summary['complete_lean_fail_count']}")
    lines.append(f"BASE57_ORIGINAL_OR_CORE_COUNT: {base57_count}")
    lines.append(f"Elapsed total ms: {summary['elapsed_ms_total']:.2f}")
    lines.append(f"Elapsed avg ms: {summary['elapsed_ms_avg']:.2f}")
    lines.append(f"Elapsed p50 ms: {summary['elapsed_ms_p50']:.2f}")
    lines.append(f"Elapsed p95 ms: {summary['elapsed_ms_p95']:.2f}")
    lines.append(f"Internal token units total: {summary['internal_token_units_total']}")
    lines.append("")
    lines.append("## By group")
    lines.append("")
    lines.append("| Group | Total | PASS | FAIL | TIMEOUT | ms total | avg ms | p50 ms | p95 ms | internal token units |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for group, data in sorted(by_group.items()):
        lines.append(
            f"| {group} | {data['total']} | {data['pass']} | {data['fail']} | {data['timeout']} | "
            f"{data['elapsed_ms_total']:.2f} | {data['elapsed_ms_avg']:.2f} | "
            f"{data['elapsed_ms_p50']:.2f} | {data['elapsed_ms_p95']:.2f} | "
            f"{data['internal_token_units_total']} |"
        )
    lines.append("")
    lines.append("## By discovery source")
    lines.append("")
    lines.append("| Source | Total | PASS | FAIL | TIMEOUT | ms total | internal token units |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for source, data in sorted(by_source.items()):
        lines.append(
            f"| {source} | {data['total']} | {data['pass']} | {data['fail']} | {data['timeout']} | "
            f"{data['elapsed_ms_total']:.2f} | {data['internal_token_units_total']} |"
        )
    lines.append("")
    lines.append("## Slowest files")
    lines.append("")
    lines.append("| Status | Group | Path | ms | units |")
    lines.append("|---|---|---|---:|---:|")
    for r in slowest:
        lines.append(f"| {r['status']} | {r['group']} | {r['path']} | {float(r['elapsed_ms']):.2f} | {r['internal_token_units_total']} |")
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    if failures:
        lines.append("| Status | Group | Path | exit | stderr preview |")
        lines.append("|---|---|---|---:|---|")
        for r in failures:
            preview = (r["stderr_preview"] or "").replace("\n", " ").replace("|", "\\|")[:700]
            lines.append(f"| {r['status']} | {r['group']} | {r['path']} | {r['exit_code']} | {preview} |")
    else:
        lines.append("No Lean failures.")
    lines.append("")
    lines.append("## All files")
    lines.append("")
    lines.append("| Status | Group | Path | Sources | ms | units |")
    lines.append("|---|---|---|---|---:|---:|")
    for r in results:
        src = ",".join(r["sources"])
        lines.append(f"| {r['status']} | {r['group']} | {r['path']} | {src} | {float(r['elapsed_ms']):.2f} | {r['internal_token_units_total']} |")

    (REPORT_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print("")
    print(f"REPORT_DIR={REPORT_DIR}")
    print(f"SUMMARY_JSON={REPORT_DIR / 'summary.json'}")
    print(f"SUMMARY_MD={REPORT_DIR / 'summary.md'}")
    print(f"COMPLETE_LEAN_TOTAL={len(results)}")
    print(f"COMPLETE_LEAN_PASS_COUNT={pass_count}")
    print(f"COMPLETE_LEAN_FAIL_COUNT={summary['complete_lean_fail_count']}")
    print(f"BASE57_ORIGINAL_OR_CORE_COUNT={base57_count}")
    print(f"COMPLETE_LEAN_ELAPSED_MS_TOTAL={summary['elapsed_ms_total']:.2f}")
    print(f"COMPLETE_LEAN_INTERNAL_TOKEN_UNITS_TOTAL={summary['internal_token_units_total']}")

    return 1 if summary["complete_lean_fail_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
