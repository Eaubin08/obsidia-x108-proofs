-- Rythme_Decisionnel -- r(t) frequence de decision modulee par sigma, lambda, urgence et saturation
-- Status : PROVISIONAL scaffold -- Palier 5 item 98/134
-- SOURCE_COVERAGE: rythme_decisionnel | frequence_decision | r_max | sigma_t | lambda_t
--                  urgence_U | queue_saturation | ralentissement | saturation | r_admissible
--                  decision_allowed | tempo_slowed | kernel_boundary
-- PROVISIONAL_BOUNDARY: frequence continue approchee par flags Bool et entiers Nat.
--   r(t) = r_max * Sigma(t) / (1 + lambda(t)) avec modulation par urgence_U et queue_saturation.
--   Plus lambda_t ou saturation monte, plus le rythme ralentit.
--   Le rythme decisionnel module la cadence ; il ne decide pas a la place du kernel.

namespace Obsidia
namespace RythmeDecisionnel

structure RythmeState where
  r_max : Nat
  sigma_t : Nat
  lambda_t : Nat
  urgence_U : Nat
  queue_saturation : Bool
  saturation_detected : Bool
  tempo_slowed : Bool
  decision_allowed : Bool
  r_admissible : Bool
  kernel_boundary : Bool

def rythme_admissible (r : RythmeState) : Prop :=
  And (r.r_admissible = true)
  (And (r.decision_allowed = true)
  (And (r.saturation_detected = false)
       (r.kernel_boundary = true)))

def rythme_ralenti (r : RythmeState) : Prop :=
  And (r.tempo_slowed = true)
      (r.queue_saturation = true)

def rythme_sature (r : RythmeState) : Prop :=
  r.saturation_detected = true

def rythme_kernel_safe (r : RythmeState) : Prop :=
  And (rythme_admissible r)
      (r.kernel_boundary = true)

def rythme_canonique : RythmeState :=
  { r_max := 10,
    sigma_t := 80,
    lambda_t := 1,
    urgence_U := 20,
    queue_saturation := false,
    saturation_detected := false,
    tempo_slowed := false,
    decision_allowed := true,
    r_admissible := true,
    kernel_boundary := true }

def rythme_sature_exemple : RythmeState :=
  { r_max := 10,
    sigma_t := 20,
    lambda_t := 9,
    urgence_U := 90,
    queue_saturation := true,
    saturation_detected := true,
    tempo_slowed := true,
    decision_allowed := false,
    r_admissible := false,
    kernel_boundary := true }

theorem rythme_canonique_admissible : rythme_admissible rythme_canonique :=
  And.intro rfl (And.intro rfl (And.intro rfl rfl))

theorem rythme_canonique_kernel_safe : rythme_kernel_safe rythme_canonique :=
  And.intro rythme_canonique_admissible rfl

theorem rythme_sature_exemple_detected : rythme_sature rythme_sature_exemple :=
  rfl

theorem rythme_ralenti_from_flags
    (r : RythmeState)
    (h : rythme_ralenti r) :
    r.tempo_slowed = true :=
  h.left

theorem rythme_admissible_has_boundary
    (r : RythmeState)
    (h : rythme_admissible r) :
    r.kernel_boundary = true :=
  h.right.right.right

theorem rythme_admissible_allows_decision
    (r : RythmeState)
    (h : rythme_admissible r) :
    r.decision_allowed = true :=
  h.right.left

end RythmeDecisionnel
end Obsidia
