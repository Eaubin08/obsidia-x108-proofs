/-
  Obsidia / MissionAuthority / ConformanceVectors.lean
  ===================================================
  STAGE 4D — FORMAL_LAYER — NON_RUNTIME — couche de CONFORMANCE.

  Oracle EXÉCUTABLE : `decide` sur les prédicats formels COMMITTÉS de
  Stage 4A/4B (`Invariants.ActionWitnessValid`, `Invariants.StaticActionCovered`,
  `scopeLE`, `actionIdOfOrdinal`), évalué sur une PROJECTION SÉMANTIQUE
  CANONIQUE (`CanonicalVector`).

  Il NE MODIFIE AUCUNE sémantique 4A/4B — il les CONSOMME via `decide`.
  Aucune réponse « attendue » n'est saisie ici : chaque verdict est
  CALCULÉ par les prédicats committés.

  Il N'IMPLÉMENTE PAS SHA-256 : les identités sont des `Nat` (mapping
  explicite runtime↔Nat tenu côté Python). La liaison EAH est modélisée
  par l'égalité SÉMANTIQUE `witnessEAH = envelopeEAH`, jamais un hachage.

  Aucun `sorry`, `admit`, `axiom` ; `CryptoInterface` non consommée.
-/
import Obsidia.MissionAuthority.Invariants

namespace Obsidia.MissionAuthority.Conformance

open Obsidia.MissionAuthority
open Obsidia.MissionAuthority.Invariants

/-- Verdict sémantique NORMALISÉ (vocabulaire minimal partagé Lean↔runtime). -/
inductive Verdict where
  | allowable
  | scopeAmplification
  | planMismatch
  | actionMismatch
  | eahMismatch
  | staleBase
  | dependencyUnsatisfied
  | budgetExceeded
  | revoked
  | planCompleted
  | hmaInvalid
  deriving DecidableEq, Repr

def Verdict.toString : Verdict → String
  | .allowable             => "ALLOWABLE"
  | .scopeAmplification    => "SCOPE_AMPLIFICATION"
  | .planMismatch          => "PLAN_MISMATCH"
  | .actionMismatch        => "ACTION_MISMATCH"
  | .eahMismatch           => "EAH_MISMATCH"
  | .staleBase             => "STALE_BASE"
  | .dependencyUnsatisfied => "DEPENDENCY_UNSATISFIED"
  | .budgetExceeded        => "BUDGET_EXCEEDED"
  | .revoked               => "REVOKED"
  | .planCompleted         => "PLAN_COMPLETED"
  | .hmaInvalid            => "HMA_INVALID"

/-- Ligne de plan canonique. -/
structure PlanRow where
  ordinal          : Nat
  actionId         : Nat
  target           : Nat
  operation        : Nat
  sourceCommit     : Nat
  sourceHist       : Nat
  testContractHash : Nat
  actionBaseSha    : Nat
  dependencyOrds   : List Nat
  deriving Repr

/-- Projection sémantique canonique commune Lean↔runtime (§6). Toutes les
    identités sont des `Nat`. -/
structure CanonicalVector where
  vectorId          : String
  -- HMA
  hmaId             : Nat
  hmaIssuerHuman    : Bool
  hmaDomainHma      : Bool
  hmaPlanId         : Nat
  hmaPlanHash       : Nat
  hmaMissionId      : Nat
  hmaGenesisHash    : Nat
  hmaTargets        : List Nat
  hmaOps            : List Nat
  hmaMaxActions     : Nat
  hmaMaxRetries     : Nat
  genTargets        : List Nat
  genOps            : List Nat
  genMaxActions     : Nat
  genMaxRetries     : Nat
  repoId            : Nat
  branchId          : Nat
  canonicalBase     : Nat
  depCommitment     : Nat
  -- plan
  planId            : Nat
  planHash          : Nat
  planRows          : List PlanRow
  -- DAAW
  daawDomainDaaw    : Bool
  daawNonSovereign  : Bool
  daawMissionAuthId : Nat
  daawMissionId     : Nat
  daawPlanId        : Nat
  daawPlanHash      : Nat
  daawActionId      : Nat
  daawOrdinal       : Nat
  daawOperation     : Nat
  daawTarget        : Nat
  daawSourceCommit  : Nat
  daawSourceHist    : Nat
  daawTch           : Nat
  daawDepOrds       : List Nat
  daawActionBase    : Nat
  daawExecIndex     : Nat
  daawEAH           : Nat
  daawTargets       : List Nat
  daawOps           : List Nat
  daawMaxActions    : Nat
  daawMaxRetries    : Nat
  daawRepoId        : Nat
  daawBranchId      : Nat
  daawCanonicalBase : Nat
  daawDepCommitment : Nat
  -- projection mission
  missionTip        : Nat
  snapshotted       : List Nat
  executedIndex     : Nat
  phaseCompleted    : Bool
  revokedList       : List Nat
  -- enveloppe
  envelopeEAH       : Nat
  deriving Repr

