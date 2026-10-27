# Cartographie Exhaustive des Sources et Fichiers Obsidia

**Objectif :** Localiser précisément chaque fichier source, chaque archive ZIP, les versions canoniques des formules mathématiques, et les spécifications à coder pour builder la suite du projet Obsidia.

---

## 1. Inventaire des Archives ZIP (Bundles de Déploiement)
Voici la liste exacte des archives ZIP transmises, leur rôle et leur contenu clé. Elles contiennent le code source réel du backend Python et de l'interface React/TypeScript OS4.

### `obsidia_engine_v1_0_0-1.zip`
**Rôle :** Moteur Python canonique (Backend souverain) — Version 1.0.0 gelée
**Fichiers clés à l'intérieur :**
- `forge_os01_x108_v1/src/obsidia_os0/` : Base gelée (Axiomes, Contrat, IR, Sandbox)
- `forge_os01_x108_v1/src/obsidia_os1/` : Orchestration des décisions et Guard X-108
- `forge_os01_x108_v1/src/obsidia_os2/` : Métriques structurelles (pure functions, équilibre)
- `forge_os01_x108_v1/CANONICAL_FREEZE.txt` : Marqueur de gel canonique
- `forge_os01_x108_v1/CANONICAL_HASH.sha256` : Hash de sécurité de la version

### `agent-trad_v25_global_merge_bundle.zip`
**Rôle :** Bundle de fusion globale de la famille agent-trad (V20 à V24)
**Fichiers clés à l'intérieur :**
- `DEPENDENCY_MATRIX_V25.md` : Matrice des dépendances inter-repos
- `GLOBAL_CLAIMS_MATRIX_FINAL.md` : Matrice globale des revendications
- `MERGE_ORDER_V25.md` : Ordre de fusion (Core → Deploy → Compliance → Distributed)
- `NOT_YET_PROVEN_GLOBAL.md` : Ce qui reste à prouver (audit externe, load test)

### `os4_x108_fusion_merge_bundle_v1.zip`
**Rôle :** Code source React/TypeScript pour l'intégration de la couche de décision X-108
**Fichiers clés à l'intérieur :**
- `client/src/components/Canonical*.tsx` : Composants UI canoniques (Decision, Proof, Simulation)
- `client/src/pages/BankWorld.tsx`, `TradingWorld.tsx`, `EcomWorld.tsx` : Pages métiers patchées
- `server/canonical/` : Bridge backend et contrats (TypeScript)
- `server/engines/guardX108.ts`, `tradingEngine.ts`, `bankEngine.ts` : Moteurs locaux
- `docs/OS4_MERGE_ORDER.md`, `OS4_FUSION_STATUS.md` : Documentation d'intégration

### `os4_e2e_freeze_pack_v1.zip`
**Rôle :** Template opérationnel de validation End-to-End
**Fichiers clés à l'intérieur :**
- `docs/REAL_ACCEPTANCE_CHECKLIST.md` : Checklist d'acceptation pour passer en REAL
- `docs/CAPTURE_PROTOCOL.md` : Protocole de capture des preuves (payloads, screenshots, logs)
- `PAYLOAD_SNAPSHOTS/*.json` : Snapshots des payloads de succès (trading, bank, ecom, replay)

### `os4_runtime_validation_freeze_bundle_v1.zip`
**Rôle :** Bundle de validation du runtime OS4
**Fichiers clés à l'intérieur :**
- `BACKEND_UI_SOURCE_OF_TRUTH_MAP.md` : Cartographie de la source de vérité (Backend souverain vs UI)
- `REAL_PARTIAL_SCAFFOLD_STATUS.md` : Statut d'intégration des zones (Bank, Trading, Preuves)
- `OS4_ObsidiaLabTrad_Payload_Validation_Matrix_v1.md` : Matrice de validation des payloads JSON

### `os4_x108_decision_layer_targeted_pack.zip`
**Rôle :** Pack ciblé pour la couche décisionnelle
**Fichiers clés à l'intérieur :**
- `client/src/pages/DecisionFlow.canonical.patch.example.tsx` : Code source de la page Decision
- `client/src/components/DecisionTicketPanel.canonical.example.tsx` : Panel des tickets

---

## 2. Localisation des Formules Mathématiques Canoniques
Les versions canoniques et finales des formules mathématiques qui fondent le couplage AGI / Déterministe se trouvent dans les e-mails de formalisation. Voici où les retrouver exactement dans les documents d'audit :

