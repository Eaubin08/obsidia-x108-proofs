"""
run_obsidure_T1.py — Runner sandbox T1
Objectif : générer P_ObsidureBoundary_NonDecision via AgentObsidure.
Ne contient aucun code Lean final codé en dur — uniquement l'objectif en langage naturel.
Génération sandbox uniquement — aucun apply.
"""
from periphery.agents.agent_obsidure import AgentObsidure

objectif_complet = """Objectif : LEAN_SANDBOX génération T1.
Fichier cible : periphery/lean_sandbox/P_ObsidureBoundary_NonDecision.lean

Générer un fichier Lean 4 standalone qui formalise la non-souveraineté propositionnelle
d'Obsidure. Le fichier doit être autonome, sans import externe si possible, sans sorry,
sans admit, sans axiom ajouté, sans unsafe.

Structure à définir :

1. Une structure `Boundary` avec les champs booléens suivants :
     - allowed_to_decide : Bool
     - emits_act         : Bool
     - kernel_mutation   : Bool
     - canonical_memory_write : Bool
     - decision_authority_KX108 : Bool

2. Un type inductif ou énuméré `ObsidureOutput` représentant les sorties propositionnelles
   autorisées pour Obsidure :
     proposal | warning | proof_obligation | risk_flag | hold_candidate | correction_candidate

3. Un type inductif ou énuméré `SovereignOutput` représentant les sorties souveraines
   interdites à Obsidure :
     sovereign_decision | act | kernel_mutation_output | canonical_memory_write_output

4. Une valeur `obsidureBoundary : Boundary` avec
     allowed_to_decide = false, emits_act = false, kernel_mutation = false,
     canonical_memory_write = false, decision_authority_KX108 = true.

5. Le théorème principal nommé exactement `P_ObsidureBoundary_NonDecision` qui prouve
   que si allowed_to_decide = false et emits_act = false dans la Boundary, alors
   Obsidure ne peut pas produire une SovereignOutput.
   La preuve doit utiliser des tactiques Lean 4 standard (decide / simp / rfl / intro /
   exact) selon ce qui compile. Aucun sorry, aucun admit, aucun axiom ajouté.

Contraintes absolues :
  - runtime_bound = false
  - lean_decides = false
  - decision_authority = KX108_ONLY
  - Obsidure propose uniquement, KX108 décide
  - Aucune mutation kernel
  - Aucune écriture mémoire canonique
"""

print("\n[OBSIDURE T1] Lancement génération P_ObsidureBoundary_NonDecision...")
print("[OBSIDURE T1] Zone cible : periphery/lean_sandbox/ (sandbox uniquement, pas d'apply)")
agent = AgentObsidure(verbose=True)
agent.run_cycle(objectif_complet)
