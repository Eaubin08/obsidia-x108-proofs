"""Read-only integration check for the local Navier research corpus."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from periphery.agents.agent_obsidure import _build_math_memory_context_pack
from periphery.agents.obsidure_research_sources import load_navier_context
from scripts.obsidure_cli import handle_special_command

context = _build_math_memory_context_pack('NS_ANTI_PUMPING')
assert context['status'] == 'AVAILABLE', context
assert context['selected_count'] == 1
item = context['selected_items'][0]
assert not item['can_use_for_proof']
assert len(item['source_evidence']) == 4
assert all(source['sha256'] and source['excerpts'] for source in item['source_evidence'])
output = io.StringIO()
with contextlib.redirect_stdout(output):
    assert handle_special_command('context navier', None)
assert 'source_evidence' in output.getvalue()
with tempfile.TemporaryDirectory() as empty:
    missing = load_navier_context(empty)
    assert missing['availability'] == 'UNAVAILABLE'
    assert len(missing['source_errors']) == 4
print('PASS: four sources, selected context, CLI without agent, missing sources, non-proof status')
