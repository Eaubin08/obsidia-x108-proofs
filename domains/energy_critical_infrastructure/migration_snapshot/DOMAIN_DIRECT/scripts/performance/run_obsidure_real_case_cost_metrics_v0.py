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
REPORT_DIR = ROOT / ".local_reports" / f"OBSIDURE_REAL_CASE_COST_METRICS_{RUN_ID}"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def safe_read(path: Path, limit: int = 6000) -> str:
    if not path.exists():
        return f"MISSING_PATH={path}"
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit]


def run_case(
    *,
    family: str,
    case_id: str,
    command: list[str],
    timeout_sec: float = 120.0,
    lean_runs: int = 0,
    pytest_runs: int = 0,
    repair_iterations: int = 0,
    required: bool = True,
) -> dict[str, Any]:
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
        stdout_text = (exc.stdout or "")
        stderr_text = (exc.stderr or "")
        if isinstance(stdout_text, bytes):
            stdout_text = stdout_text.decode("utf-8", errors="replace")
        if isinstance(stderr_text, bytes):
            stderr_text = stderr_text.decode("utf-8", errors="replace")
        stderr_text += f"\nTIMEOUT_AFTER_SECONDS={timeout_sec}\n"

    elapsed_ms = (time.perf_counter() - start) * 1000
    ended = now_iso()

    if timed_out:
        status = "TIMEOUT"
    elif exit_code == 0:
        status = "PASS"
    else:
        status = "FAIL"

    combined = "\n".join([" ".join(command), stdout_text, stderr_text]).lower()

    event = build_cost_event(
        family=family,
        route=f"OBSIDURE::{case_id}",
        status=status,
        started_at=started,
        ended_at=ended,
        elapsed_ms=elapsed_ms,
        command=command,
        request_text=f"obsidure_real_case::{case_id}",
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        exit_code=exit_code,
        modules_considered=9,
        modules_activated=5,
        modules_skipped=4,
        files_read=0,
        files_written=0,
        memory_records_read=1 if "memory" in combined or "MATH_MEMORY_INDEX".lower() in combined else 0,
        memory_records_written=0,
        cache_hit=False,
        cache_miss=True,
        domain_agents_used=0,
        domain_votes=0,
        domain_aggregates=0,
        contradictions=combined.count("contradiction") + combined.count("conflict"),
        unknowns=combined.count("unknown") + combined.count("missing") + combined.count("undefined"),
        risk_flags=combined.count("risk") + combined.count("blocked") + combined.count("fail"),
        guard_invoked=False,
        guard_result="NOT_INVOKED",
        sigma_invoked=False,
        sigma_reports=0,
        lean_runs=lean_runs,
        pytest_runs=pytest_runs,
        repair_iterations=repair_iterations,
        proof_ready=(exit_code == 0 and (lean_runs > 0 or "manifest" in case_id)),
        quality_score=1.0 if exit_code == 0 else 0.0,
        boundary_ok=True,
        extra={
            "runner": "run_obsidure_real_case_cost_metrics_v0",
            "case_id": case_id,
            "required": required,
            "timeout_sec": timeout_sec,
        },
    )
    write_cost_event(event)

    print(
        f"{family} {case_id} status={status} "
        f"ms={elapsed_ms:.2f} units={event['internal_token_units_total']} "
        f"required={required}"
    )

    return event


def existing(path: str) -> bool:
    return (ROOT / path).exists()


def compile_python_files_case(files: list[Path]) -> dict[str, Any]:
    if not files:
        return run_case(
            family="OBSIDURE_CODE",
            case_id="run_obsidure_scripts_missing",
            command=[sys.executable, "-c", "import sys; print('NO_RUN_OBSIDURE_SCRIPTS_FOUND'); sys.exit(2)"],
            timeout_sec=30,
            required=False,
        )

    rels = [str(p.relative_to(ROOT)) for p in files]
    return run_case(
        family="OBSIDURE_CODE",
        case_id="run_obsidure_scripts_py_compile",
        command=[sys.executable, "-m", "py_compile", *rels],
        timeout_sec=120,
        required=True,
    )


