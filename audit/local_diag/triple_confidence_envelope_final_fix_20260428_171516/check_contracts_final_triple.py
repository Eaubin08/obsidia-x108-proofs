from pathlib import Path
import re

text = Path("sigma/contracts.py").read_text(encoding="utf-8")

env = re.search(r'class CanonicalDecisionEnvelope\b.*?(?=^class |\Z)', text, re.S | re.M).group(0)
agent = re.search(r'class AgentVote\b.*?(?=^class |\Z)', text, re.S | re.M).group(0)
domain = re.search(r'class DomainAggregate\b.*?(?=^class |\Z)', text, re.S | re.M).group(0)

for key in [
    "confidence_integrity:",
    "confidence_governance:",
    "confidence_readiness:",
    "confidence_scope:",
    "governance_scope:",
    "readiness_scope:",
]:
    print(f"Envelope {key:<28}", "OK" if key in env else "MISSING")
    print(f"AgentVote {key:<28}", "BAD" if key in agent else "OK")

print("DomainAggregate uses x108_gate:", "BAD" if "x108_gate" in domain else "OK")
print("Envelope computes governance:", "OK" if "compute_governance_confidence" in env else "MISSING")
print("Envelope logs Sovereign Audit:", "OK" if "Sovereign Audit" in env else "MISSING")
