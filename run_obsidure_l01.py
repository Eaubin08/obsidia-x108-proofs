from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème L-01. Créer lean_theorem_faithful_path_existence.lean.
Prouver formellement que si une source et une cible sont valides, le chemin établi est fidèle.
Voici la structure mathématique à compiler :
```lean
structure Route where
  source_verified : Bool
  target_locked : Bool
  is_faithful : Bool

def establish_path (r : Route) : Route :=
  if r.source_verified == true && r.target_locked == true then
    { r with is_faithful := true }
  else
    { r with is_faithful := false }

theorem lean_theorem_faithful_path_existence (r : Route) (h1 : r.source_verified = true) (h2 : r.target_locked = true) : (establish_path r).is_faithful = true := by
  unfold establish_path
  simp [h1, h2]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (L-01 Existence d'un Chemin Fidèle)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
