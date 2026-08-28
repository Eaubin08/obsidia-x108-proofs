/-
  Obsidia / MissionAuthority / Invariants.lean
  ===========================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME.

  DÉFINITIONS de prédicats de couverture + ÉNONCÉS (propositions nommées)
  des 17 invariants de sûreté d'autorité que 4B prouvera.

  IMPORTANT : ce fichier ne PROUVE AUCUN théorème de l'inventaire. Aucun
  `sorry`, aucun `admit`, aucun `axiom`. Chaque invariant est un
  `def …Spec … : Prop`. La distinction LOGICAL_INVARIANTS /
  CRYPTOGRAPHIC_ASSUMPTIONS est explicite : les specs prennent en
  paramètre une fonction `eahOf` abstraite ; l'hypothèse d'injectivité
  (résistance aux collisions) est bundlée séparément dans
  `Refinement.lean` (`CryptoInterface`), jamais ici.
-/
import Obsidia.MissionAuthority.Transition

namespace Obsidia.MissionAuthority.Invariants

open Obsidia.MissionAuthority

/-! ### Prédicats de couverture (statique / dynamique / témoin) -/

/-- Couverture STATIQUE : l'action appartient au plan EXACT autorisé, et
    son opération/cible sont dans la portée. -/
def StaticActionCovered
    (h : MissionAuthorization) (plan : MissionPlan) (a : Action) : Prop :=
  (∃ d ∈ plan.actions, d.action = a ∧ d.actionId = a.actionId) ∧
  plan.planHash = h.planHash ∧
  a.operation ∈ h.scope.allowedOperations ∧
  a.target ∈ h.scope.allowedTargets

/-- Éligibilité DYNAMIQUE : dépendances satisfaites (prédécesseurs
    snapshotés), budget non dépassé, mission active. -/
def DynamicActionEligible
    (proj : MissionProjection) (h : MissionAuthorization)
    (plan : MissionPlan) (a : Action) : Prop :=
  (∀ o ∈ a.dependencyOrdinals,
      ∃ depId, actionIdOfOrdinal plan o = some depId ∧
               depId ∈ proj.snapshottedActions) ∧
  proj.executedActionCount < h.scope.maxActions ∧
  proj.phase = MissionPhase.active

/-- Validité complète d'un témoin d'action vis-à-vis d'une HMA, d'un plan,
    d'une projection et d'une enveloppe. C'est la définition d'« autorisé
    en mode Stage 4 » — sans elle, aucune exécution. -/
def ActionWitnessValid
    (eahOf : ExecutionEnvelope → EAH)
    (w : ActionWitness) (h : MissionAuthorization) (plan : MissionPlan)
    (proj : MissionProjection) (env : ExecutionEnvelope) : Prop :=
  w.domain = DomainTag.daawV0 ∧
  w.sovereignty = Sovereignty.NON_SOVEREIGN ∧
  w.missionAuthId = h.id ∧
  w.missionId = h.missionId ∧
  w.planId = plan.planId ∧
  w.planHash = h.planHash ∧
  plan.planHash = h.planHash ∧
  StaticActionCovered h plan w.action ∧
  DynamicActionEligible proj h plan w.action ∧
  w.actionBaseSha = proj.missionTip ∧                 -- ActionBaseEqualsCurrentMissionTip
  w.eah = eahOf env ∧                                 -- ActionAuthorityBindsExactEAH
  env.action = w.action ∧
  w.executedActionIndex = proj.executedActionCount ∧
  w.executedActionIndex < h.scope.maxActions ∧        -- MissionActionBudgetNeverExceeded
  ¬ (h.id ∈ proj.revokedAuthorities) ∧                -- RevokedMissionCannotAuthorizeAction
  proj.phase ≠ MissionPhase.planCompleted ∧           -- ClosedMissionCannotAuthorizeAction
  scopeLE w.scope h.scope                             -- NoAuthorityAmplification (exigence)

/-- Alias : « ce témoin autorise cette action ». -/
def Authorizes
    (eahOf : ExecutionEnvelope → EAH)
    (w : ActionWitness) (h : MissionAuthorization) (plan : MissionPlan)
    (proj : MissionProjection) (env : ExecutionEnvelope) : Prop :=
  ActionWitnessValid eahOf w h plan proj env

/-! ### Modèle d'évidence (fail-closed) -/

