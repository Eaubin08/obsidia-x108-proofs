namespace Obsidia
namespace P55EspaceGeometrique

structure Point where
  x : Nat
  y : Nat

def coincident (p1 p2 : Point) : Prop :=
  p1.x = p2.x ∧ p1.y = p2.y

theorem coincident_reflexif (p : Point) : coincident p p := ⟨rfl, rfl⟩

theorem coincident_symetrique (p1 p2 : Point) (h : coincident p1 p2) :
    coincident p2 p1 := ⟨h.1.symm, h.2.symm⟩

theorem coincident_transitif (p1 p2 p3 : Point)
    (h1 : coincident p1 p2) (h2 : coincident p2 p3) :
    coincident p1 p3 := ⟨h1.1.trans h2.1, h1.2.trans h2.2⟩

def espace_valide (p : Point) : Prop := coincident p p

theorem espace_toujours_valide (p : Point) : espace_valide p := coincident_reflexif p

end P55EspaceGeometrique
end Obsidia
