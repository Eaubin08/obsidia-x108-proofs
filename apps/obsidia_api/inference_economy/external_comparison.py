"""OIE V0 External Benchmark — ExternalComparisonReceipt.

Mesure comparative entre Obsidia et un provider externe (Claude Code / API).
Non-souverain : readonly, emits_act=False, kernel_mutation=False.
Aucune cle API n'est jamais stockee. secrets_redacted=True toujours.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional

# ── Governance constants (immutable) ─────────────────────────────────────────
READONLY: bool = True
DECISION_AUTHORITY: str = "KX108_ONLY"
EMITS_ACT: bool = False
KERNEL_MUTATION: bool = False
MEMORY_WRITE: bool = False
GRAPHITI_WRITE: bool = False
NEO4J_WRITE: bool = False
SECRETS_REDACTED: bool = True

# ── Output excerpt max length ─────────────────────────────────────────────────
EXCERPT_MAX_CHARS: int = 500


@dataclass
class ExternalComparisonReceipt:
    # ── Identity ──────────────────────────────────────────────────────────────
    comparison_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ── Task description ──────────────────────────────────────────────────────
    task_id: str = ""
    task_family: str = ""
    task_prompt: str = ""
    obsidia_route: str = ""
    obsidia_expected_output_type: str = ""

    # ── Obsidia side ──────────────────────────────────────────────────────────
    obsidia_cost_eur_per_1m: float = 0.0
    obsidia_latency_ms: float = 0.0
    obsidia_success: bool = True

    # ── External side — detection ─────────────────────────────────────────────
    external_provider: str = ""
    external_model_or_cli: str = ""
    external_command_detected: str = ""
    external_available: bool = False
    external_network_allowed: bool = False

    # ── External side — run result ────────────────────────────────────────────
    external_latency_ms: Optional[float] = None
    external_success: bool = False
    external_error: str = ""
    external_output_excerpt: str = ""      # max EXCERPT_MAX_CHARS

    # ── External side — usage ─────────────────────────────────────────────────
    external_usage_available: bool = False
    external_input_tokens: Optional[int] = None
    external_output_tokens: Optional[int] = None
    external_total_tokens: Optional[int] = None
    external_cost_eur: Optional[float] = None
    external_cost_eur_per_1m_estimate: Optional[float] = None
    cost_source: str = "USAGE_UNAVAILABLE"

    # ── Quality ───────────────────────────────────────────────────────────────
    quality_score: Optional[float] = None
    quality_notes: str = ""
    retries_count: int = 0

    # ── Comparison ────────────────────────────────────────────────────────────
    savings_ratio_vs_external: Optional[float] = None
    avoided_cost_eur_per_1m: Optional[float] = None

    # ── Governance (immutable via __post_init__) ──────────────────────────────
    readonly: bool = READONLY
    decision_authority: str = DECISION_AUTHORITY
    emits_act: bool = EMITS_ACT
    kernel_mutation: bool = KERNEL_MUTATION
    memory_write: bool = MEMORY_WRITE
    graphiti_write: bool = GRAPHITI_WRITE
    neo4j_write: bool = NEO4J_WRITE
    secrets_redacted: bool = SECRETS_REDACTED

    def __post_init__(self) -> None:
        object.__setattr__(self, "readonly", READONLY)
        object.__setattr__(self, "decision_authority", DECISION_AUTHORITY)
        object.__setattr__(self, "emits_act", EMITS_ACT)
        object.__setattr__(self, "kernel_mutation", KERNEL_MUTATION)
        object.__setattr__(self, "memory_write", MEMORY_WRITE)
        object.__setattr__(self, "graphiti_write", GRAPHITI_WRITE)
        object.__setattr__(self, "neo4j_write", NEO4J_WRITE)
        object.__setattr__(self, "secrets_redacted", SECRETS_REDACTED)
        # Enforce excerpt length
        if len(self.external_output_excerpt) > EXCERPT_MAX_CHARS:
            object.__setattr__(
                self,
                "external_output_excerpt",
                self.external_output_excerpt[:EXCERPT_MAX_CHARS],
            )

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "ExternalComparisonReceipt":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ── Claude detection ──────────────────────────────────────────────────────────

def detect_claude_cli() -> tuple[bool, str, str]:
    """Detect whether a Claude CLI is available locally.

    Returns (available: bool, command: str, version_info: str).
    No network call is made.
    """
    if shutil.which("claude") is None:
        return False, "", "NOT_IN_PATH"

    for args in [["claude", "--version"], ["claude", "--help"]]:
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info = (result.stdout or result.stderr or "").strip()
                return True, "claude", info[:200]
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue

    return False, "", "DETECTION_FAILED"


# ── External run (network mode only) ─────────────────────────────────────────

def run_claude_cli(prompt: str, timeout: int = 60) -> dict:
    """Run 'claude -p <prompt>' and return a result dict.

    Only called when OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1.
    Never stores secrets. Output excerpt is capped at EXCERPT_MAX_CHARS.
    """
    import time

    start = time.perf_counter()
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        success = result.returncode == 0
        output = stdout if stdout else stderr
        return {
            "success": success,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": output[:EXCERPT_MAX_CHARS],
            "error": "" if success else f"exit_code={result.returncode}",
        }
    except subprocess.TimeoutExpired:
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": "",
            "error": "TIMEOUT",
        }
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": "",
            "error": f"EXCEPTION:{type(exc).__name__}",
        }


# ── Comparison helper ─────────────────────────────────────────────────────────

def compute_comparison(
    obsidia_cost: float,
    external_cost_per_1m: Optional[float],
) -> tuple[Optional[float], Optional[float], str]:
    """Return (savings_ratio, avoided_cost, cost_source)."""
    if external_cost_per_1m is None or external_cost_per_1m <= 0:
        return None, None, "USAGE_UNAVAILABLE"
    ratio = external_cost_per_1m / obsidia_cost
    avoided = external_cost_per_1m - obsidia_cost
    return ratio, avoided, "MEASURED"
