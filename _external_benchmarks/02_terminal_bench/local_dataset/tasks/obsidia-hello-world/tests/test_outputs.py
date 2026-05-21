from pathlib import Path

def test_obsidia_output_file_exists():
    p = Path("/app/obsidia_output.txt")
    assert p.exists(), "obsidia_output.txt does not exist"

def test_obsidia_output_content():
    p = Path("/app/obsidia_output.txt")
    assert p.read_text().strip() == "OBSIDIA_TERMINAL_BENCH_OK"
