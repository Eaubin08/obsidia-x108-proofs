# Agents, rôles et gardiens — version consolidée

## Lecture correcte

Les sources ne donnent pas une liste exhaustive de classes de code `Agent`.
Elles donnent surtout des rôles, couches, gardiens, verifiers et exemples d’agents obsidiens.
Donc ce fichier sépare : agents obsidiens R&D, rôles système, adapters, et gardiens de fond.

## Liste consolidée

### AGENT_001 — Observateur
- Type : agent_obsidien_R&D
- Source : src_branche149 — Branche 85 : Entités Cognitives / Agents Obsidia
- Fonction : Observer l’état, les flux, les signaux faibles et les variations sans décider.
- Frontière kernel : Ne décide jamais. Remonte contexte et anomalies.
- Liens : Bloc 13, P137, P138, OS3, OS4

### AGENT_002 — Sentinelle
- Type : agent_obsidien_R&D
- Source : src_branche149 — Branche 85
- Fonction : Surveiller les conditions critiques, seuils, incohérences, menaces et dérives.
- Frontière kernel : Peut alerter ou recommander HOLD/BLOCK, ne force jamais ALLOW.
- Liens : ADeLe, OS-S, Audit F, Bloc 7

### AGENT_003 — Gardien
- Type : agent_obsidien_R&D / gardien de fond
- Source : src_branche149 — Branche 85 + checklist A24 Gardien des Métriques
- Fonction : Garder une frontière, une métrique, une règle ou un invariant.
- Frontière kernel : Surveille et signale. La décision souveraine reste X-108.
- Liens : A24, T1-T12, OS-S, X-108

### AGENT_004 — Architecte
- Type : agent_obsidien_R&D
- Source : src_branche149 — Branche 85
- Fonction : Assembler, relier, cadrer et proposer des structures systémiques.
- Frontière kernel : Ne modifie pas le noyau sans audit/gate.
- Liens : Bloc 13, Bloc 15, C4, G4

### ROLE_005 — Human Operator
- Type : rôle_responsabilité
- Source : src_40spec — Spec 26 Liability Boundary & Responsibility Graph
- Fonction : Porte l’intention, le veto et l’autorisation finale.
- Frontière kernel : Responsable de l’intention et de l’autorisation, pas d’une exécution technique non autorisée.
- Liens : Spec 26, Human Veto, Audit C

### ROLE_006 — Governance Layer
- Type : rôle_système
- Source : src_40spec — Spec 26
- Fonction : Appliquer les policies et gouverner les frontières d’action.
- Frontière kernel : Ne remplace pas OS3/X-108, applique le contrat.
- Liens : Spec 11, Spec 26, ADeLe

### ROLE_007 — OS3 Audit Layer
- Type : rôle_système
- Source : src_40spec — Spec 26
- Fonction : Porter la trace, l’audit, le replay et la preuve.
- Frontière kernel : Trace sans narration décisionnelle.
- Liens : OS3, Spec 1, Spec 2, Spec 5, Spec 7

### ROLE_008 — Agents / Tools
- Type : rôle_outils
- Source : src_40spec — Spec 26
- Fonction : Exécuter ou assister dans leur scope déclaré.
- Frontière kernel : Jamais décisionnaires.
- Liens : Spec 9, Spec 10, MCP, Adapters

### GUARDIAN_009 — Sigma Verifier
- Type : gardien_de_fond
- Source : checklist domaine 5
- Fonction : Vérifier l’orchestration Sigma.
- Frontière kernel : Produit un PASS/FAIL de vérification.
- Liens : Tests Python, Audit D, G3

### GUARDIAN_010 — Merkle Verifier
- Type : gardien_de_fond
- Source : checklist domaine 5
- Fonction : Vérifier immutabilité et intégrité Merkle.
- Frontière kernel : Vérifie la trace, ne décide pas.
- Liens : Merkle, Spec 2, Audit A/D

### GUARDIAN_011 — RFC3161 Verifier
- Type : gardien_de_fond
- Source : checklist domaine 5
- Fonction : Vérifier preuve temporelle légale.
- Frontière kernel : Certifie le temps, ne décide pas.
- Liens : RFC3161, Spec 17, Audit D

### GUARDIAN_012 — TLA Verifier
- Type : gardien_de_fond
- Source : checklist domaine 5
- Fonction : Vérifier SafetyX108 / NoDeadlock / NoLivelock.
- Frontière kernel : Modèle formel, pas runtime décisionnel.
- Liens : TLA+, G1/G3

### ROLE_013 — Orchestrator
- Type : rôle_runtime
- Source : checklist domaine 5
- Fonction : Coordonner le flux complet entre kernel, adapters, agents et audits.
- Frontière kernel : Coordonne, ne contourne pas le guard.
- Liens : Vitest, Integration, Spec 15

### ROLE_014 — Adapter MCP
- Type : adapter_outil
- Source : src_40spec + checklist Spec 9
- Fonction : Mapper outils/scopes vers policy gate.
- Frontière kernel : Aucun tool call hors policy.
- Liens : Spec 9, Spec 10, Spec 12

### ROLE_015 — Cortex
- Type : rôle_couche
- Source : src_40spec Event Schema / traces
- Fonction : Couche de traitement/contextualisation mentionnée dans le schéma event.
- Frontière kernel : Ne doit pas modifier OS3.
- Liens : Spec 1, OS4, CORTEX

### GUARDIAN_016 — GPS — Gardien / Guide / Alerteur
- Type : périphérie_sigma
- Source : DocD mentions GPS + mémoire projet
- Fonction : Guider la cohérence, alerter, orienter.
- Frontière kernel : Ne décide jamais.
- Liens : Sigma, OS4, G4

### GUARDIAN_017 — ADeLe
- Type : gouvernance_alignement
- Source : checklist domaine 8
- Fonction : Contrôler l’alignement critique Banking / Trading / Aviation.
- Frontière kernel : Peut refuser ou demander HOLD, ne force pas ALLOW.
- Liens : Audit F, G3, Bloc 11, OS-S

## Risque de manque

Oui, il peut manquer des agents concrets si le repo réel contient des classes/fichiers non présents dans les docs source.
Avec les documents fournis, cette liste couvre les rôles explicitement détectables ou inférables sans inventer une fausse implémentation.
