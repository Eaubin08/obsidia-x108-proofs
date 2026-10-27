# OBSIDIA_CORPUS_CADASTRE_V0 — GitHub F77 + Source Zips
## Totaux
| Corpus | Count | Statut |
|---|---:|---|
| GitHub officiel F77 | 4 506 | stabilisé / pushé |
| Local pré-freeze | 340 | non tracké / à trier |
| Source zips internes | 2 842 | archives sources avant déduplication |
| Total brut utile avant dédup | 7 688 | corpus connu Obsidia |

## GitHub officiel F77 — composition effective par groupe
> Répartition issue du full filesystem audit filtré local-only; total officiel git ls-files = 4 506.
| Groupe | Count approx | Composition |
|---|---:|---|
| `periphery` | 2617 | Périphéries runtime/cognition/mémoire/agents, plus gros corps officiel |
| `docs` | 777 | Docs runtime, architecture, release, audit, demo |
| `tests` | 264 | Tests API/Sigma/Brody/runtime/hardening |
| `proofs` | 185 | Preuves, modèles, artefacts proof/replay |
| `apps` | 153 | API runtime apps/obsidia_api |
| `scripts` | 147 | Scripts audit, test, freeze, hardening |
| `sigma` | 78 | Sigma registry/dispatcher/packets/connectors/domaines |
| `formal` | 35 | Cibles/proofs formels |
| `tools` | 32 | Outils terminal/runtime |
| `__ROOT__` | 32 | Fichiers racine repo |
| `.runtime_freezes` | 29 | Freeze manifests officiels |
| `audit` | 27 | Audit logs et fichiers auditables |
| `external_pack` | 11 | Pack review externe F77 |
| `demos` | 10 | Démo/smoke/demo scripts |
| `agents` | 9 | Agents classiques |
| `connectors` | 7 | Connecteurs |
| `qa` | 7 | QA |
| `_graphiti_readonly_indexes` | 7 | Index Graphiti readonly |
| `audit_logs` | 6 | Logs audit |
| `examples` | 6 | Exemples |
| `autres petits groupes` | 14 | .github, documentation, Demo, patches, etc. |

## Specs locales — 212 fichiers
| Sous-corpus | Count | Composition |
|---|---:|---|
| `00_SCOPE_DISCIPLINE` | 9 | claims, production blockers, dry-run, reproducibility |
| `01_X108_AUTHORITY` | 7 | KX108/X108, no bypass, temporal gate, decision ticket |
| `02_INTERLAYER_CONSTITUTION` | 8 | layer matrix, lifecycle, passage rules |
| `03_ENTROPY_DISCIPLINE` | 11 | semantic heat, thermodynamic debt, Lyapunov/P107/P161 |
| `04_AGI_TREE34_FLUX` | 5 | Tree34, AGI subordination, flux |
| `05_BALANCE_BUV_GEOMETRIES` | 9 | Balance, BUV, geometries |
| `06_HIGH_PERIPHERY_SYSTEMS` | 7 | BDF, Hexaflow, MCP bridge, MMonde, Reverse OS, Shazam |
| `07_AGENTS_CONNECTORS_MCP` | 10 | agents, tools, MCP, LLM advisory |
| `08_MEMORY_BRODY_GRAPHITI` | 7 | Brody/Graphiti/memory boundaries |
| `09_CRITICAL_WORLDS` | 14 | bank/trading/ecom/GPS/aviation |
| `10_VALUE_GENCOIN_JCOIN` | 11 | Gencoin/Jcoin/value emission |
| `11_PROOF_REPLAY_OS3` | 9 | OS3 proof, replay, attestation |
| `12_NARRATIVE_PROVENANCE_LAYER` | 34 | NPL, culture, récit, memory provenance |
| `external_signals` | 39 | Timeverse, temporal sidecar, consequence boundary |
| `_imports_readonly` | 17 | sources importées readonly |
| `_source_index` | 7 | source→spec/runtime/claim maps |
| `_invariant_graph` | 2 | formal target deltas |
| `root specs` | 6 | INDEX, registry, guide, plan reports |

## Runtime contracts — 43 fichiers
| Sous-corpus | Count | Composition |
|---|---:|---|
| `boundaries` | 13 | KX108 gateway, no ACT periphery, readonly, NPL/RSSI/RGPD guards |
| `contracts` | 7 | BoundaryContract, ContextPacket, DecisionTicket, IntentEnvelope, OS3EvidenceTicket, PeripheralSignalPacket, RuntimeAdmissionContract |
| `schemas` | 6 | JSON schemas for packets/contracts |
| `dry_run` | 4 | dry-run pipeline, no world action, X108 gateway dry-run |
| `external_signals_dry_run` | 10 | external signal adapter/pipeline/maps/reports/failure modes |
| `reports` | 6 | Plan3 P0/P1/P2 reports and next steps |
| `README` | 1 | index |

## Source zips internes — détail par pack

### ATLAS_CORPUS — 1738 fichiers
`OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS(5).zip`

| Groupe interne | Count |
|---|---:|
| `docs` | 1639 |
| `__ROOT__` | 30 |
| `periphery` | 28 |
| `.runtime_freezes` | 24 |
| `registry` | 7 |
| `.pytest_cache` | 5 |
| `tests` | 4 |
| `patches` | 1 |

Extensions: `.md`=1241, `.json`=453, `.py`=18, `.pyc`=15, `.txt`=7, `[none]`=3, `.tag`=1

### COGNITIVE_REINTEGRATION_CORPUS — 513 fichiers
`OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1)(5).zip`

