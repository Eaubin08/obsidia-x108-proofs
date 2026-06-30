-- Conservation_Informationnelle_Basic -- I_in = I_out + delta_I, forme de base
-- Status : PROVISIONAL scaffold -- Palier 6 item 108/134
-- SOURCE_COVERAGE: conservation_informationnelle_basic | I_in | I_out | delta_I
--                  information_balance | conservation_equation | delta_nonnegative
--                  trace_informationnelle | no_information_loss | audit_ready
--                  kernel_boundary | non_sovereign_law
-- PROVISIONAL_BOUNDARY: conservation informationnelle encodee par Nat et flags Bool.
--   Forme de base : I_in = I_out + delta_I avec delta_I nonnegative.
--   delta_I represente information transformee, retenue ou non encore sortie.
--   Cette loi audite la coherence informationnelle, mais ne decide pas l action.

namespace Obsidia
namespace ConservationInformationnelleBasic

structure InfoConservationState where
  I_in : Nat
  I_out : Nat
  delta_I : Nat
  input_known : Bool
  output_known : Bool
  delta_nonnegative : Bool
  conservation_equation : Bool
  information_balance : Bool
  trace_informationnelle : Bool
  no_information_loss : Bool
  audit_ready : Bool
  kernel_boundary : Bool
  non_sovereign_law : Bool

def conservation_inputs_ready (s : InfoConservationState) : Prop :=
  And (s.input_known = true)
  (And (s.output_known = true)
       (s.delta_nonnegative = true))

def conservation_basic_ready (s : InfoConservationState) : Prop :=
  And (conservation_inputs_ready s)
  (And (s.conservation_equation = true)
  (And (s.information_balance = true)
       (s.trace_informationnelle = true)))

def information_conservation_admissible (s : InfoConservationState) : Prop :=
  And (conservation_basic_ready s)
  (And (s.no_information_loss = true)
  (And (s.audit_ready = true)
  (And (s.kernel_boundary = true)
       (s.non_sovereign_law = true))))

def conservation_informationnelle_canonique : InfoConservationState :=
  { I_in := 100,
    I_out := 80,
    delta_I := 20,
    input_known := true,
    output_known := true,
    delta_nonnegative := true,
    conservation_equation := true,
    information_balance := true,
    trace_informationnelle := true,
    no_information_loss := true,
    audit_ready := true,
    kernel_boundary := true,
    non_sovereign_law := true }

theorem conservation_informationnelle_canonique_admissible :
    information_conservation_admissible conservation_informationnelle_canonique :=
  And.intro
    (And.intro
      (And.intro rfl (And.intro rfl rfl))
      (And.intro rfl (And.intro rfl rfl)))
    (And.intro rfl
      (And.intro rfl
        (And.intro rfl rfl)))

theorem conservation_admissible_has_basic
    (s : InfoConservationState)
    (h : information_conservation_admissible s) :
    conservation_basic_ready s :=
  h.left

theorem conservation_basic_has_inputs
    (s : InfoConservationState)
    (h : conservation_basic_ready s) :
    conservation_inputs_ready s :=
  h.left

theorem conservation_admissible_has_kernel_boundary
    (s : InfoConservationState)
    (h : information_conservation_admissible s) :
    s.kernel_boundary = true :=
  h.right.right.right.left

theorem conservation_admissible_is_non_sovereign
    (s : InfoConservationState)
    (h : information_conservation_admissible s) :
    s.non_sovereign_law = true :=
  h.right.right.right.right

theorem conservation_admissible_has_no_loss
    (s : InfoConservationState)
    (h : information_conservation_admissible s) :
    s.no_information_loss = true :=
  h.right.left

theorem conservation_inputs_has_delta_nonnegative
    (s : InfoConservationState)
    (h : conservation_inputs_ready s) :
    s.delta_nonnegative = true :=
  h.right.right

end ConservationInformationnelleBasic
end Obsidia
