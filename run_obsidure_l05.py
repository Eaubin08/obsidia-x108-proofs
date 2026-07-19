from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème L-05. Créer lean_theorem_stability_before_action.lean.
Prouver formellement qu'aucune action ne peut être déclenchée si le système présente des contradictions.
Voici la structure mathématique à compiler :
```lean
structure SystemState where
  contradictions : Nat
  can_act : Bool

def enforce_stability (s : SystemState) : SystemState :=
  if s.contradictions > 0 then
    { s with can_act := false }
  else
    s

theorem lean_theorem_stability_before_action (s : SystemState) (h : s.contradictions > 0) : (enforce_stability s).can_act = false := by
  unfold enforce_stability
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (L-05 Stabilité avant action)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
