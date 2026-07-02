# OBSIDIA TERMINAL RECEIPT V0 — spécification

Statut : format tracké, log vivant NON tracké.

Le fichier vivant est écrit par `scripts/obsidia_cli.py` en append-only dans :

```
.local_obsidia/receipts/obsidia_terminal_receipts.jsonl
```

Ce chemin suit la convention `.local_*` du repo : artefact runtime local,
hors git, hors `MANIFEST_SHA256.json`, hors seal Merkle, hors freeze.
Ne jamais le tracker, ne jamais le manifester, ne jamais le sceller.

## Nature

- `receipt_type: terminal_non_sovereign`
- Un receipt terminal n'est PAS un ticket souverain (`audit/sovereign_tickets.jsonl`),
  PAS une entrée `world_action_bus.jsonl`, PAS une décision X108.
- Chaque ligne porte en dur : `authority: "NONE"`, `sovereign: false`,
  `gate_emitted: null`, `decision_authority: "KX108_ONLY"`.

## Format (une ligne JSON par invocation)

```json
{
  "receipt_type": "terminal_non_sovereign",
  "authority": "NONE",
  "sovereign": false,
  "gate_emitted": null,
  "decision_authority": "KX108_ONLY",
  "ts": "2026-07-02T00:00:00+00:00",
  "raw": "statut du kernel",
  "normalized_intent": "statut du kernel",
  "detected_layer": "live",
  "confidence": 0.7,
  "mode": "status",
  "route_reason": ["trigger 'statut' -> live"],
  "output": "EXECUTE | COMMANDS | GUIDE | POLICY_DENY | STOP_UNKNOWN",
  "guidance": "un verbe de GUIDANCE_ACTIONS (jamais ACT/ALLOW/BLOCK/HOLD)",
  "commands": ["..."],
  "doctor": {}
}
```

## Vocabulaire

Défini dans `scripts/obsidia_guidance_vocabulary.py`.
`HOLD_RECOMMENDED` est une recommandation terminale ; le HOLD souverain
reste exclusivement `X108Gate.HOLD`. `POLICY_DENY` est un refus local
de policy terminal ; le BLOCK souverain reste exclusivement X108.
