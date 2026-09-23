# X108_NO_BYPASS_RULE

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/x108_ingress/readonly_context_ingress.py` (assert_readonly())
- `periphery/reverse_os/action_projection_readonly.py` (_FORBIDDEN_TOKENS)
- `periphery/context/context_packet_builder_v2.py` (_FORBIDDEN_TOKENS)

Source Status: RUNTIME_CODE

Scope: Interdire tout bypass de X108 — y compris via forbidden tokens.

Allowed:
- "assert_readonly() lève AssertionError si can_emit_act=True"
- "Les forbidden tokens ALLOW/HOLD/BLOCK/ACT/DECIDE/VERDICT sont détectés et bloqués"

Forbidden:
- Tout composant utilisant ALLOW/HOLD/BLOCK/ACT dans son output sans passer par X108
- Tout bypass silencieux de assert_readonly()

Inputs: Tout output de composant périphérique
Outputs: Validation de non-bypass

Metrics: N/A

Invariants:
- `_FORBIDDEN_TOKENS = {"ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT", "AUTHORIZE", "APPROVE", "EXECUTE", "DEPLOY"}`
- Ces tokens ne peuvent pas apparaître dans un output périphérique sans X108

X108 Boundary: KX108_ONLY — le seul qui peut émettre ces tokens légitimement
Tests Required: test_no_forbidden_token_in_peripheral_output
Proof Expected: Python test
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: N/A
Open Questions: Aucune — règle absolue
