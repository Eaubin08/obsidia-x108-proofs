# OBSIDIA READING GUIDE
# Comment naviguer les specs Obsidia X-108

---

| Je veux comprendre... | Lire en premier |
|-----------------------|-----------------|
| X-108, autorité décisionnelle, KX108_ONLY | `01_X108_AUTHORITY/KX108_ONLY_AUTHORITY_SPEC.md` |
| Les limites de ce qu'on peut affirmer publiquement | `00_SCOPE_DISCIPLINE/CLAIM_SCOPE_DISCIPLINE_SPEC.md` |
| La différence preuve formelle vs Python spec | `00_SCOPE_DISCIPLINE/FORMAL_PROOF_VS_RUNTIME_APPROXIMATION.md` |
| La constitution intercouche (qui peut quoi) | `02_INTERLAYER_CONSTITUTION/WHO_CAN_READ_WRITE_DECIDE_ACT.md` |
| L'entropie, Lyapunov, ProofOfGovernance | `03_ENTROPY_DISCIPLINE/ENTROPY_DISCIPLINE_SPEC.md` |
| Les 34 arbres, le flux, AGI boundary | `04_AGI_TREE34_FLUX/TREE34_NON_DECISION_CONTRACT_SPEC.md` |
| Balance / BUV / géométries | `05_BALANCE_BUV_GEOMETRIES/BUV_MASTER_SPEC.md` |
| Shazam / BDF / HexaFlux / Reverse OS / MCP Bridge | `06_HIGH_PERIPHERY_SYSTEMS/SHAZAM_COGNITIF_BOUNDARY_SPEC.md` |
| Agents 52, connectors, MCP | `07_AGENTS_CONNECTORS_MCP/AGENT_PERIPHERAL_NON_SOVEREIGN_SPEC.md` |
| Brody, Graphiti, mémoire | `08_MEMORY_BRODY_GRAPHITI/BRODY_RESPONSE_AUTHORITY_SPEC.md` |
| GPS, aviation, mondes critiques | `09_CRITICAL_WORLDS/GPS_DEFENSE_AVIATION_BOUNDARY_SPEC.md` |
| Gencoin, Jcoin, valeur | `10_VALUE_GENCOIN_JCOIN/GENCOIN_CANDIDATE_VALUE_NOT_TOKEN_SPEC.md` |
| OS3 ticket, preuve, replay | `11_PROOF_REPLAY_OS3/OS3_PROOF_RUNTIME_SPEC.md` |
| NPL — Narrative Provenance Layer | `12_NARRATIVE_PROVENANCE_LAYER/NPL_CANONICAL_SPEC.md` |
| Toutes les sources réelles et leurs statuts | `_source_index/SOURCE_STATUS_MATRIX.md` |
| Quel runtime est prêt / bloqué | `_source_index/SOURCE_TO_RUNTIME_MAP.md` |
| Ce qu'on peut et ne peut pas dire | `_source_index/SOURCE_TO_CLAIM_SCOPE_MAP.md` |

---

## Principe de lecture

```
Source réelle (code/doc existant)
    ↓
_imports_readonly/ (facts extraits, chemins cités)
    ↓
specs/ (contrat d'usage, limites, autorité)
    ↓
Test futur (à créer en Plan 3)
    ↓
Runtime futur (à implémenter en Plan 3+)
    ↓
Claim public (autorisé seulement si sourcé)
```

**En cas de doute sur ce qu'on peut affirmer** → `00_SCOPE_DISCIPLINE/`
**En cas de doute sur qui décide** → `01_X108_AUTHORITY/KX108_ONLY_AUTHORITY_SPEC.md`
