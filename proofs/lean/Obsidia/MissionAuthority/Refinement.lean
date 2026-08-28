/-
  Obsidia / MissionAuthority / Refinement.lean
  ===========================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME.

  Interface de RAFFINEMENT modèle formel ↔ runtime (types uniquement) et
  bundle des ASSOMPTIONS CRYPTOGRAPHIQUES que 4B consommera.

  * `CryptoInterface` : les hypothèses de résistance aux collisions
    (injectivité de la liaison-contenu) fournies, JAMAIS prouvées ici,
    JAMAIS déclarées comme `axiom`. Elles réutilisent conceptuellement le
    modèle `Obsidia.CryptoAssumptions` (injectivité structurelle sur un
    `Hash` inductif) ; ici l'abstraction porte sur le sha256 réel.
  * `RuntimeRefinement` : la carte formelle des concepts runtime
    (`MissionActionPlan`, `HumanMissionAuthorization`,
    `DerivedActionAuthorityWitness`, `MissionProjection`,
    `ExecutionEnvelope`, record KX108_PRE) — 4D fournira les vecteurs
    canoniques de conformité.

  Aucune dépendance d'exécution Python. Ne modifie pas la souveraineté
  KX108. N'accorde aucune autorité runtime.
-/
import Obsidia.MissionAuthority.Invariants
import Obsidia.CryptoAssumptions

namespace Obsidia.MissionAuthority.Refinement

open Obsidia.MissionAuthority
open Obsidia.MissionAuthority.Invariants

/-- ASSOMPTIONS CRYPTOGRAPHIQUES bundlées (fournies à 4B, non prouvées).
    `eahOf` = calcul abstrait de `execution_authority_hash`. Les champs
    `*_injective` expriment la résistance aux collisions sur le matériel
    d'autorité — hypothèse, pas théorème. -/
structure CryptoInterface where
  eahOf : ExecutionEnvelope → EAH
  /-- CRYPTOGRAPHIC_ASSUMPTION : deux enveloppes de même EAH partagent
      l'action liée (le matériel d'autorité par-enfant). -/
  eah_action_faithful :
    ∀ e1 e2 : ExecutionEnvelope, eahOf e1 = eahOf e2 → e1.action = e2.action
  /-- CRYPTOGRAPHIC_ASSUMPTION : l'identité de témoin lie son matériel. -/
  witness_id_faithful :
    ∀ w1 w2 : ActionWitness,
      w1.id = w2.id → witnessBoundMaterial w1 = witnessBoundMaterial w2
  /-- CRYPTOGRAPHIC_ASSUMPTION : l'identité HMA lie son plan exact. -/
  hma_id_faithful :
    ∀ h1 h2 : MissionAuthorization, h1.id = h2.id → h1.planHash = h2.planHash

/-- Carte de raffinement : relation abstraite « cette trace produit cette
    mutation gouvernée » (4D : vecteurs canoniques runtime↔Lean). -/
structure RuntimeRefinement where
  producedBy : MissionProjection → List Event → GovernedMutation → Prop
  /-- Le mode runtime courant reste Stage 3. -/
  runtimeAuthorityMode : AuthorityMode
  runtime_is_stage3 :
    runtimeAuthorityMode = AuthorityMode.PER_ACTION_HUMAN_EAH

/-- Énoncé central RAFFINÉ (à prouver en 4B sous `C` et `R`). -/
def CentralTheoremStatement (C : CryptoInterface) (R : RuntimeRefinement) : Prop :=
  EveryMutationHasHumanMissionAndKXWitnessSpec C.eahOf R.producedBy

/-- Second énoncé central RAFFINÉ. -/
def SecondCentralTheoremStatement : Prop :=
  DerivedScopeSubsetHumanAuthorizedScopeSpec

/-- Correspondances de champs formel ↔ runtime, documentées pour 4D.
    (Structure vide de preuve : purement une checklist de conformité.) -/
structure ConformanceChecklist where
  planHash_matches_stage3d_plan_hash            : Bool
  actionId_matches_stage3d_action_id            : Bool
  eah_matches_compute_execution_authority_hash  : Bool
  scope_targets_match_allowed_target_paths      : Bool
  scope_ops_match_allowed_operation_shapes      : Bool
  maxActions_matches_scope_max_actions          : Bool
  executedActionIndex_matches_executed_count    : Bool
  snapshottedActions_match_stage3b_projection   : Bool
  revoked_matches_mission_authority_revoked_log : Bool
  kxPre_matches_run_and_persist_kx108_pre       : Bool
  deriving Repr

end Obsidia.MissionAuthority.Refinement
