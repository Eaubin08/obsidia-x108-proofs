# OS Trad / Reverse OS — Source Pack Candidate

**Généré :** 2026-06-03  
**Palier :** P31  
**Statut :** `OS_TRAD_REVERSE_OS_CANDIDATE_NOT_YET_ACTIVE`  
**Décision d'intégration :** CANDIDAT CONFIRMÉ — branchement runtime P32+

---

## Résumé

Le pack `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip` est le candidat recommandé pour devenir la **8e famille source runtime** `OS_TRAD_REVERSE_OS`. Il est structuré, testable, et conforme à la politique no-ACT. Il n'est **pas encore branché** dans `runtime_wiring/`.

---

## Zips disponibles

| Zip | Taille | Entrées | Tests | .pyc | .ps1 | Statut |
|-----|--------|---------|-------|------|------|--------|
| `V1.zip` | 3,610,848 B | 701 | FAIL | 3 | 0 | Non candidat |
| `V1_PATCHED.zip` | 3,934,443 B | 1176 | FAIL (packaging) | 95 | 0 | Non candidat |
| `V1_P0P1_FIXED.zip` | 3,827,593 B | 629 | **10/10 PASS** | 0 | 0 | **CANDIDAT RECOMMANDÉ** |
| `V1_FREEZE_CANDIDATE.zip` | 3,841,030 B | — | Non audité | ? | ? | Non évalué |
| `V1_FINAL.zip` | 4,157,886 B | 1429 | Non audité | 12 | 1 | Non prioritaire |
| `V1_FINAL_LIGHT_PATCH.zip` | 3,833,286 B | — | Non audité | ? | ? | Non évalué |

---

## Candidat : P0P1_FIXED

### Métriques clés
- **Taille :** 3,827,593 B (3.7 MB)
- **Entrées :** 629 fichiers
- **Tests :** 10/10 PASS (python -m unittest discover -s 17_TESTS)
- **Demo :** `DEMO_MMONDE_PIPELINE_OK` — `non_decision=true`, no ACT
- **Python files :** 63 (bloqués par `readonly_content_loader`)
- **pyc/pycache :** 0
- **Executables (.ps1/.sh) :** 0
- **Racine dans le zip :** `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/`

### Structure top-level (21 dirs)
```
00_INDEX              01_SOURCES             02_CONSTITUTION_LOIS_OBSIDIENNES
03_MEMOIRE_MONDE      04_ARBRES_34           05_SHAZAM_COGNITIF
06_REVERSE_OS_SSR     07_BDF_DOUBLE_CERVEAU  08_HEXAFLUX_LTCU
09_MCP_BRIDGE         10_AGENTS_52           11_AGENTS_RUNTIME_CONTRACTS
12_FRICTION_AVDR      13_GRAPHES             14_CONTEXT_EXPORT_X108_BOUNDARY
15_GUARDS_NON_DECISION 16_VISUALISATION      17_TESTS
18_AUDIT              19_REGISTRES_JSON      20_DEMO_MINIMALE
```

### Contenu clé
- **34 arbres :** `04_ARBRES_34_TENSOR_MATRIX/ARBRE_01__...` × 34 (specs, JSON schema, activation rules)
- **Reverse OS / SSR :** `06_REVERSE_OS_SSR_JARVIS/` — specs SSR, projection Reverse OS
- **X108 boundary :** `14_CONTEXT_EXPORT_X108_BOUNDARY/` — `ContextPacket.schema.json`, `x108_boundary_contract.md`
- **52 agents :** `10_AGENTS_52/agents_52.registry.json` — 9 familles
- **Non-décision :** `15_GUARDS_NON_DECISION/` — guards, aucun `return ACT`
- **Manifest SHA256 :** 628 entrées, 0 erreur

### Non-décision vérifiée
- Aucun `return "ACT"` dans les modules runtime
- `non_decision=true` dans les sorties demo
- Les `.py` seront bloqués par `readonly_content_loader._FORBIDDEN_EXTENSIONS`

---

## Spec de la 8e famille runtime (à activer en P32+)

```python
# Dans source_file_registry.json — entrées à créer
{
    "source_family": "OS_TRAD_REVERSE_OS",
    "source_zip": "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip",
    "adapter_target": "os_trad_reverse_to_context_packet",
    "recommended_decision": "ALLOW_CONTEXT_ONLY",
    "boundary_required": "OS_TRAD_ADVISORY_ONLY",
    "emits_act": false,
    "runtime_allowed_now": false,  # P31 = candidate only
    "decision_authority": "KX108_ONLY"
}
```

### Keywords selector à ajouter (source_family_selector.py)
```python
"OS_TRAD_REVERSE_OS": [
    "os trad", "reverse os", "ssr", "arbre", "arbres", "34 arbres",
    "tensor", "shazam", "hexaflux", "bdf", "mcp bridge",
    "agents 52", "non décision", "pipeline cognitif",
    "context packet", "x108 boundary", "jarvis",
]
```

---

## Actions requises pour activation P32+

1. Copier `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip` dans `_source_packs/raw/` (gitignored)
2. Ajouter les entrées registry pour la famille `OS_TRAD_REVERSE_OS` dans `source_file_registry.json`
3. Ajouter les keywords dans `source_family_selector.py`
4. Ajouter l'adapter `os_trad_reverse_to_context_packet` dans `adapter_target_map.py`
5. Tester avec `tests/api/test_brody_source_pack_context_p2*.py`

---

## Limites actuelles (P31)

- Zip non copié dans `_source_packs/raw/` (P32 action)
- Pas d'entrées registry pour cette famille
- Pas d'adapter actif
- Pas de selector keywords
- Les audits dans le zip (`18_AUDIT/`) restent partiellement placeholder
- Démo minimale fonctionnelle mais pipeline simplifié

---

## Chemins physiques

| Version | Chemin |
|---------|--------|
| P0P1_FIXED (candidat) | `C:/Users/User/Downloads/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip` |
| FINAL | `C:/Users/User/Downloads/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FINAL.zip` |
| Light Patch | `C:/Users/User/Downloads/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FINAL_LIGHT_PATCH.zip` |
