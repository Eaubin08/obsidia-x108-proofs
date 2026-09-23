"""OIE V0.5 External Benchmark -- ExternalComparisonReceipt + providers SDK mesures.

Mesure comparative entre Obsidia et un provider externe (Claude Code / API / Gemini).
Non-souverain : readonly, emits_act=False, kernel_mutation=False.
Aucune cle API n'est jamais stockee. secrets_redacted=True toujours.

V0.2 : separation routing vs domain-output, estimation tokens locale.
V0.3 : metriques differentielles OIE, failure tracking, UTF-8 safe subprocess.
V0.4 : mode SDK Anthropic optionnel (OIE_EXTERNAL_PROVIDER=anthropic_sdk), usage mesure reel.
       La cle ANTHROPIC_API_KEY n'est jamais logguee ni ecrite dans les receipts.
V0.5 : mode SDK Gemini optionnel (OIE_EXTERNAL_PROVIDER=gemini_sdk), usage mesure reel.
       Les cles GEMINI_API_KEY / GOOGLE_API_KEY ne sont jamais logguees ni dans les receipts.
"""
from __future__ import annotations

import json
import math
import os
import re
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

# ── Known Obsidia route labels ────────────────────────────────────────────────
KNOWN_ROUTES: list[str] = [
    "FAST_PATH", "BRODY", "BANK", "TRADING", "GPS", "OBSIDURE",
]

# ── Classification error types ────────────────────────────────────────────────
ERROR_NONE = "NONE"
ERROR_ROUTE_MISMATCH = "ROUTE_MISMATCH"
ERROR_OVER_ROUTING = "OVER_ROUTING_TO_DOMAIN"
ERROR_UNDER_ROUTING = "UNDER_ROUTING_TO_FAST_PATH"
ERROR_AMBIGUOUS = "AMBIGUOUS_PROMPT"
ERROR_UNPARSEABLE = "UNPARSEABLE_OUTPUT"
ERROR_EXTERNAL = "EXTERNAL_ERROR"
ERROR_USAGE_ONLY = "USAGE_UNAVAILABLE_ONLY"

DOMAIN_ROUTES = {"BANK", "TRADING", "GPS"}

# ── Benchmark kind constants ──────────────────────────────────────────────────
BENCHMARK_KIND_ROUTING = "ROUTING"
BENCHMARK_KIND_DOMAIN_OUTPUT = "DOMAIN_OUTPUT"

# ── Domain-output error types ─────────────────────────────────────────────────
ERROR_LABEL_MISMATCH = "LABEL_MISMATCH"

# ── External failure types (V0.3) ─────────────────────────────────────────────
FAILURE_NONE = "NONE"
FAILURE_TIMEOUT = "TIMEOUT"
FAILURE_SESSION_LIMIT = "SESSION_LIMIT"
FAILURE_UNICODE_DECODE = "UNICODE_DECODE"
FAILURE_CLI_ERROR = "CLI_ERROR"
FAILURE_UNPARSEABLE = "UNPARSEABLE_OUTPUT"
FAILURE_PROVIDER_REFUSAL = "PROVIDER_REFUSAL"
FAILURE_SDK_NOT_AVAILABLE = "SDK_NOT_AVAILABLE"    # anthropic package absent
FAILURE_MODEL_NOT_CONFIGURED = "MODEL_NOT_CONFIGURED"  # OIE_EXTERNAL_MODEL_LABEL absent
FAILURE_GEMINI_SDK_NOT_AVAILABLE = "GEMINI_SDK_NOT_AVAILABLE"  # google-genai absent
FAILURE_GEMINI_API_ERROR = "GEMINI_API_ERROR"          # erreur API Gemini
FAILURE_GEMINI_AUTH_ERROR = "GEMINI_AUTH_ERROR"        # cle absente ou invalide
FAILURE_GEMINI_MODEL_NOT_CONFIGURED = "GEMINI_MODEL_NOT_CONFIGURED"  # modele absent

# ── Comparison status (V0.3) ──────────────────────────────────────────────────
COMPARISON_STATUS_OK = "OK"
COMPARISON_STATUS_ESTIMATED = "ESTIMATED_NOT_MEASURED"
COMPARISON_STATUS_UNAVAILABLE = "COST_UNAVAILABLE"
COMPARISON_STATUS_FAILED = "EXTERNAL_FAILED"

