import subprocess
import sys
import os
import pytest

RUNNER = "sigma/tools/run_bank_confusion_matrix_pack.py"

def test_matrix_runner_execution():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    # On lance le runner de masse proprement
    p = subprocess.run([sys.executable, RUNNER], capture_output=True, text=True, env=env)
    assert p.returncode == 0, f"Erreur Kernel: {p.stderr}"
