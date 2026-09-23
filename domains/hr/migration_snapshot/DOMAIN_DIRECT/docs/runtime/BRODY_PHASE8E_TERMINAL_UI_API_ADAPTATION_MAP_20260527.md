# BRODY_PHASE8E_TERMINAL_UI_API_ADAPTATION_MAP_20260527

Status: DIAGNOSTIC_ONLY

## Scope

Map Brody adaptation across terminal, live API, and Workbench/UI layers.

## Corrected interpretation
- Terminal Brody adaptation exists.
- Live /api/brody/chat adaptation exists.
- Workbench/UI OS Trad / IR / Reverse OS minimal adaptation exists.
- Dedicated backend OS Trad / IR / Reverse OS routes are not live yet.

## Files inspected
- exists=True length=8139 path=tools/brody_chat.py
- exists=True length=1257 path=scripts/run_brody_terminal.ps1
- exists=True length=2310 path=scripts/smoke_brody_capabilities.ps1
- exists=True length=1559 path=scripts/smoke_brody_routes.ps1
- exists=True length=1926 path=tests/api/test_brody_capabilities_preserved.py
- exists=True length=951 path=tests/api/test_brody_routes_registered.py
- exists=True length=1193 path=tests/api/test_brody_boundary_readonly.py
- exists=True length=2124 path=apps/obsidia-workbench/src/lib/language.ts
- exists=True length=1985 path=apps/obsidia-workbench/src/lib/symbolicAlphabet.ts
- exists=True length=3727 path=apps/obsidia-workbench/src/lib/irCandidateBuilder.ts
- exists=True length=1903 path=apps/obsidia-workbench/src/lib/osTradPipeline.ts
- exists=True length=3649 path=apps/obsidia-workbench/src/lib/osReverseProjection.ts
- exists=True length=13461 path=apps/obsidia-workbench/src/lib/brodyResponseComposer.ts
- exists=True length=8946 path=apps/obsidia-workbench/src/api/obsidiaClient.ts
- exists=True length=7201 path=apps/obsidia-workbench/src/App.tsx