# ── Cost source values (V0.4 additions) ──────────────────────────────────────
COST_SOURCE_UNAVAILABLE = "USAGE_UNAVAILABLE"
COST_SOURCE_ESTIMATED = "ESTIMATED"
COST_SOURCE_SDK_NO_PRICE = "SDK_USAGE_MEASURED_NO_PRICE"
COST_SOURCE_SDK_MEASURED = "SDK_USAGE_MEASURED"

# ── Provider modes (V0.4 / V0.5) ─────────────────────────────────────────────
PROVIDER_CLI = "cli"
PROVIDER_SDK = "anthropic_sdk"
PROVIDER_GEMINI = "gemini_sdk"

# ── Comparison axes (V0.3) ────────────────────────────────────────────────────
AXIS_ROUTING = "ROUTING"
AXIS_DOMAIN_DECISION = "DOMAIN_DECISION"
AXIS_DOMAIN_OUTPUT = "DOMAIN_OUTPUT"
AXIS_CODE_PROOF = "CODE_PROOF"
AXIS_BRODY_RESPONSE = "BRODY_RESPONSE"
AXIS_FAST_PATH = "FAST_PATH"

_PROVIDER_REFUSAL_PHRASES = [
    "je ne peux pas", "i can't", "i cannot", "i'm unable",
    "i am unable", "je suis incapable", "je ne suis pas en mesure",
]


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
    external_output_excerpt: str = ""      # capped at EXCERPT_MAX_CHARS

    # ── External side — failure tracking (V0.3) ───────────────────────────────
    timeout_occurred: bool = False
    encoding_error_occurred: bool = False
    parser_error_occurred: bool = False
    external_failure_type: str = FAILURE_NONE

    # ── External side — usage ─────────────────────────────────────────────────
    external_usage_available: bool = False
    external_input_tokens: Optional[int] = None
    external_output_tokens: Optional[int] = None
    external_total_tokens: Optional[int] = None
    external_cost_eur: Optional[float] = None
    external_cost_eur_per_1m_estimate: Optional[float] = None
    external_model_label: str = ""
    external_cost_eur_measured: Optional[float] = None
    external_cost_eur_per_1m_measured: Optional[float] = None
    cost_source: str = COST_SOURCE_UNAVAILABLE

    # ── Benchmark kind ────────────────────────────────────────────────────────
    benchmark_kind: str = BENCHMARK_KIND_ROUTING   # ROUTING | DOMAIN_OUTPUT

    # ── Task metadata (V0.3) ──────────────────────────────────────────────────
    obsidia_model_call_required: bool = False
    external_model_call_required: bool = True
    obsidia_execution_layer: str = ""
    comparison_axis: str = ""

    # ── Quality / route evaluation (ROUTING) ──────────────────────────────────
    expected_route: str = ""
    external_detected_route: Optional[str] = None
    route_match: Optional[bool] = None
    expected_output_hint: str = ""
    quality_score: Optional[float] = None
    quality_notes: str = ""
    classification_error_type: str = ERROR_USAGE_ONLY
    retries_count: int = 0

    # ── Quality / label evaluation (DOMAIN_OUTPUT) ────────────────────────────
    expected_labels: Optional[List[str]] = None
    external_detected_label: Optional[str] = None
    label_match: Optional[bool] = None

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


# ── Route extraction ──────────────────────────────────────────────────────────

def extract_route_from_output(text: str) -> Optional[str]:
    """Detect an Obsidia route label in external output text.

    Handles: plain labels, "route: X", "Route retenue: X", backtick format `X`.
    Returns None if no clear route label is found.
    """
    if not text:
        return None

    text_upper = text.upper()

    # Priority 1: contextual label patterns (route: X, route retenue: X, primary route: X)
    ctx_pattern = re.compile(
        r'(?:ROUTE\s+RETENUE|PRIMARY\s+ROUTE|ROUTE\s+SELECTED|ROUTE)\s*[:\-]\s*([A-Z_]+)'
    )
    m = ctx_pattern.search(text_upper)
    if m:
        candidate = m.group(1).strip()
        if candidate in KNOWN_ROUTES:
            return candidate

    # Priority 2: backtick-quoted label  `TRADING`
    bt_pattern = re.compile(r'`([A-Z_]+)`')
    for m in bt_pattern.finditer(text_upper):
        candidate = m.group(1)
        if candidate in KNOWN_ROUTES:
            return candidate

    # Priority 3: plain word boundary match (longest first to avoid GPS ⊂ OBSIDURE)
    for route in sorted(KNOWN_ROUTES, key=len, reverse=True):
        # FAST_PATH: allow FAST_PATH or FAST PATH
        pattern = route.replace("_", "[_ ]?")
        if re.search(r'\b' + pattern + r'\b', text_upper):
            return route

    return None


