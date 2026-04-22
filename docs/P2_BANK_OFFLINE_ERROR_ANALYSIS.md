# P2 Bank Offline Error Analysis

## Purpose

This layer computes offline proxy metrics from the truth proxy pack.

## Metrics

- total_cases
- failed_cases
- family counts
- observed gate counts
- gap counts
- confusion matrix
- reason family counts
- total runtime
- mean milliseconds per case

## Gap interpretation

- MATCH
- HARDER_THAN_BUSINESS
- SOFTER_THAN_BUSINESS

## Confusion rule

Expected positive:
- ANALYSER
- BLOQUER

Predicted positive:
- HOLD
- BLOCK

This is an offline proxy metric.
It is not a live production false-positive / false-negative measurement.
