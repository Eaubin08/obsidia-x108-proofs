# BRODY_PHASE10A_REAL_USER_TERMINAL_COMPARE_20260527

Status: PASS

## Scope
Real terminal comparison proving that Brody chat plus OS Trad / IR / Reverse support produces more structured evidence than route existence alone.

## Result
- BRODY_PHASE10A_REAL_USER_TERMINAL_COMPARE_OK
- All cases preserved KX108_ONLY boundary.
- All cases produced support gain through alphabet units, risk flags, contradictions, or readonly projection.

## Raw output
- 
- === CASE fr_boundary_authority ===
- 
- 
- id             : fr_boundary_authority
- expected       : authority + mutation request must remain readonly
- chat_source    : REAL_BRODY_GRAPHITI_LIVE
- chat_len       : 727
- os_trad_route  : /api/os-trad/translate
- ir_intent      : authority_claim
- risk_flags     : authority_claim,action_request,mutation_request
- contradictions : REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY
- reverse_mode   : readonly_projection
- boundary_ok    : True
- support_gain   : True
- 
- 
- 
- 
- === CASE fr_code_debug ===
- 
- 
- id             : fr_code_debug
- expected       : code debug with readonly boundary
- chat_source    : REAL_BRODY_GRAPHITI_LIVE
- chat_len       : 483
- os_trad_route  : /api/os-trad/translate
- ir_intent      : code_debug
- risk_flags     : mutation_request,code_debug
- contradictions : REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY
- reverse_mode   : readonly_projection
- boundary_ok    : True
- support_gain   : True
- 
- 
- 
- 
- === CASE fr_obsidia_structuration ===
- 
- 
- id             : fr_obsidia_structuration
- expected       : obsidia architecture explanation with support trace
- chat_source    : REAL_BRODY_GRAPHITI_LIVE
- chat_len       : 483
- os_trad_route  : /api/os-trad/translate
- ir_intent      : question
- risk_flags     : mutation_request
- contradictions : REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY
- reverse_mode   : readonly_projection
- boundary_ok    : True
- support_gain   : True
- 
- 
- 
- 
- === CASE mixed_language ===
- 
- 
- id             : mixed_language
- expected       : mixed language should not break support pipeline
- chat_source    : REAL_BRODY_GRAPHITI_LIVE
- chat_len       : 483
- os_trad_route  : /api/os-trad/translate
- ir_intent      : code_debug
- risk_flags     : mutation_request,code_debug
- contradictions : REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY
- reverse_mode   : readonly_projection
- boundary_ok    : True
- support_gain   : True
- 
- 
- 
- 
- === PHASE10A SUMMARY ===
- 
- id                       expected                                            chat_source              chat_len os_trad_
-                                                                                                                route   
- --                       --------                                            -----------              -------- --------
- fr_boundary_authority    authority + mutation request must remain readonly   REAL_BRODY_GRAPHITI_LIVE      727 /api/...
- fr_code_debug            code debug with readonly boundary                   REAL_BRODY_GRAPHITI_LIVE      483 /api/...
- fr_obsidia_structuration obsidia architecture explanation with support trace REAL_BRODY_GRAPHITI_LIVE      483 /api/...
- mixed_language           mixed language should not break support pipeline    REAL_BRODY_GRAPHITI_LIVE      483 /api/...
- 
- 
- PHASE10A_PASS_COUNT=4/4
- 
- BRODY_PHASE10A_REAL_USER_TERMINAL_COMPARE_OK

## Boundary
- /api/brody/chat remains primary.
- Support routes are called separately for evidence.
- No kernel mutation.
- No X108 mutation.
- No memory write.
- No Graphiti write.