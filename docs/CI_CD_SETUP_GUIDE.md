# 🚀 CI/CD Setup Guide — GitHub Actions for X-108

**Version:** 18.3.1 | **Status:** Production-Ready | **Last Updated:** 2026-03-03

---

## Overview

This guide explains how to set up **GitHub Actions CI/CD** to automatically verify X-108 proofs, run tests, and generate reports on every push and pull request.

---

## What Gets Automated

### 1. Lean 4 Proof Verification
- ✅ Compiles all Lean 4 theorems
- ✅ Verifies 33 theorems are proven (0 sorry)
- ✅ Generates build artifacts

### 2. TLA+ Model Checking
- ✅ Runs model checker on X108.tla
- ✅ Explores 1.2M states
- ✅ Verifies 0 violations
- ✅ Checks for deadlocks

### 3. Merkle Chain Verification
- ✅ Verifies Merkle chain integrity
- ✅ Checks root hash consistency
- ✅ Validates immutability

### 4. RFC3161 Timestamp Verification
- ✅ Verifies RFC3161 signature
- ✅ Validates TSA certificate
- ✅ Checks timestamp format

### 5. Connector Testing
- ✅ Tests Banking connector
- ✅ Tests Trading connector
- ✅ Tests Aviation connector
- ✅ Captures logs and errors

### 6. Test Suite Execution
- ✅ Runs 64 Vitest unit tests
- ✅ Runs 30 Python integration tests
- ✅ Runs 8 Chaos failure tests
- ✅ Runs 5 Load performance tests
- ✅ Generates coverage reports

### 7. Report Generation
- ✅ Creates PROOFKIT_REPORT.json
- ✅ Comments on PRs with results
- ✅ Creates releases with artifacts

---

## Installation Steps

### Step 1: Create Workflow Directory

```bash
# In your repo root
mkdir -p .github/workflows
```

### Step 2: Copy Workflow File

```bash
# Copy the GitHub Actions workflow
cp verify-proofs.yml .github/workflows/verify-proofs.yml
```

### Step 3: Configure Repository Settings

**Go to GitHub → Settings → Actions:**

1. ✅ Enable "Allow all actions and reusable workflows"
2. ✅ Set "Workflow permissions" to "Read and write permissions"
3. ✅ Enable "Allow GitHub Actions to create and approve pull requests"

### Step 4: Add Secrets (if needed)

**Go to GitHub → Settings → Secrets and variables → Actions:**

```bash
# If you need external services, add secrets here
# Examples:
# - SLACK_WEBHOOK (for notifications)
# - DOCKER_TOKEN (for container registry)
# - NPM_TOKEN (for private packages)
```

### Step 5: Commit and Push

```bash
git add .github/workflows/verify-proofs.yml
git add .gitignore
git commit -m "ci: Add GitHub Actions CI/CD for X-108 proof verification"
git push origin master
```

---

## Workflow Triggers

The workflow runs automatically on:

### 1. Push to Main Branches
```yaml
on:
  push:
    branches: [ master, main, develop ]
```

**Triggers on:**
- ✅ Push to master
- ✅ Push to main
- ✅ Push to develop

### 2. Pull Requests
```yaml
on:
  pull_request:
    branches: [ master, main, develop ]
```

**Triggers on:**
- ✅ PR created
- ✅ PR updated
- ✅ PR reopened

