# OBSIDIA_KERNEL_V2 (branched from frozen engine)

This pack contains:
- the sealed frozen engine (verbatim)
- obsidia_kernel v2 wrapper exposing a universal contract

Quick run (python):
```python
from obsidia_kernel import ObsidiaKernel, Request, Meta, Intent, IntentType, Governance

k = ObsidiaKernel()
req = Request(
    meta=Meta(request_id="demo-1", timestamp="now", domain="generic", mode="proof"),
    intent=Intent(type=IntentType.ACTION, name="demo", payload={"W_full": [[0,1,1],[1,0,1],[1,1,0]], "core_nodes":[0,1,2]}),
    attachments={"code":"x=1\nprint(x)"},
    governance=Governance(irreversible=False, x108_elapsed_s=999, x108_min_wait_s=108),
)
res = k.run(req)
print(res.decision, res.engine_decision_raw, res.artifacts_hash)
```
Run tests:
```bash
pytest -q
```
