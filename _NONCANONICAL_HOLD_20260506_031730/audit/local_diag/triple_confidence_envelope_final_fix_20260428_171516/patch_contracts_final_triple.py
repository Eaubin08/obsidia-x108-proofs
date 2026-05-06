from pathlib import Path
import re

path = Path("sigma/contracts.py")
text = path.read_text(encoding="utf-8-sig")

TRIPLE_FIELDS = [
    'confidence_integrity: float = 0.0',
    'confidence_governance: float = 0.0',
    'confidence_readiness: float = 0.0',
    'confidence_scope: str = "integrity"',
    'governance_scope: str = "x108_decision_robustness"',
    'readiness_scope: str = "harmonic_integrity_governance"',
]

def class_blocks(src):
    matches = list(re.finditer(r'(?m)^class\s+([A-Za-z_][A-Za-z0-9_]*)\b.*?:\s*$', src))
    out = []
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(src)
        out.append((name, start, end))
    return out

# ------------------------------------------------------------
# 1. Remove triple fields from AgentVote
# ------------------------------------------------------------

for name, start, end in reversed(class_blocks(text)):
    if name == "AgentVote":
        block = text[start:end]
        before = block
        for field in TRIPLE_FIELDS:
            block = re.sub(r'(?m)^\s*' + re.escape(field) + r'\s*\n', '', block)
        text = text[:start] + block + text[end:]
        print("[OK] AgentVote cleaned" if block != before else "[SKIP] AgentVote already clean")
        break

# ------------------------------------------------------------
# 2. Downgrade DomainAggregate:
#    only raw integrity + severity.
#    no governance/readiness here, no x108_gate here.
# ------------------------------------------------------------

for name, start, end in class_blocks(text):
    if name == "DomainAggregate":
        block = text[start:end]
        break
else:
    raise SystemExit("ERROR: DomainAggregate not found")

lines = block.splitlines(keepends=True)

if_start = None
for i, line in enumerate(lines):
    if re.match(r"^\s*if\s+self\.agent_votes\s*:\s*(#.*)?$", line):
        if_start = i
        break

if if_start is None:
    raise SystemExit("ERROR: if self.agent_votes block not found in DomainAggregate")

indent = re.match(r"^(\s*)", lines[if_start]).group(1)
indent_len = len(indent)

if_end = if_start + 1
while if_end < len(lines):
    line = lines[if_end]
    stripped = line.strip()

    if stripped == "":
        if_end += 1
        continue

    current_indent_len = len(re.match(r"^(\s*)", line).group(1))
    if current_indent_len <= indent_len:
        break

    if_end += 1

new_domain_block = [
    f"{indent}if self.agent_votes:\n",
    f"{indent}    # DomainAggregate owns only raw integrity confidence.\n",
    f"{indent}    # Final X-108 governance/readiness is computed in CanonicalDecisionEnvelope,\n",
    f"{indent}    # after GuardX108 has produced x108_gate.\n",
    f"{indent}    self.confidence = normalize_confidence(getattr(self, \"confidence\", 0.50))\n",
    f"{indent}\n",
    f"{indent}    if verdict in (\"BLOCK\", \"ABORT_TRAJECTORY\", \"REFUSE\", \"DENY\"):\n",
    f"{indent}        self.severity = Severity.S4\n",
    f"{indent}    elif self.contradictions or self.risk_flags:\n",
    f"{indent}        self.severity = Severity.S4\n",
    f"{indent}    elif self.unknowns:\n",
    f"{indent}        self.severity = Severity.S2\n",
    f"{indent}    elif verdict in (\"AUTHORIZE\", \"ALLOW\", \"ACT\", \"VALID\", \"PASS\", \"TRAJECTORY_VALID\", \"PAY\"):\n",
    f"{indent}        self.severity = Severity.S0\n",
    f"{indent}    else:\n",
    f"{indent}        self.severity = Severity.S2\n",
]

lines = lines[:if_start] + new_domain_block + lines[if_end:]
block = "".join(lines)

block = re.sub(
    r'(?m)^\s*obsidia_log\(f"Sovereign Audit for \{self\.domain\}.*?\n',
    '        obsidia_log(f"Aggregate Audit for {self.domain} | Verdict: {verdict} | Integrity: {self.confidence} | Severity: {self.severity}")\n',
    block,
)

text = text[:start] + block + text[end:]
print("[OK] DomainAggregate downgraded to raw integrity only")

# ------------------------------------------------------------
# 3. Add triple fields to CanonicalDecisionEnvelope
# ------------------------------------------------------------

for name, start, end in class_blocks(text):
    if name == "CanonicalDecisionEnvelope":
        env_start, env_end = start, end
        env = text[start:end]
        break
else:
    raise SystemExit("ERROR: CanonicalDecisionEnvelope not found")

