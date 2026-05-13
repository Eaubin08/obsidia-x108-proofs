# BRODY LOCAL COMMAND GATE READONLY V1 REPAIR

## Purpose

Repair the first local command gate commit.

## Fixed

- git -C <repo> push now classifies as GIT_MUTATION_COMMAND_HUMAN_ONLY.
- Git mutation patterns now tolerate git -C ....
- Runner now fails hard if smoke test fails.

## Boundary

- Brody does not execute commands.
- Brody does not authorize execution.
- Human operator remains required.
- Decision authority remains KX108_ONLY.
- No Graphiti write.
- No memory intake.
- No ACT.
- No verdict.
- No X108 runtime binding.
- No X108 merge.
