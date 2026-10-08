# V0.1 C2.8 — Original approval ↔ canonical decision ↔ ticket

Status: DRAFT / NO EGRESS. Parent C2.7 HEAD `650c1539e58823688b339fa9e20fd072516ce105`; targeted C2.7 run 37727049876 SUCCESS.

The source chain `obsidia_world_action_pre_execution_context_v0.py` validates exact request and hashed approval, but does not authenticate the approver's legal authority. C2.7 verifies an existing KX108 WORLD_ACTION_PRE_EXECUTION record against the original request and approval fields. `periphery/world_calls/sovereign_ticket.py` is locally constructible and has no cryptographically authenticated binding to the specific canonical KX108 decision record hash.

C2.8 checks original request/approval using existing verifiers, the canonical stored KX108 record through CG62/CG53, and ticket action, scope, time, and gate. Even after every structural check succeeds it returns `BLOCK:C28_TICKET_NOT_AUTHENTICATED_TO_KX108_RECORD`. A locally created SovereignTicket is not treated as trusted execution authority.

Remaining: independently verified human/organization consent and identity, authenticated ticket issuance bound to canonical decision-record hash/action/scope, durable revocation and dispatch fencing, no live provider until evidence complete. No main, kernel or Monde mutations.
