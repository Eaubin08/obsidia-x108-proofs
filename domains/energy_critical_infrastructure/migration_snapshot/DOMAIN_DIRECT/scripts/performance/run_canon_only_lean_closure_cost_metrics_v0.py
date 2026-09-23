from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from apps.obsidia_api.request_cost_event_writer import build_cost_event, now_iso, write_cost_event


RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DIR = ROOT / ".local_reports" / f"OBSIDURE_CANON_ONLY_LEAN_CLOSURE_{RUN_ID}"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

LEAN_ROOT = ROOT / "proofs" / "lean"
MANIFEST = ROOT / "proofs" / "LEAN_PROOF_SURFACE_MANIFEST.json"

EXCLUDE_PREFIXES = (
    "_BACKUP_ORIGINALS_",
    "_EPHEMERAL_CODE_SANDBOX_",
    "ci_recheck_optional_publication/",
)

EXCLUDE_CONTAINS = (
    "/wip/",
    "\\wip\\",
)

EXCLUDE_EXACT = {
    "proofs/lean/lakefile.lean",
}


MODULE_TARGETS = [
    ("CANON_MODULE", "Obsidia"),
    ("CANON_MODULE", "Obsidia.Refinement"),
    ("CANON_MODULE", "Obsidia.Peripheral"),
    ("CANON_MODULE", "Obsidia.LegacyPeripheral"),
    ("CANON_MODULE_OPTIONAL", "Obsidia.GeneratedPeripheral"),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def is_excluded_path(path_str: str) -> bool:
    s = path_str.replace("\\", "/")
    if s in EXCLUDE_EXACT:
        return True
    if any(s.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return True
    if any(token in s for token in EXCLUDE_CONTAINS):
        return True
    if s.startswith("proofs/lean/peripheral/"):
        return True
    return False


def git_tracked_lean_files() -> set[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-files", "*.lean"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    except Exception:
        return set()

    out = set()
    for line in proc.stdout.splitlines():
        line = line.strip().replace("\\", "/")
        if line.endswith(".lean") and not is_excluded_path(line):
            out.add(line)
    return out


def collect_manifest_strings(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        if ".lean" in value:
            out.append(value)
    elif isinstance(value, list):
        for item in value:
            out.extend(collect_manifest_strings(item))
    elif isinstance(value, dict):
        for item in value.values():
            out.extend(collect_manifest_strings(item))
    return out


def manifest_lean_files() -> set[str]:
    if not MANIFEST.exists():
        return set()

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return set()

    out = set()
    for raw in collect_manifest_strings(data):
        s = raw.replace("\\", "/").strip().strip("`'\" ")
        for marker in ["proofs/", "periphery/"]:
            if marker in s:
                s = s[s.index(marker):]
                break
        s = s.strip().strip("`'\" ")
        if s.endswith(".lean") and not is_excluded_path(s):
            if (ROOT / s).exists():
                out.add(s)
    return out


def canonical_file_targets() -> list[tuple[str, str]]:
    files = set()

    # tracked canon files
    files |= git_tracked_lean_files()

    # manifest canon files
    files |= manifest_lean_files()

    # explicit current sandbox origin files, but not backups/ephemeral/copies
    sandbox = ROOT / "periphery" / "lean_sandbox"
    if sandbox.exists():
        for p in sandbox.glob("*.lean"):
            s = rel(p)
            if not is_excluded_path(s):
                files.add(s)

    # Exclude module aggregators handled by lake build.
    module_aggregator_paths = {
        "proofs/lean/Obsidia.lean",
        "proofs/lean/Obsidia/Refinement.lean",
        "proofs/lean/Obsidia/Peripheral.lean",
        "proofs/lean/Obsidia/LegacyPeripheral.lean",
        "proofs/lean/Obsidia/GeneratedPeripheral.lean",
    }

    out = []
    for s in sorted(files):
        if s in module_aggregator_paths:
            continue
        if s.startswith("proofs/lean/Obsidia/Peripheral/"):
            out.append(("CANON_PERIPHERAL_CHILD", s))
        elif s.startswith("proofs/lean/Obsidia/LegacyPeripheral/"):
            out.append(("CANON_LEGACY_CHILD", s))
        elif s.startswith("proofs/lean/Obsidia/GeneratedPeripheral/"):
            out.append(("CANON_GENERATED_CHILD", s))
        elif s.startswith("proofs/lean/Obsidia/"):
            out.append(("CANON_CORE_CHILD", s))
        elif s.startswith("periphery/lean_sandbox/"):
            out.append(("CANON_ORIGINAL_SANDBOX", s))
        else:
            out.append(("CANON_OTHER_TRACKED", s))
    return out


def run_command(group: str, label: str, command: list[str], cwd: Path, required: bool = True) -> dict[str, Any]:
    started = now_iso()
    start = time.perf_counter()

    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=360,
        )
        exit_code = proc.returncode
        stdout_text = proc.stdout or ""
        stderr_text = proc.stderr or ""
        status = "PASS" if exit_code == 0 else "FAIL"
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stdout_text = exc.stdout or ""
        stderr_text = exc.stderr or ""
        if isinstance(stdout_text, bytes):
            stdout_text = stdout_text.decode("utf-8", errors="replace")
        if isinstance(stderr_text, bytes):
            stderr_text = stderr_text.decode("utf-8", errors="replace")
        stderr_text += "\nTIMEOUT_AFTER_SECONDS=360\n"
        status = "TIMEOUT"

    elapsed_ms = (time.perf_counter() - start) * 1000
    ended = now_iso()
    combined = "\n".join([" ".join(command), stdout_text, stderr_text]).lower()

    event = build_cost_event(
        family="OBSIDURE_LEAN",
        route=f"CANON_ONLY::{label}",
        status=status,
        started_at=started,
        ended_at=ended,
        elapsed_ms=elapsed_ms,
        command=command,
        request_text=f"canon_only_lean_closure::{label}",
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
        proof_ready=(exit_code == 0),
        quality_score=1.0 if exit_code == 0 else 0.0,
        boundary_ok=True,
        extra={
            "runner": "run_canon_only_lean_closure_cost_metrics_v0",
            "group": group,
            "label": label,
            "required": required,
            "cwd": str(cwd),
        },
    )
    write_cost_event(event)

    return {
        "group": group,
        "label": label,
        "command": " ".join(command),
        "cwd": str(cwd),
        "required": required,
        "status": status,
        "exit_code": exit_code,
        "elapsed_ms": elapsed_ms,
        "internal_token_units_total": int(event["internal_token_units_total"]),
        "stdout_preview": stdout_text[:1600],
        "stderr_preview": stderr_text[:1600],
    }



OBSIDIA_METRICS_HELP_GUARD_V1 = """Usage: python scripts/performance/run_canon_only_lean_closure_cost_metrics_v0.py [--help]

Obsidure canon-only Lean closure cost metrics.

Measures the active canonical Lean closure only; excludes backups, ephemeral sandboxes, and publication copies.

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

    results = []

    print("=== CANON MODULE BUILDS ===")
    for group, module in MODULE_TARGETS:
        required = group != "CANON_MODULE_OPTIONAL"
        print(f"\n--- lake build {module} ---")
        r = run_command(
            group=group,
            label=f"lake_build::{module}",
            command=["lake", "build", module],
            cwd=LEAN_ROOT,
            required=required,
        )
        results.append(r)
        print(f"{r['status']} exit={r['exit_code']} ms={r['elapsed_ms']:.2f} units={r['internal_token_units_total']}")
        if r["status"] != "PASS":
            print(r["stdout_preview"] or r["stderr_preview"])

    targets = canonical_file_targets()

    print("")
    print(f"CANON_FILE_TARGETS={len(targets)}")

    for idx, (group, path_str) in enumerate(targets, start=1):
        print(f"\n--- canon file {idx}/{len(targets)} :: {path_str} ---")
        r = run_command(
            group=group,
            label=f"lean_file::{path_str}",
            command=["lake", "env", "lean", path_str],
            cwd=ROOT,
            required=True,
        )
        results.append(r)
        print(f"{r['status']} exit={r['exit_code']} ms={r['elapsed_ms']:.2f} units={r['internal_token_units_total']}")
        if r["status"] != "PASS":
            print(r["stdout_preview"] or r["stderr_preview"])

    failures = [r for r in results if r["status"] != "PASS" and r["required"]]
    optional_failures = [r for r in results if r["status"] != "PASS" and not r["required"]]

    by_group: dict[str, dict[str, Any]] = {}
    for r in results:
        b = by_group.setdefault(r["group"], {"total": 0, "pass": 0, "fail": 0, "timeout": 0, "ms_total": 0.0, "units": 0})
        b["total"] += 1
        b["ms_total"] += float(r["elapsed_ms"])
        b["units"] += int(r["internal_token_units_total"])
        if r["status"] == "PASS":
            b["pass"] += 1
        elif r["status"] == "TIMEOUT":
            b["timeout"] += 1
        else:
            b["fail"] += 1

    summary = {
        "run_id": RUN_ID,
        "scope": "canon-only Lean closure",
        "total": len(results),
        "pass_count": sum(1 for r in results if r["status"] == "PASS"),
        "required_fail_count": len(failures),
        "optional_fail_count": len(optional_failures),
        "by_group": by_group,
        "failures": failures,
        "optional_failures": optional_failures,
        "results": results,
    }

    (REPORT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Obsidure Canon-Only Lean Closure Cost Metrics V0")
    lines.append("")
    lines.append(f"Run ID: {RUN_ID}")
    lines.append(f"Total: {summary['total']}")
    lines.append(f"PASS: {summary['pass_count']}")
    lines.append(f"Required FAIL/TIMEOUT: {summary['required_fail_count']}")
    lines.append(f"Optional FAIL/TIMEOUT: {summary['optional_fail_count']}")
    lines.append("")
    lines.append("## By group")
    lines.append("")
    lines.append("| Group | Total | PASS | FAIL | TIMEOUT | ms total | units |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for group, b in sorted(by_group.items()):
        lines.append(f"| {group} | {b['total']} | {b['pass']} | {b['fail']} | {b['timeout']} | {b['ms_total']:.2f} | {b['units']} |")

    lines.append("")
    lines.append("## Failures")
    lines.append("")
    if failures or optional_failures:
        lines.append("| Required | Group | Status | Label | Exit | Preview |")
        lines.append("|---|---|---|---|---:|---|")
        for r in failures + optional_failures:
            preview = (r["stdout_preview"] or r["stderr_preview"] or "").replace("\n", " ").replace("|", "\\|")[:800]
            lines.append(f"| {r['required']} | {r['group']} | {r['status']} | {r['label']} | {r['exit_code']} | {preview} |")
    else:
        lines.append("No failures.")

    lines.append("")
    lines.append("## All results")
    lines.append("")
    lines.append("| Group | Status | Label | ms | units |")
    lines.append("|---|---|---|---:|---:|")
    for r in results:
        lines.append(f"| {r['group']} | {r['status']} | {r['label']} | {float(r['elapsed_ms']):.2f} | {r['internal_token_units_total']} |")

    (REPORT_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print("")
    print(f"REPORT_DIR={REPORT_DIR}")
    print(f"SUMMARY_JSON={REPORT_DIR / 'summary.json'}")
    print(f"SUMMARY_MD={REPORT_DIR / 'summary.md'}")
    print(f"CANON_TOTAL={summary['total']}")
    print(f"CANON_PASS={summary['pass_count']}")
    print(f"CANON_REQUIRED_FAIL={summary['required_fail_count']}")
    print(f"CANON_OPTIONAL_FAIL={summary['optional_fail_count']}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
