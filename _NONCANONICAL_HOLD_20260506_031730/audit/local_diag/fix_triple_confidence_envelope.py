from pathlib import Path
import re

path = Path("sigma/contracts.py")
text = path.read_text(encoding="utf-8")

fields = [
    'confidence_integrity: float = 0.0',
    'confidence_governance: float = 0.0',
    'confidence_readiness: float = 0.0',
    'confidence_scope: str = "integrity"',
    'governance_scope: str = "x108_decision_robustness"',
    'readiness_scope: str = "harmonic_integrity_governance"',
]

# ------------------------------------------------------------
# Locate class blocks
# ------------------------------------------------------------
class_matches = list(re.finditer(r'(?m)^class\s+([A-Za-z_][A-Za-z0-9_]*)\b.*?:\s*$', text))

if not class_matches:
    raise SystemExit("ERROR: no class found in contracts.py")

blocks = []
for idx, m in enumerate(class_matches):
    name = m.group(1)
    start = m.start()
    end = class_matches[idx + 1].start() if idx + 1 < len(class_matches) else len(text)
    blocks.append((name, start, end))

if not any(name == "CanonicalDecisionEnvelope" for name, _, _ in blocks):
    raise SystemExit("ERROR: CanonicalDecisionEnvelope class not found")

# ------------------------------------------------------------
# Remove triple fields from every class except CanonicalDecisionEnvelope
# ------------------------------------------------------------
new_text = text
removed = 0

# Process from bottom to top so offsets stay valid
for name, start, end in reversed(blocks):
    block = new_text[start:end]
    if name != "CanonicalDecisionEnvelope":
        before = block
        for field in fields:
            block = re.sub(r'(?m)^\s*' + re.escape(field) + r'\s*\n', '', block)
        if block != before:
            removed += 1
            new_text = new_text[:start] + block + new_text[end:]

text = new_text

# Recompute class blocks after removals
class_matches = list(re.finditer(r'(?m)^class\s+([A-Za-z_][A-Za-z0-9_]*)\b.*?:\s*$', text))
blocks = []
for idx, m in enumerate(class_matches):
    name = m.group(1)
    start = m.start()
    end = class_matches[idx + 1].start() if idx + 1 < len(class_matches) else len(text)
    blocks.append((name, start, end))

for name, start, end in blocks:
    if name == "CanonicalDecisionEnvelope":
        env_start, env_end = start, end
        break

env = text[env_start:env_end]

# ------------------------------------------------------------
# Add fields only inside CanonicalDecisionEnvelope, after confidence field
# ------------------------------------------------------------
missing = [f for f in fields if f not in env]

if missing:
    m = re.search(r'(?m)^(?P<indent>\s*)confidence\s*:\s*float\s*=\s*[0-9.]+', env)
    if not m:
        raise SystemExit("ERROR: confidence field not found in CanonicalDecisionEnvelope")

    indent = m.group("indent")
    insert_lines = "".join(f"{indent}{field}\n" for field in missing)
    env = env[:m.end()] + "\n" + insert_lines.rstrip("\n") + env[m.end():]
    text = text[:env_start] + env + text[env_end:]
    print(f"[OK] Added missing fields to CanonicalDecisionEnvelope: {missing}")
else:
    print("[OK] CanonicalDecisionEnvelope already has triple confidence fields")

print(f"[OK] Removed misplaced triple fields from {removed} non-envelope class block(s)")

path.write_text(text, encoding="utf-8")
