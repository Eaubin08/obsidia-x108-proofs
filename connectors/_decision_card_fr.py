from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, Tuple

ANSI = {
    "reset": "\033[0m",
    "dim": "\033[38;5;245m",
    "line": "\033[38;5;240m",
    "aero": "\033[38;5;223m",
    "bank": "\033[38;5;27m",
    "trading": "\033[38;5;201m",
    "allow": "\033[38;5;208m",
    "block": "\033[1;31m",
    "hold": "\033[38;5;214m",
    "score": "\033[38;5;220m",
    "proof": "\033[38;5;51m",
    "crypto": "\033[38;5;99m",
    "auth": "\033[1;97m",
    "audit": "\033[38;5;183m",
}

def _col(name: str, text: Any) -> str:
    return ANSI.get(name, "") + str(text) + ANSI["reset"]

def _find_key(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = _find_key(v, key, None)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for item in obj:
            r = _find_key(item, key, None)
            if r is not None:
                return r
    return default

def _pct(v: Any) -> str:
    if v is None:
        return "non_expose"
    try:
        f = float(v)
        if 0 <= f <= 1:
            return f"{round(f * 100)}%"
        return f"{round(f)}%"
    except Exception:
        return str(v)

def _short(v: Any, n: int = 24) -> str:
    if v is None or v == "":
        return "non_expose"
    s = str(v)
    return s if len(s) <= n else s[:n] + "..."

def _as_list(v: Any) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]

def _domain_label(domain: str) -> Tuple[str, str, str]:
    if domain == "gps_defense_aviation":
        return "AERO", "Securite trajectoire / aviation", "aero"
    if domain == "bank":
        return "BANQUE", "Paiement / operation financiere", "bank"
    if domain == "trading":
        return "TRADING", "Marche / decision de trading", "trading"
    return str(domain).upper(), str(domain), "dim"

def _gate_label(gate: Any, verdict: Any) -> Tuple[str, str, str]:
    g = str(gate).upper()
    v = str(verdict).upper()

    if g == "ALLOW" and v == "TRAJECTORY_VALID":
        return "AUTORISE", "La trajectoire est valide selon X108.", "allow"
    if g == "ALLOW" and v == "ANALYZE":
        return "AUTORISE + ANALYSE", "L'action passe, mais reste en zone prudente.", "allow"
    if g == "BLOCK":
        return "BLOQUE", "Le moteur refuse l'action dans l'etat actuel.", "block"
    if g == "HOLD":
        return "EN ATTENTE", "Le moteur temporise avant action.", "hold"
    return g, v, "dim"

def _severity_label(s: Any) -> str:
    s = str(s).upper()
    return {
        "S0": "S0 normal / faible risque",
        "S1": "S1 prudence / analyse",
        "S2": "S2 attention",
        "S3": "S3 risque fort",
        "S4": "S4 blocage critique",
    }.get(s, s)

def _cause_label(domain: Any, gate: Any, verdict: Any, reason: Any) -> str:
    domain = str(domain)
    g = str(gate).upper()
    r = str(reason)

    if domain == "gps_defense_aviation" and g == "ALLOW":
        return "Aucun signal bloquant detecte sur la trajectoire."
    if domain == "bank" and g == "ALLOW":
        return "Operation autorisee par X108, mais classee en analyse prudente."
    if domain == "trading" and g == "BLOCK":
        return "Contradictions marche detectees : action bloquee."
    if r == "GUARD_ALLOW":
        return "Le garde X108 autorise cette decision."
    if r == "CONTRADICTION_THRESHOLD_REACHED":
        return "Trop de contradictions detectees : blocage."
    if "aggregate4 proof scope" in r:
        return "Cause metier non exposee directement ; voir Audit agg4."
    return r

def _bool_fr(v: Any) -> str:
    if v is True:
        return "oui"
    if v is False:
        return "non"
    if v is None:
        return "non_expose"
    return str(v)

