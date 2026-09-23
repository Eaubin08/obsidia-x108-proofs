/**
 * Mock fallback values — used when the backend is offline or VITE_USE_MOCK_FALLBACK=true.
 * All values enforce Obsidia sovereignty invariants.
 */
import type {
  ApiHealthResponse, GraphitiStatusResponse, GraphitiContextResponse,
  GraphitiReadinessResponse, GraphitiMetricsResponse, AuditChainResponse,
} from './contracts'
import {
  KERNEL_STATUS, MOCK_CONTEXT_PACKET, MOCK_MEMORY_CANDIDATES,
  MOCK_GENCOIN, MOCK_AUDIT, MOCK_WORLD_CALLS, MOCK_SOVEREIGN_TICKET,
  MOCK_OS3_TICKET,
} from '../data/mockData'

export const MOCK_HEALTH: ApiHealthResponse = {
  status: 'healthy',
  gateway: 'obsidiashell',
  version: '1.1.0-graphiti-v20 (MOCK)',
  timestamp: new Date().toISOString(),
  services: {
    graphiti_v20_db: { status: 'mock' },
    graphiti_http:   { status: 'mock' },
  },
}

export const MOCK_GRAPHITI_STATUS: GraphitiStatusResponse = {
  status: 'healthy',
  frozen: true,
  run_id: 'freeze_phase0_v20_mock',
  entity_count: 0,
  relation_count: 0,
  episode_count: 0,
  timestamp: new Date().toISOString(),
}

export const MOCK_GRAPHITI_CONTEXT: GraphitiContextResponse = {
  q: 'governance',
  results: MOCK_CONTEXT_PACKET.context_items.map((item, i) => ({
    uuid: `mock_${i}`,
    summary: item,
    score: 0.9 - i * 0.05,
  })),
  count: MOCK_CONTEXT_PACKET.context_items.length,
  readonly: true,
}

export const MOCK_GRAPHITI_READINESS: GraphitiReadinessResponse = {
  ready: true,
  missing: [],
  warnings: ['MOCK_MODE: real Graphiti not connected'],
  timestamp: new Date().toISOString(),
}

export const MOCK_GRAPHITI_METRICS: GraphitiMetricsResponse = {
  entity_count: 0,
  relation_count: 0,
  episode_count: 0,
  run_id: 'mock',
  version: 'v20-mock',
}

export const MOCK_AUDIT_CHAIN: AuditChainResponse = {
  chain: MOCK_AUDIT.map(e => ({
    trace_id: e.event_id,
    timestamp: e.timestamp,
    action: e.type,
    result: e.result,
  })),
}

// Re-export mock domain objects for consumers that want them directly
export {
  KERNEL_STATUS, MOCK_CONTEXT_PACKET, MOCK_MEMORY_CANDIDATES,
  MOCK_GENCOIN, MOCK_AUDIT, MOCK_WORLD_CALLS, MOCK_SOVEREIGN_TICKET,
  MOCK_OS3_TICKET,
}
