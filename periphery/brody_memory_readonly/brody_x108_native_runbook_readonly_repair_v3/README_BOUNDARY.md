# BRODY X108 NATIVE RUNBOOK READONLY REPAIR V3

## Purpose

Fix-forward after $beforeHead.

The runbook is aligned to the real committed pointer statuses.

This does not convert READY into PASS.
This does not smooth history.
This does not hide failed intermediate repairs.

## Boundary

- no reset
- no rebase
- no history smoothing
- X108 remains final authority
- Brody does not decide
- Memory does not decide
- Graphiti does not decide
- verify_all.py must remain PASS
- runbook runner must be green before commit
