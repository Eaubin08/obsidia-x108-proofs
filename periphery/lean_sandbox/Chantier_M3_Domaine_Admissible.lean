-- Chantier_M3_Domaine_Admissible -- Domaine Admissible D(Sigma,Phi,lambda,chi,E)
-- Status : PROVISIONAL scaffold -- Palier 4 (CHANTIER OUVERT PRIORITAIRE)
-- SOURCE_COVERAGE: domaine_admissible | sigma_borne | phi_structuree
--                  derive_controlee | derive_instable | conditions_sortie
--                  seuil_instabilite | lambda | chantier_prioritaire | fondement_preuves
-- PROVISIONAL_BOUNDARY: domaine D non completement defini (equivalent demi-plan Riemann).
--   D(Sigma, Phi, lambda, chi, E) = etats ou Obsidia peut exister legitimement.
--   Derive controlee : retour dans D possible. Derive instable : hors D trop longtemps.
--   Prioritaire : sans M3, M1/M2/M4 ne sont pas prouvables.

namespace Obsidia
namespace Chantier_M3_Domaine_Admissible

structure DomainAdmissibleState where
  sigma        : Nat
  sigma_min    : Nat
  energy       : Nat
  energy_min   : Nat
  resource     : Nat
  resource_min : Nat
  lambda_load  : Nat
  lambda_max   : Nat

def sigma_ok (s : DomainAdmissibleState) : Prop :=
  s.sigma_min <= s.sigma

def energy_ok (s : DomainAdmissibleState) : Prop :=
  s.energy_min <= s.energy

def resource_ok (s : DomainAdmissibleState) : Prop :=
  s.resource_min <= s.resource

def lambda_ok (s : DomainAdmissibleState) : Prop :=
  s.lambda_load <= s.lambda_max

def domain_admissible (s : DomainAdmissibleState) : Prop :=
  And (sigma_ok s) (And (energy_ok s) (And (resource_ok s) (lambda_ok s)))

def zero_domain_state : DomainAdmissibleState :=
  { sigma := 0, sigma_min := 0, energy := 0, energy_min := 0,
    resource := 0, resource_min := 0, lambda_load := 0, lambda_max := 0 }

theorem domain_admissible_intro
    (s : DomainAdmissibleState)
    (hs : sigma_ok s) (he : energy_ok s)
    (hr : resource_ok s) (hl : lambda_ok s) :
    domain_admissible s :=
  And.intro hs (And.intro he (And.intro hr hl))

theorem sigma_ok_from_domain_admissible
    (s : DomainAdmissibleState) (h : domain_admissible s) :
    sigma_ok s := h.left

theorem zero_domain_admissible :
    domain_admissible zero_domain_state :=
  And.intro (Nat.le_refl 0) (And.intro (Nat.le_refl 0)
    (And.intro (Nat.le_refl 0) (Nat.le_refl 0)))

end Chantier_M3_Domaine_Admissible
end Obsidia
