-- Memoire_404 -- Oubli Structurel (记忆404)
-- Status : PROVISIONAL scaffold -- Palier 2
-- SOURCE_COVERAGE: signal_decay | structural_forget | etat_vide
--                  HTTP_404_analogy | carre_brise | Signal→0
--                  distinct_oubli_volontaire | pheromonal_decay
-- PROVISIONAL_BOUNDARY: seuil numerique de Signal=0 non prouve.
--   Memoire_404 = etat limite passif : chemin non renforce → signal → 0.
--   Distinct du type 7 (Oubli Volontaire) qui est actif/intentionnel.
--   Le signal pheromonal alimente la detection Memoire_404.

namespace Obsidia
namespace Memoire404

-- Etat d'un pattern en memoire
structure MemPattern where
  signal_strength  : Nat   -- proxy force du signal (0 = oubli)
  reinforced       : Bool  -- renforce recemment ?
  voluntary_forget : Bool  -- oubli volontaire (type 7, distinct)

-- Memoire_404 : signal nul, non renforce, non volontaire
def is_404 (p : MemPattern) : Prop :=
  And (p.signal_strength = 0)
  (And (p.reinforced = false)
       (p.voluntary_forget = false))

-- Oubli volontaire (type 7) : distinct du 404
def is_voluntary_forget (p : MemPattern) : Prop :=
  p.voluntary_forget = true

-- Un pattern 404 n'est pas un oubli volontaire
theorem m404_not_voluntary (p : MemPattern) (h404 : is_404 p) :
    ¬ is_voluntary_forget p := by
  simp [is_404, is_voluntary_forget] at *
  exact h404.2.2

def canonical_404 : MemPattern :=
  { signal_strength := 0, reinforced := false, voluntary_forget := false }

def canonical_active : MemPattern :=
  { signal_strength := 5, reinforced := true, voluntary_forget := false }

theorem canonical_is_404 : is_404 canonical_404 :=
  And.intro rfl (And.intro rfl rfl)

theorem canonical_active_not_404 : ¬ is_404 canonical_active := by
  simp [canonical_active, is_404]

end Memoire404
end Obsidia
