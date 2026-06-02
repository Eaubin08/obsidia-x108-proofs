# RAW_SEARCH_LOG
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1
# Date: 2026-06-02

> Journal brut des commandes de recherche exécutées, repos inspectés, erreurs rencontrées.

---

## Repos inspectés (locaux)

| Repo | Chemin | Présent |
|------|--------|---------|
| obsidia-x108-proofs_REMOTE_A5F21C6B | C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_REMOTE_A5F21C6B | OUI (repo principal) |
| obsidia-x108-proofs | C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs | OUI |
| _obsidia-local-workspace | C:/Users/User/Desktop/obsidia-engine-proof-core/_obsidia-local-workspace | OUI (données privées quarantinées) |
| obsidia-x108-proofs_PUSH_CLEAN_20260526_195026 | C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs_PUSH_CLEAN_20260526_195026 | OUI |
| obsidia-x108-proofs-agentic-registry | C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs-agentic-registry | OUI |
| obsidia-x108-proofs-graph-memory | C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs-graph-memory | OUI |
| obsidiashell-main | C:/Users/User/Desktop/obsidia-engine-proof-core/obsidiashell-main | OUI |
| proofs | C:/Users/User/Desktop/obsidia-engine-proof-core/proofs | OUI |
| obsidia-engine-candidate | C:/Users/User/Desktop/obsidia-engine-proof-core/obsidia-engine-candidate | OUI |
| Demo-obsidia-x108-proof | — | NON VÉRIFIÉ (hors scope session) |
| bank-robo | — | NON VÉRIFIÉ |
| agentic-commerce-safe-demo-V2 | — | NON VÉRIFIÉ |
| Obsidia-lab-trad | — | NON VÉRIFIÉ |
| obsidia-guard-v1-github | — | NON VÉRIFIÉ |
| agi-vison | — | NON VÉRIFIÉ |
| preprint-conscience | — | NON VÉRIFIÉ |

---

## Commandes exécutées

### 1. Vérification de la racine
```bash
ls C:/Users/User/Desktop/obsidia-engine-proof-core/
# → ROOT_FOUND, 9 repos locaux présents + nombreux fichiers CURRENT_*
```

### 2. Vérification des 23 fichiers sources prioritaires
```bash
# Boucle sur docs/, periphery/, sigma/, connectors/ pour chaque fichier listé
# Résultat : 23/23 FOUND dans obsidia-x108-proofs_REMOTE_A5F21C6B
```

### 3. Vérification MMONDE / Tree34
```bash
# Boucle sur periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/
# Résultat : 8/8 chemins FOUND
```

### 4. Grep KX108 / X108 gate / ACT / ALLOW / HOLD / BLOCK
```bash
grep -rl "KX108|X108|emits_act|decision_authority|ALLOW|HOLD|BLOCK|OS3ProofTicket|DecisionTicket" periphery/ sigma/ connectors/
# → >20 fichiers trouvés, dont action_lifecycle.py, os3_ticket.py, gencoin.py
```

### 5. Grep Lyapunov / ProofOfGovernance / governed_state
```bash
grep -rl "Lyapunov|ProofOfGovernance|governed_state|thermo_debt|delta_E|delta_C|computational_debt" periphery/
# → 10 fichiers dont math_core/lyapunov.py, math_core/governed_state.py, energy_thermo.py
```

### 6. Grep Gencoin / Jcoin / BUV / Balance
```bash
grep -rl "Gencoin|Jcoin|BUV|Balance|mint_allowed|gencoin_candidate|gross_value|net_value" periphery/ sigma/
# → 13 fichiers, Jcoin = 0 résultats
```

### 7. Grep GPS / aviation / trajectory
```bash
grep -rl "GPS|aviation|trajectory_drift|trajectory_integrity|PeripheralSignalPacket|ABORT_TRAJECTORY" periphery/ sigma/ connectors/
# → adapters/gps_adapter.py, sigma/domains/gps_defense_aviation_agents.py, connectors/aviation_robo.py
```

### 8. Grep Shazam / HexaFlux / BDF / Reverse OS / MCP Bridge
```bash
grep -rl "Shazam|spectral_hash|dominant_tree|HexaFlux|LTCU|BDF|double_brain|Reverse OS|SSR|Jarvis|MCP.Bridge|policy_scope_guard" periphery/ sigma/
# → periphery/cognitive_trees/shazam_cognitif.py, bdf/double_brain_router.py, hexaflux/ltcu_plus.py, mcp_bridge.py, jarvis_projection.py
```

### 9. Vérification action lifecycle states
```bash
grep -n "INPUT_CAPTURED|ACTION_CANDIDATE_BUILT|..." periphery/action_lifecycle.py
# → 10 états confirmés (lignes 8-30), + FEEDBACK_CAPTURED (absent du prompt original)
```

### 10. F74-F77 statut
```bash
grep -n "PROD_BLOCKED|PACK_PARTIAL|CORS|auth.absente|health" docs/architecture/F74_F77_FINALIZATION_AUDIT.md
# → F76 PROD_BLOCKED, F77 PACK_PARTIAL confirmés
```

### 11. Agents 52 registry
```bash
cat periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/10_AGENTS_52/agents_52.registry.json | python3 parse
# → 10 premiers agents lus : OBSIDIA_ATLAS_INGESTOR, CANON_GUARDIAN, GRAPH_BUILDER, etc.
```

### 12. _obsidia-local-workspace structure
```bash
find _obsidia-local-workspace -maxdepth 2 -type d
# → Données privées retirées du repo public (graphiti, mmonde_docx, session-packets)
# → PAS un workspace Obsidia au sens fondations/domaines/agents/
```

### 13. Jcoin search
```bash
grep -rn "Jcoin|J_coin|jcoin|j_coin" . --include="*.py" --include="*.md" --include="*.json"
# → 0 résultats = ABSENT_UNDER_THIS_NAME
```

### 14. .xyz search
```bash
grep -rn "\.xyz|XYZ|xyz_spec" docs/ periphery/ sigma/
# → BRANCHESXYZKLN.md dans periphery/OBSIDIA_V4_STRUCTURED_FULL/ = SOURCE_FOUND_UNDER_DIFFERENT_NAME
```

### 15. Sept flux / 7 flux
```bash
grep -rn "sept flux|7 flux|Arbre des Flux" .
# → T31="Arbre des Flux" dans brody_tree_policy.py
# → "7 flux" dans docs/REPO_BOUNDARY.md: HORS périmètre public
```

### 16. Claim-scope risks
```bash
grep -rn "production.complete|AGI.ready|cloud.ready|fully.formally.proven|real token|Jcoin" docs/
# → Docs GENCOIN_NOT_A_TOKEN_POLICY_V1.md, TOKEN_POLICY_V1.md, BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md
# → Plusieurs sources explicitement nient : pas production-ready, pas cloud-ready, pas AGI-ready
```

---

## Erreurs rencontrées

- Aucune erreur critique
- `periphery/jarvis_projection.py` : stub minimal (3 lignes) — PLACEHOLDER confirmé
- `_obsidia-local-workspace` : contient données privées quarantinées, non un workspace hub Obsidia
- GitHub CLI (`gh`) non utilisé (non requis — toutes les sources trouvées localement)

---

## Repos Priorité 2/3 non inspectés

Demo-obsidia-x108-proof, bank-robo, agentic-commerce-safe-demo-V2-finale-hackathon-2, Obsidia-lab-trad, obsidia-guard-v1-github, agi-vison, preprint-conscience — absents du disque local ou non cherchés dans cette session. Marqués `ABSENT_LOCAL_REPO` par défaut pour cette session.
