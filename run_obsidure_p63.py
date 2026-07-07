from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P63. Créer lean_theorem_p63_sensitivity.lean.
Prouver formellement la Sensibilité aux conditions initiales : toute divergence chaotique dépassant le seuil critique est instantanément tronquée à zéro (pas d'effet papillon infini).
Voici la structure mathématique à compiler :
```lean
structure InitialCondition where
  divergence : Nat
  chaos_threshold : Nat

def butterfly_effect_filter (c : InitialCondition) : Nat :=
  if c.divergence > c.chaos_threshold then
    0 -- BLOCK : La divergence est coupée net, annulation de l'effet papillon
  else
    c.divergence

theorem lean_theorem_p63_sensitivity (c : InitialCondition) (h : c.divergence > c.chaos_threshold) : butterfly_effect_filter c = 0 := by
  unfold butterfly_effect_filter
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P63 Sensibilité aux conditions initiales)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
