# BRODY LOCAL COMMAND GATE READONLY V1

## Purpose

Classify local terminal commands for Brody / LLM Obsidien without executing them.

This module exists inside obsidia-x108-proofs.

## Boundary

- Brody may classify commands.
- Brody does not execute commands.
- Brody does not authorize execution.
- Human operator remains required.
- X108 remains final decision authority.

## Forbidden

- command execution by Brody
- network execution
- filesystem mutation execution
- git mutation execution
- secret printing
- Graphiti write
- memory intake
- memory decision
- ACT emission
- verdict emission
- kernel mutation
- X108 runtime binding
- X108 merge

## Build target

obsidia-x108-proofs only.
