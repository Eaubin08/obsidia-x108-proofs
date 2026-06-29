-- Neopsidia -- Neopsidia -- vision philosophique etendue d'Obsidia
-- Status : PROVISIONAL scaffold
-- Obsidia X-108 periphery sandbox

namespace Obsidia
namespace Neopsidia

-- Neopsidia extends the Obsidia kernel with a philosophical layer
-- Modelled as a tagged state with an extension flag
structure NeopsidiaState where
  base_active  : Bool
  extended     : Bool
  layer        : Nat   -- 0 = kernel, 1 = neopsidia extension

-- A state is in Neopsidia mode when extended and layer > 0
def neopsidiaMode (s : NeopsidiaState) : Prop :=
  And (s.extended = true) (s.layer > 0)

-- Canonical Neopsidia state
def canonical : NeopsidiaState :=
  { base_active := true, extended := true, layer := 1 }

theorem canonical_neopsidia : neopsidiaMode canonical :=
  And.intro rfl (Nat.succ_pos 0)

-- Base mode: not extended
def baseMode : NeopsidiaState :=
  { base_active := true, extended := false, layer := 0 }

theorem base_not_neopsidia : baseMode.extended = false := rfl

end Neopsidia
end Obsidia
