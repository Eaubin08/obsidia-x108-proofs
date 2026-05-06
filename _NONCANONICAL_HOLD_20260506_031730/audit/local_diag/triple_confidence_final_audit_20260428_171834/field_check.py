from pathlib import Path
import re

text = Path("sigma/contracts.py").read_text(encoding="utf-8")

def block(name):
    m = re.search(rf'class {name}\b.*?(?=^class |\Z)', text, re.S | re.M)
    return m.group(0) if m else ""

agent = block("AgentVote")
domain = block("DomainAggregate")
env = block("CanonicalDecisionEnvelope")

keys = [
    "confidence_integrity:",
    "confidence_governance:",
    "confidence_readiness:",
    "confidence_scope:",
    "governance_scope:",
    "readiness_scope:",
]

print("=== CanonicalDecisionEnvelope ===")
for k in keys:
    print(k, "OK" if k in env else "MISSING")

print("\n=== AgentVote pollution ===")
for k in keys:
    print(k, "BAD" if k in agent else "OK")

print("\n=== DomainAggregate premature x108 ===")
print("x108_gate", "BAD" if "x108_gate" in domain else "OK")
print("Sovereign Audit in envelope", "OK" if "Sovereign Audit" in env else "MISSING")
print("Aggregate Audit in DomainAggregate", "OK" if "Aggregate Audit" in domain else "CHECK")
