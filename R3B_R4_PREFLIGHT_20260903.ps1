# =====================================================================
# R3B + R4 PREFLIGHT — CANONICAL RUNTIME INTEGRATION
# No source modification.
# =====================================================================

$ErrorActionPreference = "Continue"

$OUT = "R3B_R4_PREFLIGHT_20260903.txt"

if (Test-Path $OUT) {
    Remove-Item $OUT -Force
}

Start-Transcript -Path $OUT -Force

function Section([string]$Name) {
    Write-Host ""
    Write-Host "====================================================================="
    Write-Host $Name
    Write-Host "====================================================================="
}

function Dump-File([string]$Path) {
    Write-Host ""
    Write-Host "#####################################################################"
    Write-Host "FILE: $Path"
    Write-Host "#####################################################################"

    if (Test-Path $Path) {
        Get-Content $Path -Raw
    }
    else {
        Write-Host "ABSENT"
    }
}

function Run-PyModule([string]$Module) {
    Write-Host ""
    Write-Host ">>> python -m $Module"

    python -m $Module

    Write-Host "EXIT=$LASTEXITCODE"
}

# =====================================================================
Section "0 — BASELINE"
# =====================================================================

Write-Host "ROOT:"
Get-Location

Write-Host ""
Write-Host "BRANCH:"
git branch --show-current

Write-Host ""
Write-Host "HEAD:"
git rev-parse HEAD

Write-Host ""
Write-Host "STATUS:"
git status --short

Write-Host ""
Write-Host "RECENT COMMITS:"
git log -8 --oneline


# =====================================================================
Section "1 — UNTRACKED TRUTH"
# =====================================================================

Dump-File "pytest.ini"
Dump-File "docs/runtime/POST_CG100_RUNTIME_INTEGRATION_TRUTH.md"


# =====================================================================
Section "2 — CG97: RUN CORRECTLY AS PYTHON MODULE"
# =====================================================================

$CG97 = "scripts/kernel/kx108_proof_kx108_end_to_end_validation_v1.py"

if (Test-Path $CG97) {

    Dump-File $CG97

    Run-PyModule "scripts.kernel.kx108_proof_kx108_end_to_end_validation_v1"
}
else {
    Write-Host "CG97_SCRIPT_ABSENT"
}


# =====================================================================
Section "3 — CG96: LOCATE REAL GLOBAL-RUNTIME IMPLEMENTATION"
# =====================================================================

$CG96Candidates = @(
    Get-ChildItem scripts,kernel,tests,docs `
        -Recurse `
        -File `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'cg96|global_runtime|global.*runtime.*validation'
    }
)

Write-Host "CG96_CANDIDATE_COUNT=$($CG96Candidates.Count)"

foreach ($f in $CG96Candidates) {
    Write-Host $f.FullName
}

$ExactCG96 = "scripts/kernel/kx108_proof_kx108_global_runtime_validation_v1.py"

if (Test-Path $ExactCG96) {

    Dump-File $ExactCG96

    Run-PyModule "scripts.kernel.kx108_proof_kx108_global_runtime_validation_v1"
}
else {
    Write-Host "EXACT_CG96_SCRIPT_ABSENT"
}


# =====================================================================
Section "4 — CURRENT CANONICAL AGENT -> X108 IMPLEMENTATION"
# =====================================================================

Dump-File "periphery/context/agent_result_context_adapter.py"
Dump-File "periphery/context/agent_x108_context_flow.py"
Dump-File "runtime_wiring/x108_admission_stub.py"
Dump-File "periphery/context/context_packet_validator.py"


# =====================================================================
Section "5 — EXISTING KX108 DECISION / ACT / EXECUTION SURFACES"
# =====================================================================

$Roots = @(
    "scripts/kernel",
    "kernel",
    "runtime_wiring",
    "periphery",
    "apps/obsidia_api"
) | Where-Object { Test-Path $_ }

Write-Host ""
Write-Host "--- DECISION SURFACES ---"

rg -n `
    --glob "*.py" `
    'CanonicalDecisionEnvelope|DecisionEnvelope|DecisionTicket|SovereignTicket|KX108_ONLY|decision_authority' `
    $Roots

Write-Host ""
Write-Host "--- ACT / AUTHORIZATION SURFACES ---"

rg -n `
    --glob "*.py" `
    'ACT_BLOCKED|ACT_AUTHORIZED|authorization|Authorization|authorize|act_gate|ACT_GATE|execution_authority' `
    $Roots

Write-Host ""
Write-Host "--- EXECUTION SURFACES ---"

rg -n `
    --glob "*.py" `
    'EXECUTION_BLOCKED|EXECUTION_AUTHORIZED|ExecutionResult|executor|controlled_execution|ControlledExecution|execute_action|execute\(' `
    $Roots


# =====================================================================
Section "6 — DUMP MOST RELEVANT EXECUTION/GATE FILES"
# =====================================================================

$ExecutionFiles = @(
    "runtime_wiring/source_runtime/action_gateway_hold_block_sandbox.py",
    "scripts/kernel/kx108_operational_loop_contract_v1.py",
    "scripts/kernel/kx108_execution_boundary_v1.py",
    "scripts/kernel/kx108_act_boundary_v1.py",
    "scripts/kernel/kx108_decision_gate_v1.py",
    "scripts/kernel/kernel_decision_gate_v1.py"
)

foreach ($f in $ExecutionFiles) {
    Dump-File $f
}


# =====================================================================
Section "7 — RECEIPT LIFECYCLE / RESULT BINDING"
# =====================================================================

rg -n `
    --glob "*.py" `
    'ProviderRuntimeReceipt|RuntimeReceipt|ReceiptStatus|result_ref|\.complete\(|COMPLETED|STARTED|ABORTED' `
    scripts `
    periphery `
    runtime_wiring `
    tests/cli/kernel `
    tests/cli/providers `
    2>$null

$ReceiptCandidates = @(
    Get-ChildItem scripts,periphery,runtime_wiring `
        -Recurse `
        -File `
        -Filter "*.py" `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'receipt.*flow|runtime.*receipt|receipt.*runtime'
    } |
    Select-Object -First 20
)