| Concept Mathématique | Source (Où trouver la formule exacte) | Fichier Spec Cible à Builder |
|---|---|---|
| Les 7 Fonctions Canoniques ($\mathcal{S}, \mathcal{O}, \mathcal{C}, \mathcal{T}, \mathcal{K}, \mathcal{U}_M, \mathcal{F}_Z$) | E-mail du 13 mars 2026 (Audit 7J - Section 3) | `obsidia/specs/04_real_canonization.md` et `obsidia/specs/05_latent_space.md` |
| Les 7 Géométries ($\mathcal{G}_S \to \mathcal{G}_{top}$) | E-mail du 14 mars 2026 (Audit 7J - Section 4) | `obsidia/specs/01_inter_layer_constitution.md` |
| Équations de l'Espace Latent (Guard X-108 et Promotion) | E-mail du 14 mars 2026 (Audit 7J - Section 5) | `obsidia/specs/05_latent_space.md` |
| Modèle de Fidélité sous Perturbation ($Faithful(\tau_t)$) | E-mail du 14 mars 2026 (Audit 7J - Section 8) | `obsidia/specs/08_security_layer.md` |
| Cadre BSD Autonome ($\Phi_E, \widehat{\Phi}_E, \widetilde{\Phi}_E, P_E, B_E, W_E$) | E-mail 99 du 28 mars 2026 (Audit Part 2) | `obsidia/specs/00_kernel_contract.md` |

---

## 3. Ce qu'il reste à faire (L'Arborescence Cible à Builder)
D'après l'ordre maître et l'arborescence cible (E-mail 52 du 25 mars 2026), le prochain travail consiste à transformer la théorie en spécifications exécutables. Voici les fichiers exacts qui doivent être créés ou complétés dans le dépôt cible.

### A. Le dossier des Spécifications (`obsidia/specs/`)
Ces fichiers Markdown doivent contenir les objets typés, les états définis et les triggers clos pour chaque bloc.
- `00_kernel_contract.md` : Fermer le centre (Cadre BSD, axiomes)
- `01_inter_layer_constitution.md` : Fermer les droits / interdits (Géométries)
- `02_object_registry.md` : Fermer la grammaire (Objets et statuts)
- `03_status_transitions.md` : Fermer les transitions d'états
- `04_real_canonization.md` : Fermer l'entrée (Fonctions S, O, C)
- `05_latent_space.md` : Fermer le court chemin (Guard X-108)
- `06_business_layer.md` : Fermer les moteurs (Bank, Trading, Ecom)
- `07_stabilization_layer.md` : Fermer la mémoire (LTCU, historiques)
- `08_security_layer.md` : Fermer la protection (Fidélité sous perturbation)
- `09_audit_layer.md` : Fermer la preuve (Tickets, traces, attestations)
- `10_layer_fusion.md` : Fermer l'intégration
- `11_test_matrix.md` : Fermer la validation (Checklists REAL)

### B. Le code Backend Python (`obsidia/core/`)
Le moteur canonique (déjà partiellement fourni dans `obsidia_engine_v1_0_0-1.zip`) doit être étendu :
- `obsidia/core/kernel/` : Implémentation du contrat BSD
- `obsidia/core/registry/` : Types et objets canoniques
- `obsidia/core/latent/` : Implémentation des équations de Guard X-108
- `obsidia/core/security/` : Module de calcul de fidélité

### C. L'intégration React/TypeScript OS4 (`obsidia/layers/`)
Les fichiers partiellement fournis dans `os4_x108_fusion_merge_bundle_v1.zip` doivent être finalisés :
- `client/src/pages/Decision.tsx` : Doit devenir la page du verdict canonique multi-domaines
- `client/src/pages/Simuler.tsx` : Remplacer le guard local par l'autorité finale backend
- `server/engines/ecomEngine.ts` : Produire le `market_verdict` normalisé
- `server/canonical/bridge.ts` : Finaliser le pont API vers le backend Python

---

## Conclusion Opérationnelle
Pour **builder la suite**, tu dois :
1. Extraire le backend Python canonique depuis `obsidia_engine_v1_0_0-1.zip`.
2. Extraire l'interface OS4 depuis `os4_x108_fusion_merge_bundle_v1.zip`.
3. Rédiger les 12 fichiers de specs dans `obsidia/specs/` en copiant/collant les formules mathématiques issues des e-mails du 13, 14 et 28 mars.
4. Appliquer les correctifs listés dans `NOT_YET_PROVEN_AND_NEXT_STEPS_OS4.md` (ZIP runtime validation) pour passer les modules Bank, Trading et Preuves en statut REAL.