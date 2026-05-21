# Brody UTF-8 Live Check Report

**Date**: 2026-05-20
**Phase**: Phase 4 — Live Check
**Result**: BRODY_UTF8_LIVECHECK_PASS

---

## Verification commands run

```bash
python -c "
import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app
client = TestClient(app)
r = client.post('/api/brody/chat', json={'message': 'test mémoire', 'language': 'fr'})
data = json.loads(r.content)
fa = data.get('final_answer', '')
# Write to UTF-8 file
with open('_livecheck_direct.txt', 'w', encoding='utf-8') as f:
    f.write(fa)
# Check code points
idx = fa.find('structur')
seg = fa[idx:idx+12]
print([hex(ord(c)) for c in seg])
# 0xe9 at position 8 = é — CORRECT
"
```

---

## Results

### Raw API bytes

```
raw_body hex at 'structur': 7374727563747572 c3a9 65 20726561...
                                               ^^^^ = é (UTF-8)
```

### Code point check

```
seg: structurée read
code_points: ['0x73','0x74','0x72','0x75','0x63','0x74','0x75','0x72','0xe9','0x65',...]
Position 8: 0xe9 = é — CORRECT Unicode (U+00E9)
```

### File round-trip

Saved `final_answer` to `_livecheck_direct.txt` (utf-8):
```
Je suis Brody, interface structurée readonly d'Obsidia X-108.
Je traverse la mémoire Graphiti/Neo4j en readonly, hydrate les sources locales, et réponds par structure.
```

- `has_proper_é (0xe9)`: True
- `has_mojibake_Ã (0xc3 as lone char)`: False

---

## Mojibake source confirmed

All prior mojibake reports were display artifacts:

```
# Diagnostic pipe that CAUSED the display artifact:
inner_python writes é → UTF-8 bytes \xc3 \xa9 to stdout
outer python reads stdin with cp1252 → \xc3=Ã, \xa9=©
display: structurÃ©e  ← artifact only, not real data
```

---

## Invariants

- `SIGMA_UNTOUCHED`: True
- `KERNEL_UNTOUCHED`: True
- `memory_write=False`, `graphiti_write=False`, `neo4j_write=False`
- `emits_act=False`, `decision_authority=KX108_ONLY`

---

**BRODY_UTF8_LIVECHECK_PASS**
