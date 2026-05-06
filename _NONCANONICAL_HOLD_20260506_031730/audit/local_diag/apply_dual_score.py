import re
from pathlib import Path

contracts_path = Path("sigma/contracts.py")
guard_path = Path("sigma/guard.py")

# --- 1. Update contracts.py (Add fields) ---
content = contracts_path.read_text(encoding="utf-8")

# On ajoute les champs dans CanonicalDecisionEnvelope
new_fields = """    confidence: float = 0.0
    confidence_integrity: float = 0.0
    confidence_governance: float = 0.0"""
content = re.sub(r"confidence:\s*float\s*=\s*0\.0", new_fields, content)

contracts_path.write_text(content, encoding="utf-8")
print("[OK] contracts.py: Dual-score fields added.")

# --- 2. Update guard.py (Logic) ---
g_content = guard_path.read_text(encoding="utf-8")

# On insère la fonction de calcul canonique avant la classe GuardX108
logic_func = """
def compute_governance_confidence(integrity, verdict, gate, unknowns, risk_flags, contradictions):
    try: integrity = float(integrity)
    except: integrity = 0.5
    verdict = str(verdict or "").upper()
    gate = str(gate or "").upper()
    has_unknowns = bool(unknowns)
    has_risks = bool(risk_flags)
    has_contras = bool(contradictions)

    if gate == "BLOCK":
        return 0.95 if (has_contras or has_risks) else 0.85
    if gate == "HOLD" or verdict in ("HOLD", "ANALYZE", "REVIEW"):
        return 0.75 if (has_unknowns or has_risks) else 0.65
    if verdict in ("AUTHORIZE", "ALLOW", "ACT", "VALID", "PASS", "TRAJECTORY_VALID", "PAY"):
        if not has_unknowns and not has_risks and not has_contras:
            return max(0.90, integrity)
        return min(0.75, max(0.60, integrity))
    return 0.50

"""
if "def compute_governance_confidence" not in g_content:
    g_content = g_content.replace("class GuardX108:", logic_func + "class GuardX108:")

# On modifie l'appel dans decide()
decide_pattern = r"return CanonicalDecisionEnvelope\(([\s\S]+?)\)"
def subst_decide(m):
    body = m.group(1)
    # On calcule les scores avant le return
    prefix = "        conf_gov = compute_governance_confidence(aggregate.confidence, aggregate.market_verdict, gate.value, aggregate.unknowns, aggregate.risk_flags, aggregate.contradictions)\n"
    # On injecte les nouveaux paramètres
    new_body = body.replace("confidence=aggregate.confidence,", "confidence=aggregate.confidence,\n            confidence_integrity=aggregate.confidence,\n            confidence_governance=conf_gov,")
    return prefix + "        return CanonicalDecisionEnvelope(" + new_body + ")"

g_content = re.sub(decide_pattern, subst_decide, g_content)
guard_path.write_text(g_content, encoding="utf-8")
print("[OK] guard.py: Logic updated.")
