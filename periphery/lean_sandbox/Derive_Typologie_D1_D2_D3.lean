-- Derive_Typologie_D1_D2_D3 -- D1 recuperable, D2 frontiere, D3 critique
-- Status : PROVISIONAL scaffold -- Palier 5 item 103/134
-- SOURCE_COVERAGE: derive_D1 | derive_D2 | derive_D3 | recuperable | frontiere_domaine
--                  critique | urgence_maximale | classification_derive | sigma_cible
--                  marge_securite | suspension_action | kernel_boundary
-- PROVISIONAL_BOUNDARY: typologie de derive approchee par flags Bool et Nat discret.
--   D1 : derive douce, recuperable, encore dans le domaine admissible.
--   D2 : derive de frontiere, marge_securite faible ou nulle, surveillance/HOLD possible.
--   D3 : derive critique, urgence_maximale, suspension_action avant toute execution.
--   La classification guide le kernel mais ne remplace pas son autorite.

namespace Obsidia
namespace DeriveTypologieD1D2D3

structure DeriveState where
  derive_D1 : Bool
  derive_D2 : Bool
  derive_D3 : Bool
  recuperable : Bool
  frontiere_domaine : Bool
  critique : Bool
  urgence_maximale : Bool
  classification_derive : Bool
  sigma_cible : Nat
  marge_securite : Nat
  suspension_action : Bool
  kernel_boundary : Bool

def derive_classified (d : DeriveState) : Prop :=
  And (d.classification_derive = true)
      (d.kernel_boundary = true)

def d1_recuperable (d : DeriveState) : Prop :=
  And (d.derive_D1 = true)
  (And (d.recuperable = true)
  (And (d.frontiere_domaine = false)
       (d.suspension_action = false)))

def d2_frontiere (d : DeriveState) : Prop :=
  And (d.derive_D2 = true)
  (And (d.frontiere_domaine = true)
       (d.classification_derive = true))

def d3_critique (d : DeriveState) : Prop :=
  And (d.derive_D3 = true)
  (And (d.critique = true)
  (And (d.urgence_maximale = true)
       (d.suspension_action = true)))

def derive_admissible (d : DeriveState) : Prop :=
  And (derive_classified d)
      (Or (d1_recuperable d)
          (Or (d2_frontiere d) (d3_critique d)))

def derive_D1_canonique : DeriveState :=
  { derive_D1 := true,
    derive_D2 := false,
    derive_D3 := false,
    recuperable := true,
    frontiere_domaine := false,
    critique := false,
    urgence_maximale := false,
    classification_derive := true,
    sigma_cible := 80,
    marge_securite := 10,
    suspension_action := false,
    kernel_boundary := true }

def derive_D2_canonique : DeriveState :=
  { derive_D1 := false,
    derive_D2 := true,
    derive_D3 := false,
    recuperable := false,
    frontiere_domaine := true,
    critique := false,
    urgence_maximale := false,
    classification_derive := true,
    sigma_cible := 80,
    marge_securite := 0,
    suspension_action := false,
    kernel_boundary := true }

def derive_D3_canonique : DeriveState :=
  { derive_D1 := false,
    derive_D2 := false,
    derive_D3 := true,
    recuperable := false,
    frontiere_domaine := true,
    critique := true,
    urgence_maximale := true,
    classification_derive := true,
    sigma_cible := 80,
    marge_securite := 0,
    suspension_action := true,
    kernel_boundary := true }

theorem derive_D1_canonique_admissible :
    derive_admissible derive_D1_canonique :=
  And.intro
    (And.intro rfl rfl)
    (Or.inl (And.intro rfl (And.intro rfl (And.intro rfl rfl))))

theorem derive_D2_canonique_admissible :
    derive_admissible derive_D2_canonique :=
  And.intro
    (And.intro rfl rfl)
    (Or.inr (Or.inl (And.intro rfl (And.intro rfl rfl))))

theorem derive_D3_canonique_admissible :
    derive_admissible derive_D3_canonique :=
  And.intro
    (And.intro rfl rfl)
    (Or.inr (Or.inr (And.intro rfl (And.intro rfl (And.intro rfl rfl)))))

theorem d1_recuperable_has_no_suspension
    (d : DeriveState)
    (h : d1_recuperable d) :
    d.suspension_action = false :=
  h.right.right.right

theorem d3_critique_has_suspension
    (d : DeriveState)
    (h : d3_critique d) :
    d.suspension_action = true :=
  h.right.right.right

theorem derive_admissible_has_kernel_boundary
    (d : DeriveState)
    (h : derive_admissible d) :
    d.kernel_boundary = true :=
  h.left.right

theorem derive_admissible_has_classification
    (d : DeriveState)
    (h : derive_admissible d) :
    d.classification_derive = true :=
  h.left.left

end DeriveTypologieD1D2D3
end Obsidia
