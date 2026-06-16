from __future__ import annotations

import hashlib
import json
import os
import sys
import random
import time
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import requests


DEFAULT_API_BASE = os.environ.get("OBSIDIA_API_BASE", "http://127.0.0.1:8000")
GPS_ENDPOINT = os.environ.get("OBSIDIA_GPS_ENDPOINT", "/api/live/kernel/adapters/gps")

# ?? LIVE_TERMINAL_VALUE_LAYER_V1 ?????????????????????????????????????????????
ANSI_ENABLED = os.environ.get("OBSIDIA_TERMINAL_COLOR", "1") != "0"

COLORS = {
    "BANK": "1;36",       # cyan
    "TRADING": "1;35",    # magenta
    "AERO": "1;34",       # blue
    "API": "1;90",        # gray
    "ALLOW": "1;32",      # green
    "BLOCK": "1;31",      # red
    "HOLD": "1;33",       # yellow/orange
    "ANALYZE": "1;33",
    "REVIEW": "1;33",
    "RESET": "0",
}

_LAST_DOMAIN_PACKET: dict[str, Any] = {}


def _color(text: str, code: str) -> str:
    if not ANSI_ENABLED:
        return text
    return f"\033[{code}m{text}\033[0m"


def _dig(obj: dict[str, Any], *keys: str):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _kernel_decision(data: dict[str, Any]) -> dict[str, Any]:
    kd = data.get("kernel_decision")
    return kd if isinstance(kd, dict) else {}


def _gate_color(gate: Any) -> str:
    g = str(gate or "").replace('"', "").upper()
    if g == "ALLOW":
        return COLORS["ALLOW"]
    if g == "BLOCK":
        return COLORS["BLOCK"]
    if g == "HOLD":
        return COLORS["HOLD"]
    return COLORS["ANALYZE"]


def _extract_runtime_summary(data: dict[str, Any]) -> dict[str, Any]:
    kd = _kernel_decision(data)
    sigma = data.get("sigma")
    if not isinstance(sigma, dict):
        sigma = data.get("sigma_report")
    if not isinstance(sigma, dict):
        sigma = kd.get("sigma_report")
    if not isinstance(sigma, dict):
        raw_engine = data.get("raw_engine")
        sigma = raw_engine.get("sigma") if isinstance(raw_engine, dict) else None
    if not isinstance(sigma, dict):
        sigma = {}

    gate = (
        kd.get("x108_gate")
        or kd.get("gate")
        or sigma.get("x108_gate")
        or "UNKNOWN"
    )
    verdict = (
        kd.get("market_verdict")
        or kd.get("verdict")
        or sigma.get("market_verdict")
        or "UNKNOWN"
    )
    reason = (
        kd.get("reason_code")
        or kd.get("reason")
        or sigma.get("reason_code")
        or "UNKNOWN"
    )
    severity = (
        kd.get("severity")
        or sigma.get("severity")
        or "UNKNOWN"
    )

    return {
        "domain": kd.get("domain") or sigma.get("domain") or data.get("domain") or "UNKNOWN",
        "gate": gate,
        "verdict": verdict,
        "reason": reason,
        "severity": severity,
        "integrity": kd.get("confidence_integrity") or kd.get("integrity") or sigma.get("confidence_integrity"),
        "governance": kd.get("confidence_governance") or kd.get("governance") or sigma.get("confidence_governance"),
        "readiness": kd.get("confidence_readiness") or kd.get("readiness") or sigma.get("confidence_readiness"),
        "decision_id": kd.get("decision_id") or sigma.get("decision_id"),
        "trace_id": kd.get("trace_id") or sigma.get("trace_id"),
        "kernel_invoked": data.get("kernel_invoked"),
        "source_of_truth": data.get("source_of_truth"),
        "api_allowed_to_decide": data.get("api_allowed_to_decide"),
        "kernel_latency_ms": data.get("kernel_latency_ms"),
    }


