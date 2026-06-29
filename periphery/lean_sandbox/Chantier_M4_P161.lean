namespace Obsidia
namespace Chantier_M4_P161

structure P161ChantierState where
  energy : Nat
  budget : Nat
  calibrated : Bool
  attestation_ready : Bool
  proof_ready : Bool

def energy_budget_ok (s : P161ChantierState) : Prop :=
  s.energy <= s.budget

def calibrated_ok (s : P161ChantierState) : Prop :=
  s.calibrated = true

def attestation_ready_ok (s : P161ChantierState) : Prop :=
  s.attestation_ready = true

def proof_ready_ok (s : P161ChantierState) : Prop :=
  s.proof_ready = true

def p161_chantier_admissible (s : P161ChantierState) : Prop :=
  energy_budget_ok s ∧ calibrated_ok s ∧ attestation_ready_ok s ∧ proof_ready_ok s

theorem p161_chantier_admissible_intro
    (s : P161ChantierState)
    (he : energy_budget_ok s)
    (hc : calibrated_ok s)
    (ha : attestation_ready_ok s)
    (hp : proof_ready_ok s) :
    p161_chantier_admissible s :=
  And.intro he (And.intro hc (And.intro ha hp))

theorem energy_budget_from_p161_chantier
    (s : P161ChantierState)
    (h : p161_chantier_admissible s) :
    energy_budget_ok s :=
  h.left

theorem calibrated_from_p161_chantier
    (s : P161ChantierState)
    (h : p161_chantier_admissible s) :
    calibrated_ok s :=
  h.right.left

theorem attestation_ready_from_p161_chantier
    (s : P161ChantierState)
    (h : p161_chantier_admissible s) :
    attestation_ready_ok s :=
  h.right.right.left

theorem proof_ready_from_p161_chantier
    (s : P161ChantierState)
    (h : p161_chantier_admissible s) :
    proof_ready_ok s :=
  h.right.right.right

end Chantier_M4_P161
end Obsidia
