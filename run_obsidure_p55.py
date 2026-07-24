from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX. Théorème P55. Créer lean_theorem_p55_metric_space.lean.
Prouver formellement l'Espace Métrique : la distance spatiale entre deux états dans Obsidia est strictement définie par le nombre de transitions/étapes requises pour les relier.
Voici la structure mathématique à compiler :
```lean
structure MetricState where
  transition_steps : Nat

def measure_distance (s : MetricState) : Nat :=
  s.transition_steps -- La distance n'est rien d'autre que le nombre de pas de transition

theorem lean_theorem_p55_metric_space (s : MetricState) : measure_distance s = s.transition_steps := by
  unfold measure_distance
  rfl
```"""

print("\n🚀 OBSIDURE PREND LE RELAIS (P55 Espace Métrique)...")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
