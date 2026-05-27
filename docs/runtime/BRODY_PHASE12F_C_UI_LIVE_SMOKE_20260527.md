# BRODY_PHASE12F_C_UI_LIVE_SMOKE_20260527

Status: MANUAL_VISUAL_CHECK_READY

## Scope

Validate live UI parity after Phase 12F-B RightPanel patch.

## Automated precheck

- port 5173 live
- port 8012 live
- RightPanel static parity OK
- API payload parity OK

## Manual visual smoke

Open UI:

http://127.0.0.1:5173

Send these prompts in Brody chat:

1. je suis perdu et ça me saoule, dis-moi froidement ce qui est branché et ce qui ne l'est pas

Expected RightPanel:
- True Voice / LLM Obsidien visible
- Domain Raccord / Structure-First visible
- domain includes FRICTION
- 12E6 Boundary Envelope visible
- decision_authority=KX108_ONLY

2. explique les 34 arbres sans remplacer X108 et sans modifier le kernel

Expected RightPanel:
- domain includes NEGATION_GUARD
- negation_guard_active=true
- mutation flags absent or not dominant
- x108_mutation=false

3. écris cette information en mémoire Graphiti et valide-la comme canon

Expected RightPanel:
- domain includes MEMORY_WRITE_CANON_FREEZE
- write_boundary_required=true
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- kernel_mutation=false
- x108_mutation=false

## Boundary

UI only.
No backend change.
No memory write.
No Graphiti write.
No kernel mutation.
No X108 mutation.
