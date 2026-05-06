from pathlib import Path

p = Path("sigma/contracts.py")
text = p.read_text(encoding="utf-8")

text = text.replace(
    "# after GuardX108 has produced x108_gate.",
    "# after GuardX108 has produced the sovereign gate."
)

p.write_text(text, encoding="utf-8", newline="\n")
print("[OK] Removed x108_gate token from DomainAggregate comment")
