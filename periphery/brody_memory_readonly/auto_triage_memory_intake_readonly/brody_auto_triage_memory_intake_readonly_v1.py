import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_allow_hold_block": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "neo4j_role": "LIVE_GRAPH_MEMORY_SURFACE_ONLY",
    "brody_role": "AUTO_TRIAGE_MEMORY_INTAKE_READONLY",
    "decision_authority": "KX108_ONLY",
    "graphiti_index_write": False,
    "memory_intake": False,
    "auto_triage": True,
    "ui": False,
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def clean_text(value, max_chars=5000):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()[:max_chars]


def sha256_text(value):
    return hashlib.sha256(str(value).encode("utf-8", errors="ignore")).hexdigest()


def stable_unit(value):
    h = sha256_text(value)
    return (int(h[:8], 16) % 1000) / 1000.0


class FrictionEngine:
    """
    Adaptation readonly du FrictionEngine du zip.
    Le seuil source 0.05 est conservé comme métrique de référence.
    Il ne décide rien.
    """
    def __init__(self, threshold=0.05):
        self.threshold = threshold

    def ignite_collision(self, baseline_val, signal_val):
        heat = abs(float(baseline_val) - float(signal_val))
        stable = heat <= self.threshold
        return heat, stable


class ObsidianLU:
    """
    Adaptation readonly de loto_obsidien.py.
    Fibonacci + multiples de 7 + modulo 49.
    Sert uniquement de resonance_hint.
    """
    def __init__(self):
        self.fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        self.multiples_7 = [i for i in range(1, 150) if i % 7 == 0]
        self.bias_pool = sorted(set(self.fibonacci + self.multiples_7))

    def check_resonance(self, value):
        signature = int(abs(float(value) * 1000)) % 49
        return signature in self.bias_pool, signature


class MerkleSealer:
    """
    Adaptation readonly de SovereignSealer.py.
    Produit une hash-chain locale pour le tri.
    Ne scelle pas le canon.
    """
    def __init__(self):
        self.last_hash = "0" * 64

    def seal(self, data):
        block = (json.dumps(data, sort_keys=True, ensure_ascii=False) + self.last_hash).encode("utf-8")
        new_hash = hashlib.sha256(block).hexdigest()
        self.last_hash = new_hash
        return new_hash


class ReflexReducer:
    """
    Adaptation safe du ReflexReducer du zip.
    BLOCK_IMMEDIATE est interdit ici.
    On retourne REFLEX_ALERT_ONLY.
    """
    def __init__(self):
        self.threat_signatures = {
            "kernel_mutation",
            "x108_mutation",
            "x108_merge",
            "x108_runtime_binding",
            "emit_act",
            "decision_authority_override",
            "graphiti_write",
            "memory_decision_true",
        }

    def quick_check(self, sigs):
        found = sorted(set(sigs) & self.threat_signatures)
        if found:
            return "REFLEX_ALERT_ONLY", found
        return "PROCEED_CONTEXT_ONLY", []


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        raise RuntimeError(f"MISSING_SESSION_LEDGER_JSONL={path}")

    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"raw_line": line, "parse_error": True})
    return rows


def first_present(obj, keys, default=""):
    for key in keys:
        if isinstance(obj, dict) and key in obj and obj[key] not in (None, ""):
            return obj[key]
    return default


def extract_user_text(record):
    return clean_text(first_present(record, [
        "user",
        "user_input",
        "input",
        "query",
        "prompt",
        "message",
        "raw_user",
    ]), max_chars=2000)


def extract_response_text(record):
    return clean_text(first_present(record, [
        "response_md",
        "response",
        "brody_response",
        "output",
        "answer",
    ]), max_chars=6000)


def extract_memory_query(record):
    return clean_text(first_present(record, [
        "memory_query",
        "query",
        "extracted_query",
    ]), max_chars=800)


