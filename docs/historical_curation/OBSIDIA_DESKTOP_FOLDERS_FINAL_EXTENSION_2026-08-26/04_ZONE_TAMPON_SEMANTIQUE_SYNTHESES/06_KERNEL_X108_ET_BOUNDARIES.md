# KERNEL X-108 ET BOUNDARIES — ÉTAT DOCUMENTAIRE
**Date** : 2026-06-20  
**Source** : OBSIDIA_IDENTITY.md + MODULE_MAP.md + PROTECTED_SCOPE.md + SUPPORT_COMPLET

---

## Identité du Kernel X-108

**CONFIRMED_BY_DOCUMENTS** — Obsidia X-108 est défini comme :

> *"The ex-ante governance kernel — decides whether an action is allowed before it happens"*

Le kernel décide **avant** l'action, pas après. Governance ex-ante.

---

## Sémantique BLOCK > HOLD > ALLOW — FREEZE_CONFIRMED

| Priorité | Valeur | Signification |
|---|---|---|
| 1 (plus haute) | BLOCK | Interdit — ne jamais passer |
| 2 | HOLD | En attente — décision différée |
| 3 (plus basse) | ALLOW | Autorisé |

**Invariant fondamental** : `BLOCK > HOLD > ALLOW` — cet ordre ne doit jamais être inversé.  
**Formalisé dans** : proofs/lean/ (Lean 4) + formal/tla/ + proofs/tla/ (TLA+)

---

## KX108_ONLY — CONFIRMED_BY_DOCUMENTS

`decision_authority=KX108_ONLY` est présent dans **toutes les surfaces** :
- Core, V1, Enriched, Probe
- Bank, Trading, GPS
- UI, Kernel, Tests, Preflight, Graphiti

Signification : seul le kernel X-108 détient l'autorité de décision. Aucun autre composant (Brody, Graphiti, domaines) ne peut décider.

---

## No ACT — CONFIRMED_BY_DOCUMENTS

`KX108_ONLY. No ACT. No write. No execution. readonly=True.`

Brody et les surfaces ne peuvent pas effectuer d'ACT (action) de manière autonome. Toute action doit passer par le kernel.

---

## Proof Stack — FREEZE_CONFIRMED

| Composant | Emplacement | Statut |
|---|---|---|
| Lean 4 proofs | `proofs/lean/Obsidia*.lean`, `lakefile.lean` | FREEZE_CONFIRMED / PROTECTED |
| TLA+ reference | `proofs/tla/X108.tla`, `X108_MC.tla`, `DistributedX108.tla` | FREEZE_CONFIRMED / PROTECTED |
| TLA+ CI | `formal/tla/` | FREEZE_CONFIRMED / PROTECTED |
| Merkle root | `proofs/merkle_root.json` + racine | DO_NOT_TOUCH |
| Merkle seal | `proofs/merkle_seal.json` + racine | DO_NOT_TOUCH |
| RFC3161 anchor | `proofs/rfc3161_anchor.json` | DO_NOT_TOUCH |
| PROOFKIT_REPORT.json | `proofs/` | AUDIT_CONFIRMED (all PASS, 2026-05-21) |
| V18_3_1 bundle | `proofs/V18_3_1/` | FREEZE_CONFIRMED |
| V18_7 bundle | `proofs/V18_7/` | FREEZE_CONFIRMED |
| V18_8 bundle | `proofs/V18_8/` | FREEZE_CONFIRMED |

---

## server.kernel.sealed.cjs — DO_NOT_TOUCH

Bridge Node.js scellé et tamper-evident. Toute modification silencieuse invalide l'intégrité.

---

## Frontières documentées

### Ce qui est dans le périmètre kernel
- Lean 4 théorèmes et invariants
- TLA+ specs (reference + CI)
- Merkle + seal + RFC3161 (cryptographique)
- BLOCK/HOLD/ALLOW semantics
- PROOFKIT_REPORT
- V18 bundles

### Ce qui est HORS du kernel (ne pas mélanger)

| Composant | Raison |
|---|---|
| Brody | Interface seulement — DO_NOT_CONNECT_TO_KERNEL directement |
| Graphiti V20 | Mémoire sidecar readonly — DO_NOT_CONNECT_TO_KERNEL |
| Cockpit / Dashboard | Couche supervision — DO_NOT_MERGE avec kernel |
| Domaines (bank/trading/GPS) | Couche Surface — communiquent via Sigma |
| CIC modules | Nouveaux composants — statut à statuer |
| Brody Education adapter | LOCAL ONLY — statut à statuer |
| Frontier Ledger | LOCAL ONLY — statut à statuer |

---

## Ce qui est CLAIR selon documents

1. **Autorité** : X-108 seul décide.
2. **Preuve** : Lean 4 + TLA+ + Merkle + RFC3161.
3. **Ordre** : BLOCK > HOLD > ALLOW — invariant permanent.
4. **Frontière** : Brody interface, ne substitue pas le kernel.
5. **Mémoire** : Graphiti readonly — aucune écriture depuis Brody.
6. **Immutabilité** : Toute modification d'un fichier ancré invalide les preuves.
7. **Couches** : KERNEL > SIGMA > SURFACES > DOCS > TOOLING > AGENTIC.

---

## Ce qui reste à FORMALISER

| Point | Statut |
|---|---|
| Seuils par domaine (bank threshold, trading G1, GPS) | NEEDS_FORMALIZATION |
| Machine-checking TLA+ en CI automatique | NEEDS_IMPLEMENTATION |
| Runtime ACT réel avec preuve de chemin | NEEDS_IMPLEMENTATION |
| Formalisation des domaines en Lean (bank, trading, GPS) | NEEDS_FORMALIZATION |
| Vue régulateur (audit trail lisible) | NEEDS_IMPLEMENTATION |
| Tests adversariaux formels | NEEDS_IMPLEMENTATION |
| Lean 57 reconciliation : statut définitif | NEEDS_USER_DECISION |

---

## Pépites kernel confirmées (FORMALISE / ANCREE)

| Pépite | Titre | Statut |
|---|---|---|
| P34 | Kernel = intersection des contraintes | FORMALISE |
| P35 | Preuve formelle sans sorry | FORMALISE |
| P39 | Invariant permanent | FORMALISE |
| P40 | Axiome non dérivable | FORMALISE |
| P41 | Déterminisme D1 | ANCREE |
| P42 | Seuil G1 : ACT si theta <= S | FORMALISE |
| P43 | Pas de BLOCK natif L11.3 | ANCREE |
| P44 | Verrou temporel X-108 | FORMALISE |
| P45 | Skew négatif vers HOLD | FORMALISE |
| P46 | Consensus fail-closed 4 agents | FORMALISE |
| P85 | Loi de réciprocité | FORMALISE |
| P86 | Consensus supermajorité 3/4 | ANCREE |
| P87 | Fail-closed sans supermajorité | ANCREE |
| P88 | Non-contradiction | FORMALISE |
| P89 | Complétude | FORMALISE |
| P90 | Cohérence | FORMALISE |
| P91 | Décidabilité | FORMALISE |
