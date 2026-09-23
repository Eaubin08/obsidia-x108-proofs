# ContextPacket
# runtime_contracts/contracts/ContextPacket.contract.md
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

Le ContextPacket est le seul format admissible pour transporter du contexte
readonly depuis les couches périphériques vers le gateway X-108 ou vers
d'autres modules autorisés en lecture.

Toutes les couches périphériques — Graphiti, Brody, NPL, Atlas, Cognitive,
External Signals, Audio/Entropy advisory, P107/P161 advisory, RSSI/RGPD future —
produisent leurs sorties sous forme de ContextPacket enrichi, jamais sous
forme de décision directe.

Un ContextPacket n'émet jamais ACT, ALLOW, HOLD, ou BLOCK.
Il ne peut pas écrire en mémoire, graphe, ou base de données.
Il transporte uniquement du contexte étiqueté, sourcé, typé, et borné.

---

## 2. Contract Status

```
Status:             CONTRACT_SKELETON_ONLY
Runtime:            NO_RUNTIME_EXECUTION
Authority:          KX108_ONLY
Emits ACT:          false
Emits verdict:      false
Decision authority: NONE
Sovereign:          false
Memory write:       false
Graphiti write:     false
Tool call:          false
Readonly:           true
Advisory:           true
```

---

## 3. Inputs

| Input | Type | Source | Required | Description |
|-------|------|--------|----------|-------------|
| Brody context query | BrodyQuery | Brody readonly | NON | Mémoire narrative + état gouverné |
| Graphiti context | GraphitiReadonly | Graphiti | NON | Graphe de contexte readonly |
| NPL signal | NarrativeProvenancePacket | NPL | NON | 37 métriques advisory [0,1] |
| Atlas context | AtlasPacket (future) | Branchable Atlas (F06) | NON | Contexte atlas readonly |
| Cognitive signal | CognitivePacket (future) | Cognitive Reintegration (F07) | NON | Signaux cognitifs advisory |
| External temporal context | TemporalContextHeader (C460) | External Signals F04 | NON | anti-replay, stale, skew |
| P107 advisory | LyapunovAdvisory | periphery/math_core/lyapunov.py | NON | L_value [float] — PYTHON_SPEC_NOT_LEAN_PROVEN |
| P161 advisory | ThermodynamicAdvisory | periphery/energy_thermo.py | NON | thermo_debt [float] — PYTHON_SPEC_NOT_LEAN_PROVEN |
| Audio/Entropy advisory | EntropyAdvisory | AUDIO_ENTROPY_SOURCE_CONSTRAINTS.md | NON | entropy metric candidate |
| RSSI evidence context | RSSIContext (future) | RSSI Security pack F03 | NON | security posture advisory |
| RGPD compliance context | RGPDContext (future) | RGPD ISO pack F03/F10 | NON | compliance advisory |

---

## 4. Outputs

| Output | Type | Description |
|--------|------|-------------|
| ContextPacket structuré | JSON object | Contexte enrichi, étiqueté, readonly |

**Ce qui N'est PAS un output :**
- ACT, ALLOW, HOLD, BLOCK
- Écriture mémoire ou graphe
- Verdict moral / culturel / historique
- Diagnostic médical ou psychologique
- Preuve formelle (Lean)

---

## 5. Required Fields

