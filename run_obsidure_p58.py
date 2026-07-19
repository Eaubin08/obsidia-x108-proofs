from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P58. Créer lean_theorem_p58_negentropy.lean.
Prouver formellement la Néguentropie : l'application d'une force structurante (loi du Kernel) purge l'entropie du système.
Voici la structure mathématique à compiler :
```lean
structure NegentropicState where
  entropy : Nat
  law_applied : Bool

def apply_negentropy (s : NegentropicState) : Nat :=
  if s.law_applied == true then
    0 -- L'ordre parfait est rétabli par la loi
  else
    s.entropy

theorem lean_theorem_p58_negentropy (s : NegentropicState) (h : s.law_applied = true) : apply_negentropy s = 0 := by
  unfold apply_negentropy
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P58 Néguentropie)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
