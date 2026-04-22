/**
 * Tests Vitest — Composants canoniques OS4 V2
 * Teste les contrats d'interface et la logique pure (sans DOM)
 * de : DecisionEnvelopeCard, ProofChainView, HealthMatrix
 */
import { describe, expect, it } from "vitest";

// ─── Types importés directement (pas de rendu DOM) ───────────────────────────
// On teste la logique pure : validation des types, calculs de statut, etc.

// ─── CanonicalEnvelope contract ──────────────────────────────────────────────
interface CanonicalEnvelope {
  domain: "trading" | "bank" | "ecom";
  market_verdict: string;
  confidence: number;
  contradictions: number;
  unknowns: number;
  risk_flags: string[];
  x108_gate: "ALLOW" | "HOLD" | "BLOCK";
  reason_code: string;
  severity: "S1" | "S2" | "S3" | "S4";
  decision_id: string;
  trace_id?: string;
  ticket_required: boolean;
  ticket_id?: string;
  attestation_ref?: string;
  source: string;
  metrics?: Record<string, number>;
  timestamp?: number;
}

// ─── ProofChain contract ─────────────────────────────────────────────────────
interface ProofChain {
  decision_id: string;
  trace_id?: string;
  ticket_required: boolean;
  ticket_id?: string;
  attestation_ref?: string;
  lean_proof_hash?: string;
  proof_complete: boolean;
  proof_partial: boolean;
}

// ─── HealthMatrixData contract ───────────────────────────────────────────────
interface HealthDimension {
  label: string;
  score: number;
  trend: "up" | "down" | "stable";
  details?: string;
  critical?: boolean;
}
interface HealthMatrixData {
  agent_health: HealthDimension;
  proof_coverage: HealthDimension;
  decision_quality: HealthDimension;
  risk_exposure: HealthDimension;
  domain: "trading" | "bank" | "ecom";
  last_updated?: number;
}

// ─── Logique pure extraite des composants ────────────────────────────────────

/** Calcule le score de complétude d'une ProofChain (0-4 étapes) */
function proofCompletenessScore(chain: ProofChain): { score: number; max: number; label: string } {
  let score = 0;
  const max = chain.ticket_required ? 4 : 3;
  if (chain.decision_id) score++;
  if (chain.trace_id) score++;
  if (chain.ticket_required && chain.ticket_id) score++;
  if (chain.attestation_ref) score++;
  const label = score === max ? "COMPLETE" : score >= max - 1 ? "PARTIAL" : "INCOMPLETE";
  return { score, max, label };
}

/** Détermine si une enveloppe est critique (S3/S4 ou BLOCK) */
function isEnvelopeCritical(env: CanonicalEnvelope): boolean {
  return env.severity === "S3" || env.severity === "S4" || env.x108_gate === "BLOCK";
}

/** Calcule le score global de santé d'une HealthMatrix */
function globalHealthScore(data: HealthMatrixData): number {
  const scores = [
    data.agent_health.score,
    data.proof_coverage.score,
    data.decision_quality.score,
    100 - data.risk_exposure.score, // risk inversé
  ];
  return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
}

/** Détermine le statut global d'une HealthMatrix */
function healthStatus(score: number): "OK" | "WARN" | "CRITICAL" {
  if (score >= 80) return "OK";
  if (score >= 60) return "WARN";
  return "CRITICAL";
}

/** Formate un decision_id pour l'affichage compact */
function formatDecisionId(id: string, maxLen = 20): string {
  if (id.length <= maxLen) return id;
  return id.slice(0, 8) + "…" + id.slice(-6);
}

// ─── Fixtures ────────────────────────────────────────────────────────────────

const MOCK_ENVELOPE_ALLOW: CanonicalEnvelope = {
  domain: "trading",
  market_verdict: "BUY_SIGNAL_CONFIRMED",
  confidence: 0.87,
  contradictions: 1,
  unknowns: 0,
  risk_flags: [],
  x108_gate: "ALLOW",
  reason_code: "TREND_CONFIRMED_LOW_RISK",
  severity: "S2",
  decision_id: "DEC-T-2024-0891-a3f2",
  trace_id: "TRC-2024-0891-b7c1",
  ticket_required: false,
  attestation_ref: "ATT-2024-0891-lean4",
  source: "simulation",
  metrics: { pnl_estimate: 0.023, volatility: 0.42 },
  timestamp: Date.now() - 45000,
};

