# Evidence Board - Obsidia X-108 - 3 domaines

Date : 2026-04-28 23:38:51
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_evidence_board_3_domains_20260428_233732`

## 1. Synthese courte

| Element | Valeur |
|---|---:|
| Domaines testes | 3 |
| Metriques response totales | 321 |
| Metriques runtime decisions | 2929 |
| Decisions avant audit | 7774 |
| Decisions apres audit | 7802 |
| Decisions creees pendant audit | 28 |
| Fichiers runtime hashes | 13 |
| Artefacts de preuve hashes | 23 |

## 2. Git / version

| Champ | Valeur |
|---|---|
| Branche | `temp-reims` |
| Commit | `fe801ddadf851b7e2ce5b2bb11612396999b5ef6` |
| Tags HEAD | `audit-evidence-board-v2-20260428-233523` |
| Status | ` M merkle_seal.json; ?? RUN_AUDIT_TABLEAU_POST_EVIDENCE.ps1` |

## 3. Tableau decisionnel

| Domaine | Verdict | Gate | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| bank | ANALYZE | BLOCK | 0.5 | 0.95 | 0.66 | 0.7033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 111 |
| trading | REVIEW | HOLD | 0.5 | 0.75 | 0.6 | 0.6167 | S2 | RISK_FLAGS_REQUIRE_DELAY | 108 |
| gps_defense_aviation | ABORT_TRAJECTORY | BLOCK | 0.35 | 0.95 | 0.51 | 0.6033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 102 |

## 4. Chaines de trace par domaine

| Domaine | Input SHA | Response SHA | Metrics SHA | Decision count | Decision hashes |
|---|---:|---:|---:|---:|---|
| bank | `988680FD35AD` | `255A3225E2F6` | `C791C23AF0EB` | 5 | `7FE4F8770376; 7595B7604D17; C75FE06A6489; EDB6CBBDAB98; 335E09233298` |
| trading | `A09D6DEE2AD5` | `360032506A16` | `8627C56A29A0` | 14 | `8FC122E711B3; EB18A51043A5; 084C8BB9BCCC; 36E66B73E10A; AAD68EEF8E70; 2152DC1DC2FC; CA3AE04D0CB8; EB6F5AF930BB; F6A6B7F7EFFA; 00BAA5A19023; 60D5590AF416; EC6B1DCFCDF7; 22BB2A8D9649; FD3DFD14A3AB` |
| gps_defense_aviation | `0E9835CD2BEB` | `4A18D4FB0371` | `1F5A47612074` | 9 | `2D1D218981A1; 66B2C46B07EC; 4DE3CE3464AA; EBF61A5CC42A; D7F33BB257EE; 007BA38D23CF; 9BFBCF1C376F; 6B25E99BE368; CF1CBC61A44D` |

## 5. Categories de metriques

| Domaine | Categorie | Nombre |
|---|---|---:|
| trading | evidence_refs | 27 |
| bank | evidence_refs | 22 |
| bank | sigma_report | 21 |
| trading | sigma_report | 21 |
| gps_defense_aviation | sigma_report | 21 |
| trading | raw_engine | 19 |
| gps_defense_aviation | evidence_refs | 16 |
| bank | raw_engine | 14 |
| gps_defense_aviation | unknowns | 13 |
| bank | unknowns | 9 |
| gps_defense_aviation | metrics | 9 |
| bank | sigma_step | 8 |
| gps_defense_aviation | sigma_step | 8 |
| bank | contradictions | 8 |
| trading | sigma_step | 8 |
| gps_defense_aviation | raw_engine | 8 |
| bank | metrics | 5 |
| trading | array_empty | 5 |
| trading | metrics | 5 |
| gps_defense_aviation | contradictions | 4 |
| trading | risk_flags | 4 |
| gps_defense_aviation | array_empty | 4 |
| bank | array_empty | 3 |
| bank | risk_flags | 2 |
| gps_defense_aviation | null | 1 |
| trading | source | 1 |
| gps_defense_aviation | domain | 1 |
| gps_defense_aviation | confidence | 1 |
| gps_defense_aviation | market_verdict | 1 |
| trading | sigma_override | 1 |
| gps_defense_aviation | sigma_override | 1 |
| bank | domain | 1 |
| gps_defense_aviation | source | 1 |
| gps_defense_aviation | attestation_ref | 1 |
| gps_defense_aviation | decision_id | 1 |
| gps_defense_aviation | trace_id | 1 |
| gps_defense_aviation | ticket_required | 1 |
| gps_defense_aviation | x108_gate | 1 |
| gps_defense_aviation | reason_code | 1 |
| gps_defense_aviation | severity | 1 |
| gps_defense_aviation | confidence_readiness | 1 |
| gps_defense_aviation | confidence_governance | 1 |
| gps_defense_aviation | confidence_integrity | 1 |
| gps_defense_aviation | readiness_scope | 1 |
| gps_defense_aviation | governance_scope | 1 |
| gps_defense_aviation | confidence_scope | 1 |
| trading | attestation_ref | 1 |
| bank | decision_id | 1 |
| bank | trace_id | 1 |
| bank | reason_code | 1 |
| bank | severity | 1 |
| bank | attestation_ref | 1 |
| bank | source | 1 |
| bank | ticket_required | 1 |
| bank | null | 1 |
| bank | x108_gate | 1 |
| bank | confidence_integrity | 1 |
| bank | confidence_governance | 1 |
| bank | market_verdict | 1 |
| bank | confidence | 1 |
| bank | governance_scope | 1 |
| bank | readiness_scope | 1 |
| bank | confidence_readiness | 1 |
| bank | confidence_scope | 1 |
| trading | reason_code | 1 |
| trading | severity | 1 |
| trading | readiness_scope | 1 |
| trading | x108_gate | 1 |
| trading | ticket_required | 1 |
| trading | null | 1 |
| trading | decision_id | 1 |
| trading | trace_id | 1 |
| trading | governance_scope | 1 |
| trading | market_verdict | 1 |
| trading | confidence | 1 |
| bank | sigma_override | 1 |
| trading | domain | 1 |
| trading | confidence_readiness | 1 |
| trading | confidence_scope | 1 |
| trading | confidence_integrity | 1 |
| trading | confidence_governance | 1 |

## 6. Decisions runtime creees pendant audit

| Fichier | Taille | SHA256 court |
|---|---:|---:|
| `decision_bank_1777412259624.json` | 3468 | `7FE4F8770376` |
| `decision_bank_1777412269980.json` | 3468 | `7595B7604D17` |
| `decision_bank_1777412280268.json` | 3468 | `C75FE06A6489` |
| `decision_bank_1777412290724.json` | 3468 | `EDB6CBBDAB98` |
| `decision_bank_1777412290904.json` | 3720 | `335E09233298` |
| `decision_gps_defense_aviation_1777412257489.json` | 3349 | `2D1D218981A1` |
| `decision_gps_defense_aviation_1777412261828.json` | 3349 | `66B2C46B07EC` |
| `decision_gps_defense_aviation_1777412266181.json` | 3349 | `4DE3CE3464AA` |
| `decision_gps_defense_aviation_1777412270600.json` | 3349 | `EBF61A5CC42A` |
| `decision_gps_defense_aviation_1777412275006.json` | 3349 | `D7F33BB257EE` |
| `decision_gps_defense_aviation_1777412279255.json` | 3349 | `007BA38D23CF` |
| `decision_gps_defense_aviation_1777412283512.json` | 3349 | `9BFBCF1C376F` |
| `decision_gps_defense_aviation_1777412288843.json` | 3349 | `6B25E99BE368` |
| `decision_gps_defense_aviation_1777412291900.json` | 3448 | `CF1CBC61A44D` |
| `decision_trading_1777412254119.json` | 3520 | `8FC122E711B3` |
| `decision_trading_1777412256937.json` | 3520 | `EB18A51043A5` |
| `decision_trading_1777412259565.json` | 3520 | `084C8BB9BCCC` |
| `decision_trading_1777412262211.json` | 3520 | `36E66B73E10A` |
| `decision_trading_1777412264956.json` | 3520 | `AAD68EEF8E70` |
| `decision_trading_1777412267529.json` | 3520 | `2152DC1DC2FC` |
| `decision_trading_1777412270219.json` | 3520 | `CA3AE04D0CB8` |
| `decision_trading_1777412273011.json` | 3520 | `EB6F5AF930BB` |
| `decision_trading_1777412275623.json` | 3520 | `F6A6B7F7EFFA` |
| `decision_trading_1777412278819.json` | 3520 | `00BAA5A19023` |
| `decision_trading_1777412281586.json` | 3520 | `60D5590AF416` |
| `decision_trading_1777412284291.json` | 3520 | `EC6B1DCFCDF7` |
| `decision_trading_1777412291542.json` | 3461 | `22BB2A8D9649` |
| `decision_trading_1777412292248.json` | 3520 | `FD3DFD14A3AB` |

## 7. Scellage / racines

| Element | SHA256 |
|---|---|
| Merkle before | `E264FA8A8D42E5A6F8070BBF79120BCF61CC9236DCFA397BE0962C0420BA4542` |
| Merkle after | `E264FA8A8D42E5A6F8070BBF79120BCF61CC9236DCFA397BE0962C0420BA4542` |
| Server stdout | `F98708FD4217B3463F3CA7C74A857C10028614EB702B64A2A14EAA53AA33278D` |
| Server stderr | `FAC2CD72F1F74E85A80697AA83DFDF5D6954089435521583704DA5B95C6BAF84` |
| Trace manifest | `968204A0365324E50E62C8FFF11E2E78EFC1222C60D40670439F75C53FD0A8CA` |
| Audit root | `96cc8f6648e4554a04729c4c04a4306e4bc35d235a09a88092847174b7396e69` |

## 8. Matrice de preuves

| Axe | Preuve visible | Statut |
|---|---|---:|
| Routage multi-domaine | 3 domaines appellent le meme endpoint /kernel/ragnarok | OK |
| Decision avant action | Chaque domaine retourne verdict + gate X-108 avant execution | OK |
| Securite bank | bank retourne BLOCK sur transaction risquee | OK |
| Securite trading | trading retourne HOLD sur ordre risque | OK |
| Securite aviation | gps_defense_aviation retourne BLOCK sur navigation degradee | OK |
| Metrisation | 321 metriques response flattenees | OK |
| Tracabilite input | 3 payloads input sauvegardes + hashes | OK |
| Tracabilite output | 3 responses sauvegardees + hashes | OK |
| Tracabilite metrics | metrics_full_*.csv + ALL_METRICS_FLAT.csv | OK |
| Tracabilite decisions | 28 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=968204A0365324E50E62C8FFF11E2E78EFC1222C60D40670439F75C53FD0A8CA | OK |
| Racine audit | AUDIT_ROOT_SHA256=96cc8f6648e4554a04729c4c04a4306e4bc35d235a09a88092847174b7396e69 | OK |
| Reproductibilite Git | branch/commit/tag/status captures | OK |

## 9. Lecture securite

### bank

- Sens : Transaction bancaire mobile risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte.
- Verdict : `ANALYZE`
- Gate X-108 : `BLOCK`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Severity : `S4`
- Lecture : REFUS AVANT EXECUTION : le moteur bloque l'action avant qu'elle ne puisse produire un effet.
- Metriques retournees : `111`
- Categories : `evidence_refs=22; sigma_report=21; raw_engine=14; unknowns=9; contradictions=8; sigma_step=8; metrics=5; array_empty=3; risk_flags=2; ticket_required=1; trace_id=1; null=1; attestation_ref=1; sigma_override=1; domain=1; source=1; confidence_governance=1; confidence_readiness=1; confidence_scope=1; market_verdict=1; confidence=1; confidence_integrity=1; reason_code=1; severity=1; decision_id=1; governance_scope=1; readiness_scope=1; x108_gate=1`

### trading

- Sens : Ordre de trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves.
- Verdict : `REVIEW`
- Gate X-108 : `HOLD`
- Reason : `RISK_FLAGS_REQUIRE_DELAY`
- Severity : `S2`
- Lecture : TEMPORISATION X-108 : le moteur retient l'action et impose une attente/coherence supplementaire.
- Metriques retournees : `108`
- Categories : `evidence_refs=27; sigma_report=21; raw_engine=19; sigma_step=8; array_empty=5; metrics=5; risk_flags=4; trace_id=1; ticket_required=1; null=1; domain=1; sigma_override=1; attestation_ref=1; source=1; decision_id=1; confidence_governance=1; confidence_readiness=1; confidence_integrity=1; market_verdict=1; confidence=1; confidence_scope=1; reason_code=1; severity=1; x108_gate=1; governance_scope=1; readiness_scope=1`

### gps_defense_aviation

- Sens : Navigation aviation/GPS degradee : faible qualite signal, conflit source, risque spoofing, deviation et skew temporel.
- Verdict : `ABORT_TRAJECTORY`
- Gate X-108 : `BLOCK`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Severity : `S4`
- Lecture : REFUS AVANT EXECUTION : le moteur bloque l'action avant qu'elle ne puisse produire un effet.
- Metriques retournees : `102`
- Categories : `sigma_report=21; evidence_refs=16; unknowns=13; metrics=9; sigma_step=8; raw_engine=8; contradictions=4; array_empty=4; ticket_required=1; trace_id=1; null=1; sigma_override=1; domain=1; attestation_ref=1; source=1; decision_id=1; confidence_governance=1; confidence_readiness=1; confidence_integrity=1; market_verdict=1; confidence=1; confidence_scope=1; reason_code=1; severity=1; x108_gate=1; governance_scope=1; readiness_scope=1`

## 10. Tous les fichiers de preuve

| Fichier | Taille | SHA256 court |
|---|---:|---:|
| `input_bank.json` | 486 | `988680FD35AD` |
| `input_trading.json` | 263 | `A09D6DEE2AD5` |
| `input_gps_defense_aviation.json` | 335 | `0E9835CD2BEB` |
| `response_bank.json` | 6966 | `255A3225E2F6` |
| `response_trading.json` | 6708 | `360032506A16` |
| `response_gps_defense_aviation.json` | 6341 | `4A18D4FB0371` |
| `metrics_full_bank.csv` | 8121 | `C791C23AF0EB` |
| `metrics_full_trading.csv` | 8153 | `8627C56A29A0` |
| `metrics_full_gps_defense_aviation.csv` | 8938 | `1F5A47612074` |
| `ALL_METRICS_FLAT.csv` | 25120 | `6FD72B4E3C07` |
| `ALL_METRIC_CATEGORIES.csv` | 2743 | `341AE4D7F898` |
| `TRACE_CHAINS_BY_DOMAIN.csv` | 3981 | `66A0A8B44AF1` |
| `TRACE_STATS.json` | 1034 | `555CC0F1ECE0` |
| `TRACE_MANIFEST.json` | 52755 | `968204A03653` |
| `decisions_before.csv` | 2074107 | `C65EA052397B` |
| `decisions_after.csv` | 2081563 | `E52F1AC63E06` |
| `decisions_created_during_audit.csv` | 6880 | `7A25AECBCA2A` |
| `decision_runtime_metrics_flat.csv` | 423062 | `D9B6A1481277` |
| `runtime_file_hashes.csv` | 1337 | `F8A8E4D23E91` |
| `server.stdout.log` | 949 | `F98708FD4217` |
| `server.stderr.log` | 4140 | `FAC2CD72F1F7` |
| `merkle_seal_before.json` | 317 | `E264FA8A8D42` |
| `merkle_seal_after.json` | 317 | `E264FA8A8D42` |

## 11. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines.