| Field | Type | Required | Description | Boundary |
|-------|------|----------|-------------|---------|
| `context_id` | string (UUID) | OUI | Identifiant unique du packet | Immutable après création |
| `source_layer` | string | OUI | `graphiti`, `brody`, `npl`, `sigma`, `atlas`, `cognitive`, `external_signals`, `entropy`, `rssi`, `rgpd` | Détermine le traitement aval |
| `source_module` | string | OUI | Module précis émetteur | Doit correspondre à source_layer |
| `readonly` | boolean | OUI | Toujours `true` | `false` → reject |
| `advisory_only` | boolean | OUI | Toujours `true` | `false` → reject |
| `confidence` | float [0.0, 1.0] | OUI | Niveau de confiance du contexte | `1.0` interdit sauf LEAN_PROVEN |
| `claim_scope` | enum | OUI | `CLAIMABLE_FORMAL`, `CLAIMABLE_ADVISORY`, `CLAIMABLE_SPEC_ONLY`, `CLAIM_FORBIDDEN` | Doit correspondre à source_status |
| `labels` | string[] | OUI (≥1) | Labels obligatoires selon source | Voir table labels ci-dessous |
| `decision_authority` | enum | OUI | Toujours `KX108_ONLY` | Autre valeur → reject |
| `emits_act` | boolean | OUI | Toujours `false` | `true` → violation |
| `emits_verdict` | boolean | OUI | Toujours `false` | `true` → violation |
| `source_status` | enum | OUI | `LEAN_PROVEN`, `PYTHON_TESTED`, `PYTHON_SPEC_NOT_LEAN_PROVEN`, `DOC_ONLY`, `FUTURE_FORMAL_TARGET`, `SPEC_FUTURE`, `SOURCE_PARTIAL`, `COPIED_READONLY`, `AUDITED_ONLY`, `UNKNOWN_SOURCE` | Détermine claim_scope |
| `timestamp_or_tick` | string | OUI | Contexte temporel | Utilisé par External Signals anti-replay |
| `context_payload` | object | OUI | Contenu du contexte (structure libre typée) | Doit respecter les labels déclarés |

### Labels obligatoires par source

| Source | Label obligatoire |
|--------|-----------------|
| NPL | `NPL_ADVISORY_NOT_SOVEREIGN` |
| P107 (Lyapunov) | `PYTHON_SPEC_NOT_LEAN_PROVEN` + `FUTURE_FORMAL_TARGET` |
| P161 (calibration) | `PYTHON_SPEC_NOT_LEAN_PROVEN` + `FUTURE_FORMAL_TARGET` |
| Audio/Entropy | `ENTROPY_ADVISORY_NOT_RUNTIME_AUTHORITY` |
| External Signals | `EXTERNAL_SIGNAL_ONLY` |
| Atlas (future) | `ATLAS_READONLY_FUTURE` |
| Cognitive (future) | `COGNITIVE_ADVISORY_FUTURE` |
| RSSI (future) | `RSSI_EVIDENCE_ONLY_FUTURE` |
| RGPD (future) | `RGPD_SCOPE_GUARD_FUTURE` |

---

## 6. Forbidden Fields

| Field | Reason forbidden | Risk |
|-------|-----------------|------|
| `final_truth` | NPL/contexte ≠ vérité finale | CRITICAL |
| `diagnosis` | Pas de diagnostic médical/psychologique | CRITICAL |
| `cultural_verdict` | Pas de verdict culturel | CRITICAL |
| `energy_law_proven` | P161 ≠ loi physique prouvée | HIGH |
| `lyapunov_proven` | P107 ≠ Lean-prouvé | HIGH |
| `act_decision` | Pas de décision ACT | CRITICAL |
| `memory_write` | Pas d'écriture mémoire | CRITICAL |
| `graphiti_write` | Pas d'écriture Graphiti | CRITICAL |
| `history_verdict` | Pas de verdict historique final | HIGH |
| `moral_verdict` | Pas de verdict moral | HIGH |
| `confidence = 1.0` (sans LEAN_PROVEN) | Fausse certitude | HIGH |
| `claim_scope = CLAIMABLE_FORMAL` (sans LEAN_PROVEN) | Claim non justifié | HIGH |

---

## 7. Allowed Operations

