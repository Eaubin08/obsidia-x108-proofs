# COGNITIVE_TO_CONTEXTPACKET_MAP

Status: SPEC_ONLY  
Boundary: COGNITIVE_REINTEGRATION_ADVISORY_ONLY  

| Cognitive source object | Contract target | Allowed use | Forbidden use | Failure mode |
|---|---|---|---|---|
| reasoning component | ContextPacket | advisory context enrichment | final decision | fail_closed |
| agent description | ContextPacket | non-executable description | autonomous runtime agent | fail_closed |
| metric description | PeripheralSignalPacket | advisory signal candidate | score authority | fail_closed |
| world_action_candidate | IntentEnvelope candidate only | requires X108 review | direct ACT | fail_closed |
| AutoForge note | ContextPacket | future design context | kernel mutation | fail_closed |
| consciousness note | ContextPacket | philosophical/spec context | consciousness proof claim | fail_closed |
| educational reconstruction | ContextPacket | learning path candidate | student diagnosis | fail_closed |
| cognitive reduction | PeripheralSignalPacket | reduction quality signal | decision override | fail_closed |
| memory relation | ContextPacket | readonly context | memory write | fail_closed |
| agent orchestration note | ContextPacket | architecture advisory | agent authority | fail_closed |

Rule:

Cognitive material can enrich context.  
Cognitive material cannot decide.  
Cognitive material cannot act.  
Critical adaptation must pass through IntentEnvelope → X108 → DecisionTicket.