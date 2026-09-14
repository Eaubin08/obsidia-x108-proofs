/-
  Obsidia / MissionAuthority / Proofs.lean
  =======================================
  STAGE 4B — FORMAL_LAYER — NON_RUNTIME.

  Preuves machine-vérifiées des 16 invariants de sûreté d'autorité + du
  second théorème central, CONTRE les spécifications committées en 4A
  (`Invariants.lean`, `Scope.lean`, `ActionWitness.lean`,
  `Transition.lean`). AUCUN fichier de spécification 4A n'est modifié :
  ces preuves les CONSOMMENT.

  Contraintes : 0 `sorry`, 0 `admit`, 0 `axiom` nouveau, 0 déclaration
  `unsafe`. `CryptoInterface` n'est PAS utilisée : aucun des 16 énoncés
  committés n'en a besoin (voir le rapport 4B — les formes fortes de
  #5/#6 par unicité de sérialisation croisée nécessiteraient
  `CryptoInterface` mais ne sont pas les énoncés committés).

  Le théorème central #17 (`EveryMutationHasHumanMissionAndKXWitnessSpec`)
  N'EST PAS prouvé de bout en bout : il dépend d'une instanciation
  concrète de `RuntimeRefinement.producedBy` fournie en 4D. Le prouver
  ici exigerait d'assumer directement sa conclusion — écarté (§29).
-/
import Obsidia.MissionAuthority.Invariants

namespace Obsidia.MissionAuthority.Proofs

open Obsidia.MissionAuthority
open Obsidia.MissionAuthority.Invariants

/-! ### A / B / C — portée : monotonie + non-amplification -/

/-- 3. `scopeLE` est un préordre. PROOF_CHARACTER = COMPOSITIONAL
    (réutilise `scopeLE_refl` / `scopeLE_trans` committés). -/
theorem missionScopeMonotone : MissionScopeMonotoneSpec :=
  ⟨scopeLE_refl, fun _ _ _ hab hbc => scopeLE_trans hab hbc⟩

theorem missionScopeMonotone' : Invariants.MissionScopeMonotoneSpec :=
  ⟨scopeLE_refl, fun _ _ _ hab hbc => scopeLE_trans hab hbc⟩

/-- 1. NoAuthorityAmplification. PROOF_CHARACTER = DEFINITIONAL
    (`scopeLE w.scope h.scope` est le dernier conjoint committé de
    `DerivedFrom`). -/
theorem noAuthorityAmplification : NoAuthorityAmplificationSpec := by
  intro w h hd
  obtain ⟨_, _, _, _, _, _, hscope⟩ := hd
  exact hscope

/-- (second central) DerivedScopeSubsetHumanAuthorizedScope — énoncé
    identique à #1. PROOF_CHARACTER = DEFINITIONAL. -/
theorem derivedScopeSubsetHumanAuthorizedScope :
    DerivedScopeSubsetHumanAuthorizedScopeSpec := by
  intro w h hd
  obtain ⟨_, _, _, _, _, _, hscope⟩ := hd
  exact hscope

/-! ### D / E — base d'action = tip ; liaison EAH exacte -/

/-- 11. ActionBaseEqualsCurrentMissionTip. PROOF_CHARACTER = DEFINITIONAL. -/
theorem actionBaseEqualsCurrentMissionTip (eahOf : ExecutionEnvelope → EAH) :
    ActionBaseEqualsCurrentMissionTipSpec eahOf := by
  intro w h plan proj env hv
  obtain ⟨_, _, _, _, _, _, _, _, _, hbase, _, _, _, _, _, _, _⟩ := hv
  exact hbase

/-- 4. ActionAuthorityBindsExactEAH. PROOF_CHARACTER = STRUCTURAL
    (transitivité d'égalité ; liaison logique d'UN témoin, pas d'unicité
    cryptographique — `CryptoInterface` non requise). -/
theorem actionAuthorityBindsExactEAH (eahOf : ExecutionEnvelope → EAH) :
    ActionAuthorityBindsExactEAHSpec eahOf := by
  intro w h plan proj env hv e' he'
  obtain ⟨_, _, _, _, _, _, _, _, _, _, heah, _, _, _, _, _, _⟩ := hv
  exact he'.symm.trans heah

/-! ### F — décision sémantique non souveraine -/

/-- 13. SemanticDecisionNonSovereign. PROOF_CHARACTER = DEFINITIONAL. -/
theorem semanticDecisionNonSovereign : SemanticDecisionNonSovereignSpec := by
  intro _d
  rfl

/-! ### G / H — clôture / révocation -/

/-- 15. ClosedMissionCannotAuthorizeAction. PROOF_CHARACTER = STRUCTURAL
    (contradiction avec le conjoint committé `proj.phase ≠ planCompleted`). -/
theorem closedMissionCannotAuthorizeAction (eahOf : ExecutionEnvelope → EAH) :
    ClosedMissionCannotAuthorizeActionSpec eahOf := by
  intro w h plan proj env hclosed hv
  obtain ⟨_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, hnclosed, _⟩ := hv
  exact hnclosed hclosed