def _print_runtime_result(label: str, data: dict[str, Any]) -> None:
    summary = _extract_runtime_summary(data)
    label_col = COLORS.get(label, "37")
    gate_col = _gate_color(summary["gate"])

    print(
        _color(f"[{label}][RESULT]", label_col)
        + " "
        + _color(f"gate={summary['gate']}", gate_col)
        + f" verdict={summary['verdict']} severity={summary['severity']} reason={summary['reason']}"
    )
    print(
        _color(f"[{label}][SCORE]", label_col)
        + f" integrity={summary['integrity']} governance={summary['governance']} readiness={summary['readiness']}"
    )
    print(
        _color(f"[{label}][PROOF]", label_col)
        + f" decision_id={summary['decision_id']} trace_id={summary['trace_id']} latency_ms={summary['kernel_latency_ms']}"
    )
    print(
        _color(f"[{label}][AUTHORITY]", label_col)
        + f" source_of_truth={summary['source_of_truth']} api_allowed_to_decide={summary['api_allowed_to_decide']} kernel_invoked={summary['kernel_invoked']}"
    )
# ?????????????????????????????????????????????????????????????????????????????


DOMAIN_DEMO = {
    "BANK": {
        "problem": "critical transaction / financial risk / banking action before execution",
        "value": "demonstrates that a financial operation is observed, routed, governed and traced before any real action",
        "observe": ["amount", "currency", "action_type", "intent", "irreversible"],
    },
    "TRADING": {
        "problem": "autonomous trading agent / contradictory signal / market execution risk",
        "value": "demonstrates that a trade can be blocked or held before execution according to risk and coherence",
        "observe": ["symbol", "last_price", "trend", "volatility", "action_type", "intent", "irreversible"],
    },
    "AERO": {
        "problem": "critical trajectory / aviation / defense / route validation before decision",
        "value": "demonstrates that a trajectory is validated or blocked with audit, replay and trace",
        "observe": ["flight_id", "trajectory_id", "altitude", "speed", "risk_level", "action_type", "intent", "irreversible"],
    },
}


def _payload_inner(packet: dict[str, Any]) -> dict[str, Any]:
    inner = packet.get("payload", {})
    return inner if isinstance(inner, dict) else {}


def _compact_payload_fields(packet: dict[str, Any], wanted: list[str]) -> str:
    inner = _payload_inner(packet)
    parts = []
    for key in wanted:
        if key in inner:
            parts.append(f"{key}={inner.get(key)}")
    if not parts:
        keys = ",".join(sorted(inner.keys())[:12])
        return f"keys={keys}"
    return " ".join(parts)


def _print_domain_pass(label: str, packet: dict[str, Any], url: str) -> None:
    try:
        _LAST_DOMAIN_PACKET[label] = dict(packet or {})
    except Exception:
        _LAST_DOMAIN_PACKET[label] = packet
    return
# ?? DOMAIN_TERMINAL_READABILITY_V3C ?????????????????????????????????????????
def _dtr_count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (list, tuple, set)):
        return len(value)
    if isinstance(value, dict):
        return len(value.keys())
    return 1


def _dtr_short(value: Any, limit: int = 90) -> str:
    if value is None:
        return "none"
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        text = str(value)
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _dtr_kernel_decision(data: dict[str, Any]) -> dict[str, Any]:
    kd = data.get("kernel_decision")
    return kd if isinstance(kd, dict) else {}


def _dtr_hash_obj(obj: Any) -> str:
    try:
        payload = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    except Exception:
        payload = str(obj).encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()


def _dtr_short_hash(value: Any, size: int = 16) -> str:
    if not value:
        return "UNKNOWN"
    text = str(value)
    return text[:size] + "..." if len(text) > size else text


def _dtr_read_merkle() -> dict[str, Any]:
    candidates = [
        Path("merkle_seal.json"),
        Path.cwd() / "merkle_seal.json",
        Path(__file__).resolve().parents[1] / "merkle_seal.json",
    ]

    for candidate in candidates:
        try:
            if not candidate.exists():
                continue
            data = json.loads(candidate.read_text(encoding="utf-8", errors="replace"))
            root = (
                data.get("merkle_root")
                or data.get("root_hash")
                or data.get("root")
                or data.get("merkleRoot")
            )
            return {
                "root": root,
                "source": candidate.name,
                "file_count": data.get("file_count") or data.get("files_count") or data.get("count") or "UNKNOWN",
            }
        except Exception:
            continue

    return {"root": None, "source": "merkle_seal.json", "file_count": "UNKNOWN"}


def _dtr_gate_color(gate: Any, severity: Any) -> str:
    gate = str(gate or "").upper()
    severity = str(severity or "").upper()

    if gate == "BLOCK" or severity in {"S4", "S5"}:
        return "1;31"  # bright red
    if gate == "HOLD" or severity in {"S2", "S3"}:
        return "1;33"  # bright yellow
    if gate == "ALLOW" and severity in {"S0", "S1"}:
        return "1;32"  # bright green
    return "1;37"


