from pathlib import Path
import ast
import json

ROOT = Path(".")
text = Path("sigma/contracts.py").read_text(encoding="utf-8")
lines = text.splitlines()
tree = ast.parse(text)

def class_src(name):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return "\n".join(lines[node.lineno - 1:node.end_lineno])
    raise SystemExit(f"Missing class: {name}")

agent = class_src("AgentVote")
domain = class_src("DomainAggregate")
env = class_src("CanonicalDecisionEnvelope")

keys = [
    "confidence_integrity",
    "confidence_governance",
    "confidence_readiness",
    "confidence_scope",
    "governance_scope",
    "readiness_scope",
]

ok = True
json_ok = True

print("=== STRUCTURE CHECK ===")

for k in keys:
    r = k in env
    print(f"Envelope has {k:<28}", "OK" if r else "MISSING")
    ok = ok and r

for k in keys:
    r = k not in agent
    print(f"AgentVote clean {k:<27}", "OK" if r else "BAD")
    ok = ok and r

bad_domain_tokens = [
    "x108_gate",
    "confidence_governance",
    "confidence_readiness",
    "compute_governance_confidence",
    "compute_readiness_confidence",
    "Sovereign Audit",
]

for token in bad_domain_tokens:
    r = token not in domain
    print(f"DomainAggregate no {token:<24}", "OK" if r else "BAD")
    ok = ok and r

print("DomainAggregate has Aggregate Audit", "OK" if "Aggregate Audit" in domain else "MISSING")
print("Envelope has Sovereign Audit", "OK" if "Sovereign Audit" in env else "MISSING")

print("\n=== JSON CHECK ===")
files = sorted((ROOT / "MonProjet" / "allData").glob("decision_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:12]

for p in files:
    data = json.loads(p.read_text(encoding="utf-8"))
    i = data.get("confidence_integrity")
    g = data.get("confidence_governance")
    r = data.get("confidence_readiness")

    missing = [k for k in [
        "confidence_integrity",
        "confidence_governance",
        "confidence_readiness",
        "confidence_scope",
        "governance_scope",
        "readiness_scope",
    ] if data.get(k) is None]

    expected = round(min(0.98, (2 * i * g) / (i + g)), 2) if i and g else None
    harmonic_ok = expected is not None and abs(expected - r) <= 0.01

    print(f"{p.name} | {data.get('domain')} | gate={data.get('x108_gate')} | I={i} | G={g} | R={r} | expected={expected} | harmonic={'OK' if harmonic_ok else 'BAD'} | missing={missing}")

    if missing or not harmonic_ok:
        json_ok = False

print("\n=== FINAL ===")
print("STRUCTURE_OK=", ok)
print("JSON_OK=", json_ok)

if not ok or not json_ok:
    raise SystemExit(1)