### 3. Daily Schedule
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
```

**Triggers:**
- ✅ Every day at 2 AM UTC
- ✅ Ensures proofs are still valid

---

## Workflow Jobs

### Job 1: verify-lean4
**Duration:** ~2-3 minutes

```
Install Lean 4 → Build proofs → Verify 33 theorems
```

**Success Criteria:**
- ✅ All 33 theorems proven
- ✅ 0 sorry statements
- ✅ Build succeeds

**Artifacts:**
- Lean build artifacts
- Proof verification logs

---

### Job 2: verify-tlaplus
**Duration:** ~5-10 minutes

```
Install TLA+ → Run model checker → Explore 1.2M states
```

**Success Criteria:**
- ✅ SafetyX108 verified
- ✅ NoDeadlock verified
- ✅ 0 violations found

**Artifacts:**
- TLA+ verification output
- State exploration logs

---

### Job 3: verify-merkle
**Duration:** ~1 minute

```
Install Python → Verify Merkle chain → Check integrity
```

**Success Criteria:**
- ✅ Chain integrity valid
- ✅ Root hash consistent
- ✅ All decisions recorded

**Artifacts:**
- merkle_seal.json
- Verification report

---

### Job 4: verify-rfc3161
**Duration:** ~1 minute

```
Install Python → Verify RFC3161 → Check TSA signature
```

**Success Criteria:**
- ✅ Timestamp valid
- ✅ TSA signature valid
- ✅ Certificate chain valid

**Artifacts:**
- rfc3161_anchor.json
- Verification report

---

### Job 5: test-connectors
**Duration:** ~2-3 minutes

```
Start Kernel → Test Banking → Test Trading → Test Aviation
```

**Success Criteria:**
- ✅ Banking connector responds
- ✅ Trading connector responds
- ✅ Aviation connector responds

**Artifacts:**
- Connector logs
- Runtime data

---

### Job 6: run-tests
**Duration:** ~3-5 minutes

```
Run Vitest → Run Python tests → Run Chaos tests → Run Load tests
```

**Success Criteria:**
- ✅ 64/64 Vitest PASS
- ✅ 30/30 Python PASS
- ✅ 8/8 Chaos PASS
- ✅ 5/5 Load PASS

**Artifacts:**
- Test results
- Coverage reports
- Performance metrics

---

### Job 7: generate-report
**Duration:** ~1 minute

```
Download artifacts → Generate PROOFKIT_REPORT → Comment on PR
```

**Success Criteria:**
- ✅ Report generated
- ✅ PR commented
- ✅ All jobs succeeded

**Artifacts:**
- PROOFKIT_REPORT.json
- Release notes (if tagged)

---

## Monitoring Workflow Runs

### View Workflow Status

**GitHub UI:**
1. Go to repo → Actions
2. Click on workflow run
3. View job status and logs

### View Job Logs

**For each job:**
1. Click job name
2. Expand step details
3. View console output

### Download Artifacts

**After workflow completes:**
1. Go to workflow run
2. Scroll to "Artifacts" section
3. Download desired artifacts

---

## Troubleshooting

### Issue: Lean 4 Build Fails

**Cause:** Lean 4 version mismatch

**Solution:**
```bash
# Update Lean 4 in workflow
# Change version in verify-proofs.yml:
# v4.0.0 → v4.1.0 (or latest)
```

### Issue: TLA+ Model Checking Times Out

**Cause:** Too many states to explore

**Solution:**
```bash
# Increase timeout in workflow
# Change timeout from 30m to 60m:
timeout-minutes: 60
```

### Issue: Connector Tests Fail

**Cause:** Kernel not starting

**Solution:**
```bash
# Add longer sleep time
sleep 5  # Instead of sleep 2
```

### Issue: Python Dependencies Missing

**Cause:** requirements.txt not updated

**Solution:**
```bash
# Update requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: Update dependencies"
```

---

## Performance Optimization

### Parallel Job Execution

By default, jobs run in parallel (except for dependencies):

```
verify-lean4 ─┐
              ├─→ generate-report
verify-tlaplus┤
verify-merkle ┤
verify-rfc3161┤
test-connectors
run-tests ────┘
```

**Total time:** ~10-15 minutes (parallel)

### Caching Dependencies

Add caching to speed up subsequent runs:

```yaml
- name: Cache Lean 4
  uses: actions/cache@v3
  with:
    path: ~/.elan
    key: ${{ runner.os }}-lean4

- name: Cache Python
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

- name: Cache Node
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('package-lock.json') }}
```

### Conditional Job Execution

Run expensive jobs only on main branch:

```yaml
if: github.ref == 'refs/heads/master'
```

---

## Notifications

### Slack Notifications

Add to workflow:

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "X-108 Proof Verification: ${{ job.status }}"
      }
```

### Email Notifications

GitHub automatically notifies:
- ✅ Workflow failures
- ✅ PR comments
- ✅ Release creation

---

## Release Process

### Automatic Release Creation

When you tag a commit:

```bash
git tag v18.3.1
git push origin v18.3.1
```

**Workflow automatically:**
1. ✅ Runs all verifications
2. ✅ Creates GitHub Release
3. ✅ Uploads artifacts
4. ✅ Generates release notes

---

## Best Practices

### 1. Keep Workflow Updated
- ✅ Review workflow monthly
- ✅ Update tool versions
- ✅ Add new tests

### 2. Monitor Workflow Health
- ✅ Check for failing jobs
- ✅ Review performance metrics
- ✅ Optimize slow steps

### 3. Document Changes
- ✅ Update CHANGELOG.md
- ✅ Add release notes
- ✅ Commit workflow changes

### 4. Test Locally First
- ✅ Run Lean 4 locally
- ✅ Run TLA+ locally
- ✅ Run tests locally
- ✅ Then push to trigger CI

---

## Next Steps

1. ✅ Copy workflow file to `.github/workflows/`
2. ✅ Configure repository settings
3. ✅ Add secrets (if needed)
4. ✅ Commit and push
5. ✅ Monitor first workflow run
6. ✅ Iterate and optimize

---

## References

- **GitHub Actions:** https://docs.github.com/en/actions
- **Lean 4:** https://lean-lang.org/
- **TLA+:** https://lamport.azurewebsites.net/tla/tla.html
- **Workflow Syntax:** https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions

---

**X-108 CI/CD: Automated Proof Verification on Every Push**

**Status:** ✅ Production-Ready | ✅ Fully Automated | ✅ Scalable
