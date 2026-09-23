/**
 * Obsidia API Client — V5B+ Backend-first.
 * All calls try the live Brody API on port 8000 first, then fall back to mock.
 * No real action. No wallet. KX108_ONLY always.
 */
import type { Resolved } from './contracts'
import type {
  ApiHealthResponse, GraphitiStatusResponse, GraphitiContextResponse,
  GraphitiReadinessResponse, GraphitiMetricsResponse,
} from './contracts'
import * as mock from './mockFallback'
import type { KernelStatus, ContextPacket, OS3ProofTicket, SovereignTicket,
              WorldCallEvent, MemoryCandidate, GencoinEntry, AuditEvent } from '../types/obsidia'

const API_BASE    = (import.meta.env.VITE_OBSIDIA_API_BASE  ?? 'http://127.0.0.1:8011').replace(/\/$/, '')
const ENGINE_BASE = (import.meta.env.VITE_ENGINE_API_BASE ?? import.meta.env.VITE_BRODY_API_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')
const USE_MOCK    = import.meta.env.VITE_USE_MOCK_FALLBACK === 'true'
const TIMEOUT_MS  = Number(import.meta.env.VITE_PROBE_TIMEOUT_MS ?? 3000)
// Brody chat can be slow on cold start (hydration scan ~40-50s) — use a separate longer timeout
const BRODY_CHAT_TIMEOUT_MS = Number(import.meta.env.VITE_BRODY_CHAT_TIMEOUT_MS ?? 120000)

export const config = { API_BASE, ENGINE_BASE, USE_MOCK, TIMEOUT_MS }

async function safeFetch<T>(url: string, fallback: T): Promise<Resolved<T>> {
  if (USE_MOCK) return { data: fallback, source: 'mock' }
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT_MS) })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return { data: (await res.json()) as T, source: 'api' }
  } catch {
    return { data: fallback, source: 'mock' }
  }
}

export async function getBackendHealth(): Promise<Resolved<ApiHealthResponse>> {
  return safeFetch(`${API_BASE}/health`, mock.MOCK_HEALTH)
}

export async function getKernelStatus(): Promise<Resolved<KernelStatus>> {
  const h = await getBackendHealth()
  return { data: { ...mock.KERNEL_STATUS, status: h.data.status === 'healthy' ? 'ACTIVE' : 'DEGRADED', last_checked: h.data.timestamp }, source: h.source }
}

export async function getGraphitiStatus(): Promise<Resolved<GraphitiStatusResponse>> {
  return safeFetch(`${API_BASE}/graph/v20/frozen/status`, mock.MOCK_GRAPHITI_STATUS)
}

export async function getGraphitiReadiness(): Promise<Resolved<GraphitiReadinessResponse>> {
  return safeFetch(`${API_BASE}/graph/v20/frozen/readiness`, mock.MOCK_GRAPHITI_READINESS)
}

export async function getGraphitiMetrics(): Promise<Resolved<GraphitiMetricsResponse>> {
  return safeFetch(`${API_BASE}/graph/v20/frozen/metrics`, mock.MOCK_GRAPHITI_METRICS)
}

export async function getContextPacket(q = 'governance'): Promise<Resolved<ContextPacket>> {
  const raw = await safeFetch<GraphitiContextResponse>(`${API_BASE}/graph/v20/frozen/context?q=${encodeURIComponent(q)}&limit=10`, mock.MOCK_GRAPHITI_CONTEXT)
  return { data: { ...mock.MOCK_CONTEXT_PACKET, query: q, context_items: raw.data.results.map(r => r.summary ?? r.fact ?? r.name ?? '') }, source: raw.source }
}

// ── Brody — BACKEND-FIRST ────────────────────────────────────────────────────

export type BrodyApiPayload = Record<string, unknown> & {
  final_answer: string
  response: string
  decision_authority: string
  emits_act: boolean
  memory_write: boolean
  source: string
  readonly: boolean
}

