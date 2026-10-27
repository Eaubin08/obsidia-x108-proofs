# BRODY_EDUCATION_MODULES_V0.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Modules éducatifs Obsidia X-108 — V0

Ces modules constituent la base d'un curriculum d'apprentissage sur le système Obsidia X-108. Chaque module est autonome et peut être lu indépendamment.

---

## MODULE 01 — Qu'est-ce qu'Obsidia X-108 ?

**Niveau :** Débutant | **Durée estimée :** 20 min | **Sources :** README.md, PUBLIC_STATUS.md, START_HERE.md

### Objectif

Comprendre ce qu'est Obsidia X-108, à quoi il sert, et ce qu'il n'est pas.

### Contenu

**Définition :** Obsidia X-108 est un noyau de gouvernance déterministe. C'est un "juge mathématique" qui évalue les actions d'agents IA *avant* qu'elles s'exécutent.

**Ce que c'est :**
- Un périmètre public de preuve et vérification (P1)
- Un kernel déterministe avec preuves formelles Lean 4 + TLA+
- Un pipeline exécutable (Python, PowerShell)
- Une couche Sigma publique minimale

**Ce que ce n'est pas :**
- Un moteur de production complet
- Une application business finale
- Un cockpit opérateur institutionnel
- Un LLM ou une IA générative

**Le paradigme fondamental :**
```
Intention / Agent → [KERNEL X-108] → ACT / HOLD / BLOCK → Trace / Preuve
```

**Statut actuel :** P1 FERMÉ. Tag : `p1-freeze-2026-04-22`. Commit : `99e966a`. Tous les tests PASS.

### Exercice

Lire `PUBLIC_STATUS.md` et identifier : quels 9 domaines sont à l'état PASS ? Qu'est-ce que PASS garantit ? Qu'est-ce qu'il ne garantit pas ?

---

## MODULE 02 — Le Kernel X-108 : le juge mathématique

**Niveau :** Intermédiaire | **Durée estimée :** 30 min | **Source principale :** docs/KERNEL_OVERVIEW.md

### Objectif

Comprendre comment X-108 prend une décision et pourquoi elle est deterministe et immuable.

### Contenu

**Les 3 verdicts :**

| Verdict | Quand | Conséquence |
|---|---|---|
| ACT | Tous les invariants respectés | Exécution immédiate |
| HOLD | Seuil de certitude insuffisant | Attendre clarification |
| BLOCK | Violation d'invariant | Refus d'exécution |

**Le pipeline en 8 étapes :**
1. Réception du signal par le kernel
2. Validation des invariants locaux (D1, E2)
3. Vote des agents domaine
4. Agrégation des votes par Sigma
5. Décision du kernel (ACT/HOLD/BLOCK)
6. Scellement (Decision ID + Trace ID + Merkle Root)
7. Ancrage RFC3161 (timestamp immuable)
8. Exécution (ou refus)

**Les 5 invariants prouvés en Lean 4 :**
- D1 : Les règles ne se contredisent pas
- E2 : Même input = même vote (déterminisme)
- G1 : La trace ne peut pas être modifiée
- G2 : L'arbre Merkle est cohérent
- G3 : Aucune contradiction circulaire

### Exercice

Simuler mentalement : une transaction bancaire de 15 000€ vers un compte inconnu avec fraud_score=0.9. Quel verdict ? Pourquoi ? Quels agents votent ?

---

## MODULE 03 — BRODY : la surface conversationnelle

**Niveau :** Intermédiaire | **Durée estimée :** 25 min | **Sources :** docs/brody/

### Objectif

Comprendre ce qu'est BRODY, ses invariants, et pourquoi il ne peut pas décider.

### Contenu

**Règle fondamentale :**
```
Brody répond. X108 décide.
Contexte ≠ Décision.
```

**Ce que BRODY fait :**
- Répond en langage naturel
- Fournit du contexte et des analyses
- Route les requêtes selon la langue
- Suggère des flags (advisory input vers Sigma)

**Ce que BRODY ne peut pas faire :**
- Émettre ACT, BLOCK, HOLD (emits_act=False, emits_verdict=False)
- Écrire en mémoire (memory_write=False)
- Muter le kernel (kernel_mutation=False)
- Décider (decision_authority=KX108_ONLY toujours)

**La séparation des rôles :**
```
BRODY  → contexte (signal)
SIGMA  → agrégation
X108   → décision souveraine
OS3    → preuve cryptographique
```

**Le contrat invariant (BRODY_RESPONSE_CONTRACT_V1) :**
Chaque réponse BRODY porte 8 champs invariants. Toute violation → BRODY_CONTRACT_VIOLATION.

### Exercice

Identifier, dans une réponse BRODY hypothétique, ce qui serait une violation de contrat : "Je valide cette transaction et l'autorise à s'exécuter."
→ Violations : emits_verdict=True (implicite), decision_authority violée.

---

## MODULE 04 — Sigma : l'agrégateur

**Niveau :** Intermédiaire | **Durée estimée :** 20 min | **Source :** docs/SIGMA.md, sigma/

### Objectif

Comprendre le rôle de Sigma dans le pipeline, ses inputs, ses outputs, et sa position.

### Contenu

**Position dans le stack :**
```
Agents domaine → SIGMA (agrégation) → recommandation → X-108 (décision)
```

