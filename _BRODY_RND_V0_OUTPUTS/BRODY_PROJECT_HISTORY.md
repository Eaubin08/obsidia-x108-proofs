# BRODY_PROJECT_HISTORY.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Chronologie du projet Obsidia X-108

### Phase P1 — Preuves publiques (2026-04-22, FERMÉ)

**Objectif :** Établir un périmètre public de vérification déterministe.

**Jalons :**
- `bd87e15` — Commit de clôture technique : ferme les zones d'ombre techniques de P1
- `99e966a` — Commit de gel public : ajoute le pack de clôture public, gèle P1 en périmètre lisible public
- `p1-freeze-2026-04-22` — Tag officiel de gel public (cible canonique pour audit externe)
- `v1.0.0-stable-kernel` — Release GitHub officielle (même périmètre que le freeze P1)
- `v1.0-sovereign-kernel` — Tag de souveraineté (même commit que v1.0.0-stable-kernel : `ac2b56a`)

**Contenu livré en P1 :**
- Lean 4 : 5 invariants formels prouvés (D1, E2, G1, G2, G3) — 0 sorry
- TLA+ : X108.tla + DistributedX108.tla — 1,2M états explorés, 0 violation
- Python verifiers : verify_all.py, verify_decision.py, verify_merkle.py
- Sigma public minimal : run_pipeline.py, sigma_monitor.py, contracts.py
- RFC3161 anchor schema checks
- 22/22 tests Python PASS, 39/39 tests TypeScript PASS
- 1M+ cas adversariaux sans faille
- Runner public : run_all_proofs.ps1 → `=== DONE ===`

**Ce qui n'est PAS dans P1 :**
- Moteur de production propriétaire complet
- Couche Sigma de production complète
- Adaptateurs métier finaux (banking, trading, ecom)
- Cockpit opérateur institutionnel
- Garantie permanente des TSA tiers

---

### Phase P2 — Banking (post-P1, actif)

**Objectif :** Extension du périmètre public vers les scénarios bancaires avancés.

**Sous-phases observées :**
- `P2_BANK_SCOPE` : définition du périmètre bank P2
- `P2_BANK_TEST_SCOPE` : tests bank
- `P2_BANK_SCALE_SCOPE` / `P2_BANK_SCALE_RESULTS` : tests à l'échelle (1000+ transactions)
- `P2_BANK_ADVERSARIAL_SCOPE` : scénarios adversariaux bank
- `P2_BANK_SECURITY_FUZZ_SCOPE` / `_EXTENDED` : fuzzing sécurité
- `P2_BANK_REGULATORY_PROXY_SCOPE` : proxy réglementaire
- `P2_BANK_TRUTH_PROXY_SCOPE` : vérité-proxy
- `P2_BANK_REPLAY_RESULTS` : replay 10k transactions
- `P2_BANK_CONFUSION_MATRIX_SCOPE` : matrice de confusion
- `P2_BANK_ENTERPRISE_SCOPE` : scénarios entreprise
- `P2_BANK_ROBO_REAL_BATCH1000` : batch réel 1000 transactions
- `P2_BANK_HARDER_THAN_BUSINESS_CASES` : cas plus difficiles que des cas business

**Sigma batches P2 :**
- `sigma/batches/bank_enterprise_pack.json`
- `sigma/batches/bank_regulatory_proxy_pack.json`
- `sigma/batches/bank_truth_proxy_pack.json`

---

### Développement du module BRODY (historique audits locaux)

Observé via `_local_audits/` (nomenclature datée) :

| Date | Audit | Sujet |
|---|---|---|
| 2026-05-14 | BRODY_X108_FULL_STABILIZED_SYSTEM_FINAL_SMOKE_READONLY | Smoke test complet stabilisé |
| 2026-05-14 | BRODY_NON_ACTIVATED_LAYERS_INTEGRITY_TEST_READONLY | Test intégrité couches non activées |
| 2026-05-14 | BRODY_RUNTIME_REAL_FILES_AUDIT_READONLY | Audit fichiers runtime réels |
| 2026-05-20 | BRODY_CONNECTION_MAP_AUDIT | Carte connexions Brody |
| 2026-05-21 | BRODY_BRIDGE_EVENTBUS_IMPORT_AUDIT | Audit import EventBus/Bridge |
| 2026-05-21 | BRODY_BRIDGE_LIFECYCLE_FIX | Fix cycle de vie du bridge |
| 2026-05-21 | BRODY_OBSIDIEN_FULL_RUNTIME_FREEZE | Gel runtime complet Obsidien |
| 2026-05-21 | BRODY_TERMINAL_LIVE_16 (x2) | Tests live terminal 16 cas |
| 2026-05-22 | BRODY_HTTP_UTF8_PAYLOAD_PACKETIZATION_V1_PASS | Packetisation HTTP UTF8 |
| 2026-05-22 | BRODY_OUTPUT_PRINCIPLE_EXTENSION_AUDIT | Audit extension principe output |
| 2026-05-22 | OUTPUT_ENVELOPE_V1 (multiple passes) | Enveloppe output V1 |
| 2026-05-22 | BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1 | Gate d'intake réel |
| 2026-05-23 | BRODY_GENERAL_CONVERSATION_MODE_READONLY_V1_FINAL_PASS | Mode conversation général final |
| 2026-05-23 | BRODY_LANGUAGE_TERMINAL_TEST | Test terminal multilingue |
| 2026-05-23 | BRODY_NATURAL_LANGUAGE_16_CASES_RETEST | Retest 16 cas langage naturel |

**Pattern observé :** Développement itératif intense sur 2 semaines (14-23 mai 2026), orienté vers la stabilisation du runtime BRODY + validation des invariants de souveraineté.

---

### TRI_RAPPORT — Rapports de tri datés

Observés à la racine du repo (non lus en profondeur) :
- TRI_RAPPORT_20260520 → TRI_RAPPORT_20260617 (14 rapports)

Ces rapports documentent les opérations de tri et réorganisation du repo au fil du temps.

---

### Évolution architecturale (OS0 → OS4)

Observé via noms de fichiers et références dans `periphery/` :
- **OS3** : `periphery/agents/os3_proof_agent.py` — couche de preuve
- **OS4** / `OBSIDIA_V4_STRUCTURED_FULL/` : version V4 complète structurée
- **OS_MMONDE** / `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1` : reverse OS, 34 arbres agents, P2+
- Contrats OS3/OS4/ADELE dans `periphery/OBSIDIA_V4_STRUCTURED_FULL/11_CONTRATS_OS3_OS4_ADELE`

---

### Gencoin

Observé via :
- `OBSIDIA_GENCOIN_ENGINE_LARGE_SANDBOX_PRE_FREEZE.zip` (racine)
- `periphery/agents/gencoin_value_agent.py`
- `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md` — **Gencoin n'est PAS un token crypto**
- `docs/GENCOIN_SANDBOX_INGESTION_REPORT.md`

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
