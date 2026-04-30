from pathlib import Path
import re

text = Path("sigma/contracts.py").read_text(encoding="utf-8")

m = re.search(r'class CanonicalDecisionEnvelope\b.*?(?=^class |\Z)', text, re.S | re.M)
if not m:
    raise SystemExit("ERROR: CanonicalDecisionEnvelope not found")

block = m.group(0)

print("=== CanonicalDecisionEnvelope field check ===")
for key in [
    "confidence:",
    "confidence_integrity:",
    "confidence_governance:",
    "confidence_readiness:",
    "confidence_scope:",
    "governance_scope:",
    "readiness_scope:",
    "x108_gate:",
]:
    print(f"{key:<32} {'OK' if key in block else 'MISSING'}")

print("\n=== CanonicalDecisionEnvelope confidence excerpt ===")
for i, line in enumerate(block.splitlines(), 1):
    if (
        "confidence" in line
        or "scope" in line
        or "market_verdict" in line
        or "x108_gate" in line
    ):
        print(f"{i:03d}: {line}")

print("\n=== Misplaced field check outside CanonicalDecisionEnvelope ===")
outside = text.replace(block, "")
for key in [
    "confidence_integrity:",
    "confidence_governance:",
    "confidence_readiness:",
    "confidence_scope:",
    "governance_scope:",
    "readiness_scope:",
]:
    print(f"{key:<32} {'MISPLACED' if key in outside else 'OK'}")