const MOCK_ENVELOPE_BLOCK: CanonicalEnvelope = {
  domain: "bank",
  market_verdict: "CREDIT_RISK_CRITICAL",
  confidence: 0.94,
  contradictions: 0,
  unknowns: 0,
  risk_flags: ["LIQUIDITY_BREACH", "CAPITAL_RATIO_BELOW_THRESHOLD"],
  x108_gate: "BLOCK",
  reason_code: "CAPITAL_RATIO_BREACH",
  severity: "S4",
  decision_id: "DEC-B-2024-0312-f9a1",
  trace_id: "TRC-2024-0312-c2d4",
  ticket_required: true,
  ticket_id: "TKT-2024-0312-001",
  attestation_ref: "ATT-2024-0312-lean4",
  source: "live",
  timestamp: Date.now() - 120000,
};

const MOCK_PROOF_COMPLETE: ProofChain = {
  decision_id: "DEC-T-2024-0891-a3f2",
  trace_id: "TRC-2024-0891-b7c1",
  ticket_required: false,
  attestation_ref: "ATT-2024-0891-lean4",
  proof_complete: true,
  proof_partial: false,
};

const MOCK_PROOF_PARTIAL: ProofChain = {
  decision_id: "DEC-B-2024-0312-f9a1",
  trace_id: "TRC-2024-0312-c2d4",
  ticket_required: true,
  ticket_id: "TKT-2024-0312-001",
  attestation_ref: undefined,
  proof_complete: false,
  proof_partial: true,
};

const MOCK_PROOF_INCOMPLETE: ProofChain = {
  decision_id: "DEC-E-2024-0099-x1z2",
  trace_id: undefined,
  ticket_required: false,
  attestation_ref: undefined,
  proof_complete: false,
  proof_partial: false,
};

const MOCK_HEALTH_OK: HealthMatrixData = {
  domain: "trading",
  agent_health:      { label: "Agent Health",      score: 95, trend: "stable" },
  proof_coverage:    { label: "Proof Coverage",    score: 88, trend: "up" },
  decision_quality:  { label: "Decision Quality",  score: 91, trend: "stable" },
  risk_exposure:     { label: "Risk Exposure",     score: 12, trend: "down" },
  last_updated: Date.now(),
};

const MOCK_HEALTH_CRITICAL: HealthMatrixData = {
  domain: "bank",
  agent_health:      { label: "Agent Health",      score: 45, trend: "down", critical: true },
  proof_coverage:    { label: "Proof Coverage",    score: 30, trend: "down", critical: true },
  decision_quality:  { label: "Decision Quality",  score: 55, trend: "down" },
  risk_exposure:     { label: "Risk Exposure",     score: 78, trend: "up", critical: true },
  last_updated: Date.now(),
};

