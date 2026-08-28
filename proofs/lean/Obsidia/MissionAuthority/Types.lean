/-
  Obsidia / MissionAuthority / Types.lean
  ======================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME.

  Vocabulaire formel minimal du modèle d'autorité de mission bornée.
  Ce fichier NE modifie PAS la souveraineté KX108, N'accorde AUCUNE
  autorité runtime, ne dépend d'AUCUNE exécution Python.

  Il modèle la SÉMANTIQUE D'AUTORITÉ, pas chaque champ JSON runtime.
  Les identités (mission, plan, action, hash de contenu, EAH, sha de
  commit) sont abstraites en enveloppes `Nat` distinctes par type — la
  résistance aux collisions du sha256 réel est traitée comme une
  ASSOMPTION CRYPTOGRAPHIQUE explicite dans `Refinement.lean`
  (cf. `Obsidia.CryptoAssumptions`), jamais comme un théorème Lean
  inconditionnel ni comme un `axiom` caché.
-/
namespace Obsidia.MissionAuthority

/-- Identité de mission (abstraction de `mission_id`). -/
structure MissionId where
  val : Nat
  deriving DecidableEq, Repr

/-- Identité de plan (abstraction de `plan_id`). -/
structure PlanId where
  val : Nat
  deriving DecidableEq, Repr

/-- Identité d'action (abstraction de `action_id` dérivé, Stage 3D). -/
structure ActionId where
  val : Nat
  deriving DecidableEq, Repr

/-- Identité de dépôt (abstraction de `repository_identity`). -/
structure RepositoryId where
  val : Nat
  deriving DecidableEq, Repr

/-- Identité de branche (abstraction de `branch_name`). -/
structure BranchId where
  val : Nat
  deriving DecidableEq, Repr

/-- Sha de commit Git 40-hex, abstrait (base canonique, tip de mission,
    base d'action). -/
structure CommitSha where
  val : Nat
  deriving DecidableEq, Repr

/-- Hash de contenu sha256 64-hex, abstrait (`plan_hash`,
    `mission_genesis_record_hash`, `hma_record_hash`, `daaw_record_hash`,
    `dependency_satisfaction_digest`, `source_content_sha256`, blob…). -/
structure ContentHash where
  val : Nat
  deriving DecidableEq, Repr

/-- Hash de `TestContract` (abstraction de `test_contract_hash`, Stage 3D
    `compute_test_contract_hash`). -/
structure TestContractHash where
  val : Nat
  deriving DecidableEq, Repr

/-- `execution_authority_hash` — identité IMMUABLE du contenu d'exécution
    présenté à l'autorisation. Abstraite ici ; la fonction de calcul est
    un paramètre d'interface (cf. `ActionWitness.lean`,
    `Refinement.lean`), jamais l'implémentation sha256. -/
structure EAH where
  val : Nat
  deriving DecidableEq, Repr

/-- Ordinal d'action dans un plan borné. -/
abbrev Ordinal : Type := Nat

/-- Budget d'actions gouvernées (`max_actions`). -/
abbrev Budget : Type := Nat

/-- Budget de retries par action (`max_retries_per_action`). -/
abbrev RetryBudget : Type := Nat

/-- Forme d'opération gouvernée supportée. V0 : une seule. -/
inductive Operation where
  | updateTargetFromSource
  deriving DecidableEq, Repr

/-- Chemin cible, abstrait (`target_path`). -/
structure Target where
  val : Nat
  deriving DecidableEq, Repr

/-- Identité de source immuable (GIT_BLOB : commit + chemin historique +
    blob + sha256 de contenu). -/
structure SourceIdentity where
  commit         : CommitSha
  historicalPath : Nat
  blob           : ContentHash
  contentSha256  : ContentHash
  deriving DecidableEq, Repr

/-- Émetteur d'une autorité. -/
inductive Issuer where
  | HUMAN
  | STACK
  deriving DecidableEq, Repr

/-- Niveau de souveraineté. -/
inductive Sovereignty where
  | SOVEREIGN
  | NON_SOVEREIGN
  deriving DecidableEq, Repr

/-- Décision de porte KX108 (valeurs souveraines de `x108_gate`). -/
inductive Gate where
  | ALLOW
  | HOLD
  | BLOCK
  deriving DecidableEq, Repr

/-- Phase du gate KX108 deux-phases. -/
inductive Phase where
  | PRE
  | POST
  deriving DecidableEq, Repr

/-- Autorité de décision d'exécution — invariant : KX108 seul. -/
inductive KXAuthority where
  | KX108_ONLY
  deriving DecidableEq, Repr

/-- Mode d'autorisation. Le runtime reste `PER_ACTION_HUMAN_EAH` (Stage 3) ;
    `BOUNDED_MISSION_AUTHORITY` est le mode Stage 4, NON activé. -/
inductive AuthorityMode where
  | PER_ACTION_HUMAN_EAH
  | BOUNDED_MISSION_AUTHORITY
  deriving DecidableEq, Repr

/-- Phase de mission suffisante au raisonnement d'autorité. -/
inductive MissionPhase where
  | active
  | revoked
  | planCompleted
  deriving DecidableEq, Repr

/-- Étiquettes de séparation de domaine (domain separation) — les identités
    HMA et DAAW ne peuvent être confondues sémantiquement. -/
inductive DomainTag where
  | hmaV0   -- "OBSIDIA_STAGE4_HMA_V0"
  | daawV0  -- "OBSIDIA_STAGE4_DAAW_V0"
  deriving DecidableEq, Repr

/-- Inclusion de listes (sémantique d'appartenance ⊆), utilisée par
    l'ordre de portée. -/
def subOf {α : Type} (xs ys : List α) : Prop :=
  ∀ a, a ∈ xs → a ∈ ys

theorem subOf_refl {α : Type} (xs : List α) : subOf xs xs := by
  intro a h; exact h

theorem subOf_trans {α : Type} {xs ys zs : List α}
    (h1 : subOf xs ys) (h2 : subOf ys zs) : subOf xs zs := by
  intro a h; exact h2 a (h1 a h)

end Obsidia.MissionAuthority