/-- 16. RevokedMissionCannotAuthorizeAction. PROOF_CHARACTER = STRUCTURAL. -/
theorem revokedMissionCannotAuthorizeAction (eahOf : ExecutionEnvelope → EAH) :
    RevokedMissionCannotAuthorizeActionSpec eahOf := by
  intro w h plan proj env hrev hv
  obtain ⟨_, _, _, _, _, _, _, _, _, _, _, _, _, _, hnrev, _, _⟩ := hv
  exact hnrev hrev

/-! ### I — révision de plan ⊄ portée sans nouvel HMA -/

/-- 14. PlanRevisionCannotExpandAuthorizedScope. PROOF_CHARACTER =
    STRUCTURAL (contradiction avec le conjoint `plan.planHash = h.planHash`
    de `StaticActionCovered`). -/
theorem planRevisionCannotExpandAuthorizedScope :
    PlanRevisionCannotExpandAuthorizedScopeSpec := by
  intro h plan' a hne hsac
  obtain ⟨_, hph, _, _⟩ := hsac
  exact hne hph

/-! ### J — seul KEEP fait avancer le tip -/

/-- 10. OnlyKeepAdvancesMissionTip. PROOF_CHARACTER = INDUCTIVE
    (analyse de cas sur `Event` contre la relation `Step` committée). -/
theorem onlyKeepAdvancesMissionTip : OnlyKeepAdvancesMissionTipSpec := by
  intro s e s' hstep hne
  cases e with
  | planBound ph =>
      simp only [Step] at hstep; subst hstep; exact absurd rfl hne
  | actionPrepared a =>
      simp only [Step] at hstep; subst hstep; exact absurd rfl hne
  | actionExecuteKeep a ee =>
      simp only [Step] at hstep; subst hstep; exact absurd rfl hne
  | actionExecuteRolledBack a =>
      simp only [Step] at hstep; exact absurd hstep.1 hne
  | actionExecuteQuarantine a =>
      simp only [Step] at hstep; exact absurd hstep.1 hne
  | authorityRevoked hh =>
      simp only [Step] at hstep; exact absurd hstep.2.1 hne
  | planCompleted =>
      simp only [Step] at hstep; exact absurd hstep.2.2.1 hne
  | snapshotCommitted a t =>
      exact ⟨a, t, rfl⟩

theorem onlyKeepAdvancesMissionTip' : Invariants.OnlyKeepAdvancesMissionTipSpec := by
  intro s e s' hstep hne
  cases e with
  | planBound ph =>
      simp only [Step] at hstep; subst hstep; exact absurd rfl hne
  | actionPrepared a =>
      simp only [Step] at hstep; subst hstep; exact absurd rfl hne
  | actionExecuteKeep a ee =>
      simp only [Step] at hstep; subst hstep; exact absurd rfl hne
  | actionExecuteRolledBack a =>
      simp only [Step] at hstep; exact absurd hstep.1 hne
  | actionExecuteQuarantine a =>
      simp only [Step] at hstep; exact absurd hstep.1 hne
  | authorityRevoked hh =>
      simp only [Step] at hstep; exact absurd hstep.2.1 hne
  | planCompleted =>
      simp only [Step] at hstep; exact absurd hstep.2.2.1 hne
  | snapshotCommitted a t =>
      exact ⟨a, t, rfl⟩

/-! ### K — action autorisée ∈ portée du plan exact -/

/-- 2. ActionWithinMissionScope. PROOF_CHARACTER = DEFINITIONAL
    (`StaticActionCovered` est un conjoint committé de `ActionWitnessValid`). -/
theorem actionWithinMissionScope (eahOf : ExecutionEnvelope → EAH) :
    ActionWithinMissionScopeSpec eahOf := by
  intro w h plan proj env hv
  obtain ⟨_, _, _, _, _, _, _, hstatic, _, _, _, _, _, _, _, _, _⟩ := hv
  exact hstatic

/-! ### L — ordre de dépendances préservé -/

/-- 9. DependencyOrderPreserved. PROOF_CHARACTER = DEFINITIONAL
    (premier conjoint de `DynamicActionEligible`, lui-même conjoint de
    `ActionWitnessValid`). -/
theorem dependencyOrderPreserved (eahOf : ExecutionEnvelope → EAH) :
    DependencyOrderPreservedSpec eahOf := by
  intro w h plan proj env hv
  obtain ⟨_, _, _, _, _, _, _, _, hdyn, _, _, _, _, _, _, _, _⟩ := hv
  exact hdyn.1

/-! ### M — évidence invalide ⇒ pas d'autorisation (fail-closed) -/

/-- 12. InvalidAuthorityEvidenceCannotAuthorize. PROOF_CHARACTER =
    STRUCTURAL (contraposée). Quantifié sur la relation d'autorisation
    par évidence. -/
