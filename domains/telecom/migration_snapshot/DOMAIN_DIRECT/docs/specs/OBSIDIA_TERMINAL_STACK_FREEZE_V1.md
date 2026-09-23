# OBSIDIA_TERMINAL_STACK_FREEZE_V1

## 0. Identité du freeze

- Nom : `OBSIDIA_TERMINAL_STACK_FREEZE_V1`
- Branche : `feat/path-brody-r02-thermo-mcp-closure`
- Date : 2026-07-02
- Type : **freeze documentaire**. Ce document n'est PAS un seal, PAS un
  manifest, PAS une ancre cryptographique. Il fige un état de référence,
  pas une preuve. Aucun répertoire freeze/manifest/seal n'est créé ni
  modifié par ce document. Le hash du commit portant ce freeze n'est pas
  inscrit ici : il vivra dans Git après commit.

## 1. Ligne de commits terminal

```
99c7270 feat(terminal): add non-sovereign obsidia CLI cockpit v0
db5e962 feat(terminal): add sigma guidance calibration
4ba26c4 feat(terminal): multi-source fresh signal with staleness rules for sigma guidance
71ed7e9 feat(terminal): align registry with observed live stack v1
484adb1 feat(terminal): add interactive shell v1
```

Fichiers portés par cette ligne : `scripts/obsidia_cli.py`,
`scripts/obsidia_registry.yaml`, `scripts/obsidia_guidance_vocabulary.py`,
`scripts/obsidia_sigma_guidance.py`, `scripts/obsidia.ps1`,
`docs/specs/OBSIDIA_TERMINAL_RECEIPT_V0.md`,
`docs/specs/OBSIDIA_SIGMA_GUIDANCE_V0.md`.

## 2. Ligne protocols / gates

```
1bc94e8 docs(obsidia): add core build protocols v0
1ba3f9b docs(obsidia): add specialized build protocols v0
064e3d6 feat(obsidia): add minimal build gates v0
```

Livrés : 7 protocols (`docs/protocols/`), 3 gates + 3 tests
(`scripts/gates/`, `tests/gates/`), 29 tests passed. Le gate
`obsidia_sigma_non_sovereignty_check` protège l'invariant de
non-souveraineté dont dépend le terminal.

## 3. Observations runtime (instantané, pas une garantie)

Source : observation PowerShell locale utilisateur. Ces statuts sont un
instantané daté, pas un engagement permanent.

```
doctor:
  sigma_domains           UP
  sigma_evaluate          UP
  graphiti_frozen_status  UP
  ui                      UP
  kernel_unconfirmed      DOWN / NOT_CONFIRMED

sigma coherence: CONTINUE

domains: bank, trading, ecom, gps_defense_aviation — bridge-only

memory: Graphiti frozen readonly status (8011 /graph/v20/frozen/status)

brody: vit dans l'API 8000 via /api/brody/* (pas de serveur séparé)

adapters: /api/live/kernel/adapters/{bank,trading,gps}
          POST_ONLY_ADAPTERS — jamais sondés en GET par doctor
```

## 4. Doctrine d'autorité

```
Le terminal guide et observe, uniquement.
X108 décide.
Sigma guide.
Brody explique.
Obsidure construit des proposals.
Domains bridge-only.
Memory readonly.
Aucun ALLOW/BLOCK/HOLD/ACT émis par le terminal.
HOLD_RECOMMENDED est une guidance, rien d'autre.
```

Enforcement (où la doctrine est verrouillée, pas seulement énoncée) :
`FORBIDDEN_TERMINAL_ACTIONS` et `assert_output_allowed()` dans
`scripts/obsidia_guidance_vocabulary.py` (exception levée sur mot
interdit) ; gate `scripts/gates/obsidia_sigma_non_sovereignty_check.py` ;
suite `tests/gates/` (29 tests).

## 5. Sorties terminal autorisées

```
EXECUTE      — HTTP GET readonly uniquement (doctor/status/sigma)
COMMANDS     — affiche les commandes exactes, ne les lance jamais
GUIDE        — orientation quand la demande est floue mais routable
POLICY_DENY  — refus local de policy (PAS un BLOCK souverain)
STOP_UNKNOWN — intention non reconnue, arrêt et demande de contexte
```

## 6. Verbes de guidance

```
CONTINUE, SLOW_DOWN, RELAUNCH_LAYER, REQUEST_CONTEXT, REQUEST_TRACE,
REQUEST_REPLAY, REQUEST_TEST, REQUEST_PROOF, CHECK_INVARIANT,
STOP_UNKNOWN, HOLD_RECOMMENDED
```

`HOLD_RECOMMENDED` n'est pas `X108Gate.HOLD`. `POLICY_DENY` n'est pas un
BLOCK souverain. Le HOLD/BLOCK souverain reste exclusivement X108
(`decision_authority = KX108_ONLY`).

## 7. Commande globale (manuelle)

Fonction de profil PowerShell, validée manuellement :

```powershell
function obsidia { & "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\scripts\obsidia.ps1" @args }
```

Statut : manuel uniquement. Aucun fichier repo. Aucune mutation PATH.
Aucun installeur. Aucune autorité nouvelle — pur alias ergonomique vers
`scripts/obsidia.ps1`. Si le repo est déplacé : erreur "path not found",
correction = rééditer la ligne dans `$PROFILE`.

## 8. Shell interactif

`obsidia` (via la fonction de profil) ou `.\scripts\obsidia.ps1` sans
argument ouvre le shell `obsidia>`.

```
help / ?     — aide locale (registry + doctrine), commande interne
clear        — effacement ANSI pur, commande interne, état intact
exit / quit  — seules sorties du shell
session_id   — uniquement sur les IN interactifs traités
help/clear/exit n'écrivent aucun receipt
EOF / Ctrl+C — sortie propre, jamais de traceback
one-shot     — comportement inchangé (obsidia doctor, obsidia "<IN>")
```

Le shell est une boucle autour du pipeline `handle()` existant : aucun
pouvoir nouveau, aucun subprocess, mêmes receipts.

## 9. Frontière Obsidure

```
obsidure status / proposal / lance  -> COMMANDS uniquement (jamais EXECUTE)
apply / commit (demandes de mutation) -> POLICY_DENY + HOLD_RECOMMENDED
Le terminal n'exécute jamais scripts/run_agent_obsidure.ps1.
Aucun chemin subprocess n'existe dans le CLI (par construction).
_PATCH_PROPOSALS/ observé en lecture seule — 537 proposals constatés
lors de l'audit OBSIDURE_TERMINAL_COMMANDS_ONLY_AUDIT_V1, zéro touché.
```

## 10. Backlog restant

- `kernel /health` 3001 à confirmer lors d'une prochaine observation live.
- Archive optionnelle de rapports d'observation runtime sous
  `.local_obsidia/reports/` (local, non tracké, non souverain — comme les
  receipts ; aucun contenu de receipt n'est reproduit dans ce document).
- Script installeur différé (la fonction de profil suffit).
- Intégration optionnelle des 3 gates dans `scripts/run_ci_local.ps1`.
- Gates futurs : `lean_manifest_guard`, `forbidden_write_check`,
  `secret_scan` local, `quality_gate` orchestrateur.
