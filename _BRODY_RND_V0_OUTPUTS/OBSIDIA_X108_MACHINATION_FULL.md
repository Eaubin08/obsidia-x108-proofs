# OBSIDIA_X108_MACHINATION_FULL.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Vue d'ensemble : L'architecture complète Obsidia X-108

### Le paradigme fondamental

```
"L'IA propose, le Juge dispose."
```

Obsidia X-108 est un **noyau de gouvernance déterministe**. Il sépare strictement deux espaces :

- **L'Espace Latent** : zone d'exploration libre de l'IA (cognition, hypothèses, contexte)
- **Le Noyau Déterministe** : juge mathématique qui évalue les actions avant exécution

---

## Le stack constitutionnel complet

Source : `docs/architecture/OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0.md`

```
INPUT
  ↓
Control Plane        ← orchestre les gates, fusionne les signaux, ne décide pas
  ↓
Data Gate            ← pureté des données entrantes
  ↓
Provenance           ← traçabilité de l'origine
  ↓
Memory               ← mémoire stabilisée (Mémoire Fractale)
  ↓
Sigma Engine         ← agrégation des agents domain, recommandation
  ↓
EML                  ← Energie / Mémoire / Langage (couche symbolique)
  ↓
Energy/Thermo        ← thermodynamique informationnelle
  ↓
Timeverse            ← contexte temporel, constance
  ↓
OCS                  ← Operational Constance System
  ↓
Operational Constance Agent
  ↓
Permission/Economic  ← gates de permission et couche économique (Gencoin)
  ↓
X-108 KERNEL         ← DÉCISION SOUVERAINE : ACT / HOLD / BLOCK
  ↓
OS3                  ← preuve cryptographique de la décision
  ↓
Gencoin              ← valeur / récompense / ancrage économique
  ↓
Feedback             ← boucle de retour vers mémoire candidate
```

---

## Le noyau X-108 en détail

### Rôle

Le Kernel X-108 est le "juge" qui évalue les actions **avant exécution** (paradigme ex ante). Il n'utilise aucune IA générative. Il évalue des **invariants mathématiques**.

### Verdicts possibles

| Verdict | Quand | Conséquence |
|---|---|---|
| **ACT** (ALLOW) | Tous les invariants respectés | Exécution immédiate |
| **HOLD** | Seuil de certitude insuffisant | Attendre clarification |
| **BLOCK** | Violation d'invariant détectée | Refus d'exécution |

### Les 5 invariants formels (Lean 4, 0 sorry)

| Invariant | Domaine | Vérification |
|---|---|---|
| **D1** | Décision | Non-contradiction des règles |
| **E2** | Exécution | Déterminisme du vote |
| **G1** | Gouvernance | Immuabilité de la trace |
| **G2** | Gouvernance | Cohérence du sceau Merkle |
| **G3** | Gouvernance | Absence de contradiction circulaire |

---

## Le pipeline Sigma

Sigma est l'**orchestrateur d'agrégation**. Il reçoit les signaux des agents domaine et produit une recommandation vers X-108.

```
Agent domaine 1 (vote + score)  ┐
Agent domaine 2 (vote + score)  ├→ SIGMA (agrégation pondérée) → recommandation → X-108
Agent domaine 3 (vote + score)  ┘
```

**Outputs Sigma publics :**
- `market_verdict`
- `x108_gate`
- `reason_code`
- `decision_id`
- `trace_id`
- `ticket_required` / `ticket_id`
- `attestation_ref`
- `sigma_report`

---

## La couche de traçabilité

Chaque décision est scellée en 3 couches :

```
Decision ID : DEC-{DOMAIN}-{TIMESTAMP}-{HASH}
Trace ID    : TRACE-{DECISION_ID}-{MERKLE_ROOT}
Merkle Root : Merkle(decision_1, ..., decision_n)
RFC 3161    : Signature(Merkle_Root, Timestamp, Authority) → immuable
```

---

## Protocole TLA+ — Preuves distribuées

**X108.tla** : 1,2M états explorés, 0 violation → protocole X-108 correct
**DistributedX108.tla** : veto distribué sans deadlock → cohérence multi-agents

---

## Le module BRODY dans le stack

BRODY ne fait **pas partie du chemin de décision**. Il est en périphérie :

```
Utilisateur → BRODY (contexte advisory) → Sigma (si applicable) → X-108 (décision)
                   ↑
           BRODY répond. X108 décide.
```

BRODY peut alimenter Sigma avec des signaux contextuels (advisory), mais ne peut jamais décider.

---

## Les domaines réels couverts

| Domaine | Équivalence | Exemples de cas |
|---|---|---|
| **Banking** | Économie | Fraude, virements suspects, comportements anormaux |
| **Trading** | Marché | Ordres massifs, volatilité, liquidité, slippage |
| **GPS/Defense** | Trajectoire/Source/Temps/Énergie | Brownout, source conflict, time skew, omega chaos |
| **E-Commerce** | Ventes | Commandes frauduleuses, intent analysis |
| **Gouvernance** | Accès systèmes | Anomalies d'accès, heure/géo inhabituels |

---

## Les agents cognitifs (Espace Latent)

| Agent | Rôle |
|---|---|
| **Le Douteur** | Friction cognitive, critique des hypothèses |
| **Le Nettoyeur Cognitif** | Purge de l'Espace Latent |
| **L'Empathe** | Adaptation contexte humain |
| **Le Clarificateur (Shazam)** | Synthèse, résolution de complexité |

---

## Ce que le système NE FAIT PAS

- ❌ Génération de contenu
- ❌ Décisions métier (juge les règles, pas la stratégie)
- ❌ Stockage de données
- ❌ Connexion directe aux systèmes (via Sigma)
- ❌ Prédictions (évalue les invariants, pas l'avenir)
- ❌ Contournement possible (disjoncteur mathématique)

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
