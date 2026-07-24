-- Espace_Etat_Obsidia -- Definition canonique de l espace d etat x(t) d Obsidia V4/V5
-- Status : PROVISIONAL scaffold -- Palier 5 item 95/134
-- SOURCE_COVERAGE: espace_etat | vecteur_etat | sigma_t | phi_t | memoire_M | vitesse_memoire
--                  ressources_Rc | energie_E | lambda_t | chi_t | urgence_U | V4_V5
--                  domaine_admissible | etat_critique | etat_stable | kernel_boundary
-- PROVISIONAL_BOUNDARY: modele discret et provisoire de x(t).
--   x(t) = (Sigma(t), Phi(t), M(t), dM(t), Rc(t), E(t), lambda(t), chi(t), U(t)).
--   Le kernel ne comprend pas le monde : les domaines projettent le reel dans cet alphabet d etat.
--   Ici les bornes continues sont representees par des flags Bool verificatifs.

namespace Obsidia
namespace EspaceEtatObsidia

structure EtatObsidia where
  sigma   : Nat
  phi     : Nat
  mem     : Nat
  dmem    : Nat
  rc      : Nat
  energie : Nat
  lambda  : Nat
  chi     : Nat
  urgence : Nat
  vector_complete  : Bool
  sigma_bounded    : Bool
  rc_positive      : Bool
  urgence_bounded  : Bool
  kernel_boundary  : Bool

def etat_valide (x : EtatObsidia) : Prop :=
  And (x.vector_complete = true)
  (And (x.sigma_bounded = true)
  (And (x.rc_positive = true)
  (And (x.urgence_bounded = true)
       (x.kernel_boundary = true))))

def etat_critique (x : EtatObsidia) : Prop :=
  And (x.vector_complete = true)
  (Or (x.sigma_bounded = false)
  (Or (x.rc_positive = false)
      (x.urgence_bounded = false)))

def etat_stable (x : EtatObsidia) : Prop :=
  And (etat_valide x)
      (x.urgence <= 50)

def etat_canonique : EtatObsidia :=
  { sigma := 80, phi := 0, mem := 10, dmem := 1,
    rc := 5, energie := 100, lambda := 0, chi := 0, urgence := 20,
    vector_complete := true, sigma_bounded := true,
    rc_positive := true, urgence_bounded := true, kernel_boundary := true }

theorem etat_canonique_valide : etat_valide etat_canonique :=
  And.intro rfl (And.intro rfl (And.intro rfl (And.intro rfl rfl)))

theorem etat_valide_has_kernel_boundary
    (x : EtatObsidia)
    (h : etat_valide x) :
    x.kernel_boundary = true :=
  h.right.right.right.right

theorem etat_stable_implies_valide
    (x : EtatObsidia)
    (h : etat_stable x) :
    etat_valide x :=
  h.left

end EspaceEtatObsidia
end Obsidia
