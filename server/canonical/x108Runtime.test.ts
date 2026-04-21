import { describe, it, expect } from "vitest";
import {
  runCanonicalPipeline,
  defaultBankState,
  defaultTradingState,
  defaultEcomState,
} from "./canonicalPipeline";

describe("X108 runtime canonical pipeline", () => {
  it("bank -> active le HOLD temporel si elapsed_s < min_required_elapsed_s", () => {
    const state = {
      ...defaultBankState(),
      elapsed_s: 12,
      min_required_elapsed_s: 108,
      recent_failed_attempts: 0,
      fraud_score: 0.10,
      behavior_shift_score: 0.05,
      urgency_score: 0.10,
      identity_mismatch_score: 0.05,
      narrative_conflict_score: 0.05,
      affordability_score: 0.92,
      counterparty_known: true,
      counterparty_age_days: 365,
      amount: 100,
      policy_limit: 1000,
    };

    const env = runCanonicalPipeline("bank", state);

    expect(env.python_available).toBe(true);
    expect(env.reason_code).toBe("X108_TEMPORAL_GATE_ACTIVE");
    expect(env.x108_gate).toBe("HOLD");
    expect(env.x108).toEqual({
      elapsed: 12,
      tau: 108,
      irr: true,
    });
    expect(env.metrics.elapsed_s).toBe(12);
    expect(env.metrics.min_required_elapsed_s).toBe(108);
    expect(env.metrics.irr).toBe(true);
  });

  it("bank -> n'active pas X108 si elapsed_s > tau", () => {
    const state = {
      ...defaultBankState(),
      elapsed_s: 222,
      min_required_elapsed_s: 108,
      recent_failed_attempts: 0,
      fraud_score: 0.10,
      behavior_shift_score: 0.05,
      urgency_score: 0.10,
      identity_mismatch_score: 0.05,
      narrative_conflict_score: 0.05,
      affordability_score: 0.92,
      counterparty_known: true,
      counterparty_age_days: 365,
      amount: 100,
      policy_limit: 1000,
    };

    const env = runCanonicalPipeline("bank", state);

    expect(env.python_available).toBe(true);
    expect(env.reason_code).not.toBe("X108_TEMPORAL_GATE_ACTIVE");
    expect(env.x108).toEqual({
      elapsed: 222,
      tau: 108,
      irr: true,
    });
    expect(env.metrics.elapsed_s).toBe(222);
    expect(env.metrics.min_required_elapsed_s).toBe(108);
    expect(env.metrics.irr).toBe(true);
  });

  it("trading -> smoke canonical pipeline", () => {
    const env = runCanonicalPipeline("trading", defaultTradingState());
    expect(env.python_available).toBe(true);
    expect(["ALLOW", "HOLD", "BLOCK"]).toContain(env.x108_gate);
    expect(env.x108).toBeDefined();
  });

  it("ecom -> smoke canonical pipeline", () => {
    const env = runCanonicalPipeline("ecom", defaultEcomState());
    expect(env.python_available).toBe(true);
    expect(["ALLOW", "HOLD", "BLOCK"]).toContain(env.x108_gate);
    expect(env.x108).toBeDefined();
  });
});
