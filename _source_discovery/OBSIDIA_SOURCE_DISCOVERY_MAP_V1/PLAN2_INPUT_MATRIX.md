# PLAN2_INPUT_MATRIX
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1
# Date: 2026-06-02

> Entrées de préparation pour le Plan 2 (spec writing).
> Ne crée aucune spec. Liste seulement ce dont chaque spec future a besoin.

---

## Règle absolue Plan 2

```
Source réelle → Spec → Runtime → Claim
X-108 avant ACT
```

Aucune spec ne peut être créée si la source n'est pas confirmée dans cette table.

---

## P0 — Bloquant avant toute spec

| Spec future | Sources exactes à citer | Statut source | Interdictions | Tests futurs | Proof attendu | Claim-scope |
|-------------|------------------------|---------------|---------------|--------------|---------------|-------------|
| `ACTION_LIFECYCLE_SPEC_V1.md` | `periphery/action_lifecycle.py` (lignes 8-31) | RUNTIME_CODE | Ne pas ajouter d'états sans décision humaine ; FEEDBACK_CAPTURED est le 9e état — décider si public | `tests/sigma/test_f61_sigma_dispatcher_readonly_evaluate.py` | Python test uniquement | Cycle privé → inclure FEEDBACK_CAPTURED dans périmètre public seulement si décision explicite |
| `X108_GATE_DECISION_AUTHORITY_SPEC_V1.md` | `periphery/os3_ticket.py`, `periphery/export_for_x108.py`, `periphery/action_lifecycle.py:12` | RUNTIME_CODE + KX108_BOUNDARY | JAMAIS attribuer ACT à un agent périphérique — seul KX108 décide | Tests de non-souveraineté existants (`tests/sigma/`) | Lean proof kernel KX108 (périmètre `proofs/lean/`) | ALLOW / HOLD / BLOCK = seuls verdicts — jamais de "verdict implicite" |
| `OS3_PROOF_TICKET_SPEC_V1.md` | `periphery/os3_ticket.py` (entièreté) | RUNTIME_CODE | Ne pas modifier le schéma de hash sans mise à jour du protocole Merkle | Tests de replay (`replay_status` champ) | Hash sha256 chain — pas de preuve Lean pour ce fichier | merkle_root doit couvrir input+output+trace — vérifier cohérence avec `proofs/` |
| `F76_PROD_READINESS_REMEDIATION_SPEC.md` | `docs/architecture/F74_F77_FINALIZATION_AUDIT.md:193-250`, `apps/obsidia_api/main.py` | PROD_BLOCKED | Ne pas utiliser `allow_origins=["*"]` en prod ; ne pas activer sans auth | Test de CORS restreint, test /health, test auth token | Aucun proof formel requis — audit suffisant | "production-ready" interdit tant que 4 bloqueurs non résolus |
| Clarification Jcoin | — | ABSENT_UNDER_THIS_NAME | Ne pas créer de spec Jcoin sans décision humaine | — | — | Si Jcoin ≠ Gencoin, risque claim-scope majeur |
| Décision 7 flux | `docs/REPO_BOUNDARY.md:84` | HORS_PERIMETRE_PUBLIC | Ne pas inclure "7 flux complets" dans périmètre public sans validation explicite | — | — | docs/REPO_BOUNDARY.md dit explicitement HORS périmètre |

---

## P1 — Nécessaire avant Plan 2