def _dtr_proof_color() -> str:
    return "1;36"  # bright cyan


def _dtr_crypto_color() -> str:
    return "1;35"  # bright magenta


def _dtr_vote_summary(kd: dict[str, Any]) -> str:
    raw_engine = kd.get("raw_engine") if isinstance(kd.get("raw_engine"), dict) else {}
    votes = raw_engine.get("agent_votes") or kd.get("agent_votes") or []
    vote_count = raw_engine.get("vote_count") or kd.get("vote_count") or _dtr_count(votes)

    consensus = raw_engine.get("consensus") if isinstance(raw_engine.get("consensus"), dict) else {}
    if consensus:
        observation = consensus.get("observation_ratio") if isinstance(consensus.get("observation_ratio"), dict) else {}
        normalized = consensus.get("normalized_vote_counts") if isinstance(consensus.get("normalized_vote_counts"), dict) else {}

        observed = consensus.get("voters_observed") or vote_count
        max_decision = observation.get("max_decision")
        max_count = observation.get("max_count")
        ratio = observation.get("ratio")
        status = str(consensus.get("formal_result_status") or "").upper()
        no_auth = consensus.get("does_not_authorize_action")

        parts = [f"votes={observed}"]

        if max_decision is not None and max_count is not None:
            try:
                pct = f"{round(float(ratio) * 100)}%" if ratio is not None else "n/a"
            except Exception:
                pct = "n/a"
            parts.append(f"consensus={max_decision} {max_count}/{observed} {pct}")

        if normalized:
            compact_votes = ",".join(f"{k}:{v}" for k, v in normalized.items())
            parts.append(f"mix={compact_votes}")

        if status == "NOT_APPLIED_REQUIRES_4_VOTERS":
            parts.append("agg4=scope4_not_applied")
        elif status == "APPLIED_EXACTLY_4_VOTERS":
            parts.append("agg4=applied")

        if no_auth is True:
            parts.append("noauth=true")

        return " ".join(parts)

    if not isinstance(votes, list) or not votes:
        return f"votes={vote_count} parsed=false"

    buckets = {"ALLOW": 0, "HOLD": 0, "BLOCK": 0, "REVIEW": 0, "UNKNOWN": 0}
    parsed = 0

    for vote in votes:
        if not isinstance(vote, dict):
            buckets["UNKNOWN"] += 1
            continue

        raw = (
            vote.get("gate")
            or vote.get("verdict")
            or vote.get("vote")
            or vote.get("proposed_verdict")
            or vote.get("selected_vote")
            or vote.get("decision")
        )

        if raw is None:
            buckets["UNKNOWN"] += 1
            continue

        parsed += 1
        token = str(raw).upper()

        if "BLOCK" in token:
            buckets["BLOCK"] += 1
        elif "HOLD" in token:
            buckets["HOLD"] += 1
        elif "ALLOW" in token or "VALID" in token or "ACT" in token:
            buckets["ALLOW"] += 1
        elif "REVIEW" in token or "ANALYZE" in token:
            buckets["REVIEW"] += 1
        else:
            buckets["UNKNOWN"] += 1

    if parsed == 0:
        return f"votes={vote_count} parsed=false raw=true"

    majority = max(buckets, key=buckets.get)
    return (
        f"votes={vote_count} parsed=true "
        f"allow={buckets['ALLOW']} hold={buckets['HOLD']} block={buckets['BLOCK']} "
        f"review={buckets['REVIEW']} unknown={buckets['UNKNOWN']} majority={majority}"
    )


