# TEST_MEMORY_FEEDBACK_CANDIDATE.ps1 — Memory feedback candidate flow tests
Set-Location $PSScriptRoot\..
python -m pytest tests/non_sovereignty/test_memory_promotion_not_automatic.py `
               -v --tb=short
python connectors/memory_feedback_candidate_flow.py
