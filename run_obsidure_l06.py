from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème L-06. Créer lean_theorem_order_error_prevention.lean.
Prouver formellement qu'aucune action ne peut être exécutée si le processus n'est pas qualifié.
Voici la structure mathématique à compiler :
```lean
structure ProcessState where
  is_qualified : Bool
  execute_action : Bool

def enforce_order (s : ProcessState) : ProcessState :=
  if s.is_qualified == false then
    { s with execute_action := false }
  else
    s

theorem lean_theorem_order_error_prevention (s : ProcessState) (h : s.is_qualified = false) : (enforce_order s).execute_action = false := by
  unfold enforce_order
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (L-06 Prévention d'erreur d'ordre)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
