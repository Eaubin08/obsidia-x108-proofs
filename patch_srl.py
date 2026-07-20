import pathlib

file_path = pathlib.Path('scripts/f_srl_session_registry_layer_audit_v0.py')
content = file_path.read_text(encoding='utf-8')

old_read = 'text = read_text_safe(path)'
new_read = 'text = read_text_safe(path)\n        lines = text.splitlines()'

old_loop = 'for match in rx.finditer(text):'
new_loop = r"""for match in rx.finditer(text):
                line_no = text.count("\n", 0, match.start())
                line_txt = lines[line_no] if line_no < len(lines) else ""
                if "violations.append" in line_txt or line_txt.strip().startswith(("'", '"', "#")):
                    continue"""

if "lines = text.splitlines()" not in content:
    content = content.replace(old_read, new_read)

if "violations.append" not in content:
    content = content.replace(old_loop, new_loop)

file_path.write_text(content, encoding='utf-8')
print("✅ Faux positifs filtrés proprement dans le scanner SRL.")
