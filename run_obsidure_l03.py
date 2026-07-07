from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème L-03. Créer lean_theorem_memory_non_sovereignty.lean.
Prouver formellement que la mémoire périphérique ne possède aucune autorité décisionnelle.
Voici la structure mathématique à compiler :
```lean
structure MemoryState where
  is_readonly : Bool
  decision_authority : Nat

def enforce_boundary (m : MemoryState) : MemoryState :=
  if m.is_readonly then 
    { m with decision_authority := 0 } 
  else 
    m

theorem lean_theorem_memory_non_sovereignty (m : MemoryState) (h : m.is_readonly = true) : (enforce_boundary m).decision_authority = 0 := by
  unfold enforce_boundary
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (L-03 Non-Souveraineté Mémoire)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
