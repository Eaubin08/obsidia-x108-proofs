# CLEANUP DECISION TABLE

## 01 — TRACKED BUILD ARTIFACTS TO REMOVE FROM GIT LATER
Count: 544
Action: git rm --cached later, after full green Sigma/Lean/TLA.

## 02 — TRACKED STAGING OR PRIVATE REVIEW
Count: 905
Action: split or quarantine later. Do not delete during active repair.

## 03 — UNTRACKED SAFE QUARANTINE
Count: 19
Action: can move outside repo now if needed.

## 04 — PRIVATE PUBLIC EXPOSURE REVIEW
Count: 300
Action: inspect for real secrets before deciding.
