# BoundaryContract
# runtime_contracts/contracts/BoundaryContract.contract.md
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

Le BoundaryContract définit les droits exacts d'un module Obsidia :
ce qu'il peut lire, écrire, émettre, et appeler. Par défaut, tous
les champs sont à leur valeur la plus restrictive.

Il sert de référence pour la validation automatique de la boundary
d'un module lors de la création d'un IntentEnvelope ou ContextPacket.

---

## 2. Required Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `module_name` | string | — | Nom du module |
| `module_type` | enum | — | `KERNEL`, `SIGMA`, `GRAPHITI`, `BRODY`, `NPL`, `ATLAS`, `COGNITIVE`, `EXTERNAL_SIGNALS`, `BALANCE`, `GENCOIN`, `GPS`, `AGENT`, `LLM`, `UNKNOWN` |
| `os_layer` | string | — | `OS1`, `OS2`, `OS3`, `OS4` |
| `readonly` | boolean | `true` | Lecture seule |
| `advisory_only` | boolean | `true` | Advisory uniquement |
| `emits_act` | boolean | `false` | Peut émettre ACT |
| `emits_verdict` | boolean | `false` | Peut émettre verdict |
| `can_write_memory` | boolean | `false` | Peut écrire mémoire |
| `can_write_graph` | boolean | `false` | Peut écrire graphe |
| `can_call_tools` | boolean | `false` | Peut appeler des outils |
| `requires_x108` | boolean | `true` | Passe par X-108 |
| `authority` | enum | `KX108_ONLY` | Autorité décisionnelle |
| `allowed_outputs` | string[] | — | Outputs autorisés explicitement |
| `forbidden_outputs` | string[] | — | Outputs interdits explicitement |
| `source_status` | enum | `UNKNOWN_SOURCE` | Statut formel du module |
| `claim_scope` | enum | `CLAIMABLE_SPEC_ONLY` | Portée des claims publics |

### Defaults absolus (ne jamais surcharger sans approbation humaine)

```yaml
readonly: true
advisory_only: true
emits_act: false
emits_verdict: false
can_write_memory: false
can_write_graph: false
can_call_tools: false
decision_authority: KX108_ONLY
```

---

## 3. Module type boundaries prédéfinies

| Module type | readonly | emits_act | can_write_memory | authority |
|-------------|----------|-----------|-----------------|-----------|
| KERNEL | false (produit DecisionTicket) | true (via ALLOW) | true (via gate) | KX108_ONLY |
| SIGMA | true | false | false | KX108_ONLY |
| GRAPHITI | true | false | false | KX108_ONLY |
| BRODY | true | false | false | KX108_ONLY |
| NPL | true | false | false | KX108_ONLY |
| ATLAS | true | false | false | KX108_ONLY |
| COGNITIVE | true | false | false | KX108_ONLY |
| EXTERNAL_SIGNALS | true | false | false | KX108_ONLY |
| BALANCE | true | false | false | KX108_ONLY |
| GENCOIN | false (mint si X108_ALLOW) | false | false | KX108_ONLY |
| GPS | true | false | false | KX108_ONLY |
| AGENT | true | false | false | KX108_ONLY |
| LLM | true | false | false | KX108_ONLY |

---

## 4. JSON Example

```json
{
  "module_name": "narrative_provenance_layer",
  "module_type": "NPL",
  "os_layer": "OS2",
  "readonly": true,
  "advisory_only": true,
  "emits_act": false,
  "emits_verdict": false,
  "can_write_memory": false,
  "can_write_graph": false,
  "can_call_tools": false,
  "requires_x108": true,
  "authority": "KX108_ONLY",
  "allowed_outputs": ["NarrativeProvenancePacket", "ContextPacket", "PeripheralSignalPacket"],
  "forbidden_outputs": ["DecisionTicket", "ACT", "ALLOW", "HOLD", "BLOCK"],
  "source_status": "SPEC_FUTURE",
  "claim_scope": "CLAIMABLE_SPEC_ONLY"
}
```

---

## 5. Failure Mode

- `emits_act = true` pour module non-KERNEL → violation → fail_closed
- `can_write_memory = true` sans gate humain → violation
- `authority ≠ KX108_ONLY` → reject

---

## 6. Tests Required Later

- `test_boundary_contract_defaults_enforced`
- `test_boundary_contract_non_kernel_no_act`
- `test_boundary_contract_schema_valid`

---

## 7. Claim-Scope

**Autorisé :** "Le BoundaryContract définit les droits d'un module de façon explicite et auditable"
**Interdit :** "Le BoundaryContract autorise un module à décider à la place de X-108"