/-- État d'évidence : chaque drapeau est une condition requise. -/
structure EvidenceState where
  hmaPresent    : Bool
  hmaHashValid  : Bool
  daawPresent   : Bool
  daawHashValid : Bool
  planHashMatch : Bool
  actionInPlan  : Bool
  eahMatch      : Bool
  baseMatch     : Bool
  depsSatisfied : Bool
  withinBudget  : Bool
  notRevoked    : Bool
  notClosed     : Bool
  deriving Repr

def EvidenceWellFormed (ev : EvidenceState) : Prop :=
  ev.hmaPresent = true ∧ ev.hmaHashValid = true ∧
  ev.daawPresent = true ∧ ev.daawHashValid = true ∧
  ev.planHashMatch = true ∧ ev.actionInPlan = true ∧
  ev.eahMatch = true ∧ ev.baseMatch = true ∧
  ev.depsSatisfied = true ∧ ev.withinBudget = true ∧
  ev.notRevoked = true ∧ ev.notClosed = true

/-! ### Mutation gouvernée + décision humaine sémantique -/

/-- Mutation de cible gouvernée : porte l'évidence requise par le
    théorème central. -/
structure GovernedMutation where
  action        : Action
  envelope      : ExecutionEnvelope
  eah           : EAH
  missionAuthId : ContentHash
  witnessId     : ContentHash
  kxPre         : KXDecision
  deriving Repr

/-- Mutation bien formée : témoin valide ∧ KX108_PRE = ALLOW liée à
    l'enveloppe exacte (autorité KX108_ONLY). On ne peut PAS construire
    une mutation bien formée sans le `ALLOW` PRE → `KXVetoPreserved`. -/
def WellFormedMutation
    (eahOf : ExecutionEnvelope → EAH)
    (gm : GovernedMutation) (h : MissionAuthorization)
    (w : ActionWitness) (plan : MissionPlan) (proj : MissionProjection) : Prop :=
  ActionWitnessValid eahOf w h plan proj gm.envelope ∧
  gm.action = w.action ∧
  gm.eah = w.eah ∧
  gm.missionAuthId = h.id ∧
  gm.witnessId = w.id ∧
  gm.kxPre.phase = Phase.PRE ∧
  gm.kxPre.gate = Gate.ALLOW ∧
  gm.kxPre.authority = KXAuthority.KX108_ONLY ∧
  gm.kxPre.boundEnvelope = gm.envelope.batchExecutionId

/-- Décision humaine sémantique (résolution de HOLD) — TYPE DISTINCT de
    `MissionAuthorization`, `ActionWitness`, `KXDecision`. -/
structure HumanMissionDecision where
  holdId       : Nat
  chosenOption : Nat
  deriving Repr

def semanticDecisionIsExecutionApproval : HumanMissionDecision → Bool :=
  fun _ => false

/-! ### 17 énoncés d'invariants (à prouver en 4B) -/

/-- 1. Aucun descendant machine n'élargit la portée humaine. -/
def NoAuthorityAmplificationSpec : Prop :=
  ∀ (w : ActionWitness) (h : MissionAuthorization),
    DerivedFrom w h → scopeLE w.scope h.scope

/-- 2. Toute action autorisée est dans la portée du plan exact. -/
def ActionWithinMissionScopeSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env,
    ActionWitnessValid eahOf w h plan proj env →
    StaticActionCovered h plan w.action

/-- 3. `scopeLE` est un préordre (réflexif + transitif). -/
def MissionScopeMonotoneSpec : Prop :=
  (∀ a : AuthorityScope, scopeLE a a) ∧
  (∀ a b c : AuthorityScope, scopeLE a b → scopeLE b c → scopeLE a c)

/-- 4. Un témoin lie un EAH et un seul. -/
def ActionAuthorityBindsExactEAHSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env,
    ActionWitnessValid eahOf w h plan proj env →
    ∀ e', w.eah = e' → e' = eahOf env

/-- 5. Deux actions distinctes ⇒ matériel lié distinct. -/
def PerActionAuthorityDistinctSpec : Prop :=
  ∀ (w1 w2 : ActionWitness),
    w1.action.actionId ≠ w2.action.actionId →
    witnessBoundMaterial w1 ≠ witnessBoundMaterial w2

/-- 6. Un témoin pour l'action A ne peut chevaucher une enveloppe portant
    une action B ≠ A. -/
def CrossActionReplayImpossibleSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env (b : Action),
    ActionWitnessValid eahOf w h plan proj env →
    b ≠ w.action →
    env.action ≠ b

