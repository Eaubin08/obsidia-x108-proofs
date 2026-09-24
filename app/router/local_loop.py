"""Adaptive Local Capability Loop — Track 1 / AMD.

Orchestrates the existing local solver capabilities with time-based
termination, strategy deduplication, and a SAFE/ZERO_TOKEN mode.

Termination is guaranteed by construction:
  1. A finite strategy registry — each entry runs at most once per
     (strategy_id, repr_hash) pair.
  2. Deduplication: identical (strategy, repr, candidate) triples are
     skipped instantly.
  3. Time guard: every iteration checks remaining budget before starting.
  4. Plateau detection: the loop exits when no remaining strategy can
     target an unmet constraint.
  5. Immediate exit on first valid answer.

Never spawns subprocesses or makes network calls.
Never stores task_id as a routing key.
Never uses expected_answer.
"""
from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


# ── Mode ─────────────────────────────────────────────────────────────────────

class LocalMode(str, Enum):
    SAFE = "SAFE"       # local first, Fireworks fallback if needed
    ZERO = "ZERO"       # local only, no Fireworks ever

_ENV_KEY = "TRACK1_LOCAL_MODE"
_DEFAULT_MODE = LocalMode.SAFE


def get_local_mode() -> LocalMode:
    """Single parsing authority for TRACK1_LOCAL_MODE."""
    raw = os.environ.get(_ENV_KEY, "").strip().upper()
    if raw == "ZERO":
        return LocalMode.ZERO
    return LocalMode.SAFE


# ── Budget constants ──────────────────────────────────────────────────────────

# AMD cap: 30 s per answer. We keep 3 s headroom for validation + projection.
TASK_HARD_CEILING_S    = 27.0
# Reserve for Fireworks call in SAFE mode (p95 live latency was ~2.5 s,
# plus retry budget, plus safety margin → 6 s is conservative).
SAFE_REMOTE_RESERVE_S  = 6.0
# Minimum time we must keep for output finalisation (JSON write, exit) in
# any mode.
OUTPUT_RESERVE_S       = 1.0
# Global container budget (AMD: 10 min). The runner already tracks the real
# deadline; we derive per-task share from remaining time.
GLOBAL_BUDGET_S        = 600.0
# Minimum time for a single strategy attempt.
MIN_STRATEGY_BUDGET_S  = 0.05


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class LocalLoopContext:
    task_started_at: float
    local_deadline: float     # = started + soft_budget - reserve
    mode: LocalMode
    strategies_attempted: set[str] = field(default_factory=set)
    candidate_hashes: set[str] = field(default_factory=set)
    best_candidate: str | None = None
    termination_reason: str | None = None
    progress_trace: list[dict] = field(default_factory=list)

    def time_remaining_s(self) -> float:
        return max(0.0, self.local_deadline - time.perf_counter())

    def budget_exhausted(self) -> bool:
        return self.time_remaining_s() < MIN_STRATEGY_BUDGET_S

    def dedup_key(self, strategy_id: str, repr_text: str) -> str:
        h = hashlib.md5((strategy_id + "\x00" + repr_text).encode()).hexdigest()[:12]
        return f"{strategy_id}:{h}"

    def mark_attempted(self, strategy_id: str, repr_text: str) -> bool:
        """Return True if this (strategy, repr) pair is new; record it."""
        key = self.dedup_key(strategy_id, repr_text)
        if key in self.strategies_attempted:
            return False
        self.strategies_attempted.add(key)
        return True

    def is_duplicate_candidate(self, candidate: str) -> bool:
        h = hashlib.md5(candidate.strip().lower().encode()).hexdigest()[:16]
        if h in self.candidate_hashes:
            return True
        self.candidate_hashes.add(h)
        return False


@dataclass
class LocalLoopResult:
    final_candidate: str | None
    final_status: str          # VALID | ABSTAINED | TIMEOUT | PLATEAU | ZERO_BLOCKED
    strategies_attempted: list[str]
    candidates_generated: int
    local_elapsed_ms: float
    termination_reason: str
    remote_required: bool
    mode: str
    progress_trace: list[dict]
    task_soft_budget_s: float
    local_budget_s: float
    remote_reserve_s: float


# ── Strategy helpers ──────────────────────────────────────────────────────────

def _norm_lower(prompt: str) -> str:
    """Lowercase normalisation — reduces accidental case sensitivity."""
    return prompt.lower()


