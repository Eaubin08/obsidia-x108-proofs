# CONTEXT OS ARCHITECTURE CONTRACT

```
status:            PROPOSED_CONTRACT
canonical_after:   CONTEXT_OS_ARCHITECTURE_ACCEPTED
palier:            T0.3-B
document_id:       F02
version:           1.0.0
produced_by:       T0_3_B_EXEC_20260718
```

---

## 1. PÉRIMÈTRE ET STATUT

Ce document est PROPOSED_CONTRACT. Il ne devient canonique qu'après la gate CONTEXT_OS_ARCHITECTURE_ACCEPTED, résultant de la décision humaine ACCEPTER_T0_3_B.

Ce document décrit les contrats de séparation des responsabilités au sein du Context OS d'Obsidia X-108. Il ne produit pas de runtime, ne résout pas CS-01 ou CS-02, ne modifie pas le dépôt source.

---

## 2. FRONTIÈRE GATEWAY

Le Gateway est la frontière entre le Terminal (ou tout client externe) et les composants internes du Context OS.

### 2.1 Responsabilités du Gateway

```
gateway_responsibilities:
  - frontiere_de_transport
  - application_des_permissions
  - limitation_exposition_capacites
  - controle_references_credentials
  - journalisation
```

Le Gateway applique les permissions (vérifie que le demandeur a le droit d'effectuer la requête), expose uniquement les capacités déclarées dans le contrat de capacité, gère uniquement des `credential_ref` (jamais de valeur littérale de secret), journalise toutes les transactions avec un identifiant de traçabilité.

### 2.2 Ce que le Gateway ne fait PAS

```
gateway_forbidden:
  - assemblage_unified_ir
  - routage_semantique
  - verdict_souverain
  - production_ACT
  - production_HOLD
  - production_BLOCK
  - elevation_autorite
  - modification_politique
  - promotion_memoire
```

### 2.3 Séparation Gateway / Router / MCP / Kernel

```
ROUTER:
  role:    selection_de_route_uniquement
  verdict: aucun

GATEWAY:
  role:    transport_permissions_capacites_credentials_journalisation
  verdict: aucun

MCP:
  role:    exposition_capacites
  verdict: aucun

KERNEL_X108:
  role:    verdict_souverain_uniquement
  verdict: ACT | HOLD | BLOCK
  note:    seul composant pouvant produire ACT
```

---

## 3. MODÈLE DE CONFIANCE ET D'INJECTION DE CONTEXTE

### 3.1 Principe général

Toute source de données externe reçoit par défaut :

```
content_role:           DATA_ONLY
instruction_capability: false
```

### 3.2 Sources TRUSTED_POLICY_SOURCE

Même une source classée `TRUSTED_POLICY_SOURCE` reste une source de données jusqu'à validation par un registre de politiques actives.

Une source ne peut jamais, par son seul contenu :
- devenir une instruction système
- modifier directement une politique active
- créer ou élever une autorité
- changer le mode opérationnel
- accorder une permission
- autoriser une mutation
- contourner le Router ou le Gateway
- contourner le Kernel X-108

### 3.3 Conditions pour qu'une politique influence l'évaluation

Une politique ne peut influencer l'évaluation que si elle possède tous les champs suivants, vérifiés dans le registre de politiques actives :

```
policy_id:           requis
policy_version:      requis
policy_hash:         requis
authority_ref:       requis
scope:               requis
valid_from:          requis
valid_until:         requis
activation_status:   ACTIVE
verification_status: VERIFIED
```

### 3.4 Règle d'injection

Une instruction incluse dans un document, une page web, Graphiti, un fichier, une sortie d'outil ou un message reste `DATA_ONLY` sauf contrat d'autorité séparé et humainement accepté.

### 3.5 Six classifications de source

```
TRUSTED_POLICY_SOURCE:    Source de politique vérifiée — DATA_ONLY jusqu'a validation registre
TRUSTED_EVIDENCE_SOURCE:  Source de preuve vérifiée — peut contribuer a EVIDENCE
UNTRUSTED_DATA_SOURCE:    Données non vérifiées — DATA_ONLY strict
TAINTED_SOURCE:           Source contaminée — traitement restreint
REDACTED_SOURCE:          Source dont le contenu a ete redacte
BLOCKED_SOURCE:           Source bloquee — aucun contenu autorise
```

### 3.6 Interdictions absolues hors TRUSTED_POLICY_SOURCE (+ validation registre)

```
FORBIDDEN_EFFECTS:
  - modifier_politique
  - creer_ou_elever_autorite
  - changer_mode
  - accorder_permission
  - produire_instruction_systeme
  - autoriser_mutation
  - contourner_kernel
```

---

## 4. POLITIQUE DE SÉCURITÉ ET DE REDACTION

### 4.1 Principe général

Aucun secret en clair dans un Context Object. Les secrets sont remplacés par `credential_ref` ou `capability_broker_ref`.

### 4.2 Redaction par niveau de sensibilité

```
HUMAN_REVIEWER_UNAUTHORIZED:
  sensitivity: CRITICAL
  resultat:    REDACTED

HUMAN_REVIEWER_AUTHORIZED:
  sensitivity: CRITICAL
  resultat:    ALLOWED_MINIMAL_VIEW
  conditions_obligatoires:
    - authority_ref:     valide
    - purpose:           declare
    - need_to_know:      verifie
    - mission_scope:     precise
    - operation_scope:   precise
    - time_scope:        borne
    - audit_requirement: satisfait
```

Même autorisé, l'humain ne reçoit pas automatiquement le Context Graph complet.

### 4.3 Scanner de secrets — approche value-aware

Le scanner distingue les noms de champs doctrinaux des valeurs sensibles.

Noms de champs ne déclenchant PAS d'alerte : `token`, `password`, `private_key`, `api_key`, `credential`, `secret`

Patterns déclencheurs (valeurs, non noms) :
- valeurs après clé à risque (`"password": "..."`)
- chaînes haute entropie ≥ 40 caractères base64/hex
- blocs clé privée (`-----BEGIN ... KEY-----`)
- URI avec userinfo (`scheme://user:pass@host`)
- affectations hors contrat (`TOKEN = "..."`)

Champs explicitement sûrs : `credential_ref`, `capability_broker_ref`, `token_forbidden`, `password_field_forbidden`, `credential_field_policy`, `secret_scanning_categories`

En cas de détection : ne pas afficher la valeur, enregistrer fichier + emplacement + catégorie + hash_redacted.

Résultat : `POTENTIAL_SECRET_DETECTED` → fail-closed

Résultat en l'absence de détection : `NO_SECRET_PATTERN_DETECTED_IN_SCANNED_ARTIFACTS`

---

## 5. FRONTIÈRE D'AUTORITÉ

### 5.1 Niveaux d'autorité

```
AUTHORITY_CLAIMED:
  definition: Revendication observee. Aucune preuve d'application.

AUTHORITY_CONTRACTUALLY_ASSIGNED:
  definition: Role attribue par contrat architectural humainement accepte.
  note:       T0.3-B produit ce niveau uniquement.
  limite:     Ne prouve pas l'application runtime.

AUTHORITY_RUNTIME_PROVEN:
  definition: Comportement démontre par preuve formelle ou test runtime.
  exigences:
    - preuve_runtime liee a implementation_hash exact
    ou
    - preuve_formelle avec proof_to_runtime_binding verifiable
  note:       T0.3-B ne produit pas ce niveau.
  attention:  Une preuve portant sur un modele abstrait seul ne prouve
              pas l'application runtime.
```

### 5.2 Kernel X-108

```
kernel_sovereignty_contract:           AUTHORITY_CONTRACTUALLY_ASSIGNED
kernel_runtime_enforcement_evidence:   non_produit_en_T0_3_B
kernel_sole_producer_of:               ACT | HOLD | BLOCK
```

---

## 6. FRONTIÈRE MÉMOIRE

```
promotion_vers_memoire:
  palier_requis:             T10
  decision_humaine:          requise
  auto_promote:              false

context_receipt_vers_memoire:  non_automatique
context_fact_vers_memoire:     non_automatique
context_candidate_vers_memoire: non_automatique
graphiti_vers_memoire:         non_automatique
```

---

## 7. RÉFÉRENCE AUX COMPOSANTS T0.3-A

```
CX01  (normalize_unified_input) — AB03_NOT_PROVEN — candidat Assembler
CX11  (infrastructure_graphiti) — AB05_NOT_PROVEN — candidat Graphiti Reader
CX17  (budget/selection)        — EXISTING_REUSABLE
CX22  (aggregateurs)            — EXISTING_REUSABLE
CX03  (context_filtering)       — EXISTING_ADAPTABLE
CS-01 (provenance_gate.py)      — QUARANTINED_PENDING_HUMAN_DECISION
```

---

## 8. NON-PÉRIMÈTRE DE CE DOCUMENT

```
OUT_OF_SCOPE:
  - implementation_runtime
  - modification_depot_source
  - resolution_CS-01_CS-02
  - verdict_souverain
  - promotion_memoire_automatique
  - declaration_CONTEXT_OS_ARCHITECTURE_ACCEPTED
```
