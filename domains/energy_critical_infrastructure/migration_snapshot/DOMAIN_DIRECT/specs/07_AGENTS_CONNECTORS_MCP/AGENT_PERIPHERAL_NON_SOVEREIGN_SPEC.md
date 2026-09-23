# AGENT_PERIPHERAL_NON_SOVEREIGN_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/10_AGENTS_52/agents_52.registry.json`
- `docs/status/PERIPHERY_PUBLIC_INDEX.md`
- `docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md`

Source Status: SOURCE_CANON

Scope:
Définir la non-souveraineté de tous les agents périphériques Obsidia.

Allowed:
- "Agents 52 = signal / context packet / artefact auditable"
- "Aucun des 52 agents n'émet ACT, ALLOW, HOLD, BLOCK"
- "MEMOIRE_PERSONNELLE_OBSIDIA = agent mémoire readonly"
- "DATA_SOVEREIGNTY_GUARD = garde de souveraineté des données"

Forbidden:
- "Un agent périphérique décide"
- "Un agent périphérique émet ALLOW/HOLD/BLOCK directement"
- "Un agent produit un verdict final"
- "LLM = autorité décisionnelle"

Inputs: Context packets + signals
Outputs: Signaux contextuels + artefacts auditables

Metrics: N/A

Invariants:
- 52 agents dans le registry — tous non-souverains
- AgentPeripheral ↛ ACT
- Decision = KX108_ONLY
- LLM = advisory only

X108 Boundary: KX108_ONLY — agents fournissent contexte

Tests Required:
- test_no_agent_emits_act
- test_agent_output_is_context_packet

Proof Expected: Python test (non-sovereignty tests existants)

Runtime Status: SOURCE_CANON (registry) + RUNTIME_CODE (implémentations partielles)

Claim-Scope Notes:
"Agents 52 = signal / context / audit — jamais décision."

Open Questions: Combien des 52 agents sont implémentés en runtime ?