export async function sendBrodyMessage(
  text: string,
  language: string = 'fr',
  sessionId: string = 'local',
): Promise<BrodyApiPayload> {
  const lang = language || 'fr'
  if (!USE_MOCK) {
    try {
      const res = await fetch(`/api/brody/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, language: lang, session_id: sessionId, mode: 'readonly' }),
        signal: AbortSignal.timeout(BRODY_CHAT_TIMEOUT_MS),
      })
      if (res.ok) {
        const data = await res.json() as Record<string, unknown>
        const rawFinal = (data.final_answer as string) || (data.response as string) || ''
        // Explicit flag when HTTP 200 but final_answer absent — never fall back to fake text
        const finalAnswer = rawFinal || 'API_RESPONSE_MISSING_FINAL_ANSWER'
        // Resolve effective source: prefer true_voice chain attribution
        const tv = data.true_voice_snapshot as Record<string, unknown> | undefined
        const effectiveSource = (tv?.final_answer_source as string) || (tv?.voice_source as string) || (data.source as string) || 'BACKEND_STUB'
        return {
          ...data,
          final_answer: finalAnswer,
          response: finalAnswer,
          readonly: (data.readonly as boolean) ?? true,
          emits_act: (data.emits_act as boolean) ?? false,
          memory_write: (data.memory_write as boolean) ?? false,
          decision_authority: (data.decision_authority as string) ?? 'KX108_ONLY',
          source: effectiveSource,
        }
      }
      return {
        final_answer: `API_ERROR — HTTP ${res.status}`,
        response: `API_ERROR — HTTP ${res.status}`,
        readonly: true, emits_act: false, memory_write: false,
        decision_authority: 'KX108_ONLY', source: 'API_ERROR',
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      return {
        final_answer: `API_ERROR — ${msg}`,
        response: `API_ERROR — ${msg}`,
        readonly: true, emits_act: false, memory_write: false,
        decision_authority: 'KX108_ONLY', source: 'API_ERROR',
      }
    }
  }
  return {
    final_answer: '', response: '', readonly: true,
    emits_act: false, memory_write: false,
    decision_authority: 'KX108_ONLY', source: 'FRONTEND_MOCK',
  }
}

export type OSTradStatus = 'LIVE_AVAILABLE' | 'MOCK_ONLY' | 'STUB' | 'NEEDS_FASTAPI_ROUTE'

export async function getTranslationTrace(userInput: string): Promise<{ data: null; status: OSTradStatus }> {
  void userInput; return { data: null, status: 'NEEDS_FASTAPI_ROUTE' }
}

export async function getIRCandidate(userInput: string): Promise<{ data: null; status: OSTradStatus }> {
  void userInput; return { data: null, status: 'NEEDS_FASTAPI_ROUTE' }
}

export async function getOSReverseProjection(irCandidateId: string): Promise<{ data: null; status: OSTradStatus }> {
  void irCandidateId; return { data: null, status: 'NEEDS_FASTAPI_ROUTE' }
}

export async function getAlphabetUnits(userInput: string): Promise<{ data: null; status: OSTradStatus }> {
  void userInput; return { data: null, status: 'NEEDS_FASTAPI_ROUTE' }
}

export async function getAuditEvents(): Promise<Resolved<AuditEvent[]>> {
  const raw = await safeFetch<{events: Record<string, unknown>[]; total: number}>(`${ENGINE_BASE}/api/audit/events`, { events: [], total: 0 })
  return {
    data: (raw.data.events ?? []).map(e => ({
      event_id: String(e.event_id ?? ''),
      type: 'world_call' as AuditEvent['type'],
      description: String(e.intent ?? e.action_id ?? ''),
      result: (e.blocked ? 'BLOCKED' : 'OK') as AuditEvent['result'],
      timestamp: String(e.timestamp ?? ''),
    })),
    source: raw.source,
  }
}

export async function getOS3Ticket(): Promise<Resolved<OS3ProofTicket>> {
  if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/os3/tickets`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) { const d = await res.json(); if (d.tickets?.length) return { data: d.tickets[0], source: 'api' } } } catch {} }
  return { data: mock.MOCK_OS3_TICKET, source: 'mock' }
}

export async function getSovereignTickets(): Promise<Resolved<SovereignTicket[]>> {
  if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/worldcalls/sovereign-tickets`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).tickets ?? [], source: 'api' } } catch {} }
  return { data: [mock.MOCK_SOVEREIGN_TICKET], source: 'mock' }
}

export async function getWorldCalls(): Promise<Resolved<WorldCallEvent[]>> {
  if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/worldcalls`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).calls ?? [], source: 'api' } } catch {} }
  return { data: mock.MOCK_WORLD_CALLS, source: 'mock' }
}

export async function getMemoryCandidates(): Promise<Resolved<MemoryCandidate[]>> {
  if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/memory/candidates`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).candidates ?? [], source: 'api' } } catch {} }
  return { data: mock.MOCK_MEMORY_CANDIDATES, source: 'mock' }
}

export async function getGencoinLedger(): Promise<Resolved<GencoinEntry[]>> {
  if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/gencoin`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).entries ?? [], source: 'api' } } catch {} }
  return { data: mock.MOCK_GENCOIN, source: 'mock' }
}




