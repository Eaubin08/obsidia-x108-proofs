-- Pipeline_Reversion -- Genealogie de la Verite Fractale (Psi->Lambda->Phi->Delta->Sigma)
-- Status : PROVISIONAL scaffold -- Palier 3
-- SOURCE_COVERAGE: pipeline_reversion | genealogie_verite | reversion_fractale
--                  psi_illusion | lambda_narratif | phi_donnees | delta_brut | sigma_verite
--                  detection_illusion | deconstruction | decompress | reconstruction | loi_ROM
-- PROVISIONAL_BOUNDARY: reversion complete multi-etapes non prouvee formellement.
--   Application formelle de la Loi ROM : tout chemin biaise peut etre parcouru en sens inverse.
--   5 etats : Psi(illusion) -> Lambda(narratif) -> Phi(donnees) -> Delta(brut) -> Sigma(verite).
--   Pipeline_Reversion = protocole detaille ; ROM = le principe directeur.

namespace Obsidia
namespace PipelineReversion

inductive VeriteState
  | psi
  | lambda
  | phi
  | delta
  | sigma

def reversion_level : VeriteState -> Nat
  | VeriteState.psi    => 0
  | VeriteState.lambda => 1
  | VeriteState.phi    => 2
  | VeriteState.delta  => 3
  | VeriteState.sigma  => 4

def more_reliable (a b : VeriteState) : Prop :=
  reversion_level a > reversion_level b

def fully_reverted (s : VeriteState) : Prop :=
  s = VeriteState.sigma

def reversion_step (s : VeriteState) : VeriteState :=
  match s with
  | VeriteState.psi    => VeriteState.lambda
  | VeriteState.lambda => VeriteState.phi
  | VeriteState.phi    => VeriteState.delta
  | VeriteState.delta  => VeriteState.sigma
  | VeriteState.sigma  => VeriteState.sigma

theorem sigma_fully_reverted : fully_reverted VeriteState.sigma := rfl

theorem reversion_improves (s : VeriteState) (h : Not (s = VeriteState.sigma)) :
    reversion_level (reversion_step s) > reversion_level s := by
  cases s <;> simp_all [reversion_step, reversion_level]

theorem psi_to_lambda : reversion_step VeriteState.psi = VeriteState.lambda := rfl

end PipelineReversion
end Obsidia
