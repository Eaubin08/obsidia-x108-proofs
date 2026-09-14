/-
  Obsidia / MissionAuthority / MissionAuthorization.lean
  =====================================================
  STAGE 4A — FORMAL_LAYER — NON_RUNTIME.

  `MissionAuthorization` (HMA) = autorité RACINE, émise par l'humain,
  immuable, liée-contenu à EXACTEMENT UN `plan_hash`. BORNE SUPÉRIEURE :
  ne choisit aucune action, n'exécute rien, ne produit AUCUN `ALLOW` KX.

  Séparation structurelle : `MissionAuthorization` ne porte AUCUN champ
  `Gate` / `Phase` / `KXAuthority` ; il n'existe aucune fonction
  `MissionAuthorization → KXDecision`. Distinct de `KXDecision`
  (`Transition.lean`), de `HumanMissionDecision` (`Invariants.lean`) et de
  `ActionWitness` (`ActionWitness.lean`).
-/
import Obsidia.MissionAuthority.Scope

namespace Obsidia.MissionAuthority

/-- Portée de genèse : la borne que le mandat humain de la mission
    respecte lui-même (`genesis.scope`, Stage 3D). Toute HMA valide a
    `scopeLE hma.scope genesis.scope`. -/
structure GenesisScope where
  missionId   : MissionId
  genesisHash : ContentHash
  scope       : AuthorityScope
  deriving Repr

/-- HumanMissionAuthorization. `id` abstrait `hma-<sha256(canon(bound))>` ;
    `authorizationRef` abstrait la `human_authorization_reference`. -/
structure MissionAuthorization where
  id                 : ContentHash
  domain             : DomainTag
  issuer             : Issuer
  schemaVersion      : Nat
  missionId          : MissionId
  missionGenesisHash : ContentHash
  planId             : PlanId
  planHash           : ContentHash
  scope              : AuthorityScope
  authorizationRef   : Nat
  deriving Repr

/-- Révocation append-only : `hma.id` figure dans l'ensemble révoqué
    dérivé du journal de mission (événement `MISSION_AUTHORITY_REVOKED`). -/
def Revoked (h : MissionAuthorization) (revokedIds : List ContentHash) : Prop :=
  h.id ∈ revokedIds

/-- Validité STATIQUE d'une HMA vis-à-vis de la genèse et du plan exact.
    Exprime : émetteur HUMAIN ; domain-sep HMA ; liaison au plan EXACT ;
    portée bornée par la genèse ; non révoquée ; mission ni close ni
    révoquée. (La position dynamique — base, budget, dépendances — est
    portée par `ActionWitnessValid`, cf. `Invariants.lean`.) -/
def ValidMissionAuthorization
    (h : MissionAuthorization) (g : GenesisScope)
    (boundPlanHash : ContentHash)
    (revokedIds : List ContentHash) (phase : MissionPhase) : Prop :=
  h.domain = DomainTag.hmaV0 ∧
  h.issuer = Issuer.HUMAN ∧
  h.missionId = g.missionId ∧
  h.missionGenesisHash = g.genesisHash ∧
  h.planHash = boundPlanHash ∧              -- MISSION_AUTHORIZATION_PLAN_BINDING = EXACT_PLAN_HASH
  h.scope.planHash = boundPlanHash ∧
  scopeLE h.scope g.scope ∧                 -- bornée par la portée de mission/genèse
  ¬ Revoked h revokedIds ∧
  phase ≠ MissionPhase.planCompleted ∧
  phase ≠ MissionPhase.revoked

/-- `MissionAuthorization` n'est jamais une autorité KX : aucune valeur de
    `Gate` ne peut en être extraite (proposition-témoin structurelle,
    triviale, exposée pour l'audit). -/
def MissionAuthorizationCarriesNoGate : Prop :=
  ∀ _h : MissionAuthorization, True

end Obsidia.MissionAuthority