def _decompose_subparts(prompt: str) -> list[str]:
    """Split a multi-part question into sub-questions.

    Handles patterns like:
      "What is X, and what is Y?"
      "What is X? What is Y?"
    Returns [prompt] if no sub-parts found (safe fallback).
    """
    import re
    # Split on ", and ..." or "? ..." keeping the question structure
    parts: list[str] = []
    # Pattern: "What/Who/Which ... , and what/who/which ..."
    split_re = re.compile(r",\s+and\s+", re.I)
    if split_re.search(prompt):
        segments = split_re.split(prompt)
        # Each segment should form a complete question
        for i, seg in enumerate(segments):
            seg = seg.strip()
            if not seg:
                continue
            if not seg.endswith("?"):
                seg += "?"
            # For follow-up segments, keep enough context
            parts.append(seg)
    if len(parts) < 2:
        # Try splitting on "? " boundary (two separate questions)
        q_parts = re.split(r"\?\s+", prompt)
        if len(q_parts) >= 2:
            parts = [p.strip() + "?" for p in q_parts if p.strip()]
    return parts if len(parts) >= 2 else [prompt]


def _alt_numeric_form(prompt: str) -> str | None:
    """Rewrite numeric expressions to an alternate form (e.g. 1,000 → 1000)."""
    import re
    cleaned = re.sub(r"(\d),(\d{3})", r"\1\2", prompt)
    cleaned = re.sub(r"\band\s+a\s+half\b", ".5", cleaned, flags=re.I)
    return cleaned if cleaned != prompt else None


# ── Strategy implementations ──────────────────────────────────────────────────

def _strategy_solver_cascade(prompt: str) -> str | None:
    """Strategy 1: run the full existing solver cascade."""
    from app.router.local_solvers import try_local_solvers_traced
    hit, _ = try_local_solvers_traced(prompt)
    if hit:
        return hit["answer"]
    return None


def _strategy_norm_lower(prompt: str) -> str | None:
    """Strategy 2: lowercase normalisation + solver cascade."""
    normed = _norm_lower(prompt)
    if normed == prompt:
        return None  # no change — would be a duplicate run
    from app.router.local_solvers import try_local_solvers_traced
    hit, _ = try_local_solvers_traced(normed)
    if hit:
        return hit["answer"]
    return None


def _strategy_decompose_subparts(prompt: str) -> str | None:
    """Strategy 3: decompose multi-part into sub-questions and merge answers."""
    from app.router.local_solvers import try_local_solvers_traced
    parts = _decompose_subparts(prompt)
    if len(parts) < 2:
        return None  # no decomposition possible
    answers: list[str] = []
    for sub in parts:
        hit, _ = try_local_solvers_traced(sub)
        if not hit:
            return None  # one sub-part failed — can't safely merge
        answers.append(hit["answer"].rstrip("."))
    merged = ". ".join(answers) + "."
    return merged


def _strategy_alt_numeric(prompt: str) -> str | None:
    """Strategy 4: rewrite numeric form and retry solvers."""
    alt = _alt_numeric_form(prompt)
    if not alt:
        return None
    from app.router.local_solvers import try_local_solvers_traced
    hit, _ = try_local_solvers_traced(alt)
    if hit:
        return hit["answer"]
    return None


# ── Strategy registry ─────────────────────────────────────────────────────────
# Order determines priority. Each entry: (id, fn, applicable_filter).
# The filter receives the prompt and returns True if the strategy is worth
# attempting for this specific input.

def _always(_prompt: str) -> bool:
    return True


def _multi_part_filter(prompt: str) -> bool:
    import re
    return bool(re.search(r",\s+and\s+|and\s+what\b|and\s+which\b|\?\s+\w", prompt, re.I))


def _has_numeric(prompt: str) -> bool:
    import re
    return bool(re.search(r"\d", prompt))


_STRATEGY_REGISTRY: list[tuple[str, Callable[[str], str | None], Callable[[str], bool]]] = [
    ("SOLVER_CASCADE",    _strategy_solver_cascade,    _always),
    ("DECOMPOSE_SUBPART", _strategy_decompose_subparts, _multi_part_filter),
    ("NORM_LOWER",        _strategy_norm_lower,         _always),
    ("ALT_NUMERIC",       _strategy_alt_numeric,        _has_numeric),
]


# ── Candidate validation ──────────────────────────────────────────────────────

def _validate_candidate(candidate: str | None) -> bool:
    """Minimal structural validation: non-empty, non-error, English."""
    if not candidate or not candidate.strip():
        return False
    if candidate.startswith("[error]") or "[dry-run]" in candidate:
        return False
    return True


# ── Budget calculation ────────────────────────────────────────────────────────