// Cognitive trees live support.
// Used by TreeExplorer.
// This does not replace Brody chat and does not decide.

export type CognitiveTree = {
  id: string
  tree_id?: string | number
  name: string
  title?: string
  domain: string
  description?: string
  label?: string
  [key: string]: unknown
}

function extractArrayPayload(raw: unknown): unknown[] {
  if (Array.isArray(raw)) return raw

  if (raw && typeof raw === 'object') {
    const obj = raw as Record<string, unknown>
    for (const key of ['trees', 'items', 'results', 'data', 'cognitive_trees']) {
      const value = obj[key]
      if (Array.isArray(value)) return value
    }
  }

  return []
}

function normalizeCognitiveTree(raw: unknown, index: number): CognitiveTree {
  const obj = raw && typeof raw === 'object'
    ? raw as Record<string, unknown>
    : {}

  const rawId = obj.id ?? obj.tree_id ?? obj.name ?? obj.title ?? `tree_${index}`
  const rawName = obj.name ?? obj.title ?? obj.label ?? rawId
  const rawDomain = obj.domain ?? obj.category ?? obj.group ?? 'unknown'

  return {
    ...obj,
    id: String(rawId),
    name: String(rawName),
    domain: String(rawDomain),
    tree_id: obj.tree_id as string | number | undefined,
    title: obj.title ? String(obj.title) : undefined,
    description: obj.description ? String(obj.description) : undefined,
    label: obj.label ? String(obj.label) : undefined,
  }
}

export async function getCognitiveTrees(): Promise<Resolved<CognitiveTree[]>> {
  if (!USE_MOCK) {
    try {
      const res = await fetch(`${ENGINE_BASE}/api/periphery/cognitive/trees`, {
        signal: AbortSignal.timeout(TIMEOUT_MS),
      })

      if (res.ok) {
        const raw = await res.json()
        return {
          data: extractArrayPayload(raw).map(normalizeCognitiveTree),
          source: 'api',
        }
      }
    } catch {}
  }

  return {
    data: [],
    source: 'mock',
  }
}


// Phase 9B4 support surfaces.
// These helpers do not replace sendBrodyMessage().
// /api/brody/chat remains the primary spoken Brody interface.

export type OSTradSupportRequest = {
  text: string
  language?: 'auto' | 'fr' | 'en'
  session_id?: string
  include_context?: boolean
  include_tree_context?: boolean
  include_graphiti_context?: boolean
}

export type IRCandidateSupportRequest = {
  text: string
  language?: 'auto' | 'fr' | 'en'
  alphabet_units?: Array<Record<string, unknown>>
  tree_context?: Record<string, unknown>
  memory_context?: Record<string, unknown>
  graphiti_context?: Record<string, unknown>
  session_id?: string
}

export type OSReverseSupportRequest = {
  text: string
  language?: 'auto' | 'fr' | 'en'
  ir_candidate?: Record<string, unknown>
  audience?: 'general' | 'technical' | 'business' | 'operator'
  format?: 'short' | 'structured' | 'terminal' | 'ui'
  tree_context?: Record<string, unknown>
  memory_context?: Record<string, unknown>
  graphiti_context?: Record<string, unknown>
  session_id?: string
}

async function postSupportRoute(path: string, body: Record<string, unknown>) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new Error(`Support route failed ${path}: ${res.status}`)
  }

  return res.json()
}

export async function callOSTradTranslateSupport(req: OSTradSupportRequest) {
  return postSupportRoute('/api/os-trad/translate', {
    language: 'auto',
    include_context: true,
    include_tree_context: true,
    include_graphiti_context: true,
    ...req,
  })
}

export async function callIRCandidateSupport(req: IRCandidateSupportRequest) {
  return postSupportRoute('/api/ir/candidate', {
    language: 'auto',
    alphabet_units: [],
    tree_context: {},
    memory_context: {},
    graphiti_context: {},
    ...req,
  })
}

export async function callOSReverseProjectSupport(req: OSReverseSupportRequest) {
  return postSupportRoute('/api/os-reverse/project', {
    language: 'auto',
    ir_candidate: {},
    audience: 'general',
    format: 'structured',
    tree_context: {},
    memory_context: {},
    graphiti_context: {},
    ...req,
  })
}
