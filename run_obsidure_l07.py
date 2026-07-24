from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème L-07. Créer lean_theorem_external_input_non_sovereignty.lean.
Prouver formellement que toute entrée externe est immédiatement dépouillée de son autorité native.
Voici la structure mathématique à compiler :
```lean
structure ExternalInput where
  payload_size : Nat
  native_authority : Nat

def sanitize_input (e : ExternalInput) : ExternalInput :=
  { e with native_authority := 0 }

theorem lean_theorem_external_input_non_sovereignty (e : ExternalInput) : (sanitize_input e).native_authority = 0 := by
  unfold sanitize_input
  rfl
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (L-07 Non-Souveraineté Entrées Externes)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
