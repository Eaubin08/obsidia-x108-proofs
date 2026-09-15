# BRODY_V1_PROJECT_STORYLINE.md
# Pack: BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Statut : VALIDATED_BY_REPO + HISTORIC_USEFUL (clairement distingués)
# Sources : PUBLIC_STATUS.md, git log, BRODY_PROJECT_HISTORY.md (Cowork — HISTORIC_USEFUL)

---

## Le problème central : le droit d'agir

À l'origine d'Obsidia X-108 se trouve une question simple et fondamentale :

**Comment savoir si une IA a le droit d'agir ?**

Dans les systèmes conventionnels, une IA agit, puis on vérifie après coup.
C'est le paradigme ex post — vérification après exécution. Ce paradigme
est insuffisant dans les domaines à haute fréquence et haute conséquence :
une transaction bancaire frauduleuse exécutée et annulée laisse une trace.
Un ordre de trading mal jugé peut cascader en millisecondes.
Une décision de navigation GPS erronée ne se corrige pas en vol.

Obsidia X-108 répond à ce problème par le paradigme **ex ante** :
le juge mathématique évalue avant d'autoriser.

```
L'IA propose. Le Juge dispose.
```

---

## La naissance : gouvernance déterministe

L'idée centrale : remplacer le "on verra après" par des invariants mathématiques
vérifiés avant chaque action. Ces invariants ne sont pas des règles heuristiques —
ce sont des **preuves formelles**, vérifiées par Lean 4 et TLA+.

Les preuves ne mentent pas. Elles ne se fatiguent pas. Elles ne dérivent pas.

---

## Phase P1 — Le premier périmètre public (VALIDATED_BY_REPO)

**Source :** `PUBLIC_STATUS.md`, `git log`

Le 22 avril 2026, le périmètre public P1 a été gelé.

**Jalons :**
- `99e966a` — Commit de gel public
- `p1-freeze-2026-04-22` — Tag officiel
- `v1.0.0-stable-kernel` — Release GitHub

**Ce qui est livré et reproductible :**
- 5 invariants Lean 4 prouvés (D1, E2, G1, G2, G3) — sans sorry
- TLA+ : 1,2M états, 0 violation
- Python verifiers : `verify_all.py`, `verify_decision.py`, `verify_merkle.py`
- Sigma public minimal : `run_pipeline.py`, `sigma_monitor.py`, `contracts.py`
- 9 domaines PASS

**Ce qui n'est pas dans P1 :**
- Moteur de production propriétaire complet
- Couche Sigma de production complète
- Cockpit opérateur institutionnel

PASS P1 = vérifiabilité déterministe. Pas déploiement production.

---

## L'émergence de Brody — Le moteur de contexte

Brody est né du besoin de donner une **surface naturelle** à l'architecture.
X-108 est un juge mathématique — il ne parle pas. Sigma est un agrégateur —
il ne répond pas. Il fallait un composant qui puisse :

1. Recevoir des questions en langage naturel
2. Assembler du contexte à partir des différentes couches
3. Formuler des réponses compréhensibles
4. Faire tout cela sans jamais décider

Brody a été conçu comme un **FIRST_CLASS_X108_MODULE** de la couche PERIPHERY —
présent et utile, mais toujours soumis à l'autorité de X-108.

Son contrat (`BRODY_RESPONSE_CONTRACT_V1`) cristallise cette séparation :
`advisory_only=True`, `emits_act=False`, `emits_verdict=False`.

---

## Le CIC — La mémoire causale de chaque décision

À chaque appel Brody, un paquet de contexte causal (CIC) est assemblé.
Il contient le contexte du domaine, les familles de métriques confirmées,
les règles centrales, les capacités interdites.

Le `cic_receipt` (avec son `invocation_hash`) permet le **replay** :
toute décision peut être rejouée et auditée avec exactement le même
contexte causal. La traçabilité est cryptographiquement ancrée.

---

## Phase P2 — Banking (HISTORIC_USEFUL — source Cowork)

**Source :** `BRODY_PROJECT_HISTORY.md` (ZIP Cowork — HISTORIC_USEFUL)
**Note :** Éléments observés via audits locaux, non tous vérifiés par lecture directe des fichiers.

Après P1, l'extension vers les scénarios bancaires avancés a débuté :
- Tests adversariaux bank
- Scénarios de confusion, fuzzing sécurité, proxy réglementaire
- Batches de transactions à l'échelle
- Matrices de confusion

---

## HEAD actuel — commit 783e664 (VALIDATED_BY_REPO)

**Source :** `git log`

```
783e664 feat(cic): bind ncp and scraping readonly contexts
```

Ce commit ajoute `ncp_context` et `scraping_context` comme stubs advisory
read-only dans le CIC. C'est la Phase 3 de la liaison des fournisseurs de contexte.
92/92 tests PASS. 44/44 checks E2E PASS.

---

## Le fil conducteur : du signal à la preuve

```
Question utilisateur
  → Brody assemble le contexte (CIC)
  → Sigma agrège les votes des agents domaine
  → X-108 applique les invariants mathématiques
  → Verdict : ACT / HOLD / BLOCK
  → OS3 produit la preuve cryptographique
  → RFC3161 ancre le timestamp
  → Merkle tree garantit l'immuabilité
  → CIC Receipt permet le replay et l'audit
```

À chaque étape, chaque transformation est traçable, rejouable, auditée.
C'est le sens profond d'Obsidia X-108 : non pas un système qui agit,
mais un système qui **prouve qu'il avait le droit d'agir**.
