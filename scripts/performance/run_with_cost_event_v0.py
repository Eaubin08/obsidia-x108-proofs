from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from apps.obsidia_api.request_cost_event_writer import (
    VALID_FAMILIES,
    build_cost_event,
    now_iso,
    write_cost_event,
)


DEFAULT_MODULES = {
    "BRODY_CHAT": (8, 3),
    "BRODY_MEMORY": (8, 4),
    "BRODY_FASTPATH": (8, 3),
    "DOMAIN_BANK": (10, 6),
    "DOMAIN_TRADING": (10, 6),
    "DOMAIN_GPS_AVIATION": (10, 6),
    "OBSIDURE_LEAN": (9, 5),
    "OBSIDURE_CODE": (9, 5),
    "X108_GUARD": (7, 4),
    "SIGMA_REPORT": (7, 4),
    "RUNTIME_API": (8, 5),
    "UNKNOWN": (0, 0),
}


def infer_counts(family: str, command: list[str], stdout_text: str, stderr_text: str) -> dict[str, object]:
    text = " ".join(command).lower() + "\n" + stdout_text.lower() + "\n" + stderr_text.lower()

    modules_considered, modules_activated = DEFAULT_MODULES.get(family, (0, 0))

    lean_runs = 1 if ("lake env lean" in text or ".lean" in text) else 0
    pytest_runs = 1 if ("pytest" in text or "python -m pytest" in text) else 0
    repair_iterations = 1 if ("repair" in text or "fix" in text or "corrig" in text) else 0

    guard_invoked = family in {"DOMAIN_BANK", "DOMAIN_TRADING", "DOMAIN_GPS_AVIATION", "X108_GUARD"}
    sigma_invoked = family in {"DOMAIN_BANK", "DOMAIN_TRADING", "DOMAIN_GPS_AVIATION", "SIGMA_REPORT"}

    contradictions = sum(text.count(k) for k in ["contradiction", "conflict", "mismatch"])
    unknowns = sum(text.count(k) for k in ["unknown", "missing", "undefined"])
    risk_flags = sum(text.count(k) for k in ["risk", "fraud", "blocked", "suspicious", "brownout", "spoof", "flashcrash"])

    guard_result = "NOT_INVOKED"
    if guard_invoked:
        guard_result = "HOLD_OR_BLOCK_CANDIDATE" if (contradictions or unknowns or risk_flags) else "ALLOW_CANDIDATE"

    return {
        "modules_considered": modules_considered,
        "modules_activated": modules_activated,
        "modules_skipped": max(0, modules_considered - modules_activated),
        "lean_runs": lean_runs,
        "pytest_runs": pytest_runs,
        "repair_iterations": repair_iterations,
        "guard_invoked": guard_invoked,
        "guard_result": guard_result,
        "sigma_invoked": sigma_invoked,
        "sigma_reports": 1 if sigma_invoked else 0,
        "contradictions": contradictions,
        "unknowns": unknowns,
        "risk_flags": risk_flags,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real Obsidia command and append a cost_event.")
    parser.add_argument("--family", required=True, choices=sorted(VALID_FAMILIES))
    parser.add_argument("--route", required=True)
    parser.add_argument("--request-text", default="")
    parser.add_argument("--cwd", default=str(ROOT))
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        print("BLOCK: no command supplied after --", file=sys.stderr)
        return 2

    started = now_iso()
    start = time.perf_counter()

    proc = subprocess.run(
        command,
        cwd=args.cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000
    ended = now_iso()

    stdout_text = proc.stdout or ""
    stderr_text = proc.stderr or ""

    if stdout_text:
        print(stdout_text, end="")
    if stderr_text:
        print(stderr_text, end="", file=sys.stderr)

    inferred = infer_counts(args.family, command, stdout_text, stderr_text)
    status = "PASS" if proc.returncode == 0 else "FAIL"

    event = build_cost_event(
        family=args.family,
        route=args.route,
        status=status,
        started_at=started,
        ended_at=ended,
        elapsed_ms=elapsed_ms,
        command=command,
        request_text=args.request_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        exit_code=proc.returncode,
        modules_considered=int(inferred["modules_considered"]),
        modules_activated=int(inferred["modules_activated"]),
        modules_skipped=int(inferred["modules_skipped"]),
        lean_runs=int(inferred["lean_runs"]),
        pytest_runs=int(inferred["pytest_runs"]),
        repair_iterations=int(inferred["repair_iterations"]),
        guard_invoked=bool(inferred["guard_invoked"]),
        guard_result=str(inferred["guard_result"]),
        sigma_invoked=bool(inferred["sigma_invoked"]),
        sigma_reports=int(inferred["sigma_reports"]),
        contradictions=int(inferred["contradictions"]),
        unknowns=int(inferred["unknowns"]),
        risk_flags=int(inferred["risk_flags"]),
        proof_ready=proc.returncode == 0 and int(inferred["lean_runs"]) > 0,
        quality_score=1.0 if proc.returncode == 0 else 0.0,
        boundary_ok=True,
        extra={
            "runner": "run_with_cost_event_v0",
            "cwd": str(Path(args.cwd).resolve()),
        },
    )

    target = write_cost_event(event)

    print("")
    print(f"COST_EVENT_WRITTEN={target}")
    print(f"COST_EVENT_REQUEST_ID={event['request_id']}")
    print(f"COST_EVENT_FAMILY={event['family']}")
    print(f"COST_EVENT_ROUTE={event['route']}")
    print(f"COST_EVENT_STATUS={event['status']}")
    print(f"COST_EVENT_ELAPSED_MS={event['elapsed_ms']:.4f}")
    print(f"COST_EVENT_INTERNAL_TOKEN_UNITS_TOTAL={event['internal_token_units_total']}")

    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
