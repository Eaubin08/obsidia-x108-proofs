from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P107_Lyapunov. Prouver formellement L(Phi(s)) <= L(s).
Voici la véritable physique du Kernel à extraire et à compiler :
```lean
structure DomainState where
  risk_score : Nat
  contradictions : Nat

def L (s : DomainState) : Nat :=
  s.risk_score + s.contradictions

def Phi (s : DomainState) : DomainState :=
  if s.contradictions > 0 then
    { s with risk_score := 0, contradictions := 0 }
  else
    s

theorem {thname} (s : DomainState) : L (Phi s) <= L s := by
  unfold Phi
  split
  · unfold L; omega
  · omega
```"""

print("\n🚀 INJECTION DIRECTE DE LA THERMODYNAMIQUE (P107)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
