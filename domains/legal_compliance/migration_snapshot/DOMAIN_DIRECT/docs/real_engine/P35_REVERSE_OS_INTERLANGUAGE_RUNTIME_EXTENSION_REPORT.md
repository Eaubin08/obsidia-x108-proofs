# P35 — Reverse OS Interlanguage Runtime Extension Report

**Branche :** p10-real-engine-controlled-bridge  
**Date :** 2026-06-03  
**Verdict :** P35_REVERSE_OS_INTERLANGUAGE_RUNTIME_EXTENSION_READY

---

## Contexte

P34 a canonisé `_source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/` en pack local propre.
P35 branche ce pack dans la chaîne source runtime existante, sous la famille `OS_TRAD_REVERSE_OS`
avec subfamily `REVERSE_OS_INTERLANGUAGE_CANON_V1`.

---

## Fichiers branchés dans le runtime

### Chaîne de branchement

```
REVERSE_OS_INTERLANGUAGE_CANON_V1 (P34 directory pack)
  → source_pack_resolver.py       — résolution répertoire local
  → source_file_registry.json     — 9 entrées P35 avec source_subfamily
  → registry_loader.py            — chargement source_subfamily
  → registry_to_adapter_dry_run.py — dispatch vers adapter P35
  → source_adapters.py            — reverse_os_interlanguage_to_context_packet()
  → ContextPacket                 — boundary REVERSE_OS_INTERLANGUAGE_ADVISORY_ONLY
  → X108 gate                     — ALLOW_CONTEXT_ONLY (pas de décision)
  → OS3 evidence                  — readonly, advisory
  → Brody context                 — enrichi avec source_subfamily + concepts_detected
  → API preview                   — selected_families + hydrated_entries
```

### Fichiers modifiés

| Fichier | Modification |
|---|---|
| `runtime_wiring/source_registry/registry_types.py` | +2 à VALID_ADAPTER_TARGETS (os_trad + interlanguage) ; +`source_subfamily` field |
| `runtime_wiring/source_registry/registry_loader.py` | Lecture `source_subfamily` dans JSON et CSV loaders |
| `runtime_wiring/source_runtime/source_pack_resolver.py` | Résolution répertoires en plus des ZIPs dans `_source_packs/` |
| `runtime_wiring/source_adapters.py` | +`reverse_os_interlanguage_to_context_packet()` |
| `runtime_wiring/source_registry/registry_to_adapter_dry_run.py` | Import + `_ADAPTER_DISPATCH` P35 |
| `runtime_wiring/source_runtime/source_family_selector.py` | +15 mots-clés interlanguage dans OS_TRAD_REVERSE_OS |
| `runtime_wiring/source_registry/source_file_registry.json` | +9 entrées P35 |

### Fichiers créés

| Fichier | Rôle |
|---|---|
| `runtime_wiring/source_runtime/reverse_os_interlanguage_index.py` | Layer index 6 couches + index builder |
| `tests/test_reverse_os_interlanguage_runtime_extension_p35.py` | 28 tests runtime |
| `tests/api/test_reverse_os_interlanguage_preview_p35.py` | 5 tests API |
| `docs/real_engine/P35_REVERSE_OS_INTERLANGUAGE_RUNTIME_EXTENSION_REPORT.md` | Ce rapport |

---

## Registry — 9 entrées ajoutées

| fichier | extension | couche | bytes |
|---|---|---|---|
| `evidence/reverse_os_interlanguage_canon_v1.json` | .json | IR_ALPHABET_LAYER | 12 593 |
| `evidence/interlanguage_proof_obligations_v1.md` | .md | PROTOCOLS_TRANSDUCTION_LAYER | 1 318 |
| `evidence/interlanguage_transduction_v1.md` | .md | PROTOCOLS_TRANSDUCTION_LAYER | 2 454 |
| `evidence/audience_packet_07_investor.json` | .json | AUDIENCE_PROJECTION_LAYER | 5 283 |
| `evidence/audience_packet_08_non_tech.json` | .json | AUDIENCE_PROJECTION_LAYER | 3 367 |
| `evidence/architecture_narrative_reverse_os.txt` | .txt | REVERSE_OS_NARRATIVE_LAYER | 4 070 |
| `evidence/architecture_protocoles_os_cognitif.txt` | .txt | PROTOCOLS_TRANSDUCTION_LAYER | 5 775 |
| `evidence/plan_execution_industriel.txt` | .txt | EXECUTION_PLAN_LAYER | 10 509 |
| `support/universal_io_matrix_samples/matrix_cell_0181_*.json` | .json | UNIVERSAL_IO_SUPPORT_LAYER | 2 231 |

Chaque entrée : `source_family=OS_TRAD_REVERSE_OS`, `source_subfamily=REVERSE_OS_INTERLANGUAGE_CANON_V1`,
`runtime_allowed_now=false`, `emits_act=false`, `decision_authority=KX108_ONLY`.

---

## Selector — règles P35

Requêtes qui sélectionnent `OS_TRAD_REVERSE_OS` avec extension P35 :
- `"IR alphabet"`, `"alphabet ir"`
- `"reverse os interlanguage"`
- `"réciproque miroir"`, `"reciproque miroir"`
- `"TWIN_CALL"`, `"twin call"`
- `"SCF réciproque"`, `"inversion path"`
- `"translation layer"`, `"OS Trad interlanguage"`
- `"interlanguage canon"`, `"alphabet reverse"`

---

## ContextPacket exemple