/-- 7. Autorité valide n'implique pas exécution : toute mutation bien
    formée porte un KX108_PRE = ALLOW lié à l'enveloppe exacte. -/
def KXVetoPreservedSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ gm h w plan proj,
    WellFormedMutation eahOf gm h w plan proj →
    gm.kxPre.phase = Phase.PRE ∧
    gm.kxPre.gate = Gate.ALLOW ∧
    gm.kxPre.authority = KXAuthority.KX108_ONLY ∧
    gm.kxPre.boundEnvelope = gm.envelope.batchExecutionId

/-- 8. `executedActionIndex < max_actions` pour tout témoin valide. -/
def MissionActionBudgetNeverExceededSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env,
    ActionWitnessValid eahOf w h plan proj env →
    w.executedActionIndex < h.scope.maxActions

/-- 9. Toute dépendance requise est un prédécesseur snapshoté (KEEP). -/
def DependencyOrderPreservedSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env,
    ActionWitnessValid eahOf w h plan proj env →
    ∀ o ∈ w.action.dependencyOrdinals,
      ∃ depId, actionIdOfOrdinal plan o = some depId ∧
               depId ∈ proj.snapshottedActions

/-- 10. Le tip n'avance que par le chemin KEEP → snapshot. -/
def OnlyKeepAdvancesMissionTipSpec : Prop :=
  ∀ s e s', Step s e s' → s'.missionTip ≠ s.missionTip →
    ∃ a t, e = Event.snapshotCommitted a t

/-- 11. La base d'action égale le tip de mission vérifié courant. -/
def ActionBaseEqualsCurrentMissionTipSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env,
    ActionWitnessValid eahOf w h plan proj env →
    w.actionBaseSha = proj.missionTip

/-- 12. Toute évidence non bien formée ne peut autoriser. -/
def InvalidAuthorityEvidenceCannotAuthorizeSpec
    (AuthByEvidence : EvidenceState → Prop) : Prop :=
  (∀ ev, AuthByEvidence ev → EvidenceWellFormed ev) →
  ∀ ev, ¬ EvidenceWellFormed ev → ¬ AuthByEvidence ev

/-- 13. Une décision sémantique n'est jamais une approbation d'exécution. -/
def SemanticDecisionNonSovereignSpec : Prop :=
  ∀ d : HumanMissionDecision, semanticDecisionIsExecutionApproval d = false

/-- 14. Réviser le plan (hash différent) n'élargit pas la portée
    autorisée sans nouvel HMA. -/
def PlanRevisionCannotExpandAuthorizedScopeSpec : Prop :=
  ∀ (h : MissionAuthorization) (plan' : MissionPlan) (a : Action),
    plan'.planHash ≠ h.planHash →
    ¬ StaticActionCovered h plan' a

/-- 15. Mission close ⇒ aucun témoin valide. -/
def ClosedMissionCannotAuthorizeActionSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env,
    proj.phase = MissionPhase.planCompleted →
    ¬ ActionWitnessValid eahOf w h plan proj env

/-- 16. HMA révoquée ⇒ aucun témoin valide. -/
def RevokedMissionCannotAuthorizeActionSpec (eahOf : ExecutionEnvelope → EAH) : Prop :=
  ∀ w h plan proj env,
    h.id ∈ proj.revokedAuthorities →
    ¬ ActionWitnessValid eahOf w h plan proj env

/-- 17. (central) Pour toute mutation gouvernée d'une trace valide, il
    existe une HMA humaine couvrante ET un KX108_PRE ALLOW lié à
    l'exécution exacte. Paramétré par la fonction `eahOf` et par la
    relation de production runtime (fournie par `Refinement.lean` / 4D). -/
def EveryMutationHasHumanMissionAndKXWitnessSpec
    (eahOf : ExecutionEnvelope → EAH)
    (ProducedBy : MissionProjection → List Event → GovernedMutation → Prop) : Prop :=
  ∀ init t gm,
    ValidTrace init t →
    ProducedBy init t gm →
    ∃ h w plan proj,
      h.issuer = Issuer.HUMAN ∧
      WellFormedMutation eahOf gm h w plan proj

/-- (second central) L'autorité dérivée ne fait que préserver/réduire la
    portée humaine. -/
def DerivedScopeSubsetHumanAuthorizedScopeSpec : Prop :=
  ∀ (w : ActionWitness) (h : MissionAuthorization),
    DerivedFrom w h → scopeLE w.scope h.scope

end Obsidia.MissionAuthority.Invariants
