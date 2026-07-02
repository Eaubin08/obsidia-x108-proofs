# OBSIDIA SIGMA GUIDANCE V0 — spécification

Scope : `SIGMA_GUIDANCE_V0`. Module : `scripts/obsidia_sigma_guidance.py`.

## Principe

Le terminal `obsidia` enrichit chaque réponse d'un verbe de guidance
non souverain, dérivé de signaux **strictement readonly**. Sigma Core
(`sigma/`) n'est ni importé, ni modifié, ni exécuté.

## Canaux de signaux (readonly uniquement)

1. Fichiers (à froid, sans serveur) :
   - `sigma/stress_test_results.json` — steps non-PASS, violations
   - `sigma/sigma_config.json` — présence calibration
   - `proofs/LEAN_PROOF_SURFACE_MANIFEST.json` — total_entries
2. HTTP GET (si API 8000 up, timeout 1.5s, DOWN = normal) :
   - `/api/periphery/monitoring/sigma/domains`
   - `/api/periphery/monitoring/sigma/evaluate`

Interdit : subprocess, import de `sigma/`, écriture hors receipt terminal,
émission de `X108Gate`, création d'un `SigmaReport` canonique.

## Règles de dérivation V0

| Condition | Verbe |
|---|---|
| POLICY_DENY (mutation refusée) | HOLD_RECOMMENDED |
| Intention non reconnue | REQUEST_CONTEXT |
| Violations / steps non-PASS dans stress_test_results ET couche ∈ {sigma, audit, obsidienne, kernel} | CHECK_INVARIANT |
| Violations stress hors de ces couches | signal diagnostic non contraignant (verbe par défaut conservé) |
| Couche sigma visée + routes monitoring DOWN | RELAUNCH_LAYER |
| Aucun signal négatif | défaut couche (obsidure→REQUEST_TEST, obsidienne→REQUEST_PROOF, audit→CHECK_INVARIANT, kernel/memory→REQUEST_TRACE, domains→REQUEST_CONTEXT, sinon CONTINUE) |

Tous les verbes passent par `assert_output_allowed()` : ACT/ALLOW/BLOCK/HOLD
lèvent une exception. `HOLD_RECOMMENDED` reste une recommandation terminale ;
le HOLD souverain est exclusivement `X108Gate.HOLD` (KX108_ONLY).

## Sortie

Champs ajoutés au receipt terminal : `guidance`, `guidance_reasons`,
`guidance_authority: "NONE"`, `guidance_note`. Pour la couche sigma,
un bloc `sigma` complet (file_signals + live_signals) est retourné en EXECUTE.
