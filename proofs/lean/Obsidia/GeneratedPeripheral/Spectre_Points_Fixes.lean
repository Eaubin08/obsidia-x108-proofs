-- Spectre_Points_Fixes -- spectre des points fixes et signatures de stabilite
-- Status : PROVISIONAL scaffold -- Palier 7 item 123/134
-- SOURCE_COVERAGE: spectre_points_fixes | fixed_point_spectrum | fixed_point_candidate
--                  stable_fixed_point | unstable_fixed_point | neutral_fixed_point
--                  basin_link | eigen_signature | convergence_radius
--                  multiplicity_control | spectral_partition | spectrum_ready
--                  proof_trace_ready | kernel_boundary | non_sovereign_spectrum
-- PROVISIONAL_BOUNDARY: le spectre des points fixes est encode par flags Bool.
--   Il separe points fixes stables, instables et neutres.
--   La signature spectrale relie rayon de convergence, multiplicite et partition.
--   Le spectre classe les attracteurs possibles, mais ne decide aucune action.

namespace Obsidia
namespace SpectrePointsFixes

structure SpectrePointsFixesState where
  fixed_point_spectrum : Bool
  fixed_point_candidate : Bool
  stable_fixed_point : Bool
  unstable_fixed_point : Bool
  neutral_fixed_point : Bool
  basin_link : Bool
  eigen_signature : Bool
  convergence_radius : Bool
  multiplicity_control : Bool
  spectral_partition : Bool
  spectrum_ready : Bool
  proof_trace_ready : Bool
  kernel_boundary : Bool
  non_sovereign_spectrum : Bool

def fixed_points_ready (s : SpectrePointsFixesState) : Prop :=
  And (s.fixed_point_spectrum = true)
  (And (s.fixed_point_candidate = true)
  (And (s.stable_fixed_point = true)
  (And (s.unstable_fixed_point = true)
       (s.neutral_fixed_point = true))))

def spectral_analysis_ready (s : SpectrePointsFixesState) : Prop :=
  And (s.eigen_signature = true)
  (And (s.convergence_radius = true)
  (And (s.multiplicity_control = true)
       (s.spectral_partition = true)))

def fixed_point_context_ready (s : SpectrePointsFixesState) : Prop :=
  And (s.basin_link = true)
  (And (s.spectrum_ready = true)
       (s.proof_trace_ready = true))

def spectre_points_fixes_ready (s : SpectrePointsFixesState) : Prop :=
  And (fixed_points_ready s)
  (And (spectral_analysis_ready s)
       (fixed_point_context_ready s))

def spectre_points_fixes_admissible (s : SpectrePointsFixesState) : Prop :=
  And (spectre_points_fixes_ready s)
  (And (s.kernel_boundary = true)
       (s.non_sovereign_spectrum = true))

def spectre_points_fixes_canonique : SpectrePointsFixesState :=
  { fixed_point_spectrum := true,
    fixed_point_candidate := true,
    stable_fixed_point := true,
    unstable_fixed_point := true,
    neutral_fixed_point := true,
    basin_link := true,
    eigen_signature := true,
    convergence_radius := true,
    multiplicity_control := true,
    spectral_partition := true,
    spectrum_ready := true,
    proof_trace_ready := true,
    kernel_boundary := true,
    non_sovereign_spectrum := true }

theorem spectre_points_fixes_canonique_admissible :
    spectre_points_fixes_admissible spectre_points_fixes_canonique :=
  And.intro
    (And.intro
      (And.intro rfl
        (And.intro rfl
          (And.intro rfl
            (And.intro rfl rfl))))
      (And.intro
        (And.intro rfl
          (And.intro rfl
            (And.intro rfl rfl)))
        (And.intro rfl
          (And.intro rfl rfl))))
    (And.intro rfl rfl)

theorem spectre_has_fixed_points
    (s : SpectrePointsFixesState)
    (h : spectre_points_fixes_admissible s) :
    fixed_points_ready s :=
  h.left.left

theorem spectre_has_spectral_analysis
    (s : SpectrePointsFixesState)
    (h : spectre_points_fixes_admissible s) :
    spectral_analysis_ready s :=
  h.left.right.left

theorem spectre_has_context
    (s : SpectrePointsFixesState)
    (h : spectre_points_fixes_admissible s) :
    fixed_point_context_ready s :=
  h.left.right.right

theorem spectre_has_kernel_boundary
    (s : SpectrePointsFixesState)
    (h : spectre_points_fixes_admissible s) :
    s.kernel_boundary = true :=
  h.right.left

theorem spectre_is_non_sovereign
    (s : SpectrePointsFixesState)
    (h : spectre_points_fixes_admissible s) :
    s.non_sovereign_spectrum = true :=
  h.right.right

theorem fixed_points_have_stable_component
    (s : SpectrePointsFixesState)
    (h : fixed_points_ready s) :
    s.stable_fixed_point = true :=
  h.right.right.left

theorem spectral_analysis_has_partition
    (s : SpectrePointsFixesState)
    (h : spectral_analysis_ready s) :
    s.spectral_partition = true :=
  h.right.right.right

end SpectrePointsFixes
end Obsidia
