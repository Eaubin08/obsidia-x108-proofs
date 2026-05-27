from pathlib import Path


def read_any(path: str) -> str:
    p = Path(path)
    raw = p.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "cp1252", "cp850"):
        try:
            txt = raw.decode(enc)
            if "BRODY" in txt or "DOMAIN_RACCORD" in txt or "KX108_ONLY" in txt:
                return txt
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace")


write_txt = read_any("docs/runtime/F12C_TERMINAL_WRITE_BOUNDARY_LIVE.txt")
mut_txt = read_any("docs/runtime/F12C_TERMINAL_MUTATION_BOUNDARY_LIVE.txt")

checks = {
    "write_has_domain_boundary": "DOMAIN_RACCORD_BOUNDARY" in write_txt,
    "write_has_memory_write_canon_freeze": "MEMORY_WRITE_CANON_FREEZE" in write_txt,
    "write_has_write_boundary_required_true": "write_boundary_required=true" in write_txt,
    "mutation_has_action_mutation_boundary": "ACTION_MUTATION_BOUNDARY" in mut_txt,
    "mutation_keeps_kx108": "KX108_ONLY" in mut_txt,
    "mutation_no_act": "emits_act=false" in mut_txt,
    "both_terminal_ok": "BRODY_TERMINAL_NATIVE_ONCE_OK" in write_txt and "BRODY_TERMINAL_NATIVE_ONCE_OK" in mut_txt,
}

for k, v in checks.items():
    print(f"{k}={v}")

if not all(checks.values()):
    raise SystemExit("F12C_TERMINAL_MARKERS_FAIL")

print("F12C_TERMINAL_MARKERS_PASS")
