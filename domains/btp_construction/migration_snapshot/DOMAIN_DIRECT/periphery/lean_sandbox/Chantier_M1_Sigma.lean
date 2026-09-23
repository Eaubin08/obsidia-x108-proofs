namespace Obsidia
namespace Chantier_M1_Sigma

structure SigmaTState where
  t : Nat
  sigma : Nat
  threshold : Nat
  report_ready : Bool

def time_ordered (a b : SigmaTState) : Prop :=
  a.t <= b.t

def sigma_bounded (s : SigmaTState) : Prop :=
  s.sigma <= s.threshold

def sigma_report_ready (s : SigmaTState) : Prop :=
  s.report_ready = true

def sigma_t_admissible (a b : SigmaTState) : Prop :=
  time_ordered a b ∧ sigma_bounded b ∧ sigma_report_ready b

theorem sigma_t_admissible_intro
    (a b : SigmaTState)
    (ht : time_ordered a b)
    (hb : sigma_bounded b)
    (hr : sigma_report_ready b) :
    sigma_t_admissible a b :=
  And.intro ht (And.intro hb hr)

theorem time_ordered_from_sigma_t_admissible
    (a b : SigmaTState)
    (h : sigma_t_admissible a b) :
    time_ordered a b :=
  h.left

theorem sigma_bounded_from_sigma_t_admissible
    (a b : SigmaTState)
    (h : sigma_t_admissible a b) :
    sigma_bounded b :=
  h.right.left

theorem report_ready_from_sigma_t_admissible
    (a b : SigmaTState)
    (h : sigma_t_admissible a b) :
    sigma_report_ready b :=
  h.right.right

end Chantier_M1_Sigma
end Obsidia
