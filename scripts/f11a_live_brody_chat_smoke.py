from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path


BASE_URLS = [
    "http://127.0.0.1:8011",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
]

PAYLOAD = {
    "message": "prepare un command packet pour git status",
    "session_id": "f11a-live-smoke",
    "language": "fr",
    "debug": True,
    "compact": False,
}


def post_json(url: str, payload: dict) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def main() -> int:
    out_dir = Path("docs/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)

    attempts = []
    selected = None

    for base in BASE_URLS:
        url = base.rstrip("/") + "/api/brody/chat"
        status, body = post_json(url, PAYLOAD)
        attempts.append({"url": url, "status": status, "body_type": type(body).__name__})
        if status == 200 and isinstance(body, dict):
            selected = {"url": url, "status": status, "body": body}
            break

    (out_dir / "F11A_LIVE_CHAT_ATTEMPTS.json").write_text(
        json.dumps(attempts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if selected is None:
        (out_dir / "F11A_LIVE_CHAT_SMOKE_RESULT.json").write_text(
            json.dumps({"ok": False, "attempts": attempts}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print("F11A_LIVE_CHAT_SMOKE_NO_SERVER")
        print(json.dumps(attempts, indent=2, ensure_ascii=False))
        return 2

    body = selected["body"]
    automation = body.get("automation_snapshot") or {}
    operator_loop = automation.get("operator_loop") or {}
    operator_view = body.get("operator_view_packet") or {}

    checks = {
        "response_is_dict": isinstance(body, dict),
        "has_automation_snapshot": isinstance(automation, dict) and bool(automation),
        "has_operator_loop": isinstance(operator_loop, dict) and bool(operator_loop),
        "has_operator_view_packet": isinstance(operator_view, dict) and bool(operator_view),
        "execution_allowed_for_brody_false": operator_loop.get("execution_allowed_for_brody") is False,
        "brody_execute_allowed_false": operator_loop.get("brody_execute_allowed") is False,
        "human_command_packet_ready_present": "human_command_packet_ready" in operator_loop,
        "command_copy_block_present": "command_copy_block" in operator_loop,
        "operator_view_readonly_true": operator_view.get("readonly") is True,
        "operator_view_emits_act_false": operator_view.get("emits_act") is False,
        "operator_view_emits_verdict_false": operator_view.get("emits_verdict") is False,
    }

    result = {
        "ok": all(checks.values()),
        "url": selected["url"],
        "status": selected["status"],
        "checks": checks,
        "operator_loop": operator_loop,
        "operator_view_summary": {
            "version": operator_view.get("version"),
            "system_status": operator_view.get("system_status"),
            "next_safe_action": operator_view.get("next_safe_action"),
            "decision_authority": operator_view.get("decision_authority"),
            "readonly": operator_view.get("readonly"),
            "emits_act": operator_view.get("emits_act"),
            "emits_verdict": operator_view.get("emits_verdict"),
        },
    }

    (out_dir / "F11A_LIVE_CHAT_SMOKE_RESULT.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("F11A_LIVE_CHAT_SMOKE_PASS" if result["ok"] else "F11A_LIVE_CHAT_SMOKE_FAIL")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