# ── Route quality evaluator ───────────────────────────────────────────────────

def evaluate_route_quality(
    expected_route: str,
    external_output: str,
    external_success: bool,
) -> dict:
    """Evaluate whether the external output matches the expected Obsidia route.

    Returns a dict with:
        external_detected_route, route_match, quality_score,
        quality_notes, classification_error_type
    """
    if not external_success:
        return {
            "external_detected_route": None,
            "route_match": False,
            "quality_score": 0.0,
            "quality_notes": "External call failed",
            "classification_error_type": ERROR_EXTERNAL,
        }

    detected = extract_route_from_output(external_output)

    if detected is None:
        return {
            "external_detected_route": None,
            "route_match": False,
            "quality_score": 0.0,
            "quality_notes": "No route label found in output",
            "classification_error_type": ERROR_UNPARSEABLE,
        }

    match = detected == expected_route

    if match:
        return {
            "external_detected_route": detected,
            "route_match": True,
            "quality_score": 1.0,
            "quality_notes": f"Correct: {detected}",
            "classification_error_type": ERROR_NONE,
        }

    # Mismatch — classify the error type
    if expected_route == "FAST_PATH" and detected in DOMAIN_ROUTES:
        err = ERROR_OVER_ROUTING
        note = f"Expected FAST_PATH, got domain route {detected}"
        score = 0.0
    elif expected_route in DOMAIN_ROUTES | {"OBSIDURE"} and detected == "FAST_PATH":
        err = ERROR_UNDER_ROUTING
        note = f"Expected {expected_route}, got FAST_PATH (under-routing)"
        score = 0.2
    else:
        err = ERROR_ROUTE_MISMATCH
        note = f"Expected {expected_route}, got {detected}"
        score = 0.3

    return {
        "external_detected_route": detected,
        "route_match": False,
        "quality_score": score,
        "quality_notes": note,
        "classification_error_type": err,
    }


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
    UTF-8 forced with errors=replace to survive cp1252 / binary output.
    """
    import time

    start = time.perf_counter()
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        success = result.returncode == 0
        output = stdout if stdout else stderr
        encoding_warning = "�" in output  # replacement char = encoding issue
        error_str = "" if success else f"exit_code={result.returncode}"
        failure_type = detect_failure_type(error_str, output)
        return {
            "success": success,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": output[:EXCERPT_MAX_CHARS],
            "error": error_str,
            "timeout_occurred": False,
            "encoding_error_occurred": encoding_warning,
            "failure_type": failure_type,
        }
    except subprocess.TimeoutExpired:
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": "",
            "error": "TIMEOUT",
            "timeout_occurred": True,
            "encoding_error_occurred": False,
            "failure_type": FAILURE_TIMEOUT,
        }
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        error_str = f"EXCEPTION:{type(exc).__name__}"
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": "",
            "error": error_str,
            "timeout_occurred": False,
            "encoding_error_occurred": False,
            "failure_type": detect_failure_type(error_str, ""),
        }


# ── Anthropic SDK runner (V0.4, network mode only) ───────────────────────────

def run_anthropic_sdk(prompt: str, model: str, timeout: int = 60) -> dict:
    """Call Anthropic SDK messages.create and return a result dict with real usage.

    Only called when OIE_EXTERNAL_PROVIDER=anthropic_sdk AND
    OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1.

    Security:
    - API key read exclusively from ANTHROPIC_API_KEY env var.
    - Key is NEVER logged, printed, or included in the returned dict.
    - If key absent: returns controlled failure without crashing.

    Returns the same shape as run_claude_cli() plus usage fields.
    """
    import time

    start = time.perf_counter()

    # Guard: model must be configured
    if not model:
        return {
            "success": False,
            "latency_ms": 0.0,
            "output_excerpt": "",
            "error": "MODEL_NOT_CONFIGURED",
            "timeout_occurred": False,
            "encoding_error_occurred": False,
            "failure_type": FAILURE_MODEL_NOT_CONFIGURED,
            "usage_available": False,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "model_label": model,
        }

    # Guard: package must be installed
    try:
        import anthropic as _anthropic_pkg
    except ImportError:
        return {
            "success": False,
            "latency_ms": 0.0,
            "output_excerpt": "",
            "error": "SDK_NOT_AVAILABLE: pip install anthropic",
            "timeout_occurred": False,
            "encoding_error_occurred": False,
            "failure_type": FAILURE_SDK_NOT_AVAILABLE,
            "usage_available": False,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "model_label": model,
        }

    # Guard: key must be present (never logged)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {
            "success": False,
            "latency_ms": 0.0,
            "output_excerpt": "",
            "error": "ANTHROPIC_API_KEY not set",
            "timeout_occurred": False,
            "encoding_error_occurred": False,
            "failure_type": FAILURE_CLI_ERROR,
            "usage_available": False,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "model_label": model,
        }

    try:
        client = _anthropic_pkg.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
            timeout=timeout,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        raw_text = response.content[0].text if response.content else ""
        encoding_warning = "�" in raw_text
        input_tok = getattr(response.usage, "input_tokens", None)
        output_tok = getattr(response.usage, "output_tokens", None)
        total_tok = (input_tok + output_tok) if (input_tok is not None and output_tok is not None) else None
        usage_ok = input_tok is not None and output_tok is not None

        return {
            "success": True,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": raw_text[:EXCERPT_MAX_CHARS],
            "error": "",
            "timeout_occurred": False,
            "encoding_error_occurred": encoding_warning,
            "failure_type": FAILURE_NONE,
            "usage_available": usage_ok,
            "input_tokens": input_tok,
            "output_tokens": output_tok,
            "total_tokens": total_tok,
            "model_label": model,
        }

    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        err_str = f"EXCEPTION:{type(exc).__name__}"
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": "",
            "error": err_str,
            "timeout_occurred": "Timeout" in type(exc).__name__,
            "encoding_error_occurred": False,
            "failure_type": detect_failure_type(err_str, ""),
            "usage_available": False,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "model_label": model,
        }


# ── Secret sanitization (V0.5) ───────────────────────────────────────────────

_SECRET_PATTERNS = [
    re.compile(r'AIza[0-9A-Za-z_\-]{35}', re.IGNORECASE),  # Google/Gemini API key pattern
    re.compile(r'sk-ant-[0-9A-Za-z_\-]{20,}', re.IGNORECASE),  # Anthropic key pattern
]

def sanitize_external_error_message(msg: str) -> str:
    """Mask any API key patterns that could appear in error strings.

    Masks: AIza... (Google/Gemini), sk-ant-... (Anthropic).
    Also masks runtime values of GEMINI_API_KEY and GOOGLE_API_KEY from env.
    Never raises. Returns sanitized string.
    """
    if not msg:
        return msg
    result = msg
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    # Also mask literal env values if accidentally present
    for env_var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"):
        val = os.environ.get(env_var, "")
        if val and len(val) > 8 and val in result:
            result = result.replace(val, "[REDACTED]")
    return result


# ── Gemini SDK runner (V0.5, network mode only) ───────────────────────────────

def run_gemini_sdk(prompt: str, model: str, timeout: int = 60) -> dict:
    """Call Gemini API via google-genai SDK and return a result dict with real usage.

    Only called when OIE_EXTERNAL_PROVIDER=gemini_sdk AND
    OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1.

    Security:
    - API key read exclusively from GEMINI_API_KEY or GOOGLE_API_KEY env vars.
    - Key is NEVER logged, printed, or included in the returned dict.
    - Error messages are sanitized via sanitize_external_error_message().
    - If key absent: returns controlled failure without crashing.

    Returns the same shape as run_anthropic_sdk().
    """
    import time

    start = time.perf_counter()

    _fail_shape: dict = {
        "success": False,
        "latency_ms": 0.0,
        "output_excerpt": "",
        "error": "",
        "timeout_occurred": False,
        "encoding_error_occurred": False,
        "failure_type": FAILURE_NONE,
        "usage_available": False,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "model_label": model,
    }

    # Guard: model must be configured
    if not model:
        return {**_fail_shape, "error": "GEMINI_MODEL_NOT_CONFIGURED", "failure_type": FAILURE_GEMINI_MODEL_NOT_CONFIGURED}

    # Guard: package must be installed
    try:
        from google import genai as _genai_pkg
    except ImportError:
        return {**_fail_shape, "error": "GEMINI_SDK_NOT_AVAILABLE: pip install google-genai", "failure_type": FAILURE_GEMINI_SDK_NOT_AVAILABLE}

    # Guard: key must be present (never logged)
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if not api_key:
        return {**_fail_shape, "error": "GEMINI_API_KEY or GOOGLE_API_KEY not set", "failure_type": FAILURE_GEMINI_AUTH_ERROR}

    try:
        client = _genai_pkg.Client(api_key=api_key)
        interaction = client.interactions.create(
            model=model,
            input=prompt,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        # Extract output text — primary field, fallback via steps
        raw_text = ""
        if hasattr(interaction, "output_text") and interaction.output_text:
            raw_text = interaction.output_text
        elif hasattr(interaction, "steps"):
            for step in (interaction.steps or []):
                candidate = getattr(step, "output_text", None) or getattr(step, "text", None) or ""
                if candidate:
                    raw_text = candidate
                    break

        encoding_warning = "?" in raw_text and "�" in raw_text

        # Extract usage tokens
        usage = getattr(interaction, "usage", None)
        input_tok = getattr(usage, "total_input_tokens", None) if usage else None
        output_tok = getattr(usage, "total_output_tokens", None) if usage else None
        total_tok = getattr(usage, "total_tokens", None) if usage else None
        if total_tok is None and input_tok is not None and output_tok is not None:
            total_tok = input_tok + output_tok
        usage_ok = input_tok is not None and output_tok is not None

        return {
            "success": True,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": raw_text[:EXCERPT_MAX_CHARS],
            "error": "",
            "timeout_occurred": False,
            "encoding_error_occurred": encoding_warning,
            "failure_type": FAILURE_NONE,
            "usage_available": usage_ok,
            "input_tokens": input_tok,
            "output_tokens": output_tok,
            "total_tokens": total_tok,
            "model_label": model,
        }

    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        raw_err = f"EXCEPTION:{type(exc).__name__}:{exc}"
        err_str = sanitize_external_error_message(raw_err)
        timeout_hit = "Timeout" in type(exc).__name__ or "timeout" in str(exc).lower()
        failure = FAILURE_TIMEOUT if timeout_hit else FAILURE_GEMINI_API_ERROR
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "output_excerpt": "",
            "error": err_str,
            "timeout_occurred": timeout_hit,
            "encoding_error_occurred": False,
            "failure_type": failure,
            "usage_available": False,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "model_label": model,
        }


# ── Measured SDK cost (V0.4) ──────────────────────────────────────────────────

def compute_measured_sdk_cost(
    input_tokens: int,
    output_tokens: int,
    input_cost_per_1m: Optional[float],
    output_cost_per_1m: Optional[float],
) -> dict:
    """Compute real cost from SDK-measured token counts and optional price rates.

    Prices come from caller (env OIE_EXTERNAL_INPUT_COST_PER_1M /
    OIE_EXTERNAL_OUTPUT_COST_PER_1M). Never hardcoded here.

    cost_source:
        SDK_USAGE_MEASURED_NO_PRICE — tokens known, prices absent
        SDK_USAGE_MEASURED          — tokens + prices known, cost computed
    """
    total_tokens = input_tokens + output_tokens

    if input_cost_per_1m is None or output_cost_per_1m is None:
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "measured_cost_eur": None,
            "measured_cost_eur_per_1m": None,
            "cost_source": COST_SOURCE_SDK_NO_PRICE,
        }

    input_cost = input_tokens * input_cost_per_1m / 1_000_000
    output_cost = output_tokens * output_cost_per_1m / 1_000_000
    measured_cost_eur = input_cost + output_cost
    measured_cost_eur_per_1m = (
        measured_cost_eur * 1_000_000 / total_tokens
        if total_tokens > 0 else None
    )

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "measured_cost_eur": measured_cost_eur,
        "measured_cost_eur_per_1m": measured_cost_eur_per_1m,
        "cost_source": COST_SOURCE_SDK_MEASURED,
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


# ── Domain-output extractor ───────────────────────────────────────────────────

def extract_domain_output_label(text: str, allowed_labels: List[str]) -> Optional[str]:
    """Detect a domain-output label (e.g. ALLOW, HOLD, VALID) in external output text.

    Matches longest label first to avoid partial overlap.
    Returns None if no allowed label is found.
    """
    if not text or not allowed_labels:
        return None
    text_upper = text.upper()
    for label in sorted(allowed_labels, key=len, reverse=True):
        if re.search(r'\b' + re.escape(label.upper()) + r'\b', text_upper):
            return label.upper()
    return None


# ── Domain-output quality evaluator ──────────────────────────────────────────

def evaluate_domain_output_quality(
    expected_labels: List[str],
    external_output: str,
    external_success: bool,
) -> dict:
    """Evaluate whether the external output matches one of the expected domain labels.

    Returns a dict with:
        external_detected_label, label_match, quality_score,
        quality_notes, classification_error_type
    """
    if not external_success:
        return {
            "external_detected_label": None,
            "label_match": False,
            "quality_score": 0.0,
            "quality_notes": "External call failed",
            "classification_error_type": ERROR_EXTERNAL,
        }

    detected = extract_domain_output_label(external_output, expected_labels)

    if detected is None:
        # Try detecting any known-ish label even outside expected_labels
        return {
            "external_detected_label": None,
            "label_match": False,
            "quality_score": 0.0,
            "quality_notes": "No domain label found in output",
            "classification_error_type": ERROR_UNPARSEABLE,
        }

    if detected in [lbl.upper() for lbl in expected_labels]:
        return {
            "external_detected_label": detected,
            "label_match": True,
            "quality_score": 1.0,
            "quality_notes": f"Correct label: {detected}",
            "classification_error_type": ERROR_NONE,
        }

    return {
        "external_detected_label": detected,
        "label_match": False,
        "quality_score": 0.3,
        "quality_notes": f"Label {detected} not in expected {expected_labels}",
        "classification_error_type": ERROR_LABEL_MISMATCH,
    }


# ── Token estimation (local, no network) ─────────────────────────────────────

def estimate_tokens_from_text(text: str) -> int:
    """Rough token count estimate: ceil(len(text) / 4).

    Source: CHAR_ESTIMATE. Never presented as a real token count.
    """
    return math.ceil(len(text) / 4)


def detect_failure_type(error_str: str, output_str: str) -> str:
    """Classify the failure mode from error and output strings.

    Returns one of the FAILURE_* constants. Never raises.
    """
    combined = (error_str + " " + output_str).lower()
    if "timeout" in error_str.lower():
        return FAILURE_TIMEOUT
    if "session limit" in combined or "session_limit" in combined:
        return FAILURE_SESSION_LIMIT
    if "�" in output_str or "unicodedecodeerror" in combined or "unicode_decode" in error_str.lower():
        return FAILURE_UNICODE_DECODE
    if any(p in combined for p in _PROVIDER_REFUSAL_PHRASES):
        return FAILURE_PROVIDER_REFUSAL
    if error_str.startswith("exit_code") or error_str.startswith("EXCEPTION"):
        return FAILURE_CLI_ERROR
    return FAILURE_NONE


# ── OIE differential metrics (V0.3) ──────────────────────────────────────────

def compute_oie_differential_metrics(
    obsidia_cost_eur_per_1m: float,
    obsidia_latency_ms: float,
    external_latency_ms: Optional[float],
    external_success: bool,
    quality_score: Optional[float],
    cost_source: str,
    estimated_cost_eur_per_1m: Optional[float] = None,
    external_cost_eur_per_1m_measured: Optional[float] = None,
    external_model_call_required: bool = True,
    obsidia_model_call_required: bool = False,
) -> dict:
    """Compute OIE differential metrics: cost avoided, latency avoided, model-call avoided.

    comparison_status values:
        OK                   — measured cost available, comparison valid
        ESTIMATED_NOT_MEASURED — estimated cost only, not final
        COST_UNAVAILABLE     — no cost data at all
        EXTERNAL_FAILED      — external call failed, comparison meaningless

    Rules:
        quality_penalty = 1.0 - quality_score when quality_score is not None
        model_call_avoided = external_model_call_required AND NOT obsidia_model_call_required
        avoided_latency_ms = None when external_latency_ms is None
    """
    if not external_success:
        return {
            "obsidia_cost_eur_per_1m": obsidia_cost_eur_per_1m,
            "external_cost_eur_per_1m": None,
            "external_cost_available": False,
            "cost_source": cost_source,
            "avoided_cost_eur_per_1m": None,
            "savings_ratio": None,
            "obsidia_latency_ms": obsidia_latency_ms,
            "external_latency_ms": None,
            "avoided_latency_ms": None,
            "latency_ratio": None,
            "obsidia_model_call_required": obsidia_model_call_required,
            "external_model_call_required": external_model_call_required,
            "model_call_avoided": external_model_call_required and not obsidia_model_call_required,
            "quality_score": quality_score,
            "quality_penalty": (1.0 - quality_score) if quality_score is not None else None,
            "comparison_status": COMPARISON_STATUS_FAILED,
        }

    # Resolve external cost
    external_cost = external_cost_eur_per_1m_measured or estimated_cost_eur_per_1m
    external_cost_available = external_cost is not None and external_cost > 0

    if cost_source == "USAGE_UNAVAILABLE" or not external_cost_available:
        comparison_status = COMPARISON_STATUS_UNAVAILABLE
    elif cost_source == "ESTIMATED":
        comparison_status = COMPARISON_STATUS_ESTIMATED
    else:
        comparison_status = COMPARISON_STATUS_OK

    avoided_cost = (external_cost - obsidia_cost_eur_per_1m) if external_cost_available else None
    savings_ratio = (external_cost / obsidia_cost_eur_per_1m) if external_cost_available and obsidia_cost_eur_per_1m > 0 else None

    avoided_latency = (external_latency_ms - obsidia_latency_ms) if external_latency_ms is not None else None
    latency_ratio = (external_latency_ms / obsidia_latency_ms) if external_latency_ms is not None and obsidia_latency_ms > 0 else None

    return {
        "obsidia_cost_eur_per_1m": obsidia_cost_eur_per_1m,
        "external_cost_eur_per_1m": external_cost,
        "external_cost_available": external_cost_available,
        "cost_source": cost_source,
        "avoided_cost_eur_per_1m": avoided_cost,
        "savings_ratio": savings_ratio,
        "obsidia_latency_ms": obsidia_latency_ms,
        "external_latency_ms": external_latency_ms,
        "avoided_latency_ms": avoided_latency,
        "latency_ratio": latency_ratio,
        "obsidia_model_call_required": obsidia_model_call_required,
        "external_model_call_required": external_model_call_required,
        "model_call_avoided": external_model_call_required and not obsidia_model_call_required,
        "quality_score": quality_score,
        "quality_penalty": (1.0 - quality_score) if quality_score is not None else None,
        "comparison_status": comparison_status,
    }


def compute_estimated_external_cost(
    input_text: str,
    output_text: str,
    input_cost_per_1m: Optional[float],
    output_cost_per_1m: Optional[float],
) -> dict:
    """Estimate external cost from text lengths and optional price rates.

    Prices come from caller (env vars OIE_EXTERNAL_INPUT_COST_PER_1M /
    OIE_EXTERNAL_OUTPUT_COST_PER_1M). Never hardcoded here.

    Returns dict with token estimates and cost fields.
    cost_source = ESTIMATED when prices are provided, USAGE_UNAVAILABLE otherwise.
    """
    input_tokens = estimate_tokens_from_text(input_text)
    output_tokens = estimate_tokens_from_text(output_text)
    total_tokens = input_tokens + output_tokens

    if input_cost_per_1m is None or output_cost_per_1m is None:
        return {
            "input_tokens_estimated": input_tokens,
            "output_tokens_estimated": output_tokens,
            "total_tokens_estimated": total_tokens,
            "estimated_cost_eur": None,
            "estimated_cost_eur_per_1m": None,
            "cost_source": "USAGE_UNAVAILABLE",
        }

    estimated_cost_eur = (
        input_tokens * input_cost_per_1m / 1_000_000
        + output_tokens * output_cost_per_1m / 1_000_000
    )
    estimated_cost_eur_per_1m = (
        estimated_cost_eur * 1_000_000 / total_tokens
        if total_tokens > 0 else None
    )

    return {
        "input_tokens_estimated": input_tokens,
        "output_tokens_estimated": output_tokens,
        "total_tokens_estimated": total_tokens,
        "estimated_cost_eur": estimated_cost_eur,
        "estimated_cost_eur_per_1m": estimated_cost_eur_per_1m,
        "cost_source": "ESTIMATED",
    }