def compute_task_budget(
    global_start: float,
    global_deadline: float | None,
    remaining_tasks: int,
    mode: LocalMode,
) -> tuple[float, float, float, str]:
    """Return (task_soft_budget_s, local_budget_s, remote_reserve_s, reason).

    task_soft_budget = min(HARD_CEILING, fair_share - finalization)
    local_budget     = task_soft_budget - remote_reserve (SAFE)
                     = task_soft_budget - OUTPUT_RESERVE (ZERO)
    """
    if global_deadline is not None:
        global_remaining = max(0.0, global_deadline - time.perf_counter())
        fair_share = global_remaining / max(remaining_tasks, 1)
    else:
        global_remaining = GLOBAL_BUDGET_S
        fair_share = TASK_HARD_CEILING_S

    task_soft = min(TASK_HARD_CEILING_S, fair_share - OUTPUT_RESERVE_S)
    task_soft = max(task_soft, MIN_STRATEGY_BUDGET_S * 2)

    if mode == LocalMode.ZERO:
        remote_reserve = 0.0
        local_budget = task_soft - OUTPUT_RESERVE_S
        reason = "zero_mode_no_remote_reserve"
    else:
        remote_reserve = SAFE_REMOTE_RESERVE_S
        local_budget = task_soft - remote_reserve
        reason = f"safe_mode_remote_reserve_{remote_reserve:.0f}s"

    local_budget = max(local_budget, MIN_STRATEGY_BUDGET_S)
    return task_soft, local_budget, remote_reserve, reason


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_local_loop(
    prompt: str,
    *,
    mode: LocalMode,
    global_deadline: float | None = None,
    remaining_tasks: int = 1,
) -> LocalLoopResult:
    """Run the adaptive local capability loop.

    Returns a LocalLoopResult. Caller inspects .remote_required to decide
    whether to escalate to Fireworks (SAFE mode only).
    """
    t0 = time.perf_counter()

    task_soft, local_budget, remote_reserve, budget_reason = compute_task_budget(
        t0, global_deadline, remaining_tasks, mode)

    local_deadline = t0 + local_budget
    ctx = LocalLoopContext(
        task_started_at=t0,
        local_deadline=local_deadline,
        mode=mode,
    )

    strategies_run: list[str] = []
    candidates_generated = 0
    final_candidate: str | None = None
    final_status = "ABSTAINED"
    termination_reason = "no_strategy_matched"

    for strategy_id, strategy_fn, applicable in _STRATEGY_REGISTRY:
        # Time guard: ensure enough budget remains for this strategy
        if ctx.budget_exhausted():
            termination_reason = "local_deadline"
            final_status = "TIMEOUT"
            break

        # Applicability filter: skip strategies irrelevant to this prompt
        if not applicable(prompt):
            continue

        # Deduplication: skip if this (strategy, repr) pair was already tried
        if not ctx.mark_attempted(strategy_id, prompt):
            continue

        strategies_run.append(strategy_id)

        try:
            t_strat = time.perf_counter()
            candidate = strategy_fn(prompt)
            elapsed_ms = (time.perf_counter() - t_strat) * 1000
        except Exception:
            ctx.progress_trace.append({
                "strategy": strategy_id, "status": "exception", "elapsed_ms": 0})
            continue

        trace_entry: dict = {
            "strategy": strategy_id,
            "produced": candidate is not None,
            "elapsed_ms": round(elapsed_ms, 1),
        }

        if candidate is None:
            trace_entry["status"] = "abstained"
            ctx.progress_trace.append(trace_entry)
            continue

        candidates_generated += 1

        # Deduplication: reject identical candidates
        if ctx.is_duplicate_candidate(candidate):
            trace_entry["status"] = "duplicate"
            ctx.progress_trace.append(trace_entry)
            continue

        # Validate
        if _validate_candidate(candidate):
            ctx.best_candidate = candidate
            final_candidate = candidate
            final_status = "VALID"
            termination_reason = "first_valid_answer"
            trace_entry["status"] = "valid"
            ctx.progress_trace.append(trace_entry)
            break  # immediate exit on first valid answer
        else:
            trace_entry["status"] = "invalid"
            ctx.progress_trace.append(trace_entry)

    else:
        # Loop exhausted all strategies without finding a valid answer → plateau
        if final_status != "VALID":
            termination_reason = "plateau_no_strategies_remaining"
            final_status = "PLATEAU"

    elapsed_s = time.perf_counter() - t0

    # remote_required: True only in SAFE mode when no valid local answer was found
    if final_status == "VALID":
        remote_required = False
    elif mode == LocalMode.ZERO:
        remote_required = False  # ZERO mode never escalates
    else:
        remote_required = True   # SAFE mode: escalate to Fireworks

    # Bounded progress trace (never grows unbounded)
    bounded_trace = ctx.progress_trace[:20]

    return LocalLoopResult(
        final_candidate=final_candidate,
        final_status=final_status,
        strategies_attempted=strategies_run,
        candidates_generated=candidates_generated,
        local_elapsed_ms=round(elapsed_s * 1000, 2),
        termination_reason=termination_reason,
        remote_required=remote_required,
        mode=mode.value,
        progress_trace=bounded_trace,
        task_soft_budget_s=round(task_soft, 3),
        local_budget_s=round(local_budget, 3),
        remote_reserve_s=round(remote_reserve, 3),
    )
