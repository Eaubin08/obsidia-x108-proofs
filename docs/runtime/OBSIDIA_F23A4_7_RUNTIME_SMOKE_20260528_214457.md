# OBSIDIA F23A4.7 — RUNTIME SMOKE

Mode: RUNTIME_SMOKE_NO_PATCH  
Patch: NO  
Commit: NO  
Tag: NO  
Freeze: NO  

## Ports

- 8000 — Brody API main runtime
- 8012 — Brody API second runtime

## Results

``json
[
    {
        "port":  8000,
        "case":  "bank",
        "ok":  true,
        "domain":  "bank",
        "x108_gate":  "ALLOW",
        "decision_authority":  "KX108_ONLY",
        "emits_act":  false,
        "readonly":  true,
        "status":  "PASS"
    },
    {
        "port":  8000,
        "case":  "trading",
        "ok":  true,
        "domain":  "trading",
        "x108_gate":  "ALLOW",
        "decision_authority":  "KX108_ONLY",
        "emits_act":  false,
        "readonly":  true,
        "status":  "PASS"
    },
    {
        "port":  8000,
        "case":  "gps",
        "ok":  true,
        "domain":  "gps_defense_aviation",
        "x108_gate":  "ALLOW",
        "decision_authority":  "KX108_ONLY",
        "emits_act":  false,
        "readonly":  true,
        "status":  "PASS"
    },
    {
        "port":  8012,
        "case":  "bank",
        "ok":  true,
        "domain":  "bank",
        "x108_gate":  "ALLOW",
        "decision_authority":  "KX108_ONLY",
        "emits_act":  false,
        "readonly":  true,
        "status":  "PASS"
    },
    {
        "port":  8012,
        "case":  "trading",
        "ok":  true,
        "domain":  "trading",
        "x108_gate":  "ALLOW",
        "decision_authority":  "KX108_ONLY",
        "emits_act":  false,
        "readonly":  true,
        "status":  "PASS"
    },
    {
        "port":  8012,
        "case":  "gps",
        "ok":  true,
        "domain":  "gps_defense_aviation",
        "x108_gate":  "ALLOW",
        "decision_authority":  "KX108_ONLY",
        "emits_act":  false,
        "readonly":  true,
        "status":  "PASS"
    }
]
Boundary expected
decision_authority=KX108_ONLY
readonly=true
emits_act=false
Next

F23A4.8_CONNECTORS_ALIGNMENT
