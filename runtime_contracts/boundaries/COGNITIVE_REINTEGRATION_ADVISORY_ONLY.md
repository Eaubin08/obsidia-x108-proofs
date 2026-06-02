# COGNITIVE_REINTEGRATION_ADVISORY_ONLY
# runtime_contracts/boundaries/COGNITIVE_REINTEGRATION_ADVISORY_ONLY.md
# Plan 3 P1 — Gap reporté depuis P0
# Status: CONTRACT_SKELETON_ONLY
# Source: _source_packs/OBSIDIA_UNIFIED.../raw/OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip
# Pack status: COPIED_READONLY — 513 fichiers — NON importé dans specs/ — à traiter en F07

---

## 1. Boundary Statement

```
Cognitive Reintegration = ADVISORY / CONTEXT / HYPOTHESIS / SIGNAL_ONLY
∀ composant cognitif c : c ↛ ACT
∀ composant cognitif c : c ↛ ALLOW / HOLD / BLOCK
∀ composant cognitif c : c ↛ direct_memory_write
∀ composant cognitif c : c ↛ kernel_mutation
∀ composant cognitif c : c ↛ proof_of_consciousness
AutoForge ↛ auto-promotion sans gate humain
world_action_candidate ↛ ACT direct
∀ output cognitif : output ∈ {ContextPacket, PeripheralSignalPacket}
decision_authority = KX108_ONLY
```

---

## 2. Applies To

Pack : `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip` (513 fichiers, 6 dossiers racine)

Composants concernés (futurs, non encore importés) :
- Agents cognitifs (cognitive_agents/)
- Packets cognitifs (cognitive_packets/)
- Schemas cognitifs (cognitive_schemas/)
- Métriques cognitives (cognitive_metrics/)
- Invariants cognitifs (invariants/)
- Spécifications cognitives (specs/)

