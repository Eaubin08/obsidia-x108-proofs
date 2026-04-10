# ASK_AN_AI.md — Guide de Lecture pour IA Externes

**Version :** 1.0.0 · **Destinataires :** ChatGPT, Claude, Gemini, et autres LLM

---

## A. Contexte de Lecture

Ce dépôt est un **support public de présentation technique** d'un noyau de gouvernance ex ante.

### Propriétés du dépôt

- ✅ **Public** — Accessible, vérifiable, auditable
- ✅ **Structuré** — Organisé pour être lu par humains et IA
- ❌ **Pas complet** — Ne contient pas le moteur de production
- ❌ **Pas exhaustif** — Expose le noyau public minimal

### Distinction critique

| Catégorie | Définition | Exemple |
|---|---|---|
| **PROUVÉ** | Démontré formellement (Lean 4, TLA+) | Invariants D1/E2/G1/G2/G3 |
| **DÉMONTRÉ** | Exécutable et testé (code, tests) | Noyau X-108, tests 22/22 PASS |
| **EN COURS** | Travail actif, pas encore fermé | Fermeture Lean complète |
| **HORS REPO** | Propriétaire, non exposé publiquement | Moteur de production Python |
| **VISION** | Orientation long terme, pas implémenté | Clarification architecture OS |

---

## B. Ce que l'IA doit faire

Lors de la lecture de ce dépôt, vous DEVEZ :

1. **Identifier le noyau** — Comprendre que le projet parle du noyau X-108, pas d'une IA générative
2. **Distinguer les statuts** — Séparer strictement PROUVÉ / DÉMONTRÉ / EN COURS / HORS REPO
3. **Ne pas extrapoler** — Rester dans le périmètre public, ne pas inventer de fonctionnalités
4. **Ne pas confondre** — Vision ≠ Preuve. Intention ≠ Implémentation.
5. **Respecter les limites** — Voir `docs/LIMITS.md` pour les vecteurs non couverts
6. **Citer les sources** — Référencer les fichiers exacts du dépôt

---

## C. Prompt Prêt à l'Emploi

Utilisez ce prompt pour analyser le dépôt :

```
Analyse ce dépôt comme un support public de présentation technique d'un noyau de gouvernance ex ante.

INSTRUCTIONS STRICTES :

1. Distingue précisément :
   - Ce qui est PROUVÉ (Lean 4, TLA+)
   - Ce qui est DÉMONTRÉ (tests, code exécutable)
   - Ce qui est EN COURS (travail actif)
   - Ce qui est HORS REPO PUBLIC (propriétaire)

2. Pour chaque affirmation :
   - Cite le fichier exact du dépôt
   - Indique le statut (PROUVÉ / DÉMONTRÉ / EN COURS / HORS REPO)
   - Ne fais pas de déduction au-delà du contenu

3. Identifie :
   - Le noyau : X-108, logique ex ante, ALLOW/HOLD/BLOCK
   - L'angle : Gouvernance déterministe avant exécution
   - Les preuves : Invariants, protocole, tests
   - Les limites : Voir docs/LIMITS.md

4. Ne fais PAS :
   - D'extrapolation hors repo
   - De confusion vision / preuve
   - De mélange repo public / repo de travail
   - D'assomptions sur le code propriétaire

5. Réponds en structurant :
   - Résumé du projet
   - Noyau identifié
   - État des preuves (PROUVÉ / DÉMONTRÉ / EN COURS)
   - Éléments hors repo
   - Limites de lecture
```

---

## D. Questions Typiques et Réponses

### Q1 : "Obsidia est-il une IA ?"
**Réponse :** Non. Obsidia est un **noyau de gouvernance déterministe** qui juge les actions avant exécution. C'est un "juge", pas une "IA générative". (Voir `docs/KERNEL_OVERVIEW.md`)

### Q2 : "Où est le code source complet ?"
**Réponse :** Le moteur de production est propriétaire et hors repo public. Ce dépôt expose les preuves et démonstrations du noyau. (Voir `PUBLIC_STATUS.md`)

