# Evidence Board - Obsidia X-108 - 3 domaines

Date : 2026-04-29 15:47:19
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_evidence_board_3_domains_20260429_154534`

## 1. Synthese courte

| Element | Valeur |
|---|---:|
| Domaines testes | 3 |
| Metriques response totales | 321 |
| Metriques runtime decisions | 4278 |
| Decisions avant audit | 8398 |
| Decisions apres audit | 8439 |
| Decisions creees pendant audit | 41 |
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
| bank | `988680FD35AD` | `128380709C77` | `28F472CF8A67` | 7 | `477896BD4420; F482AEDC12DC; B4C77C99EBD1; 3C81942F4896; E2290456752D; 6FB5EB48389B; 9FAD84930988` |
| trading | `A09D6DEE2AD5` | `6FEDD66FCD5B` | `78DA1F1A2234` | 20 | `32BDF6FA2AEE; A4C21C407E88; CF32596294F3; 7AF8254B47D7; 5E67E414D224; 22C5EEED49EC; 43F9656770EE; 262ADD07DB31; 14E4D68C701C; 39432F022E99; 69AC348E158B; D345925089F0; 0F73278054B5; 56731A149FFC; AD478893C8A8; 973CBC682D72; 60E54D3C46CF; 1C94D448BCD3; 09A141E87F14; 88DBE0F73228` |
| gps_defense_aviation | `0E9835CD2BEB` | `DC1C168712D2` | `2815F96A255D` | 14 | `042678A0E83A; 9DD704F8B95E; 2AFFB79EC4D0; B293BA84C70C; DAF9B2605DC5; BC02CDB9CDEA; 6130DE675ACE; 03F9313B2B35; 5A664814D0CF; 27902F90A300; CD1390D34BA6; B32ED03DE550; E648CB2DAB0D; 7E469F2198B7` |

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
| `decision_bank_1777470339830.json` | 3468 | `477896BD4420` |
| `decision_bank_1777470350459.json` | 3468 | `F482AEDC12DC` |
| `decision_bank_1777470361604.json` | 3468 | `B4C77C99EBD1` |
| `decision_bank_1777470372238.json` | 3468 | `3C81942F4896` |
| `decision_bank_1777470382835.json` | 3468 | `E2290456752D` |
| `decision_bank_1777470393240.json` | 3468 | `6FB5EB48389B` |
| `decision_bank_1777470398736.json` | 3720 | `9FAD84930988` |
| `decision_gps_defense_aviation_1777470340099.json` | 3349 | `042678A0E83A` |
| `decision_gps_defense_aviation_1777470344664.json` | 3349 | `9DD704F8B95E` |
| `decision_gps_defense_aviation_1777470349274.json` | 3349 | `2AFFB79EC4D0` |
| `decision_gps_defense_aviation_1777470354191.json` | 3349 | `B293BA84C70C` |
| `decision_gps_defense_aviation_1777470358662.json` | 3349 | `DAF9B2605DC5` |
| `decision_gps_defense_aviation_1777470362984.json` | 3349 | `BC02CDB9CDEA` |
| `decision_gps_defense_aviation_1777470367438.json` | 3349 | `6130DE675ACE` |
| `decision_gps_defense_aviation_1777470372043.json` | 3349 | `03F9313B2B35` |
| `decision_gps_defense_aviation_1777470377082.json` | 3349 | `5A664814D0CF` |
| `decision_gps_defense_aviation_1777470381650.json` | 3349 | `27902F90A300` |
| `decision_gps_defense_aviation_1777470388742.json` | 3349 | `CD1390D34BA6` |
| `decision_gps_defense_aviation_1777470393147.json` | 3349 | `B32ED03DE550` |
| `decision_gps_defense_aviation_1777470398235.json` | 3349 | `E648CB2DAB0D` |
| `decision_gps_defense_aviation_1777470400242.json` | 3448 | `7E469F2198B7` |
| `decision_trading_1777470337899.json` | 3520 | `32BDF6FA2AEE` |
| `decision_trading_1777470341020.json` | 3520 | `A4C21C407E88` |
| `decision_trading_1777470344369.json` | 3520 | `CF32596294F3` |
| `decision_trading_1777470348377.json` | 3520 | `7AF8254B47D7` |
| `decision_trading_1777470351569.json` | 3520 | `5E67E414D224` |
| `decision_trading_1777470356135.json` | 3520 | `22C5EEED49EC` |
| `decision_trading_1777470359157.json` | 3520 | `43F9656770EE` |
| `decision_trading_1777470362199.json` | 3520 | `262ADD07DB31` |
| `decision_trading_1777470365496.json` | 3520 | `14E4D68C701C` |
| `decision_trading_1777470369004.json` | 3520 | `39432F022E99` |
| `decision_trading_1777470372202.json` | 3520 | `69AC348E158B` |
| `decision_trading_1777470375213.json` | 3520 | `D345925089F0` |
| `decision_trading_1777470378235.json` | 3520 | `0F73278054B5` |
| `decision_trading_1777470381503.json` | 3520 | `56731A149FFC` |
| `decision_trading_1777470384373.json` | 3520 | `AD478893C8A8` |
| `decision_trading_1777470389326.json` | 3520 | `973CBC682D72` |
| `decision_trading_1777470392714.json` | 3520 | `60E54D3C46CF` |
| `decision_trading_1777470397776.json` | 3520 | `1C94D448BCD3` |
| `decision_trading_1777470399702.json` | 3461 | `09A141E87F14` |
| `decision_trading_1777470400885.json` | 3520 | `88DBE0F73228` |

## 7. Scellage / racines

| Element | SHA256 |
|---|---|
| Merkle before | `F24ED74FD5E7B756395F9F63F104A19C18DB58C8411FD823B1ABF9254B0055F7` |
| Merkle after | `90E1414A8750DD969B0DECDBE01AB81584E702838484FF1D8EE7271BF657F6E2` |
| Server stdout | `9B71A764857C05AC52036549B6424A9D1E0904C5F5AD6A542D957DA6E533450D` |
| Server stderr | `EB2A1134376CA1462B0B88AAB838A09FCA6D5A7DE132CBB554E717410630D45A` |
| Trace manifest | `D1E3534711C0704AC270E7ACECBB022D21EAAA00FB9A8FB9F1B5509BE0092283` |
| Audit root | `4502fa58bea3829b8c19d0daa00da904b5f4227e7022af8613eae3fa0391310e` |

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
| Tracabilite decisions | 41 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=D1E3534711C0704AC270E7ACECBB022D21EAAA00FB9A8FB9F1B5509BE0092283 | OK |
| Racine audit | AUDIT_ROOT_SHA256=4502fa58bea3829b8c19d0daa00da904b5f4227e7022af8613eae3fa0391310e | OK |
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
| `response_bank.json` | 6966 | `128380709C77` |
| `response_trading.json` | 6708 | `6FEDD66FCD5B` |
| `response_gps_defense_aviation.json` | 6341 | `DC1C168712D2` |
| `metrics_full_bank.csv` | 8121 | `28F472CF8A67` |
| `metrics_full_trading.csv` | 8153 | `78DA1F1A2234` |
| `metrics_full_gps_defense_aviation.csv` | 8938 | `2815F96A255D` |
| `ALL_METRICS_FLAT.csv` | 25120 | `78DA71B15908` |
| `ALL_METRIC_CATEGORIES.csv` | 2743 | `341AE4D7F898` |
| `TRACE_CHAINS_BY_DOMAIN.csv` | 5380 | `EA97A53090D2` |
| `TRACE_STATS.json` | 1034 | `C427FFB39617` |
| `TRACE_MANIFEST.json` | 60720 | `D1E3534711C0` |
| `decisions_before.csv` | 2241051 | `2FE15169D7AA` |
| `decisions_after.csv` | 2251992 | `51D2F44D4A9B` |
| `decisions_created_during_audit.csv` | 10079 | `3A4F6800D717` |
| `decision_runtime_metrics_flat.csv` | 620075 | `89D735485953` |
| `runtime_file_hashes.csv` | 1337 | `FECBEBBB9946` |
| `server.stdout.log` | 955 | `9B71A764857C` |
| `server.stderr.log` | 4551 | `EB2A1134376C` |
| `merkle_seal_before.json` | 317 | `F24ED74FD5E7` |
| `merkle_seal_after.json` | 317 | `90E1414A8750` |

## 11. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines.
