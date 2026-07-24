namespace Obsidia
namespace PipelinePerception

-- Pipeline de Perception
-- Type: algorithm — peripherique, non-decisionnel, runtime_bound=false

structure PipelinePerceptionState where
  active    : Bool
  validated : Bool

def pipelineperception_valide (s : PipelinePerceptionState) : Prop :=
  s.active = true ∧ s.validated = true

def pipelineperception_hold (s : PipelinePerceptionState) : Prop := ¬ pipelineperception_valide s

def canonical : PipelinePerceptionState := { active := true, validated := true }

theorem canonical_valide : pipelineperception_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : PipelinePerceptionState) (h : s.active = false) :
    pipelineperception_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : PipelinePerceptionState) (h : s.validated = false) :
    pipelineperception_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end PipelinePerception
end Obsidia
