from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CARD = (
    ROOT
    / "frontend"
    / "src"
    / "components"
    / "Chat"
    / "ObsidiaGovernedActionCard.tsx"
).read_text(
    encoding="utf-8"
)

API = (
    ROOT
    / "frontend"
    / "src"
    / "lib"
    / "api.ts"
).read_text(
    encoding="utf-8"
)

PROXY = (
    ROOT
    / "src"
    / "openjarvis"
    / "server"
    / "obsidia_governance_routes.py"
).read_text(
    encoding="utf-8"
)


def test_ui_has_no_execution_authority():
    text = CARD + "\n" + API

    for forbidden in (
        "relay_submit_mission",
        "relay_respond_to_hold",
        "execute_governed_remediation",
        "run_governed_content_apply",
        "run_and_persist_kx108",
        "store_approval_artifact",
        "ApprovalStore(",
    ):
        assert forbidden not in text

    assert (
        "Autoriser cette EAH"
        in CARD
    )

    assert (
        "UI_AUTHORITY=NONE"
        in CARD
    )


def test_openjarvis_proxy_has_no_authority_logic():
    for forbidden in (
        "relay_submit_mission",
        "relay_respond_to_hold",
        "execute_governed_remediation",
        "run_governed_content_apply",
        "run_and_persist_kx108",
        "ApprovalStore(",
    ):
        assert forbidden not in PROXY

    assert (
        'AUTHORITY = "NONE"'
        in PROXY
    )

    assert (
        'DECISION_AUTHORITY = "KX108_ONLY"'
        in PROXY
    )


def test_native_approval_is_explicitly_not_authority():
    assert (
        "NATIVE_APPROVAL_AUTHORITY=false"
        in CARD
    )

    assert (
        "Native OpenJarvis ApprovalStore is intentionally NOT used"
        in PROXY
    )