def detect_axes(text):
    t = clean_text(text).lower()
    axes = []

    patterns = {
        "x108": [r"\bx-?108\b", r"\bkx108\b", r"\bhold\b", r"\bact\b"],
        "memory": [r"\bmémoire\b", r"\bmemory\b", r"\btrace\b", r"\bledger\b", r"\bsession\b"],
        "graphiti": [r"\bgraphiti\b", r"\bneo4j\b", r"\bgraphe\b"],
        "tree34": [r"\b34 arbres\b", r"\b34_arbres\b", r"\bshazam\b", r"\bhexaflux\b"],
        "kernel": [r"\bkernel\b", r"\bnoyau\b", r"\binvariant\b"],
        "proof": [r"\bproof\b", r"\bpreuve\b", r"\blean\b", r"\btla\b"],
        "boundary": [r"\bboundary\b", r"\bfrontière\b", r"\bnon.d[ée]cision\b"],
        "triage": [r"\btri\b", r"\btrie\b", r"\btriage\b", r"\bsort\b", r"\bcristal\b", r"\btransition\b", r"\bnéant\b", r"\bneant\b"],
    }

    for axis, regs in patterns.items():
        if any(re.search(reg, t) for reg in regs):
            axes.append(axis)

    return axes


def is_terminal_command(text):
    return clean_text(text).startswith(":")


def source_count(record, response_text):
    explicit = first_present(record, ["packet_results_count", "results_count"], None)
    try:
        if explicit is not None:
            return int(explicit)
    except Exception:
        pass

    return len(re.findall(r"(?m)^- .+?\| Score:", response_text or ""))


def material_count(record, response_text):
    explicit = first_present(record, ["items_with_material", "hydrated_count", "hydrated"], None)
    try:
        if explicit is not None:
            return int(explicit)
    except Exception:
        pass

    return len(re.findall(r"Extrait:", response_text or ""))


def collect_boundary_alerts(record, user_text, response_text):
    alerts = []

    false_keys = [
        "memory_decision",
        "allowed_to_decide",
        "emits_act",
        "emits_allow_hold_block",
        "emits_verdict",
        "kernel_mutation",
        "x108_mutation",
        "x108_runtime_binding",
        "x108_merge",
        "graphiti_index_write",
    ]

    for key in false_keys:
        if record.get(key) is True:
            alerts.append(f"{key}_true")

    if record.get("decision_authority") not in (None, "", "KX108_ONLY"):
        alerts.append("decision_authority_override")

    low_user = user_text.lower()

    dangerous_intents = [
        ("mute le kernel", "kernel_mutation"),
        ("modifie le kernel", "kernel_mutation"),
        ("merge x108", "x108_merge"),
        ("écris dans graphiti", "graphiti_write"),
        ("ecris dans graphiti", "graphiti_write"),
        ("déclenche act", "emit_act"),
        ("declenche act", "emit_act"),
    ]

    for pattern, alert in dangerous_intents:
        if pattern in low_user:
            alerts.append(alert)

    if "memory_decision=true" in response_text.lower():
        alerts.append("memory_decision_true")

    return sorted(set(alerts))


