# F52 — Bus/Bridge : Intention Architecturale

**Artifact:** `OBSIDIA_F52_BUS_BRIDGE_INTENT`  
**Palier:** F52  
**Date:** 2026-05-29  

---

## Ce que bus/bridge N'est PAS

bus/bridge n'est pas :
- Un simple endpoint de statistiques
- Deux tests orphelins sans signification
- Une dette technique sans intérêt
- Une fonctionnalité abandonnée

---

## Ce que bus/bridge EST

bus/bridge est une **surface de connexion existentielle** — une interface capable de répondre à la question :

> *"Quel est l'état réel de l'ensemble du projet à cet instant ?"*

Elle doit pouvoir répondre **sans donner d'autorité de décision à Brody**, en exposant uniquement de l'état observable.

---

## Dimensions couvertes par bus/bridge

### État interne du runtime
- Santé des processus uvicorn
- État des ports
- Routes actives et disponibles

### État de l'enveloppe de sortie
- Couverture OutputEnvelopeV1 sur l'ensemble des routes
- Cohérence des flags boundary

### État de préparation
- Readiness demo/runtime de toutes les surfaces
- Disponibilité des connecteurs opérateur / workbench

### État des preuves
- Intégrité de la chaîne F-palier (F24→F52+)
- Statut des manifestes de gel
- Derniers SHA256 de référence

### État d'audit
- Dernier résultat d'audit F-palier
- Dernier run de tests (baseline, F47.1/F47.2/F47.3)
- Présence des tags git

### État des routes
- Inventaire OpenAPI
- Santé des routes V1

### Contexte mémoire / Graphiti / Brody
- Disponibilité du contexte advisory
- Aucune écriture — lecture seule

### Signaux entrants externes
- Ce qui arrive de l'extérieur du projet
- Demandes de connexion, requêtes d'audit, signaux de supervision

### Statut existentiel global
- Comment l'ensemble de la machinerie répond à un instant donné

---

## Contrat de souveraineté (préservé pour F53)

bus/bridge expose de l'état — il ne décide pas.

| Contrainte | Valeur |
|-----------|--------|
| `decision_authority` | `KX108_ONLY` |
| `brody_role` | `advisory_readonly` |
| `allowed_to_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| Brody peut lire l'état | Oui |
| Brody peut décider | Non |

---

## Statut des tests F52

Les tests `test_output_envelope_bus_stats.py` et `test_output_envelope_bus_bridge.py` sont **mis en quarantaine** (skip), pas supprimés. Ils représentent un contrat valide — prématuré par rapport à l'implémentation, mais architecturalement correct.

Le contrat sera honoré en F53+.

---

## Prochaine étape : F53

F53 produira le **plan contractuel complet** de bus/bridge :

1. Inventaire exact de ce que bus/bridge doit exposer
2. Schéma d'ingest des signaux externes
3. Architecture de connexion Brody / Graphiti / runtime / preuves / audit
4. Protocole KX108_ONLY — état sans décision
5. Schéma de réponse pour `/bus/stats` et `/bus/bridge`
6. Plan d'implémentation F54+

---

*F52 · QUARANTINE ONLY · bus/bridge INTENT PRESERVED · KX108_ONLY · 2026-05-29*
