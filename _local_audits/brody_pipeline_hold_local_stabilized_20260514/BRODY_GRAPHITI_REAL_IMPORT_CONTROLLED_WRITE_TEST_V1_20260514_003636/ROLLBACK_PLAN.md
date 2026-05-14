# ROLLBACK_PLAN — BRODY_REAL_IMPORT_20260514_003636

**Statut :** PRÊT — NON EXÉCUTÉ  
**Batch_ID :** `BRODY_REAL_IMPORT_20260514_003636`  
**Label cible :** `BrodyImportedMemory`  
**Autorité :** KX108_ONLY

---

## Commande rollback

```cypher
MATCH (n:BrodyImportedMemory {batch_id: 'BRODY_REAL_IMPORT_20260514_003636'})
DETACH DELETE n
```

Fichier Cypher : `ROLLBACK_PLAN.cypher`

---

## Périmètre du rollback

| Champ | Valeur |
|---|---|
| Nœuds ciblés | Uniquement `BrodyImportedMemory` avec `batch_id=BRODY_REAL_IMPORT_20260514_003636` |
| Nœuds attendus à supprimer | 42 |
| BrodyMemoryDoc impactés | **0** — nœuds existants non touchés |
| Relations | DETACH DELETE supprime les relations incidentes uniquement |

---

## Conditions d'exécution du rollback

Le rollback **NE DOIT PAS** être exécuté sauf si :

1. L'opérateur donne l'autorisation explicite
2. Un échec critique post-import est constaté (post_import_read_validation=FAIL, ou corruption détectée)
3. La validation POST_WRITE_VALIDATION.json indique un état incohérent

**État actuel :** POST_IMPORT_READ_VALIDATION=PASS — rollback non requis.

---

## Vérification pré-rollback recommandée

```cypher
MATCH (n:BrodyImportedMemory {batch_id: 'BRODY_REAL_IMPORT_20260514_003636'})
RETURN count(n) AS nodes_to_delete
```

Attendu : 42

---

**ROLLBACK_EXECUTED=false — NE PAS EXÉCUTER SANS AUTORISATION OPÉRATEUR**
