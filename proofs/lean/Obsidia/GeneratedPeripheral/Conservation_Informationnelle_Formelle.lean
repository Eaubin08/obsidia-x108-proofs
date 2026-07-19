-- Conservation_Informationnelle_Formelle -- conservation formelle des flux d information
-- Status : PROVISIONAL scaffold -- Palier 7 item 121/134
-- SOURCE_COVERAGE: conservation_informationnelle_formelle | i_input | i_output
--                  i_memory | delta_i | loss_bound | trace_informationnelle
--                  balance_equation | no_untracked_loss | audit_conservation
--                  replay_conservation | conservation_ready | proof_trace_ready
--                  kernel_boundary | non_sovereign_conservation
-- PROVISIONAL_BOUNDARY: la conservation informationnelle formelle est encodee par flags Bool.
--   Elle relie information entrante, sortante, memorisee et variation delta_i.
--   La balance exige trace, audit, replay et absence de perte non tracee.
--   Cette loi certifie la conservation, mais ne decide aucune action.

namespace Obsidia
namespace ConservationInformationnelleFormelle

structure ConservationInfoState where
  i_input : Bool
  i_output : Bool
  i_memory : Bool
  delta_i : Bool
  loss_bound : Bool
  trace_informationnelle : Bool
  balance_equation : Bool
  no_untracked_loss : Bool
  audit_conservation : Bool
  replay_conservation : Bool
  conservation_ready : Bool
  proof_trace_ready : Bool
  kernel_boundary : Bool
  non_sovereign_conservation : Bool

def information_flow_ready (s : ConservationInfoState) : Prop :=
  And (s.i_input = true)
  (And (s.i_output = true)
  (And (s.i_memory = true)
       (s.delta_i = true)))

def conservation_balance_ready (s : ConservationInfoState) : Prop :=
  And (s.balance_equation = true)
  (And (s.loss_bound = true)
       (s.no_untracked_loss = true))

def conservation_trace_ready (s : ConservationInfoState) : Prop :=
  And (s.trace_informationnelle = true)
  (And (s.audit_conservation = true)
  (And (s.replay_conservation = true)
  (And (s.conservation_ready = true)
       (s.proof_trace_ready = true))))

def conservation_informationnelle_ready (s : ConservationInfoState) : Prop :=
  And (information_flow_ready s)
  (And (conservation_balance_ready s)
       (conservation_trace_ready s))

def conservation_informationnelle_admissible (s : ConservationInfoState) : Prop :=
  And (conservation_informationnelle_ready s)
  (And (s.kernel_boundary = true)
       (s.non_sovereign_conservation = true))

def conservation_informationnelle_canonique : ConservationInfoState :=
  { i_input := true,
    i_output := true,
    i_memory := true,
    delta_i := true,
    loss_bound := true,
    trace_informationnelle := true,
    balance_equation := true,
    no_untracked_loss := true,
    audit_conservation := true,
    replay_conservation := true,
    conservation_ready := true,
    proof_trace_ready := true,
    kernel_boundary := true,
    non_sovereign_conservation := true }

theorem conservation_informationnelle_canonique_admissible :
    conservation_informationnelle_admissible conservation_informationnelle_canonique :=
  And.intro
    (And.intro
      (And.intro rfl
        (And.intro rfl
          (And.intro rfl rfl)))
      (And.intro
        (And.intro rfl
          (And.intro rfl rfl))
        (And.intro rfl
          (And.intro rfl
            (And.intro rfl
              (And.intro rfl rfl))))))
    (And.intro rfl rfl)

theorem conservation_has_information_flow
    (s : ConservationInfoState)
    (h : conservation_informationnelle_admissible s) :
    information_flow_ready s :=
  h.left.left

theorem conservation_has_balance
    (s : ConservationInfoState)
    (h : conservation_informationnelle_admissible s) :
    conservation_balance_ready s :=
  h.left.right.left

theorem conservation_has_trace
    (s : ConservationInfoState)
    (h : conservation_informationnelle_admissible s) :
    conservation_trace_ready s :=
  h.left.right.right

theorem conservation_has_kernel_boundary
    (s : ConservationInfoState)
    (h : conservation_informationnelle_admissible s) :
    s.kernel_boundary = true :=
  h.right.left

theorem conservation_is_non_sovereign
    (s : ConservationInfoState)
    (h : conservation_informationnelle_admissible s) :
    s.non_sovereign_conservation = true :=
  h.right.right

theorem conservation_balance_has_no_untracked_loss
    (s : ConservationInfoState)
    (h : conservation_balance_ready s) :
    s.no_untracked_loss = true :=
  h.right.right

theorem conservation_trace_has_replay
    (s : ConservationInfoState)
    (h : conservation_trace_ready s) :
    s.replay_conservation = true :=
  h.right.right.left

end ConservationInformationnelleFormelle
end Obsidia
