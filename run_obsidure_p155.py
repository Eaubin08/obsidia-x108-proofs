from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P155. Créer lean_theorem_p155_metaphor.lean.
Prouver formellement la Métaphore comme Analogie : une situation cible inconnue, si elle est strictement analogue à une source validée, hérite de sa validation.
Voici la structure mathématique à compiler :
```lean
structure MetaphorState where
  is_analogous : Bool
  source_validated : Bool

def evaluate_metaphor (s : MetaphorState) : Nat :=
  if s.is_analogous == true && s.source_validated == true then
    1 -- ALLOW : L'analogie transfère mathématiquement la validation (le pont est franchi)
  else
    0 -- BLOCK : Pas d'analogie stricte, l'inconnu est rejeté

theorem lean_theorem_p155_metaphor (s : MetaphorState) (h1 : s.is_analogous = true) (h2 : s.source_validated = true) : evaluate_metaphor s = 1 := by
  unfold evaluate_metaphor
  simp [h1, h2]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P155 Métaphore = Analogie)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
