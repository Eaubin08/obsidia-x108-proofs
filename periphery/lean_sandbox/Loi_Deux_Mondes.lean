-- Loi_Deux_Mondes -- Loi des Deux Mondes (双世律)
-- Status : PROVISIONAL scaffold -- Palier 2
-- SOURCE_COVERAGE: monde_reel R | monde_modele M | relation R<->M
--                  projection pi_R | projection pi_M | coherence epsilon
--                  re_synchronisation | pipeline_perception | LUO lien
-- PROVISIONAL_BOUNDARY: metrique de coherence epsilon non prouvee.
--   Tout concept obsidien existe simultanement dans R et M.
--   Le passage R→M est la modelisation ; M→R est la verification.
--   ROM surveille les divergences R↔M (lien doctrinal).

namespace Obsidia
namespace LoiDeuxMondes

-- Représentation d'un concept dans les deux mondes
structure BiWorldConcept where
  name_real  : Bool  -- ancrage monde réel
  name_model : Bool  -- ancrage monde modèle
  coherent   : Bool  -- |pi_R - pi_M| < epsilon (proxy Bool)

-- Projection monde réel active
def has_real_projection (c : BiWorldConcept) : Prop :=
  c.name_real = true

-- Projection monde modèle active
def has_model_projection (c : BiWorldConcept) : Prop :=
  c.name_model = true

-- Coherence R↔M maintenue
def is_coherent (c : BiWorldConcept) : Prop :=
  c.coherent = true

-- Loi des Deux Mondes : les deux projections doivent exister
def deux_mondes_valid (c : BiWorldConcept) : Prop :=
  And (has_real_projection c)
  (And (has_model_projection c)
       (is_coherent c))

def canonical : BiWorldConcept :=
  { name_real := true, name_model := true, coherent := true }

theorem canonical_deux_mondes : deux_mondes_valid canonical :=
  And.intro rfl (And.intro rfl rfl)

-- Marqueur : re-synchronisation requise si coherent = false (proxy)
def needs_resync (c : BiWorldConcept) : Prop :=
  c.coherent = false

theorem canonical_no_resync : ¬ needs_resync canonical := by
  simp [canonical, needs_resync]

end LoiDeuxMondes
end Obsidia
