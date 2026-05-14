# NEXT_REAL_WRITE_PROMPT
## Pour la mission : BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1
## À utiliser UNIQUEMENT si l'opérateur a déclaré explicitement :
## "J'autorise l'écriture canonique des 96 tags sur les 48 nodes validés."
##
## NE PAS ENVOYER CETTE MISSION SANS AUTORISATION EXPLICITE OPÉRATEUR.
## DECISION_AUTHORITY=KX108_ONLY

---

MISSION CLAUDE — BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1

Objectif :
Exécuter l'écriture contrôlée des tags canoniques arbre/famille sur les 48 BrodyMemoryDoc validés.

Autorisation préalable requise :
- operator_approval=true — opérateur a déclaré explicitement son accord
- kx108_gate_pass=true — gate KX108 ouvert

Source du protocole :
_local_audits/BRODY_CANONICAL_TAGGING_WRITE_CANDIDATE_PROTOCOL_READONLY_20260514_020923/

Fichiers à lire en premier :
- CANONICAL_TAGGING_WRITE_PROTOCOL.json
- CANONICAL_TAGGING_WRITE_CYPHER_PLAN.cypher
- ROLLBACK_CANONICAL_TAGGING_PLAN.cypher
- POST_WRITE_VALIDATION_PLAN.json
- WRITE_SCOPE_LOCK.json
- WRITE_FORBIDDEN_ACTIONS.json
- OPERATOR_APPROVAL_TEMPLATE.json

Gate source :
_local_audits/BRODY_CANONICAL_TAGGING_REVIEW_GATE_READONLY_20260514_020148/
- CANONICAL_TAGGING_APPROVED_WRITE_CANDIDATES.jsonl (48 entries)

Opérateur gate :
_local_audits/BRODY_CANONICAL_TAGGING_OPERATOR_GATE_READONLY_20260514_021730/
- OPERATOR_GATE_DECISION_READONLY.json
- CANONICAL_TAGGING_GO_NO_GO_MATRIX.json
- OPERATOR_DECISION_BRIEF.md

Travail demandé :

1. Préflight :
   - Vérifier root staged = 136
   - Vérifier operator_approval=true dans la déclaration opérateur
   - Vérifier kx108_gate_pass=true
   - Vérifier CANONICAL_TAGGING_APPROVED_WRITE_CANDIDATES.jsonl = 48 lignes
   - Vérifier CANONICAL_TAGGING_BLOCKED_ITEMS.jsonl = 0 lignes
   - Ne pas commencer l'écriture si une vérification échoue

2. Exécuter CANONICAL_TAGGING_WRITE_CYPHER_PLAN.cypher :
   - D'abord les 2 CHECK queries en lecture seule (CHECK_01, CHECK_02)
   - Si CHECK_01 ≠ 0 ou CHECK_02 ≠ 48 : STOP, ne pas écrire
   - Exécuter les 48 SET queries une par une
   - Chaque query : MATCH par node_id + WHERE title =~ pattern + SET tags append-only
   - batch_id = "CANONICAL_TAGGING_20260514_020923"
   - Neo4j : bolt://127.0.0.1:7688, auth=(neo4j, obsidia-graphiti-dev)

3. Exécuter POST_WRITE_VALIDATION_PLAN.json :
   - PWV_01 à PWV_10 obligatoires
   - Si un check échoue : STOP + exécuter ROLLBACK immédiatement

4. Si rollback nécessaire :
   - Exécuter ROLLBACK_CANONICAL_TAGGING_PLAN.cypher (48 queries)
   - Vérifier ROLLBACK_SPOT_01 : remaining_tagged = 0
   - Documenter l'échec

5. Produire les fichiers dans :
   _local_audits/BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1_<timestamp>/

   Fichiers requis :
   - CURRENT_BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1.txt
   - WRITE_EXECUTION_LOG.jsonl (une ligne par query exécutée)
   - POST_WRITE_VALIDATION_RESULTS.json (10 checks)
   - ROLLBACK_LOG.jsonl (si rollback exécuté)
   - BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1_REPORT.json
   - BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1_REPORT.md
   - _POINTER_BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1.md

6. Vérifications post-write :
   - root staged count toujours 136
   - aucun git add / commit / freeze / push
   - aucun Graphiti write
   - aucun memory intake
   - aucun runtime binding
   - aucun X108 merge

Règles absolues :
- Append-only sur les tags — jamais SET n.tags = [nouvelle liste complète]
- Ne toucher que les 48 node_ids approuvés
- Ne pas toucher les 9 exclus
- Ne pas toucher T13-T34
- Ne pas modifier title/source/text_preview
- Decision_authority = KX108_ONLY

Sortie finale attendue :

BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1_DONE
WRITES_EXECUTED=48
WRITES_PASS=<n>
WRITES_FAIL=<n>
TAGS_ADDED=<n>
POST_WRITE_VALIDATION=<PASS/FAIL>
ROLLBACK_EXECUTED=<true/false>
NEO4J_WRITE=true
GRAPHITI_WRITE=false
MEMORY_INTAKE=false
DECISION_AUTHORITY=KX108_ONLY
GROUP_A_STAGED_PRESERVED=true
STAGED_FILES_STILL=136
