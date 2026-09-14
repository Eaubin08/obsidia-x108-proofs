from periphery.reverse_os.action_projection_readonly import project_action_readonly


def test_f39_reverse_os_projection_contract():
    result = project_action_readonly(
        "f39_contract",
        "project readonly",
        "validation"
    )

    assert result is not None
    assert getattr(result, "advisory_only", True) is True


def test_f39_route_uses_safe_response():
    from pathlib import Path

    src = Path("apps/obsidia_api/routes/os_trad_ir_reverse.py").read_text(
        encoding="utf-8"
    )

    assert "safe_backend_response" in src
