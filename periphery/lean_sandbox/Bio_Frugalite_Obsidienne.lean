namespace Obsidia
namespace BioFrugaliteObsidienne

-- Bio-Frugalité Obsidienne
-- Type: model — peripherique, non-decisionnel, runtime_bound=false

inductive BioFrugaliteObsidienneStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : BioFrugaliteObsidienneStep) : Prop :=
  s = BioFrugaliteObsidienneStep.active ∨ s = BioFrugaliteObsidienneStep.complete

theorem init_not_valid : ¬ step_valid BioFrugaliteObsidienneStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid BioFrugaliteObsidienneStep.active := Or.inl rfl

theorem complete_valid : step_valid BioFrugaliteObsidienneStep.complete := Or.inr rfl

end BioFrugaliteObsidienne
end Obsidia
