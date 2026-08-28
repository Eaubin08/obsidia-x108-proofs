/-
  Obsidia / MissionAuthority.lean  — AGRÉGATEUR
  ============================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME — Offline uniquement.

  Modèle formel de l'AUTORITÉ DE MISSION BORNÉE (Stage 4).
  KX108 reste le SEUL kernel souverain. Ces définitions sont formelles,
  hors-runtime : elles ne modifient PAS la souveraineté KX108, n'accordent
  AUCUNE autorité runtime, et ne doivent PAS être importées dans le
  runtime Python / FastAPI / GuardX108.

  Phase 4A = vocabulaire + types + prédicats + relation de transition +
  énoncés d'invariants (propositions nommées). Les preuves de l'inventaire
  de théorèmes appartiennent à 4B. Aucun `sorry`, aucun `admit`, aucun
  `axiom` non sûr ajouté.

  Direction d'import (acyclique) :
    Types → Scope → MissionAuthorization → ActionWitness → Transition
          → Invariants → Refinement → (cet agrégateur)
-/
import Obsidia.MissionAuthority.Types
import Obsidia.MissionAuthority.Scope
import Obsidia.MissionAuthority.MissionAuthorization
import Obsidia.MissionAuthority.ActionWitness
import Obsidia.MissionAuthority.Transition
import Obsidia.MissionAuthority.Invariants
import Obsidia.MissionAuthority.Refinement

#print axioms Obsidia.MissionAuthority.scopeLE_refl
#print axioms Obsidia.MissionAuthority.scopeLE_trans
#print axioms Obsidia.MissionAuthority.subOf_refl
#print axioms Obsidia.MissionAuthority.subOf_trans
