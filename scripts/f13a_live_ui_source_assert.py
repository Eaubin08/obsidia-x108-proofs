from pathlib import Path


client = Path("apps/obsidia-workbench/src/api/obsidiaClient.ts").read_text(encoding="utf-8")
chat = Path("apps/obsidia-workbench/src/views/ChatView.tsx").read_text(encoding="utf-8")
pkg = Path("apps/obsidia-workbench/package.json").read_text(encoding="utf-8")

checks = {
    "package_has_dev": '"dev": "vite"' in pkg,
    "package_has_build": '"build": "tsc -b && vite build"' in pkg,
    "client_has_engine_base": "VITE_ENGINE_API_BASE" in client,
    "client_posts_brody_chat": "${ENGINE_BASE}/api/brody/chat" in client,
    "client_sends_session_id": "session_id" in client,
    "client_preserves_backend_payload": "...data" in client,
    "chat_has_brody_terminal": "BRODY TERMINAL — TRANSVERSE STACK" in chat,
    "chat_has_operator_view_packet": "operator_view_packet" in chat,
    "chat_has_automation_snapshot": "automation_snapshot" in chat,
    "chat_has_operator_loop": "operator_loop" in chat,
    "chat_has_human_command_packet": "human_command_packet" in chat,
    "chat_has_command_copy_block": "command_copy_block" in chat,
    "chat_has_boundary_lines": "decision_authority=${String" in chat and "emits_act=${String" in chat,
    "chat_has_no_write_badge": "readonly / no ACT / no write" in chat,
}

for k, v in checks.items():
    print(f"{k}={v}")

if not all(checks.values()):
    raise SystemExit("F13A_SOURCE_ASSERT_FAIL")

print("F13A_SOURCE_ASSERT_PASS")