/-! ### Instances de décidabilité — pont d'ÉVALUATION des prédicats formels
    committés (aucune redéfinition sémantique : `unfold` + `infer_instance`
    sur les `def : Prop` de Stage 4A). -/

deriving instance DecidableEq for SourceIdentity
deriving instance DecidableEq for Action
deriving instance DecidableEq for AuthorityScope
deriving instance DecidableEq for MissionAuthorization
deriving instance DecidableEq for PlanActionDescriptor
deriving instance DecidableEq for MissionPlan
deriving instance DecidableEq for MissionProjection
deriving instance DecidableEq for ExecutionEnvelope
deriving instance DecidableEq for ActionWitness

instance instDecidableSubOf {α : Type} [DecidableEq α] (xs ys : List α) :
    Decidable (subOf xs ys) := by
  unfold subOf; infer_instance

instance instDecidableScopeLE (a b : AuthorityScope) : Decidable (scopeLE a b) := by
  unfold scopeLE; infer_instance

instance instDecidableStaticActionCovered
    (h : MissionAuthorization) (plan : MissionPlan) (a : Action) :
    Decidable (Invariants.StaticActionCovered h plan a) := by
  unfold Invariants.StaticActionCovered; infer_instance

instance instDecidableDepExists
    (plan : MissionPlan) (o : Ordinal) (proj : MissionProjection) :
    Decidable (∃ depId, actionIdOfOrdinal plan o = some depId ∧
                        depId ∈ proj.snapshottedActions) :=
  match actionIdOfOrdinal plan o with
  | none => isFalse (fun ⟨_, hd, _⟩ => by cases hd)
  | some d =>
    if hmem : d ∈ proj.snapshottedActions then
      isTrue ⟨d, rfl, hmem⟩
    else
      isFalse (fun ⟨_, hd, hm⟩ => by cases hd; exact hmem hm)

instance instDecidableDynamicActionEligible
    (proj : MissionProjection) (h : MissionAuthorization)
    (plan : MissionPlan) (a : Action) :
    Decidable (Invariants.DynamicActionEligible proj h plan a) := by
  unfold Invariants.DynamicActionEligible; infer_instance

instance instDecidableActionWitnessValid
    (f : ExecutionEnvelope → EAH) (w : ActionWitness) (h : MissionAuthorization)
    (plan : MissionPlan) (proj : MissionProjection) (env : ExecutionEnvelope) :
    Decidable (Invariants.ActionWitnessValid f w h plan proj env) := by
  unfold Invariants.ActionWitnessValid; infer_instance

private def opOf (_n : Nat) : Operation := Operation.updateTargetFromSource

private def mkAction (aid ord _op tgt sc sh tch base : Nat) (deps : List Nat) : Action :=
  { actionId := ⟨aid⟩, ordinal := ord, operation := opOf _op, target := ⟨tgt⟩,
    source := { commit := ⟨sc⟩, historicalPath := sh, blob := ⟨0⟩, contentSha256 := ⟨0⟩ },
    testContractHash := ⟨tch⟩, dependencyOrdinals := deps, actionBaseSha := ⟨base⟩ }

