import contextlib
import importlib.util
import io
from pathlib import Path


def load_cli():
    path = Path("tools/brody_chat.py")
    spec = importlib.util.spec_from_file_location("brody_chat_cli_f20c", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_terminal_renders_gencoin_cognitive_ledger_block():
    cli = load_cli()

    payload = {
        "gencoin_shadow_packet": {
            "version": "GENCOIN_SHADOW_VALUE_PACKET_V1",
            "usable_shadow_value": True,
        },
        "gencoin_cognitive_ledger_packet": {
            "version": "GENCOIN_COGNITIVE_LEDGER_PACKET_V1",
            "status": "GENCOIN_COGNITIVE_LEDGER_READONLY_PASS",
            "source": "BRODY_F20B_GENCOIN_COGNITIVE_LEDGER",
            "mode": "READONLY_PROJECTED_LEDGER",
            "ledger_status": "LIVE_EMPTY_REGISTRY",
            "entry_count": 1,
            "projected_only": True,
            "persisted": False,
            "mint_allowed": False,
            "wallet_enabled": False,
            "blockchain_enabled": False,
            "is_real_token": False,
            "readonly": True,
            "emits_act": False,
            "decision_authority": "KX108_ONLY",
            "entries": [
                {
                    "cognitive_ledger_score": 0.8031,
                    "score_status": "HIGH_READONLY_VALUE",
                    "shadow_scores": {
                        "cognitive_value": 0.94,
                        "proof_value": 0.89,
                        "reuse_value": 0.832,
                        "memory_value": 0.795,
                        "attention_cost": 0.2,
                        "energy_cost": 0.108,
                        "stability_value": 0.95,
                        "economic_projection": None,
                    },
                }
            ],
        },
    }

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        cli._print_gencoin_cognitive_ledger(payload)

    text = out.getvalue()
    assert "GENCOIN COGNITIVE LEDGER / READONLY" in text
    assert "GENCOIN_COGNITIVE_LEDGER_READONLY_PASS" in text
    assert "score=0.8031" in text
    assert "score_status=HIGH_READONLY_VALUE" in text
    assert "mint_allowed=false" in text
    assert "wallet_enabled=false" in text
    assert "blockchain_enabled=false" in text
    assert "is_real_token=false" in text
    assert "authority=KX108_ONLY" in text
