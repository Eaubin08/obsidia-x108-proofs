/-
  Obsidia / MissionAuthority / Transition.lean
  ===========================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME.

  `KXDecision`, `MissionProjection`, `Event`, relation `Step`, et traces.

  Ne modélise AUCUN interne de `GuardX108` : seul le fait « l'exécution
  exige une décision PRE = ALLOW liée à l'enveloppe exacte » est requis.
  L'avancée du `missionTip` ne se produit QUE par le chemin
  KEEP → snapshot (patron dérivé de Stage 3B).
-/
import Obsidia.MissionAuthority.ActionWitness

namespace Obsidia.MissionAuthority

/-- Décision KX108 (abstraction du record persisté). L'exécution exige
    `phase = PRE`, `gate = ALLOW`, `authority = KX108_ONLY`, liée à
    l'`batchExecutionId` exact. -/
structure KXDecision where
  phase         : Phase
  gate          : Gate
  boundEnvelope : Nat
  authority     : KXAuthority
  deriving Repr

/-- Vue de projection de mission minimale requise par la vérification
    d'autorité (sous-ensemble de la projection runtime Stage 3D). -/
structure MissionProjection where
  missionTip          : CommitSha
  snapshottedActions  : List ActionId
  executedActionCount : Nat
  phase               : MissionPhase
  revokedAuthorities  : List ContentHash
  planCompleted       : Bool
  activePlanHash      : ContentHash
  deriving Repr

/-- Événements pertinents pour l'autorité. -/
inductive Event where
  | planBound               (planHash : ContentHash)
  | actionPrepared          (a : Action)
  | actionExecuteKeep       (a : Action) (eah : EAH)
  | actionExecuteRolledBack (a : Action)
  | actionExecuteQuarantine (a : Action)
  | snapshotCommitted       (a : Action) (newTip : CommitSha)
  | authorityRevoked        (hmaId : ContentHash)
  | planCompleted
  deriving Repr

/-- Classe l'issue KEEP. -/
def isKeep : Event → Bool
  | Event.actionExecuteKeep _ _ => true
  | _ => false

/-- Un snapshot ne suit légitimement qu'un KEEP de la MÊME action
    (propriété de trace prouvée en 4B ; définie ici). -/
def snapshotFollowsKeep : Event → Event → Prop
  | Event.actionExecuteKeep a _, Event.snapshotCommitted b _ => a.actionId = b.actionId
  | _, _ => False

/-- Relation de transition formelle (projection pertinente pour
    l'autorité). Seul `snapshotCommitted` fait avancer le tip et le
    compteur d'actions exécutées. -/
def Step (s : MissionProjection) (e : Event) (s' : MissionProjection) : Prop :=
  match e with
  | Event.snapshotCommitted a newTip =>
      s'.missionTip = newTip ∧
      s'.snapshottedActions = a.actionId :: s.snapshottedActions ∧
      s'.executedActionCount = s.executedActionCount + 1 ∧
      s'.phase = s.phase ∧
      s'.revokedAuthorities = s.revokedAuthorities ∧
      s'.planCompleted = s.planCompleted
  | Event.actionExecuteRolledBack _ =>
      s'.missionTip = s.missionTip ∧
      s'.snapshottedActions = s.snapshottedActions ∧
      s'.executedActionCount = s.executedActionCount ∧
      s'.phase = s.phase
  | Event.actionExecuteQuarantine _ =>
      s'.missionTip = s.missionTip ∧
      s'.snapshottedActions = s.snapshottedActions ∧
      s'.executedActionCount = s.executedActionCount
  | Event.authorityRevoked h =>
      s'.revokedAuthorities = h :: s.revokedAuthorities ∧
      s'.missionTip = s.missionTip ∧
      s'.snapshottedActions = s.snapshottedActions
  | Event.planCompleted =>
      s'.phase = MissionPhase.planCompleted ∧
      s'.planCompleted = true ∧
      s'.missionTip = s.missionTip ∧
      s'.snapshottedActions = s.snapshottedActions
  | Event.planBound _        => s' = s
  | Event.actionPrepared _   => s' = s
  | Event.actionExecuteKeep _ _ => s' = s

/-- Spécification `OnlyKeepAdvancesMissionTip` (prouvée en 4B) : si le tip
    change lors d'un pas, l'événement est un `snapshotCommitted`, lequel
    ne suit légitimement qu'un KEEP. -/
def OnlyKeepAdvancesMissionTipSpec : Prop :=
  ∀ s e s', Step s e s' → s'.missionTip ≠ s.missionTip →
    ∃ a t, e = Event.snapshotCommitted a t

/-- Enchaînement de pas. -/
def stepsFrom : MissionProjection → List Event → MissionProjection → Prop
  | s, [],      s' => s' = s
  | s, e :: es, s' => ∃ smid, Step s e smid ∧ stepsFrom smid es s'

/-- Trace valide depuis un état initial. -/
def ValidTrace (init : MissionProjection) (t : List Event) : Prop :=
  ∃ final, stepsFrom init t final

end Obsidia.MissionAuthority
