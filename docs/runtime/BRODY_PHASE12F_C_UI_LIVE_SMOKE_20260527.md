# BRODY_PHASE12F_C_UI_LIVE_SMOKE_20260527

Status: VISUAL_PASS

## Scope

Validate live UI parity after Phase 12F-B RightPanel patch.

## Automated precheck

- port 5173 live
- port 8012 live
- RightPanel static parity OK
- API payload parity OK

## Manual visual proof

Fresh live prompt used:

je suis perdu et ça me saoule, dis-moi froidement ce qui est branché et ce qui ne l'est pas

## Observed UI sections

- True Voice / LLM Obsidien
- Domain Raccord / Structure-First
- 12E6 Boundary Envelope
- Native Machination
- Contracts / Permission Matrix
- Native Boundary
- Live Backend — Last Response
- Context Packet — Live

## Observed payload

- voice_source=DOMAIN_RACCORD_STRUCTURAL
- final_answer_source=DOMAIN_RACCORD_STRUCTURAL
- domain_voice_mode=DOMAIN_RACCORD_STRUCTURAL
- domains=FRICTION
- graphiti_status=GRAPHITI_LIVE_READONLY_PASS
- neo4j_status=LIVE_READONLY
- readonly=true
- advisory_only=true
- context_signal_only=true
- allowed_to_decide=false
- allowed_to_act=false
- emits_act=false
- emits_verdict=false
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY

## Decision

Brody UI / RightPanel parity with terminal/API 12E6 is visually validated.

12F-C is passed.

## Boundary

UI only.
No backend change.
No memory write.
No Graphiti write.
No kernel mutation.
No X108 mutation.
