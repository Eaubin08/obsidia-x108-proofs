/-
  Obsidia / MissionAuthority / Scope.lean
  ======================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME.

  `AuthorityScope` = l'espace d'actions BORNÉ qu'une autorisation humaine
  de mission décrit. C'est une BORNE SUPÉRIEURE : elle ne choisit ni
  n'exécute aucune action.

  `scopeLE a b` : « a n'est pas plus permissif que b ». Ordre partiel qui
  sous-tend `NoAuthorityAmplification` et
  `DerivedScopeSubsetHumanAuthorizedScope` (prouvés en 4B).

  4A prouve seulement réflexivité et transitivité de `scopeLE` (triviaux,
  requis pour l'ergonomie de l'API). AUCUN théorème de l'inventaire 4B
  n'est prouvé ici.
-/
import Obsidia.MissionAuthority.Types

namespace Obsidia.MissionAuthority

/-- Portée d'autorité bornée. Les chemins/opérations sont des bornes
    d'inclusion ; les budgets des bornes numériques ; le plan, le dépôt,
    la branche, la base canonique et l'engagement de dépendances sont
    liés par ÉGALITÉ EXACTE (aucune substitution). -/
structure AuthorityScope where
  allowedTargets       : List Target
  allowedOperations    : List Operation
  maxActions           : Budget
  maxRetriesPerAction  : RetryBudget
  planHash             : ContentHash
  repositoryIdentity   : RepositoryId
  branchIdentity       : BranchId
  canonicalBaseSha     : CommitSha
  dependencyCommitment : ContentHash
  deriving Repr

/-- « a n'est pas plus permissif que b ». -/
def scopeLE (a b : AuthorityScope) : Prop :=
  subOf a.allowedTargets b.allowedTargets ∧
  subOf a.allowedOperations b.allowedOperations ∧
  a.maxActions ≤ b.maxActions ∧
  a.maxRetriesPerAction ≤ b.maxRetriesPerAction ∧
  a.planHash = b.planHash ∧
  a.repositoryIdentity = b.repositoryIdentity ∧
  a.branchIdentity = b.branchIdentity ∧
  a.canonicalBaseSha = b.canonicalBaseSha ∧
  a.dependencyCommitment = b.dependencyCommitment

theorem scopeLE_refl (a : AuthorityScope) : scopeLE a a := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · exact subOf_refl _
  · exact subOf_refl _
  · exact Nat.le_refl _
  · exact Nat.le_refl _
  · rfl
  · rfl
  · rfl
  · rfl
  · rfl

theorem scopeLE_trans {a b c : AuthorityScope}
    (hab : scopeLE a b) (hbc : scopeLE b c) : scopeLE a c := by
  obtain ⟨t1, o1, m1, r1, p1, rp1, br1, cb1, dc1⟩ := hab
  obtain ⟨t2, o2, m2, r2, p2, rp2, br2, cb2, dc2⟩ := hbc
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · exact subOf_trans t1 t2
  · exact subOf_trans o1 o2
  · exact Nat.le_trans m1 m2
  · exact Nat.le_trans r1 r2
  · exact Eq.trans p1 p2
  · exact Eq.trans rp1 rp2
  · exact Eq.trans br1 br2
  · exact Eq.trans cb1 cb2
  · exact Eq.trans dc1 dc2

/-- Spécification (prouvée en 4B via les deux lemmes ci-dessus, exposée
    ici comme proposition nommée). -/
def MissionScopeMonotoneSpec : Prop :=
  (∀ a : AuthorityScope, scopeLE a a) ∧
  (∀ a b c : AuthorityScope, scopeLE a b → scopeLE b c → scopeLE a c)

end Obsidia.MissionAuthority

#print axioms Obsidia.MissionAuthority.scopeLE_refl
#print axioms Obsidia.MissionAuthority.scopeLE_trans