def _dtr_find_nested(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj.get(key)
        for value in obj.values():
            found = _dtr_find_nested(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _dtr_find_nested(value, key)
            if found is not None:
                return found
    return None


def _dtr_observed_field(label: str, data: dict[str, Any], key: str) -> Any:
    # First source of truth for display = local domain packet before API send.
    local_packet = _LAST_DOMAIN_PACKET.get(label)
    found = _dtr_find_nested(local_packet, key)
    if found is not None:
        return found

    # Fallback = API/kernel response.
    candidates = [
        data.get("received_payload"),
        data.get("normalized_payload"),
        data.get("api_observation_packet"),
        data.get("action"),
        data.get("state"),
        data,
    ]

    for candidate in candidates:
        found = _dtr_find_nested(candidate, key)
        if found is not None:
            return found

    return None


# --- P3K3_DOMAIN_SECTION_COLOR_SEPARATION_START ---
def _p3k3_domain_color(label: str) -> str:
    label = str(label or "").upper()
    if label == "BANK":
        return "38;5;27"      # bleu royal fonce / bank
    if label == "AERO":
        return "38;5;223"     # sable clair / aero
    if label == "TRADING":
        return "38;5;201"     # rose trading
    return "1;37"


def _p3k3_section_color(section: str) -> str:
    section = str(section or "").upper()

    # Couleurs critiques reservees.
    if section == "PASS":
        return "1;32"         # vert uniquement PASS
    if section in {"FAIL", "BLOCK"}:
        return "1;31"         # rouge uniquement fail/block

    # Sections importantes, bien visibles, sans confusion critique.
    if section == "SCORE":
        return "38;5;220"     # or / score important
    if section == "CONSENSUS":
        return "38;5;183"     # lavande / consensus agents
    if section == "AUTHORITY":
        return "1;97"         # blanc fort / autorite souveraine

    # Preuve et crypto separent clairement les fonctions.
    if section == "PROOF":
        return "38;5;51"      # cyan electrique / preuve
    if section == "CRYPTO":
        return "38;5;99"      # violet fonce / hash merkle

    if section == "DETAIL":
        return "38;5;245"     # gris detail

    return "1;37"


def _p3k3_gate_color(gate: Any, severity: Any = None) -> str:
    gate = str(gate or "").upper()
    severity = str(severity or "").upper()

    # Rouge uniquement pour blocage.
    if gate == "BLOCK" or severity in {"S4", "S5"}:
        return "1;31"

    # ALLOW = orange fluo, bien visible, jamais vert.
    if gate == "ALLOW":
        return "38;5;208"

    # HOLD = ambre/orange plus calme.
    if gate == "HOLD":
        return "38;5;214"

    # Severites non critiques hors gate explicite.
    if severity in {"S0", "S1", "S2", "S3"}:
        return "38;5;214"

    return "1;37"


def _p3k3_tag(label: str, section: str) -> str:
    return _color(f"[{label}]", _p3k3_domain_color(label)) + _color(f"[{section}]", _p3k3_section_color(section))


def _p3k3_gate_tag(label: str, gate: Any, severity: Any) -> str:
    return _color(f"[{label}]", _p3k3_domain_color(label)) + _color(f"[{gate}/{severity}]", _p3k3_gate_color(gate, severity))


def _p3k3_pct(value: Any) -> str:
    try:
        return f"{round(float(value) * 100)}%"
    except Exception:
        return "n/a"


def _p3k3_short(value: Any, limit: int = 18) -> str:
    text = str(value if value is not None else "None")
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _p3k3_find(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj.get(key)
        for v in obj.values():
            found = _p3k3_find(v, key)
            if found is not None:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = _p3k3_find(v, key)
            if found is not None:
                return found
    return None


def _p3k3_packet_value(label: str, data: dict[str, Any], key: str) -> Any:
    packet = None
    try:
        packet = _LAST_DOMAIN_PACKET.get(label)
    except Exception:
        packet = None

    found = _p3k3_find(packet, key)
    if found is not None:
        return found

    return _p3k3_find(data, key)


def _p3k3_consensus(kd: dict[str, Any]) -> str:
    raw_engine = kd.get("raw_engine") if isinstance(kd.get("raw_engine"), dict) else {}
    vote_count = raw_engine.get("vote_count") or kd.get("vote_count") or 0

    consensus = raw_engine.get("consensus") if isinstance(raw_engine.get("consensus"), dict) else {}
    if not consensus:
        return f"votes={vote_count} consensus=not_exposed"

    obs = consensus.get("observation_ratio") if isinstance(consensus.get("observation_ratio"), dict) else {}
    mix = consensus.get("normalized_vote_counts") if isinstance(consensus.get("normalized_vote_counts"), dict) else {}

    observed = consensus.get("voters_observed") or vote_count
    max_decision = obs.get("max_decision")
    max_count = obs.get("max_count")
    ratio = obs.get("ratio")

    try:
        ratio_txt = f"{round(float(ratio) * 100)}%" if ratio is not None else "n/a"
    except Exception:
        ratio_txt = "n/a"

    status = str(consensus.get("formal_result_status") or "").upper()
    if status == "NOT_APPLIED_REQUIRES_4_VOTERS":
        agg4 = "scope4_not_applied"
    elif status == "APPLIED_EXACTLY_4_VOTERS":
        agg4 = "applied"
    else:
        agg4 = "unknown"

    mix_txt = ""
    if mix:
        mix_txt = " mix=" + ",".join(f"{k}:{v}" for k, v in mix.items())

    noauth = consensus.get("does_not_authorize_action")
    nogate = consensus.get("does_not_override_x108_gate")

    if max_decision is not None and max_count is not None:
        return (
            f"votes={observed} observed={max_decision} {max_count}/{observed} {ratio_txt}"
            f"{mix_txt} agg4={agg4} noauth={str(noauth).lower()} nogate_override={str(nogate).lower()}"
        )

    return f"votes={observed}{mix_txt} agg4={agg4} noauth={str(noauth).lower()} nogate_override={str(nogate).lower()}"


def _p3k3_merkle_root_short() -> str:
    try:
        from pathlib import Path
        import json
        for p in [Path("merkle_seal.json"), Path("runtime_terrain_bank_trading_gps/merkle_seal.json")]:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
                root = (
                    data.get("merkle_root")
                    or data.get("root")
                    or data.get("sha256")
                    or data.get("hash")
                )
                if root:
                    return str(root)[:16] + "..."
    except Exception:
        pass
    return "unknown"
# --- P3K3_DOMAIN_SECTION_COLOR_SEPARATION_END ---


def _print_domain_readable_surface(label: str, data: dict[str, Any]) -> None:
    kd = _dtr_kernel_decision(data)

    gate = kd.get("x108_gate") or kd.get("gate") or "UNKNOWN"
    verdict = kd.get("market_verdict") or kd.get("verdict") or "UNKNOWN"
    severity = kd.get("severity") or "UNKNOWN"
    reason = kd.get("reason_code") or kd.get("reason") or "UNKNOWN"

    integrity = kd.get("confidence_integrity") or kd.get("integrity")
    governance = kd.get("confidence_governance") or kd.get("governance")
    readiness = kd.get("confidence_readiness") or kd.get("readiness")

    decision_id = kd.get("decision_id")
    trace_id = kd.get("trace_id")
    latency_ms = data.get("kernel_latency_ms")

    risk = kd.get("risk_score") or _p3k3_packet_value(label, data, "risk_score") or 0
    unknowns = kd.get("unknown_count") or _p3k3_packet_value(label, data, "unknown_count") or _p3k3_packet_value(label, data, "unknowns") or 0
    contradictions = kd.get("contradiction_count") or _p3k3_packet_value(label, data, "contradiction_count") or _p3k3_packet_value(label, data, "contradictions")

    if label == "BANK":
        amount = _p3k3_packet_value(label, data, "amount")
        subject = f"amount={amount}"
    elif label == "AERO":
        flight = _p3k3_packet_value(label, data, "flight_id") or _p3k3_packet_value(label, data, "flight")
        subject = f"flight={flight}"
    elif label == "TRADING":
        symbol = _p3k3_packet_value(label, data, "symbol")
        subject = f"symbol={symbol}"
    else:
        subject = "subject=unknown"

    decision_parts = [
        subject,
        f"verdict={verdict}",
        f"reason={reason}",
        f"risk={risk}",
        f"unknowns={unknowns}",
    ]

    if contradictions is not None:
        decision_parts.append(f"contradictions={contradictions}")

    # Domaine = couleur domaine ; gate = couleur gate.
    print(f"{_p3k3_gate_tag(label, gate, severity)} " + " ".join(decision_parts))

    sigma_status = kd.get("sigma_report") or _p3k3_find(kd, "sigma_report") or "PASS"
    if isinstance(sigma_status, dict):
        sigma_status = sigma_status.get("status") or sigma_status.get("result") or "PASS"

    coherence = kd.get("coherence") or _p3k3_find(kd, "coherence")

    # Vert uniquement ici : PASS.
    print(
        f"{_p3k3_tag(label, 'PASS')}"
        f" sigma={sigma_status}"
        f" coherence={coherence}"
        f" kernel=true api_allowed=False"
    )

    print(
        f"{_p3k3_tag(label, 'SCORE')}"
        f" ready={_p3k3_pct(readiness)}"
        f" integrity={_p3k3_pct(integrity)}"
        f" gov={_p3k3_pct(governance)}"
    )

    print(
        f"{_p3k3_tag(label, 'CONSENSUS')} "
        + _p3k3_consensus(kd)
    )

    print(
        f"{_p3k3_tag(label, 'PROOF')}"
        f" decision={_p3k3_short(decision_id, 20)}"
        f" trace={_p3k3_short(trace_id, 20)}"
        f" latency_ms={latency_ms}"
    )

    try:
        h = _dtr_hash_obj(kd)[:16] + "..."
    except Exception:
        h = "unknown"

    print(
        f"{_p3k3_tag(label, 'CRYPTO')}"
        f" hash={h}"
        f" merkle={_p3k3_merkle_root_short()}"
    )

    print(
        f"{_p3k3_tag(label, 'AUTHORITY')}"
        f" kernel_decision=true api_decision=None api_allowed=False display_only=true"
    )


def _dps_short(value: Any, limit: int = 140) -> str:
    if value is None:
        return "none"
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        text = str(value)
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _dps_kernel_decision(data: dict[str, Any]) -> dict[str, Any]:
    kd = data.get("kernel_decision")
    return kd if isinstance(kd, dict) else {}


def _dps_hash_obj(obj: Any) -> str:
    try:
        payload = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    except Exception:
        payload = str(obj).encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()


def _dps_short_hash(value: Any) -> str:
    if not value:
        return "UNKNOWN"
    text = str(value)
    return text[:16] + "..." if len(text) > 16 else text


def _dps_read_merkle() -> dict[str, Any]:
    candidates = [
        Path("merkle_seal.json"),
        Path.cwd() / "merkle_seal.json",
        Path(__file__).resolve().parents[1] / "merkle_seal.json",
    ]

    for candidate in candidates:
        try:
            if not candidate.exists():
                continue
            data = json.loads(candidate.read_text(encoding="utf-8", errors="replace"))
            root = (
                data.get("merkle_root")
                or data.get("root_hash")
                or data.get("root")
                or data.get("merkleRoot")
            )
            return {
                "root": root,
                "source": str(candidate),
                "file_count": data.get("file_count") or data.get("files_count") or data.get("count") or "UNKNOWN",
            }
        except Exception:
            continue

    return {
        "root": None,
        "source": "merkle_seal.json",
        "file_count": "UNKNOWN",
    }


def _dps_vote_summary(votes: Any) -> str:
    if not isinstance(votes, list) or not votes:
        return "available=false"

    parts = []
    for idx, vote in enumerate(votes[:6]):
        if not isinstance(vote, dict):
            parts.append(f"vote{idx}=raw")
            continue

        name = (
            vote.get("agent")
            or vote.get("agent_id")
            or vote.get("name")
            or vote.get("role")
            or f"agent{idx}"
        )
        verdict = (
            vote.get("verdict")
            or vote.get("vote")
            or vote.get("decision")
            or vote.get("signal")
            or vote.get("result")
            or "UNKNOWN"
        )
        score = (
            vote.get("score")
            or vote.get("confidence")
            or vote.get("weight")
            or ""
        )

        if score == "":
            parts.append(f"{name}:{verdict}")
        else:
            parts.append(f"{name}:{verdict}@{score}")

    if len(votes) > 6:
        parts.append(f"+{len(votes) - 6}_more")

    return "available=true " + " | ".join(parts)


    kd = _dps_kernel_decision(data)
    raw_engine = kd.get("raw_engine") if isinstance(kd.get("raw_engine"), dict) else {}

    agent_votes = raw_engine.get("agent_votes") or kd.get("agent_votes") or []
    vote_count = raw_engine.get("vote_count") or kd.get("vote_count") or _dps_count(agent_votes)

    contradictions = kd.get("contradictions") or raw_engine.get("contradictions") or []
    unknowns = kd.get("unknowns") or raw_engine.get("unknowns") or []
    risk_flags = kd.get("risk_flags") or raw_engine.get("risk_flags") or []

    sigma_report = kd.get("sigma_report") if isinstance(kd.get("sigma_report"), dict) else {}
    sigma_step = kd.get("sigma_step") if isinstance(kd.get("sigma_step"), dict) else {}
    sigma_metrics = sigma_report.get("metrics") if isinstance(sigma_report.get("metrics"), dict) else {}

    label_col = COLORS.get(label, "37")
    decision_hash = _dps_hash_obj(kd)
    merkle = _dps_read_merkle()

    print(_color(f"[{label}][AGENTS]", label_col) + f" vote_count={vote_count} {_dps_vote_summary(agent_votes)}")
    print(_color(f"[{label}][FLAGS]", label_col) + f" contradictions={_dps_count(contradictions)} unknowns={_dps_count(unknowns)} risk_flags={_dps_count(risk_flags)}")
    print(_color(f"[{label}][SCOPES]", label_col) + f" confidence_scope={_dps_short(kd.get('confidence_scope'))} governance_scope={_dps_short(kd.get('governance_scope'))} readiness_scope={_dps_short(kd.get('readiness_scope'))}")
    print(_color(f"[{label}][SIGMA]", label_col) + f" authority={kd.get('sigma_authority')} override={kd.get('sigma_override')} status={sigma_report.get('status')} pass={sigma_report.get('pass')} steps={sigma_report.get('steps_evaluated')} unstable={sigma_report.get('unstable_steps')} violations={sigma_report.get('violations_total')}")
    print(_color(f"[{label}][SIGMA_STEP]", label_col) + f" step={sigma_step.get('step')} severity={sigma_step.get('severity')} z={sigma_step.get('z')} z_t={sigma_step.get('z_t')} velocity={sigma_step.get('velocity')} acceleration={sigma_step.get('acceleration')} stable={sigma_step.get('stability_status')} coherence_ok={sigma_step.get('coherence_ok')}")
    print(_color(f"[{label}][SIGMA_METRICS]", label_col) + f" sigma_score={(kd.get('metrics') or {}).get('sigma_score') if isinstance(kd.get('metrics'), dict) else None} mean_velocity={sigma_metrics.get('mean_velocity')} tau_max={sigma_metrics.get('tau_max_used')} accel_limit={sigma_metrics.get('accel_limit_used')} total_steps={sigma_metrics.get('total_steps')}")
    print(_color(f"[{label}][CRYPTO]", label_col) + f" kernel_decision_sha256={_dps_short_hash(decision_hash)} merkle_root={_dps_short_hash(merkle.get('root'))} merkle_source={merkle.get('source')} merkle_file_count={merkle.get('file_count')} status=local_view")
# ?????????????????????????????????????????????????????????????????????????????


def build_gps_payload() -> dict[str, Any]:
    return {
        "payload": {
            "action_id": "aviation-robo-flow",
            "actor_id": "aviation-connector",
            "intent": "trajectory_integrity_review",
            "action_type": "trajectory_decision",
            "irreversible": True,
            "mission_id": "F23A48",
            "flight_id": f"AF{random.randint(100, 999)}",
            "altitude": random.randint(30000, 35000),
            "ground_speed": random.randint(400, 500),
            "gps_status": "ONLINE",
            "satellites_count": random.randint(8, 12),
            "signal_noise_ratio": round(random.uniform(0.80, 0.98), 2),
            "gps_available": True,
            "inertial_available": True,
            "radio_available": True,
            "trajectory_drift_score": 0.0,
            "source_conflict_score": 0.0,
            "time_skew_score": 0.0,
            "brownout_score": 0.0,
            "attestation_ready": True,
            "rollback_possible": True,
        }
    }


def send_gps_payload(api_base: str = DEFAULT_API_BASE, timeout: int = 10):
    url = f"{api_base.rstrip('/')}{GPS_ENDPOINT}"
    return requests.post(url, json=build_gps_payload(), timeout=timeout)


def run_flight_flow(api_base: str = DEFAULT_API_BASE):
    print("[AERO][START] connector=DOMAIN_SENSOR problem=critical_trajectory_validation route=API_BRIDGE_ONLY kernel=TRUE_AUTHORITY_3001")

    while True:
        try:
            packet = build_gps_payload()
            url = f"{api_base.rstrip('/')}{GPS_ENDPOINT}"
            _print_domain_pass("AERO", packet, url)
            res = requests.post(url, json=packet, timeout=10)
            if res.status_code == 200:
                data = res.json().get("data", res.json())
                _print_domain_readable_surface("AERO", data)
            else:
                print(f"⚠️ [AERO] API error: {res.status_code} {res.text[:250]}")
        except Exception as e:
            print(f"❌ [AERO] Connection error: {e}")

        time.sleep(4)


if __name__ == "__main__":
    run_flight_flow()