Write-Host ""
Write-Host "RECEIPT_CANDIDATES=$($ReceiptCandidates.Count)"

foreach ($f in $ReceiptCandidates) {
    Write-Host $f.FullName
}


# =====================================================================
Section "8 — FEEDBACK -> NEW CONTEXT SURFACES"
# =====================================================================

Dump-File "periphery/feedback_memory_candidate.py"
Dump-File "periphery/feedback_memory_bridge_brody_readonly.py"
Dump-File "tests/periphery/test_feedback_memory_candidate.py"
Dump-File "tests/periphery/test_feedback_memory_bridge_readonly.py"

rg -n `
    --glob "*.py" `
    'feedback_state|update_feedback|FeedbackMemoryCandidate|feedback.*ContextPacket|ContextPacket.*feedback|new_context|next_context' `
    scripts `
    periphery `
    runtime_wiring `
    apps/obsidia_api `
    tests `
    2>$null


# =====================================================================
Section "9 — OPERATIONAL AGENT REGISTRY — REAL INVOCABLE SET"
# =====================================================================

Dump-File "periphery/agent_registry.py"

python -c "from periphery.agent_registry import list_agents; a=list_agents(); print('OPERATIONAL_AGENT_COUNT=',len(a)); print(*a,sep='\n')"

Write-Host "OPERATIONAL_REGISTRY_EXIT=$LASTEXITCODE"

python -m pytest -q `
    tests/periphery/test_agent_registry.py `
    tests/periphery/test_agent_registry_v3_v4.py

Write-Host "OPERATIONAL_REGISTRY_TEST_EXIT=$LASTEXITCODE"


# =====================================================================
Section "10 — 52 AGENT CONFIG REGISTRY — STRUCTURAL SET"
# =====================================================================

Dump-File "periphery/agents_obsidia_config_registry.py"

$Agent52Files = @(
    Get-ChildItem periphery `
        -Recurse `
        -File `
        -Filter "agents_52.registry.json" `
        -ErrorAction SilentlyContinue
)

Write-Host "AGENTS52_REGISTRY_FILES=$($Agent52Files.Count)"

foreach ($f in $Agent52Files) {
    Write-Host $f.FullName
}

