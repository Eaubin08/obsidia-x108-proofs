-- Renormalisation_Theories -- changement d echelle et invariants conserves
-- Status : PROVISIONAL scaffold -- Palier 7 item 117/134
-- SOURCE_COVERAGE: renormalisation_theories | scale_local | scale_global | coarse_grain
--                  flow_R | fixed_point_candidate | invariant_preservation
--                  noise_absorption | stability_under_scale | theory_family_ready
--                  renormalisation_ready | proof_trace_ready | kernel_boundary
--                  non_sovereign_renormalisation
-- PROVISIONAL_BOUNDARY: la renormalisation est encodee par flags Bool.
--   Elle relie echelle locale, echelle globale, coarse graining et flux R.
--   Un point fixe candidat stabilise la lecture entre echelles.
--   La theorie conserve les invariants et absorbe le bruit,
--   mais ne produit aucune action souveraine sans kernel_boundary.

namespace Obsidia
namespace RenormalisationTheories

structure RenormalisationState where
  scale_local : Bool
  scale_global : Bool
  coarse_grain : Bool
  flow_R : Bool
  fixed_point_candidate : Bool
  invariant_preservation : Bool
  noise_absorption : Bool
  stability_under_scale : Bool
  theory_family_ready : Bool
  renormalisation_ready : Bool
  proof_trace_ready : Bool
  kernel_boundary : Bool
  non_sovereign_renormalisation : Bool

def scale_bridge_ready (s : RenormalisationState) : Prop :=
  And (s.scale_local = true)
  (And (s.scale_global = true)
  (And (s.coarse_grain = true)
       (s.flow_R = true)))

def fixed_point_scale_ready (s : RenormalisationState) : Prop :=
  And (s.fixed_point_candidate = true)
  (And (s.invariant_preservation = true)
       (s.stability_under_scale = true))

def renormalisation_theory_ready (s : RenormalisationState) : Prop :=
  And (scale_bridge_ready s)
  (And (fixed_point_scale_ready s)
  (And (s.noise_absorption = true)
  (And (s.theory_family_ready = true)
  (And (s.renormalisation_ready = true)
       (s.proof_trace_ready = true)))))

def renormalisation_admissible (s : RenormalisationState) : Prop :=
  And (renormalisation_theory_ready s)
  (And (s.kernel_boundary = true)
       (s.non_sovereign_renormalisation = true))

def renormalisation_canonique : RenormalisationState :=
  { scale_local := true,
    scale_global := true,
    coarse_grain := true,
    flow_R := true,
    fixed_point_candidate := true,
    invariant_preservation := true,
    noise_absorption := true,
    stability_under_scale := true,
    theory_family_ready := true,
    renormalisation_ready := true,
    proof_trace_ready := true,
    kernel_boundary := true,
    non_sovereign_renormalisation := true }

theorem renormalisation_canonique_admissible :
    renormalisation_admissible renormalisation_canonique :=
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
            (And.intro rfl rfl)))))
    (And.intro rfl rfl)

theorem renormalisation_has_scale_bridge
    (s : RenormalisationState)
    (h : renormalisation_admissible s) :
    scale_bridge_ready s :=
  h.left.left

theorem renormalisation_has_fixed_point
    (s : RenormalisationState)
    (h : renormalisation_admissible s) :
    fixed_point_scale_ready s :=
  h.left.right.left

theorem renormalisation_has_kernel_boundary
    (s : RenormalisationState)
    (h : renormalisation_admissible s) :
    s.kernel_boundary = true :=
  h.right.left

theorem renormalisation_is_non_sovereign
    (s : RenormalisationState)
    (h : renormalisation_admissible s) :
    s.non_sovereign_renormalisation = true :=
  h.right.right

theorem scale_bridge_has_flow_R
    (s : RenormalisationState)
    (h : scale_bridge_ready s) :
    s.flow_R = true :=
  h.right.right.right

theorem fixed_point_preserves_invariants
    (s : RenormalisationState)
    (h : fixed_point_scale_ready s) :
    s.invariant_preservation = true :=
  h.right.left

end RenormalisationTheories
end Obsidia