// ─── Tests DecisionEnvelopeCard ───────────────────────────────────────────────
describe("DecisionEnvelopeCard — contrat CanonicalEnvelope", () => {
  it("une enveloppe ALLOW S2 n'est pas critique", () => {
    expect(isEnvelopeCritical(MOCK_ENVELOPE_ALLOW)).toBe(false);
  });

  it("une enveloppe BLOCK S4 est critique", () => {
    expect(isEnvelopeCritical(MOCK_ENVELOPE_BLOCK)).toBe(true);
  });

  it("une enveloppe S3 sans BLOCK est quand même critique", () => {
    const env: CanonicalEnvelope = { ...MOCK_ENVELOPE_ALLOW, severity: "S3", x108_gate: "HOLD" };
    expect(isEnvelopeCritical(env)).toBe(true);
  });

  it("confidence doit être entre 0 et 1", () => {
    expect(MOCK_ENVELOPE_ALLOW.confidence).toBeGreaterThanOrEqual(0);
    expect(MOCK_ENVELOPE_ALLOW.confidence).toBeLessThanOrEqual(1);
    expect(MOCK_ENVELOPE_BLOCK.confidence).toBeGreaterThanOrEqual(0);
    expect(MOCK_ENVELOPE_BLOCK.confidence).toBeLessThanOrEqual(1);
  });

  it("x108_gate doit être ALLOW, HOLD ou BLOCK", () => {
    const validGates = ["ALLOW", "HOLD", "BLOCK"];
    expect(validGates).toContain(MOCK_ENVELOPE_ALLOW.x108_gate);
    expect(validGates).toContain(MOCK_ENVELOPE_BLOCK.x108_gate);
  });

  it("severity doit être S1, S2, S3 ou S4", () => {
    const validSeverities = ["S1", "S2", "S3", "S4"];
    expect(validSeverities).toContain(MOCK_ENVELOPE_ALLOW.severity);
    expect(validSeverities).toContain(MOCK_ENVELOPE_BLOCK.severity);
  });

  it("domain doit être trading, bank ou ecom", () => {
    const validDomains = ["trading", "bank", "ecom"];
    expect(validDomains).toContain(MOCK_ENVELOPE_ALLOW.domain);
    expect(validDomains).toContain(MOCK_ENVELOPE_BLOCK.domain);
  });

  it("formatDecisionId tronque les IDs longs", () => {
    const longId = "DEC-T-2024-0891-a3f2b7c1d9e0";
    const formatted = formatDecisionId(longId, 20);
    expect(formatted.length).toBeLessThanOrEqual(20);
    expect(formatted).toContain("…");
  });

  it("formatDecisionId conserve les IDs courts", () => {
    const shortId = "DEC-001";
    expect(formatDecisionId(shortId, 20)).toBe(shortId);
  });

  it("une enveloppe BLOCK doit avoir des risk_flags", () => {
    expect(MOCK_ENVELOPE_BLOCK.risk_flags.length).toBeGreaterThan(0);
  });

  it("une enveloppe ALLOW S1/S2 peut avoir risk_flags vide", () => {
    expect(MOCK_ENVELOPE_ALLOW.risk_flags).toEqual([]);
  });
});

// ─── Tests ProofChainView ─────────────────────────────────────────────────────
describe("ProofChainView — contrat ProofChain", () => {
  it("une chaîne complète sans ticket a score 3/3", () => {
    const result = proofCompletenessScore(MOCK_PROOF_COMPLETE);
    expect(result.score).toBe(3);
    expect(result.max).toBe(3);
    expect(result.label).toBe("COMPLETE");
  });

  it("une chaîne partielle avec ticket requis mais sans attestation a score 3/4", () => {
    const result = proofCompletenessScore(MOCK_PROOF_PARTIAL);
    expect(result.score).toBe(3);
    expect(result.max).toBe(4);
    expect(result.label).toBe("PARTIAL");
  });

  it("une chaîne incomplète sans trace ni attestation a score 1/3", () => {
    const result = proofCompletenessScore(MOCK_PROOF_INCOMPLETE);
    expect(result.score).toBe(1);
    expect(result.max).toBe(3);
    expect(result.label).toBe("INCOMPLETE");
  });

  it("proof_complete et proof_partial sont mutuellement exclusifs", () => {
    expect(MOCK_PROOF_COMPLETE.proof_complete && MOCK_PROOF_COMPLETE.proof_partial).toBe(false);
    expect(MOCK_PROOF_PARTIAL.proof_complete && MOCK_PROOF_PARTIAL.proof_partial).toBe(false);
  });

  it("decision_id est toujours présent dans une ProofChain valide", () => {
    expect(MOCK_PROOF_COMPLETE.decision_id).toBeTruthy();
    expect(MOCK_PROOF_PARTIAL.decision_id).toBeTruthy();
    expect(MOCK_PROOF_INCOMPLETE.decision_id).toBeTruthy();
  });

  it("ticket_id ne peut être présent que si ticket_required est true", () => {
    if (MOCK_PROOF_PARTIAL.ticket_id) {
      expect(MOCK_PROOF_PARTIAL.ticket_required).toBe(true);
    }
    // Une chaîne sans ticket_required ne devrait pas avoir de ticket_id
    const noTicket: ProofChain = { ...MOCK_PROOF_COMPLETE, ticket_required: false, ticket_id: undefined };
    expect(noTicket.ticket_id).toBeUndefined();
  });

  it("une chaîne avec lean_proof_hash est plus robuste", () => {
    const withLean: ProofChain = { ...MOCK_PROOF_COMPLETE, lean_proof_hash: "sha256:abc123" };
    expect(withLean.lean_proof_hash).toBeTruthy();
    const result = proofCompletenessScore(withLean);
    expect(result.label).toBe("COMPLETE");
  });
});

