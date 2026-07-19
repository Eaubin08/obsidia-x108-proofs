from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P50. Créer lean_theorem_p50_fundamental_recursion.lean.
Prouver formellement la Récursivité Fondamentale : la loi du Kernel s'applique de manière fractale et absolue, quelle que soit la profondeur (depth) de la couche.
Voici la structure mathématique à compiler :
```lean
structure RecursiveLayer where
  depth : Nat
  kernel_law_applied : Bool

def apply_fractal_law (l : RecursiveLayer) : RecursiveLayer :=
  { l with kernel_law_applied := true }

theorem lean_theorem_p50_fundamental_recursion (l : RecursiveLayer) : (apply_fractal_law l).kernel_law_applied = true := by
  unfold apply_fractal_law
  rfl
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P50 Récursivité Fondamentale)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
