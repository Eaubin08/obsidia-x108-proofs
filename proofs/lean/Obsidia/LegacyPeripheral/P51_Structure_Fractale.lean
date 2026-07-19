namespace Obsidia
namespace LegacyPeripheral
namespace P51StructureFractale

structure FractalState where
  scale : Nat
  depth : Nat
  invariant : Nat

def self_similarity (s : FractalState) : Prop :=
  s.invariant = s.invariant

def depth_expands (a b : FractalState) : Prop :=
  a.depth ≤ b.depth

theorem self_similarity_intro (s : FractalState) :
    self_similarity s :=
  rfl

theorem depth_expands_intro
    (a b : FractalState)
    (h : a.depth ≤ b.depth) :
    depth_expands a b :=
  h

theorem scale_nonneg (s : FractalState) :
    s.scale ≥ 0 :=
  Nat.zero_le s.scale

theorem depth_nonneg (s : FractalState) :
    s.depth ≥ 0 :=
  Nat.zero_le s.depth

end P51StructureFractale
end LegacyPeripheral
end Obsidia