## Evidence hits
- .\tools\brody_chat.py:4: Dialogue direct avec le moteur Obsidia via http://127.0.0.1:8012/api/brody/chat
- .\tools\brody_chat.py:23: BASE_URL  = "http://127.0.0.1:8012"
- .\tools\brody_chat.py:24: ENDPOINT  = f"{BASE_URL}/api/brody/chat"
- .\tools\brody_chat.py:70: auth     = data.get("decision_authority", "KX108_ONLY")
- .\tools\brody_chat.py:219: ENDPOINT  = f"{BASE_URL}/api/brody/chat"
- .\scripts\run_brody_terminal.ps1:2: [string]$Base = "http://127.0.0.1:8012",
- .\scripts\run_brody_terminal.ps1:10: Write-Host "BRODY_TERMINAL_READONLY"
- .\scripts\run_brody_terminal.ps1:13: Write-Host "Commands: :quit, :boundary, :who"
- .\scripts\run_brody_terminal.ps1:19: if ($msg -eq ":boundary") {
- .\scripts\run_brody_terminal.ps1:20: Write-Host "decision_authority=KX108_ONLY"
- .\scripts\run_brody_terminal.ps1:21: Write-Host "emits_act=false"
- .\scripts\run_brody_terminal.ps1:23: Write-Host "memory_write=false"
- .\scripts\run_brody_terminal.ps1:29: $msg = "Qui es-tu Brody ? Réponds en français naturel, readonly, sans action."
- .\scripts\run_brody_terminal.ps1:42: $r = Invoke-WebRequest -Uri "$Base/api/brody/chat" -Method POST -ContentType "application/json; charset=utf-8" -Body $bytes -TimeoutSec 60
- .\scripts\smoke_brody_capabilities.ps1:2: [string]$Base = "http://127.0.0.1:8012"
- .\scripts\smoke_brody_capabilities.ps1:13: $uri = "$Base/api/brody/chat"
- .\scripts\smoke_brody_capabilities.ps1:17: name = "francais_utf8"
- .\scripts\smoke_brody_capabilities.ps1:21: name = "english_understanding"
- .\scripts\smoke_brody_capabilities.ps1:25: name = "code_debug"
- .\scripts\smoke_brody_capabilities.ps1:29: name = "boundary"
- .\scripts\smoke_brody_capabilities.ps1:30: message = "Boundary probe. Do not act. Return readonly metadata if available."
- .\scripts\smoke_brody_capabilities.ps1:76: Write-Host "`nBRODY_CAPABILITY_SMOKE_OK"
- .\scripts\smoke_brody_routes.ps1:2: [string]$Base = "http://127.0.0.1:8012"
- .\scripts\smoke_brody_routes.ps1:21: "/api/brody/chat",
- .\tests\api\test_brody_capabilities_preserved.py:11: "/api/brody/chat",
- .\tests\api\test_brody_capabilities_preserved.py:35: def test_english_understanding_capability_preserved():
- .\tests\api\test_brody_capabilities_preserved.py:54: "Qui es-tu Brody ? Réponds en français naturel, readonly.",
- .\tests\api\test_brody_routes_registered.py:8: "/api/brody/chat",
- .\tests\api\test_brody_boundary_readonly.py:15: def test_brody_boundary_readonly():
- .\tests\api\test_brody_boundary_readonly.py:19: "/api/brody/chat",
- .\tests\api\test_brody_boundary_readonly.py:21: "message": "Boundary probe. Do not act. Return readonly metadata if available.",
- .\tests\api\test_brody_boundary_readonly.py:22: "session_id": "pytest_boundary_probe",
- .\tests\api\test_brody_boundary_readonly.py:33: "emits_act",
- .\tests\api\test_brody_boundary_readonly.py:35: "memory_write",
- .\tests\api\test_brody_boundary_readonly.py:44: assert "KX108" in serialized or "readonly" in serialized.lower() or "READONLY" in serialized
- .\apps\obsidia-workbench\src\lib\symbolicAlphabet.ts:5: const CONSTRAINT_RE = /\b(readonly/read[-\s]?only/sans écrire/without write?/no write/pas d'écriture/seulement/only/uniquement/exclusivement/just/merely/review/révision)\b/gi
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:33: export function buildIRCandidate(text: string, alphabetUnits: AlphabetUnit[]): IRCandidate {
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:54: if (/\b(act\b/acte)\b/i.test(t) && !/readonly/lecture/i.test(t)) {
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:66: contradictions.push('DECISION_AUTHORITY_IS_X108_ONLY')
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:69: contradictions.push('MEMORY_WRITE_FORBIDDEN_BRODY_READONLY')
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:72: contradictions.push('EMITS_ACT_FALSE')
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:96: readonly: true,
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:99: memory_write: false,
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:101: decision_authority: 'X108_ONLY',
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:4: import { buildAlphabetUnits } from './symbolicAlphabet'
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:5: import { buildIRCandidate } from './irCandidateBuilder'
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:6: import { buildOSReverseProjection } from './osReverseProjection'
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:16: export function runOSTradPipeline(
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:27: const irCandidate   = buildIRCandidate(userInput, alphabetUnits)
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:28: const reverseProj   = buildOSReverseProjection(irCandidate, responseLang)
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:45: x108_boundary_status: 'READONLY',
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:46: readonly:            true,
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:49: memory_write:        false,
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:14: "Une demande de création est détectée. Brody est readonly — aucune création directe. Je peux préparer une proposition structurée pour X-108.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:35: "A creation request is detected. Brody is readonly — no direct creation. I can prepare a structured proposal for X-108.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:46: export function buildOSReverseProjection(
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:1: // FALLBACK ONLY. Primary Brody response source is POST /api/brody/chat (port 8000).
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:35: "Bonjour. Brody est en ligne — mode readonly, advisory uniquement. Kernel X-108 actif, 397 tests passing. Mémoire en CANDIDATE_ONLY. Dis-moi ce que tu cherches à comprendre ou à préparer.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:47: "Graphiti V20 est le graphe de contexte readonly. Les candidats mémoire transitent par BRODY_RUNTIME → CANDIDATE → NEEDS_REVIEW → PROMOTION_READY. La promotion manuelle requiert une décision humaine explicite. Aucune promotion automatique.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:50: "X-108 est le kernel de gouvernance souverain — la seule autorité de décision du système. OS3 prouve ses décisions via Lean 4 et TLA+. Brody l'interface, il ne le substitue pas. Statut actuel : ACTIVE, mode READONLY. 397 tests passing. Fichiers protégés : intacts.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:55: "Les 7 invariants de non-souveraineté : decision_authority=KX108_ONLY, emits_act=false, memory_write=false, auto_promotion=false, graphiti_write=false, real_chain_action=false, Gencoin is_real_token=false. Ces invariants ne peuvent pas être overridés.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:66: "Les WorldCalls sont les actions d'egress contrôlées par le Gateway. Mode actuel : dry-run uniquement. Le Gateway bloque toute action réelle non-dry-run. Un SovereignTicket X-108 est requis pour tout WorldCall non-READONLY.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:67: "Le SovereignTicket autorise, le Gateway exécute (ou bloque). WorldActionBus trace tout. Egress réel : bloqué dans la configuration courante. Brody ne génère pas de WorldCall — il consulte le registre readonly.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:80: "Hello. Brody is online — readonly mode, advisory only. X-108 kernel active, 397 tests passing. Memory in CANDIDATE_ONLY mode. What are you trying to understand or prepare?",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:95: "X-108 is the sovereign governance kernel — the sole decision authority in the system. OS3 proves its decisions via Lean 4 and TLA+. Brody interfaces with it, never substitutes for it. Current status: ACTIVE, READONLY mode. 397 tests passing. Protected files: intact.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:100: "The 7 non-sovereignty invariants: decision_authority=KX108_ONLY, emits_act=false, memory_write=false, auto_promotion=false, graphiti_write=false, real_chain_action=false, Gencoin is_real_token=false. These invariants cannot be overridden.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:111: "WorldCalls are egress actions controlled by the Gateway. Current mode: dry-run only. Gateway blocks all non-dry-run real actions. An X-108 SovereignTicket is required for any non-READONLY WorldCall.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:112: "SovereignTicket authorizes, Gateway executes (or blocks). WorldActionBus traces everything. Real egress: blocked in current configuration. Brody doesn't generate WorldCalls — it consults the readonly registry.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:138: export function composeBrodyResponse(opts: ComposeOptions): string {
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:3: * All calls try the live Brody API on port 8012 first, then fall back to mock.
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:4: * No real action. No wallet. KX108_ONLY always.
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:16: const ENGINE_BASE = (import.meta.env.VITE_ENGINE_API_BASE ?? import.meta.env.VITE_BRODY_API_URL ?? 'http://127.0.0.1:8012').replace(/\/$/, '')
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:66: decision_authority: string
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:67: emits_act: boolean
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:68: memory_write: boolean
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:70: readonly: boolean
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:73: export async function sendBrodyMessage(
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:81: const res = await fetch(`${ENGINE_BASE}/api/brody/chat`, {
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:84: body: JSON.stringify({ message: text, language: lang, session_id: sessionId, mode: 'readonly' }),
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:99: readonly: (data.readonly as boolean) ?? true,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:100: emits_act: (data.emits_act as boolean) ?? false,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:101: memory_write: (data.memory_write as boolean) ?? false,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:102: decision_authority: (data.decision_authority as string) ?? 'KX108_ONLY',
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:107: final_answer: `API_ERROR — HTTP ${res.status}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:108: response: `API_ERROR — HTTP ${res.status}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:109: readonly: true, emits_act: false, memory_write: false,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:110: decision_authority: 'KX108_ONLY', source: 'API_ERROR',
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:115: final_answer: `API_ERROR — ${msg}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:116: response: `API_ERROR — ${msg}`,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:117: readonly: true, emits_act: false, memory_write: false,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:118: decision_authority: 'KX108_ONLY', source: 'API_ERROR',
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:123: final_answer: '', response: '', readonly: true,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:124: emits_act: false, memory_write: false,
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:125: decision_authority: 'KX108_ONLY', source: 'FRONTEND_MOCK',
- .\apps\obsidia-workbench\src\App.tsx:18: import { getKernelStatus, sendBrodyMessage } from './api/obsidiaClient'
- .\apps\obsidia-workbench\src\App.tsx:19: import { composeBrodyResponse } from './lib/brodyResponseComposer'
- .\apps\obsidia-workbench\src\App.tsx:21: import { runOSTradPipeline } from './lib/osTradPipeline'
- .\apps\obsidia-workbench\src\App.tsx:75: readonly: true,
- .\apps\obsidia-workbench\src\App.tsx:76: emits_act: false,
- .\apps\obsidia-workbench\src\App.tsx:77: memory_write: false,
- .\apps\obsidia-workbench\src\App.tsx:78: decision_authority: 'KX108_ONLY',
- .\apps\obsidia-workbench\src\App.tsx:88: // BACKEND-FIRST: Always call real API. Never fall back to FRONTEND_MOCK on HTTP 200.
- .\apps\obsidia-workbench\src\App.tsx:93: const res = await sendBrodyMessage(text, lang, activeSessionId)
- .\apps\obsidia-workbench\src\App.tsx:94: if (res.source !== 'FRONTEND_MOCK') {
- .\apps\obsidia-workbench\src\App.tsx:95: // Real API response (including API_ERROR) — never replace with frontend mock
- .\apps\obsidia-workbench\src\App.tsx:102: const trace = runOSTradPipeline(text, lang)
- .\apps\obsidia-workbench\src\App.tsx:103: responseText = composeBrodyResponse({ userInput: text, language: lang, translationTrace: trace })
- .\apps\obsidia-workbench\src\App.tsx:104: backendSource = 'FRONTEND_MOCK'
- .\apps\obsidia-workbench\src\App.tsx:108: const trace: TranslationTrace = backendPayload?.translation_trace as TranslationTrace ?? runOSTradPipeline(text, lang)
- .\apps\obsidia-workbench\src\App.tsx:116: readonly: true,
- .\apps\obsidia-workbench\src\App.tsx:117: emits_act: false,
- .\apps\obsidia-workbench\src\App.tsx:118: memory_write: false,
- .\apps\obsidia-workbench\src\App.tsx:119: decision_authority: 'KX108_ONLY',

## Live route gap
- route=/api/brody/chat exists=True
- route=/api/os-trad/translate exists=False
- route=/api/ir/candidate exists=False
- route=/api/os-reverse/project exists=False
- route=/api/graphiti/status exists=True
- route=/api/memory/status exists=True

## Current position
- Brody adaptive behavior is already partially validated in terminal/API/UI.
- The missing piece is not adaptation itself.
- The missing piece is backend route decomposition for OS Trad / IR / OS Reverse.

## Boundary
- Diagnostic only.
- No patch.
- No mutation.
- KX108_ONLY remains sole decision authority.