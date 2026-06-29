-- Sigma_t -- Sigma(t) -- Coherence interne du moteur
-- Status : PROVISIONAL scaffold
-- Obsidia X-108 periphery sandbox

namespace Obsidia
namespace SigmaT

-- Coherence state at time t
structure CoherenceState where
  t      : Nat
  value  : Nat   -- coherence in [0, max_val]
  max_val: Nat
  stable : Bool

-- Coherence is bounded
def bounded (s : CoherenceState) : Prop :=
  s.value <= s.max_val

-- Full coherence: value = max_val and stable
def fullCoherence (s : CoherenceState) : Prop :=
  And (s.value = s.max_val) (s.stable = true)

-- Canonical: value = max_val = 1, stable
def canonical : CoherenceState :=
  { t := 0, value := 1, max_val := 1, stable := true }

theorem canonical_bounded : bounded canonical := Nat.le_refl 1

theorem canonical_full_coherence : fullCoherence canonical :=
  And.intro rfl rfl

-- Coherence degrades: value decreases
theorem degraded_bounded (s : CoherenceState) (h : s.value <= s.max_val)
    (hd : s.value > 0) : s.value - 1 < s.max_val :=
  Nat.lt_of_lt_of_le (Nat.sub_lt hd Nat.one_pos) h

end SigmaT
end Obsidia
