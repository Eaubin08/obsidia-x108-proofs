# SOURCE_STATUS_MATRIX

> Statut de chaque source principale. Référence pour tous les claims.

| Source | Chemin | Statut | Claim autorisé | Claim interdit |
|--------|--------|--------|----------------|----------------|
| PROOF_SCOPE.md | `docs/PROOF_SCOPE.md` | SOURCE_CANON | "4 catégories de preuves définies" | Modifier sans protocole |
| Action lifecycle | `periphery/action_lifecycle.py` | RUNTIME_CODE | "10 états cycle action Python" | "Formellement prouvé" |
| OS3ProofTicket | `periphery/os3_ticket.py` | RUNTIME_CODE | "Ticket sha256 chain" | "RFC3161 prod / replay opérationnel" |
| Lyapunov | `periphery/math_core/lyapunov.py` | PYTHON_SPEC | "Scoring Python stabilité" | "Lean proof Lyapunov" |
| ProofOfGovernance | `periphery/math_core/proof_of_governance.py` | PYTHON_SPEC | "Vérification Python gouvernance" | "Preuve formelle PoG" |
| governed_state | `periphery/math_core/governed_state.py` | PYTHON_SPEC | "Métriques état gouverné Python" | "Stabilité formellement prouvée" |
| Gencoin | `periphery/gencoin.py` + policy | RUNTIME_CODE + CANDIDATE | "Ledger valeur candidate" | "Token réel / Jcoin / blockchain" |
| Balance | `periphery/gencoin_sandbox/balance_operator.py` | RUNTIME_CODE (sandbox) | "Score balance sandbox" | "Balance décide / BUV = token" |
| GPS adapter | `periphery/adapters/gps_adapter.py` | RUNTIME_CODE + DRY_RUN | "Scores GPS Python local" | "Défense production / aviation réelle" |
| aviation_robo | `connectors/aviation_robo.py` | RUNTIME_CODE + DRY_RUN | "POST local DRY_RUN" | "Actuateur réel / défense prod" |
| Shazam Cognitif | `periphery/cognitive_trees/shazam_cognitif.py` | RUNTIME_CODE + ADVISORY_ONLY | "Patterns cognitifs contextuels" | "Shazam décide / émet ACT" |
| BDF | `periphery/bdf/double_brain_router.py` | RUNTIME_CODE + ADVISORY_ONLY | "Route System1/System2" | "BDF décide / émet verdict" |
| HexaFlux/LTCU | `periphery/hexaflux/ltcu_plus.py` | RUNTIME_CODE + ADVISORY_ONLY | "Drift contextuel advisory" | "LTCU autorise / HexaFlux décide" |
| Jarvis | `periphery/jarvis_projection.py` | PLACEHOLDER | "Stub présent — non implémenté" | "Jarvis implémenté" |
| Tree34 | `04_ARBRES_34_TENSOR_MATRIX/` | DOC_ONLY + RUNTIME_CODE partiel | "34 arbres signal contextuel" | "Tree34 moteur AGI décisionnel" |
| Agents 52 | `agents_52.registry.json` | SOURCE_CANON | "52 agents registrés" | "Agents décident" |
| Brody | `periphery/brody/brody_runtime_readonly.py` | RUNTIME_CODE + READONLY | "Brody readonly advisory" | "Brody décide / écrit mémoire" |
| Graphiti | `sigma/graphiti_readonly_bridge.py` | RUNTIME_CODE + READONLY | "Graphiti readonly" | "Graphiti write sans gate" |
| F74 Fresh Clone | `F74_F77_FINALIZATION_AUDIT.md` | COMPLETE | "F74 reproductible" | "Production-ready" |
| F76 Cloud/Prod | `F74_F77_FINALIZATION_AUDIT.md` | PROD_BLOCKED | "F76 = 4 bloqueurs documentés" | "Production-ready" |
| F77 Pack Externe | `F74_F77_FINALIZATION_AUDIT.md` | PACK_PARTIAL | "F77 = 9 fichiers manquants" | "Pack prêt pour diffusion" |
| NPL | _source_discovery/ + récepteurs | SPEC_CANDIDATE | "NPL = signaux contextuels narratifs readonly" | "NPL diagnostique / décide / prouve provenance" |
| Jcoin | ABSENT | ABSENT_UNDER_THIS_NAME | Décision humaine requise | "Jcoin existe dans le repo" |
| 7 flux exacts | `docs/REPO_BOUNDARY.md:84` | HORS_PERIMETRE_PUBLIC | "T31 = Arbre des Flux" | "7 flux exacts dans périmètre public" |
| .xyz / XYZ pipeline | `BRANCHESXYZKLN.md` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | "BRANCHESXYZKLN.md dans 12_EXTENSIONS_R_D/" | "Pipeline .xyz implémenté" |
