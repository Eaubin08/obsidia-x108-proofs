# Bias Module

**Status:** FIRST_CLASS_X108_MODULE — DETECTION ONLY
**Source:** `periphery/bias/` (2 modules)
**Tests:** `tests/periphery/test_bias_gate_blocks_unvalidated_bias.py`

## Role
Bias detection and tracing. Detects cognitive bias in agent output and flags it for review. Never blocks autonomously — flagged bias goes to X108 as context signal.

## Status
**DETECTION_ONLY** — Flags bias. X108 decides on action.
