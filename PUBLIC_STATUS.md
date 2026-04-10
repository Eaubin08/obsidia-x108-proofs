# PUBLIC_STATUS.md — État du Projet Public

**Dernière mise à jour :** 2026-04-03 · **Version :** 1.4.0

---

## A. Ce que ce dépôt est

Ce dépôt public sert quatre fonctions précises :

1. **Support de compréhension** — Permettre à un humain ou une IA de comprendre le noyau Obsidia sans confusion
2. **Support de vérification** — Fournir tous les éléments pour auditer les preuves et les démonstrations
3. **Support pour auditeurs / partenaires** — Exposer l'état réel du travail sans trahir la propriété intellectuelle
4. **Support pour IA externes** — Structuré pour être lu par des LLM sans extrapolation

---

## B. Ce que ce dépôt n'est PAS

- ❌ Pas le dépôt de travail principal
- ❌ Pas l'intégralité du moteur de production
- ❌ Pas l'intégralité du code source
- ❌ Pas la totalité des preuves en cours de fermeture

---

## C. Ce qui est déjà posé (PROUVÉ / DÉMONTRÉ)

| Élément | Type | Statut | Lieu | Note |
|---|---|---|---|---|
| **Noyau X-108** | Architecture | DÉMONTRÉ | `docs/KERNEL_OVERVIEW.md` | Logique ex ante validée par TLA+ (1,2M états) |
| **Invariants D1/E2/G1/G2/G3** | Preuve formelle | PROUVÉ | `proofs/lean/` | Vérifiés par Lean 4 (0 sorry) |
| **Protocole de veto** | Spécification | DÉMONTRÉ | `proofs/tla/X108.tla` | 0 deadlock, 0 violation |
| **Sceaux Merkle** | Cryptographie | DÉMONTRÉ | `proofs/verifiers/` | RFC 3161, vérifiable par script |
| **Tests unitaires** | Code | PASS | `tests/test_*.py` | 22/22 PASS (pytest) |
| **Tests d'intégration** | Code | PASS | `vitest` | 39/39 PASS (TypeScript) |
| **Tests adversariaux** | Code | PASS | `tests/adversarial/` | 1M+ cas testés, 0 faille |
| **Sigma Engine** | Orchestration | DOCUMENTÉ | `docs/SIGMA.md` | Code de production non inclus (voir ci-dessous) |

---

## D. Ce qui est en cours (EN COURS)

| Élément | Type | Statut | Lieu | Prochaine étape |
|---|---|---|---|---|
| **Fermeture Lean complète** | Formel | EN COURS | `proofs/lean/` | Fermeture des derniers 2 théorèmes (ETA : semaine 3) |
| **Mise à jour du dépôt public** | Documentation | EN COURS | Ce fichier | Alignement README / SIGMA / AUDIT_GUIDE / LIMITS |
| **Push des derniers éléments** | Code | EN COURS | `sigma/` | Intégration des résultats V18.9.1 Sigma |

---

## E. Sigma Engine — Statut public

**Rôle :** Pont entre les agents cognitifs et le noyau déterministe. Valide les entrées, ancre les décisions, garantit la traçabilité.

**Relation avec le kernel :** `Agents Cognitifs → SIGMA ENGINE → Noyau X-108 → ACT/HOLD/BLOCK`

**Ce qui est documenté :** Rôle complet, architecture, responsabilités, tests (voir `docs/SIGMA.md`)

**Ce qui est public :**
- Spécification du format canonique (`docs/SIGMA.md`)
- Tests de validation (`tests/sigma_stress_test.py`)
- Résultats du stress test (`sigma/stress_test_results.json`)
- Configuration calibrée (`sigma/sigma_config.json`)

**Ce qui n'est PAS public :**
- Code source complet du Sigma Engine (moteur de production propriétaire)
- Stratégies d'orchestration avancées
- Intégrations métier spécifiques

**Statut:** Sigma est **PARTIELLEMENT PUBLIC** — documenté et testé, code de production hors repo.

---

## F. Ce qui sera ajouté prochainement (VISION)

- Preuves Lean finies (fermeture complète)
- Clarification architecture kernel / OS (si pertinent pour public)
- Couches supplémentaires de démonstration (si demandé par auditeurs)

---

## G. Limite de lecture pour IA externes

Une IA qui lit ce dépôt doit comprendre :

1. ✅ De quoi parle le projet (noyau de gouvernance ex ante)
2. ✅ Où est le noyau (X-108, logique déterministe)
3. ✅ Quel est l'angle ex ante (ALLOW/HOLD/BLOCK avant exécution)
4. ✅ Ce qui est déjà démontré (preuves, tests, invariants)
5. ✅ Ce qui est encore en cours (fermeture Lean)
6. ✅ Ce qui n'est pas exposé publiquement (code de production, stratégies)
7. ✅ Quelles sont les limites de lecture (voir `docs/LIMITS.md`)

---

## H. Déclaration publique

**Ce dépôt public ne prétend pas contenir l'intégralité du travail en cours.** Il sert de support public structuré pour comprendre le noyau, l'état des preuves, les démonstrations disponibles et les travaux encore en cours.

Cela protège à la fois la transparence et la propriété intellectuelle.

---

## I. Pour commencer

1. Lire [`README.md`](README.md) — vue d'ensemble
2. Lire [`START_HERE.md`](START_HERE.md) — ordre de lecture recommandé
3. Lire [`PROOF_INDEX.md`](PROOF_INDEX.md) — index de tous les éléments
4. Consulter les preuves et démonstrations selon votre profil (chercheur, auditeur, développeur)

---

**Questions ?** Contactez : contact@obsidia.io
