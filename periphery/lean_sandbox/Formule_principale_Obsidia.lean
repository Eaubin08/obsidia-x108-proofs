namespace Obsidia
namespace Formule_principale_Obsidia

structure ObsidiaState where
  sigma : Nat
  epsilon : Nat
  chi : Bool
  lambda_load : Nat
  lambda_max : Nat
  phi_ready : Bool
  energy : Nat
  cost : Nat

def coherence_ok (s : ObsidiaState) : Prop :=
  s.epsilon <= s.sigma

def guard_ok (s : ObsidiaState) : Prop :=
  s.chi = true

def lambda_ok (s : ObsidiaState) : Prop :=
  s.lambda_load <= s.lambda_max

def phi_ok (s : ObsidiaState) : Prop :=
  s.phi_ready = true

def energy_ok (s : ObsidiaState) : Prop :=
  s.cost <= s.energy

def obsidia_state_valid (s : ObsidiaState) : Prop :=
  And (energy_ok s) (And (guard_ok s) (And (coherence_ok s) (And (lambda_ok s) (phi_ok s))))

def m_obs_ready (s : ObsidiaState) : Prop :=
  obsidia_state_valid s

def zero_obsidia_state : ObsidiaState :=
  { sigma := 0, epsilon := 0, chi := true, lambda_load := 0, lambda_max := 0, phi_ready := true, energy := 0, cost := 0 }

theorem obsidia_state_valid_intro
    (s : ObsidiaState)
    (he : energy_ok s)
    (hg : guard_ok s)
    (hc : coherence_ok s)
    (hl : lambda_ok s)
    (hp : phi_ok s) :
    obsidia_state_valid s :=
  And.intro he (And.intro hg (And.intro hc (And.intro hl hp)))

theorem energy_ok_from_obsidia_state_valid
    (s : ObsidiaState)
    (h : obsidia_state_valid s) :
    energy_ok s :=
  h.left

theorem guard_ok_from_obsidia_state_valid
    (s : ObsidiaState)
    (h : obsidia_state_valid s) :
    guard_ok s :=
  h.right.left

theorem coherence_ok_from_obsidia_state_valid
    (s : ObsidiaState)
    (h : obsidia_state_valid s) :
    coherence_ok s :=
  h.right.right.left

theorem lambda_ok_from_obsidia_state_valid
    (s : ObsidiaState)
    (h : obsidia_state_valid s) :
    lambda_ok s :=
  h.right.right.right.left

theorem phi_ok_from_obsidia_state_valid
    (s : ObsidiaState)
    (h : obsidia_state_valid s) :
    phi_ok s :=
  h.right.right.right.right

theorem m_obs_ready_from_obsidia_state_valid
    (s : ObsidiaState)
    (h : obsidia_state_valid s) :
    m_obs_ready s :=
  h

theorem zero_obsidia_energy_ok :
    energy_ok zero_obsidia_state :=
  Nat.le_refl 0

theorem zero_obsidia_guard_ok :
    guard_ok zero_obsidia_state :=
  rfl

theorem zero_obsidia_coherence_ok :
    coherence_ok zero_obsidia_state :=
  Nat.le_refl 0

theorem zero_obsidia_lambda_ok :
    lambda_ok zero_obsidia_state :=
  Nat.le_refl 0

theorem zero_obsidia_phi_ok :
    phi_ok zero_obsidia_state :=
  rfl

theorem zero_obsidia_state_valid :
    obsidia_state_valid zero_obsidia_state :=
  And.intro (Nat.le_refl 0) (And.intro rfl (And.intro (Nat.le_refl 0) (And.intro (Nat.le_refl 0) rfl)))

end Formule_principale_Obsidia
end Obsidia
