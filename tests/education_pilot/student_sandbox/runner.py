"""Student-side protocol runner, executed INSIDE the isolated container.

Only this directory (read-only), the student's state directory (/state) and, for probes,
an extra read-only directory are mounted. The repository, the bench and the private exam
keys are not visible. The runner speaks JSON lines on stdin/stdout:
  {"op": "learn", "items": [...]}            -> {"ok": true, "result": null}
  {"op": "answer", "word": w, "sentence": s} -> {"ok": true, "result": {"sense": ..., "provenance": [...]}}
Errors are reported as {"ok": false, "error": <exception class name>, "message": ...}.
"""
from __future__ import annotations

import importlib
import json
import os
import pathlib
import sys

for extra in filter(None, os.environ.get("STUDENT_PATHS", "/student").split(":")):
    if extra not in sys.path:
        sys.path.insert(0, extra)

STATE = pathlib.Path("/state")


def main() -> None:
    module_name, class_name = os.environ.get("STUDENT", "students:EmptyStudent").split(":")
    cls = getattr(importlib.import_module(module_name), class_name)
    try:
        student = cls.load(STATE) if os.environ.get("LOAD") == "1" else cls()
        ready = {"ok": True, "result": "READY"}
    except Exception as exc:  # reported to the host, e.g. StateIntegrityError
        student, ready = None, {"ok": False, "error": type(exc).__name__, "message": str(exc)[:200]}
    print(json.dumps(ready), flush=True)
    if student is None:
        return
    for line in sys.stdin:
        req = json.loads(line)
        op = req.get("op")
        try:
            if op == "learn":
                result = student.learn([tuple(i) for i in req["items"]])
            elif op == "apply_correction":
                result = student.apply_correction(tuple(req["correction"]), tuple(req["exercise"]))
            elif op == "answer":
                result = student.answer(req["word"], req["sentence"])
            elif op == "retrieve":
                result = student.retrieve(**req["query"])
            elif op == "history":
                result = student.history(req["word"], req["sense"])
            elif op == "save":
                result = student.save(STATE)
            elif op == "probe":
                result = student.probe()
            elif op == "close":
                print(json.dumps({"ok": True, "result": None}), flush=True)
                return
            else:
                raise ValueError(f"unknown op {op!r}")
            print(json.dumps({"ok": True, "result": result}, default=str), flush=True)
        except Exception as exc:
            print(json.dumps({"ok": False, "error": type(exc).__name__, "message": str(exc)[:200]}), flush=True)


if __name__ == "__main__":
    main()