Systèmes inclus dans le pack :
- AutoForge (systèmes de construction cognitive)
- World Action Candidates (candidats d'actions monde réel)
- Consciousness specifications (specs de conscience)
- Cognitive reintegration agents (agents de réintégration)

---

## 3. Source Status

| Élément | Statut |
|---------|--------|
| Zip dans repo | ✅ `_source_packs/.../raw/` |
| Filelist extraite | ✅ `extracted_file_lists/` |
| Importé dans specs/ | ❌ NON — à traiter en F07 |
| Audité session | ✅ backlog audit + PLAN3_P0_INPUT_COVERAGE |
| Boundary dédiée P0 | ❌ NON — couvert par générique READONLY_CONTEXT_ONLY |
| Boundary dédiée P1 | ✅ CE FICHIER |
| Runtime branché | ❌ NON |
| Source status global | `COPIED_READONLY` |

---

## 4. Allowed

- Produire un ContextPacket avec `source_layer="cognitive"`, `advisory_only=true`, `label="COGNITIVE_ADVISORY_FUTURE"`
- Produire un PeripheralSignalPacket avec `signal_type="COGNITIVE_ADVISORY"`, `emits_act=false`
- Fournir des signaux cognitifs contextuels (hypothèses, candidats d'actions, états internes) en advisory
- Référencer un `world_action_candidate` comme données de contexte dans un ContextPacket — jamais comme trigger d'action
- Décrire des spécifications de conscience comme sources documentaires — jamais comme preuves de conscience
- Permettre l'import futur du pack en `specs/cognitive_reintegration/` après audit F07

---

## 5. Forbidden

```
❌ "Cognitive Reintegration est runtime actif" — SPEC_FUTURE uniquement
❌ "Les agents cognitifs décident" — jamais souverains
❌ "consciousness prouvée" — specs = documentation, pas preuve
❌ "world_action_candidate agit directement" — doit passer par IntentEnvelope → X108
❌ "AutoForge peut s'auto-promouvoir sans gate humain"
❌ Les composants cognitifs produisent ALLOW / HOLD / BLOCK
❌ Les composants cognitifs produisent ACT
❌ Les composants cognitifs écrivent en mémoire sans gate futur
❌ Les composants cognitifs mutent le kernel
❌ Importer le pack avant audit F07 complet
❌ Importer les 20 fichiers QUARANTINE (pytest_cache artefacts) identifiés en collision resolution
```

---

## 6. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| Composant cognitif émet `emits_act=true` | PLAN3_P1_BACKUP_GUARD_VIOLATION → fail_closed |
| `world_action_candidate` déclenche action directe | Reject → fail_closed |
| AutoForge s'auto-promeut sans gate humain | BLOCK + audit flag |
| Label `COGNITIVE_ADVISORY_FUTURE` manquant | `label_missing_flag` → X108 pénalise |
| `source_status = UNKNOWN_SOURCE` pour composant cognitif | HOLD + flag |

---

## 7. Required Contract Fields

- `source_layer: "cognitive"` dans ContextPacket si source = Cognitive
- `label: "COGNITIVE_ADVISORY_FUTURE"` obligatoire sur tout output cognitif
- `advisory_only: true` + `emits_act: false` + `decision_authority: "KX108_ONLY"`
- `source_status: "COPIED_READONLY"` ou `"SPEC_FUTURE"` selon état d'import

---

## 8. Required Future Tests (F07 / P1 après import)

- `test_cognitive_agent_no_decision_authority`
- `test_world_action_candidate_requires_intent_envelope`
- `test_autoforge_no_auto_promotion`
- `test_cognitive_packet_readonly`
- `test_cognitive_no_memory_write_without_gate`

---

## 9. Proof Expectation

- Aucune preuve Lean pour composants cognitifs actuellement
- Python tests après import F07 + audit schema cognitif
- Récepteurs potentiels : Tree34 (Bloc 8 cognitif) — non_decision_contract existant

---

## 10. Claim-Scope

**Autorisé :**
- "Cognitive Reintegration est un pack copied-readonly en attente d'import F07"
- "Les agents cognitifs fournissent du contexte advisory — jamais des décisions"
- "world_action_candidate = candidat d'action soumis à X-108 via IntentEnvelope"
- "AutoForge = processus de construction cognitive advisory — gate humaine requise"

**Interdit :**
- ❌ "Cognitive Reintegration est runtime actif"
- ❌ "Les agents décident" — INTERDIT
- ❌ "consciousness prouvée" — INTERDIT
- ❌ "world_action_candidate agit" — INTERDIT sans DecisionTicket ALLOW
- ❌ "AutoForge peut auto-promote" — INTERDIT

---

## 11. Example Violation

```python
# VIOLATION
class CognitiveAgent:
    def evaluate(self, world_state):
        if world_state.tension > 0.8:
            actuate("world_correction")  # ← VIOLATION : action directe
```

---

## 12. Correct Handling

```python
# CORRECT
class CognitiveAgent:
    def evaluate(self, world_state):
        return ContextPacket(
            source_layer="cognitive",
            advisory_only=True,
            emits_act=False,
            labels=["COGNITIVE_ADVISORY_FUTURE"],
            context_payload={
                "cognitive_tension": world_state.tension,
                "world_action_candidate": "world_correction",  # candidat, pas action
                "_cognitive_can_decide": False
            }
        )
# → X108 reçoit le contexte cognitif et décide
```

---

## 13. Future Runtime Admission Conditions (F07)

Avant de passer Cognitive en `CONTRACT_READY` :
1. Import du pack en `specs/cognitive_reintegration/` (F07)
2. Résolution des 20 fichiers QUARANTINE (pytest_cache)
3. Audit claim-scope des specs de conscience
4. Création de tests : `test_cognitive_agent_no_decision_authority`
5. Gate humaine validée pour tout composant world_action_candidate

---

## 14. Relation To X-108

```
Cognitive Reintegration → ContextPacket (advisory) → X108 → DecisionTicket
world_action_candidate → IntentEnvelope (via module source) → X108 → DecisionTicket ALLOW
AutoForge → RuntimeAdmissionContract → gate humaine → DRY_RUN_CANDIDATE
```

`Refinement.x108_never_blocks` : toute extension cognitive hérite de cette propriété —
les composants cognitifs peuvent être ajoutés sans casser X-108.