theorem invalidAuthorityEvidenceCannotAuthorize
    (AuthByEvidence : EvidenceState → Prop) :
    InvalidAuthorityEvidenceCannotAuthorizeSpec AuthByEvidence := by
  intro himpl ev hnwf hauth
  exact hnwf (himpl ev hauth)

/-! ### N — veto KX108 préservé -/

/-- 7. KXVetoPreserved. PROOF_CHARACTER = DEFINITIONAL (les 4 conjoints
    KX108_PRE sont des conjoints committés de `WellFormedMutation` ; on ne
    peut PAS construire une mutation bien formée sans le PRE=ALLOW). -/
theorem kxVetoPreserved (eahOf : ExecutionEnvelope → EAH) :
    KXVetoPreservedSpec eahOf := by
  intro gm h w plan proj hwf
  obtain ⟨_, _, _, _, _, hphase, hgate, hauth, hbound⟩ := hwf
  exact ⟨hphase, hgate, hauth, hbound⟩

/-! ### O — budget d'actions jamais dépassé -/

/-- 8. MissionActionBudgetNeverExceeded. PROOF_CHARACTER = DEFINITIONAL
    (`w.executedActionIndex < h.scope.maxActions` est un conjoint
    committé de `ActionWitnessValid`). -/
theorem missionActionBudgetNeverExceeded (eahOf : ExecutionEnvelope → EAH) :
    MissionActionBudgetNeverExceededSpec eahOf := by
  intro w h plan proj env hv
  obtain ⟨_, _, _, _, _, _, _, _, _, _, _, _, _, hbudget, _, _, _⟩ := hv
  exact hbudget

/-! ### P — autorité par action distincte -/

/-- 5. PerActionAuthorityDistinct. PROOF_CHARACTER = STRUCTURAL
    (injectivité de la 3ᵉ projection du 5-uplet `witnessBoundMaterial` —
    `CryptoInterface` NON requise : l'énoncé committé porte sur
    `witnessBoundMaterial`, pas sur `w.id`). -/
theorem perActionAuthorityDistinct : PerActionAuthorityDistinctSpec := by
  intro w1 w2 hne heq
  apply hne
  have h3 : w1.action.actionId = w2.action.actionId :=
    congrArg (fun t => t.2.2.1) heq
  exact h3

/-! ### Q — rejeu cross-action impossible -/

/-- 6. CrossActionReplayImpossible. PROOF_CHARACTER = STRUCTURAL (chaîne
    d'égalités via le conjoint committé `env.action = w.action`).
    L'énoncé committé est la forme « même enveloppe » ; la forme forte par
    unicité de sérialisation croisée (qui nécessiterait
    `CryptoInterface.eah_action_faithful`) n'est pas l'énoncé 4A. -/
theorem crossActionReplayImpossible (eahOf : ExecutionEnvelope → EAH) :
    CrossActionReplayImpossibleSpec eahOf := by
  intro w h plan proj env b hv hbne hcontra
  obtain ⟨_, _, _, _, _, _, _, _, _, _, _, henvact, _, _, _, _, _⟩ := hv
  exact hbne (hcontra.symm.trans henvact)

end Obsidia.MissionAuthority.Proofs

/-! ### #print axioms — TCB de chaque théorème 4B -/
#print axioms Obsidia.MissionAuthority.Proofs.missionScopeMonotone
#print axioms Obsidia.MissionAuthority.Proofs.missionScopeMonotone'
#print axioms Obsidia.MissionAuthority.Proofs.noAuthorityAmplification
#print axioms Obsidia.MissionAuthority.Proofs.derivedScopeSubsetHumanAuthorizedScope
#print axioms Obsidia.MissionAuthority.Proofs.actionBaseEqualsCurrentMissionTip
#print axioms Obsidia.MissionAuthority.Proofs.actionAuthorityBindsExactEAH
#print axioms Obsidia.MissionAuthority.Proofs.semanticDecisionNonSovereign
#print axioms Obsidia.MissionAuthority.Proofs.closedMissionCannotAuthorizeAction
#print axioms Obsidia.MissionAuthority.Proofs.revokedMissionCannotAuthorizeAction
#print axioms Obsidia.MissionAuthority.Proofs.planRevisionCannotExpandAuthorizedScope
#print axioms Obsidia.MissionAuthority.Proofs.onlyKeepAdvancesMissionTip
#print axioms Obsidia.MissionAuthority.Proofs.onlyKeepAdvancesMissionTip'
#print axioms Obsidia.MissionAuthority.Proofs.actionWithinMissionScope
#print axioms Obsidia.MissionAuthority.Proofs.dependencyOrderPreserved
#print axioms Obsidia.MissionAuthority.Proofs.invalidAuthorityEvidenceCannotAuthorize
#print axioms Obsidia.MissionAuthority.Proofs.kxVetoPreserved
#print axioms Obsidia.MissionAuthority.Proofs.missionActionBudgetNeverExceeded
#print axioms Obsidia.MissionAuthority.Proofs.perActionAuthorityDistinct
#print axioms Obsidia.MissionAuthority.Proofs.crossActionReplayImpossible
