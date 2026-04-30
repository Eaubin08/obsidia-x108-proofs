from pathlib import Path
import re

path = Path("sigma/contracts.py")
text = path.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1. Add readiness helper if missing
# ------------------------------------------------------------

readiness_helper = r'''
def compute_readiness_confidence(integrity, governance):
    """
    Conservative global readiness score.

    Harmonic mean:
    - rewards balance between proof integrity and governance robustness
    - punishes asymmetric cases where one score is weak
    - avoids marketing-style arithmetic averaging
    """
    integrity = normalize_confidence(integrity)
    governance = normalize_confidence(governance)

    if integrity <= 0 or governance <= 0:
        return 0.50

    readiness = (2 * integrity * governance) / (integrity + governance)
    return round(min(0.98, readiness), 2)

'''

if "def compute_readiness_confidence(" not in text:
    class_pos = text.find("class CanonicalDecisionEnvelope")
    if class_pos == -1:
        raise SystemExit("ERROR: class CanonicalDecisionEnvelope not found")

    insert_pos = text.rfind("@dataclass", 0, class_pos)
    if insert_pos == -1:
        insert_pos = class_pos

    text = text[:insert_pos] + readiness_helper + "\n" + text[insert_pos:]
    print("[OK] Added compute_readiness_confidence")
else:
    print("[SKIP] compute_readiness_confidence already exists")


# ------------------------------------------------------------
# 2. Add confidence_readiness field if missing
# ------------------------------------------------------------

if "confidence_readiness:" not in text:
    m = re.search(r"(?m)^(?P<indent>\s*)confidence_governance\s*:\s*float\s*=\s*[0-9.]+", text)
    if not m:
        raise SystemExit("ERROR: confidence_governance field not found")

    indent = m.group("indent")
    replacement = m.group(0) + "\n" + f"{indent}confidence_readiness: float = 0.0"
    text = text[:m.start()] + replacement + text[m.end():]
    print("[OK] Added confidence_readiness field")
else:
    print("[SKIP] confidence_readiness field already exists")


if "readiness_scope:" not in text:
    m = re.search(r'(?m)^(?P<indent>\s*)governance_scope\s*:\s*str\s*=\s*"[^"]*"', text)
    if not m:
        raise SystemExit("ERROR: governance_scope field not found")

    indent = m.group("indent")
    replacement = m.group(0) + "\n" + f'{indent}readiness_scope: str = "harmonic_integrity_governance"'
    text = text[:m.start()] + replacement + text[m.end():]
    print("[OK] Added readiness_scope field")
else:
    print("[SKIP] readiness_scope already exists")


# ------------------------------------------------------------
# 3. Replace if self.agent_votes block with triple confidence logic
# ------------------------------------------------------------

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
    f"{indent}    # Triple confidence architecture:\n",
    f"{indent}    # - confidence_integrity = raw Sigma aggregation / vote truth\n",
    f"{indent}    # - confidence_governance = robustness of the sovereign X-108 decision\n",
    f"{indent}    # - confidence_readiness = conservative harmonic synthesis\n",
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
    f"{indent}    self.confidence_readiness = compute_readiness_confidence(\n",
    f"{indent}        self.confidence_integrity,\n",
    f"{indent}        self.confidence_governance,\n",
    f"{indent}    )\n",
    f"{indent}    self.readiness_scope = \"harmonic_integrity_governance\"\n",
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
text = "".join(lines)


# ------------------------------------------------------------
# 4. Upgrade Sovereign Audit log if the old line is present
# ------------------------------------------------------------

old_log_pattern = re.compile(
    r'obsidia_log\(f"Sovereign Audit for \{self\.domain\} \| Verdict: \{verdict\} \| Conf: \{self\.confidence\} \| Severity: \{self\.severity\}"\)'
)

new_log = (
    'obsidia_log('
    'f"Sovereign Audit for {self.domain} | Verdict: {verdict} | '
    'Integrity: {self.confidence_integrity} | '
    'Governance: {self.confidence_governance} | '
    'Readiness: {self.confidence_readiness} | '
    'Severity: {self.severity}"'
    ')'
)

text2, count = old_log_pattern.subn(new_log, text)
text = text2

if count:
    print(f"[OK] Upgraded Sovereign Audit log line: {count}")
else:
    print("[WARN] Old Sovereign Audit log pattern not found; fields still added")


path.write_text(text, encoding="utf-8")

print(f"[OK] Triple confidence patch applied in sigma/contracts.py")