Sigma ne décide pas non plus. Il agrège les votes et produit une recommandation.

**Outputs Sigma publics :**
```
market_verdict, x108_gate, reason_code,
decision_id, trace_id, ticket_required, ticket_id,
attestation_ref, sigma_report
```

**Les domaines Sigma :**
- bank_agents.py : Fraude, comportement, validation
- trading_agents.py : Marché, liquidité, volatilité
- gps_defense_aviation_agents.py : Source, temps, énergie
- ecom_agents.py : Trafic, intent, fraude
- meta_agents.py : Identité, anomalie, conformité

**Sigma public P1 ≠ Sigma production :**
Le repo expose une couche minimale auditable. La couche production complète reste propriétaire.

### Exercice pratique

```bash
python sigma/run_pipeline.py bank sigma/examples/bank_normal.json
python sigma/run_pipeline.py bank sigma/examples/bank_suspicious.json
```
Observer la différence de verdict et de reason_code.

---

## MODULE 05 — Preuves formelles : Lean 4 et TLA+

**Niveau :** Avancé | **Durée estimée :** 45 min | **Sources :** PROOF_INDEX.md, formal/tla/, proofs/lean/

### Objectif

Comprendre la différence entre "testé" et "prouvé formellement".

### Contenu

**Lean 4 — Preuves mathématiques**

Lean 4 est un assistant de preuve. Quand on dit qu'un invariant est "prouvé" avec 0 sorry, ça signifie que la preuve est complète et vérifiée mécaniquement — aucune étape n'est assumée.

Les 5 invariants prouvés de ce repo :
- D1 : Non-contradiction des règles de gouvernance
- E2 : Déterminisme du vote
- G1 : Immuabilité de la trace
- G2 : Cohérence du sceau Merkle
- G3 : Absence de contradiction circulaire

**TLA+ — Model checking**

TLA+ est un langage de spécification formelle. TLC (le model checker) explore *tous* les états possibles du système.

- X108.tla : 1,2M états explorés, 0 violation
- DistributedX108.tla : veto distribué prouvé sans deadlock

**La différence "testé" vs "prouvé" :**

| Testé (pytest) | Prouvé (Lean 4 / TLA+) |
|---|---|
| Vérifie des cas spécifiques | Prouve pour TOUS les cas possibles |
| Peut manquer des edge cases | Aucun edge case possible |
| 22/22 PASS → 22 cas OK | Invariant G1 → trace TOUJOURS immuable |

### RFC3161 — L'ancrage temporel

RFC3161 est le standard d'horodatage cryptographique. Il permet à un tiers de vérifier qu'une signature existait *à un moment précis*.

Pipeline : Merkle Root → TSA (Trusted Stamp Authority) → Signature + Timestamp → immuable

---

## MODULE 06 — Les domaines réels : Bank, Trading, GPS

**Niveau :** Débutant | **Durée estimée :** 30 min | **Source :** USE_CASES.md, docs/architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md

### Objectif

Comprendre concrètement comment X-108 gouverne des opérations réelles.

### Contenu — 5 cas d'usage réels

**Cas 1 : Blocage fraude bancaire 8 000€**
→ Avant exécution, kernel bloque. Transaction jamais exécutée. Trace immuable. Zéro perte.

**Cas 2 : Autorisation ordre trading 500 BTC**
→ Kernel évalue volatilité, liquidité, exposition. ACT ou HOLD selon conditions marché.

**Cas 3 : Refus commande e-commerce suspecte 500€**
→ Intent Analysis + Fraud Detection → BLOCK. Aucune expédition.

**Cas 4 : Délai accès système critique**
→ Anomalie heure/géo → HOLD. Attente vérification supplémentaire.

**Cas 5 : Audit régulateur**
→ Decision ID → Trace ID → Merkle Root → RFC3161 → preuve complète et immuable.

### Domaines GPS/Defense

Obsidia gère aussi des scénarios non-financiers :
- GPS brownout : perte partielle de signal → HOLD
- GPS omega chaos : défaillances multiples → BLOCK
- Source conflict : sources contradictoires → investigation

Cela prouve que X-108 est domain-agnostic : tout système où des agents votent sur une action peut être gouverné.

---

## MODULE 07 — La World Call Gateway et la frontière monde

**Niveau :** Avancé | **Durée estimée :** 20 min | **Source :** docs/WORLD_CALL_GATEWAY_INTEGRATION_REPORT.md

### Objectif

Comprendre comment Obsidia empêche les agents IA d'agir dans le monde réel sans autorisation.

### Contenu

**Invariant V4 absolu :**
```
egress_allowed = False (TOUJOURS)
dry_run_only   = True  (TOUJOURS)
```

Aucun agent ne peut sortir vers le monde réel en V4. Tout passe par la gateway et produit un journal local append-only.

**Pipeline :**
```
ActionCandidate → risk classification → world call classification
→ autonomy level → sovereign ticket (dry_run=True)
→ gateway (egress=False) → local journal
```

**WorldCallClass :**
- NO_WORLD_CALL, READ_ONLY, REVERSIBLE → autorisés (dry-run)
- IRREVERSIBLE → niveau d'autonomie 4+ requis
- CRITICAL, FORBIDDEN → BLOCK immédiat

**Secret boundary :** `assert_no_secret_in_agent_payload()` s'exécute avant tout gateway pass.

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
