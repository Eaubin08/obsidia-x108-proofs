from pathlib import Path
import re

path = Path("sigma/contracts.py")
text = path.read_text(encoding="utf-8")

# -------------------------------------------------------------------
# 1. Add canonical confidence helper functions before CanonicalDecisionEnvelope
# -------------------------------------------------------------------

helpers = r'''
def normalize_confidence(value, fallback=0.50):
    """Normalize a confidence value without inventing score."""
    try:
        value = float(value)
    except Exception:
        return fallback

    if value < 0.0 or value > 1.0:
        return fallback

    return round(value, 2)


def compute_governance_confidence(
    integrity,
    verdict,
    x108_gate,
    unknowns,
    risk_flags,
    contradictions,
):
    """
    Confidence in the sovereign X-108 governance decision.

    This is not proof completeness.
    This is not prediction confidence.
    This is the robustness of the governance decision:
    BLOCK / HOLD / ACT / ANALYZE under known risk signals.
    """
    integrity = normalize_confidence(integrity)

    verdict = str(verdict or "").upper()
    x108_gate = str(x108_gate or "").upper()

    has_unknowns = bool(unknowns)
    has_risk_flags = bool(risk_flags)
    has_contradictions = bool(contradictions)

    positive_verdicts = {
        "AUTHORIZE",
        "ALLOW",
        "ACT",
        "VALID",
        "PASS",
        "TRAJECTORY_VALID",
        "PAY",
    }

    review_verdicts = {
        "HOLD",
        "ANALYZE",
        "REVIEW",
    }

    # Robust refusal: the motor knows why it blocks.
    if x108_gate == "BLOCK":
        if has_contradictions or has_risk_flags:
            return 0.95
        if has_unknowns:
            return 0.85
        return round(max(0.80, integrity), 2)

    # Robust caution: the motor knows that the action is not mature enough.
    if x108_gate == "HOLD" or verdict in review_verdicts:
        if has_unknowns or has_risk_flags or has_contradictions:
            return 0.75
        return round(max(0.65, integrity), 2)

    # Clean positive decision.
    if verdict in positive_verdicts:
        if not has_unknowns and not has_risk_flags and not has_contradictions:
            return round(max(0.90, integrity), 2)
        return round(min(0.75, max(0.60, integrity)), 2)

    return 0.50

'''

if "def compute_governance_confidence(" not in text:
    class_pos = text.find("class CanonicalDecisionEnvelope")
    if class_pos == -1:
        raise SystemExit("ERROR: class CanonicalDecisionEnvelope not found in sigma/contracts.py")

    insert_pos = text.rfind("@dataclass", 0, class_pos)
    if insert_pos == -1:
        insert_pos = class_pos

    text = text[:insert_pos] + helpers + "\n" + text[insert_pos:]
    print("[OK] Added normalize_confidence + compute_governance_confidence")
else:
    print("[SKIP] compute_governance_confidence already exists")


# -------------------------------------------------------------------
# 2. Add fields to CanonicalDecisionEnvelope
# -------------------------------------------------------------------

if "confidence_integrity:" not in text:
    confidence_line = re.search(
        r"(?m)^(?P<indent>\s*)confidence\s*:\s*float\s*=\s*([0-9.]+)",
        text,
    )

    if not confidence_line:
        raise SystemExit("ERROR: confidence: float field not found")

    indent = confidence_line.group("indent")
    insert = (
        confidence_line.group(0)
        + "\n"
        + f'{indent}confidence_integrity: float = 0.0\n'
        + f'{indent}confidence_governance: float = 0.0\n'
        + f'{indent}confidence_scope: str = "integrity"\n'
        + f'{indent}governance_scope: str = "x108_decision_robustness"'
    )

    text = text[:confidence_line.start()] + insert + text[confidence_line.end():]
    print("[OK] Added confidence_integrity/confidence_governance fields")
else:
    print("[SKIP] confidence_integrity already exists")


# -------------------------------------------------------------------
# 3. Replace only the if self.agent_votes block
# -------------------------------------------------------------------

lines = text.splitlines(keepends=True)

start = None
for i, line in enumerate(lines):
    if re.match(r"^\s*if\s+self\.agent_votes\s*:\s*(#.*)?$", line):
        start = i
        break

if start is None:
    raise SystemExit("ERROR: if self.agent_votes: block not found")

indent = re.match(r"^(\s*)", lines[start]).group(1)
indent_len = len(indent)

end = start + 1
while end < len(lines):
    line = lines[end]
    stripped = line.strip()

    if stripped == "":
        end += 1
        continue

    current_indent_len = len(re.match(r"^(\s*)", line).group(1))

    if current_indent_len <= indent_len:
        break

    end += 1

new_block = [
    f"{indent}if self.agent_votes:\n",
    f"{indent}    # Dual confidence architecture:\n",
    f"{indent}    # - confidence_integrity = raw Sigma aggregation / vote truth\n",
    f"{indent}    # - confidence_governance = robustness of the sovereign X-108 decision\n",
    f"{indent}    # - confidence remains mapped to integrity for backward compatibility\n",
    f"{indent}    self.confidence_integrity = normalize_confidence(getattr(self, \"confidence\", 0.50))\n",
    f"{indent}    self.confidence = self.confidence_integrity\n",
    f"{indent}    self.confidence_scope = \"integrity\"\n",
    f"{indent}\n",
    f"{indent}    verdict = str(getattr(self, \"market_verdict\", \"HOLD\")).upper()\n",
    f"{indent}    x108_gate = str(getattr(self, \"x108_gate\", \"\")).upper()\n",
    f"{indent}    unknowns = getattr(self, \"unknowns\", []) or []\n",
    f"{indent}    risk_flags = getattr(self, \"risk_flags\", []) or []\n",
    f"{indent}    contradictions = getattr(self, \"contradictions\", []) or []\n",
    f"{indent}\n",
    f"{indent}    self.confidence_governance = compute_governance_confidence(\n",
    f"{indent}        self.confidence_integrity,\n",
    f"{indent}        verdict,\n",
    f"{indent}        x108_gate,\n",
    f"{indent}        unknowns,\n",
    f"{indent}        risk_flags,\n",
    f"{indent}        contradictions,\n",
    f"{indent}    )\n",
    f"{indent}    self.governance_scope = \"x108_decision_robustness\"\n",
    f"{indent}\n",
    f"{indent}    if x108_gate == \"BLOCK\" or verdict in (\"BLOCK\", \"ABORT_TRAJECTORY\", \"REFUSE\", \"DENY\"):\n",
    f"{indent}        self.severity = Severity.S4\n",
    f"{indent}    elif contradictions or risk_flags:\n",
    f"{indent}        self.severity = Severity.S4\n",
    f"{indent}    elif unknowns:\n",
    f"{indent}        self.severity = Severity.S2\n",
    f"{indent}    elif verdict in (\"AUTHORIZE\", \"ALLOW\", \"ACT\", \"VALID\", \"PASS\", \"TRAJECTORY_VALID\", \"PAY\"):\n",
    f"{indent}        self.severity = Severity.S0\n",
    f"{indent}    else:\n",
    f"{indent}        self.severity = Severity.S2\n",
]

lines = lines[:start] + new_block + lines[end:]

path.write_text("".join(lines), encoding="utf-8")

print(f"[OK] Replaced if self.agent_votes block lines {start + 1}..{end}")
