/-
  Obsidia / MissionAuthority / ActionWitness.lean
  ==============================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME.

  `Action`, `MissionPlan` (NON_SOUVERAIN), `ExecutionEnvelope`,
  `ActionWitness` (DerivedActionAuthorityWitness — NON_SOUVERAIN).

  Le calcul de `execution_authority_hash` est modélisé comme un PARAMÈTRE
  d'interface `eahOf : ExecutionEnvelope → EAH` — jamais l'implémentation
  sha256, jamais un `opaque`/`axiom`. Sa résistance aux collisions est une
  ASSOMPTION CRYPTOGRAPHIQUE explicite bundlée dans `Refinement.lean`.
-/
import Obsidia.MissionAuthority.MissionAuthorization

namespace Obsidia.MissionAuthority

/-- Action gouvernée — sémantique pertinente pour l'autorité uniquement. -/
structure Action where
  actionId           : ActionId
  ordinal            : Ordinal
  operation          : Operation
  target             : Target
  source             : SourceIdentity
  testContractHash   : TestContractHash
  dependencyOrdinals : List Ordinal
  actionBaseSha      : CommitSha
  deriving Repr

/-- Descripteur d'action tel qu'il figure dans le plan immuable. -/
structure PlanActionDescriptor where
  actionId : ActionId
  ordinal  : Ordinal
  action   : Action
  deriving Repr

/-- Plan d'action de mission immuable (Stage 3D). NON_SOUVERAIN :
    `planIsExecutionAuthority = False`. Aucune fonction d'autorité ne
    naît de la seule existence d'un plan. -/
structure MissionPlan where
  planId         : PlanId
  planHash       : ContentHash
  actions        : List PlanActionDescriptor
  executionOrder : List ActionId
  deriving Repr

/-- Le plan n'est JAMAIS une autorité d'exécution. -/
def planIsExecutionAuthority : Prop := False

/-- action_id associé à un ordinal dans le plan (déterministe). -/
def actionIdOfOrdinal (plan : MissionPlan) (o : Ordinal) : Option ActionId :=
  (plan.actions.find? (fun d => decide (d.ordinal = o))).map (fun d => d.actionId)

/-- Enveloppe d'exécution : abstraction du contenu présenté à
    l'autorisation. `batchExecutionId`/`childExecutionId` abstraits. -/
structure ExecutionEnvelope where
  batchExecutionId   : Nat
  childExecutionId   : Nat
  action             : Action
  preExecContextHash : ContentHash
  deriving Repr

/-- DerivedActionAuthorityWitness — témoin machine NON_SOUVERAIN, par
    action, liant EXACTEMENT : mission, plan, action, base d'action,
    position de budget, EAH, portée. -/
structure ActionWitness where
  id                  : ContentHash
  domain              : DomainTag
  sovereignty         : Sovereignty
  missionAuthId       : ContentHash
  missionId           : MissionId
  planId              : PlanId
  planHash            : ContentHash
  action              : Action
  ordinal             : Ordinal
  operation           : Operation
  target              : Target
  source              : SourceIdentity
  testContractHash    : TestContractHash
  actionBaseSha       : CommitSha
  dependencyDigest    : ContentHash
  executedActionIndex : Nat
  eah                 : EAH
  scope               : AuthorityScope
  deriving Repr

/-- Matériel lié d'un témoin — base de `PerActionAuthorityDistinct` (4B). -/
def witnessBoundMaterial (w : ActionWitness)
    : MissionId × ContentHash × ActionId × Ordinal × EAH :=
  (w.missionId, w.planHash, w.action.actionId, w.action.ordinal, w.eah)

/-- Relation « w dérive de h ». Centrale pour `NoAuthorityAmplification`
    et `DerivedScopeSubsetHumanAuthorizedScope` (4B). Exige
    structurellement la liaison de mission/plan et `scopeLE w.scope
    h.scope`. -/
def DerivedFrom (w : ActionWitness) (h : MissionAuthorization) : Prop :=
  w.domain = DomainTag.daawV0 ∧
  w.sovereignty = Sovereignty.NON_SOVEREIGN ∧
  w.missionAuthId = h.id ∧
  w.missionId = h.missionId ∧
  w.planId = h.planId ∧
  w.planHash = h.planHash ∧
  scopeLE w.scope h.scope

end Obsidia.MissionAuthority
