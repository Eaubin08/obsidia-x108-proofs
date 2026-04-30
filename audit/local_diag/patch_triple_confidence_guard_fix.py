from pathlib import Path
import re

contracts = Path("sigma/contracts.py")
guard = Path("sigma/guard.py")

contracts_text = contracts.read_text(encoding="utf-8")
guard_text = guard.read_text(encoding="utf-8")


# ============================================================
# PATCH 1 — contracts.py
# DomainAggregate must NOT compute X-108 governance/readiness.
# It only normalizes the raw integrity confidence from aggregation.
# ============================================================

class_matches = list(re.finditer(r'(?m)^class\s+([A-Za-z_][A-Za-z0-9_]*)\b.*?:\s*$', contracts_text))
blocks = []
for idx, m in enumerate(class_matches):
    name = m.group(1)
    start = m.start()
    end = class_matches[idx + 1].start() if idx + 1 < len(class_matches) else len(contracts_text)
    blocks.append((name, start, end))

domain_block = None
for name, start, end in blocks:
    if name == "DomainAggregate":
        domain_block = (start, end)
        break

if domain_block is None:
    raise SystemExit("ERROR: DomainAggregate not found")

start, end = domain_block
block = contracts_text[start:end]

if "Triple confidence architecture:" in block:
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

    new_block = [
        f"{indent}if self.agent_votes:\n",
        f"{indent}    # DomainAggregate owns only raw integrity confidence.\n",
        f"{indent}    # X-108 governance/readiness is computed later in GuardX108,\n",
        f"{indent}    # after x108_gate is known.\n",
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

    lines = lines[:if_start] + new_block + lines[if_end:]
    block = "".join(lines)

    block = re.sub(
        r'obsidia_log\(f"Sovereign Audit for \{self\.domain\} \| Verdict: \{verdict\} \| Integrity: \{self\.confidence_integrity\} \| Governance: \{self\.confidence_governance\} \| Readiness: \{self\.confidence_readiness\} \| Severity: \{self\.severity\}"\)',
        'obsidia_log(f"Aggregate Audit for {self.domain} | Verdict: {verdict} | Integrity: {self.confidence} | Severity: {self.severity}")',
        block,
    )

    contracts_text = contracts_text[:start] + block + contracts_text[end:]
    print("[OK] DomainAggregate downgraded to raw integrity only")
else:
    print("[SKIP] DomainAggregate triple block not found; probably already fixed")


# Ensure CanonicalDecisionEnvelope has fields
env_match = re.search(r'class CanonicalDecisionEnvelope\b.*?(?=^class |\Z)', contracts_text, re.S | re.M)
if not env_match:
    raise SystemExit("ERROR: CanonicalDecisionEnvelope not found")

env = env_match.group(0)
required_fields = [
    'confidence_integrity: float = 0.0',
    'confidence_governance: float = 0.0',
    'confidence_readiness: float = 0.0',
    'confidence_scope: str = "integrity"',
    'governance_scope: str = "x108_decision_robustness"',
    'readiness_scope: str = "harmonic_integrity_governance"',
]

missing = [f for f in required_fields if f not in env]
if missing:
    m = re.search(r'(?m)^(?P<indent>\s*)confidence\s*:\s*float\s*=\s*[0-9.]+', env)
    if not m:
        raise SystemExit("ERROR: confidence field not found in CanonicalDecisionEnvelope")

    indent = m.group("indent")
    insert = "".join(f"{indent}{field}\n" for field in missing)
    env2 = env[:m.end()] + "\n" + insert.rstrip("\n") + env[m.end():]
    contracts_text = contracts_text[:env_match.start()] + env2 + contracts_text[env_match.end():]
    print(f"[OK] Added missing envelope fields: {missing}")
else:
    print("[OK] CanonicalDecisionEnvelope fields already present")

contracts.write_text(contracts_text, encoding="utf-8", newline="\n")


# ============================================================
# PATCH 2 — guard.py
# Compute governance/readiness AFTER x108_gate exists.
# ============================================================

if "triple confidence architecture — final envelope scoring" not in guard_text:
    idx = guard_text.find("return CanonicalDecisionEnvelope(")
    if idx == -1:
        raise SystemExit("ERROR: return CanonicalDecisionEnvelope(...) not found in sigma/guard.py")

    # Find matching closing parenthesis for CanonicalDecisionEnvelope call
    call_start = guard_text.find("CanonicalDecisionEnvelope(", idx)
    paren_start = guard_text.find("(", call_start)

    depth = 0
    call_end = None
    for pos in range(paren_start, len(guard_text)):
        ch = guard_text[pos]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                call_end = pos + 1
                break

    if call_end is None:
        raise SystemExit("ERROR: could not find end of CanonicalDecisionEnvelope call")

    old_call = guard_text[idx:call_end]
    env_call = old_call.replace("return CanonicalDecisionEnvelope(", "env = CanonicalDecisionEnvelope(", 1)

    indent = re.match(r"^(\s*)", guard_text[idx:guard_text.find("\n", idx)]).group(1)

    addition = f'''
{env_call}

{indent}# triple confidence architecture — final envelope scoring
{indent}# This happens after GuardX108 has produced x108_gate.
{indent}try:
{indent}    from sigma.contracts import (
{indent}        normalize_confidence,
{indent}        compute_governance_confidence,
{indent}        compute_readiness_confidence,
{indent}        obsidia_log,
{indent}    )
{indent}except Exception:
{indent}    from .contracts import (
{indent}        normalize_confidence,
{indent}        compute_governance_confidence,
{indent}        compute_readiness_confidence,
{indent}        obsidia_log,
{indent}    )

{indent}env.confidence_integrity = normalize_confidence(getattr(aggregate, "confidence", getattr(env, "confidence", 0.50)))
{indent}env.confidence = env.confidence_integrity
{indent}env.confidence_scope = "integrity"

{indent}env.confidence_governance = compute_governance_confidence(
{indent}    env.confidence_integrity,
{indent}    getattr(env, "market_verdict", "HOLD"),
{indent}    getattr(env, "x108_gate", ""),
{indent}    getattr(env, "unknowns", []) or [],
{indent}    getattr(env, "risk_flags", []) or [],
{indent}    getattr(env, "contradictions", []) or [],
{indent})
{indent}env.governance_scope = "x108_decision_robustness"

{indent}env.confidence_readiness = compute_readiness_confidence(
{indent}    env.confidence_integrity,
{indent}    env.confidence_governance,
{indent})
{indent}env.readiness_scope = "harmonic_integrity_governance"

{indent}obsidia_log(
{indent}    f"Sovereign Audit for {{env.domain}} | Verdict: {{env.market_verdict}} | "
{indent}    f"Gate: {{env.x108_gate}} | "
{indent}    f"Integrity: {{env.confidence_integrity}} | "
{indent}    f"Governance: {{env.confidence_governance}} | "
{indent}    f"Readiness: {{env.confidence_readiness}} | "
{indent}    f"Severity: {{env.severity}}"
{indent})

{indent}return env
'''

    guard_text = guard_text[:idx] + addition + guard_text[call_end:]
    print("[OK] guard.py now computes final triple confidence after x108_gate")
else:
    print("[SKIP] guard.py already has final triple confidence scoring")

guard.write_text(guard_text, encoding="utf-8", newline="\n")