| Groupe interne | Count |
|---|---:|
| `component_specs` | 458 |
| `family_specs` | 25 |
| `__ROOT__` | 15 |
| `schemas` | 8 |
| `packets` | 5 |
| `proof` | 1 |
| `tests` | 1 |

Extensions: `.yaml`=490, `.md`=12, `.json`=8, `.csv`=2, `.sha256`=1

### RSSI_RGPD_ISO_CORPUS — 280 fichiers
`OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2(4).zip`

| Groupe interne | Count |
|---|---:|
| `docs` | 129 |
| `rssi` | 15 |
| `.runtime_freezes` | 14 |
| `rgpd` | 14 |
| `iso27001` | 13 |
| `tests` | 12 |
| `periphery` | 11 |
| `ai_security` | 11 |
| `security` | 10 |
| `data_governance` | 10 |
| `audit` | 9 |
| `__ROOT__` | 8 |
| `registry` | 8 |
| `deployment` | 8 |
| `legal` | 8 |

Extensions: `.md`=229, `.json`=26, `.py`=23, `.txt`=2

### RSSI_SECURITY_PRESENTATION_CORPUS — 167 fichiers
`OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1(5).zip`

| Groupe interne | Count |
|---|---:|
| `docs` | 129 |
| `periphery` | 11 |
| `registry` | 8 |
| `.runtime_freezes` | 7 |
| `__ROOT__` | 7 |
| `tests` | 5 |

Extensions: `.md`=132, `.json`=18, `.py`=16, `.txt`=1

### EXTERNAL_SIGNALS_CORPUS — 41 fichiers
`OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1(5).zip`

| Groupe interne | Count |
|---|---:|
| `component_specs` | 24 |
| `merge_appendices` | 5 |
| `__ROOT__` | 4 |
| `family_specs` | 3 |
| `packets` | 3 |
| `proof` | 1 |
| `tests` | 1 |

Extensions: `.yaml`=32, `.md`=6, `.csv`=2, `.txt`=1

### NPL_ARCHIVE_CORPUS — 103 fichiers
`OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX(2).zip`

| Groupe interne | Count |
|---|---:|
| `05_METRICS` | 13 |
| `10_EXTERNAL_REFERENCES` | 11 |
| `03_SIGNALS` | 10 |
| `11_ADVANCED_PROVENANCE` | 10 |
| `06_OBSIDIA_BRANCHING` | 8 |
| `__ROOT__` | 8 |
| `02_CORE_CONCEPTS` | 7 |
| `07_ADVERSARIAL_RISKS` | 7 |
| `08_TESTS_REQUIRED` | 7 |
| `00_INDEX` | 6 |
| `09_AUDIT` | 6 |
| `01_MASTER_SPEC` | 5 |
| `04_PACKET_SCHEMA` | 5 |

Extensions: `.md`=102, `.json`=1

## Ontologie composant — groupe/couche/module/pépite
| Classe matière | Module/corpus | Couche | Ce que ça porte | Count connu |
|---|---|---|---|---:|
| CORE_AUTHORITY_MATTER | KX108/X108 | OS0 | autorité, no bypass, temporal gate, decision ticket | 7 specs + runtime GitHub |
| INTERLAYER_CONSTITUTION_MATTER | Constitution | OS1 | qui lit/écrit/décide/agit; passage périphérie→kernel | 8 specs |
| RUNTIME_API_DISPATCH_MATTER | API Runtime | OS2 | routes, envelopes, dispatch, Bus, Sigma, Brody | 4 506 official corpus |
| PROOF_REPLAY_AUDIT_MATTER | OS3 | OS3 | tests, manifests, replay, evidence tickets | 9 specs + tests/proofs/freezes |
| PUBLIC_REVIEW_MATTER | Review/Demo | OS4 | external pack, docs, release/readiness | F77 + external_pack 11 |
| SIGMA_LAYER_MATTER | Sigma | Module | registry, dispatcher, packets, endpoints, connectors, bus bridge | 78 top-level + tests/docs |
| BUS_LAYER_MATTER | Bus | Module | stats, bridge, signal, sigma_state | GitHub official |
| BRODY_RUNTIME_MATTER | Brody | Module | True Voice, domain raccord, response, memory chain | GitHub official/periphery |
| MEMORY_CONTEXT_MATTER | Graphiti/Mémoire | Module | ContextPacket readonly, memory boundaries, Graphiti read only | 7 specs + runtime |
| TREE34_FLUX_MATTER | Tree34 | Cosmos | cognitive trees, flux, non-decision contract | 5 specs + Atlas source |
| BALANCE_BUV_MATTER | BUV/Balance | Cosmos | admissibility/weighting no decision | 9 specs |
| NARRATIVE_PROVENANCE_MATTER | NPL | Cosmos | logic as culture, archive gap, truth regime, hidden transcript | 34 local specs + 103 zip |
| EXTERNAL_SIGNAL_MATTER | External Signals/Timeverse | Protocol | temporal context, receipts, anti replay, consequence boundary | 39 local specs + 41 zip |
| CRITICAL_WORLD_MATTER | Bank/Trading/Ecom/GPS | Domain | critical-world admission, no actuator without ticket | 14 specs + Sigma runtime |
| VALUE_MATTER | Gencoin/Jcoin | Domain | value attestation, no mint without X108 | 11 specs + runtime partial |
| SECURITY_COMPLIANCE_MATTER | RSSI/RGPD/ISO | Security | risk, controls, evidence, compliance readiness | 280 + 167 zip |
| SOURCE_PROVENANCE_MATTER | Source packs/discovery | Source | raw packs, audits, mapping, backlog | 36 discovery + 20 source packs |
