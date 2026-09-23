# HIGH_PERIPHERY_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/cognitive_trees/shazam_cognitif.py`
- `periphery/bdf/double_brain_router.py`
- `periphery/hexaflux/ltcu_plus.py`
- `periphery/hexaflux/transition_mapper.py`
- `periphery/mcp_bridge.py`
- `periphery/jarvis_projection.py`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/05_SHAZAM_COGNITIF/`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/06_REVERSE_OS_SSR_JARVIS/`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/07_BDF_DOUBLE_CERVEAU/`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/08_HEXAFLUX_LTCU_MUTATIONS/`
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/09_MCP_BRIDGE_OBSIDIA_IR/`

Imported Facts:
- ShazamCognitif : `can_decide=False`, `can_emit_act=False` — patterns cognitifs LANGUAGE/CAUSAL/RISK/AUTHORITY/EPISTEMIC/GOVERNANCE
- DoubleBrainRouter (BDF) : `emits_act=False`, `emits_verdict=False` — route System1 vs System2
- LTCUPlusSignal (HexaFlux) : `advisory_only=True`, `authorizes=False` — drift contextuel longue durée
- MCP Bridge : `non_decision=True`, `policy_scope="READONLY_CONTEXT"` — conversion requête → structure Obsidia
- jarvis_projection.py : stub 3 lignes — PLACEHOLDER — pas d'implémentation réelle

What This Source Proves:
- Tous ces systèmes ont `can_emit_act=False` ou équivalent codé en dur
- Ces systèmes sont des signaux contextuels, jamais décisionnels
- Jarvis = stub — pas implémenté

What This Source Does NOT Prove:
- Que ces systèmes fonctionnent en production
- Que Jarvis / Reverse OS SSR sont implémentés

Boundary:
- ADVISORY_ONLY — NON_SOVEREIGN — signal contextuel uniquement

Claim-Scope:
- "Shazam/BDF/HexaFlux/MCP produisent des signaux contextuels pour X108" — AUTORISÉ
- "Ces systèmes décident ou agissent" — INTERDIT

Specs Depending On This Source:
- 06_HIGH_PERIPHERY_SYSTEMS/SHAZAM_COGNITIF_BOUNDARY_SPEC.md
- 06_HIGH_PERIPHERY_SYSTEMS/BDF_DOUBLE_BRAIN_NON_SOVEREIGN_SPEC.md
- 06_HIGH_PERIPHERY_SYSTEMS/HEXAFLOW_LTCU_MUTATION_SPEC.md
- 06_HIGH_PERIPHERY_SYSTEMS/MCP_BRIDGE_TO_IR_ADMISSION_SPEC.md

Runtime Status: RUNTIME_CODE (sauf Jarvis = PLACEHOLDER)

Do Not Move Original Source: true
Authority: KX108_ONLY
