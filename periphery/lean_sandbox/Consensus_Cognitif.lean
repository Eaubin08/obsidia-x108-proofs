namespace Obsidia
namespace ConsensusCognitif

structure Vote where
  signal : Bool
  confidence : Nat

def agrees (v : Vote) : Prop :=
  v.signal = true

def reliable (v : Vote) : Prop :=
  50 <= v.confidence

def supports_consensus (v : Vote) : Prop :=
  agrees v ∧ reliable v

theorem supports_consensus_intro
    (v : Vote)
    (ha : agrees v)
    (hr : reliable v) :
    supports_consensus v :=
  And.intro ha hr

theorem agrees_from_supports
    (v : Vote)
    (h : supports_consensus v) :
    agrees v :=
  h.left

theorem reliable_from_supports
    (v : Vote)
    (h : supports_consensus v) :
    reliable v :=
  h.right

end ConsensusCognitif
end Obsidia