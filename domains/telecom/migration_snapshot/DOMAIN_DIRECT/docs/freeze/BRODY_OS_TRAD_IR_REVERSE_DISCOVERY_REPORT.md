# BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT
**Date :** 2026-05-20  
**Mode :** READONLY DISCOVERY  
**Autorité :** KX108_ONLY

---

## Résultat

**BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_PASS**
Sources trouvées dans repos externes — non bridgeables dans l'API sans engine-candidate.

---

## Fichiers trouvés

### OS Trad

| Fichier | Chemin | Description |
|---|---|---|
| `adapter.py` | `engine/core_full/modules/os_trad/adapter.py` | PROPOSE module — compile `.os` spec → python/js. Intent: OS_TRAD/OS_TRAD_BUILD |
| `os1.py` | `engine/core_full/modules/os_trad/vendor/obsidia_os1/os1.py` | Moteur OS1 — alphabet units, structural translation |
| `parse_input.py` | `engine/core_full/modules/os_trad/vendor/obsidia_os1/parse_input.py` | Parsing des unités de sens |

**Nature :** OS Trad est un module de génération de code à partir de specs `.os`. C'est un outil de compilation (spec→python/js), pas un pipeline de réponse structurée. Il opère dans l'engine-candidate hors API.

### IR / Reverse OS

| Fichier | Chemin | Description |
|---|---|---|
| `zip2_reverse_os_real_adapter.py` | `obsidia-engine-candidate/bridge/zip2_reverse_os_real_adapter.py` | Reverse OS sur vecteur 34 arbres (tree_vector float[34]) |
| `zip2_context_export_real_adapter.py` | `obsidia-engine-candidate/bridge/zip2_context_export_real_adapter.py` | Export contexte engine-candidate |

**Nature :** Reverse OS utilise des vecteurs d'arbres activés (`activated_trees`, tree_vector[34]). Spécifique au pipeline zip2 de l'engine-candidate. Pas importable directement dans l'API sans le package zip2 complet.

---

## Status bridgeability

| Composant | Status | Raison |
|---|---|---|
| OS Trad (code generation) | NOT_BRIDGEABLE_TO_API | Opère sur specs `.os`, pas sur messages utilisateur |
| OS Trad (structural units / unités de sens) | FOUND_IN_EXISTING_SOURCES | `obsidia_os1/parse_input.py` — mais requiert engine-candidate |
| IR Candidate | PARTIALLY_FOUND | `ir_candidate` est utilisé dans l'API comme placeholder structurel |
| Reverse OS / os_reverse_projection | FOUND_IN_EXISTING_SOURCES | `zip2_reverse_os_real_adapter.py` — mais lié à zip2 package |
| Alphabet units | FOUND_IN_EXISTING_SOURCES | Dans `os1.py` — hors scope API directe |

---

## Ce qui existe dans l'API actuelle

| Champ API | Source | Valeur |
|---|---|---|
| `translation_trace.os_trad_status` | Placeholder | `"READONLY_PASS"` |
| `translation_trace.alphabet_units` | Placeholder | `[]` |
| `translation_trace.ir_candidate` | Structurel | `intent_type, entities, constraints, risk_flags` |
| `translation_trace.os_reverse_projection` | Placeholder | `{"readonly": True, "advisory_only": True}` |

Ces champs existent dans le payload mais sont des placeholders structurels. Ils ne sont pas connectés aux modules OS Trad / Reverse de l'engine-candidate.

---

## Recommandation

Les modules OS Trad et Reverse OS sont des composants de l'engine-candidate (hors obsidia-x108-proofs). Les brancher dans l'API nécessite :
1. Un protocole d'import engine-candidate → x108-proofs approuvé par opérateur
2. Une autorisation KX108 explicite (runtime binding)
3. Un test de boundary complet

**Décision courante :** `NOT_BRIDGEABLE_TO_API_WITHOUT_OPERATOR_APPROVAL`

---

*BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_PASS — 2026-05-20 — KX108_ONLY*
