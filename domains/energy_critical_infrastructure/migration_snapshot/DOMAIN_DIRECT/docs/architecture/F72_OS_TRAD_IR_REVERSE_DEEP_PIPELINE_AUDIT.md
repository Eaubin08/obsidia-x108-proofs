# F72 ? OS Trad / IR / Reverse Deep Pipeline Audit

- Status: PASS_AUDIT_READY
- Mode: AUDIT_ONLY
- Build performed: false
- Patch performed: false
- Decision authority: KX108_ONLY
- Readonly: true
- Allowed to decide: false
- Emits ACT: false
- Emits verdict: false
- Memory/Graphiti/Neo4j write: false

## Files checked

- `apps/obsidia_api/routes/os_trad_ir_reverse.py` ? OK ? parse `True` ? sha256 `0c1e0023833ee4ab88981c93b754681a76249bd2aad3c417f0368b486d7ed838`
- `apps/obsidia_api/brody_existing_reverse_os_bridge.py` ? OK ? parse `True` ? sha256 `d3c13a0d53f46afb0ce1d8c8d5cc6c5991344daa071741ab333c135810240671`
- `periphery/reverse_os/action_projection_readonly.py` ? OK ? parse `True` ? sha256 `742f9a9973a27a46ed88d0f30fdf8e7cf25aa859061ff49e81a3e64161a8073c`
- `periphery/reverse_os/audience_projection.py` ? OK ? parse `True` ? sha256 `db7c5df2e5a8aea19fee31644777ac14775c767fa8e5bcb723ed0d225decbb80`
- `apps/obsidia_api/routes/translation.py` ? OK ? parse `True` ? sha256 `03ad8fa404ba61c5f9f87cc95c1191dc166abe5c10e7eb2ccb2f66874b67a6a2`
- `tests/api/test_brody_os_trad_ir_reverse_discovery.py` ? OK ? parse `True` ? sha256 `10774d04ae4e7e3a7bf215932599a118d7ca4e6537545acd235ef7e2921b966b`
- `sigma/packets.py` ? OK ? parse `True` ? sha256 `3b774de869af5dd4f353921108db9db2ae874c352dbb36d02b40e923603d7e2d`
- `sigma/orchestrator_preview.py` ? OK ? parse `True` ? sha256 `d94a955220fda76b65a1b93a5fa148f3a73bb94baf191a8188b89bdde77c785b`

## Routes detected

- `apps/obsidia_api/routes/os_trad_ir_reverse.py` ? `router.post('/api/os-trad/translate')` ? `os_trad_translate`
- `apps/obsidia_api/routes/os_trad_ir_reverse.py` ? `router.post('/api/ir/candidate')` ? `ir_candidate`
- `apps/obsidia_api/routes/os_trad_ir_reverse.py` ? `router.post('/api/os-reverse/project')` ? `os_reverse_project`
- `apps/obsidia_api/routes/translation.py` ? `router.post('/trace')` ? `translation_trace`

## Recommended readonly pipeline

- `input`
- `os_trad_translate`
- `ir_candidate`
- `reverse_projection`
- `audience_projection`
- `readonly_response`

## Risk flags

- `IR_REVERSE_SURFACE_WITHOUT_READONLY_WORD_REVIEW_REQUIRED` ? `periphery/reverse_os/audience_projection.py`

## Recommended next build

- File: `sigma/ir_reverse_readonly_bridge.py`
- Test: `tests/sigma/test_f72_ir_reverse_readonly_bridge.py`
- Purpose: Sigma packet ? IR/reverse/audience projection context
- Boundary: no decision, no ACT, no verdict, no mutation, no memory write

## Next

F72_BUILD_OR_F73_ADVERSARIAL_HARDENING
