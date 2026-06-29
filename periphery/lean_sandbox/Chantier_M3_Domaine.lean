namespace Obsidia
namespace Chantier_M3_Domaine

structure DomaineState where
  domain_ready : Bool
  constraints_ready : Bool
  invariants_ready : Bool
  admissible : Bool

def domain_ready_ok (s : DomaineState) : Prop :=
  s.domain_ready = true

def constraints_ready_ok (s : DomaineState) : Prop :=
  s.constraints_ready = true

def invariants_ready_ok (s : DomaineState) : Prop :=
  s.invariants_ready = true

def domain_admissible_ok (s : DomaineState) : Prop :=
  s.admissible = true

def governed_domain_admissible (s : DomaineState) : Prop :=
  domain_ready_ok s ∧ constraints_ready_ok s ∧ invariants_ready_ok s ∧ domain_admissible_ok s

theorem governed_domain_admissible_intro
    (s : DomaineState)
    (hd : domain_ready_ok s)
    (hc : constraints_ready_ok s)
    (hi : invariants_ready_ok s)
    (ha : domain_admissible_ok s) :
    governed_domain_admissible s :=
  And.intro hd (And.intro hc (And.intro hi ha))

theorem domain_ready_from_governed_domain
    (s : DomaineState)
    (h : governed_domain_admissible s) :
    domain_ready_ok s :=
  h.left

theorem constraints_ready_from_governed_domain
    (s : DomaineState)
    (h : governed_domain_admissible s) :
    constraints_ready_ok s :=
  h.right.left

theorem invariants_ready_from_governed_domain
    (s : DomaineState)
    (h : governed_domain_admissible s) :
    invariants_ready_ok s :=
  h.right.right.left

theorem admissible_from_governed_domain
    (s : DomaineState)
    (h : governed_domain_admissible s) :
    domain_admissible_ok s :=
  h.right.right.right

end Chantier_M3_Domaine
end Obsidia
