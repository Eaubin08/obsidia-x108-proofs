# TREE34_NON_DECISION_CONTRACT_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/04_ARBRES_34_TENSOR_MATRIX/ARBRE_*/non_decision_contract.md`

Source Status: DOC_ONLY (contrats présents dans chaque arbre)

Scope: Verrouiller le contrat de non-décision pour les 34 arbres cognitifs.

Allowed:
- "Tree34 produit des signaux d'activation [0,1] — contexte uniquement"
- "Le non_decision_contract est présent dans chaque arbre : Tree34 ↛ ACT"

Forbidden:
- "Un arbre cognitif prend une décision"
- "Tree34 émet ALLOW/HOLD/BLOCK"
- "T30-T34 constituent un moteur AGI décisionnel"

Inputs: Données d'activation (vecteur 34 dimensions)
Outputs: Signal contextuel [0,1] par arbre — contexte X108

Metrics:
- Activation par arbre : valeur normalisée ∈ [0,1]
- Seuil dominant : θ = 0.15 (par défaut)

Invariants:
- Tree34 ↛ ACT (inscrit dans non_decision_contract.md de chaque arbre)
- Toute décision finale appartient à X-108
- 7 flux exacts = HORS périmètre public (docs/REPO_BOUNDARY.md:84)

X108 Boundary: KX108_ONLY — Tree34 fournit contexte
Tests Required: test_no_act_from_tree34
Proof Expected: Python test (vérifier non_decision_contract)
Runtime Status: DOC_ONLY + RUNTIME_CODE partiel
Claim-Scope Notes: "Tree34 ≠ moteur AGI décisionnel" — signaux contextuels uniquement.
Open Questions: 7 flux exacts — à inclure dans périmètre public ? (HORS selon REPO_BOUNDARY.md)
