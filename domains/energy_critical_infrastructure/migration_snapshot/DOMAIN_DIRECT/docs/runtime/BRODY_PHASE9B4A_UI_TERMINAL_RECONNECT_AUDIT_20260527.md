# BRODY_PHASE9B4A_UI_TERMINAL_RECONNECT_AUDIT_20260527

Status: DIAGNOSTIC_ONLY

## Scope
Audit UI and terminal client surfaces before reconnecting them to Phase 9B2 support routes.

## Rule
- /api/brody/chat remains primary.
- OS Trad / IR / Reverse routes are support surfaces only.
- Terminal and UI must not bypass Brody chat.

## Files inspected
- exists=True length=8139 path=tools/brody_chat.py
- exists=True length=1257 path=scripts/run_brody_terminal.ps1
- exists=True length=2310 path=scripts/smoke_brody_capabilities.ps1
- exists=True length=1559 path=scripts/smoke_brody_routes.ps1
- exists=True length=8946 path=apps/obsidia-workbench/src/api/obsidiaClient.ts
- exists=True length=7201 path=apps/obsidia-workbench/src/App.tsx
- exists=True length=1903 path=apps/obsidia-workbench/src/lib/osTradPipeline.ts
- exists=True length=3727 path=apps/obsidia-workbench/src/lib/irCandidateBuilder.ts
- exists=True length=3649 path=apps/obsidia-workbench/src/lib/osReverseProjection.ts
- exists=True length=13461 path=apps/obsidia-workbench/src/lib/brodyResponseComposer.ts

## Evidence hits
- .\tools\brody_chat.py:4: Dialogue direct avec le moteur Obsidia via http://127.0.0.1:8012/api/brody/chat
- .\tools\brody_chat.py:23: BASE_URL  = "http://127.0.0.1:8012"
- .\tools\brody_chat.py:24: ENDPOINT  = f"{BASE_URL}/api/brody/chat"
- .\tools\brody_chat.py:219: ENDPOINT  = f"{BASE_URL}/api/brody/chat"
- .\scripts\run_brody_terminal.ps1:2: [string]$Base = "http://127.0.0.1:8012",
- .\scripts\run_brody_terminal.ps1:42: $r = Invoke-WebRequest -Uri "$Base/api/brody/chat" -Method POST -ContentType "application/json; charset=utf-8" -Body $bytes -TimeoutSec 60
- .\scripts\smoke_brody_capabilities.ps1:2: [string]$Base = "http://127.0.0.1:8012"
- .\scripts\smoke_brody_capabilities.ps1:13: $uri = "$Base/api/brody/chat"
- .\scripts\smoke_brody_routes.ps1:2: [string]$Base = "http://127.0.0.1:8012"
- .\scripts\smoke_brody_routes.ps1:21: "/api/brody/chat",
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:3: * All calls try the live Brody API on port 8012 first, then fall back to mock.
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:11: import * as mock from './mockFallback'
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:16: const ENGINE_BASE = (import.meta.env.VITE_ENGINE_API_BASE ?? import.meta.env.VITE_BRODY_API_URL ?? 'http://127.0.0.1:8012').replace(/\/$/, '')
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:17: const USE_MOCK    = import.meta.env.VITE_USE_MOCK_FALLBACK === 'true'
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:22: export const config = { API_BASE, ENGINE_BASE, USE_MOCK, TIMEOUT_MS }
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:24: async function safeFetch<T>(url: string, fallback: T): Promise<Resolved<T>> {
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:25: if (USE_MOCK) return { data: fallback, source: 'mock' }
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:31: return { data: fallback, source: 'mock' }
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:73: export async function sendBrodyMessage(
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:81: const res = await fetch(`${ENGINE_BASE}/api/brody/chat`, {
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:107: final_answer: `API_ERROR — HTTP ${res.status}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:108: response: `API_ERROR — HTTP ${res.status}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:110: decision_authority: 'KX108_ONLY', source: 'API_ERROR',
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:115: final_answer: `API_ERROR — ${msg}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:116: response: `API_ERROR — ${msg}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:118: decision_authority: 'KX108_ONLY', source: 'API_ERROR',
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:125: decision_authority: 'KX108_ONLY', source: 'FRONTEND_MOCK',
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:148: const raw = await safeFetch<AuditChainResponse>(`${ENGINE_BASE}/v1/audit/chain`, mock.MOCK_AUDIT_CHAIN)
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:153: if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/os3/tickets`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) { const d = await res.json(); if (d.tickets?.length) return { data: d.tickets[0], source: 'api' } } } catch {} }
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:158: if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/worldcalls/sovereign-tickets`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).tickets ?? [], source: 'api' } } catch {} }
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:163: if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/worldcalls`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).calls ?? [], source: 'api' } } catch {} }
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:168: if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/memory/candidates`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).candidates ?? [], source: 'api' } } catch {} }
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:173: if (!USE_MOCK) { try { const res = await fetch(`${ENGINE_BASE}/api/gencoin`, { signal: AbortSignal.timeout(TIMEOUT_MS) }); if (res.ok) return { data: (await res.json()).entries ?? [], source: 'api' } } catch {} }
- .\apps\obsidia-workbench\src\App.tsx:18: import { getKernelStatus, sendBrodyMessage } from './api/obsidiaClient'
- .\apps\obsidia-workbench\src\App.tsx:21: import { runOSTradPipeline } from './lib/osTradPipeline'
- .\apps\obsidia-workbench\src\App.tsx:88: // BACKEND-FIRST: Always call real API. Never fall back to FRONTEND_MOCK on HTTP 200.
- .\apps\obsidia-workbench\src\App.tsx:93: const res = await sendBrodyMessage(text, lang, activeSessionId)
- .\apps\obsidia-workbench\src\App.tsx:94: if (res.source !== 'FRONTEND_MOCK') {
- .\apps\obsidia-workbench\src\App.tsx:95: // Real API response (including API_ERROR) — never replace with frontend mock
- .\apps\obsidia-workbench\src\App.tsx:102: const trace = runOSTradPipeline(text, lang)
- .\apps\obsidia-workbench\src\App.tsx:104: backendSource = 'FRONTEND_MOCK'
- .\apps\obsidia-workbench\src\App.tsx:108: const trace: TranslationTrace = backendPayload?.translation_trace as TranslationTrace ?? runOSTradPipeline(text, lang)
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:5: import { buildIRCandidate } from './irCandidateBuilder'
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:6: import { buildOSReverseProjection } from './osReverseProjection'
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:16: export function runOSTradPipeline(
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:27: const irCandidate   = buildIRCandidate(userInput, alphabetUnits)
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:28: const reverseProj   = buildOSReverseProjection(irCandidate, responseLang)
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:33: export function buildIRCandidate(text: string, alphabetUnits: AlphabetUnit[]): IRCandidate {
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:46: export function buildOSReverseProjection(
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:1: // FALLBACK ONLY. Primary Brody response source is POST /api/brody/chat (port 8000).

## Live route availability
- route=/api/brody/chat exists=True
- route=/api/os-trad/translate exists=True
- route=/api/ir/candidate exists=True
- route=/api/os-reverse/project exists=True

## Intended reconnect
- Add terminal smoke script for OS Trad / IR / Reverse support routes.
- Add UI API client helpers for OS Trad / IR / Reverse support routes.
- Preserve sendBrodyMessage as primary chat call.
- Do not modify Brody runtime behavior in this audit phase.

## Boundary
- Diagnostic only.
- No patch.
- No runtime mutation.
- No kernel mutation.
- No X108 mutation.
- No memory write.
- No Graphiti write.
- KX108_ONLY remains sole decision authority.