private def mkScope (tgts ops : List Nat) (ph ma mr repo br base dep : Nat) : AuthorityScope :=
  { allowedTargets := tgts.map (fun t => (⟨t⟩ : Target)),
    allowedOperations := ops.map opOf,
    maxActions := ma, maxRetriesPerAction := mr,
    planHash := ⟨ph⟩, repositoryIdentity := ⟨repo⟩, branchIdentity := ⟨br⟩,
    canonicalBaseSha := ⟨base⟩, dependencyCommitment := ⟨dep⟩ }

private def toHMA (cv : CanonicalVector) : MissionAuthorization :=
  { id := ⟨cv.hmaId⟩,
    domain := if cv.hmaDomainHma then DomainTag.hmaV0 else DomainTag.daawV0,
    issuer := if cv.hmaIssuerHuman then Issuer.HUMAN else Issuer.STACK,
    schemaVersion := 1,
    missionId := ⟨cv.hmaMissionId⟩, missionGenesisHash := ⟨cv.hmaGenesisHash⟩,
    planId := ⟨cv.hmaPlanId⟩, planHash := ⟨cv.hmaPlanHash⟩,
    scope := mkScope cv.hmaTargets cv.hmaOps cv.hmaPlanHash cv.hmaMaxActions cv.hmaMaxRetries
                     cv.repoId cv.branchId cv.canonicalBase cv.depCommitment,
    authorizationRef := 0 }

private def toWitness (cv : CanonicalVector) : ActionWitness :=
  { id := ⟨0⟩,
    domain := if cv.daawDomainDaaw then DomainTag.daawV0 else DomainTag.hmaV0,
    sovereignty := if cv.daawNonSovereign then Sovereignty.NON_SOVEREIGN else Sovereignty.SOVEREIGN,
    missionAuthId := ⟨cv.daawMissionAuthId⟩, missionId := ⟨cv.daawMissionId⟩,
    planId := ⟨cv.daawPlanId⟩, planHash := ⟨cv.daawPlanHash⟩,
    action := mkAction cv.daawActionId cv.daawOrdinal cv.daawOperation cv.daawTarget
                       cv.daawSourceCommit cv.daawSourceHist cv.daawTch cv.daawActionBase cv.daawDepOrds,
    ordinal := cv.daawOrdinal, operation := opOf cv.daawOperation, target := ⟨cv.daawTarget⟩,
    source := { commit := ⟨cv.daawSourceCommit⟩, historicalPath := cv.daawSourceHist,
                blob := ⟨0⟩, contentSha256 := ⟨0⟩ },
    testContractHash := ⟨cv.daawTch⟩, actionBaseSha := ⟨cv.daawActionBase⟩,
    dependencyDigest := ⟨0⟩, executedActionIndex := cv.daawExecIndex, eah := ⟨cv.daawEAH⟩,
    scope := mkScope cv.daawTargets cv.daawOps cv.daawPlanHash cv.daawMaxActions cv.daawMaxRetries
                     cv.daawRepoId cv.daawBranchId cv.daawCanonicalBase cv.daawDepCommitment }

private def toPlanDescriptor (r : PlanRow) : PlanActionDescriptor :=
  { actionId := ⟨r.actionId⟩, ordinal := r.ordinal,
    action := mkAction r.actionId r.ordinal r.operation r.target r.sourceCommit r.sourceHist
                       r.testContractHash r.actionBaseSha r.dependencyOrds }

private def toPlan (cv : CanonicalVector) : MissionPlan :=
  { planId := ⟨cv.planId⟩, planHash := ⟨cv.planHash⟩,
    actions := cv.planRows.map toPlanDescriptor,
    executionOrder := cv.planRows.map (fun r => (⟨r.actionId⟩ : ActionId)) }

private def toProj (cv : CanonicalVector) : MissionProjection :=
  { missionTip := ⟨cv.missionTip⟩,
    snapshottedActions := cv.snapshotted.map (fun a => (⟨a⟩ : ActionId)),
    executedActionCount := cv.executedIndex,
    phase := if cv.phaseCompleted then MissionPhase.planCompleted else MissionPhase.active,
    revokedAuthorities := cv.revokedList.map (fun x => (⟨x⟩ : ContentHash)),
    planCompleted := cv.phaseCompleted,
    activePlanHash := ⟨cv.planHash⟩ }