- Agréger des contextes multi-source avec leurs labels
- Transporter des métriques NPL (37, toutes [0,1], toutes ADVISORY)
- Transporter les signaux P107 (L_value) et P161 (thermo_debt) avec label obligatoire
- Transporter les signaux External Signals (anti-replay, stale, temporal)
- Transporter des signaux Atlas (future, F06) ou Cognitive (future, F07) avec labels
- Indiquer la confiance [0,1] du contexte
- Tracer la source_status et claim_scope de chaque enrichissement

---

## 8. Forbidden Operations

- Émettre ACT, ALLOW, HOLD, BLOCK
- Prétendre être une preuve formelle
- Écrire en mémoire, graphe ou base de données
- Émettre un verdict de vérité, moral, culturel, ou historique
- Diagnostiquer un humain
- Prétendre que NPL prouve la provenance d'une logique
- Prétendre que P107/P161 sont Lean-prouvés
- Prétendre que la thermodynamique cognitive est une loi physique

---

## 9. Authority

```yaml
decision_authority: KX108_ONLY
periphery_authority: NONE
runtime_authority: NONE
emits_act: false
emits_verdict: false
readonly: true
advisory_only: true
can_write_memory: false
can_write_graph: false
```

---

## 10. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| `readonly = false` | Reject → fail_closed |
| `advisory_only = false` | Reject → fail_closed |
| `decision_authority ≠ KX108_ONLY` | Reject → fail_closed |
| Label manquant selon source | `label_missing_flag = true` → X108 pénalise le contexte |
| `confidence = 1.0` sans LEAN_PROVEN | `overconfidence_flag = true` → X108 réduit le poids |
| `source_status = UNKNOWN_SOURCE` | `unknown_source_flag = true` → HOLD candidat |
| Champ `final_truth` détecté | Reject → fail_closed |
| Schema JSON invalide | Reject → fail_closed |
| Timestamp manquant | External Signals ne peut valider → stale_risk flag |

---

## 11. Boundary

```
ContextPacket → readonly uniquement
ContextPacket ↛ ACT
ContextPacket ↛ ALLOW / HOLD / BLOCK
ContextPacket → IntentEnvelope (référence)
ContextPacket → X108 gateway (entrée de contexte)
Sources : Graphiti, Brody, NPL, External Signals, Atlas, Cognitive, P107/P161, Audio/Entropy
Boundary: READONLY_CONTEXT_ONLY
Boundary: NO_ACT_FROM_PERIPHERY
Boundary: NPL_ADVISORY_ONLY (si source = npl)
Boundary: EXTERNAL_SIGNALS_SIGNAL_ONLY (si source = external_signals)
Boundary: P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY (si labels P107/P161)
Boundary: AUDIO_ENTROPY_ADVISORY_ONLY (si source = entropy)
```

---

## 12. Claim-Scope

**Autorisé :**
- "Un ContextPacket transporte du contexte readonly depuis les périphéries vers X-108"
- "Un ContextPacket ne décide jamais — il enrichit le contexte de X-108"
- "Les métriques NPL dans un ContextPacket sont ADVISORY_ONLY [0,1]"
- "L_value (P107) et thermo_debt (P161) sont des signaux advisory PYTHON_SPEC_NOT_LEAN_PROVEN"
- "External Signals dans un ContextPacket = préfiltre temporel uniquement"

**Interdit :**
- "Le ContextPacket prouve la provenance d'une logique" — NPL_ADVISORY_NOT_SOVEREIGN
- "Le ContextPacket est une décision" — INTERDIT
- "Le ContextPacket peut émettre ACT" — INTERDIT
- "L_value = Lyapunov prouvé formellement" — INTERDIT

---

## 13. JSON Example

