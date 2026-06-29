namespace Obsidia
namespace Chantier_M3_Domaine_Admissible

structure DomainAdmissibleState where
sigma : Nat
sigma_min : Nat
energy : Nat
energy_min : Nat
resource : Nat
resource_min : Nat
lambda_load : Nat
lambda_max : Nat

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
{ sigma := 0, sigma_min := 0, energy := 0, energy_min := 0, resource := 0, resource_min := 0, lambda_load := 0, lambda_max := 0 }

theorem domain_admissible_intro
(s : DomainAdmissibleState)
(hs : sigma_ok s)
(he : energy_ok s)
(hr : resource_ok s)
(hl : lambda_ok s) :
domain_admissible s :=
And.intro hs (And.intro he (And.intro hr hl))

theorem sigma_ok_from_domain_admissible
(s : DomainAdmissibleState)
(h : domain_admissible s) :
sigma_ok s :=
h.left

theorem energy_ok_from_domain_admissible
(s : DomainAdmissibleState)
(h : domain_admissible s) :
energy_ok s :=
h.right.left

theorem resource_ok_from_domain_admissible
(s : DomainAdmissibleState)
(h : domain_admissible s) :
resource_ok s :=
h.right.right.left

theorem lambda_ok_from_domain_admissible
(s : DomainAdmissibleState)
(h : domain_admissible s) :
lambda_ok s :=
h.right.right.right

theorem zero_domain_sigma_ok :
sigma_ok zero_domain_state :=
Nat.le_refl 0

theorem zero_domain_energy_ok :
energy_ok zero_domain_state :=
Nat.le_refl 0

theorem zero_domain_resource_ok :
resource_ok zero_domain_state :=
Nat.le_refl 0

theorem zero_domain_lambda_ok :
lambda_ok zero_domain_state :=
Nat.le_refl 0

theorem zero_domain_admissible :
domain_admissible zero_domain_state :=
And.intro (Nat.le_refl 0) (And.intro (Nat.le_refl 0) (And.intro (Nat.le_refl 0) (Nat.le_refl 0)))

end Chantier_M3_Domaine_Admissible
end Obsidia
