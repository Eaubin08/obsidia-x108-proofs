namespace Obsidia
namespace Chantier_M2_Phi

structure PhiTState where
  t : Nat
  phi : Nat
  threshold : Nat
  coherent : Bool

def time_ordered (a b : PhiTState) : Prop :=
  a.t <= b.t

def phi_bounded (s : PhiTState) : Prop :=
  s.phi <= s.threshold

def phi_coherent (s : PhiTState) : Prop :=
  s.coherent = true

def phi_t_admissible (a b : PhiTState) : Prop :=
  time_ordered a b ∧ phi_bounded b ∧ phi_coherent b

theorem phi_t_admissible_intro
    (a b : PhiTState)
    (ht : time_ordered a b)
    (hb : phi_bounded b)
    (hc : phi_coherent b) :
    phi_t_admissible a b :=
  And.intro ht (And.intro hb hc)

theorem time_ordered_from_phi_t_admissible
    (a b : PhiTState)
    (h : phi_t_admissible a b) :
    time_ordered a b :=
  h.left

theorem phi_bounded_from_phi_t_admissible
    (a b : PhiTState)
    (h : phi_t_admissible a b) :
    phi_bounded b :=
  h.right.left

theorem coherent_from_phi_t_admissible
    (a b : PhiTState)
    (h : phi_t_admissible a b) :
    phi_coherent b :=
  h.right.right

end Chantier_M2_Phi
end Obsidia
