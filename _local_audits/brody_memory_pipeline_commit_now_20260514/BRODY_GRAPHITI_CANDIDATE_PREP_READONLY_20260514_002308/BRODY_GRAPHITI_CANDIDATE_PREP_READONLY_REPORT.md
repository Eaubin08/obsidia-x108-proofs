# BRODY_GRAPHITI_CANDIDATE_PREP_READONLY
**Timestamp :** 20260514_002308  
**Mode :** READONLY — NO_IMPORT — NO_COMMIT — NO_FREEZE — NO_PUSH  
**Autorité :** KX108_ONLY

---

## Précurseur consommé — validé

| Champ | Valeur |
|---|---|
| source_triage_status | BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_DONE |
| candidates_consumed | 42 |
| review_excluded | 4 |
| precursor_valid | true |

---

## Graphiti / Neo4j — Read Path Confirmation

| Champ | Valeur |
|---|---|
| graphiti_read_path_connected | **true** |
| neo4j_live_access_validated | **true** |
| neo4j_uri | bolt://127.0.0.1:7688 |
| brody_memory_doc_nodes_with_text_preview | **3267** |
| low_material_resolved | **true** |
| live_validation_source | `_local_audits/LOW_MATERIAL_LIVE_VALIDATION_READONLY_20260513_231701/` |
| write_path_enabled | false |
| import_path_enabled | false |

---

## Résultats du dry-run

| Type | Fichier | Candidats |
|---|---|---|
| GRAPHITI_CANDIDATES_DRY_RUN | `GRAPHITI_CANDIDATES_DRY_RUN.jsonl` | **42** |
| GRAPHITI_CANDIDATES_REVIEW_EXCLUDED | `GRAPHITI_CANDIDATES_REVIEW_EXCLUDED.jsonl` | **4** |
| **TOTAL** | | **46** |

---

## Distribution des labels Graphiti

| proposed_graphiti_label | Groupe | Candidats |
|---|---|---|
| BrodySessionQuery | A | 2 |
| BrodyRealStateClassification | C | 10 |
| BrodyAuditStep | D | 9 |
| BrodySessionArtifact | E | 21 |
| **TOTAL** | | **42** |

---

## Candidats Review exclus (4)

| candidate_id | Titre | Raison |
|---|---|---|
| TRIAGE_001 | Quel est l'état du kernel dans le corpus Graphiti V20 ? | TRANSITION — uplift CRISTAL requis |
| TRIAGE_003 | Donne-moi la liste de tous les arbres 34 dans le corpus. | TRANSITION — uplift CRISTAL requis |
| TRIAGE_013 | User memory intake candidate auto_triage — step 5 V2 | TRANSITION — uplift CRISTAL requis |
| TRIAGE_022 | Pointers Brody ~90 CURRENT_BRODY*.txt dans x108-proofs | TRANSITION — uplift CRISTAL requis |

---

## Fichiers produits

| Fichier | Rôle |
|---|---|
| `CURRENT_BRODY_GRAPHITI_CANDIDATE_PREP_READONLY.txt` | Précurseur requis par import_dry_run_review_gate |
| `GRAPHITI_CANDIDATES_DRY_RUN.jsonl` | 42 candidats prêts pour review import |
| `GRAPHITI_CANDIDATES_REVIEW_EXCLUDED.jsonl` | 4 candidats TRANSITION exclus |
| `GRAPHITI_NEO4J_READ_PATH_CONFIRMATION.json` | Confirmation read path live |
| `GRAPHITI_CANDIDATE_PREP_SUMMARY.json` | Résumé structuré complet |
| `BRODY_GRAPHITI_CANDIDATE_PREP_READONLY_REPORT.json` | Rapport structuré |
| `BRODY_GRAPHITI_CANDIDATE_PREP_READONLY_REPORT.md` | Ce document |

---

## Guardrails

| Check | Valeur |
|---|---|
| MEMORY_WRITE_ALLOWED | false |
| GRAPHITI_WRITE | false |
| NEO4J_WRITE | false |
| MEMORY_INTAKE | false |
| BRODY_EXECUTE_ALLOWED | false |
| BRODY_AUTHORIZE_ALLOWED | false |
| GROUP_A_STAGED_PRESERVED | true |
| STAGED_FILES_STILL | 136 |
| NO_GIT_ADD | true |
| NO_COMMIT | true |
| NO_FREEZE | true |
| NO_PUSH | true |

---

## Prochaines actions

```
NEXT_BRODY_MEMORY_ACTION=BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY
NEXT_REAL_WORLD_ACTION=BRODY_WORLD_PROVIDER_MATRIX_READONLY
NOTE: 4 TRANSITION candidates require explicit operator uplift to CRISTAL before graphiti_candidate_prep
```

**VERDICT : BRODY_GRAPHITI_CANDIDATE_PREP_READONLY_DONE**
