from scripts.gates.obsidia_sigma_non_sovereignty_check import (
    DEFAULT_TARGET,
    check_text,
)


def test_sigma_cannot_bypass_x108():
    text = DEFAULT_TARGET.read_text(
        encoding="utf-8",
    )

    violations = check_text(text)

    assert violations == []
    assert "KX108_ONLY" in text
    assert "emits_act: bool = False" in text
    assert "kernel_mutation: bool = False" in text