missing = [field for field in TRIPLE_FIELDS if field not in env]
if missing:
    m = re.search(r'(?m)^(?P<indent>\s*)confidence\s*:\s*float\s*=\s*[0-9.]+', env)
    if not m:
        raise SystemExit("ERROR: confidence field not found in CanonicalDecisionEnvelope")

    indent2 = m.group("indent")
    insert = "\n" + "".join(f"{indent2}{field}\n" for field in missing).rstrip("\n")
    env = env[:m.end()] + insert + env[m.end():]
    print(f"[OK] Added fields to CanonicalDecisionEnvelope: {missing}")
else:
    print("[SKIP] CanonicalDecisionEnvelope already has triple fields")

# ------------------------------------------------------------
# 4. Replace CanonicalDecisionEnvelope.__post_init__
#    Final scoring happens here because x108_gate is now known.
# ------------------------------------------------------------

lines = env.splitlines(keepends=True)

post_start = None
for i, line in enumerate(lines):
    if re.match(r"^\s*def\s+__post_init__\s*\(self\)\s*:\s*$", line):
        post_start = i
        break

if post_start is None:
    raise SystemExit("ERROR: CanonicalDecisionEnvelope.__post_init__ not found")

post_indent = re.match(r"^(\s*)", lines[post_start]).group(1)
post_indent_len = len(post_indent)

post_end = post_start + 1
while post_end < len(lines):
    line = lines[post_end]
    stripped = line.strip()

    if stripped == "":
        post_end += 1
        continue

    current_indent_len = len(re.match(r"^(\s*)", line).group(1))
    if current_indent_len <= post_indent_len:
        break

    post_end += 1

new_post = [
    f"{post_indent}def __post_init__(self):\n",
    f"{post_indent}    # Normalize severity display format.\n",
    f"{post_indent}    if hasattr(self, \"severity\"):\n",
    f"{post_indent}        if isinstance(self.severity, int) and not isinstance(self.severity, str):\n",
    f"{post_indent}            self.severity = f\"S{{self.severity}}\"\n",
    f"{post_indent}        elif hasattr(self.severity, \"name\"):\n",
    f"{post_indent}            self.severity = str(self.severity.name)\n",
    f"{post_indent}\n",
    f"{post_indent}    # Final triple confidence architecture.\n",
    f"{post_indent}    # At envelope level, x108_gate is already known.\n",
    f"{post_indent}    self.confidence_integrity = normalize_confidence(getattr(self, \"confidence\", 0.50))\n",
    f"{post_indent}    self.confidence = self.confidence_integrity\n",
    f"{post_indent}    self.confidence_scope = \"integrity\"\n",
    f"{post_indent}\n",
    f"{post_indent}    self.confidence_governance = compute_governance_confidence(\n",
    f"{post_indent}        self.confidence_integrity,\n",
    f"{post_indent}        getattr(self, \"market_verdict\", \"HOLD\"),\n",
    f"{post_indent}        getattr(self, \"x108_gate\", \"\"),\n",
    f"{post_indent}        getattr(self, \"unknowns\", []) or [],\n",
    f"{post_indent}        getattr(self, \"risk_flags\", []) or [],\n",
    f"{post_indent}        getattr(self, \"contradictions\", []) or [],\n",
    f"{post_indent}    )\n",
    f"{post_indent}    self.governance_scope = \"x108_decision_robustness\"\n",
    f"{post_indent}\n",
    f"{post_indent}    self.confidence_readiness = compute_readiness_confidence(\n",
    f"{post_indent}        self.confidence_integrity,\n",
    f"{post_indent}        self.confidence_governance,\n",
    f"{post_indent}    )\n",
    f"{post_indent}    self.readiness_scope = \"harmonic_integrity_governance\"\n",
    f"{post_indent}\n",
    f"{post_indent}    obsidia_log(\n",
    f"{post_indent}        f\"Sovereign Audit for {{self.domain}} | Verdict: {{self.market_verdict}} | \"\n",
    f"{post_indent}        f\"Gate: {{self.x108_gate}} | \"\n",
    f"{post_indent}        f\"Integrity: {{self.confidence_integrity}} | \"\n",
    f"{post_indent}        f\"Governance: {{self.confidence_governance}} | \"\n",
    f"{post_indent}        f\"Readiness: {{self.confidence_readiness}} | \"\n",
    f"{post_indent}        f\"Severity: {{self.severity}}\"\n",
    f"{post_indent}    )\n",
]

lines = lines[:post_start] + new_post + lines[post_end:]
env = "".join(lines)

text = text[:env_start] + env + text[env_end:]
print("[OK] CanonicalDecisionEnvelope.__post_init__ now computes final triple score")

# ------------------------------------------------------------
# 5. Final cleanup: remove accidental triple fields outside envelope.
# ------------------------------------------------------------

env_match = re.search(r'class CanonicalDecisionEnvelope\b.*?(?=^class |\Z)', text, re.S | re.M)
env_block = env_match.group(0)

outside = text.replace(env_block, "__ENVELOPE_BLOCK__")
for field in TRIPLE_FIELDS:
    outside = re.sub(r'(?m)^\s*' + re.escape(field) + r'\s*\n', '', outside)

text = outside.replace("__ENVELOPE_BLOCK__", env_block)

path.write_text(text, encoding="utf-8", newline="\n")
print("[OK] contracts.py final triple confidence fix complete")