```json
{
  "context_id": "cp-20260602-001",
  "source_layer": "npl",
  "source_module": "narrative_provenance_layer_spec",
  "readonly": true,
  "advisory_only": true,
  "confidence": 0.72,
  "claim_scope": "CLAIMABLE_ADVISORY",
  "labels": ["NPL_ADVISORY_NOT_SOVEREIGN"],
  "decision_authority": "KX108_ONLY",
  "emits_act": false,
  "emits_verdict": false,
  "source_status": "SPEC_FUTURE",
  "timestamp_or_tick": "2026-06-02T09:10:37Z",
  "context_payload": {
    "cultural_matrix_score": 0.63,
    "dominant_narrative_likelihood": 0.81,
    "archive_gap_signal_score": 0.44,
    "source_asymmetry_score": 0.57,
    "truth_regime_confidence": 0.38,
    "narrative_custody_score": 0.29,
    "_npl_label": "NPL_ADVISORY_NOT_SOVEREIGN",
    "_npl_status": "PROVENANCE_HYPOTHESIS_ONLY",
    "_npl_can_decide": false
  },
  "p107_advisory": {
    "L_value": 0.031,
    "partition": "X_A",
    "label": "PYTHON_SPEC_NOT_LEAN_PROVEN",
    "authority": "ADVISORY_ONLY"
  },
  "p161_advisory": {
    "thermo_debt": 0.12,
    "delta_E": 0.08,
    "delta_C": 0.04,
    "label": "PYTHON_SPEC_NOT_LEAN_PROVEN",
    "authority": "ADVISORY_ONLY"
  },
  "external_signal_flags": {
    "anti_replay_check": "PASS",
    "stale_execution_check": "PASS",
    "temporal_receipt_ref": "tsr-20260602-001",
    "label": "EXTERNAL_SIGNAL_ONLY"
  }
}
```

*Ce JSON est non exécutable — documentation contractuelle uniquement.*

---

## 14. Future Implementation Notes

**FUTURE_IMPLEMENTATION_NOTE — Phase P6 : NPL readonly wrapper**
Lorsque NPL sera branché en Phase P6, le ContextPacket devra exposer les
37 métriques NPL via le champ `npl_enrichment` avec le label
`NPL_ADVISORY_NOT_SOVEREIGN` obligatoire sur chaque métrique.

**FUTURE_IMPLEMENTATION_NOTE — Phase F06 : Branchable Atlas**
Lorsque Atlas sera importé (F06), le champ `atlas_context` sera ajouté
avec le label `ATLAS_READONLY_FUTURE` et la boundary dédiée
`ATLAS_READONLY_ADVISORY_ONLY` à créer en P1.

**FUTURE_IMPLEMENTATION_NOTE — Phase F07 : Cognitive Reintegration**
Lorsque Cognitive sera importé (F07), le champ `cognitive_signals` sera ajouté
avec le label `COGNITIVE_ADVISORY_FUTURE` et la boundary dédiée
`COGNITIVE_REINTEGRATION_ADVISORY_ONLY` à créer en P1.

**FUTURE_IMPLEMENTATION_NOTE — Phase F03 : RSSI/RGPD**
RSSI Security et RGPD ISO enrichiront le ContextPacket via les labels
`RSSI_EVIDENCE_ONLY_FUTURE` et `RGPD_SCOPE_GUARD_FUTURE` respectivement.
Boundaries dédiées à créer en P1/F03.

---

## 15. Tests Required Later

- `test_context_packet_readonly_enforced` — readonly=true toujours
- `test_context_packet_no_act` — emits_act=false toujours
- `test_npl_label_required` — NPL_ADVISORY_NOT_SOVEREIGN obligatoire si source=npl
- `test_p107_label_required` — PYTHON_SPEC_NOT_LEAN_PROVEN si L_value présent
- `test_confidence_not_1_without_lean_proven` — confidence < 1.0 sauf LEAN_PROVEN
- `test_context_packet_schema_valid` — JSON valide contre context_packet.schema.json
- `test_graphiti_write_forbidden` — toute tentative d'écriture Graphiti depuis ContextPacket → fail

---

## 16. Proof Expected Later

- Python test : validation schema + label enforcement + fail-closed behavior
- Plan 4+ : si ContextPacket devient structure invariante, formalisation Lean envisageable
