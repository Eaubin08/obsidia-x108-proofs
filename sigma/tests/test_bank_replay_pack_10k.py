import subprocess
import sys
import os
import json
import pytest

RUNNER = "sigma/tools/run_bank_replay_pack.py" # On utilise le runner de base

def test_replay_10k_execution_and_stability():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    # On force la génération des données si elles manquent
    p = subprocess.run([sys.executable, RUNNER, "--cases", "100"], # Réduit à 100 pour le runner GitHub
                     capture_output=True, text=True, env=env, cwd=os.getcwd())
    assert p.returncode == 0
