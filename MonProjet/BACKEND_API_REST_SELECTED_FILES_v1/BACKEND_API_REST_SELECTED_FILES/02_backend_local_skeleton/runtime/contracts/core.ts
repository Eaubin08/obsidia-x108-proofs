import { z } from 'zod';

// Verdicts: BLOCK, HOLD, ALLOW
export enum Verdict {
  BLOCK = 'BLOCK',
  HOLD = 'HOLD',
  ALLOW = 'ALLOW'
}

// 1. SovereignCase
export const SovereignCaseSchema = z.object({
  id: z.string(),
  source_os: z.string(),
  priority: z.number(),
  payload: z.any(),
  timestamp: z.string()
});
export type SovereignCase = z.infer<typeof SovereignCaseSchema>;

// 2. SovereignDecision
export const SovereignDecisionSchema = z.object({
  case_id: z.string(),
  verdict: z.nativeEnum(Verdict),
  reason: z.string(),
  signature_kernel: z.string()
});
export type SovereignDecision = z.infer<typeof SovereignDecisionSchema>;

// 3. RealEvent
export const RealEventSchema = z.object({
  raw_data: z.any(),
  input_channel: z.string(),
  reception_time: z.string()
});
export type RealEvent = z.infer<typeof RealEventSchema>;

// 4. AttestationBundle
export const AttestationBundleSchema = z.object({
  data: z.any(),
  proof_of_origin: z.string(),
  hash: z.string()
});
export type AttestationBundle = z.infer<typeof AttestationBundleSchema>;

// 5. AttestedEvent
export const AttestedEventSchema = RealEventSchema.extend({
  attestation: AttestationBundleSchema
});
export type AttestedEvent = z.infer<typeof AttestedEventSchema>;

// 6. CanonicalInput
export const CanonicalInputSchema = z.object({
  cleaned_data: z.any(),
  ready_for_os0: z.boolean()
});
export type CanonicalInput = z.infer<typeof CanonicalInputSchema>;

// 7. RiskLatentAlert
export const RiskLatentAlertSchema = z.object({
  level: z.string(),
  description: z.string(),
  trigger_source: z.string()
});
export type RiskLatentAlert = z.infer<typeof RiskLatentAlertSchema>;

// 8. RawRequest
export const RawRequestSchema = z.object({
  intent: z.string(),
  user_id: z.string()
});
export type RawRequest = z.infer<typeof RawRequestSchema>;

// 9. QualifiedNeed
export const QualifiedNeedSchema = RawRequestSchema.extend({
  business_mapping: z.string()
});
export type QualifiedNeed = z.infer<typeof QualifiedNeedSchema>;

// 10. ContextualPersona
export const ContextualPersonaSchema = z.object({
  system_state: z.any(),
  timestamp: z.string()
});
export type ContextualPersona = z.infer<typeof ContextualPersonaSchema>;

// 11. NeedRouting
export const NeedRoutingSchema = z.object({
  target_os: z.string(),
  target_engine: z.string()
});
export type NeedRouting = z.infer<typeof NeedRoutingSchema>;

// 12. ReflexPattern
export const ReflexPatternSchema = z.object({
  trigger_hash: z.string(),
  response_template: z.string()
});
export type ReflexPattern = z.infer<typeof ReflexPatternSchema>;

// 13. ReflexResponse
export const ReflexResponseSchema = z.object({
  immediate_response: z.string()
});
export type ReflexResponse = z.infer<typeof ReflexResponseSchema>;

// 14. ExplorationCase
export const ExplorationCaseSchema = z.object({
  problem_statement: z.string(),
  constraints: z.array(z.string()),
  depth_limit: z.number()
});
export type ExplorationCase = z.infer<typeof ExplorationCaseSchema>;

// 15. Hypothesis
export const HypothesisSchema = z.object({
  path_id: z.string(),
  probability: z.number(),
  estimated_impact: z.number()
});
export type Hypothesis = z.infer<typeof HypothesisSchema>;

// 16. CandidatePath
export const CandidatePathSchema = z.object({
  steps: z.array(z.string())
});
export type CandidatePath = z.infer<typeof CandidatePathSchema>;

// 17. DecisionTicket
export const DecisionTicketSchema = z.object({
  decision: SovereignDecisionSchema,
  full_trace: z.array(z.string()),
  system_state_snapshot: z.any()
});
export type DecisionTicket = z.infer<typeof DecisionTicketSchema>;