def pick_lean_targets(limit: int = 6) -> list[Path]:
    candidates: list[Path] = []

    preferred = [
        ROOT / "proofs/lean/Obsidia/LegacyPeripheral/P47_Couplage_dR_dt.lean",
        ROOT / "proofs/lean/Obsidia/LegacyPeripheral/P50_DecisionAuthority.lean",
        ROOT / "proofs/lean/Obsidia/LegacyPeripheral/P52_ProofReady.lean",
        ROOT / "proofs/lean/Obsidia/LegacyPeripheral/P53_BridgeOnly.lean",
    ]

    for p in preferred:
        if p.exists() and p not in candidates:
            candidates.append(p)

    for pattern in [
        "proofs/lean/Obsidia/Peripheral/*.lean",
        "proofs/lean/Obsidia/LegacyPeripheral/*.lean",
        "proofs/lean/peripheral/*.lean",
    ]:
        for p in sorted(ROOT.glob(pattern)):
            if p.exists() and p not in candidates:
                candidates.append(p)
            if len(candidates) >= limit:
                return candidates

    return candidates[:limit]


def main() -> int:
    events: list[dict[str, Any]] = []

    # OBSIDURE_CODE: real scripts/tools surface.
    if existing("scripts/obsidure_cli.py"):
        events.append(run_case(
            family="OBSIDURE_CODE",
            case_id="obsidure_cli_py_compile",
            command=[sys.executable, "-m", "py_compile", "scripts/obsidure_cli.py"],
            timeout_sec=60,
            required=True,
        ))
    else:
        events.append(run_case(
            family="OBSIDURE_CODE",
            case_id="obsidure_cli_missing",
            command=[sys.executable, "-c", "import sys; print('MISSING scripts/obsidure_cli.py'); sys.exit(2)"],
            timeout_sec=30,
            required=False,
        ))

    for ps1_case, ps1_path in [
        ("obsidure_agent_runner_ps1_present", "scripts/run_agent_obsidure.ps1"),
        ("obsidure_apply_proposal_ps1_present", "scripts/apply_proposal.ps1"),
    ]:
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"if (Test-Path '{ps1_path}') {{ Get-Content '{ps1_path}' -TotalCount 80 | Out-String; exit 0 }} else {{ Write-Host 'MISSING {ps1_path}'; exit 2 }}",
        ]
        events.append(run_case(
            family="OBSIDURE_CODE",
            case_id=ps1_case,
            command=command,
            timeout_sec=45,
            required=True,
        ))

    run_obsidure_files = sorted(ROOT.glob("run_obsidure_*.py"))
    events.append(compile_python_files_case(run_obsidure_files))

    # OBSIDURE_LEAN: manifest + real Lean proof checks.
    if existing("scripts/gen_lean_proof_surface_manifest.py"):
        events.append(run_case(
            family="OBSIDURE_LEAN",
            case_id="lean_proof_surface_manifest_generate",
            command=[sys.executable, "scripts/gen_lean_proof_surface_manifest.py"],
            timeout_sec=120,
            lean_runs=0,
            required=True,
        ))
    else:
        events.append(run_case(
            family="OBSIDURE_LEAN",
            case_id="lean_proof_surface_manifest_missing",
            command=[sys.executable, "-c", "import sys; print('MISSING scripts/gen_lean_proof_surface_manifest.py'); sys.exit(2)"],
            timeout_sec=30,
            required=False,
        ))

    lean_targets = pick_lean_targets(limit=6)
    if not lean_targets:
        events.append(run_case(
            family="OBSIDURE_LEAN",
            case_id="lean_targets_missing",
            command=[sys.executable, "-c", "import sys; print('NO_LEAN_TARGETS_FOUND'); sys.exit(2)"],
            timeout_sec=30,
            lean_runs=0,
            required=False,
        ))
    else:
        for p in lean_targets:
            rel = str(p.relative_to(ROOT))
            safe_id = rel.replace("\\", "/").replace("/", "__").replace(".", "_")
            events.append(run_case(
                family="OBSIDURE_LEAN",
                case_id=f"lean_check__{safe_id}",
                command=["lake", "env", "lean", rel],
                timeout_sec=180,
                lean_runs=1,
                required=True,
            ))

    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "event_count": len(events),
        "pass_count": sum(1 for e in events if e["status"] == "PASS"),
        "fail_count": sum(1 for e in events if e["status"] not in {"PASS"}),
        "required_fail_count": sum(1 for e in events if e["status"] != "PASS" and e.get("extra", {}).get("required") is True),
        "by_family": {},
        "events": [
            {
                "family": e["family"],
                "route": e["route"],
                "status": e["status"],
                "elapsed_ms": e["elapsed_ms"],
                "internal_token_units_total": e["internal_token_units_total"],
                "lean_runs": e["lean_runs"],
                "pytest_runs": e["pytest_runs"],
            }
            for e in events
        ],
    }

    for e in events:
        fam = e["family"]
        bucket = summary["by_family"].setdefault(
            fam,
            {
                "total": 0,
                "pass": 0,
                "fail": 0,
                "elapsed_ms_total": 0.0,
                "internal_token_units_total": 0,
                "lean_runs": 0,
                "pytest_runs": 0,
            },
        )
        bucket["total"] += 1
        bucket["elapsed_ms_total"] += float(e["elapsed_ms"])
        bucket["internal_token_units_total"] += int(e["internal_token_units_total"])
        bucket["lean_runs"] += int(e["lean_runs"])
        bucket["pytest_runs"] += int(e["pytest_runs"])
        if e["status"] == "PASS":
            bucket["pass"] += 1
        else:
            bucket["fail"] += 1

    (REPORT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Obsidure Real Case Cost Metrics V0")
    lines.append("")
    lines.append(f"Run ID: {RUN_ID}")
    lines.append(f"Events: {summary['event_count']}")
    lines.append(f"PASS: {summary['pass_count']}")
    lines.append(f"FAIL: {summary['fail_count']}")
    lines.append(f"REQUIRED_FAIL: {summary['required_fail_count']}")
    lines.append("")
    lines.append("## By family")
    lines.append("")
    lines.append("| Family | Total | PASS | FAIL | Lean runs | Pytest runs | ms total | internal token units |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for fam, data in summary["by_family"].items():
        lines.append(
            f"| {fam} | {data['total']} | {data['pass']} | {data['fail']} | "
            f"{data['lean_runs']} | {data['pytest_runs']} | {data['elapsed_ms_total']:.2f} | "
            f"{data['internal_token_units_total']} |"
        )
    lines.append("")
    lines.append("## Events")
    lines.append("")
    lines.append("| Family | Route | Status | ms | units | Lean runs |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for e in summary["events"]:
        lines.append(
            f"| {e['family']} | {e['route']} | {e['status']} | "
            f"{float(e['elapsed_ms']):.2f} | {e['internal_token_units_total']} | {e['lean_runs']} |"
        )

    (REPORT_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print("")
    print(f"REPORT_DIR={REPORT_DIR}")
    print(f"SUMMARY_JSON={REPORT_DIR / 'summary.json'}")
    print(f"SUMMARY_MD={REPORT_DIR / 'summary.md'}")
    print(f"EVENT_COUNT={summary['event_count']}")
    print(f"PASS_COUNT={summary['pass_count']}")
    print(f"FAIL_COUNT={summary['fail_count']}")
    print(f"REQUIRED_FAIL_COUNT={summary['required_fail_count']}")

    return 1 if summary["required_fail_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