private def toEnv (cv : CanonicalVector) : ExecutionEnvelope :=
  { batchExecutionId := 0, childExecutionId := 0,
    action := (toWitness cv).action, preExecContextHash := ⟨0⟩ }

/-- Portée de genèse — la borne que la HMA doit respecter
    (`ValidMissionAuthorization.scopeLE h.scope g.scope`, 4A). -/
private def toGenScope (cv : CanonicalVector) : AuthorityScope :=
  mkScope cv.genTargets cv.genOps cv.hmaPlanHash cv.genMaxActions cv.genMaxRetries
          cv.repoId cv.branchId cv.canonicalBase cv.depCommitment

/-- Verdict sémantique CALCULÉ par les prédicats formels committés. -/
def semanticVerdict (cv : CanonicalVector) : Verdict :=
  let h := toHMA cv
  let w := toWitness cv
  let plan := toPlan cv
  let proj := toProj cv
  let env := toEnv cv
  let eahOf : ExecutionEnvelope → EAH := fun _ => ⟨cv.envelopeEAH⟩
  let genScope := toGenScope cv
  -- `ValidMissionAuthorization` (MissionAuthorization.lean) : émetteur HUMAIN,
  -- domain-sep HMA, portée bornée par la genèse. Le vérificateur runtime les
  -- applique via verify_human_mission_authorization ; l'oracle les applique ici.
  if ¬ decide (h.issuer = Issuer.HUMAN) then
    Verdict.hmaInvalid
  else if ¬ decide (h.domain = DomainTag.hmaV0) then
    Verdict.hmaInvalid
  else if ¬ decide (scopeLE h.scope genScope) then
    Verdict.scopeAmplification            -- HMA hors de la portée de genèse (ValidMissionAuthorization)
  else if decide (Invariants.ActionWitnessValid eahOf w h plan proj env) then
    Verdict.allowable
  else if ¬ decide (w.planHash = h.planHash ∧ plan.planHash = h.planHash) then
    Verdict.planMismatch
  else if ¬ decide (Invariants.StaticActionCovered h plan w.action) then
    Verdict.actionMismatch
  else if ¬ decide (w.actionBaseSha = proj.missionTip) then
    Verdict.staleBase
  else if ¬ decide (w.eah = eahOf env) then
    Verdict.eahMismatch
  else if ¬ decide (∀ o ∈ w.action.dependencyOrdinals,
      ∃ depId, actionIdOfOrdinal plan o = some depId ∧ depId ∈ proj.snapshottedActions) then
    Verdict.dependencyUnsatisfied
  else if ¬ decide (w.executedActionIndex = proj.executedActionCount) then
    Verdict.budgetExceeded            -- index d'action non dérivé du nombre de snapshots
  else if ¬ decide (w.executedActionIndex < h.scope.maxActions) then
    Verdict.budgetExceeded
  else if decide (h.id ∈ proj.revokedAuthorities) then
    Verdict.revoked
  else if decide (proj.phase = MissionPhase.planCompleted) then
    Verdict.planCompleted
  else if ¬ decide (scopeLE w.scope h.scope) then
    Verdict.scopeAmplification
  else
    Verdict.hmaInvalid

/-- Oracle `scopeLE` (miroir de `scope_le` runtime). -/
def scopePairVerdict
    (aT aO : List Nat) (aPh aMa aMr aRepo aBr aBase aDep : Nat)
    (bT bO : List Nat) (bPh bMa bMr bRepo bBr bBase bDep : Nat) : Bool :=
  decide (scopeLE (mkScope aT aO aPh aMa aMr aRepo aBr aBase aDep)
                  (mkScope bT bO bPh bMa bMr bRepo bBr bBase bDep))

/-- Sortie machine-readable pour le pilote Python. -/
def runVectors (cvs : List CanonicalVector) : List (String × String) :=
  cvs.map (fun cv => (cv.vectorId, (semanticVerdict cv).toString))

end Obsidia.MissionAuthority.Conformance