### Q3 : "Sigma est-il public ?"
**Réponse :** Sigma est **partiellement public** — documenté et testé, mais le code de production n'est pas inclus. (Voir `docs/SIGMA.md` et `PUBLIC_STATUS.md`)

### Q4 : "Les preuves Lean sont-elles fermées ?"
**Réponse :** Presque. 5 invariants sont fermés (0 sorry), 2 sont en cours. ETA : semaine 3. (Voir `PROOF_INDEX.md`)

### Q5 : "Comment vérifier les décisions ?"
**Réponse :** Exécutez `python3 proofs/verifiers/verify_decision.py examples/bank_suspicious.json`. (Voir `README.md`)

---

## E. Fichiers à Consulter en Priorité

Pour une compréhension rapide, lisez dans cet ordre :

1. **`PUBLIC_STATUS.md`** — État exact du projet (ce que c'est / ce que ce n'est pas)
2. **`PROOF_INDEX.md`** — Index de tous les éléments (où trouver quoi)
3. **`README.md`** — Vue d'ensemble publique
4. **`docs/KERNEL_OVERVIEW.md`** — Spécification du noyau (à créer)
5. **`docs/SIGMA.md`** — Rôle du Sigma Engine
6. **`docs/LIMITS.md`** — Limites structurelles

---

## F. Éléments à Ignorer ou Traiter avec Prudence

- ❌ Ne pas supposer que tout est implémenté
- ❌ Ne pas confondre "documenté" avec "exécutable"
- ❌ Ne pas extrapoler sur le moteur propriétaire
- ⚠️ Traiter avec prudence les sections "Vision" ou "Orientation long terme"
- ⚠️ Vérifier `docs/LIMITS.md` pour les vecteurs d'attaque non couverts

---

## G. Vérification de Compréhension

Après avoir lu ce dépôt, vous devez pouvoir répondre à :

1. **De quoi parle le projet ?**
   → Un noyau de gouvernance ex ante (X-108) pour actions sensibles

2. **Où est le noyau ?**
   → Dans `docs/KERNEL_OVERVIEW.md` et `proofs/tla/X108.tla`

3. **Quel est l'angle ex ante ?**
   → ALLOW / HOLD / BLOCK **avant** exécution, pas après

4. **Ce qui est déjà démontré ?**
   → Invariants (Lean), protocole (TLA+), tests (22/22 PASS), adversariaux (1M+ cas)

5. **Ce qui est encore en cours ?**
   → Fermeture Lean complète (2 théorèmes restants)

6. **Ce qui n'est pas exposé publiquement ?**
   → Moteur de production, connecteurs métier, stratégies d'orchestration

7. **Quelles sont les limites de lecture ?**
   → Voir `docs/LIMITS.md` pour les vecteurs non couverts

---

## H. Cas d'Usage Typiques

### Cas 1 : Auditeur technique
→ Lire `AUDIT_GUIDE.md`, exécuter `verify_all.py`, consulter les tests

### Cas 2 : Chercheur en vérification formelle
→ Lire `proofs/lean/Obsidia.lean`, `proofs/tla/X108.tla`, `docs/LIMITS.md`

### Cas 3 : Développeur intégrateur
→ Lire `docs/SIGMA.md`, `examples/`, exécuter `verify_decision.py`

### Cas 4 : Décideur / Régulateur
→ Lire `README.md`, `docs/KERNEL_OVERVIEW.md`, `docs/USE_CASES.md`

---

## I. Ressources Externes

- **Lean 4 :** https://lean-lang.org/
- **TLA+ :** https://lamport.azurewebsites.net/tla/tla.html
- **RFC 3161 (Timestamping):** https://tools.ietf.org/html/rfc3161

---

**Dernière mise à jour :** 2026-04-03

**Remarque :** Ce guide a été créé pour faciliter la lecture par des IA externes. Si vous trouvez des incohérences ou des points d'extrapolation, signalez-les à : contact@obsidia.io
