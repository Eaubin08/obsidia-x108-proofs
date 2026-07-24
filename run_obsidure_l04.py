from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème L-04. Créer lean_theorem_hold_preservation.lean.
Prouver formellement qu'un état HOLD fige le système et empêche toute action périphérique.
Voici la structure mathématique à compiler :
```lean
structure ActionState where
  is_hold : Bool
  can_act : Bool

def apply_hold_policy (s : ActionState) : ActionState :=
  if s.is_hold then
    { s with can_act := false }
  else
    s

theorem lean_theorem_hold_preservation (s : ActionState) (h : s.is_hold = true) : (apply_hold_policy s).can_act = false := by
  unfold apply_hold_policy
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (L-04 Préservation du HOLD)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