```json
{
  "context_id": "cp-dryrun-reverse_os_interlanguage-<hash>",
  "source": "reverse_os_interlanguage_canon_v1",
  "boundary": "REVERSE_OS_INTERLANGUAGE_ADVISORY_ONLY",
  "advisory_only": true,
  "readonly": true,
  "runtime_allowed_now": false,
  "emits_act": false,
  "decision_authority": "KX108_ONLY",
  "payload": {
    "interlanguage_layer": "IR_ALPHABET_LAYER",
    "semantic_role": "IR_ALPHABET_SPEC",
    "source_subfamily": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
    "evidence_pack": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
    "canonization_source": "P34",
    "concepts_detected": [
      "IR_ALPHABET", "RECIPROQUE_MIROIR", "REVERSE_OS_INTERLANGUAGE",
      "SCF_RECIPROQUE", "TWIN_CALL", "AUDIENCE_PROJECTION"
    ],
    "_interlanguage_can_act": false,
    "_interlanguage_can_decide": false,
    "_alphabet_ir_included": true,
    "_reciproque_miroir_included": true,
    "_dry_run": true
  }
}
```

---

## API preview exemple

`POST /api/runtime-wiring/source-runtime/preview`
```json
{"query": "IR alphabet reverse OS interlanguage canon", "limit": 3}
```

Réponse :
```json
{
  "source_runtime_status": "PREVIEW_READY",
  "selected_families": ["OS_TRAD_REVERSE_OS"],
  "x108_decision": "ALLOW_CONTEXT_ONLY",
  "x108_decision_authority": "KX108_ONLY",
  "readonly": true,
  "emits_act": false,
  "decision_authority": "KX108_ONLY"
}
```

---

## Preuve no ACT / runtime_allowed_now=false

- `validate_invariants()` appelé à chaque `ContextPacket` — lèverait `AssertionError` si `emits_act=True`
- `_is_forbidden()` dans `registry_to_adapter_dry_run.py` bloque tout entry avec `runtime_allowed_now=True`
- `VALID_ADAPTER_TARGETS` liste explicitement l'adapter — toute entrée avec adapter non listé → forbidden
- `readonly_content_loader.py` interdit `.py` — `ForbiddenFileError` levée
- 0 fichier `.py` dans le pack P34 (vérifié par test P34)

---

## Différence P34 vs P35

| P34 | P35 |
|---|---|
| Pack local isolé (`_source_packs/`) | Branché dans source runtime |
| Pas dans le registry | 9 entrées dans `source_file_registry.json` |
| Tests d'intégrité de fichiers | Tests runtime end-to-end |
| `runtime_allowed_now=false` (manuel) | `runtime_allowed_now=false` (enforced by invariants) |
| Pas de ContextPacket | ContextPacket avec boundary + payload |

---

## Limites restantes

1. **Hydration réelle** : les entrées P35 sont dans le registry et routable en dry-run, mais
   la hydration complète (lecture du contenu des fichiers) nécessite que le pack resolver
   retourne correctement `source_type="directory"`. ✓ Validé par `test_p35_pack_p34_is_resolvable`.

2. **source_family = OS_TRAD_REVERSE_OS** : P35 est une extension/subfamily d'OS_TRAD, pas
   une 9e famille indépendante. `source_runtime_family_count` reste 8.

3. **canonicalization_needed=True** pour IR_ALPHABET et REVERSE_LANGUAGE dans le ZIP OS_TRAD —
   les concepts sont formalisés dans le Core Parent mais pas encore dans le ZIP source.

4. **Workbench front-end** : le workbench affiche les familles et les paquets via l'API source
   runtime — les entrées P35 apparaîtront dans `hydrated_entries` sous `OS_TRAD_REVERSE_OS`.
   Pas de refactor front nécessaire.

---

## Prochain palier P36

Options :
- **P36A** : Intégrer `reverse_os_interlanguage_canon_v1.json` dans le ZIP OS_TRAD source
  pour passer `canonicalization_needed` de `True` à `False` pour IR_ALPHABET et RECIPROQUE_MIROIR
- **P36B** : Valider la hydration complète du pack P34 via `source_context_hydrator.py`
  avec tests `test_hydration_if_pack_present` (skip si pack absent)
- **P36C** : Créer une 9e famille runtime dédiée `REVERSE_OS_INTERLANGUAGE_CANON` si le
  volume de fichiers justifie une famille indépendante

---

## Fichiers P35 stagés

```
runtime_wiring/source_runtime/reverse_os_interlanguage_index.py    — NEW
runtime_wiring/source_adapters.py                                   — MODIFIED (+adapter P35)
runtime_wiring/source_registry/registry_types.py                    — MODIFIED (+2 VALID_TARGETS)
runtime_wiring/source_registry/registry_loader.py                   — MODIFIED (+source_subfamily)
runtime_wiring/source_registry/registry_to_adapter_dry_run.py      — MODIFIED (+dispatch P35)
runtime_wiring/source_registry/source_file_registry.json            — MODIFIED (+9 entrées)
runtime_wiring/source_runtime/source_pack_resolver.py              — MODIFIED (+dir resolution)
runtime_wiring/source_runtime/source_family_selector.py            — MODIFIED (+15 keywords)
tests/test_reverse_os_interlanguage_runtime_extension_p35.py       — NEW (28 tests)
tests/api/test_reverse_os_interlanguage_preview_p35.py             — NEW (5 tests)
docs/real_engine/P35_REVERSE_OS_INTERLANGUAGE_RUNTIME_EXTENSION_REPORT.md — NEW
```

## Commit

```
feat(p35): connect reverse os interlanguage canon to source runtime
```
