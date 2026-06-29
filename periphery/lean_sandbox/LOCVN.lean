-- LOCVN -- Loi Obsidienne de Causalite Vibratoire Non-Locale
-- Status : PROVISIONAL scaffold
-- Obsidia X-108 periphery sandbox

namespace Obsidia
namespace LOCVN

structure NonLocalState where
  source    : Nat
  target    : Nat
  linked    : Bool
  influence : Bool

def causallyActive (s : NonLocalState) : Prop :=
  And (s.linked = true) (s.influence = true)

def canonical : NonLocalState :=
  { source := 0, target := 1, linked := true, influence := true }

theorem canonical_link : canonical.linked = true := rfl

theorem canonical_influence : canonical.influence = true := rfl

theorem canonical_active : causallyActive canonical :=
  And.intro rfl rfl

end LOCVN
end Obsidia
