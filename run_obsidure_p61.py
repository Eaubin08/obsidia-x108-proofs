from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P61. Créer lean_theorem_p61_bifurcation.lean.
Prouver formellement la Bifurcation de Trajectoire : le dépassement d'un seuil scinde la réalité en deux chemins stricts, écrasant toute superposition probabiliste.
Voici la structure mathématique à compiler :
```lean
structure TrajectoryState where
  critical_value : Nat
  threshold : Nat

def compute_bifurcation (s : TrajectoryState) : Nat :=
  if s.critical_value > s.threshold then
    0 -- Chemin de blocage absolu (Bifurcation vers HOLD/BLOCK)
  else
    1 -- Chemin d'autorisation (ALLOW)

theorem lean_theorem_p61_bifurcation (s : TrajectoryState) (h : s.critical_value > s.threshold) : compute_bifurcation s = 0 := by
  unfold compute_bifurcation
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P61 Bifurcation de Trajectoire)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