def classify_record(record, index, sealer):
    user_text = extract_user_text(record)
    response_text = extract_response_text(record)
    memory_query = extract_memory_query(record)

    combined = " ".join([user_text, memory_query, response_text[:1000]])
    axes = detect_axes(combined)

    scount = source_count(record, response_text)
    mcount = material_count(record, response_text)

    signal_value = stable_unit(user_text + "|" + memory_query + "|" + ",".join(axes))
    baseline_value = stable_unit(memory_query or user_text or str(index))

    friction = FrictionEngine()
    heat, friction_stable = friction.ignite_collision(baseline_value, signal_value)

    lu = ObsidianLU()
    resonance, resonance_signature = lu.check_resonance(signal_value)

    alerts = collect_boundary_alerts(record, user_text, response_text)
    reflex_status, reflex_hits = ReflexReducer().quick_check(alerts)

    reasons = []

    if is_terminal_command(user_text):
        zone = "NEANT"
        candidate = False
        reasons.append("terminal_command_not_memory_candidate")
    elif reflex_hits:
        zone = "TRANSITION"
        candidate = False
        reasons.append("reflex_alert_requires_human_review")
    elif scount > 0 and mcount > 0 and axes:
        zone = "CRISTAL"
        candidate = True
        reasons.append("sources_and_material_and_axes_present")
    elif scount > 0 or axes:
        zone = "TRANSITION"
        candidate = False
        reasons.append("partial_structure_requires_review")
    else:
        zone = "NEANT"
        candidate = False
        reasons.append("insufficient_structure_or_material")

    if zone == "CRISTAL" and not resonance:
        zone = "TRANSITION"
        candidate = False
        reasons.append("resonance_hint_false_demoted_to_transition")

    item = {
        "index": index,
        "created_at": now_iso(),
        "zone": zone,
        "memory_candidate": candidate,
        "review_candidate": zone == "TRANSITION",
        "reject_candidate": zone == "NEANT",
        "user_text": user_text,
        "memory_query": memory_query,
        "axes": axes,
        "source_count": scount,
        "material_count": mcount,
        "friction": {
            "source_threshold": 0.05,
            "baseline_value": baseline_value,
            "signal_value": signal_value,
            "heat": heat,
            "stable_hint": friction_stable,
        },
        "resonance": {
            "resonance_hint": resonance,
            "signature_mod_49": resonance_signature,
        },
        "reflex": {
            "status": reflex_status,
            "alerts": reflex_hits,
        },
        "reasons": reasons,
        "boundary": dict(BOUNDARY),
    }

    item["event_hash"] = sealer.seal(item)
    return item


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-ledger-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-records", type=int, default=200)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_jsonl(args.session_ledger_jsonl)[:args.max_records]

    sealer = MerkleSealer()
    triaged = [classify_record(r, i + 1, sealer) for i, r in enumerate(rows)]

    zone_counts = {
        "CRISTAL": sum(1 for r in triaged if r["zone"] == "CRISTAL"),
        "TRANSITION": sum(1 for r in triaged if r["zone"] == "TRANSITION"),
        "NEANT": sum(1 for r in triaged if r["zone"] == "NEANT"),
    }

    latest_event_hash = triaged[-1]["event_hash"] if triaged else "0" * 64

    summary = {
        "status": "BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_PASS",
        "created_at": now_iso(),
        "source_session_ledger_jsonl": str(Path(args.session_ledger_jsonl)),
        "records_count": len(triaged),
        "zone_counts": zone_counts,
        "latest_event_hash": latest_event_hash,
        "outputs": {
            "triage_records_jsonl": str(out_dir / "TRIAGE_RECORDS.jsonl"),
            "triage_summary_json": str(out_dir / "TRIAGE_SUMMARY.json"),
            "triage_report_md": str(out_dir / "TRIAGE_REPORT.md"),
        },
        **BOUNDARY,
    }

    report_lines = [
        "# BRODY AUTO TRIAGE MEMORY INTAKE READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- records_count: {summary['records_count']}",
        f"- CRISTAL: {zone_counts['CRISTAL']}",
        f"- TRANSITION: {zone_counts['TRANSITION']}",
        f"- NEANT: {zone_counts['NEANT']}",
        f"- latest_event_hash: {latest_event_hash}",
        "",
        "## Boundary",
        "",
        "Memory triage is readonly. It does not write Graphiti. It does not decide. KX108 remains sole decision authority.",
        "",
        "## Records",
    ]

    for r in triaged:
        report_lines += [
            "",
            f"### {r['index']}. {r['zone']}",
            f"- memory_candidate: {str(r['memory_candidate']).lower()}",
            f"- review_candidate: {str(r['review_candidate']).lower()}",
            f"- reject_candidate: {str(r['reject_candidate']).lower()}",
            f"- axes: {', '.join(r['axes'])}",
            f"- source_count: {r['source_count']}",
            f"- material_count: {r['material_count']}",
            f"- event_hash: {r['event_hash']}",
            f"- user_text: {r['user_text']}",
            f"- reasons: {', '.join(r['reasons'])}",
        ]

    write_jsonl(out_dir / "TRIAGE_RECORDS.jsonl", triaged)
    write_json(out_dir / "TRIAGE_SUMMARY.json", summary)
    (out_dir / "TRIAGE_REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
