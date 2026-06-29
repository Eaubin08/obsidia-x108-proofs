-- Faisceau_futurs -- Faisceau de futurs -- espace de trajectoires possibles
-- Status : PROVISIONAL scaffold
-- Obsidia X-108 periphery sandbox

namespace Obsidia
namespace FaisceauFuturs

-- A trajectory is a sequence of states indexed by Nat
structure Trajectory where
  length : Nat
  active : Bool

-- A beam of futures: a finite collection of possible trajectories
structure FutureBeam where
  count    : Nat
  selected : Nat

-- The selected trajectory must be within range
def validSelection (b : FutureBeam) : Prop :=
  b.selected < b.count

-- Canonical: single trajectory, selected = 0
def canonical : FutureBeam :=
  { count := 1, selected := 0 }

theorem canonical_valid : validSelection canonical := Nat.lt.base 0

-- Adding a trajectory increases count
theorem beam_grows (b : FutureBeam) : (b.count + 1) > b.count :=
  Nat.lt.base b.count

end FaisceauFuturs
end Obsidia
