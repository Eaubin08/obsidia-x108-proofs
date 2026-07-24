namespace Obsidia
namespace Phi_St

structure PhiState where
  source : Nat
  transformed : Nat
  max_delta : Nat

def phi_delta (s : PhiState) : Nat :=
  if s.source <= s.transformed then s.transformed - s.source else s.source - s.transformed

def phi_forward_or_stable (s : PhiState) : Prop :=
  s.source <= s.transformed

def phi_delta_bounded (s : PhiState) : Prop :=
  phi_delta s <= s.max_delta

def phi_admissible (s : PhiState) : Prop :=
  And (phi_forward_or_stable s) (phi_delta_bounded s)

def identity_phi_state (value bound : Nat) : PhiState :=
  { source := value, transformed := value, max_delta := bound }

theorem phi_admissible_intro
    (s : PhiState)
    (hf : phi_forward_or_stable s)
    (hb : phi_delta_bounded s) :
    phi_admissible s :=
  And.intro hf hb

theorem forward_from_phi_admissible
    (s : PhiState)
    (h : phi_admissible s) :
    phi_forward_or_stable s :=
  h.left

theorem bounded_from_phi_admissible
    (s : PhiState)
    (h : phi_admissible s) :
    phi_delta_bounded s :=
  h.right

theorem identity_phi_delta_zero
    (value bound : Nat) :
    phi_delta (identity_phi_state value bound) = 0 := by
  unfold phi_delta identity_phi_state
  simp

theorem identity_phi_forward_or_stable
    (value bound : Nat) :
    phi_forward_or_stable (identity_phi_state value bound) :=
  Nat.le_refl value

theorem identity_phi_delta_bounded
    (value bound : Nat) :
    phi_delta_bounded (identity_phi_state value bound) := by
  unfold phi_delta_bounded
  rw [identity_phi_delta_zero]
  exact Nat.zero_le bound

theorem identity_phi_admissible
    (value bound : Nat) :
    phi_admissible (identity_phi_state value bound) :=
  And.intro (Nat.le_refl value) (identity_phi_delta_bounded value bound)

end Phi_St
end Obsidia