| Spec future | Sources exactes à citer | Statut source | Interdictions | Tests futurs | Proof attendu | Claim-scope |
|-------------|------------------------|---------------|---------------|--------------|---------------|-------------|
| `GOVERNED_STATE_ENTROPY_SPEC_V1.md` | `periphery/math_core/governed_state.py`, `periphery/energy_thermo.py` | PYTHON_SPEC | Ne pas clamer "Lean-proven" — Python spec uniquement | Tests unitaires Python | FORMAL_PROOF_PENDING — si spec formelle souhaitée, Lean requis | thermo_debt, delta_E, delta_C sont des approximations Python, pas des invariants prouvés |
| `LYAPUNOV_STABILITY_SPEC_V1.md` | `periphery/math_core/lyapunov.py`, `periphery/math_core/governance_partition.py` | PYTHON_SPEC | Ne pas clamer stabilité Lyapunov = preuve formelle | Tests d'invariants Python | FORMAL_PROOF_PENDING | "runtime approximation" doit être explicite dans la spec |
| `PROOF_OF_GOVERNANCE_SPEC_V1.md` | `periphery/math_core/proof_of_governance.py` | PYTHON_SPEC | Même interdiction que Lyapunov | Tests Python | FORMAL_PROOF_PENDING | PoG = validation Python, pas Lean |
| `GENCOIN_LEDGER_CANDIDATE_SPEC_V1.md` | `periphery/gencoin.py`, `periphery/gencoin_ledger.py`, `periphery/gencoin_debt_model.py`, `docs/gencoin/GENCOIN_FORMAL_MATH_SPEC_V0_2.md`, `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md` | RUNTIME_CODE + CANDIDATE | JAMAIS minter, déployer, créer token réel ; `mint_allowed=False` si x108_gate != ALLOW | Tests de token policy (`periphery/blockchain/token_policy.py`) | Hash OS3 ticket requis avant toute émission | "candidate" = valeur calculée post-preuve, jamais on-chain |
| `BALANCE_BUV_MASTER_SPEC_V1.md` | `periphery/gencoin_sandbox/balance_operator.py`, `docs/gencoin/sandbox_pre_freeze/BALANCE_CANON.md`, `docs/gencoin/sandbox_pre_freeze/LIMITS_AND_STATUS.md` | RUNTIME_CODE + DOC_ONLY | Sandbox uniquement — ne pas exposer balance_operator en production sans gate | Tests balance dans sandbox | Python test uniquement | "Balance Obsidienne" ≠ décision finale — résultat d'une évaluation multi-facteur |
| `GPS_AVIATION_CONNECTOR_SPEC_V1.md` | `periphery/adapters/gps_adapter.py`, `connectors/aviation_robo.py`, `sigma/domains/gps_defense_aviation_agents.py`, `docs/periphery/GPS_ADAPTER_MAPPING_V0.md`, `docs/architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md` | RUNTIME_CODE + DRY_RUN | Ne pas déployer aviation connector en défense réelle sans validation externe ; POST local uniquement | `tests/api/test_f72_os_trad_ir_reverse_pipeline_audit.py` | Audit externe requis pour toute utilisation défense | GPS strategic surface ≠ défense production |
| `BRODY_MEMORY_READONLY_SPEC_V1.md` | `periphery/brody/brody_runtime_readonly.py`, `sigma/graphiti_readonly_bridge.py`, `docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md`, `docs/freeze/BRODY_TREE_POLICY_BINDING_REPORT.md` | RUNTIME_CODE + READONLY | Brody ne décide jamais — graphiti_write et neo4j_write nécessitent gate humain | `tests/api/test_brody_chat_readonly.py`, `test_brody_f7b_operator_view_packet.py` | Preuve de non-souveraineté dans tests existants | "Brody non souverain ≠ Brody inutile" — signal contextuel précieux |
| `F77_EXTERNAL_PACK_COMPLETION_SPEC.md` | `docs/architecture/F74_F77_FINALIZATION_AUDIT.md:253-282` | PACK_PARTIAL | Ne pas créer external_pack/ avec claims > ce que le repo prouve | Tests de reproducibilité fresh clone | Aucun proof formel requis | "external pack partiel" ≠ "prêt pour diffusion" |

---

## P2 — Utile mais non bloquant

| Spec future | Sources exactes à citer | Statut source | Notes |
|-------------|------------------------|---------------|-------|
| `SHAZAM_COGNITIF_CONTEXT_SPEC_V1.md` | `periphery/cognitive_trees/shazam_cognitif.py` | RUNTIME_CODE + ADVISORY_ONLY | `can_decide=False`, `can_emit_act=False` |
| `BDF_DOUBLE_BRAIN_ROUTER_SPEC_V1.md` | `periphery/bdf/double_brain_router.py`, `periphery/bdf/llm_diffusion_mix.py` | RUNTIME_CODE + ADVISORY_ONLY | `emits_act=False` |
| `HEXAFLUX_LTCU_SPEC_V1.md` | `periphery/hexaflux/ltcu_plus.py`, `periphery/hexaflux/transition_mapper.py` | RUNTIME_CODE + ADVISORY_ONLY | `advisory_only=True` |
| `MCP_BRIDGE_POLICY_SPEC_V1.md` | `periphery/mcp_bridge.py` | RUNTIME_CODE + ADVISORY_ONLY | `non_decision=True`, `policy_scope=READONLY_CONTEXT` |
| BRANCHESXYZKLN / .xyz | `periphery/OBSIDIA_V4_STRUCTURED_FULL/12_EXTENSIONS_R_D/BRANCHESXYZKLN.md` | DOC_ONLY | Lire contenu avant de décider si spec nécessaire |

---

## P3 — Annexe

| Spec future | Sources | Notes |
|-------------|---------|-------|
| `REVERSE_OS_SSR_JARVIS_SPEC_V1.md` | `periphery/jarvis_projection.py` (stub 3 lignes), `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/06_REVERSE_OS_SSR_JARVIS/` | Placeholder — implémentation à créer d'abord |
| `obsidia_interlayer_constitution.md` | `docs/civilization/AGENTIC_CONSTITUTIONAL_CIVILIZATION_STACK_V1.md` | Couche agentic-constitutional existe déjà |