def _extract(data: Dict[str, Any]) -> Dict[str, Any]:
    env = data.get("domain_sigma_envelope") if isinstance(data, dict) else None
    if not isinstance(env, dict):
        env = data if isinstance(data, dict) else {}

    raw = env.get("raw_engine") or data.get("raw_engine") or {}
    consensus = raw.get("consensus") if isinstance(raw, dict) else {}
    if not isinstance(consensus, dict):
        consensus = {}

    obs = consensus.get("observation_ratio")
    if not isinstance(obs, dict):
        obs = {}

    domain = env.get("domain") or data.get("domain") or _find_key(data, "domain", "non_expose")
    gate = env.get("x108_gate") or data.get("x108_gate") or _find_key(data, "x108_gate", "non_expose")
    verdict = env.get("market_verdict") or data.get("market_verdict") or _find_key(data, "market_verdict", "non_expose")
    severity = env.get("severity") or data.get("severity") or _find_key(data, "severity", "non_expose")

    reason = (
        env.get("x108_reason")
        or data.get("x108_reason")
        or env.get("reason")
        or data.get("reason")
        or "non_expose"
    )

    ready = env.get("confidence_readiness") or data.get("confidence_readiness") or _find_key(data, "confidence_readiness", None)
    integrity = env.get("confidence_integrity") or data.get("confidence_integrity") or _find_key(data, "confidence_integrity", None)
    governance = env.get("confidence_governance") or data.get("confidence_governance") or _find_key(data, "confidence_governance", None)

    decision_id = env.get("decision_id") or data.get("decision_id") or _find_key(data, "decision_id", None)
    trace_id = env.get("trace_id") or data.get("trace_id") or _find_key(data, "trace_id", None)
    latency = env.get("latency_ms") or data.get("latency_ms") or _find_key(data, "latency_ms", None)

    h = env.get("decision_hash") or data.get("decision_hash") or env.get("hash") or data.get("hash") or _find_key(data, "decision_hash", None)
    merkle = env.get("merkle_root") or data.get("merkle_root") or env.get("merkle") or data.get("merkle") or _find_key(data, "merkle_root", None)

    risk = env.get("risk") or data.get("risk") or _find_key(data, "risk", 0)
    unknowns = _as_list(env.get("unknowns") or data.get("unknowns") or _find_key(data, "unknowns", []))
    contradictions = _as_list(env.get("contradictions") or data.get("contradictions") or _find_key(data, "contradictions", []))

    amount = env.get("amount") or data.get("amount") or _find_key(data, "amount", None)
    flight = env.get("flight") or data.get("flight") or _find_key(data, "flight", None)
    symbol = env.get("symbol") or data.get("symbol") or _find_key(data, "symbol", None)

    vote_count = raw.get("vote_count") if isinstance(raw, dict) else None
    observed = obs.get("max_decision") or obs.get("observed") or "non_expose"
    ratio = obs.get("ratio")
    total = obs.get("total") or vote_count or "non_expose"
    count = obs.get("count") or obs.get("supporting_votes") or "non_expose"

    agent_details = raw.get("agent_vote_details") if isinstance(raw, dict) else []
    votes = []
    if isinstance(agent_details, list):
        for item in agent_details:
            if isinstance(item, dict):
                votes.append(str(item.get("vote") or item.get("decision") or "?"))

    legacy_tokens = {"bank", "trading", "gps_defense_aviation"}
    if votes and set(votes).issubset(legacy_tokens):
        mix = f"details_legacy_non_decodes | total={len(votes)}"
    elif votes:
        mix = ",".join([f"{k}:{v}" for k, v in Counter(votes).items()])
    else:
        mix = "non_expose"

    return {
        "domain": domain,
        "gate": gate,
        "verdict": verdict,
        "severity": severity,
        "reason": reason,
        "ready": ready,
        "integrity": integrity,
        "governance": governance,
        "decision_id": decision_id,
        "trace_id": trace_id,
        "latency": latency,
        "hash": h,
        "merkle": merkle,
        "risk": risk,
        "unknowns": unknowns,
        "contradictions": contradictions,
        "amount": amount,
        "flight": flight,
        "symbol": symbol,
        "observed": observed,
        "ratio": ratio,
        "count": count,
        "total": total,
        "mix": mix,
        "agg4": consensus.get("formal_result_status", "non_expose"),
        "noauth": consensus.get("does_not_authorize_action", None),
        "nogate": consensus.get("does_not_override_x108_gate", None),
        "kernel_decision": env.get("kernel_decision", data.get("kernel_decision", True)),
        "api_allowed": env.get("api_allowed", data.get("api_allowed", False)),
        "display_only": obs.get("display_only", True),
    }

def format_decision_card_fr(data: Dict[str, Any]) -> str:
    x = _extract(data)
    label, desc, dcolor = _domain_label(x["domain"])
    decision, reading, gcolor = _gate_label(x["gate"], x["verdict"])

    context = []
    if x["flight"] is not None:
        context.append(f"vol={x['flight']}")
    if x["amount"] is not None:
        context.append(f"montant={x['amount']}")
    if x["symbol"] is not None:
        context.append(f"actif={x['symbol']}")
    context_txt = " | ".join(context) if context else "non_expose_json"

    unknowns = x["unknowns"]
    contradictions = x["contradictions"]
    unknown_txt = "aucune" if len(unknowns) == 0 else ", ".join(map(str, unknowns))

    if len(contradictions) == 0:
        contradiction_txt = "aucune"
    else:
        counts = Counter(map(str, contradictions))
        contradiction_txt = ", ".join([f"{k} x{v}" if v > 1 else k for k, v in counts.items()])

    sep = "-" * 78
    lines = [
        _col("line", sep),
        f"{_col(dcolor, label)} | {_col(gcolor, decision)} | {x['severity']} | {x['verdict']}",
        _col("line", sep),
        f"DOMAINE   {desc}",
        f"CONTEXTE  {context_txt}",
        f"LECTURE   {reading}",
        f"CAUSE     {_cause_label(x['domain'], x['gate'], x['verdict'], x['reason'])}",
        f"NIVEAU    {_severity_label(x['severity'])}",
        f"SIGNAUX   risque={x['risk']} | inconnues={unknown_txt} | contradictions={contradiction_txt}",
        _col("score", f"SCORES    preparation={_pct(x['ready'])} | integrite={_pct(x['integrity'])} | gouvernance={_pct(x['governance'])}"),
        f"ACCORD    observe={x['observed']} | accord={x['count']}/{x['total']} | ratio={_pct(x['ratio'])} | details={x['mix']}",
        _col("proof", f"PREUVE    decision_id={_short(x['decision_id'], 24)} | trace={_short(x['trace_id'], 24)} | latence={x['latency'] if x['latency'] is not None else 'non_expose'}ms"),
        _col("crypto", f"CRYPTO    hash={_short(x['hash'], 24)} | merkle={_short(x['merkle'], 24)}"),
        _col("auth", f"AUTORITE  kernel={_bool_fr(x['kernel_decision'])} | api_autorise={_bool_fr(x['api_allowed'])} | affichage_seul={_bool_fr(x['display_only'])}"),
        _col("audit", f"AUDIT     agg4={x['agg4']} | ne_peut_pas_autoriser={_bool_fr(x['noauth'])} | ne_change_pas_x108={_bool_fr(x['nogate'])}"),
        _col("line", sep),
    ]
    return "\n".join(lines)

def print_decision_card_fr(data: Dict[str, Any]) -> None:
    print(format_decision_card_fr(data))
