# Invariant to Extension Rules — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07

Pour chaque invariant, la règle d'extension définit ce qu'une nouvelle fonctionnalité ou un nouveau module DOIT respecter pour ne pas invalider la garantie.

---

## Règles d'extension par invariant

### DETERMINISM
**Règle :** Toute extension qui introduit un état non-déterministe dans le chemin de décision est INTERDITE.  
**Champs obligatoires :** emits_act, advisory_only  
**Conséquence si violée :** Les théorèmes E2, aggregate4_unanimous et no_two_distinct_supermajorities_4 ne s'appliquent plus.

### NO_ACT_BEFORE_TAU
**Règle :** Aucune extension ne peut court-circuiter le test `beforeTau` pour des décisions irréversibles.  
**Champs obligatoires :** irr flag déclaré, elapsed validé avant decideX108  
**Conséquence si violée :** X108_no_act_before_tau est invalidé — action irréversible possible avant τ.

### HOLD_BEFORE_TAU
**Règle :** Le résultat HOLD avant τ est une garantie Lean. Ne pas remplacer par BLOCK ou état intermédiaire.  
**Conséquence si violée :** Comportement avant τ devient non-déterministe ou bloquant.

### IRREVERSIBLE_ACTION_DELAY
**Règle :** Post-τ, la décision suit exactement la base. Ne pas ajouter de délai supplémentaire non-prouvé.  
**Conséquence si violée :** X108_irreversible_after_tau_equals_base ne couvre plus le comportement post-tau.

### REVERSIBLE_ACTION_BASELINE
**Règle :** Les actions réversibles n'ont pas de délai. Ne pas appliquer `beforeTau` si irr=false.  
**Conséquence si violée :** Actions réversibles bloquées sans justification formelle.

### NEGATIVE_CLOCK_SKEW_TO_HOLD
**Règle :** Les bridges temporels doivent préserver le comportement HOLD en cas de skew négatif.  
**Conséquence si violée :** Une horloge corrompue pourrait déclencher ACT au lieu de HOLD.

### THRESHOLD_CONSERVATION
**Règle :** Conserver exactement aggregate4 (4 votants, seuil 3/4). Modifier le quorum invalide les preuves.  
**Champs obligatoires :** 4 votants exact, seuil 3 exact  
**Conséquence si violée :** no_two_distinct_supermajorities_4 et aggregate4_fail_closed ne s'appliquent plus.

### BLOCK_PRIORITY_OVER_HOLD_ALLOW
**Règle :** Le default fail-closed est prouvé. Ne pas ajouter `else ACT` ou `else HOLD` dans aggregate4.  
**Conséquence si violée :** Comportement défaut devient non-sécurisé (ACT ou HOLD par défaut).

### HOLD_PRIORITY_OVER_ALLOW
**Règle :** L'ordre de priorité BLOCK > HOLD > ACT est prouvé. Ne pas inverser dans un fork ou adapter.  
**Conséquence si violée :** Actions autorisées dans des contextes où elles devraient être retenues.

### GUARD_X108_FINAL_AUTHORITY
**Règle :** Aucune couche périphérique ne peut prendre une décision finale. Guard seul est autorité.  
**Champs obligatoires :** has_kx108_authority=False pour tout composant non-Guard  
**Conséquence si violée :** Décisions prises sans validation X-108.

### SIGMA_POST_GUARD_VETO_ONLY
**Règle :** Tout ajout à sigma/ doit rester en mode veto-only. Sigma ne propose pas, ne décide pas.  
**Conséquence si violée :** Sigma devient une couche décisionnelle non-prouvée.

### NO_PERIPHERY_DECISION_AUTHORITY
**Règle :** Tout ajout périphérique doit déclarer emits_act=False et advisory_only=True.  
**Champs obligatoires :** emits_act=False, advisory_only=True  
**Conséquence si violée :** Composant périphérique émet des décisions sans gate KX108.

### NO_GRAPHITI_WRITE
**Règle :** graphiti_v20_readonly_client.py — GET uniquement, write=False. Confirmer dans tout audit P7X+.  
**Conséquence si violée :** Écriture graphiti non-gatée = mutation état sans autorité KX108.

### NO_MEMORY_WRITE_WITHOUT_GATE
**Règle :** SRL = lecture seule. Tout write nécessite gate explicite KX108.  
**Champs obligatoires :** memory_write_enabled=False par défaut  
**Conséquence si violée :** État mémoire session modifiable sans contrôle.

### NO_KERNEL_MUTATION_FROM_PERIPHERY
**Règle :** kernel_mutation_enabled=False. Aucun adaptateur périphérique ne doit modifier le kernel ou la trace.  
**Conséquence si violée :** G1 invalide — trace mutée, audit compromis.

### DRY_RUN_ONLY_ADAPTERS
**Règle :** DRY_RUN_ONLY: bool = True dans chaque adapter. Confirmer emits_act=False avant tout runtime load.  
**Champs obligatoires :** DRY_RUN_ONLY=True, emits_act=False, advisory_only=True  
**Conséquence si violée :** Adapter source émet une décision réelle sans gate Guard.

### BUS_PROPOSE_ONLY
**Règle :** Bus adapter avec emit_act=True = violation critique. Bus = PROPOSE_ONLY.  
**Conséquence si violée :** Bus devient décisionnel — court-circuit du Guard.

### ROUTE_AUTH_BOUNDARY
**Règle :** Toute nouvelle route exposant des données doit ajouter `Depends(require_api_key)`.  
**Finding ouvert :** POST /preview + POST /os-map/query sans auth (P69/P71).  
**Conséquence si violée :** Données source exposées sans authentification.

### NETWORK_EGRESS_REVIEW_REQUIRED
**Règle :** Tout nouveau connecteur avec `requests.post()` ou socket ouvert doit passer audit P7X avant runtime.  
**Champs obligatoires :** dry_run_declared=True, kx108_authority_declared=False  
**Conséquence si violée :** Action réseau irréversible sans gate KX108.

### SOURCE_PACK_NOT_CANON_BY_EXISTENCE
**Règle :** Pack LOCAL_ONLY_UNCANONIZED ≠ runtime-loadable. Exiger MANIFEST_SHA256.json + source_file_registry.  
**Conséquence si violée :** Pack non-vérifié chargé comme source canonique.

### ARCHIVE_NOT_RUNTIME
**Règle :** SOURCE_ARCHIVE_ONLY = jamais runtime-loadable. Merkle seal = preuve d'intégrité, non de chargeabilité.  
**Conséquence si violée :** Archive gelée rechargée en runtime — données historiques potentiellement corrompues.

### PYTHON_TESTED_NOT_LEAN_PROVEN
**Règle :** Ne jamais écrire « prouvé » pour un test pytest. Utiliser LEAN_PROVEN uniquement si `#print axioms` valide.  
**Conséquence si violée :** Sur-claim public — communication mensongère sur le périmètre de preuve.

### KX108_ONLY_DECISION_AUTHORITY
**Règle :** `has_kx108_authority` doit être True pour tout composant prenant des décisions. Sinon `emits_act=False` obligatoire.  
**Conséquence si violée :** Autorité décisionnelle diffuse — perte de traçabilité des décisions.
