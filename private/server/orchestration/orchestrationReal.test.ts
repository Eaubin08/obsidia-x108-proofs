import { describe, it, expect } from "vitest";
import { orchestrateReal, validateOrchestrationFlow } from "./orchestratorReal";
import { defaultTradingState, defaultBankState, defaultEcomState } from "../canonical/canonicalPipeline";

describe("Orchestration Real — full honest flow", () => {
  it("should orchestrate trading flow", () => {
    const output = orchestrateReal("trading", defaultTradingState);

    expect(output).toBeDefined();
    expect(output.envelope).toBeDefined();
    expect(output.audit_entry).toBeDefined();
    expect(output.sigma).toBeDefined();
    expect(output.attestation).toBeDefined();
    expect(output.verify_all).toBeDefined();
    expect(output.timestamps).toBeDefined();
  });

  it("should orchestrate bank flow", () => {
    const output = orchestrateReal("bank", defaultBankState);
    expect(output.envelope?.domain).toBe("bank");
    expect(output.envelope?.decision_id).toBeDefined();
    expect(output.envelope?.trace_id).toBeDefined();
  });

  it("should orchestrate ecom flow", () => {
    const output = orchestrateReal("ecom", defaultEcomState);
    expect(output.envelope?.domain).toBe("ecom");
    expect(output.envelope?.decision_id).toBeDefined();
    expect(output.envelope?.trace_id).toBeDefined();
  });

  it("should write audit evidence ref", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    expect(Array.isArray(output.envelope?.evidence_refs)).toBe(true);
    expect(output.envelope!.evidence_refs.some((x) => String(x).startsWith("audit:"))).toBe(true);
  });

  it("should keep Sigma observation-only", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    expect(output.sigma).toBeDefined();
    expect("kernel_verdict" in output.sigma!).toBe(false);
    expect("consensus_verdict" in output.sigma!).toBe(false);
    expect("x108_gate" in output.sigma!).toBe(false);
  });

  it("should attach honest Merkle attestation", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    expect(output.attestation).toBeDefined();
    expect(output.attestation!.decision_id).toBe(output.envelope!.decision_id);
    expect(["verified", "incomplete", "failed", "ok"]).toContain(output.attestation!.status);
  });

  it("should expose honest RFC status", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    if (output.rfc3161) {
      expect(["verified", "pending", "failed", "incomplete"]).toContain(output.rfc3161.status);
    }
  });

  it("should export tla trace and vars", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    expect(output.tla_export).toBeDefined();

    if (output.tla_export?.status === "exported") {
      expect(output.tla_export.trace).toBeDefined();
      expect(output.tla_export.vars).toBeDefined();
      expect(output.tla_export.trace.decision_id).toBe(output.envelope!.decision_id);
      expect(output.tla_export.vars.decisionId).toBe(output.envelope!.decision_id);
    }
  });

  it("should expose verify_all structure", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    expect(typeof output.verify_all!.success).toBe("boolean");
    expect(typeof output.verify_all!.output).toBe("string");
    expect(Array.isArray(output.verify_all!.errors)).toBe(true);
  });

  it("should validate full orchestration flow with correct signature", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    const { valid, errors } = validateOrchestrationFlow(output);
    expect(Array.isArray(errors)).toBe(true);
    if (output.success) {
      expect(valid).toBe(true);
      expect(errors).toHaveLength(0);
    }
  });

  it("should keep timestamps ordered", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    const t = output.timestamps!;
    expect(t.started_at).toBeLessThanOrEqual(t.pipeline_at);
    expect(t.pipeline_at).toBeLessThanOrEqual(t.audit_at);
    expect(t.audit_at).toBeLessThanOrEqual(t.sigma_at);
    expect(t.sigma_at).toBeLessThanOrEqual(t.merkle_at);
    expect((t.tla_at ?? t.merkle_at)).toBeLessThanOrEqual(t.completed_at);
  });

  it("should add tla evidence_refs if export successful", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    if (output.tla_export?.status === "exported") {
      expect(output.envelope!.evidence_refs.some((x) => String(x).startsWith("tla:"))).toBe(true);
      expect(output.envelope!.evidence_refs.some((x) => String(x).startsWith("tla_vars:"))).toBe(true);
    }
  });

  it("should validate envelope structure", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    const { valid, errors } = validateOrchestrationFlow(output);
    expect(errors).not.toContain("envelope is missing");
    if (output.envelope) {
      expect(errors).not.toContain("envelope.decision_id is missing");
      expect(errors).not.toContain("envelope.trace_id is missing");
    }
  });

  it("should validate audit entry structure", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    const { errors } = validateOrchestrationFlow(output);
    expect(errors).not.toContain("audit_entry is missing");
  });

  it("should validate sigma non-decisional", () => {
    const output = orchestrateReal("trading", defaultTradingState);
    const { errors } = validateOrchestrationFlow(output);
    expect(errors).not.toContain("sigma should not contain kernel_verdict");
    expect(errors).not.toContain("sigma should not contain consensus_verdict");
    expect(errors).not.toContain("sigma should not contain x108_gate");
  });
});
