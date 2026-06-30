from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EVENTS_FILE = ROOT / ".local_reports" / "REQUEST_COST_EVENTS" / "cost_events.jsonl"

VALID_FAMILIES = {
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
    "UNKNOWN",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def estimate_internal_token_units(char_count: int) -> int:
    return int(math.ceil(max(char_count, 0) / 4))


def normalize_family(family: str | None) -> str:
    value = (family or "UNKNOWN").strip().upper()
    return value if value in VALID_FAMILIES else "UNKNOWN"


def make_id(prefix: str, family: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{normalize_family(family)}_{stamp}"


def build_cost_event(
    *,
    family: str,
    route: str,
    status: str,
    started_at: str,
    ended_at: str,
    elapsed_ms: float,
    command: list[str] | None = None,
    request_text: str = "",
    stdout_text: str = "",
    stderr_text: str = "",
    exit_code: int | None = None,
    modules_considered: int = 0,
    modules_activated: int = 0,
    modules_skipped: int | None = None,
    files_read: int = 0,
    files_written: int = 0,
    memory_records_read: int = 0,
    memory_records_written: int = 0,
    cache_hit: bool = False,
    cache_miss: bool = False,
    domain_agents_used: int = 0,
    domain_votes: int = 0,
    domain_aggregates: int = 0,
    contradictions: int = 0,
    unknowns: int = 0,
    risk_flags: int = 0,
    guard_invoked: bool = False,
    guard_result: str = "NOT_INVOKED",
    sigma_invoked: bool = False,
    sigma_reports: int = 0,
    lean_runs: int = 0,
    pytest_runs: int = 0,
    repair_iterations: int = 0,
    proof_ready: bool = False,
    quality_score: float = 1.0,
    boundary_ok: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_family = normalize_family(family)
    command = command or []
    command_text = " ".join(command)

    input_chars = len(request_text) + len(command_text)
    output_chars = len(stdout_text) + len(stderr_text)

    internal_in = estimate_internal_token_units(input_chars)
    internal_out = estimate_internal_token_units(output_chars)
    internal_total = internal_in + internal_out

    if modules_skipped is None:
        modules_skipped = max(0, modules_considered - modules_activated)

    event: dict[str, Any] = {
        "request_id": make_id("REQ", normalized_family),
        "trace_id": make_id("TRACE_COST_EVENT", normalized_family),
        "family": normalized_family,
        "route": route or "UNKNOWN",
        "status": status,
        "started_at": started_at,
        "ended_at": ended_at,
        "elapsed_ms": float(elapsed_ms),

        "internal_token_units_in": internal_in,
        "internal_token_units_out": internal_out,
        "internal_token_units_total": internal_total,
        "internal_token_estimate_method": "ceil(char_count / 4)",
        "native_token_ledger_available": False,

        "modules_considered": int(modules_considered),
        "modules_activated": int(modules_activated),
        "modules_skipped": int(modules_skipped),

        "files_read": int(files_read),
        "files_written": int(files_written),
        "memory_records_read": int(memory_records_read),
        "memory_records_written": int(memory_records_written),
        "cache_hit": bool(cache_hit),
        "cache_miss": bool(cache_miss),

        "domain_agents_used": int(domain_agents_used),
        "domain_votes": int(domain_votes),
        "domain_aggregates": int(domain_aggregates),
        "contradictions": int(contradictions),
        "unknowns": int(unknowns),
        "risk_flags": int(risk_flags),

        "guard_invoked": bool(guard_invoked),
        "guard_result": guard_result,
        "sigma_invoked": bool(sigma_invoked),
        "sigma_reports": int(sigma_reports),

        "lean_runs": int(lean_runs),
        "pytest_runs": int(pytest_runs),
        "repair_iterations": int(repair_iterations),

        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "memory_write": False,
        "proof_ready": bool(proof_ready),

        "quality_score": float(quality_score),
        "boundary_ok": bool(boundary_ok),

        "command": command,
        "command_text": command_text,
        "exit_code": exit_code,
        "stdout_chars": len(stdout_text),
        "stderr_chars": len(stderr_text),
        "pid": os.getpid(),
        "writer": "request_cost_event_writer_v0",
    }

    if extra:
        event["extra"] = extra

    return event


def write_cost_event(event: dict[str, Any]) -> Path:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return EVENTS_FILE
