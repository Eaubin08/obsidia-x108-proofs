
from __future__ import annotations
import subprocess, sys
from pathlib import Path
from typing import Dict, Any

from obsidia_os1.parse_input import parse_input, parse_project
from obsidia_os0.contract import validate
from obsidia_os0.sandbox import Sandbox
from proof.codegen import generate_python, generate_js, generate_project_python, generate_project_js

class Refusal(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason

def safe_parse(text: str, fname: str | None = None):
    try:
        return parse_input({'text': text})
    except Exception as e:
        loc = f":file={fname}" if fname else ""
        raise Refusal('REFUSE_PARSE:' + str(e) + loc)

def build(spec_path: Path, target: str, out_dir: Path) -> Dict[str, Any]:
    text = spec_path.read_text(encoding="utf-8")

    # Palier-3: project mode (#file: blocks)
    if "#file:" in text.lower():
        proj = parse_project(text)
        files_text = proj["files"]
        entry = proj["entry"]

        files_prog: Dict[str, Any] = {}
        # Parse + validate each file independently (no cross-file intelligence).
        for fname, ftext in files_text.items():
            parsed = safe_parse(ftext, fname)
            program = parsed["program"]

            violations = validate(program)
            if violations:
                raise Refusal("CONTRACT_VIOLATION:" + ";".join([f"{r}:{m}" for r, m in violations]) + f":file={fname}")

            files_prog[fname] = program

        # Sandbox run: load modules first so CALLFUNC in entry can resolve.
        sb = Sandbox()
        for fname, program in files_prog.items():
            if fname == entry:
                continue
            try:
                sb.run(program)
            except Exception as e:
                raise Refusal("SANDBOX_REFUSE:" + str(e) + f":file={fname}")

        try:
            sb.run(files_prog[entry])
        except Exception as e:
            raise Refusal("SANDBOX_REFUSE:" + str(e) + f":file={entry}")

        out_dir.mkdir(parents=True, exist_ok=True)

        if target == "python":
            py_files = generate_project_python(files_prog, entry=entry)
            for fn, content in py_files.items():
                (out_dir / fn).write_text(content, encoding="utf-8")
            return {"target": target, "out_dir": str(out_dir), "entry": "main.py", "mode": "project"}

        if target == "js":
            js_files = generate_project_js(files_prog, entry=entry)
            for fn, content in js_files.items():
                (out_dir / fn).write_text(content, encoding="utf-8")
            return {"target": target, "out_dir": str(out_dir), "entry": "main.js", "mode": "project"}

        raise Refusal("UNKNOWN_TARGET")

    # Single-file mode
    parsed = safe_parse(text)
    program = parsed["program"]

    violations = validate(program)
    if violations:
        raise Refusal("CONTRACT_VIOLATION:" + ";".join([f"{r}:{m}" for r, m in violations]))

    sb = Sandbox()
    try:
        sb.run(program)
    except Exception as e:
        raise Refusal("SANDBOX_REFUSE:" + str(e))

    out_dir.mkdir(parents=True, exist_ok=True)

    if target == "python":
        code = generate_python(program)
        out_file = out_dir / "app.py"
        out_file.write_text(code, encoding="utf-8")
        return {"target": target, "out_file": str(out_file)}

    if target == "js":
        code = generate_js(program)
        out_file = out_dir / "app.js"
        out_file.write_text(code, encoding="utf-8")
        return {"target": target, "out_file": str(out_file)}

    raise Refusal("UNKNOWN_TARGET")

def run_generated(target: str, out_dir: Path) -> str:
    if target == "python":
        entry = out_dir / ("main.py" if (out_dir / "main.py").exists() else "app.py")
        p = subprocess.run([sys.executable, str(entry)], capture_output=True, text=True)
        if p.returncode != 0:
            raise Refusal("RUNTIME_FAIL_PY:" + (p.stderr or p.stdout))
        return p.stdout
    if target == "js":
        entry = out_dir / ("main.js" if (out_dir / "main.js").exists() else "app.js")
        p = subprocess.run(["node", str(entry)], capture_output=True, text=True)
        if p.returncode != 0:
            raise Refusal("RUNTIME_FAIL_JS:" + (p.stderr or p.stdout))
        return p.stdout
    raise Refusal("UNKNOWN_TARGET")