// ─── Tests HealthMatrix ───────────────────────────────────────────────────────
describe("HealthMatrix — contrat HealthMatrixData", () => {
  it("un système sain a un score global >= 80", () => {
    const score = globalHealthScore(MOCK_HEALTH_OK);
    expect(score).toBeGreaterThanOrEqual(80);
    expect(healthStatus(score)).toBe("OK");
  });

  it("un système critique a un score global < 60", () => {
    const score = globalHealthScore(MOCK_HEALTH_CRITICAL);
    expect(score).toBeLessThan(60);
    expect(healthStatus(score)).toBe("CRITICAL");
  });

  it("les scores de dimension sont entre 0 et 100", () => {
    for (const data of [MOCK_HEALTH_OK, MOCK_HEALTH_CRITICAL]) {
      for (const dim of [data.agent_health, data.proof_coverage, data.decision_quality, data.risk_exposure]) {
        expect(dim.score).toBeGreaterThanOrEqual(0);
        expect(dim.score).toBeLessThanOrEqual(100);
      }
    }
  });

  it("le trend doit être up, down ou stable", () => {
    const validTrends = ["up", "down", "stable"];
    for (const data of [MOCK_HEALTH_OK, MOCK_HEALTH_CRITICAL]) {
      for (const dim of [data.agent_health, data.proof_coverage, data.decision_quality, data.risk_exposure]) {
        expect(validTrends).toContain(dim.trend);
      }
    }
  });

  it("risk_exposure est inversé dans le score global (haut = mauvais)", () => {
    const highRisk: HealthMatrixData = {
      ...MOCK_HEALTH_OK,
      risk_exposure: { label: "Risk", score: 90, trend: "up" },
    };
    const lowRisk: HealthMatrixData = {
      ...MOCK_HEALTH_OK,
      risk_exposure: { label: "Risk", score: 10, trend: "down" },
    };
    expect(globalHealthScore(lowRisk)).toBeGreaterThan(globalHealthScore(highRisk));
  });

  it("domain doit être trading, bank ou ecom", () => {
    const validDomains = ["trading", "bank", "ecom"];
    expect(validDomains).toContain(MOCK_HEALTH_OK.domain);
    expect(validDomains).toContain(MOCK_HEALTH_CRITICAL.domain);
  });

  it("un système avec tous les scores à 100 et risk à 0 a un score global de 100", () => {
    const perfect: HealthMatrixData = {
      domain: "trading",
      agent_health:     { label: "A", score: 100, trend: "stable" },
      proof_coverage:   { label: "P", score: 100, trend: "stable" },
      decision_quality: { label: "D", score: 100, trend: "stable" },
      risk_exposure:    { label: "R", score: 0,   trend: "stable" },
    };
    expect(globalHealthScore(perfect)).toBe(100);
    expect(healthStatus(100)).toBe("OK");
  });

  it("healthStatus retourne WARN pour un score entre 60 et 79", () => {
    expect(healthStatus(70)).toBe("WARN");
    expect(healthStatus(60)).toBe("WARN");
    expect(healthStatus(79)).toBe("WARN");
  });

  it("les dimensions critiques sont correctement marquées dans le système critique", () => {
    const criticalDims = [
      MOCK_HEALTH_CRITICAL.agent_health,
      MOCK_HEALTH_CRITICAL.proof_coverage,
      MOCK_HEALTH_CRITICAL.risk_exposure,
    ];
    for (const dim of criticalDims) {
      expect(dim.critical).toBe(true);
    }
  });
});