if (Test-Path "periphery/modules_agents/test_agents_52_registry.py") {

    python -m pytest -q `
        periphery/modules_agents/test_agents_52_registry.py

    Write-Host "AGENTS52_TEST_EXIT=$LASTEXITCODE"
}
else {
    Write-Host "AGENTS52_TEST_FILE_ABSENT"
}


# =====================================================================
Section "11 — AUTHORITY ESCALATION AUDIT — SAFE POWERSHELL QUOTING"
# =====================================================================

$AuthorityPattern = 'emits_act\s*=\s*True|memory_write\s*=\s*True|kernel_mutation\s*=\s*True|execution_authority\s*=\s*True|decision_authority\s*=\s*["'']?(SELF|AGENT|PROVIDER)'

rg -n `
    --glob "*.py" `
    $AuthorityPattern `
    periphery `
    kernel `
    scripts `
    apps `
    runtime_wiring `
    2>$null

Write-Host "AUTHORITY_RG_EXIT=$LASTEXITCODE"


# =====================================================================
Section "12 — TARGETED CANONICAL RUNTIME TESTS"
# =====================================================================

$RuntimeTests = @(
    "tests/periphery/test_agent_result_context_adapter.py",
    "tests/periphery/test_agent_x108_context_flow.py",
    "tests/api/test_agent_x108_context_route.py",
    "tests/cli/kernel/test_kx108_proof_kx108_end_to_end_validation_v1.py",
    "tests/cli/providers/test_canonical_runtime_receipt_lifecycle_v1.py"
) | Where-Object {
    Test-Path $_
}

Write-Host "RUNTIME_TEST_COUNT=$($RuntimeTests.Count)"

python -m pytest -q @RuntimeTests

Write-Host "RUNTIME_TEST_EXIT=$LASTEXITCODE"


# =====================================================================
Section "13 — EXECUTION BOUNDARY TEST CLUSTER"
# =====================================================================

$ExecutionTests = @(
    "tests/cli/kernel/test_kx108_execution_boundary_v1.py",
    "tests/cli/kernel/test_kx108_act_boundary_v1.py",
    "tests/cli/kernel/test_kx108_act_receipt_v1.py",
    "tests/cli/kernel/test_kx108_proof_action_boundary_v1.py",
    "tests/cli/kernel/test_kx108_proof_execution_authority_boundary_v1.py",
    "tests/cli/kernel/test_kernel_decision_gate_v1.py",
    "tests/cli/kernel/test_kx108_operational_loop_contract_v1.py",
    "tests/cli/kernel/test_kx108_operational_loop_state_v1.py"
) | Where-Object {
    Test-Path $_
}

Write-Host "EXECUTION_TEST_COUNT=$($ExecutionTests.Count)"

if ($ExecutionTests.Count -gt 0) {

    python -m pytest -q @ExecutionTests

    Write-Host "EXECUTION_TEST_EXIT=$LASTEXITCODE"
}
else {
    Write-Host "NO_EXECUTION_TESTS_FOUND"
}


# =====================================================================
Section "14 — PYTEST CURRENT COLLECTION"
# =====================================================================

python -m pytest --collect-only -q

Write-Host "COLLECT_EXIT=$LASTEXITCODE"


# =====================================================================
Section "15 — FULL CURRENT REGRESSION"
# =====================================================================

python -m pytest -q

Write-Host "CURRENT_PYTEST_EXIT=$LASTEXITCODE"


# =====================================================================
Section "16 — CURRENT / LEGACY / ARCHIVED PROOF SIGNALS"
# =====================================================================

Write-Host "--- pytest.ini ---"

if (Test-Path "pytest.ini") {
    Get-Content "pytest.ini" -Raw
}

Write-Host ""
Write-Host "--- historical proof directories ---"

Get-ChildItem `
    proofs `
    tests `
    -Directory `
    -Recurse `
    -ErrorAction SilentlyContinue |
Where-Object {
    $_.FullName -match 'legacy|archive|snapshot|V18_3_1'
} |
Select-Object FullName


# =====================================================================
Section "17 — FINAL GIT STATE"
# =====================================================================

git status --short

Write-Host ""
Write-Host "UNTRACKED:"

git ls-files --others --exclude-standard

Write-Host ""
Write-Host "WORKTREE DIFF:"

git diff --stat


# =====================================================================
Section "18 — R4 SOURCE CANDIDATES SUMMARY"
# =====================================================================

Write-Host ""
Write-Host "CANONICAL INPUT:"
Write-Host "  periphery/context/agent_result_context_adapter.py"
Write-Host "  periphery/context/agent_x108_context_flow.py"

Write-Host ""
Write-Host "NEXT REQUIRED LINK:"
Write-Host "  X108/KX108 decision -> canonical authorization -> controlled execution"
Write-Host "  -> terminal receipt -> readonly feedback -> next ContextPacket"

Write-Host ""
Write-Host "NO FILES MODIFIED BY THIS PASS."

Stop-Transcript

Write-Host ""
Write-Host "====================================================================="
Write-Host "R3B + R4 PREFLIGHT COMPLETE"
Write-Host "OUTPUT: $OUT"
Write-Host "====================================================================="
