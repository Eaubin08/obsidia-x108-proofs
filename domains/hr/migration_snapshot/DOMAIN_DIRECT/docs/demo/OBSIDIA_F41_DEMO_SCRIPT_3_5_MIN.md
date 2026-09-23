# Obsidia X-108 — Oral Demo Script (3–5 minutes)

**Mode:** READONLY · KX108_ONLY · emits_act=false  
**Date:** 2026-05-29  
**Format:** Oral presentation with live terminal. One speaker. One screen.

---

## Pre-flight (before the audience arrives)

- [ ] Terminal open at project root
- [ ] Server NOT yet started (you'll start it live)
- [ ] Browser tab ready (blank)
- [ ] `docs/demo/OBSIDIA_F40_OPERATOR_RELEASE_CANDIDATE_CHECKLIST.md` open as backup

---

## Beat 1 — Hook (0:00–0:30)

> "Every AI system you've seen today tells you it won't make decisions on its own.
> I'm going to show you one where you can verify that claim yourself — live, right now, with a command you can run at home."

**[pause]**

> "The question we're answering is not 'does the AI behave well?' — it's 'can you prove the AI isn't the decision authority?' Those are very different questions."

---

## Beat 2 — Problem (0:30–1:00)

> "Current AI guardrails are behavioral constraints — prompts, fine-tuning, filters. They work until they don't. When they fail, there's no proof they were ever there.
>
> Regulators don't want promises. They want audit trails. SHA256-signed artifacts. Verifiable tests. A boundary you can inspect."

---

## Beat 3 — Start the server (1:00–1:30)

**[type in terminal]**

```powershell
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
```

> "That's a real FastAPI server. We're going to call it right now."

**[wait for `Uvicorn running on http://127.0.0.1:8011`]**

> "Good. The server is up."

---

## Beat 4 — The money call (1:30–2:30)

**[open new terminal tab, type]**

```powershell
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f38/multi-domain-scenarios" `
  -Method POST -Body "{}" -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object packet_id, global_status, scenario_count, all_mutations_false, forbidden_tokens_found
```

**[show output]**

> "Four domains — bank, GPS-defense-aviation, trading, unknown refusal — in a single packet.
> Look at these fields: `global_status=READY_READONLY`, `all_mutations_false=True`, `forbidden_tokens_found=False`.
> That means the system consulted its runtime surfaces, built an advisory response, and never once tried to decide anything."

**[show one scenario]**

```powershell
$resp.scenarios | Select-Object domain, status, can_decide, surfaces_ready
```

> "`can_decide=False` in every domain. 7 runtime surfaces consulted. This is the boundary."

---

## Beat 5 — The boundary (2:30–3:00)

> "Every response from this system carries a BOUNDARY dictionary — 15 flags. Here's what matters:
>
> `decision_authority = KX108_ONLY`
>
> Brody, the advisory AI, doesn't decide. The kernel decides. Brody observes, aggregates, and reports — nothing more.
> This isn't a setting you can accidentally turn off. It's enforced at three independent layers: the Python module, the API route, and the response text."

---

## Beat 6 — The proof chain (3:00–3:30)

> "This demo is backed by a verifiable proof chain.
>
> 103 unit tests — all passing.
> 474 smoke checks across 6 scripts.
> 3 live-server proofs with SHA256 signatures — generated on a real uvicorn server, not mocked.
> 10 git tags, one per palier, F32 through F39.
>
> Every one of those artifacts is in the repository. You can verify them independently."

**[optional: open browser]**

```powershell
Start-Process "http://127.0.0.1:8011/api/periphery/operator/runtime-panel.html"
```

> "This is the operator dashboard. `READY_READONLY`. `KX108_ONLY`. Live."

---

## Beat 7 — Close (3:30–4:00)

> "What we've shown: an AI component that consults multiple information sources, generates multi-domain advisory responses, and provably never crosses the line into decision-making.
>
> Not because we told it not to.
> Because the architecture makes it impossible.
>
> That's what Obsidia X-108 is."

**[pause]**

> "Questions?"

---

## Backup commands (if demo fails)

```powershell
# If server won't start — run tests offline:
python -m pytest tests\api\ -q
# Expected: 103 passed

# If port 8011 occupied:
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 9010

# Direct module call (no server needed):
python scripts\smoke_f37_multi_domain_user_scenarios_readonly.py
# Expected: F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_STATUS=PASS · CHECKS=139/139
```

---

## Timing guide

| Beat | Content | Target time |
|------|---------|-------------|
| 1 | Hook | 0:30 |
| 2 | Problem | 0:30 |
| 3 | Server start | 0:30 |
| 4 | Live call + result | 1:00 |
| 5 | Boundary explanation | 0:30 |
| 6 | Proof chain | 0:30 |
| 7 | Close | 0:30 |
| **Total** | | **~4:00** |

---

*F41 RC1 · Oral Demo Script · READONLY · KX108_ONLY · Generated 2026-05-29*
