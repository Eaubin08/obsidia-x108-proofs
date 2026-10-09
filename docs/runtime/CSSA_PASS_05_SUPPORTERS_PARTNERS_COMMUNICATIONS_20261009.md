# CSSA — Passe 05/10 : supporters, partenaires et communication

2026-10-09. CSSA-only branch `feat/cssa-v01-active`. Reuses historical F3H-E read-only mail router contract; no duplicate native CRM writer. No merge on main.

## Integrated package

`periphery/cssa_supporters_partners_communications_pass5_v0.py` covers 11 case types: match information, marketing, ticket confirmations, subscriptions, supporter requests, partner invitations, partner delivery, sponsor contracts, institutional messages, operational requests and refund requests.

It separates personal spectator ticket/subscription messages from club-internal tasks; only explicitly scoped synthetic operational observations can be **candidates** for CRM work. Public communications, sales campaigns, fan inbox transactions and real operational authority are separate classes. Each communication retains provenance, channel, audience, a draft when content exists, reviewer and explicit legal basis/recipient checks. Missing approvals, lawful-basis verification, recipients or actor permission causes HOLD; contradictions cause BLOCK. Sending email, posting to social media, creating CRM state, and implicit consent are forbidden.

Related historical sources: F3H-E `organizations/cssa/intake/readonly_router_v0.py` with `CLASS_MATCHDAY_INFORMATION`, `CLASS_MARKETING_COMMUNICATION`, `CLASS_TICKETING_TRANSACTION`, `CLASS_OPERATIONAL_ACTION_REQUEST` and associated read-only routes; CSSA operating map COMMUNICATION, PARTNERS_COMMERCIAL, SUPPORTERS_TICKETING. This pass complements their workflow, not a replacement for historical message classification.

## Tests

`tests/test_cssa_supporters_partners_communications_pass5_v0.py` adds 20 local deterministic tests, covering the 11 types, personal ticket and subscription distinctions, public-source vs operational scope, authorized-shape work candidates without a write, contradiction, evidence omission, complete synthetic campaign, duplicate case rejection, and a rejected real-send flag.

Last user-confirmed baseline: 220 passed, 1 skipped, clean Git. New expected scoped total: 240 passed, 1 skipped (subject to execution). No claim of fresh validation until the Windows run.

```powershell
Set-Location (Join-Path $env:TEMP 'cssa-eol-final')
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter 'test_cssa_*.py' -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

## Acceptance claim and next boundary

Upon passing, PASS05_CLOSED_SIMULATION (supporters/partners/comms). No real CSSA mailing list, transactional mailbox, identity, partner contract, permission, sender domain, or delivery was verified. The CRM candidate flag means eligibility for human review, not a committed CRM task. Pass 06/10 will test cross-lot A+B campaign and is the planned final Lot B closure. No additional pass.