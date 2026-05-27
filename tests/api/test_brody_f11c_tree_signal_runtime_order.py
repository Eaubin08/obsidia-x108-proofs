from pathlib import Path


def test_tree_signal_runtime_build_exists_once():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert src.count("_tree_signal_raw = safe_call_snapshot(") == 1
    assert "_tree_text = str(req.message or \"\")" in src
    assert "build_tree_signal_packet" in src
    assert "_tree_signal_packet = (" in src


def test_tree_signal_runtime_order_before_memory_guard_and_value_layer():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert src.index("_tree_signal_raw = safe_call_snapshot(") < src.index("_memory_guard_raw = safe_call_snapshot(")
    assert src.index("_tree_text = str(req.message or \"\")") < src.index("request_text=_tree_text")
    assert src.index("_tree_signal_packet = (") < src.index("tree_signal_packet=_tree_signal_packet")
    assert src.index("_tree_signal_packet = (") < src.index('"tree_signal_packet": _tree_signal_packet')
