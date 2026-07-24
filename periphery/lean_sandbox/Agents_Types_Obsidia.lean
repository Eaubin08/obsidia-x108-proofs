-- Agents_Types_Obsidia -- Taxonomie Masters / Ephemeres / Spectres
-- Status : PROVISIONAL scaffold -- Palier 2
-- SOURCE_COVERAGE: Masters | Ephemeres | Spectres | modes_conscience
--                  persistant | temporaire | trace_memorielle
--                  creation_selon_tache | dissolution_apres_tache
--                  apprentissage NoProp | compression Ephemere→Spectre
-- PROVISIONAL_BOUNDARY: critere formel de creation/dissolution non prouve.
--   Masters = permanents (perception/memoire/raisonnement/action).
--   Ephemeres = temporaires, crees par tache, dissolus apres.
--   Spectres = traces memorielles (≠ Ephemeres actifs).
--   Spheres = variante nomenclature anterieure (obsolete).

namespace Obsidia
namespace AgentsTypes

inductive AgentCategory
  | master
  | ephemere
  | spectre

structure AgentInstance where
  category    : AgentCategory
  persistent  : Bool
  task_bound  : Bool
  mem_trace   : Bool

-- Masters : persistants, non lies a une tache, pas de trace seule
def is_master (a : AgentInstance) : Prop :=
  And (a.category = AgentCategory.master)
  (And (a.persistent = true)
       (a.task_bound = false))

-- Ephemeres : non persistants, lies a une tache
def is_ephemere (a : AgentInstance) : Prop :=
  And (a.category = AgentCategory.ephemere)
  (And (a.persistent = false)
       (a.task_bound = true))

-- Spectres : trace memorielle uniquement
def is_spectre (a : AgentInstance) : Prop :=
  And (a.category = AgentCategory.spectre)
  (And (a.persistent = false)
       (a.mem_trace = true))

def canonical_master : AgentInstance :=
  { category := AgentCategory.master, persistent := true,
    task_bound := false, mem_trace := false }

def canonical_ephemere : AgentInstance :=
  { category := AgentCategory.ephemere, persistent := false,
    task_bound := true, mem_trace := false }

def canonical_spectre : AgentInstance :=
  { category := AgentCategory.spectre, persistent := false,
    task_bound := false, mem_trace := true }

theorem canonical_master_ok : is_master canonical_master :=
  And.intro rfl (And.intro rfl rfl)

theorem canonical_ephemere_ok : is_ephemere canonical_ephemere :=
  And.intro rfl (And.intro rfl rfl)

theorem canonical_spectre_ok : is_spectre canonical_spectre :=
  And.intro rfl (And.intro rfl rfl)

end AgentsTypes
end Obsidia
