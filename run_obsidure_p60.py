from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P60. Créer lean_theorem_p60_self_organization.lean.
Prouver formellement l'Auto-organisation : l'application des cycles du Kernel force l'ordre à émerger en effondrant l'entropie.
Voici la structure mathématique à compiler :
```lean
structure ChaosState where
  entropy_level : Nat
  kernel_cycles : Nat

def auto_organize (s : ChaosState) : Nat :=
  if s.kernel_cycles > 0 then
    0 -- L'ordre parfait émerge après l'application de la loi
  else
    s.entropy_level

theorem lean_theorem_p60_self_organization (s : ChaosState) (h : s.kernel_cycles > 0) : auto_organize s = 0 := by
  unfold auto_organize
  simp [h]
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P60 Auto-organisation)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
