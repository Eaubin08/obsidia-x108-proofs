-- Marge_Securite_m -- m(x,t) marge avant violation de contrainte
-- Status : PROVISIONAL scaffold -- Palier 5 item 97/134
-- SOURCE_COVERAGE: marge_securite | contraintes_admissibles | CE_energie | CR_ressources
--                  C_sigma | C_lambda | violation_imminente | frontiere_domaine
--                  m_positif | domaine_interieur | admissibilite | kernel_boundary
-- PROVISIONAL_BOUNDARY: m(x,t) est represente par flags Bool et Nat discret.
--   m(x,t) = min_i(-Ci(x)) est ici approxime par un marqueur m_positif.
--   m > 0 signifie interieur du domaine admissible.
--   m = 0 signifie frontiere ; violation_imminente declenche HOLD/BLOCK selon contexte.

namespace Obsidia
namespace MargeSecuriteM

structure MargeState where
  ce_energie_ok : Bool
  cr_ressources_ok : Bool
  c_sigma_ok : Bool
  c_lambda_ok : Bool
  m_value : Nat
  m_positif : Bool
  frontiere_domaine : Bool
  violation_imminente : Bool
  admissibilite : Bool
  kernel_boundary : Bool

def contraintes_admissibles (m : MargeState) : Prop :=
  And (m.ce_energie_ok = true)
  (And (m.cr_ressources_ok = true)
  (And (m.c_sigma_ok = true)
       (m.c_lambda_ok = true)))

def marge_positive (m : MargeState) : Prop :=
  m.m_positif = true

def domaine_interieur (m : MargeState) : Prop :=
  And (marge_positive m)
      (m.frontiere_domaine = false)

def violation_detectee (m : MargeState) : Prop :=
  m.violation_imminente = true

def marge_admissible (m : MargeState) : Prop :=
  And (contraintes_admissibles m)
  (And (marge_positive m)
  (And (m.admissibilite = true)
       (m.kernel_boundary = true)))

def marge_canonique : MargeState :=
  { ce_energie_ok := true,
    cr_ressources_ok := true,
    c_sigma_ok := true,
    c_lambda_ok := true,
    m_value := 10,
    m_positif := true,
    frontiere_domaine := false,
    violation_imminente := false,
    admissibilite := true,
    kernel_boundary := true }

theorem marge_canonique_admissible : marge_admissible marge_canonique :=
  And.intro
    (And.intro rfl (And.intro rfl (And.intro rfl rfl)))
    (And.intro rfl (And.intro rfl rfl))

theorem marge_admissible_has_constraints
    (m : MargeState)
    (h : marge_admissible m) :
    contraintes_admissibles m :=
  h.left

theorem marge_admissible_has_positive_margin
    (m : MargeState)
    (h : marge_admissible m) :
    marge_positive m :=
  h.right.left

theorem domaine_interieur_has_positive_margin
    (m : MargeState)
    (h : domaine_interieur m) :
    marge_positive m :=
  h.left

theorem marge_admissible_has_kernel_boundary
    (m : MargeState)
    (h : marge_admissible m) :
    m.kernel_boundary = true :=
  h.right.right.right

end MargeSecuriteM
end Obsidia
