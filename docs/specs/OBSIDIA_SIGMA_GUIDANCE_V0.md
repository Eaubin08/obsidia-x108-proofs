# OBSIDIA SIGMA GUIDANCE — spécification (V0 + FRESH_SIGNAL_V1)

Scopes : `SIGMA_GUIDANCE_V0`, `CALIBRATE_SIGMA_TERMINAL_GUIDANCE_V0`,
`SIGMA_GUIDANCE_FRESH_SIGNAL_V1`. Module : `scripts/obsidia_sigma_guidance.py`.

## Principe

Le terminal `obsidia` enrichit chaque réponse d'un verbe de guidance
non souverain, dérivé de signaux **strictement readonly**. Sigma Core
(`sigma/`) n'est ni importé, ni modifié, ni exécuté. Aucun subprocess,
aucune écriture, aucune régénération de preuve/seal/manifest.

## Carte des signaux (V1)

| Classe | Signal | Lecture |
|---|---|---|
| PRIMARY | `proofs/PROOFKIT_REPORT.json` | timestamp, overall, âge (FRESH ≤ 14j) |
| PRIMARY | `proofs/LEAN_PROOF_SURFACE_MANIFEST.json` | total_entries, forbidden_ok, lean_decides |
| SECONDARY | `merkle_seal.json` | status, audit_date uniquement — ne JAMAIS suggérer de le régénérer |
| SECONDARY | `_PATCH_PROPOSALS/` | dernier proposal.json (created_at), présence RECEIPT.md, launch_status (KNOWN_COMMANDS_ONLY si run_agent_obsidure.ps1 existe, sinon UNKNOWN — jamais inventé) |
| SECONDARY | routes HTTP live | `/api/periphery/monitoring/sigma/*`, timeout court |
| DIAGNOSTIC_ONLY | `sigma/stress_test_results.json` | ancien (2026-03) — ne domine jamais un signal frais |
| INTERDIT | `.local_obsidia/receipts/`, contenu .lean GeneratedPeripheral, `MANIFEST_SHA256.json` | jamais utilisés pour la guidance |

## Règles de priorité (V1)

1. ProofKit FAIL → CHECK_INVARIANT.
2. Manifest Lean illisible, forbidden_ok=false ou lean_decides=true → CHECK_INVARIANT (+ REQUEST_PROOF en raison).
3. merkle_seal status ≠ INTEGRITY_VERIFIED → HOLD_RECOMMENDED + REQUEST_TRACE (guidance terminale, PAS un HOLD X108).
4. ProofKit PASS frais + Lean sain → CONTINUE par défaut (toutes couches, y compris brody).
5. ProofKit PASS mais périmé (> 14j) → REQUEST_PROOF ; suggestion texte `python proofs/verify_all.py` (humain uniquement, jamais exécuté par le terminal).
6. Stress ancien non-PASS : diagnostic non contraignant si signaux primaires frais PASS ; peut porter CHECK_INVARIANT seulement sur {sigma, audit, obsidienne, kernel} ET sans signal frais qui le neutralise.
7. Aucun signal primaire lisible → REQUEST_PROOF.

Cas transverses : POLICY_DENY → HOLD_RECOMMENDED (inchangé) ; intention
inconnue → REQUEST_CONTEXT/STOP_UNKNOWN (inchangé) ; couche sigma + routes
monitoring DOWN → RELAUNCH_LAYER ; couche obsidure + dernier proposal < 7j
avec receipt → CONTINUE sur COMMANDS gated (les mutations restent POLICY_DENY).

Dates illisibles → `age_status: UNKNOWN`, raison diagnostique, jamais de crash.

## Topologie live (documentaire uniquement)

Kernel Ragnarok 3001 ; API Obsidia/Brody 8000 (Brody vit dans l'API via
`/api/brody/*`, pas de serveur séparé) ; Graphiti/Shell 8011 ; UI 5173 ;
Neo4j 7475/7688 ; adapters domaines `/api/live/kernel/adapters/{bank,trading,gps}`
→ Kernel. Le terminal ne démarre aucune stack — cette topologie sert
uniquement à étiqueter les signaux live.

## Vocabulaire

Défini dans `scripts/obsidia_guidance_vocabulary.py`, verrouillé par
`assert_output_allowed()`. `HOLD_RECOMMENDED` reste une recommandation
terminale ; le HOLD souverain est exclusivement `X108Gate.HOLD` (KX108_ONLY).
Aucun ALLOW/BLOCK/ACT n'est émissible.

## Sortie

Champs ajoutés : `guidance`, `guidance_reasons`, `guidance_authority: "NONE"`,
`guidance_note`. Couche sigma : bloc `sigma` complet (file_signals classés +
live_signals) retourné en EXECUTE.
