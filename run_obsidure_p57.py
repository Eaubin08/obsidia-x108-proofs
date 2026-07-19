from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P57. Créer lean_theorem_p57_shannon_entropy.lean.
Prouver formellement que l'Entropie de Shannon (incertitude) d'un état tombe à zéro si toutes les variables sont connues (déterminisme absolu).
Voici la structure mathématique à compiler :
```lean
structure EntropicState where
  unknown_factors : Nat
  shannon_entropy : Nat

def measure_entropy (s : EntropicState) : Nat :=
  if s.unknown_factors == 0 then
    0
  else
    s.unknown_factors + 1

theorem lean_theorem_p57_shannon_entropy (s : EntropicState) (h : s.unknown_factors = 0) : measure_entropy s = 0 := by
  unfold measure_entropy
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P57 Entropie de Shannon)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
